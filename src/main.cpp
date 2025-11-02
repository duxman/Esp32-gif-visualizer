/*
  ESP32 Configurator v0.3 (integrated, with GIF support and verbose logs)
  - Serves web UI from SPIFFS (data/)
  - Saves configuration in Preferences (NVS) as JSON
  - NTP sync + relay schedule
  - LED panel config
  - GIF upload/play/list/playback (GifPlayer)
  - Serial logging verbose
*/

#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <SPIFFS.h>
#include <Preferences.h>
#include <ESPmDNS.h>
#include <ArduinoJson.h>
#include <time.h>
#include "gif_player.h"  // Incluye LedPanelCfg

WebServer server(80);
Preferences prefs;

const char* PREF_NAMESPACE = "config";
const char* FIRMWARE_VERSION = "0.3";

#ifndef RELAY_PIN
#define RELAY_PIN 2
#endif

struct ScheduleEntry { bool enabled = false; String start = "08:00"; String end = "18:00"; };

struct Config {
  bool apMode = false;
  String sta_ssid = "";
  String sta_password = "";
  bool useStaticIP = false;
  IPAddress staticIP = IPAddress(192,168,1,50);
  IPAddress gateway = IPAddress(192,168,1,1);
  IPAddress subnet = IPAddress(255,255,255,0);
  bool mdnsEnabled = false;
  String mdnsName = "esp32";

  bool ntpEnabled = false;
  String ntpServer = "pool.ntp.org";
  int timezoneOffsetMinutes = 0;

  ScheduleEntry schedule;
  int relayPin = RELAY_PIN;
  LedPanelCfg led;
};

Config config;
GifPlayer gifPlayer;

bool relayState = false;
unsigned long lastScheduleCheck = 0;
const unsigned long SCHEDULE_CHECK_INTERVAL_MS = 1000;

String ipToString(const IPAddress& ip){
  return String(ip[0])+"."+String(ip[1])+"."+String(ip[2])+"."+String(ip[3]);
}
IPAddress stringToIP(const String& s){
  int parts[4] = {0,0,0,0};
  sscanf(s.c_str(), "%d.%d.%d.%d", &parts[0], &parts[1], &parts[2], &parts[3]);
  return IPAddress(parts[0], parts[1], parts[2], parts[3]);
}
bool parseHHMM(const String& s, int &outH, int &outM){
  if (s.length() < 4) return false;
  int h=0,m=0;
  if (sscanf(s.c_str(), "%d:%d", &h, &m) == 2){
    if (h >= 0 && h < 24 && m >= 0 && m < 60){
      outH = h; outM = m;
      return true;
    }
  }
  return false;
}

/* -------------------------
   Relay
   ------------------------- */
void setRelay(bool on){
  Serial.printf("[RELAY] setRelay(): pin=%d -> %s\n", config.relayPin, on ? "ON" : "OFF");
  pinMode(config.relayPin, OUTPUT);
  digitalWrite(config.relayPin, on ? HIGH : LOW);
  relayState = on;
}

/* -------------------------
   NTP helper
   ------------------------- */
void setupNTP(){
  Serial.println("[NTP] setupNTP(): starting configuration");
  if (!config.ntpEnabled){
    Serial.println("[NTP] setupNTP(): ntpEnabled = false, skipping");
    return;
  }
  long offsetSeconds = (long)config.timezoneOffsetMinutes * 60L;
  const char* server1 = config.ntpServer.c_str();
  Serial.printf("[NTP] setupNTP(): server=%s offsetMinutes=%d (offsetSeconds=%ld)\n", server1, config.timezoneOffsetMinutes, offsetSeconds);
  configTime(offsetSeconds, 0, server1);
  Serial.println("[NTP] setupNTP(): configTime() called");
}

bool isTimeSynced(){
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) return false;
  bool synced = (timeinfo.tm_year + 1900) > 2016;
  return synced;
}
String currentTimeString(){
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) return String();
  char buf[32];
  strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", &timeinfo);
  return String(buf);
}

/* -------------------------
   Schedule
   ------------------------- */
bool isNowInSchedule(){
  if (!config.schedule.enabled) return false;
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) return false;
  int nowMinutes = timeinfo.tm_hour * 60 + timeinfo.tm_min;
  int sh=0, sm=0, eh=0, em=0;
  if (!parseHHMM(config.schedule.start, sh, sm)) return false;
  if (!parseHHMM(config.schedule.end, eh, em)) return false;
  int startMinutes = sh * 60 + sm;
  int endMinutes = eh * 60 + em;
  if (startMinutes <= endMinutes){
    return (nowMinutes >= startMinutes) && (nowMinutes < endMinutes);
  } else {
    return (nowMinutes >= startMinutes) || (nowMinutes < endMinutes);
  }
}

/* -------------------------
   Config load/save
   ------------------------- */
void loadConfig(){
  Serial.println("[CONFIG] loadConfig(): reading NVS 'cfg'");
  prefs.begin(PREF_NAMESPACE, true);
  String json = prefs.getString("cfg", "");
  prefs.end();
  if (json.length() == 0){ Serial.println("[CONFIG] loadConfig(): no saved config"); return; }
  StaticJsonDocument<2048> doc;
  auto err = deserializeJson(doc, json);
  if (err){ Serial.printf("[CONFIG] loadConfig(): JSON parse error: %s\n", err.c_str()); return; }
  config.apMode = doc["apMode"] | config.apMode;
  config.sta_ssid = String((const char*)(doc["sta_ssid"] | config.sta_ssid.c_str()));
  config.sta_password = String((const char*)(doc["sta_password"] | config.sta_password.c_str()));
  config.useStaticIP = doc["useStaticIP"] | config.useStaticIP;
  config.staticIP = stringToIP(String((const char*)(doc["staticIP"] | ipToString(config.staticIP).c_str())));
  config.gateway = stringToIP(String((const char*)(doc["gateway"] | ipToString(config.gateway).c_str())));
  config.subnet = stringToIP(String((const char*)(doc["subnet"] | ipToString(config.subnet).c_str())));
  config.mdnsEnabled = doc["mdnsEnabled"] | config.mdnsEnabled;
  config.mdnsName = String((const char*)(doc["mdnsName"] | config.mdnsName.c_str()));
  config.ntpEnabled = doc["ntpEnabled"] | config.ntpEnabled;
  config.ntpServer = String((const char*)(doc["ntpServer"] | config.ntpServer.c_str()));
  config.timezoneOffsetMinutes = doc["timezoneOffsetMinutes"] | config.timezoneOffsetMinutes;
  config.schedule.enabled = doc["schedule"]["enabled"] | config.schedule.enabled;
  config.schedule.start = String((const char*)(doc["schedule"]["start"] | config.schedule.start.c_str()));
  config.schedule.end = String((const char*)(doc["schedule"]["end"] | config.schedule.end.c_str()));
  config.relayPin = doc["relayPin"] | config.relayPin;
  JsonObject led = doc["led"];
  if (!led.isNull()){
    config.led.pin = led["pin"] | config.led.pin;
    config.led.panelWidth = led["panelWidth"] | config.led.panelWidth;
    config.led.panelHeight = led["panelHeight"] | config.led.panelHeight;
    config.led.chainX = led["chainX"] | config.led.chainX;
    config.led.chainY = led["chainY"] | config.led.chainY;
    config.led.firstCorner = String((const char*)(led["firstCorner"] | config.led.firstCorner.c_str()));
    config.led.serpentine = led["serpentine"] | config.led.serpentine;
  }
  Serial.println("[CONFIG] loadConfig(): loaded");
}

void saveConfig(){
  Serial.println("[CONFIG] saveConfig(): serializing and storing");
  StaticJsonDocument<2048> doc;
  doc["apMode"] = config.apMode;
  doc["sta_ssid"] = config.sta_ssid;
  doc["sta_password"] = config.sta_password;
  doc["useStaticIP"] = config.useStaticIP;
  doc["staticIP"] = ipToString(config.staticIP);
  doc["gateway"] = ipToString(config.gateway);
  doc["subnet"] = ipToString(config.subnet);
  doc["mdnsEnabled"] = config.mdnsEnabled;
  doc["mdnsName"] = config.mdnsName;
  doc["ntpEnabled"] = config.ntpEnabled;
  doc["ntpServer"] = config.ntpServer;
  doc["timezoneOffsetMinutes"] = config.timezoneOffsetMinutes;
  JsonObject sched = doc.createNestedObject("schedule");
  sched["enabled"] = config.schedule.enabled;
  sched["start"] = config.schedule.start;
  sched["end"] = config.schedule.end;
  doc["relayPin"] = config.relayPin;
  JsonObject led = doc.createNestedObject("led");
  led["pin"] = config.led.pin;
  led["panelWidth"] = config.led.panelWidth;
  led["panelHeight"] = config.led.panelHeight;
  led["chainX"] = config.led.chainX;
  led["chainY"] = config.led.chainY;
  led["firstCorner"] = config.led.firstCorner;
  led["serpentine"] = config.led.serpentine;
  String out; serializeJson(doc, out);
  prefs.begin(PREF_NAMESPACE, false);
  prefs.putString("cfg", out);
  prefs.end();
  Serial.println("[CONFIG] saveConfig(): saved");
}

/* -------------------------
   Network / HTTP handlers
   ------------------------- */

void applyNetworkConfig(){
  Serial.println("[NETWORK] applyNetworkConfig()");
  WiFi.disconnect(true);
  delay(100);
  if (config.apMode){
    WiFi.mode(WIFI_AP);
    if (config.sta_password.length() >= 8) WiFi.softAP(config.sta_ssid.c_str(), config.sta_password.c_str());
    else WiFi.softAP(config.sta_ssid.c_str());
    Serial.printf("[NETWORK] AP IP=%s\n", ipToString(WiFi.softAPIP()).c_str());
  } else {
    WiFi.mode(WIFI_STA);
    if (config.useStaticIP){
      if (WiFi.config(config.staticIP, config.gateway, config.subnet)) Serial.println("[NETWORK] Static IP set");
      else Serial.println("[NETWORK] WiFi.config() failed");
    }
    WiFi.begin(config.sta_ssid.c_str(), config.sta_password.c_str());
    unsigned long start = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - start < 15000){ delay(200); Serial.print("."); }
    Serial.println();
    if (WiFi.status() == WL_CONNECTED) Serial.printf("[NETWORK] STA IP=%s\n", ipToString(WiFi.localIP()).c_str());
    else Serial.println("[NETWORK] STA connect failed");
  }
  if (config.mdnsEnabled && config.mdnsName.length() > 0){
    if (MDNS.begin(config.mdnsName.c_str())) Serial.printf("[MDNS] mDNS %s.local\n", config.mdnsName.c_str());
    else Serial.println("[MDNS] mDNS failed");
  } else MDNS.end();
  if (config.ntpEnabled && !config.apMode) setupNTP();
}

void handleNotFound(){
  Serial.printf("[HTTP] notFound %s\n", server.uri().c_str());
  if (SPIFFS.exists("/index.html")){
    File f = SPIFFS.open("/index.html", "r");
    server.streamFile(f, "text/html");
    f.close();
    return;
  }
  server.send(404, "text/plain", "Not found");
}

void handleGetConfig(){
  Serial.println("[HTTP] GET /api/config");
  StaticJsonDocument<2048> doc;
  doc["version"] = FIRMWARE_VERSION;
  doc["apMode"] = config.apMode;
  doc["sta_ssid"] = config.sta_ssid;
  doc["sta_password"] = config.sta_password;
  doc["useStaticIP"] = config.useStaticIP;
  doc["staticIP"] = ipToString(config.staticIP);
  doc["gateway"] = ipToString(config.gateway);
  doc["subnet"] = ipToString(config.subnet);
  doc["mdnsEnabled"] = config.mdnsEnabled;
  doc["mdnsName"] = config.mdnsName;
  doc["ntpEnabled"] = config.ntpEnabled;
  doc["ntpServer"] = config.ntpServer;
  doc["timezoneOffsetMinutes"] = config.timezoneOffsetMinutes;
  JsonObject sched = doc.createNestedObject("schedule");
  sched["enabled"] = config.schedule.enabled;
  sched["start"] = config.schedule.start;
  sched["end"] = config.schedule.end;
  doc["relayPin"] = config.relayPin;
  JsonObject led = doc.createNestedObject("led");
  led["pin"] = config.led.pin;
  led["panelWidth"] = config.led.panelWidth;
  led["panelHeight"] = config.led.panelHeight;
  led["chainX"] = config.led.chainX;
  led["chainY"] = config.led.chainY;
  led["firstCorner"] = config.led.firstCorner;
  led["serpentine"] = config.led.serpentine;
  doc["timeSynced"] = isTimeSynced();
  doc["currentTime"] = currentTimeString();
  String out; serializeJson(doc, out);
  server.send(200, "application/json", out);
  Serial.println("[HTTP] /api/config response sent");
}

void handlePostConfig(){
  Serial.println("[HTTP] POST /api/config");
  if (!server.hasArg("plain")){ server.send(400, "application/json", "{\"error\":\"No body\"}"); return; }
  String body = server.arg("plain");
  StaticJsonDocument<2048> doc;
  auto err = deserializeJson(doc, body);
  if (err){ Serial.println("[HTTP] POST /api/config: invalid json"); server.send(400, "application/json", "{\"error\":\"Invalid JSON\"}"); return; }
  config.apMode = doc["apMode"].as<bool>();
  config.sta_ssid = String((const char*)(doc["sta_ssid"] | config.sta_ssid.c_str()));
  config.sta_password = String((const char*)(doc["sta_password"] | config.sta_password.c_str()));
  config.useStaticIP = doc["useStaticIP"].as<bool>();
  config.staticIP = stringToIP(String((const char*)(doc["staticIP"] | ipToString(config.staticIP).c_str())));
  config.gateway = stringToIP(String((const char*)(doc["gateway"] | ipToString(config.gateway).c_str())));
  config.subnet = stringToIP(String((const char*)(doc["subnet"] | ipToString(config.subnet).c_str())));
  config.mdnsEnabled = doc["mdnsEnabled"].as<bool>();
  config.mdnsName = String((const char*)(doc["mdnsName"] | config.mdnsName.c_str()));
  config.ntpEnabled = doc["ntpEnabled"].as<bool>();
  config.ntpServer = String((const char*)(doc["ntpServer"] | config.ntpServer.c_str()));
  config.timezoneOffsetMinutes = doc["timezoneOffsetMinutes"] | config.timezoneOffsetMinutes;
  JsonObject schedObj = doc["schedule"];
  if (!schedObj.isNull()){
    config.schedule.enabled = schedObj["enabled"] | config.schedule.enabled;
    config.schedule.start = String((const char*)(schedObj["start"] | config.schedule.start.c_str()));
    config.schedule.end = String((const char*)(schedObj["end"] | config.schedule.end.c_str()));
  }
  config.relayPin = doc["relayPin"] | config.relayPin;
  JsonObject ledObj = doc["led"];
  if (!ledObj.isNull()){
    config.led.pin = ledObj["pin"] | config.led.pin;
    config.led.panelWidth = ledObj["panelWidth"] | config.led.panelWidth;
    config.led.panelHeight = ledObj["panelHeight"] | config.led.panelHeight;
    config.led.chainX = ledObj["chainX"] | config.led.chainX;
    config.led.chainY = ledObj["chainY"] | config.led.chainY;
    config.led.firstCorner = String((const char*)(ledObj["firstCorner"] | config.led.firstCorner.c_str()));
    config.led.serpentine = ledObj["serpentine"] | config.led.serpentine;
  }
  saveConfig();
  applyNetworkConfig();
  server.send(200, "application/json", "{\"result\":\"ok\"}");
  Serial.println("[HTTP] POST /api/config saved and applied");
}

/* -------------------------
   GIF endpoints
   ------------------------- */
void ensureGifsDir(){
  if (!SPIFFS.exists("/gifs")) SPIFFS.mkdir("/gifs");
}

void handleGifUpload(){
  HTTPUpload& upload = server.upload();
  if (upload.status == UPLOAD_FILE_START){
    String filename = upload.filename;
    if (!filename.startsWith("/")) filename = "/" + filename;
    String path = "/gifs" + filename;
    Serial.printf("[GIF] Upload start %s\n", path.c_str());
    if (SPIFFS.exists(path)) SPIFFS.remove(path);
    File f = SPIFFS.open(path, "w");
    if (f) f.close();
  } else if (upload.status == UPLOAD_FILE_WRITE){
    String filename = upload.filename;
    if (!filename.startsWith("/")) filename = "/" + filename;
    String path = "/gifs" + filename;
    File f = SPIFFS.open(path, "a");
    if (f){ f.write(upload.buf, upload.currentSize); f.close(); }
  } else if (upload.status == UPLOAD_FILE_END){
    String filename = upload.filename;
    if (!filename.startsWith("/")) filename = "/" + filename;
    String path = "/gifs" + filename;
    Serial.printf("[GIF] Upload finished %s (%u bytes)\n", path.c_str(), upload.totalSize);
    server.send(200, "application/json", "{\"result\":\"ok\"}");
  } else if (upload.status == UPLOAD_FILE_ABORTED){
    Serial.println("[GIF] Upload aborted");
    server.send(500, "application/json", "{\"error\":\"aborted\"}");
  }
}

void handleGifList(){
  Serial.println("[GIF] handleGifList()");
  ensureGifsDir();
  File root = SPIFFS.open("/gifs", "r");
  if (!root){ server.send(500, "application/json", "{\"error\":\"open dir\"}"); return; }
  StaticJsonDocument<1024> doc;
  JsonArray arr = doc.createNestedArray("gifs");
  File file = root.openNextFile();
  while (file){
    String name = String(file.name());
    if (name.startsWith("/gifs/")) name = name.substring(6);
    arr.add(name);
    file = root.openNextFile();
  }
  String out; serializeJson(doc, out);
  server.send(200, "application/json", out);
}

void handleGifPlay(){
  Serial.println("[GIF] handleGifPlay()");
  if (!server.hasArg("plain")){ server.send(400, "application/json", "{\"error\":\"No body\"}"); return; }
  String body = server.arg("plain");
  StaticJsonDocument<256> doc;
  auto err = deserializeJson(doc, body);
  if (err){ server.send(400, "application/json", "{\"error\":\"Invalid JSON\"}"); return; }
  const char *name = doc["name"] | "";
  bool loop = doc["loop"] | true;
  if (!name || strlen(name) == 0){ server.send(400, "application/json", "{\"error\":\"Missing name\"}"); return; }
  String path = "/gifs/";
  path += name;
  if (!SPIFFS.exists(path)){ server.send(404, "application/json", "{\"error\":\"not found\"}"); return; }

  LedPanelCfg ledCfg;
  ledCfg.pin = config.led.pin;
  ledCfg.panelWidth = config.led.panelWidth;
  ledCfg.panelHeight = config.led.panelHeight;
  ledCfg.chainX = config.led.chainX;
  ledCfg.chainY = config.led.chainY;
  ledCfg.firstCorner = config.led.firstCorner;
  ledCfg.serpentine = config.led.serpentine;

  gifPlayer.setPanelConfig(ledCfg);
  gifPlayer.begin(ledCfg);

  if (gifPlayer.playGif(path.c_str(), loop)) server.send(200, "application/json", "{\"result\":\"playing\"}");
  else server.send(500, "application/json", "{\"error\":\"play failed\"}");
}

void handleGifStop(){
  Serial.println("[GIF] handleGifStop()");
  gifPlayer.stop();
  server.send(200, "application/json", "{\"result\":\"stopped\"}");
}

void handleGifFile(){
  String filename = server.uri(); // e.g. /gifs/my.gif
  Serial.printf("[GIF] serve file %s\n", filename.c_str());
  if (SPIFFS.exists(filename)){
    File f = SPIFFS.open(filename, "r");
    server.streamFile(f, "image/gif");
    f.close();
  } else {
    server.send(404, "text/plain", "not found");
  }
}

void setupGifEndpoints(){
  ensureGifsDir();
  server.onFileUpload(handleGifUpload);
  server.on("/api/gifs/upload", HTTP_POST, [](){ server.send(200); });
  server.on("/api/gifs", HTTP_GET, handleGifList);
  server.on("/api/gifs/play", HTTP_POST, handleGifPlay);
  server.on("/api/gifs/stop", HTTP_POST, handleGifStop);
  server.on("^/gifs/.*", HTTP_GET, handleGifFile);
}

/* -------------------------
   NTP force sync
   ------------------------- */
void handleForceSync(){
  Serial.println("[HTTP] handleForceSync()");
  if (!config.ntpEnabled){ server.send(400, "application/json", "{\"error\":\"NTP not enabled\"}"); return; }
  setupNTP();
  delay(2000);
  if (isTimeSynced()) server.send(200, "application/json", "{\"result\":\"ok\",\"time\":\"" + currentTimeString() + "\"}");
  else server.send(500, "application/json", "{\"error\":\"Sync failed\"}");
}

/* -------------------------
   setup / loop
   ------------------------- */
void setup(){
  Serial.begin(115200);
  Serial.println();
  Serial.println("=== ESP32 Configurator v0.3 (with GIFs) starting ===");

  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  Serial.println("[SETUP] SPIFFS begin");
  if (!SPIFFS.begin(true)) Serial.println("[SETUP] SPIFFS mount failed");

  Serial.println("[SETUP] Load config");
  loadConfig();

  Serial.println("[SETUP] Apply network config");
  applyNetworkConfig();

  if (config.ntpEnabled && !config.apMode) setupNTP();

  server.on("/api/config", HTTP_GET, handleGetConfig);
  server.on("/api/config", HTTP_POST, handlePostConfig);
  server.on("/api/ntp_sync", HTTP_POST, handleForceSync);

  setupGifEndpoints();

  server.on("/", HTTP_GET, [](){
    if (SPIFFS.exists("/index.html")){
      File f = SPIFFS.open("/index.html", "r");
      server.streamFile(f, "text/html");
      f.close();
    } else server.send(500, "text/plain", "index.html missing");
  });

  server.onNotFound(handleNotFound);

  server.begin();
  Serial.println("[SETUP] HTTP server started");
}

void loop(){
  server.handleClient();
  gifPlayer.loop();

  unsigned long now = millis();
  if (now - lastScheduleCheck >= SCHEDULE_CHECK_INTERVAL_MS){
    lastScheduleCheck = now;
    bool shouldBeOn = isNowInSchedule();
    if (shouldBeOn != relayState){
      Serial.printf("[LOOP] Schedule triggered: %d -> set relay\n", shouldBeOn ? 1 : 0);
      setRelay(shouldBeOn);
    }
  }

  static unsigned long lastNtpAttempt = 0;
  if (config.ntpEnabled && !isTimeSynced()){
    if (millis() - lastNtpAttempt > 60000){
      lastNtpAttempt = millis();
      Serial.println("[NTP] Attempting NTP sync");
      setupNTP();
    }
  }
}
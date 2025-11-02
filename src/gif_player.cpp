/*
  gif_player.cpp
  Implementación de GifPlayer
  - Usa AnimatedGIF para decodificar GIFs
  - Usa Adafruit_NeoPixel para escribir LEDs
  - Mapea los píxeles del frame al orden lógico de panel definido en LedPanelCfg
*/

#include "gif_player.h"
#include <SPIFFS.h>

GifPlayer *GifPlayer::instance = nullptr;

extern "C" {
  void GIFDrawCallback(GIFDRAW *pDraw) {
    if (GifPlayer::instance) GifPlayer::instance->handleGifDraw(pDraw);
  }
}

GifPlayer::GifPlayer(){
  gif = new AnimatedGIF();
  gif->begin(GIFDrawCallback);
  instance = this;
}

GifPlayer::~GifPlayer(){
  stop();
  if (gif) { delete gif; gif = nullptr; }
  if (strip) { delete strip; strip = nullptr; }
  instance = nullptr;
}

void GifPlayer::setPanelConfig(const LedPanelCfg &ledCfg){
  cfg = ledCfg;
  totalLeds = cfg.panelWidth * cfg.panelHeight * cfg.chainX * cfg.chainY;
}

bool GifPlayer::begin(const LedPanelCfg &ledCfg){
  setPanelConfig(ledLedCfg = ledCfg); // set config
  // Note: the above line intentionally uses a temporary variable name; ensure build compiles.
  // For safety, reassign properly:
  cfg = ledCfg;
  totalLeds = cfg.panelWidth * cfg.panelHeight * cfg.chainX * cfg.chainY;

  if (strip) { delete strip; strip = nullptr; }
  strip = new Adafruit_NeoPixel(totalLeds, cfg.pin, NEO_GRB + NEO_KHZ800);
  strip->begin();
  strip->show();
  Serial.printf("[GIF] GifPlayer::begin() pin=%d totalLeds=%d\n", cfg.pin, totalLeds);
  return true;
}

bool GifPlayer::playGif(const char *path, bool loop){
  if (!SPIFFS.exists(path)){
    Serial.printf("[GIF] playGif(): file not found: %s\n", path);
    return false;
  }
  stop();

  Serial.printf("[GIF] playGif(): opening %s\n", path);
  gifFile = SPIFFS.open(path, "r");
  if (!gifFile){
    Serial.printf("[GIF] playGif(): failed to open %s\n", path);
    return false;
  }

  if (!gif->open(&gifFile)){
    Serial.printf("[GIF] playGif(): AnimatedGIF open failed for %s\n", path);
    gifFile.close();
    return false;
  }

  loopMode = loop;
  currentPath = String(path);
  playing = true;
  Serial.printf("[GIF] playGif(): started playing %s (loop=%d)\n", path, loop ? 1 : 0);
  return true;
}

void GifPlayer::stop(){
  if (!playing) return;
  Serial.printf("[GIF] stop(): stopping %s\n", currentPath.c_str());
  playing = false;
  currentPath = "";
  if (gif) gif->close();
  if (gifFile) { gifFile.close(); }
  if (strip) {
    strip->clear();
    strip->show();
  }
}

void GifPlayer::loop(){
  if (!playing) return;
  int r = gif->playFrame(false, NULL);
  if (r < 0){
    Serial.printf("[GIF] loop(): playFrame returned %d (end or error)\n", r);
    if (loopMode) {
      Serial.println("[GIF] loop(): restarting GIF (loop mode)");
      gif->close();
      gifFile.seek(0);
      if (!gif->open(&gifFile)){
        Serial.println("[GIF] loop(): failed to reopen GIF for looping");
        stop();
      }
    } else {
      stop();
    }
  } else {
    delay(1);
  }
}

void GifPlayer::handleGifDraw(GIFDRAW *pDraw){
  if (!strip) return;
  int fw = pDraw->iWidth;
  int fh = pDraw->iHeight;
  int fx = pDraw->iX;
  int fy = pDraw->iY;

  for (int y = 0; y < fh; y++){
    for (int x = 0; x < fw; x++){
      int srcIndex = y * fw + x;
      uint8_t idx = pDraw->pPixels[srcIndex];
      uint32_t rgb = pDraw->pPalette[idx];
      uint8_t r = (rgb >> 16) & 0xFF;
      uint8_t g = (rgb >> 8) & 0xFF;
      uint8_t b = rgb & 0xFF;

      int gx = fx + x;
      int gy = fy + y;
      int totalW = cfg.panelWidth * cfg.chainX;
      int totalH = cfg.panelHeight * cfg.chainY;
      if (gx < 0 || gx >= totalW) continue;
      if (gy < 0 || gy >= totalH) continue;

      int ledIndex = xyToIndex(gx, gy);
      if (ledIndex < 0 || ledIndex >= totalLeds) continue;
      strip->setPixelColor(ledIndex, strip->Color(r, g, b));
    }
  }
  strip->show();
}

int GifPlayer::xyToIndex(int gx, int gy){
  int panelW = cfg.panelWidth;
  int panelH = cfg.panelHeight;
  int pcol = gx / panelW;
  int prow = gy / panelH;
  int localX = gx % panelW;
  int localY = gy % panelH;

  bool topToBottom = (cfg.firstCorner == "TL" || cfg.firstCorner == "TR");
  bool leftToRight = (cfg.firstCorner == "TL" || cfg.firstCorner == "BL");

  int px = leftToRight ? localX : (panelW - 1 - localX);
  int py = topToBottom ? localY : (panelH - 1 - localY);

  int idxInPanel;
  if (cfg.serpentine){
    if ((py % 2) == 0){
      idxInPanel = py * panelW + px;
    } else {
      idxInPanel = py * panelW + (panelW - 1 - px);
    }
  } else {
    idxInPanel = py * panelW + px;
  }

  int panelsPerRow = cfg.chainX;
  int panelIndex = prow * panelsPerRow + pcol;
  int ledsPerPanel = panelW * panelH;
  int globalIndex = panelIndex * ledsPerPanel + idxInPanel;
  return globalIndex;
}
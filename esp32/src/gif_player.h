/*
  gif_player.h
  Clase GifPlayer para decodificar y reproducir GIFs en un panel WS2812
  Dependencias:
    - Adafruit_NeoPixel
    - AnimatedGIF (bitluni/AnimatedGIF)
*/

#ifndef GIF_PLAYER_H
#define GIF_PLAYER_H

#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#include <AnimatedGIF.h>
#include <FS.h>

struct LedPanelCfg {
  int pin;
  int panelWidth;
  int panelHeight;
  int chainX;
  int chainY;
  String firstCorner;
  bool serpentine;
};

// Declaración anticipada de GifPlayer para el friend
class GifPlayer;

// Declaración del callback como función externa C
extern "C" void GIFDrawCallback(GIFDRAW *pDraw);

class GifPlayer {
public:
  GifPlayer();
  ~GifPlayer();

  // Inicializa NeoPixel (pin y número de LEDs)
  bool begin(const LedPanelCfg &ledCfg);

  // Reproduce un GIF desde SPIFFS (path) en bucle o una vez
  bool playGif(const char *path, bool loop = true);

  // Detiene reproducción
  void stop();

  // Debe llamarse periódicamente desde loop() para procesar frames
  void loop();

  // Estado
  bool isPlaying() const { return playing; }
  String currentGif() const { return currentPath; }

  // Config del panel
  void setPanelConfig(const LedPanelCfg &ledCfg);

  // Declarar el callback como friend para que pueda acceder a los miembros privados
  friend void GIFDrawCallback(GIFDRAW *pDraw);

private:
  Adafruit_NeoPixel *strip = nullptr;
  LedPanelCfg cfg;
  int totalLeds = 0;

  AnimatedGIF *gif = nullptr;
  File gifFile;
  bool playing = false;
  bool loopMode = true;
  String currentPath;

  void handleGifDraw(GIFDRAW *pDraw);
  int xyToIndex(int gx, int gy);
  static GifPlayer *instance;
};

#endif // GIF_PLAYER_H
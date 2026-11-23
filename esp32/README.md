```markdown
# ESP32 GIF Visualizer — v0.3

Este proyecto (versión 0.3) proporciona:

- Interfaz web servida desde SPIFFS (carpeta `data/`) con pestañas (Bootstrap).
- Persistencia de configuración en NVS (Preferences) como JSON.
- Pestañas: Red, Horario, Panel LED, GIFs, Otros.
- NTP opcional y endpoint para forzar sincronización (POST /api/ntp_sync).
- Control de relé según horario (usa hora sincronizada vía NTP).
- Configuración de panel WS2812 (pin, ancho/alto panel, panels encadenados, esquina inicial, serpentina).
- Subida, lista y reproducción de GIFs animados en el panel LED:
  - Endpoints para subir/listar/servir/play/stop GIFs.
  - Reproductor implementado con AnimatedGIF (decodificación) y Adafruit_NeoPixel (salida).
- Logging serial exhaustivo para depuración.

Archivos incluidos (v0.3)
- platformio.ini
- src/main.cpp
- src/gif_player.h
- src/gif_player.cpp
- data/index.html
- README.md

Instalación / prueba local
1. Coloca los archivos en un directorio (misma estructura).
2. Subir contenido de `data/` a SPIFFS (PlatformIO):
   platformio run --target uploadfs
3. Compila y flashea:
   platformio run --target upload
4. Abre monitor serie:
   platformio device monitor
   Verás logs detallados del arranque, NVS, red y GIF playback.
5. Accede a la UI: http://<ip>/ (o al AP si está en modo AP).

Endpoints principales
- GET  /api/config         -> devuelve JSON de configuración (incluye "version": "0.3")
- POST /api/config         -> guarda configuración
- POST /api/ntp_sync       -> fuerza sincronización NTP
- POST /api/gifs/upload    -> sube GIF (multipart/form-data, campo "file")
- GET  /api/gifs           -> lista GIFs
- POST /api/gifs/play      -> { "name": "file.gif", "loop": true }
- POST /api/gifs/stop      -> detiene reproducción
- GET  /gifs/<file.gif>    -> sirve el archivo GIF

Limitaciones y recomendaciones
- GIFs: se recomiendan GIFs con resolución igual o menor al total de LEDs del panel; paleta pequeña para menor consumo de memoria.
- Si la reproducción falla por memoria o velocidad, reducir resolución o framerate del GIF.
- En producción, añade autenticación a la UI para proteger endpoints.
- Si tu relé es "active LOW", modifica setRelay() en src/main.cpp para invertir la lógica.

Licencia
- MIT (incluye código de librerías externas con sus propias licencias)

¿Siguientes pasos que puedo hacer por ti?
- Ajustar mapeo (column-major chaining), o añadir escalado automático de GIF al tamaño del panel.
- Cambiar a FastLED para aprovechar funciones de color y rendimiento.
- Añadir validaciones de upload y límites de tamaño/autorrechazo.

```
# Manual de usuario: Esp32-gif-visualizer

- **Versión documentada:** f66f0f4
- **Cubre:** `doc/tareas/2026-11-22-panel-raspberry-arreglos.md` hasta F1
- **Basado en:** `doc/analisis/2026-11-22-panel-raspberry-arreglos.md`, `doc/arquitectura/2026-11-22-panel-raspberry-arreglos.md`, `doc/tareas/2026-11-22-panel-raspberry-arreglos.md`, `doc/pruebas/2026-11-23-panel-raspberry-arreglos/informe-2026-11-23-135646.md`
- **Estado:** verificado
- **Última actualización:** 2026-11-23

## Introducción

Esp32-gif-visualizer muestra imágenes y GIF animados en paneles de LED. Tiene dos partes: el firmware del ESP32 y el panel de la Raspberry Pi. Esta primera versión del manual solo explica dónde está cada parte en el repositorio. El uso de cada parte se documentará al cerrar las fases que lo arreglan.

## Antes de empezar

- **Firmware del ESP32:** se abre y se compila desde la carpeta `esp32/`. Ahí están `platformio.ini`, `src/`, `data/` y `README.md`. Ya no están en la raíz del repositorio.
- **Panel de la Raspberry Pi:** el código vigente está en `raspberry-panel/panel/` (incluidos `configuracion.json`, `panel.service` y `apagado.sh`). Las imágenes originales están en `raspberry-panel/ficheros/`.
- **Archivos antiguos:** lo que ya no se usa, pero se conserva, está en `archivo/`. No hace falta para usar el producto.

## Primeros pasos

1. Abre la carpeta `esp32/` con PlatformIO para trabajar con el firmware. No abras la raíz del repositorio: el firmware no está allí y PlatformIO no encuentra el entorno `esp32dev`.
2. Para el panel, trabaja con la carpeta `raspberry-panel/panel/`.

Si ves un `platformio.ini` sin entornos en la raíz del repositorio, es una plantilla que PlatformIO crea al abrir la raíz. No es el firmware: el firmware está en `esp32/`.

## Uso

### Abrir el firmware del ESP32

Para qué sirve: compilar o cargar el firmware del ESP32.

1. Abre PlatformIO y elige la carpeta `esp32/` del repositorio.
2. En la lista de entornos debe aparecer `esp32dev`.

### Abrir el código del panel de la Raspberry Pi

Para qué sirve: revisar o modificar el programa que muestra las imágenes en el panel.

1. Ve a la carpeta `raspberry-panel/panel/`.
2. Los archivos `.py` son el programa. `configuracion.json` contiene la configuración que lee el panel.
3. Las imágenes están en `raspberry-panel/ficheros/`, con los nombres `banner1.png` a `banner12.png`. La subcarpeta `iconos/` no la muestra el panel: solo se leen los `.png` y `.gif` del primer nivel.

### Encontrar un archivo antiguo

Para qué sirve: recuperar material que ya no forma parte del producto.

1. Busca el archivo en `archivo/`. Están los archivos que no tenían otra copia, con el mismo contenido. Las copias duplicadas se eliminaron; el original está en `raspberry-panel/` o en `archivo/`.

## Referencia

No aplica.

## Mensajes y errores

No aplica.

## Solución de problemas

- **PlatformIO no muestra el entorno `esp32dev`.** Causa probable: se ha abierto la raíz del repositorio. Qué hacer: abre la carpeta `esp32/`.
- **No encuentras el código del panel.** Causa probable: la ruta antigua `panel/`. Qué hacer: el código está en `raspberry-panel/panel/`.

## Limitaciones conocidas

- La Raspberry Pi ejecuta el panel desde `/home/pi/panel` y lee las imágenes de `/home/pi/ficheros` (clave `directorio` de `configuracion.json`). Cambiar `raspberry-panel/ficheros/` no cambia lo que muestra la Pi. Para que la Pi use lo que hay en `raspberry-panel/` hay que copiarlo a esas carpetas; el procedimiento se documentará con el README de despliegue (F6).
- Este manual no documenta todavía el comportamiento del panel ni del firmware: se añadirá fase a fase.
- La compilación del firmware tras moverlo no está verificada por pruebas hasta la entrega (PF-08, aplazado). La compilación de T-05 se comprobó a mano, no con un caso de prueba.

## Trazabilidad

| Sección | Requisitos | Casos de prueba |
|---|---|---|
| Antes de empezar | RF-1, RF-3, RF-4 | PF-01, PF-04, PF-07 |
| Abrir el firmware del ESP32 | RF-4 | PF-09, PF-10 |
| Abrir el código del panel de la Raspberry Pi | RF-1, RF-4 | PF-01, PF-07 |
| Encontrar un archivo antiguo | RF-2, RF-3 | PF-03, PF-04 |
| Solución de problemas | RF-1, RF-4 | PF-01, PF-07 |

## Cambios

| Fecha | Versión documentada | Cambio |
|---|---|---|
| 2026-11-23 | f66f0f4 | Primera versión: ubicación del firmware ESP32 (`esp32/`), del panel (`raspberry-panel/`) y de `archivo/` (F1). |

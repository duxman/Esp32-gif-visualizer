# Diseño: Panel LED de Navidad en Raspberry Pi (Python)

- **Alcance analizado:** `panel/` de la raíz (versión nueva), `navidad/panel/` y `navidad/ficheros navidad/panel/` (versión antigua), `panel/animation_panel.log`, carpetas de imágenes (`ficheros/`, `navidad/**`) solo por listado y muestreo.
- **Commit analizado:** `e23949d` (instantánea inicial, 2026-11-14); el código leído el 2026-11-14 es el de ese commit.
- **Estado:** validado
- **Aprobación:** 2026-11-14, aprobado por el usuario tras dos rondas con el Cuestionador técnico (0 objeciones abiertas)
- **Última sesión:** 2026-11-14

Índice y diagnóstico: [indice.md](indice.md). El otro sistema: [esp32-gif-visualizer.md](esp32-gif-visualizer.md).

## Finalidad

- Programa Python para Raspberry Pi que muestra en bucle las imágenes PNG y GIF de una carpeta en un panel WS2812. `leído`: `panel/LedMatrixAnimation.py:69-143`.
- Los PNG anchos se desplazan horizontalmente (pancartas); los GIF animados se reproducen con sus tiempos. `leído`: `panel/Animation.py:74-80`, `panel/Animation.py:126-177`.
- Uso: decoración navideña y apoyo visual de un juego de intercambio de regalos. `deducido`: pancartas «Feliz navidad · Felices Fiestas» (`ficheros/banner1.png`) e imágenes `regalo`, `robo`, `ladron`, `cambiar`, `pasar`, `premio` en `navidad/ficheros navidad/`.
- Estuvo en uso real. `observado` en `panel/animation_panel.log`: ejecuciones del 2025-12-06 al menos hasta el 2025-12-09, con 864 LEDs y `/home/pi/ficheros/banner1..12.png`. El usuario confirma que funcionó y que el producto sigue vivo (`confirmado`, P-1, 2026-11-14).
- Ciclo de uso: la Pi se apagaba sola unas horas después de encenderse, para no tener el panel encendido todo el rato (`confirmado`, P-9, 2026-11-14); lo hacía `panel/apagado.sh` (5 h, `leído`: `panel/apagado.sh:2-3`) lanzado como servicio. El «arranque hacia las 23:01» que se veía en el log no es la hora real: ver R-8 y D-4.
- El código vigente es `panel/` de la raíz: es el último que el usuario tiene de la Pi (`confirmado`, P-2, 2026-11-14). No se ha comparado con lo que haya hoy en `/home/pi/panel`.
- Las imágenes originales son las de `ficheros/` de la raíz; las repetidas son copias (`confirmado`, P-3, 2026-11-14).

## Contexto y límites

| Entra / sale | Qué | Dónde |
|---|---|---|
| Entra | `configuracion.json` en `/home/pi/panel/` | `panel/Config.py:33` |
| Entra | Imágenes `*.png` y `*.gif` de `directorio` (`/home/pi/ficheros`) | `panel/LedMatrixAnimation.py:87-89`, `panel/configuracion.json:2` |
| Sale | Señal WS2812 en `board.D18` (GPIO18) | `panel/AnimationServer.py:104` |
| Sale | Log rotativo `animation_panel.log` (25 MB × 5) junto al código | `panel/LedMatrixAnimation.py:18-26` |
| Sale | En modo DEBUG, ventanas con cada frame (visor de imágenes del sistema) | `panel/AnimationServer.py:381-384` |
| Despliegue | Servicio systemd con venv `/home/pi/venv`; en la Pi corría con el usuario `pi` (`confirmado`, P-2), aunque el archivo dice `User=owner` (Z-8) | `panel/panel.service:8-14` |
| Despliegue | Servicio de apagado que ejecutaba `apagado.sh` (espera 5 h y `sudo shutdown -h now`) al encenderse la Pi (`confirmado`, P-9). Su archivo de servicio no está en el repositorio (Z-12) | `panel/apagado.sh:1-3` |
| Entra | Encendido de la Pi: por un medio externo al código, sin identificar (D-4) | — |

## Módulos

| ID | Módulo | Ruta | Responsabilidad | Certeza | Cobertura |
|---|---|---|---|---|---|
| M-1 | Principal | `panel/LedMatrixAnimation.py` | Carga configuración, crea panel y servidor, busca archivos y hace el bucle infinito | leído | entendido |
| M-2 | Configuración | `panel/Config.py`, `panel/configuracion.json` | Lee el JSON con ruta fija | leído | entendido |
| M-3 | Geometría | `panel/Panel.py` | Calcula la tabla píxel → LED (serpentina, paneles, origen arriba o abajo) | leído | entendido |
| M-4 | Animación | `panel/Animation.py` | Frames de GIF o recortes desplazados de PNG | leído | entendido |
| M-5 | Salida | `panel/AnimationServer.py` | NeoPixel, prueba de paneles, pinta frames, modo prueba en ventana | leído | entendido |
| M-6 | Despliegue | `panel/panel.service`, `panel/apagado.sh` | Arranque como servicio (usuario real `pi`, P-2); `apagado.sh` corría como servicio y apagaba la Pi 5 h después de encenderse (P-9). El servicio de apagado no está en el repositorio; qué enciende la Pi cada día no se sabe (D-4) | leído | entendido |
| M-7 | Versión antigua | `navidad/panel/`, `navidad/ficheros navidad/panel/` | Solo PNG, desplazamiento de 1 px, sin logging. Las dos copias son idénticas en código y configuración (hash); solo difieren sus `.idea/`. Sustituida por `panel/` (P-2) | observado | entendido |
| M-8 | Imágenes | `ficheros/`, `navidad/**` | Pancartas, iconos 18 px, imágenes del juego, fuentes `.pdn` y de banco de imágenes. Originales en `ficheros/` y repetidas = copias (P-3). Duplicados medidos por hash en [indice.md](indice.md#duplicados-de-imágenes). Los únicos y las versiones antiguas van a `archivo/` sin borrar nada (P-10) | observado | entendido |

## Funcionalidades

| ID | Funcionalidad (comportamiento observable) | Dónde | Certeza | Evidencia |
|---|---|---|---|---|
| F-1 | Al arrancar, si DEBUG = 0, enciende cada panel 2 s en rojo, verde, azul o amarillo | `panel/AnimationServer.py:132-174`, `panel/LedMatrixAnimation.py:122-124` | leído | `time.sleep(2)` en `panel/AnimationServer.py:166` |
| F-2 | Recorre primero todos los PNG y luego los GIF del directorio, en orden de `glob`, sin fin | `panel/LedMatrixAnimation.py:87-89`, `panel/LedMatrixAnimation.py:126-141` | leído | `while(1)` |
| F-3 | PNG: frames del ancho del panel desplazados 5 px, 250 ms cada uno con la configuración actual | `panel/Animation.py:51`, `panel/Animation.py:64`, `panel/Animation.py:165-176` | leído | Con 48 de ancho, `banner1.png` de 408 px da (408 − 48) / 5 + 1 = 73 frames, igual que el log (`panel/animation_panel.log:8985-8988`). Con un solo panel de 24 de ancho daba 77 (`panel/animation_panel.log:33-35`) |
| F-4 | GIF animado: todos sus frames en RGB, con su duración (100 ms por defecto) | `panel/Animation.py:105-124` | leído | `panel/Animation.py:118` |
| F-5 | Repeticiones distintas para GIF (3) y estáticos (1) | `panel/LedMatrixAnimation.py:132` | leído | `panel/configuracion.json:3-4` |
| F-6 | Los píxeles negros no se pintan (el strip se limpia antes de cada frame) | `panel/AnimationServer.py:305`, `panel/AnimationServer.py:322` | leído | `colourTuple(...) != 0` |
| F-7 | Modo DEBUG = 1: abre una ventana por frame escalado ×10 en vez de usar LEDs | `panel/AnimationServer.py:343-394` | leído | `display_frame.show(...)` |
| F-8 | En Windows o sin librerías de hardware, modo simulación (no pinta) | `panel/AnimationServer.py:21-33` | leído | `HARDWARE_AVAILABLE = False` |
| F-9 | Un `.gif` no animado no muestra nada | `panel/Animation.py:74-80` | deducido | Solo se generan frames si `is_animated`; los no-GIF van a `generateFrames` |

## Flujos

1. systemd espera 4 s y lanza `/home/pi/venv/bin/python3 /home/pi/panel/LedMatrixAnimation.py` (`panel/panel.service:7-11`).
2. `Config("configuracion.json")` lee `/home/pi/panel/configuracion.json` (`panel/Config.py:33`).
3. `Panel(...)` calcula tamaños; `AnimationServer` crea el NeoPixel de 864 LEDs; `calculateMatrix()` crea la tabla (`panel/LedMatrixAnimation.py:57-61`).
4. Busca PNG y GIF; prueba de paneles (F-1).
5. Bucle: por cada archivo crea `Animation` (decodifica entero en memoria) y lo reproduce `repeticiones` veces: limpia, recorre cada píxel `(x, y)`, `matrix_index = y * ancho_total + x`, LED `= matriz[matrix_index]`, `show()`, espera la duración (`panel/AnimationServer.py:300-338`).
6. Si cae, systemd lo relanza a los 10 s (`panel/panel.service:9-10`).

## Datos y estado

- `configuracion.json` (`panel/configuracion.json`): `directorio` `/home/pi/ficheros`, `repeticiones` 1, `repeticiones_gif` 3, `ancho` 24, `alto` 18, `panel_hor` 2, `panel_ver` 1, `primer_led` LEFT, `posicion_vertical` BOTTOM, `velocidad` 0.25, `DEBUG` 0.
- Obligatorias: `directorio`, `repeticiones`, `ancho`, `alto`, `panel_hor`, `panel_ver`, `primer_led`, `velocidad`. Opcionales: `repeticiones_gif`, `posicion_vertical` (BOTTOM), `DEBUG` (0) (`panel/Config.py:35-45`).
- `Panel.matriz`: lista plana fila a fila del lienzo total → índice de LED.
- Sin estado persistente; el log es la única salida escrita.
- Tamaño de lo reproducido (`observado` en el log): frames de 48×18 con 2 paneles; pancartas de 18 px de alto y varios cientos de ancho (p. ej. `banner4.png` 379×18, `panel/animation_panel.log:12047`); como máximo 151 frames por pancarta PNG en la parte legible del log (`panel/animation_panel.log:301`). Cada animación se genera entera en memoria antes de reproducirla (flujo, paso 5).

## Contratos externos

- Hardware: WS2812 en GPIO18 de la Pi, 2 paneles de 24×18 encadenados (864 LEDs). `leído` y `observado` en el log («inicilizamos ledstrip 864»).
- Cableado: primer LED abajo; filas en serpentina con la primera hacia la derecha si `primer_led` = LEFT; paneles con desplazamiento `(panel_v * panel_hor + panel_h) * 432` (`panel/Panel.py:49-85`).
- Color: `colourTuple` recibe el píxel en orden (R, G, B) de `frame.getpixel` (`panel/AnimationServer.py:319-324`; en la prueba de paneles, `(255,0,0)` para rojo, `:142`, `:163`) y hace `red = rgbTuple[1]`, `green = rgbTuple[0]`, `(green << 16) + (red << 8) + blue` (`panel/AnimationServer.py:238-241`, `leído`). Los dos cambios de nombre se anulan: el entero resultante es `(R << 16) + (G << 8) + B`, el 0xRRGGBB estándar, **sin intercambio** de rojo y verde (`leído`; corregido el 2026-11-14, antes decía que el código intercambiaba R y G). Los nombres y los docstrings (`:216-237`) dicen lo contrario de lo que hace el código. `colour()` (`:192`) y `colourrgb()` (`:214`), que sí reordenan, no se usan (`leído`: sin llamadas en `panel/`). El NeoPixel se crea sin `pixel_order` (`panel/AnimationServer.py:104`, `leído`); `ORDER = neopixel.GRB` en la línea 105 se asigna y no se usa (`leído`). Con la tira del usuario los colores se veían bien (`confirmado`, P-8, 2026-11-14). Que el orden por defecto de adafruit-circuitpython-neopixel sea GRB y que un entero se interprete como 0xRRGGBB es comportamiento de la librería, que no está en el repositorio: `deducido`, sin verificar. Si es así, la tira del usuario es GRB (`deducido`); lo confirma C-5. El orden de color es fijo (el de la librería por defecto) y no configurable (Z-6). El usuario pide que sea configurable (RU-3 de [indice.md](indice.md)).
- Dependencias: Pillow, `adafruit-circuitpython-neopixel`, `adafruit-blinka`, `rpi_ws281x` (`panel/AnimationServer.py:35-37`). No hay `requirements.txt`.
- Ruta `/home/pi/panel/` fija en el código (`panel/Config.py:33`).

## Reglas implícitas

| ID | Regla | Dónde | Certeza | Evidencia |
|---|---|---|---|---|
| R-1 | Desplazamiento de 5 px por frame | `panel/Animation.py:51` | leído | `PIXEL_SHIFT = 5` |
| R-2 | `velocidad` en segundos se convierte en ms por frame de PNG | `panel/Animation.py:64` | leído | `int(velocidad * 1000)` |
| R-3 | Duración por defecto de un frame GIF: 100 ms | `panel/Animation.py:118` | leído | `info.get('duration', 100)` |
| R-4 | El negro puro se trata como transparente o apagado | `panel/AnimationServer.py:322` | leído | `!= 0` |
| R-5 | La prueba de paneles solo tiene 4 colores | `panel/AnimationServer.py:141-158` | leído | `colores[panel_num]` |
| R-6 | Orden de reproducción: todos los PNG antes que los GIF, en el orden del sistema de archivos | `panel/LedMatrixAnimation.py:87-89` | leído | Dos `glob` concatenados |
| R-7 | La lista de archivos solo se lee al arrancar | `panel/LedMatrixAnimation.py:65` | leído | `buscarFicheros()` solo en `__init__` |
| R-8 | Las horas del log justo tras encender la Pi no son la hora real: retoman la última hora guardada y, segundos después, saltan a la hora real | `panel/animation_panel.log:8968-8997`, `panel/animation_panel.log:16688-16741`, `panel/animation_panel.log:24420-24422` | observado | La hora retrocede de 23:29:25 a 23:28:03 al rearrancar (líneas 8968-8969) y salta de 2025-12-06 23:28 a 2025-12-07 18:01 (8996-8997); lo mismo el 2025-12-07 (23:02 → 2025-12-08 18:02, 16740-16741). Que el mecanismo sea un reloj sin batería con hora guardada y NTP es `deducido` |

## Decisiones deducidas

| ID | Qué parece decidido | Porqué probable | Certeza |
|---|---|---|---|
| D-1 | La versión de `panel/` sustituye a la de `navidad/panel/` | Añade GIF, logging, `posicion_vertical` y paneles en vertical; mismo mapeo con LEFT y BOTTOM. Por hash, los 7 archivos de código, servicio y configuración de `panel/` difieren de los de las copias antiguas. El usuario confirma que `panel/` es el último código (P-2, 2026-11-14) | confirmado |
| D-2 | Modo simulación para desarrollar en Windows | `panel/AnimationServer.py:20-33`; `__pycache__` de cpython-313 | supuesto |
| D-3 | Apagado automático 5 h después de arrancar, para no tener el panel encendido todo el rato | `panel/apagado.sh:2-3`; el usuario: «era un servicio que apagaba la raspberry a las x horas de encenderse para no tener el panel todo el rato funcionando» (P-9, 2026-11-14). El log es coherente: tras el salto a la hora real (R-8), las sesiones van de ~18:01 a ~23:00 (`panel/animation_panel.log:8997`, `16688`; `16741`, `24420`) | confirmado |
| D-4 | La Pi se encendía a diario hacia las 18:00 por un medio externo al código (temporizador de corriente, enchufe programable o a mano) | Las sesiones reales empiezan a las 18:01 y 18:02 (`panel/animation_panel.log:8997`, `16741`) tras el salto de R-8; en el repositorio no hay nada que encienda la Pi. El usuario no lo ha dicho (P-9). Lo confirmaría el usuario o la configuración de la Pi | supuesto |

## Zonas frágiles

| ID | Zona | Riesgo | Dónde |
|---|---|---|---|
| Z-1 | `from venv import logger` | Funciona de casualidad (logger del módulo `venv`); sus trazas no llegan al log (0 apariciones en la parte legible) | `panel/Panel.py:2` |
| Z-2 | PNG sin convertir a RGB | Un PNG con paleta devuelve `int` en `getpixel` y `colourTuple` falla; con RGBA se ignora el alfa | `panel/Animation.py:172`, `panel/AnimationServer.py:319-324` |
| Z-3 | GIF no animado | No se muestra (F-9) | `panel/Animation.py:74-80` |
| Z-4 | GIF mayor que el panel | No se redimensiona; `y * ancho_total + x` desborda a la fila siguiente | `panel/AnimationServer.py:311-314` |
| Z-5 | Más de 4 paneles | `IndexError` en la prueba y en el contador | `panel/AnimationServer.py:158`, `panel/AnimationServer.py:308` |
| Z-6 | Orden de color | Código engañoso: `colourTuple` no intercambia colores (devuelve 0xRRGGBB), pero sus variables y su docstring dicen GRB; `colour()` y `colourrgb()` sí reordenan y no se usan; `ORDER` (línea 105) aparenta configurar el orden y no se usa. El orden real es el por defecto de la librería, que con la tira actual se ve bien (P-8). Quien «arregle» `colourTuple` según su docstring, use `colour()` o pase `pixel_order` cambiará los colores. Con otra tira, el orden no se puede ajustar sin tocar código (RU-3) | `panel/AnimationServer.py:104-105`, `panel/AnimationServer.py:176-242` |
| Z-7 | Tres `RotatingFileHandler` sobre el mismo archivo | Rotación conflictiva; el log tiene bytes nulos (cortes de corriente probables) | `panel/LedMatrixAnimation.py:18-26`, `panel/Animation.py:10-18`, `panel/AnimationServer.py:10-18` |
| Z-8 | Rutas fijas `/home/pi` con `User=owner` | Error aparente, confirmado por el usuario (P-2): el servicio corría con `pi`, así que `User=owner` en el archivo del repositorio no es lo desplegado; instalarlo tal cual fallaría si no existe `owner`. Las rutas fijas rompen además la simulación en Windows | `panel/Config.py:33`, `panel/panel.service:8-14` |
| Z-9 | `except:` desnudo al cargar | Oculta la causa real del error | `panel/Animation.py:81-82` |
| Z-10 | Versión antigua: `resize` con división float | `TypeError` en Python 3 si la altura no coincide | `navidad/panel/Animation.py:22` |
| Z-11 | Sin pruebas ni `requirements.txt` | Cualquier cambio a ciegas | `panel/` |
| Z-12 | Despliegue incompleto en el repositorio | El servicio que lanzaba `apagado.sh` no está; reinstalar desde el repositorio no reproduce el apagado. `sudo shutdown` necesita permisos sin contraseña para el usuario del servicio | `panel/apagado.sh:3` |
| Z-13 | Horas del log poco fiables | Las primeras líneas de cada arranque llevan una hora falsa (R-8); quien lea el log puede sacar conclusiones erróneas de horarios | `panel/animation_panel.log` |

## Preguntas abiertas

| ID | Pregunta | Por qué importa | Bloquea | Respuesta |
|---|---|---|---|---|
| P-2 | ¿Lo que corre en la Pi es `panel/` de la raíz? ¿Puede haber allí una versión más nueva? ¿El servicio corre como `owner` o como `pi`? | Fija cuál es la versión buena | M-1, M-6, M-7 | 2026-11-14: El último código de la Raspberry que tiene es `panel/` de la raíz. El servicio corría con el usuario `pi`; `User=owner` en `panel.service` es un error. |
| P-3 | ¿El conjunto vigente de imágenes es `ficheros/` de la raíz? ¿Se usan las imágenes del juego? ¿Se pueden archivar las copias? | Decide qué se conserva | M-8 | 2026-11-14: Las imágenes repetidas son copias; las originales son las de `ficheros/` de la raíz. Sobre las imágenes del juego no contestó: pasa a P-10. |
| P-8 | ¿La tira es de orden RGB o GRB? ¿Los colores se ven bien? | Confirma o desmiente Z-6 | M-5 | 2026-11-14: En la Pi los colores se veían bien. No dijo el orden de la tira. Pide que el orden de color sea configurable en la Pi (RU-3, requisito, no comportamiento actual). Releído el código, no hay intercambio R↔G (Contratos externos): con el orden por defecto de la librería (GRB, `deducido`) la tira sería GRB. Z-6 queda como código engañoso y orden no configurable |
| P-9 | ¿Se usa `apagado.sh` (cron u otro)? ¿Qué arranca la Pi a diario hacia las 23:00 (temporizador de corriente)? | Explica el ciclo de uso | M-6 | 2026-11-14: `apagado.sh` era un servicio que apagaba la Pi a las X horas de encenderse (5 h en el código), para no tener el panel siempre encendido (D-3 confirmada). Del arranque diario no dijo nada. Las 23:00 resultan ser una hora falsa del log (R-8); el arranque real es hacia las 18:00 y lo que lo provoca sigue sin saberse: queda como supuesto D-4, no bloquea |
| P-10 | ¿Qué hacemos con lo que no tiene copia en `ficheros/`: las imágenes del juego (`regalo`, `robo`, `ladron`, `cambiar`, `pasar`, `premio`… en `navidad/ficheros navidad/`), los recortes de `navidad/1/`, los iconos de `navidad/ficheros navidad/iconos/` (41), `navidad/globos/1..3.png`, las variantes de `navidad/iconos/banners/old/`, los `.pdn` y `navidad/ficheros/banner7-1.png` y `banner8-1.png`? ¿Se conservan como originales, se archivan o sobran? | Son los únicos archivos que se perderían al quitar las copias; decide qué se conserva en la reorganización (opción A) | M-8 | 2026-11-14: Todo eso (imágenes del juego, `navidad/1/`, iconos de «ficheros navidad», `globos/`, `banners/old`, los `.pdn`, `banner7-1`/`banner8-1` y las versiones antiguas de banner1/7/8/9) va a una carpeta `archivo/`; no se tira nada; el usuario decidirá después. Es una decisión para el plan de reorganización: aún no se ha movido nada |

P-1 y P-5 son comunes y están en [indice.md](indice.md) (respondidas el 2026-11-14).

## Pruebas de caracterización

| ID | Comportamiento que fija | Zona | Cómo | Estado |
|---|---|---|---|---|
| C-1 | `Panel.calculateMatrix` con 24×18×2, LEFT, BOTTOM, igual a la versión antigua | Z-1 | Unitaria (pytest, sin hardware) | propuesta |
| C-2 | `generateFrames`: 408×18 da 73 frames de 48×18 con 2 paneles (77 de 24×18 con uno), o del ancho de la imagen si es menor | Z-2 | Unitaria con imagen sintética | propuesta |
| C-3 | `colourTuple((r, g, b))` devuelve `(r << 16) + (g << 8) + b` (p. ej. `(255, 0, 0)` → `0xFF0000`) | Z-6 | Unitaria | propuesta |
| C-4 | `startAnimation` con una tira falsa: qué LED recibe cada píxel | Z-4 | Unitaria con doble de NeoPixel | propuesta |
| C-5 | Prueba de paneles (F-1) en la tira real: panel 0 rojo, panel 1 verde. Fija el orden de color vigente antes de hacerlo configurable (RU-3) | Z-6 | Placa, observación manual | propuesta |

## Cómo trabajar con este código

- Despliegue (`leído`): copiar a `/home/pi/panel/`, venv en `/home/pi/venv`, servicio `panel/panel.service`. En la Pi el servicio corría con el usuario `pi`, no con el `owner` del archivo (`confirmado`, P-2; Z-8). Instalación sugerida en comentarios: `pip3 install rpi_ws281x adafruit-circuitpython-neopixel` (`panel/AnimationServer.py:36-37`).
- Los módulos se importan por nombre plano: hay que ejecutar desde `panel/`.
- No se versionan bien: `.gitignore` no excluye `__pycache__/`, `*.log` ni `.idea/`. En la instantánea `e23949d` se dejó fuera `panel/__pycache__/` (queda sin seguimiento), pero entraron `panel/animation_panel.log`, los `__pycache__/` y los `.idea/` de las copias antiguas (`observado`, `git status`).
- No tocar `Panel` ni `AnimationServer.startAnimation` sin C-1 y C-4, ni el orden de color (`colourTuple`, creación del NeoPixel) sin C-3 y C-5.
- Para leer horarios en el log, descartar las líneas anteriores al salto de hora de cada arranque (R-8).

## Sesiones

| Fecha | Analizado | Queda pendiente |
|---|---|---|
| 2026-11-14 | Explorar: las tres copias del código, configuración, servicio, log y listado de imágenes | Respuestas P-1, P-2, P-3, P-5, P-8, P-9; comparar por hash las copias; comparar con `/home/pi/panel` real |
| 2026-11-14 | Profundizar con órdenes autorizadas: instantánea git `e23949d`; hash de las tres copias del código y de las imágenes | Respuestas P-1, P-2, P-3, P-5, P-8, P-9; comparar con `/home/pi/panel` real; C-1 a C-4 sin hacer |
| 2026-11-14 | Incorporar respuestas P-1, P-2 y P-3: versión vigente `panel/` (D-1 confirmada, M-7 entendido), usuario `pi` (Z-8), originales en `ficheros/` | P-8, P-9 y P-10 (resto de P-3); comparar con `/home/pi/panel` real, si se puede; C-1 a C-4 sin hacer |
| 2026-11-14 | Incorporar respuestas P-8, P-9 y P-10; relectura del log: hora falsa al arrancar (R-8), sesiones reales de ~18:00 a ~23:00 (D-3 confirmada, D-4 supuesto). M-6 y M-8 entendidos: 8 de 8. Propuesto `validado`, con el Cuestionador | Aprobación del usuario; D-4 (qué enciende la Pi), D-2 y el servicio de apagado (Z-12) sin confirmar, no bloquean; comparar con `/home/pi/panel`; C-1 a C-5 sin hacer |
| 2026-11-14 | Cuestionamiento en dos rondas: orden de color corregido (sin intercambio R↔G), 73 frames con 48 de ancho; acta con 0 objeciones abiertas. Propuesto `validado` | Aprobación del usuario; orden por defecto de la librería (deducido, C-5), D-4, D-2 y Z-12 sin confirmar; comparar con `/home/pi/panel`; C-1 a C-5 sin hacer |
| 2026-11-14 | Aprobación del usuario: documento `validado` | Orden por defecto de la librería (deducido, C-5), D-4, D-2 y Z-12 sin confirmar; comparar con `/home/pi/panel`; C-1 a C-5 sin hacer |

## Cambios

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-11-14 | Creación del documento | Encargo del Orquestador, modo explorar |
| 2026-11-14 | Commit analizado `e23949d`; M-7 y M-8 con hashes; nota de versionado | Encargo del Orquestador, modo profundizar (órdenes autorizadas) |
| 2026-11-14 | P-2 y P-3 respondidas; D-1 a `confirmado`; M-7 a `entendido`; Z-8 confirmado como error; nueva P-10 | Encargo del Orquestador, modo incorporar respuestas |
| 2026-11-14 | P-8, P-9 y P-10 respondidas. Finalidad con el ciclo de uso; color: Z-6 pasa de error aparente a acoplamiento, `ORDER` sin uso; D-3 confirmada; nuevos R-8, D-4, Z-12, Z-13 y C-5; M-6 y M-8 a `entendido`; se corrige «arrancando a diario hacia las 23:01», que era la hora falsa del log | Encargo del Orquestador, modo incorporar respuestas |
| 2026-11-14 | **Color corregido**: `colourTuple` devuelve 0xRRGGBB, no intercambia R y G (antes figuraba como `leído` el intercambio). Corregidos Contratos externos, Z-6, C-3 y la respuesta de P-8. F-3 y C-2: 73 frames con 48 de ancho (77 era con un panel de 24) | Acta del Cuestionador técnico, objeciones 1 y 2; comprobado en `panel/AnimationServer.py:176-242`, `:319-324` y `panel/animation_panel.log:19`, `:33-35`, `:8985-8988` |
| 2026-11-14 | «Contratos externos»: `colour()` y `colourrgb()` reordenan y no se usan | Acta del Cuestionador técnico, ronda 2, menor 4 |
| 2026-11-14 | Estado `en curso` → `validado` | Aprobación expresa del usuario («sí, aprobados»), transmitida por el Orquestador, modo actualizar |

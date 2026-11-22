# Índice de diseño y diagnóstico del repositorio

- **Fecha:** 2026-11-14 · **Estado:** todas las preguntas respondidas (P-1 a P-10); los dos documentos, `validado` (aprobados por el usuario el 2026-11-14, tras dos rondas con el Cuestionador técnico y 0 objeciones abiertas) · **Control de versiones:** git local desde el 2026-11-14; instantánea inicial `e23949d` («Instantánea inicial del estado heredado»), sin remoto.

Este índice no es un documento de diseño: reúne los dos sistemas del repositorio, el diagnóstico del desorden y las preguntas comunes. Desde la instantánea solo se ha eliminado `navidad/1.bat` (ver H-6); no se ha movido nada.

Los dos productos siguen vivos (`confirmado`, P-1, 2026-11-14): el panel de la Raspberry Pi funcionó; el firmware ESP32 fue una prueba que el usuario abandonó y no sabe si llegó a funcionar.

| Sistema | Documento | Ubicación del código |
|---|---|---|
| Visualizador de GIFs para ESP32 (firmware PlatformIO) | [esp32-gif-visualizer.md](esp32-gif-visualizer.md) | `platformio.ini`, `src/`, `data/`, `README.md` |
| Panel LED de Navidad en Raspberry Pi (Python) | [panel-raspberry.md](panel-raspberry.md) | `panel/` (vigente), `navidad/panel/` y `navidad/ficheros navidad/panel/` (antiguos) |

Los dos sistemas no comparten código; solo la idea de pintar imágenes en paneles WS2812.

## Diagnóstico

| ID | Hallazgo | Evidencia | Certeza |
|---|---|---|---|
| H-1 | La raíz mezcla los dos proyectos: `panel/` y `ficheros/` son de la Raspberry Pi, no del ESP32 | Nada de `src/` ni `data/` los referencia; el log de `panel/` usa `/home/pi/ficheros/banner1..12.png`, los mismos nombres que `ficheros/`. El usuario confirma que `panel/` es el último código de la Pi (P-2) y que las imágenes originales son las de `ficheros/` (P-3) | confirmado (P-2, P-3, 2026-11-14) |
| H-2 | La versión buena del código Python es `panel/` de la raíz | Es la más completa y la única con uso registrado (`panel/animation_panel.log`, diciembre de 2025). El usuario: «el último código de la Raspberry que tengo es `panel/` de la raíz». No se ha comparado con lo que haya hoy en `/home/pi/panel` de la propia Pi | confirmado (P-2, 2026-11-14) |
| H-3 | `navidad/panel/` y `navidad/ficheros navidad/panel/` son la misma versión antigua; `panel/` de la raíz es otra versión | `sha256sum`: los 7 archivos de código, servicio y configuración (`Animation.py`, `AnimationServer.py`, `Config.py`, `LedMatrixAnimation.py`, `Panel.py`, `panel.service`, `configuracion.json`) son idénticos entre las dos copias antiguas y distintos todos en `panel/`. `diff -rq` entre las antiguas: solo difieren los metadatos del IDE `.idea/` (`.gitignore`, `panel.iml`, `workspace.xml`; `misc.xml` solo en `navidad/panel/`). Ver «Comandos ejecutados» | observado |
| H-4 | Imágenes repetidas: 257 archivos de imagen y `.pdn` en `ficheros/` y `navidad/`, con solo 133 contenidos distintos | `sha256sum` agrupado por contenido; detalle en «Duplicados de imágenes» | observado |
| H-5 | Archivos sueltos en `navidad/`: `1.png`, `2.jpeg`…`7.png` son hojas de iconos de banco de imágenes (fuentes); `banner1.png` suelto, idéntico a `ficheros/banner1.png` (hash) | Muestreo visual; hash | deducido (hojas) · observado (`banner1.png`) |
| H-6 | `navidad/1.bat` no era un script: era una nota con 11 equipos `wled-WLED*`, sus IP 192.168.1.x y fragmentos de MAC. **Eliminado** del árbol de trabajo por el Programador Python con autorización del usuario (P-5); se recupera de la instantánea (`git show e23949d:navidad/1.bat`), donde sigue con su contenido | `navidad/1.bat:1-13` en `e23949d` (leído antes del borrado); ausencia del archivo comprobada por listado el 2026-11-14 | leído (contenido) · observado (eliminado) |
| H-7 | Artefactos que no deberían versionarse: `panel/__pycache__/`, `__pycache__/` de las copias antiguas, `panel/animation_panel.log` (grande, con bytes nulos), `.idea/`, `.pdn` | `.gitignore` solo cubre `.pio` y cuatro entradas de `.vscode`; no excluye `__pycache__/`, `*.log` ni `.idea/`. En la instantánea se dejó fuera solo `panel/__pycache__/` (por ruta en `git add`); los `__pycache__/` de `navidad/**/panel/`, los `.idea/` y el log **sí entraron** en `e23949d` | observado |
| H-8 | Control de versiones creado: hay copia del estado heredado antes de reorganizar | `git init` y commit `e23949d3ac794f6fc4dc3f87fcbf6ec4e52dd226`, 408 archivos; sin push. Las carpetas vacías `navidad/3/` y `navidad/5/` no quedan en git (git no guarda carpetas vacías) | observado |
| H-9 | Documentación: el README solo habla del ESP32 y está envuelto en un bloque de código; no hay README de la Pi; `CLAUDE.md` tiene «Lenguajes» sin rellenar | `README.md:1`, `README.md:60` | leído |
| H-10 | El firmware ESP32 compila, pero no puede reproducir GIFs tal como está escrito | Compila: `pio run -e esp32dev` termina en SUCCESS (observado). Los defectos Z-1 a Z-5 de [esp32-gif-visualizer.md](esp32-gif-visualizer.md) son de ejecución, no de compilación: la compilación ni los confirma ni los desmiente (deducido) | observado (compila) · deducido (no reproduce) |
| H-11 | Despliegue de la Pi incoherente: `User=owner` con rutas `/home/pi`. El servicio corría con el usuario `pi`: `User=owner` es un error del archivo del repositorio | `panel/panel.service:8-14`, `panel/Config.py:33` | leído · confirmado (P-2, 2026-11-14) |
| H-12 | Carpetas vacías `navidad/3/` y `navidad/5/` | Listado | observado |
| H-13 | En el equipo hay varias instalaciones de PlatformIO Core (aviso «Obsolete PIO Core v6.1.19 is used (previous was 6.2.0)»); la compilación reinstaló `tool-scons` 4.40801.0 y quitó la 4.41101.0 en la instalación de PlatformIO del usuario (fuera del repositorio) | Salida de `pio run -e esp32dev` | observado |

## Opciones de reorganización (decide el usuario)

**Elegida por el usuario: opción A** (P-5, 2026-11-14). Es una preferencia para el plan de reorganización; todavía no se ha movido nada. El `git init` previo ya está hecho (H-8).

En todas, antes: `git init` con un commit de la situación actual y comparación por hash de los duplicados. Nada se borra sin aviso y autorización.

| Opción | Qué es | A favor | En contra |
|---|---|---|---|
| A | Un repositorio con `esp32/` y `raspberry-panel/`, una sola carpeta de imágenes y `archivo/` para lo antiguo | Separación clara; se conserva el arnés común | PlatformIO se abre en `esp32/` o con `pio run -d esp32`; `.pio` se regenera |
| B | ESP32 en la raíz; Python a `raspberry-panel/`; `navidad/` a `archivo/` | Lo que menos cambia para PlatformIO; el nombre del repositorio sigue cuadrando | La raíz sigue mezclando firmware, arnés y otro producto |
| C | Dos repositorios | Lo más limpio | Hay que duplicar el arnés de agentes |
| D | No mover código: README por proyecto, `.gitignore` y una nota de cuál es la versión buena | Sin riesgo | La confusión sigue |

En cualquiera: ~~renombrar `1.bat` a `.txt` o sacarlo del repositorio~~ (hecho: eliminado, H-6), y, si se puede, traer `/home/pi/panel` de la Pi para compararlo con `panel/` (el usuario confirma que `panel/` es lo último que tiene, P-2, pero no se ha comparado con la placa).

## Requisitos expresados por el usuario (para el análisis futuro)

No son comportamiento actual del código: son peticiones del usuario recogidas al responder las preguntas, para que las tome el Analista funcional.

| ID | Requisito expresado | Origen | Relación con el código actual |
|---|---|---|---|
| RU-1 | ESP32: el tamaño del panel debe ser configurable (el usuario tiene un panel de 24×18 y otros de 32×32) | P-4, 2026-11-14 | El firmware ya guarda `led.panelWidth` y `led.panelHeight` desde la web (`src/main.cpp:181-214`, `data/index.html:335-341`, `leído`), pero la reproducción no está observada en placa (F-13 `deducido`) |
| RU-2 | ESP32: el pin de datos del panel debe ser configurable | P-4, 2026-11-14 | El firmware ya guarda `led.pin` desde la web (`leído`, mismas líneas); sin configurar queda en 0 (Z-13 de [esp32-gif-visualizer.md](esp32-gif-visualizer.md)) |
| RU-3 | Raspberry Pi: el orden de color debe ser configurable | P-8, 2026-11-14 | Hoy es fijo: `colourTuple` entrega 0xRRGGBB sin intercambiar colores, aunque sus nombres digan GRB (`panel/AnimationServer.py:238-241`, `leído`), y el NeoPixel se crea sin `pixel_order` (`panel/AnimationServer.py:104`), así que manda el orden por defecto de la librería (GRB, `deducido`, sin verificar); con la tira actual se ve bien (P-8). Ver Z-6 y C-5 de [panel-raspberry.md](panel-raspberry.md) |

## Dudas abiertas para el análisis

No las resuelve el análisis del código: son dudas del usuario que tendrán que decidir el análisis funcional y el diseño. Aquí solo van los hechos que ya se tienen, sin conclusión.

| ID | Duda | Origen | Hechos disponibles |
|---|---|---|---|
| V-1 | ¿Puede el ESP32 sustituir a la Raspberry Pi? El usuario duda de que tenga potencia de proceso y capacidad para hacer lo mismo | P-7, 2026-11-14 | Ver la tabla siguiente |

| Hecho | Valor | Certeza y evidencia |
|---|---|---|
| Panel de la Pi | 2 paneles de 24×18 = 864 LEDs; frames de 48×18 | `observado`: `panel/animation_panel.log:3`, `:118` |
| Contenido de la Pi | Sobre todo pancartas PNG de 18 px de alto y varios cientos de ancho (p. ej. 379×18); hasta 151 frames por pancarta; 250 ms por frame | `observado`: `panel/animation_panel.log:12047`, `:301`; `panel/configuracion.json` (`velocidad` 0.25) |
| Cómo reproduce la Pi | Genera todos los frames de una imagen en memoria antes de mostrarla | `leído`: `panel/Animation.py:126-177`, `panel/LedMatrixAnimation.py:126-141` |
| Tamaño de un frame de 48×18 en RGB de 3 bytes | 2 592 B; 151 frames = 391 392 B; una pancarta de 408×18 sin desplazar = 22 032 B | `deducido`: cálculo (ancho × alto × 3) |
| Refresco de 864 LEDs WS2812 a 800 kHz | ≈ 25,9 ms por `show()` (24 bits × 1,25 µs × 864), más el reset | `deducido`: cálculo a partir del protocolo; el firmware usa `NEO_KHZ800` (`src/gif_player.cpp:47`) |
| RAM del ESP32 (`esp32dev`) | 327 680 B de DRAM disponible para datos según el enlazador (no es la RAM total del chip); el firmware actual ocupa 48 728 B (14,9 %) de forma estática. Montículo libre en ejecución y PSRAM de la placa: sin medir, desconocidos | `observado`: `pio run -e esp32dev`, 2026-11-14 |
| Flash del ESP32 | Partición de aplicación 1 310 720 B, 890 553 B usados (67,9 %). Tamaño de la partición SPIFFS para las imágenes: sin medir | `observado`: misma compilación |
| Formatos del firmware ESP32 | Solo GIF (AnimatedGIF 1.4.7); no hay decodificador PNG entre las dependencias | `leído`: `platformio.ini:18-21` |
| Funcionamiento del firmware ESP32 | Nunca observado en placa; por el código, la reproducción no funciona tal como está | `deducido`: F-13, Z-1 a Z-5 de [esp32-gif-visualizer.md](esp32-gif-visualizer.md) |

## Preguntas comunes

| ID | Pregunta | Por qué importa | Respuesta |
|---|---|---|---|
| P-1 | ¿Son dos productos (ESP32 con web, relé y GIFs; Pi con el panel navideño de 2×24×18)? ¿Siguen vivos los dos? ¿Con cuál quieres seguir? | Finalidad de todo lo demás | 2026-11-14: Los dos productos siguen vivos. El ESP32 fue una prueba que el usuario abandonó; no sabe si llegó a funcionar. La Raspberry Pi sí funcionó. |
| P-2 | Ver [panel-raspberry.md](panel-raspberry.md) | | 2026-11-14: respondida; detalle en [panel-raspberry.md](panel-raspberry.md) |
| P-3 | Ver [panel-raspberry.md](panel-raspberry.md) | | 2026-11-14: respondida en parte; lo que falta pasa a P-10 |
| P-4 | Ver [esp32-gif-visualizer.md](esp32-gif-visualizer.md) | | 2026-11-14: respondida en parte (relé sin respuesta); detalle en [esp32-gif-visualizer.md](esp32-gif-visualizer.md) |
| P-5 | ¿Qué opción de reorganización prefieres (A, B, C o D)? ¿Autorizas el `git init` previo? ¿De qué es `1.bat` y dónde debe ir? | Decide el plan | 2026-11-14: Opción A (un repositorio con `esp32/` y `raspberry-panel/`). `git init` ya hecho (H-8). `navidad/1.bat` eliminado por el Programador Python con autorización; recuperable de `e23949d` (H-6). |
| P-6, P-7 | Ver [esp32-gif-visualizer.md](esp32-gif-visualizer.md) (relé; sustitución de la Pi) | | 2026-11-14: respondidas; el relé alimenta el panel (pin y polaridad desconocidos); la viabilidad pasa a V-1 |
| P-8, P-9 | Ver [panel-raspberry.md](panel-raspberry.md) (orden de color; `apagado.sh`) | | 2026-11-14: respondidas; requisito RU-3; el arranque diario queda como supuesto D-4 de [panel-raspberry.md](panel-raspberry.md) |
| P-10 | Ver [panel-raspberry.md](panel-raspberry.md) (imágenes del juego y archivos únicos fuera de `ficheros/`) | | 2026-11-14: todo lo que no tiene copia en `ficheros/` y las versiones antiguas de banner1/7/8/9 van a `archivo/`; no se tira nada; el usuario decidirá después |

## Duplicados de imágenes

Resultado de `sha256sum` sobre los PNG, JPEG, GIF y `.pdn` de `ficheros/` y `navidad/` (2026-11-14). `observado`.

El usuario confirma que las imágenes repetidas son copias y que las originales son las de `ficheros/` de la raíz (`confirmado`, P-3, 2026-11-14). Las imágenes del juego, los únicos de fuera de `ficheros/` (fila «Únicos»), `banner7-1`, `banner8-1`, `banners/old` y las versiones antiguas de banner1/7/8/9 van a una carpeta `archivo/`, sin tirar nada; el usuario decidirá después (`confirmado`, P-10, 2026-11-14). Aún no se ha movido nada.

| Grupo | Resultado |
|---|---|
| `ficheros/` frente a `navidad/ficheros/` | Idénticos archivo a archivo, incluido `iconos/` entero. `navidad/ficheros/` tiene además `banner7-1.png` y `banner8-1.png` (únicos) |
| `ficheros/iconos/` (iconos `n_18px`, `banners/banner1.png`, `example1.gif`, `example2.gif`) | Tres copias idénticas: `ficheros/iconos/`, `navidad/ficheros/iconos/`, `navidad/iconos/` |
| `navidad/iconos/` frente a `navidad/ficheros/iconos/` | Distintos en `banners/old/banner1`, `banner7`, `banner8`, `banner9` y `todos_capas.pdn`; solo en `navidad/iconos/banners/old/`: `banner11`, `banner12`, `logo.png`, `Sin título.png`. En `navidad/iconos/banners/old/`, `banner1`, `banner8`, `banner9`, `banner11` y `banner12` coinciden con los vigentes de `ficheros/` (no con los «old» de `ficheros/iconos/banners/old/`); `banner7` es único |
| Pancartas `banner2`…`banner6` y `banner10` | Iguales en 7 sitios: `ficheros/`, `ficheros/iconos/banners/old/`, `navidad/ficheros - copia/`, `navidad/ficheros navidad/`, `navidad/ficheros/`, `navidad/ficheros/iconos/banners/old/`, `navidad/iconos/banners/old/` |
| Pancartas `banner1`, `banner7`, `banner8`, `banner9` | Hay dos versiones de cada una: la vigente de `ficheros/` y una antigua, igual en `ficheros/iconos/banners/old/`, `navidad/ficheros - copia/`, `navidad/ficheros navidad/` y `navidad/ficheros/iconos/banners/old/` |
| `navidad/ficheros - copia/` (10 archivos) | Todo su contenido está repetido en `navidad/ficheros navidad/` y en `ficheros/iconos/banners/old/` |
| Únicos (sin copia) | `navidad/1/` (18 recortes; `2 (15).png` y `2 (20).png` son iguales entre sí), `navidad/ficheros navidad/iconos/` (41), imágenes del juego y `.pdn` de `navidad/ficheros navidad/`, `navidad/1.png`…`7.png`, `navidad/globos/1..3.png`, `navidad/iconos/todos_capas.pdn` |
| `data/` (ESP32) | Solo `index.html`; ninguna imagen |

## Comandos ejecutados

Autorizados por el usuario el 2026-11-14.

| Orden | Resultado |
|---|---|
| `git init` + `git add` (todo salvo `panel/__pycache__`) + `git commit` | Commit `e23949d3ac794f6fc4dc3f87fcbf6ec4e52dd226`, 408 archivos, «Instantánea inicial del estado heredado». Sin push. Avisos de fin de línea LF→CRLF en los archivos del arnés y de `doc/` (sin efecto en el contenido guardado) |
| `sha256sum` de las tres copias del código Python y de las imágenes | H-3, H-4 y «Duplicados de imágenes» |
| `pio run -e esp32dev` | SUCCESS en 31 s. RAM 14,9 % (48 728 de 327 680 B), flash 67,9 % (890 553 de 1 310 720 B). Avisos: H-13. Detalle en [esp32-gif-visualizer.md](esp32-gif-visualizer.md) |
| `py -3 tools/check_diseno.py <doc> --resumen` sobre los dos documentos | 0 errores y 0 avisos en ambos. ESP32: 6 de 6 módulos entendidos. Raspberry Pi: 5 de 8 (M-6, M-7 y M-8 leídos, a la espera de P-2, P-3 y P-9) |

## Cambios

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-11-14 | Respuestas P-1 a P-5 incorporadas: H-1, H-2 y H-11 confirmados; H-6 eliminado; opción A elegida; requisitos RU-1 y RU-2; nueva P-10 con lo que quedó sin responder de P-3 | Encargo del Orquestador, modo incorporar respuestas |
| 2026-11-14 | Respuestas P-6 a P-10 incorporadas: requisito RU-3; duda de viabilidad V-1 con sus hechos medidos, sin conclusión; destino `archivo/` de los únicos (P-10). Los dos documentos, propuestos `validado` | Encargo del Orquestador, modo incorporar respuestas |
| 2026-11-14 | RU-3 corregido: el código de la Pi no intercambia rojo y verde. V-1: la cifra de RAM es la DRAM de datos del enlazador; PSRAM desconocida | Acta del Cuestionador técnico (objeción 1 y nota) |
| 2026-11-14 | Los dos documentos pasan a `validado` | Aprobación expresa del usuario («sí, aprobados»), transmitida por el Orquestador, modo actualizar |

# Plan de pruebas funcionales: Panel Raspberry Pi, reorganización y arreglos

- **Origen:** `doc/tareas/2026-11-22-panel-raspberry-arreglos.md` (aprobado 2026-11-23) · `doc/analisis/2026-11-22-panel-raspberry-arreglos.md` (RF-1 a RF-19, RN, UAT-1 a UAT-19) · `doc/arquitectura/2026-11-22-panel-raspberry-arreglos.md` · `doc/decisiones-arquitectura.md` (nota F0-bis, recuentos sobre `f25ee46`)
- **Alcance:** todo el documento de tareas, F1 a F6 (F0 es solo lectura y no tiene casos). Los casos de F1 (PF-01 a PF-10 y PF-37) están escritos **y programados** en el script; los de F2 a F6 están en el plan y se programan al abrir su fase (dependen del código y de las pruebas que esa fase crea). Hasta entonces el arnés los da por «fuera de ámbito» con `--hasta-fase`.
- **Estado:** aprobado (2026-11-23)
- **Script:** `py -3 pruebas/funcionales/panel-raspberry-arreglos/run.py --hasta-fase F1 --nivel fase --no-interactivo` (cierre de F1; en cada fase siguiente, `--hasta-fase F<n>`; en la entrega de F6, `--hasta-fase F6 --nivel entrega`)

## Entorno y precondiciones

- Windows con Python 3.11 o superior (`py -3`), `git` y el repositorio con la línea base `f25ee46` en su historial. Sin hardware ni librerías de la Pi: la tira de LEDs se simula (F2 en adelante).
- Los casos de F1 son de **solo lectura** sobre el repositorio (índice de git y archivos). El único que escribe es PF-08, que compila con PlatformIO en `esp32/.pio` (ignorado). PF-07 trabaja sobre una copia temporal, no deja `__pycache__` ni `animation_panel.log` en el repositorio.
- PF-08 necesita `pio` instalado y las librerías ya descargadas; si hiciera falta red, el caso queda `bloqueado` y se pregunta al usuario (no se descarga nada por cuenta del script).
- Valores de la línea base en `config.ejemplo.json` (`base`, `esp32_ram`, `esp32_flash`): RAM 48 728 B y flash 890 553 B (RNF-4).
- Aplicación de hogar en una Raspberry Pi: sin usuarios, sin datos personales y sin servicio de red. La seguridad empresarial y la prueba de humo web **no aplican** (confirmado por el usuario). El «humo» de este producto es PF-07 (compila e importa) y, desde F2, PF-11.
- Lo que se ve en la Pi (UAT-17) y en el PC con ventana (UAT-18 con `DEBUG` = 1) lo hace el usuario: casos manuales marcados «en entrega».

## Inventario de entradas

| ID | Entrada | Tipo | Válido según especificación | Límites | Origen |
|---|---|---|---|---|---|
| E-1 | Árbol rastreado por git: rutas y contenido de cada archivo (incluye nombres con espacios y acentos, y el firmware) | ruta | Lo que dicen RF-1 a RF-4, RN-11, RN-13 y la nota F0-bis: 301 rastreados en `ficheros/`, `navidad/` y `panel/` en `f25ee46` = 133 eliminados + 104 archivados + 52 conservados + 12 `.pyc` | sí | análisis DE-7, RF-1 a RF-4, RNF-3; F0-bis |
| E-2 | `configuracion.json` (`directorio`, `repeticiones`, `ancho`, `alto`, `panel_hor`, `panel_ver`, `primer_led`, `velocidad`, `repeticiones_gif`, `DEBUG`) | config | Claves obligatorias y opcionales de DE-1; `panel_hor` y `panel_ver` enteros ≥ 1; `DEBUG` 0 o 1; `primer_led` `LEFT` | sí | análisis DE-1, DE-2, DE-3, DE-8 |
| E-3 | Imagen PNG en `directorio` | archivo | Modos `1`, `L`, `LA`, `P`, `RGB`, `RGBA`; de 1 px al ancho que sea; 18 px de alto en uso real; ancho ≤ panel = un frame (RN-1) | sí | análisis DE-4 |
| E-4 | Imagen GIF en `directorio` | archivo | Animada (≥ 2 frames) o de 1 frame; menor, igual o mayor que 48×18 (RN-3) | sí | análisis DE-5 |
| E-5 | Archivo ilegible o carpeta sin archivos reproducibles | archivo | `.png` o `.gif` corrupto, truncado o de 0 bytes; directorio vacío, inexistente o todo roto (RN-5) | sí | análisis DE-6, RN-5 |
| E-6 | Fallo no previsto del proceso (falta `configuracion.json` o una clave, o la tira lanza al pintar) | evento | Se registra con traza (ERROR o superior), código de salida 1, stderr conserva el error; `SystemExit` y `KeyboardInterrupt` no (RN-14) | no | análisis RF-19, RN-14 |
| E-7 | Carpeta desde la que se ejecuta el código (ruta de copia, directorio de trabajo) | ruta | Cualquier carpeta que contenga `configuracion.json`; el código lee el de su propia carpeta (RF-12) | no | análisis RF-12, CU-4 |
| E-8 | Estado del disco: copia de trabajo, archivos sin rastrear o ignorados (`__pycache__`, `*.log`, restos de OneDrive) | evento | Los 12 `.pyc` siguen en disco en su destino (se mueven, no se borran: RF-1, RN-13); sin archivos modificados ni sin rastrear en las rutas del producto | no | análisis RF-1, RN-13; tareas T-03 y T-06 |

## Casos

| ID | Fase | Clase | Caso | Entradas | Requisitos | Tipo | Cuándo | Prioridad | Origen del esperado |
|---|---|---|---|---|---|---|---|---|---|
| PF-01 | F1 | positiva | Existen `raspberry-panel/panel/` y `raspberry-panel/ficheros/` con lo que dice RF-1; no `panel/` ni `ficheros/` en la raíz; ningún `.pyc` rastreado | E-1 | RF-1 | automática | siempre | alta | análisis UAT-1 · RF-1 |
| PF-02 | F1 | hostil | `.gitignore` ignora `__pycache__/` y los `.py[cod]` también en rutas con espacios y acentos, ignora log, `.idea/`, `desktop.ini`, `Thumbs.db`, y no ignora `*.pdn` ni el código | E-1 | RF-1 | automática | siempre | media | tarea T-03 «Hecho cuando» · RN-13 |
| PF-03 | F1 | positiva | Cada archivo eliminado (133) tiene un par con sha256 idéntico en `raspberry-panel/` o `archivo/` | E-1 | RF-2 | automática | siempre | alta | análisis UAT-2 · RF-2 · RN-11 · F0-bis §1 |
| PF-04 | F1 | positiva | Cada archivo único (104) está en `archivo/` con el mismo sha256 que en la línea base | E-1 | RF-3 | automática | siempre | alta | análisis UAT-3 · RF-3 · F0-bis §1 |
| PF-05 | F1 | límite | Todo archivo de la línea base cae en un solo grupo (133 + 104 + 52 + 12 = 301), también los de nombre con espacios y acentos; no hay dos que vayan al mismo destino | E-1 | RF-2, RF-3 | automática | siempre | alta | F0-bis §1 (cuadre) · RNF-3 |
| PF-06 | F1 | inválida | La comprobación no es vacía (mutación del propio oráculo): un archivado con otro contenido, un destino quitado y un eliminado sin su par se detectan | E-1 | RF-2, RF-3 | automática | siempre | media | RN-11 (solo se elimina con par idéntico) · invariante R3 |
| PF-07 | F1 | positiva | Los 5 `.py` de `raspberry-panel/panel/` compilan y `import Config, Panel` funciona desde su carpeta | E-1 | RF-4 | automática | siempre | alta | análisis UAT-4 · RF-4 |
| PF-08 | F1 | positiva | `pio run -d esp32 -e esp32dev` da SUCCESS con RAM 48 728 B y flash 890 553 B, sin usar la red | E-1 | RF-4 | automática | en entrega | alta | análisis UAT-4 · RNF-4 |
| PF-09 | F1 | robustez | El firmware (`platformio.ini`, `src/`, `data/`) y `banner1..12.png` tienen en su sitio nuevo el mismo contenido que en la línea base | E-1 | RF-4 | automática | siempre | alta | análisis RF-4 («se demuestra que no cambiaron», RS-7) · invariante R2 |
| PF-10 | F1 | inválida | El disco no tiene estados prohibidos: `git status` de las rutas del producto vacío (ni modificados ni sin rastrear), los 12 `.pyc` siguen en disco en su destino y compilar e importar no deja archivos nuevos (ni ignorados) | E-8 | RF-1, RF-4 | automática | siempre | media | análisis RF-1 y RN-13 («se mueve, no se borra») · invariante R2 |
| PF-37 | F1 | positiva | Cada commit de movimiento solo hace lo autorizado: T-03 solo `.gitignore` y la baja de los 12 `.pyc`; T-04 solo elimina los 133 de la lista; T-05 a T-07 solo renombrados al 100 % | E-1 | RF-4, RF-2 | automática | siempre | alta | análisis RF-4 y RS-4 · F0-bis §2 y §3 · tareas T-03 a T-07 |
| PF-11 | F2 | positiva | `pytest raspberry-panel/tests` pasa entero sin librerías de hardware (C-1 a C-4, huellas de las 12 pancartas, modo DEBUG) | E-2, E-3 | RF-5, RF-17 | automática | siempre | alta | análisis UAT-5 · RF-5 · RF-17 |
| PF-12 | F3 | robustez | Las pruebas de caracterización siguen congeladas: `git log` de `test_caracterizacion_*.py` y `conftest.py` solo muestra el commit de F2 y `git status` sobre ellas sale vacío | E-3 | RF-5, RF-17 | automática | siempre | alta | tarea DT-10 · invariante R2 |
| PF-13 | F3 | positiva | Crear un `Panel` con `LOGGING_CONFIG` deja la línea INFO «Total LEDs in panel: 864» del logger `Panel` en el log | E-2 | RF-6 | automática | siempre | alta | análisis UAT-6 · RF-6 |
| PF-14 | F3 | positiva | Un único gestor de archivo sobre `animation_panel.log`, 26 214 400 B y 5 copias; la excepción de rotación figura con fecha en el análisis (RN-7) y en la memoria de decisiones | E-1 | RF-13 | automática | siempre | media | análisis UAT-13 · RF-13 · RN-7 |
| PF-15 | F3 | positiva | Sin `configuracion.json`, y con una tira simulada que lanza al pintar: ERROR con traza en el log, código de salida 1 y error por stderr; `KeyboardInterrupt` y `SystemExit` no dejan esa línea | E-2, E-6 | RF-19 | automática | siempre | alta | análisis UAT-19 · RF-19 · RN-14 |
| PF-16 | F3 | inválida | `configuracion.json` mal formado, vacío, con una clave obligatoria ausente o con `panel_hor` o `panel_ver` = 0: ERROR con la traza de la excepción en el log, código 1, error por stderr y sin colgarse (30 s) | E-2, E-6 | RF-19 | automática | siempre | media | análisis RF-19 y RN-14 · decisión del usuario 2026-11-23 («basta la traza») · invariante R4 |
| PF-17 | F3 | hostil | Valores del catálogo en `velocidad`, `ancho`, `directorio` y `repeticiones` (NaN, negativos, `1,5`, enormes, `../`, 100 000 caracteres, NUL): valor absurdo: si el proceso cae, ERROR con la traza en el log y código 1 (RF-19); en todo caso, sin colgarse (30 s). No se exige nombrar la clave | E-2 | RF-19 | automática | siempre | media | análisis RF-19 y RN-14 · decisión del usuario 2026-11-23 («basta la traza») · invariante R4 |
| PF-18 | F4 | límite | GIF de 1 frame de 48×18, 30×10, 1×1 y 48×17: 1 frame arriba a la izquierda, `repeticiones` veces, 250 ms; el animado sigue con `repeticiones_gif` | E-4 | RF-7 | automática | siempre | alta | análisis UAT-7 · RF-7 · RN-9 |
| PF-19 | F4 | límite | GIF de 100×100, 100×40, 100×37, 49×18, 48×19, 48×18, 100×1, animados y no animados: 18×18, 45×18, 48×18, mínimo 1 px; ningún píxel fuera del panel | E-4 | RF-8 | automática | siempre | alta | análisis UAT-8 · RF-8 · RN-3 · RN-8 |
| PF-20 | F4 | positiva | Un `.png` corrupto y un `.gif` truncado entre dos válidos: ERROR con ruta y causa, los válidos se reproducen y el bucle sigue | E-3, E-4, E-5 | RF-9 | automática | siempre | alta | análisis UAT-9 · RF-9 · RN-5 |
| PF-21 | F4 | inválida | PNG y GIF de 0 bytes, con cabecera válida y cuerpo cortado, y GIF que falla a mitad: se omiten enteros (sin frames parciales) con su causa en el log | E-3, E-4, E-5 | RF-9 | automática | siempre | alta | análisis RF-9 · RN-5 |
| PF-22 | F4 | límite | Directorio vacío, con un solo archivo roto y con todos rotos: 1 ERROR por vuelta que nombra el directorio y espera de 10 s simulada | E-5 | RF-9 | automática | siempre | alta | análisis UAT-9 · RN-5 |
| PF-23 | F4 | positiva | PNG de paleta 408×18 da 73 frames RGB sin excepción; PNG RGBA con píxel rojo transparente deja ese LED apagado; GIF de 1 frame de paleta y GIF animado con transparencia compuestos sobre negro; PF-11 sigue en verde | E-3, E-4 | RF-10, RF-17 | automática | siempre | alta | análisis UAT-10 · RF-10 · RN-4 |
| PF-24 | F4 | límite | PNG de 1 px, 48, 49 y 408 px de ancho y de modos `1`, `L`, `LA`, `P`, `RGB`, `RGBA`: frames según RN-1 y duración 250 ms | E-3 | RF-10, RF-17 | automática | siempre | media | análisis RN-1 · DE-4 |
| PF-25 | F4 | hostil | Archivos del catálogo (BOM, Latin-1, UTF-16, binario, NUL, línea de 1 MB) con extensión `.png` o `.gif`, PNG de 1×1 y de miles de píxeles, nombres con espacios, acentos y mayúsculas: se omiten o se reproducen sin traza ni cuelgue | E-3, E-4, E-5 | RF-9, RF-10 | automática | siempre | media | análisis RF-9 y RN-5 (se omite con su causa) · invariantes R1, R4, R5 |
| PF-26 | F4 | límite | Paneles 1×1, 2×1 y 3×2 (6 paneles): sin `IndexError`, cada panel 2 s con el color de RN-6 (el 4 repite rojo, el 5 verde) y el log da los LED de los 6 (el 0 va en PF-16) | E-2 | RF-11 | automática | siempre | media | análisis UAT-11 · RF-11 · RN-6 · DE-3 |
| PF-27 | F4 | robustez | Tres vueltas con un archivo roto: misma causa cada vuelta, el resto se reproduce igual cada vez, sin crecer ni caer; `KeyboardInterrupt` a mitad y nueva ejecución correcta | E-5 | RF-9, RF-17 | automática | siempre | media | invariantes R1, R2, R6 · RN-5 |
| PF-28 | F5 | positiva | El código copiado a una carpeta que no es `/home/pi/panel` lee su propio `configuracion.json`; `panel.service` dice `User=pi`; `directorio` sigue siendo `/home/pi/ficheros` | E-2, E-7 | RF-12 | automática | siempre | alta | análisis UAT-12 · RF-12 |
| PF-29 | F5 | hostil | Carpeta de copia con espacios y acentos, y ejecución lanzada desde otro directorio de trabajo: lee la `configuracion.json` de la carpeta del código, no la del directorio actual | E-7 | RF-12 | automática | siempre | media | análisis RF-12 · RS-9 |
| PF-30 | F5 | inválida | Carpeta del código sin `configuracion.json`: error que nombra la ruta buscada, registrado en el log, código 1 | E-7 | RF-12, RF-19 | automática | siempre | media | análisis CU-4 · RF-19 |
| PF-31 | F5 | positiva | `requirements.txt` (con hardware) y `requirements-dev.txt` (con `Pillow>=9.1` y `pytest`, sin `rpi_ws281x` ni `adafruit-*`) existen por separado; el servicio de apagado lanza `apagado.sh` y el README documenta su permiso y que está reconstruido; los servicios con finales LF | E-1 | RF-14, RF-15 | automática | siempre | media | análisis UAT-14, UAT-15 · RF-14 · RF-15 · tarea T-29 |
| PF-32 | F5 | robustez | `DEBUG` = 0 con tira simulada: lee el `configuracion.json` de la carpeta del código, no escribe LEDs, 2 vueltas (cada archivo con «preparamos imagen» dos veces) sin excepción; Windows sin librerías de hardware | E-2 | RF-18 | automática | siempre | alta | análisis UAT-18 · RF-18 · RS-9 |
| PF-33 | F6 | positiva | Los enlaces relativos y las rutas de `README.md`, `raspberry-panel/README.md`, `archivo/README.md` y `doc/diseno/panel-raspberry.md` existen los defectos arreglados figuran como resueltos y `archivo/README.md` explica cómo recuperar (`git show f25ee46:<ruta>` o lo que fije T-32) y nombra cada carpeta de `archivo/` | E-1 | RF-16 | automática | siempre | media | análisis UAT-16 · RF-16 |
| PF-34 | F5 | positiva | En un venv nuevo de Windows con Python 3.11 o superior, `pip install -r requirements-dev.txt` y `pytest` arrancan; en la Pi, el panel arranca con `requirements.txt` | E-1 | RF-14 | mixta | en entrega | media | análisis UAT-14 · RF-14 · RNF-6, RNF-8 |
| PF-35 | F5 | positiva | `DEBUG` = 1 en el PC del usuario: se abre una ventana por frame escalado ×10, como hoy | E-2 | RF-18 | manual | en entrega | media | análisis UAT-18 · RF-18 |
| PF-36 | F6 | positiva | En la Pi, con el `panel.service` del repositorio (`User=pi`): panel 0 rojo y 1 verde, las 12 pancartas igual y con los mismos tiempos, un GIF animado mayor que el panel y un GIF de 1 frame; instalados los dos servicios con el README, tras reiniciar el de apagado está `enabled` y activo y el panel lee el `configuracion.json` de su carpeta (UAT-12 y UAT-15) | E-2, E-3, E-4 | RF-17, RF-7, RF-8 | aceptación | en entrega | alta | análisis UAT-17 · RF-17 · RF-7 · RF-8 |

### PF-01 · Estructura nueva sin restos

- **Requisitos:** RF-1
- **Precondiciones:** T-03 y T-06 hechas y confirmadas. Se lee el índice de git (`git ls-files`).
- **Pasos:** el script lista el índice y comprueba: `raspberry-panel/panel/` con los 5 `.py` (`Animation`, `AnimationServer`, `Config`, `LedMatrixAnimation`, `Panel`), `configuracion.json`, `panel.service` y `apagado.sh`; `raspberry-panel/ficheros/banner1.png` a `banner12.png`; ningún rastreado bajo `panel/` ni `ficheros/` de la raíz y ninguna de esas carpetas en el disco; `animation_panel.log` no rastreado en `raspberry-panel/panel/` y sí en `archivo/raspberry-panel/`; `git ls-files "*.pyc"` vacío.
- **Resultado esperado:** todo lo anterior se cumple.

### PF-02 · `.gitignore` con rutas difíciles

- **Requisitos:** RF-1
- **Precondiciones:** T-03 hecha.
- **Pasos:** `git check-ignore -q` sobre rutas inventadas: `raspberry-panel/panel/__pycache__/Panel.cpython-313.pyc`, `archivo/navidad/ficheros navidad/panel/__pycache__/Config.cpython-37.pyc` (espacios), una ruta con acento, `x.pyo`, `x.pyd`, `animation_panel.log`, `animation_panel.log.1`, `.idea/a`, `desktop.ini`, `Thumbs.db`. Sobre `…/imagen.pdn`, `raspberry-panel/ficheros/banner1.png` y `raspberry-panel/panel/Panel.py`. Además, cada línea del `.gitignore` de `f25ee46` sigue en el actual.
- **Resultado esperado:** las primeras se ignoran, las tres últimas no, y no se perdió ninguna línea antigua.

### PF-03 · Cada eliminado tiene un par idéntico

- **Requisitos:** RF-2
- **Precondiciones:** T-04 hecha. La línea base `f25ee46` existe.
- **Pasos:** se clasifica cada archivo de `ficheros/`, `navidad/` y `panel/` de la línea base (sin `.pyc`, que cubre PF-01) según el destino previsto (`panel/` y `ficheros/` a `raspberry-panel/`, `navidad/` a `archivo/`, el log y los 4 banners antiguos a `archivo/`); los que no llegan a su destino son los eliminados. Se calcula el sha256 de cada uno y se busca entre los de `raspberry-panel/` y `archivo/`.
- **Resultado esperado:** hay 133 eliminados y todos tienen par; si el recuento difiere, falla (F0-bis explica 141 = 137 + 4 `.pyc`; aquí, sin `.pyc`).

### PF-04 · Cada único está archivado

- **Requisitos:** RF-3
- **Precondiciones:** T-07 hecha.
- **Pasos:** de la misma clasificación, los que llegan a `archivo/` (104: 99 de `navidad/`, 4 banners antiguos y el log) se comparan por sha256 con su original en la línea base.
- **Resultado esperado:** 104 y 0 diferencias. (Que exista `archivo/README.md` lo comprueba PF-33 en F6.)

### PF-05 · Partición exacta, con nombres difíciles

- **Requisitos:** RF-2, RF-3
- **Precondiciones:** T-04 a T-07 hechas.
- **Pasos:** se cuentan los 301 rastreados de la línea base en las tres carpetas y los 12 `.pyc`; se comprueba que 133 + 104 + 52 + 12 = 301, que hay al menos un nombre con espacio y uno con carácter no ASCII en el conjunto (si no, el caso no ataca lo que dice).
- **Resultado esperado:** el cuadre es exacto y los nombres difíciles están en un grupo.

### PF-06 · La comprobación no es vacía

- **Requisitos:** RF-2, RF-3
- **Precondiciones:** ninguna (solo el script).
- **Pasos:** sobre el índice actual: (a) se compara un archivado con el contenido de otro archivo de `archivo/`; (b) se quita del índice el destino de un archivado y se reclasifica; (c) se quita el único par de un eliminado y se busca su sha256.
- **Resultado esperado:** (a) el contenido difiere; (b) pasa a «eliminado» y el recuento de archivados baja en uno; (c) queda sin par. Sin ello, PF-03 y PF-04 no demostrarían nada. Solo usa archivos de la línea base que no cambian después.

### PF-07 · Compila e importa

- **Requisitos:** RF-4
- **Precondiciones:** T-06 hecha; Python 3.11 o superior.
- **Pasos:** compilar en memoria los 5 `.py` sin escribir `.pyc`; copiar `raspberry-panel/panel/` a una carpeta temporal con espacio y acento y ejecutar allí `import Config, Panel`.
- **Resultado esperado:** código de salida 0 en ambos. Cualquier error de importación es `falla` (`Config` y `Panel` solo usan la biblioteca estándar). Desde F2, PF-11 importa los 5 módulos con el intérprete del venv de pruebas (clave `python` de la configuración).

### PF-08 · El firmware compila igual

- **Requisitos:** RF-4
- **Precondiciones:** T-05 hecha; `pio` instalado, plataforma `espressif32` y librerías ya en caché; la orden autorizada por el usuario.
- **Pasos:** se comprueba que plataforma y `esp32/.pio/libdeps` existen (si no, `bloqueado` sin ejecutar); `pio run -d esp32 -e esp32dev`; lectura de RAM y Flash; cualquier «Downloading» o «Installing» en la salida da `bloqueado`.
- **Resultado esperado:** SUCCESS, RAM 48 728 B y flash 890 553 B, sin red. Es «en entrega» porque T-05 ya compila con autorización en F1 y PF-09 demuestra en cada cierre, por contenido, que el firmware no cambió (alternativa que admite RF-4).

### PF-09 · Contenido intacto de firmware y banners

- **Requisitos:** RF-4
- **Precondiciones:** T-05 y T-06 hechas.
- **Pasos:** cada archivo de la línea base `platformio.ini`, `src/**` y `data/**` se compara por sha256 con `esp32/<ruta>`, y `ficheros/banner{1..12}.png` con `raspberry-panel/ficheros/banner{n}.png`. No se compara `README.md` del ESP32 (T-34 lo cambia) ni el código del panel (cambia legítimamente desde F3; lo guardan PF-07 y PF-11).
- **Resultado esperado:** 0 diferencias y 0 ausentes.

### PF-10 · Disco intacto y sin efectos

- **Requisitos:** RF-1, RF-4
- **Precondiciones:** T-03 a T-07 hechas y confirmadas.
- **Pasos:** `git status --porcelain -- raspberry-panel esp32 archivo .gitignore`; comprobar que los 12 `.pyc` existen en su destino del disco; guardar `git status --ignored=matching` de esas rutas, ejecutar la compilación e importación de PF-07 y guardarlo de nuevo.
- **Resultado esperado:** estado vacío (ni modificados ni sin rastrear, p. ej. restos de OneDrive), los 12 `.pyc` presentes y estado de ignorados idéntico antes y después.

### PF-37 · Los commits de movimiento solo hacen lo autorizado

- **Requisitos:** RF-4, RF-2
- **Precondiciones:** T-03 a T-07 confirmadas, con mensaje que empieza por `T-0n:` (convención de `0059118`); si falta alguno, `bloqueado`.
- **Pasos:** `git diff --name-status -M100% -z <c>^ <c>` de cada commit. T-03: solo `M .gitignore` y `D` de los 12 `.pyc`. T-04: solo `D`, igual al conjunto de 133 eliminados. T-05 a T-07: solo `R100` (y `A esp32/.gitignore` en T-05).
- **Resultado esperado:** nada fuera de eso; un byte cambiado dentro de un `git mv` lo rompe, porque el renombrado deja de ser 100 %.

### PF-11 · Las pruebas del panel pasan sin hardware

- **Requisitos:** RF-5, RF-17
- **Precondiciones:** T-08 a T-13 hechas; venv con `requirements-dev.txt`.
- **Pasos:** `py -3 -m pytest raspberry-panel/tests` sobre el código sin corregir (F2) y, como regresión, tras cada fase.
- **Resultado esperado:** todo pasa, incluidas las huellas de `banner1..12.png`. Se programa al abrir F2.

### PF-12 · Caracterización congelada

- **Requisitos:** RF-5, RF-17
- **Precondiciones:** F2 cerrada.
- **Pasos:** `git log --oneline -- raspberry-panel/tests/test_caracterizacion_*.py raspberry-panel/tests/conftest.py` y `git status --porcelain` de esas rutas.
- **Resultado esperado:** solo el commit de F2 (o el de T-14 si PA-1 amplía C2) y estado vacío.

### PF-13 a PF-36

Se detallan paso a paso al abrir su fase, a partir del código y las pruebas que esa fase deja (la tabla ya fija qué se ataca y de dónde sale el esperado). Todas se comprueban con la tira simulada y `time.sleep` simulado, salvo las marcadas manual, mixta o aceptación (PF-34, PF-35, PF-36), que hace el usuario con el script guiándole o con `--respuestas`. En PF-36, UAT-17, el usuario antes ejecuta `systemctl show panel -p User` y debe dar `pi`; si no, se para y se pregunta (análisis UAT-17).

## Requisitos

| ID | Requisito |
|---|---|
| RF-1 | Código vigente en `raspberry-panel/panel/`, imágenes en `raspberry-panel/ficheros/`, `.pyc` sin rastrear |
| RF-2 | Una sola carpeta de imágenes: se eliminan los duplicados por sha256 |
| RF-3 | Lo único se archiva en `archivo/` sin borrarse |
| RF-4 | La reorganización no cambia comportamiento; el firmware pasa a `esp32/` |
| RF-5 | Pruebas sin hardware que fijan el comportamiento actual (C-1 a C-4) |
| RF-6 | Las trazas de `Panel` llegan al log (Z-1) |
| RF-7 | Un `.gif` no animado que cabe se muestra como estático (Z-3) |
| RF-8 | Ningún píxel fuera de su sitio; GIF mayor se reduce hasta caber (Z-4) |
| RF-9 | Un archivo que no carga deja su causa en el log y se omite (Z-9) |
| RF-10 | Toda imagen en RGB con la transparencia sobre negro (Z-2) |
| RF-11 | Prueba de paneles y contador de LED con cualquier número de paneles (Z-5) |
| RF-12 | Despliegue reproducible: carpeta del código, `User=pi` (Z-8) |
| RF-13 | Un único log con rotación (Z-7) y la excepción escrita |
| RF-14 | Dependencias de ejecución y de prueba por separado (Z-11) |
| RF-15 | El servicio de apagado figura en el repositorio (Z-12) |
| RF-16 | La documentación vigente refleja el nuevo estado |
| RF-17 | Sin regresión: colores, tiempos, mapeo y orden |
| RF-18 | Modo simulación y `DEBUG` = 1 siguen funcionando en PC |
| RF-19 | Toda excepción no capturada se registra con su traza |

## Fuera de alcance

- Seguridad empresarial, acceso de empresa y prueba de humo web: no aplican (aplicación de hogar embebida; confirmado por el usuario).
- Instalar o probar nada en la Pi desde el repositorio (RS-5): lo hace el usuario en PF-36. La prueba de paneles C-5 en la Pi forma parte de PF-36.
- Z-6, Z-10, Z-13, RU-3 y el firmware ESP32 (solo se mueve): no se prueba comportamiento nuevo de ellos.
- El código del panel entre F1 y F3 no se compara byte a byte con la línea base: cambia legítimamente desde T-14; lo cubren PF-07 y las pruebas de caracterización (PF-11).
- Recuperar lo que solo existía en `e23949d` (RS-6).

## Preguntas abiertas

| ID | Pregunta | Quién | Mientras tanto |
|---|---|---|---|
| P-1 | Resuelta 2026-11-23 (usuario, «basta la traza»): ante un valor absurdo en `configuracion.json` basta la traza de la excepción en el log (RF-19, T-16), código 1 y sin colgarse; no se exige validar ni nombrar la clave. Sin RF nuevo | Usuario | Aplicado en PF-16 y PF-17 |
| P-2 | Resuelta 2026-11-23 (usuario): 30 s por ejecución simulada para «no se cuelga» (R4) | Usuario | Aplicado en PF-16 y PF-17 |

## Cambios

| Fecha | Cambio | Origen |
|---|---|---|
| 2026-11-23 | Creación del plan en estado borrador: 36 casos, F1 programada | Encargo del Orquestador, modo planificar |
| 2026-11-23 | Ronda 1 del Cuestionador incorporada: PF-37 nuevo; PF-06 en mutación; `--no-index` en PF-02; PF-10 rehecho (E-8); PF-08 «en entrega» y sin red; PF-07 sin bloqueo; esperados de PF-16, PF-17 y PF-26 coherentes con RF-19; PF-33 y PF-36 ampliados; comprobación vacía de PF-05 quitada. Total 37 casos | Acta del Cuestionador, ronda 1 |
| 2026-11-23 | Plan aprobado por el usuario. P-1 y P-2 resueltas; PF-25 sin referencia a P-1 | Respuesta del usuario vía Orquestador |
| 2026-11-23 | PF-16 y PF-17: el esperado pasa de «error claro que dice qué valor está mal» a «traza de la excepción en el log (RF-19, T-16), código 1 y sin colgarse en 30 s»; no se exige nombrar la clave. Sin RF nuevo ni refaseo | Decisión del usuario («basta la traza») vía Orquestador |

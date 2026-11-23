# Análisis: Panel Raspberry Pi, reorganización del repositorio y arreglos

- **Petición de origen:** el usuario, 2026-11-22: «Primero arreglamos y mejoraremos panel de raspberry». Respuestas a las preguntas cerradas: arreglar todos los grupos (imágenes Z-2, Z-3 y Z-4; registro Z-1, Z-7 y Z-9; despliegue Z-8 y Z-12; Z-5 y Z-11), «solo arreglar» sin mejoras nuevas, y reorganizar (opción A) antes de los arreglos. RU-3 (orden de color configurable) queda fuera por decisión del usuario. Respuestas a PA-1 a PA-8, SP-1 a SP-6 y seguridad: el usuario, 2026-11-22 (vía Orquestador).
- **Tamaño:** M
- **Estado:** aprobado
- **Fecha:** 2026-11-22
- **Nivel de seguridad:** no aplica (firmware)   ← motivo confirmado por el usuario (2026-11-22): sin usuarios, datos personales ni servicio de red; es Python en una Pi (ver «Seguridad»)

## Objetivo

Dejar el panel LED de Navidad de la Raspberry Pi (`panel/`, código vigente por P-2) ordenado y libre de los defectos Z-1, Z-2, Z-3, Z-4, Z-5, Z-7, Z-8, Z-9, Z-11 y Z-12 de [panel-raspberry.md](../diseno/panel-raspberry.md), sin añadir funcionalidad. Para el propietario de la Pi (AT-1): el panel muestra todas las imágenes PNG y GIF de su carpeta sin caerse ni pintar fuera de sitio, el log dice la verdad, y el repositorio contiene todo lo necesario para reinstalar el panel y su apagado. Para el mantenedor (AT-3): el modo debug y el modo simulación siguen funcionando en PC (Windows).

Se sabrá que está resuelto cuando se cumplan los RF-1 a RF-19 (sus criterios y los UAT) y la Pi muestre las mismas imágenes con los mismos colores y tiempos que antes (RF-17).

## AS-IS y TO-BE

**AS-IS** (de [panel-raspberry.md](../diseno/panel-raspberry.md), validado el 2026-11-14; lo leído hoy en `panel/` coincide):

- La raíz mezcla dos productos y tres copias de imágenes y de código antiguo (`navidad/`). La reorganización está planificada y autorizada (`doc/decisiones-arquitectura.md`, plan F0 a F7); el árbol sigue sin mover. El historial se reescribió: el commit `e23949d` del plan no existe y la línea base es el HEAD `f25ee46` (RS-6).
- `panel/Panel.py:2` usa `from venv import logger`: sus trazas no llegan al log.
- Un PNG que no está en modo RGB (paleta, escala de grises, RGBA) llega sin convertir a `getpixel`; con paleta devuelve un entero y `colourTuple` falla (`panel/Animation.py:172`, `panel/AnimationServer.py:319-324`).
- Un `.gif` no animado no genera frames y no se muestra (`panel/Animation.py:74-80`).
- Un GIF mayor que el panel no se redimensiona: `y * ancho_total + x` pasa a la fila siguiente (`panel/AnimationServer.py:311-314`).
- Con más de 4 paneles, la prueba de paneles y el contador fallan con `IndexError` (`panel/AnimationServer.py:158`, `:308`).
- Tres gestores de rotación escriben sobre el mismo `animation_panel.log` (`panel/LedMatrixAnimation.py:18-26`, `panel/Animation.py:10-18`, `panel/AnimationServer.py:10-18`).
- `panel/Config.py:33` lee `/home/pi/panel/` fijo; `panel/panel.service:14` dice `User=owner` y el servicio corre con `pi` (P-2, confirmado por el usuario el 2026-11-22).
- `panel/Animation.py:81-82` tiene un `except:` que lanza un error sin causa y sin registrar nada. Un error de carga no está capturado en el bucle principal: el proceso termina y systemd lo relanza a los 10 s (`panel/LedMatrixAnimation.py:126-141`, `panel/panel.service:9-10`).
- Modo simulación (sin librerías de hardware, `HARDWARE_AVAILABLE = False`, `panel/AnimationServer.py:21-33`) y modo `DEBUG` = 1 (una ventana por frame ×10, `panel/AnimationServer.py:343-394`): el usuario confirma que funcionaban en PC.
- 12 `.pyc` están rastreados en git: 4 de `panel/__pycache__/*.cpython-313.pyc` y 8 de Python 3.7 (`navidad/panel/__pycache__/*` y `navidad/ficheros navidad/panel/__pycache__/*`), comprobado por el Orquestador con `git ls-files "*__pycache__*"` (2026-11-22). En `tools/` no hay ninguno rastreado.
- No hay pruebas ni `requirements.txt`. El servicio que lanzaba `apagado.sh` no está en el repositorio.

**TO-BE:** el repositorio queda con la estructura del plan (RF-1 a RF-4); el panel cumple RF-6 a RF-15, RF-18 y RF-19; el despliegue queda completo y documentado (RF-12, RF-16); y hay pruebas automáticas sin hardware que fijan el comportamiento (RF-5, RF-17). Nada más cambia.

## Actores

| ID | Actor | Qué hace con el sistema |
|---|---|---|
| AT-1 | Propietario de la Pi | Copia el código y las imágenes a la Pi, instala los servicios, enciende la Pi y mira el panel y el log |
| AT-2 | systemd de la Pi | Arranca `LedMatrixAnimation.py` y el servicio de apagado, relanza el panel si cae |
| AT-3 | Mantenedor del código | Ejecuta las pruebas y el modo debug o simulación en su equipo (Windows, sin hardware) y revisa el log |

## Casos de uso

| ID | Caso de uso | Actor | Flujo principal | Flujos alternativos y errores |
|---|---|---|---|---|
| CU-1 | Reorganizar el repositorio | AT-3 | 1. Se aplica el plan F0 a F7 sobre la línea base `f25ee46`. 2. Se comprueba por hash que lo eliminado es idéntico a lo conservado. 3. Se documenta | Un hash no coincide: se aborta esa fase y no se elimina nada de ella |
| CU-2 | Reproducir una imagen PNG | AT-1 | 1. El panel carga el PNG. 2. Lo convierte a RGB. 3. Lo desplaza 5 px por frame. 4. Pinta frame a frame | PNG ilegible: RF-9 |
| CU-3 | Reproducir un GIF | AT-1 | 1. El panel carga el GIF. 2. Lo ajusta al panel. 3. Reproduce sus frames con sus duraciones | GIF no animado: RF-7. GIF mayor que el panel: RF-8. GIF que falla a mitad: RF-9 |
| CU-4 | Arrancar el panel | AT-2 | 1. Lee `configuracion.json` de su carpeta. 2. Prueba cada panel 2 s. 3. Entra en el bucle | Falta el archivo: error con la ruta buscada, registrado en el log (RF-19) |
| CU-5 | Desplegar en la Pi | AT-1 | 1. Copia `panel/` e imágenes. 2. Crea el venv con `requirements.txt`. 3. Instala los dos servicios | Sin permiso para apagar: lo dice la documentación (RF-12) |
| CU-6 | Diagnosticar con el log | AT-3 | 1. Abre `animation_panel.log`. 2. Ve trazas de todos los módulos, la causa de cada error de carga de imágenes y la traza de toda excepción no capturada (RF-9, RF-19) | Los errores también salen por stderr, es decir, al journal de systemd (`journalctl -u panel`, a documentar en RF-12) |
| CU-7 | Ejecutar las pruebas | AT-3 | 1. Lanza las pruebas en Windows. 2. Todas pasan sin librerías de hardware | Una falla: el cambio no se acepta |
| CU-8 | Desarrollar en PC con el modo simulación o debug | AT-3 | 1. Ejecuta el panel en Windows con un `configuracion.json` local. 2. Con `DEBUG` = 0 no pinta LEDs y recorre las imágenes; con `DEBUG` = 1 abre una ventana por frame | Falta la carpeta de imágenes: caso de RN-5 (1 ERROR por vuelta y espera de 10 s), no de RF-19 |

## Requisitos funcionales

| ID | Requisito | Criterio de aceptación | Prioridad | Origen |
|---|---|---|---|---|
| RF-1 | El código vigente de la Pi vive en `raspberry-panel/panel/` y sus imágenes originales en `raspberry-panel/ficheros/`; los `.pyc` de `panel/__pycache__/` dejan de rastrearse | Dado el repositorio reorganizado, cuando se lista, entonces existen `raspberry-panel/panel/` con los 5 `.py`, `configuracion.json`, `panel.service` y `apagado.sh`, y `raspberry-panel/ficheros/banner1.png` a `banner12.png`; `git ls-files panel ficheros` no devuelve nada; `animation_panel.log` no está rastreado en git en `raspberry-panel/panel/`; `git ls-files "*.pyc"` no devuelve ninguno (los 12 de RN-13 salen del índice) y `.gitignore` contiene `__pycache__/` (RN-13); si tras F4 queda `panel/__pycache__/` en disco, se mueve (no se borra) a `raspberry-panel/panel/__pycache__/` o el usuario autoriza quitarlo | imprescindible | usuario (opción A, P-5; PA-4); decisiones-arquitectura.md, plan F4 |
| RF-2 | Hay una sola carpeta de imágenes: se eliminan las copias idénticas por contenido | Dado cada archivo eliminado, cuando se compara su sha256 con el de un archivo que se conserva, entonces coincide, salvo los 4 `.pyc` del grupo C (`navidad/panel/__pycache__/`), excepción autorizada expresamente (RN-11); los recuentos del plan (141 eliminados = 137 + 4) se recalculan contra la línea base `f25ee46` (RS-6, RS-7), sin copiarlos aquí como verdad | imprescindible | usuario (P-3, P-5); decisiones-arquitectura.md, plan F2 |
| RF-3 | Lo que no tiene copia (imágenes del juego, `navidad/1/`, iconos de «ficheros navidad», `globos/`, `.pdn`, `banner7-1`, `banner8-1`, versiones antiguas de banner1/7/8/9, código antiguo de Python y el log de diciembre de 2025) se archiva en `archivo/` sin borrarse | Dado cada archivo único del inventario de P-10 que exista en la línea base, cuando se busca, entonces está en `archivo/` con su contenido idéntico (sha256) al original, y `archivo/README.md` dice cómo recuperarlo; lo que solo existía en `e23949d` (p. ej. `navidad/1.bat`) se da por perdido y no se exige | imprescindible | usuario (P-10; PA-4); decisiones-arquitectura.md, plan F5 |
| RF-4 | La reorganización no cambia ningún comportamiento: ni código ni configuración de ejecución de ningún producto, y el firmware ESP32 pasa a `esp32/` | Dado el commit de cada fase de movimiento, cuando se compara con el anterior, entonces solo hay renombrados al 100 %, archivos nuevos de documentación o `.gitignore` y la salida del índice de git de los 12 `.pyc` de RN-13; los 5 `.py` compilan y se importan desde `raspberry-panel/panel`; `pio run -d esp32 -e esp32dev` da RAM 48 728 B y flash 890 553 B (o se demuestra que `src/`, `data/` y `platformio.ini` no cambiaron, RS-7) | imprescindible | usuario (P-5); decisiones-arquitectura.md, F3 y F4; SP-1 |
| RF-5 | Antes de corregir nada, existen pruebas automáticas que fijan el comportamiento actual de `Panel.calculateMatrix`, `generateFrames`, `colourTuple` y de `startAnimation` con una tira simulada (C-1 a C-4) | Dado el código sin corregir, cuando se ejecutan las pruebas sin hardware, entonces C-1 a C-4 pasan; C-1: 24×18, 2 paneles, LEFT, BOTTOM da la misma matriz que `navidad/panel/`; C-2: 408×18 con 48 de ancho da 73 frames de 48×18; C-3: `(255, 0, 0)` da `0xFF0000`; C-4: cada píxel de un frame 48×18 llega al LED `matriz[y*48+x]` | imprescindible | Z-11; panel-raspberry.md «Cómo trabajar con este código» |
| RF-6 | Las trazas de `Panel` llegan al log de la aplicación (Z-1); se hace junto con RF-13 o después, y `Panel` no añade gestor propio | Dado un arranque con la configuración actual, cuando se crea el `Panel`, entonces `animation_panel.log` contiene la línea de nivel INFO «Total LEDs in panel: 864» con el nombre de logger `Panel` | importante | usuario (Z-1); `panel/Panel.py:2` |
| RF-7 | Un `.gif` no animado que cabe en el panel se muestra como imagen estática (Z-3) | Dado un `.gif` de un solo frame de 48×18 o menor, cuando entra en el bucle, entonces genera 1 frame, se pinta arriba a la izquierda y se repite `repeticiones` veces (no `repeticiones_gif`). Un `.gif` no animado mayor que el panel sigue RF-8 | importante | usuario (Z-3; PA-1); SP-2 |
| RF-8 | Ningún píxel se pinta fuera de su sitio y un GIF mayor que el panel, animado o no, se reduce hasta caber (Z-4) | Dado un frame mayor que 48×18, cuando se pinta, entonces ningún píxel con `x ≥ ancho_total` o `y ≥ altura_total` llega a un LED; un GIF de 100×100 sobre un panel de 48×18 se pinta de 18×18 en la esquina superior izquierda; un GIF de 100×40 se pinta de 45×18 (RN-3); un GIF de 30×10 se pinta de 30×10 arriba a la izquierda, igual que hoy | imprescindible | usuario (Z-4; PA-1, 2026-11-22) |
| RF-9 | Un archivo que no se puede cargar deja su causa en el log (Z-9) y se trata según RN-5. Incluye el GIF animado que falla a mitad (hoy `loadAnimatedGif` registra el error sin la ruta y reproduce los frames ya leídos) | Dado un `.png` con contenido corrupto, cuando se carga, entonces el log tiene una línea ERROR con la ruta, el tipo de excepción y el mensaje originales, la excepción que sube desde la carga nombra la ruta y conserva la causa, y el bucle sigue con el siguiente archivo; dado un `.gif` truncado o corrupto, entonces el ERROR lleva la ruta y la causa, el GIF se descarta entero (sus frames parciales no se reproducen: cambio aceptado por el usuario, hoy se muestran) y el bucle sigue con el siguiente; dado un directorio sin ningún archivo reproducible (vacío o todos rotos), entonces se registra 1 ERROR por vuelta y se espera 10 s antes de repetir | importante | usuario (Z-9; PA-2, 2026-11-22) |
| RF-10 | Toda imagen que pasa por `generateFrames` (PNG de cualquier modo: paleta, escala de grises, con alfa, 1 bit; y GIF de un frame, que Pillow suele abrir en modo paleta) se reproduce en RGB (Z-2), con la transparencia compuesta sobre negro (RN-4) | Dado un PNG de paleta de 408×18 o un GIF de 1 frame en modo paleta, cuando se genera su animación, entonces los frames están en modo RGB (73 en el PNG) y `startAnimation` los pinta sin excepción; dado un PNG RGBA con un píxel rojo totalmente transparente, entonces ese LED no se enciende; dado un GIF animado con transparencia, entonces sus frames se componen sobre negro (cambio aceptado, RN-4); y dado cada `banner1.png` a `banner12.png`, entonces el valor que llega a cada uno de los 864 LED de la tira simulada (`colourTuple`, o 0 si no se pinta) en cada frame es el mismo antes y después del arreglo; el modo de cada banner (`Image.open(p).mode`) se registra en F0-bis; un banner que hoy no se puede pintar (paleta) se señala y no cuenta como cambio; si otro difiere, se para y se pregunta al usuario antes de seguir | imprescindible | usuario (Z-2; PA-3, 2026-11-22) |
| RF-11 | La prueba de paneles y el contador de LEDs encendidos admiten cualquier número de paneles (Z-5) | Dado una configuración de 3 paneles horizontales × 2 verticales (6 paneles), cuando se ejecuta `testPanels` y `startAnimation`, entonces no hay `IndexError`, cada panel se enciende 2 s con el color que fija RN-6 y el log da los LEDs encendidos de los 6 paneles | deseable | usuario (Z-5); SP-3 |
| RF-12 | El despliegue de la Pi es reproducible desde el repositorio: configuración y usuario correctos (Z-8) y documentación de instalación | Dado el código copiado a una carpeta cualquiera, cuando arranca, entonces lee `configuracion.json` de su propia carpeta (en `/home/pi/panel` es el mismo archivo que hoy); `panel.service` dice `User=pi`; el README de `raspberry-panel/` describe copiar `panel/` e imágenes, crear el venv con `requirements.txt`, instalar ambos servicios, consultar `journalctl -u panel`, comprobar antes con `/home/pi/venv/bin/python3 --version` que Python es 3.11 o superior (si no, se para y se pregunta) y trabajar en PC sobre una copia de `raspberry-panel/panel/` fuera del repositorio con su propio `configuracion.json`; al cerrar, `raspberry-panel/panel/configuracion.json` conserva `directorio` = `/home/pi/ficheros` | importante | usuario (Z-8, Z-12; PA-7, 2026-11-22); P-2 |
| RF-13 | Hay un único registro de log con rotación (Z-7), y la excepción a la práctica de logging queda escrita | Dado el proceso en marcha, cuando se listan los gestores de archivo de los loggers del panel, entonces solo hay uno sobre `animation_panel.log`, con 25 MB por archivo y 5 copias (RN-7); y la excepción «rotación solo por tamaño» figura con fecha en RN-7 y en la entrada de cierre de `doc/decisiones-arquitectura.md` (versionada). Si el usuario quiere además la línea en «Prácticas declaradas» de `python.instructions.md` (zona protegida: no la escribe ningún agente), la escribe él | importante | usuario (Z-7; PA-6, 2026-11-22) |
| RF-14 | Las dependencias de ejecución de la Pi y las de prueba (aparte, instalables en Windows, incluida la herramienta de pruebas) están declaradas por separado (Z-11); el formato lo decide el Ingeniero de diseño | Dado un venv nuevo con Python 3.11 o superior en la Pi, cuando se instalan las de ejecución, entonces el panel arranca; dado un venv en Windows con Python 3.11 o superior, cuando se instalan las de prueba, entonces las pruebas (RF-5) arrancan sin librerías de hardware; las versiones de cada librería en la Pi se comprueban al desplegar (SP-4) | importante | usuario (Z-11; PA-5, 2026-11-22); SP-4 |
| RF-15 | El servicio que ejecuta `apagado.sh` figura en el repositorio (Z-12) | Dado `raspberry-panel/`, cuando se mira, entonces hay un archivo de servicio que lanza `apagado.sh` al encender la Pi, y el README dice qué permiso necesita `shutdown` y que el archivo está reconstruido, no copiado de la Pi | importante | usuario (Z-12); P-9; SP-5 |
| RF-16 | La documentación vigente refleja el nuevo estado | Dado el repositorio al cerrar, cuando se abren `README.md` raíz, `raspberry-panel/README.md`, `archivo/README.md` y `doc/diseno/panel-raspberry.md`, entonces sus rutas existen y los defectos arreglados figuran como resueltos | importante | decisiones-arquitectura.md F6 y F7; regla «Todo queda escrito» |
| RF-17 | Sin regresión: colores, tiempos, mapeo de LEDs y orden de reproducción no cambian | Dado el mismo `configuracion.json` y las mismas imágenes de `ficheros/banner1..12.png`, cuando se comparan las pruebas C-1 a C-4 antes y después de los arreglos, entonces pasan sin tocarlas; y, para cada una de las 12 pancartas, el número de frames («Generados N frames», p. ej. 73 en `banner1`) y las duraciones del log nuevo son iguales a los del log de diciembre de 2025 archivado; en la Pi la prueba de paneles (C-5) enciende el panel 0 en rojo y el 1 en verde, igual que antes. C-1 guarda su matriz esperada como dato, sin importar el código antiguo | imprescindible | usuario («solo arreglar»); Z-6, C-5 |
| RF-18 | El modo simulación (sin librerías de hardware) y el modo `DEBUG` = 1 siguen funcionando en PC (Windows) tras los arreglos, incluidas las rutas de RF-12 | Dado Windows sin librerías de hardware y un `configuracion.json` local con `directorio` existente, cuando arranca con `DEBUG` = 0, entonces lee el `configuracion.json` de la carpeta del código (en PC, el de una copia fuera del repositorio, RF-12), no escribe en ningún LED, completa 2 vueltas (cada archivo aparece 2 veces con «preparamos imagen» en el log) y no lanza excepción; dado `DEBUG` = 1, entonces abre una ventana por cada frame escalado ×10, como hoy | imprescindible | usuario (2026-11-22: «hay un modo debug que funcionaba en PC»); D-2, F-7, F-8 |
| RF-19 | Toda excepción no capturada se registra con su traza en `animation_panel.log` antes de terminar el proceso | Dado un fallo no previsto (p. ej. falta `configuracion.json`, falta una clave obligatoria o falla la tira NeoPixel), cuando el proceso termina por esa excepción, entonces el log tiene una línea de nivel ERROR o superior con la traza completa, el proceso termina igual que hoy, con código de salida 1 (con `Restart=always` systemd lo relanza a los 10 s con cualquier código), y el error sigue saliendo por stderr; una parada normal (`SystemExit`, `KeyboardInterrupt`) no genera esa línea | importante | usuario (PA-8, 2026-11-22); CU-6 |

## Reglas de negocio

| ID | Regla | Valor exacto y límite | Origen | RF asociados |
|---|---|---|---|---|
| RN-1 | Tiempo y desplazamiento de las pancartas | 5 px por frame; duración del frame = `velocidad` × 1000 ms (250 ms con 0,25); los frames se generan mientras `x + ancho_recorte ≤ ancho_imagen` (con 408 de ancho y 48 de panel, 73 frames) | panel-raspberry.md R-1, R-2, F-3; `panel/Animation.py:51`, `:64` | RF-5, RF-10, RF-17 |
| RN-2 | Duración de un frame de GIF sin dato | 100 ms | `panel/Animation.py:118` | RF-17 |
| RN-3 | Un GIF (animado o no) mayor que el panel se reduce | Es mayor si ancho > `ancho_total` o alto > `altura_total` (estrictamente). Se reduce proporcionalmente, todos sus frames al mismo tamaño: el resultado cabe (ancho ≤ `ancho_total`, alto ≤ `altura_total`), uno de los dos lados iguala el del panel, la proporción se conserva con error de hasta 1 px, cada lado se redondea al entero más cercano (100×37 da 48×18) sin superar el panel, y el mínimo es 1 px por lado; el filtro de reducción lo decide el Ingeniero de diseño con el criterio de no crear colores que no estén en el GIF; queda en la esquina superior izquierda. Un GIF que ya cabe no se toca. No se desplaza como pancarta. No aplica a los PNG, que siguen RN-1 | usuario (PA-1) | RF-8 |
| RN-4 | Transparencia | Un píxel con alfa o transparencia (modos `LA`, `RGBA`, `P` con transparencia) se compone sobre negro: el transparente queda apagado (el negro puro `(0,0,0)` no se pinta: `panel/AnimationServer.py:322`). Alcance: todo PNG y todo GIF, también los frames de un GIF animado (hoy `convert('RGB')` en `panel/Animation.py:114` pinta el color de la entrada transparente); es un cambio de lo que se ve aceptado por el usuario en PA-3 («los PNG o GIF con transparencia»). Condición previa: se comprueba que `banner1..12` se ven igual con esta regla (RF-10); si alguno cambia, se para y se pregunta | usuario (PA-3); panel-raspberry.md R-4 | RF-10 |
| RN-5 | Un archivo que falla al abrir, decodificar o convertir | Se registra el error, se omite ese archivo y el bucle sigue con el siguiente. Solo se omite ese tipo de error: un fallo de la tira NeoPixel se propaga (RF-19) y el servicio se relanza a los 10 s. «Se reproduce» = se carga sin error, con al menos 1 frame, y se entrega a `startAnimation` o `startAnimationTest`, haya hardware o no. Si en una vuelta completa no se reproduce ningún archivo (directorio vacío, inexistente o todos rotos), se registra 1 ERROR más, que nombra el directorio y si existe, y se espera 10 s antes de repetir (igual que `RestartSec`). Tras la espera se repite la misma lista de archivos, sin volver a buscar en el directorio (igual que hoy) | usuario (PA-2) | RF-9 |
| RN-6 | Colores de la prueba de paneles | Panel 0 rojo `(255,0,0)`, 1 verde `(0,255,0)`, 2 azul `(0,0,255)`, 3 amarillo `(255,255,0)`; el panel n ≥ 4 repite el color de n mod 4; cada panel 2 s | panel-raspberry.md R-5; SP-3 | RF-11 |
| RN-7 | Registro | Archivo `animation_panel.log` junto al código; un único manejador con rotación solo por tamaño a 26 214 400 B (25 MB) por archivo y 5 copias; formato `%(asctime)s - %(name)s - %(levelname)s - %(message)s`; nivel INFO. Es una excepción a la rotación diaria de `python-logging.instructions.md` (con la hora falsa al encender, R-8, la diaria rotaría en cada sesión) | usuario (PA-6); `panel/LedMatrixAnimation.py:20-26` | RF-6, RF-13 |
| RN-8 | Mapeo píxel a LED | Un píxel (x, y) es válido si `0 ≤ x < ancho_total` y `0 ≤ y < altura_total` (x = `ancho_total` ya está fuera); su LED es `matriz[y * ancho_total + x]` | `panel/AnimationServer.py:314-323` | RF-5, RF-8, RF-17 |
| RN-9 | Repeticiones | GIF animado: `repeticiones_gif` (3 en la configuración actual); cualquier otra imagen, incluido un GIF no animado: `repeticiones` (1) | panel-raspberry.md F-5; SP-2 | RF-7 |
| RN-10 | Orden de reproducción | Todos los PNG y después todos los GIF del primer nivel de `directorio`, en el orden de `glob` | panel-raspberry.md R-6 | RF-17 |
| RN-11 | Qué se elimina en la reorganización | Solo un archivo cuyo sha256 es idéntico al de otro que se conserva, o los 4 `.pyc` de `navidad/panel/__pycache__/` autorizados expresamente; cualquier otro, no | decisiones-arquitectura.md (lista de eliminaciones y Nota 2026-11-15) | RF-2 |
| RN-12 | Color | `colourTuple((r, g, b))` devuelve `(r << 16) + (g << 8) + b` y el NeoPixel se crea sin `pixel_order`: no se toca | panel-raspberry.md Z-6; RU-3 fuera de alcance | RF-17 |
| RN-13 | `.pyc` rastreados | Los 12 `.pyc` rastreados (4 de `panel/__pycache__/*.cpython-313.pyc`, y 8 de Python 3.7 en `navidad/panel/__pycache__/*` y `navidad/ficheros navidad/panel/__pycache__/*`) salen del seguimiento de git (`git rm --cached`, sin borrarlos del disco) y `__pycache__/` entra en `.gitignore`, en F1 (que, a diferencia de lo escrito en el plan, deja de mantener rastreados estos 12), antes del movimiento F4. F0-bis recuenta eliminados y archivados con este cambio (RS-7). Cierra RI-10 | usuario (PA-4, 2026-11-22; decisión del 2026-11-22 sobre los 8 de `navidad/`) | RF-1, RF-4 |
| RN-14 | Excepción no capturada | Se registra con traza a nivel ERROR o superior; `SystemExit` y `KeyboardInterrupt` no; el proceso termina con código ≠ 0 | usuario (PA-8) | RF-19 |

## Entradas y datos

| ID | Dato | De dónde llega | Válido | Origen |
|---|---|---|---|---|
| DE-1 | `configuracion.json` | Archivo en la carpeta del código | Claves obligatorias `directorio`, `repeticiones`, `ancho`, `alto`, `panel_hor`, `panel_ver`, `primer_led`, `velocidad`; opcionales `repeticiones_gif`, `posicion_vertical`, `DEBUG`. En PC, `directorio` apunta a una carpeta local | `panel/Config.py:35-45`; RF-18 |
| DE-2 | `primer_led` | `configuracion.json` | `LEFT` (cualquier otro valor se trata como el otro sentido, comportamiento actual) | `panel/Panel.py:17-20` |
| DE-3 | `panel_hor` × `panel_ver` | `configuracion.json` | Enteros ≥ 1; se prueba con 1×1, 2×1 (actual) y 3×2 (6 paneles) | `panel/Panel.py:22`; RF-11 |
| DE-4 | Imagen PNG | Carpeta `directorio` | Cualquier modo de Pillow que se pueda pasar a RGB: `1`, `L`, `LA`, `P`, `RGB`, `RGBA`; de 1 px a varios cientos de ancho y 18 px de alto en uso real; ancho menor o igual al panel: un solo frame | panel-raspberry.md F-3 y log; RF-10 |
| DE-5 | Imagen GIF | Carpeta `directorio` | Animada (≥ 2 frames) o de 1 frame; menor, igual o mayor que 48×18 | RF-7, RF-8 |
| DE-6 | Archivo ilegible | Carpeta `directorio` | `.png` o `.gif` con contenido corrupto, truncado o de longitud 0 | RF-9 |
| DE-7 | Archivos del repositorio a mover o eliminar | Árbol de trabajo | Lista de `doc/decisiones-arquitectura.md`; nombres con espacios y acentos entre comillas | decisiones-arquitectura.md, riesgo 2 |
| DE-8 | `DEBUG` | `configuracion.json` | 0 (por defecto) o 1 | `panel/Config.py:45` |

## Requisitos no funcionales

| ID | Atributo | Requisito medible | Origen |
|---|---|---|---|
| RNF-1 | Registro | Rotación a 26 214 400 B por archivo y 5 copias; 1 solo gestor de rotación sobre el archivo | `panel/LedMatrixAnimation.py:22`; PA-6 |
| RNF-2 | Tiempos de reproducción | 250 ms por frame de PNG con `velocidad` 0,25; 100 ms por frame de GIF sin dato; sin variación respecto a hoy | panel-raspberry.md R-2, R-3 |
| RNF-3 | Conservación | 0 archivos de contenido distinto desaparecen (salvo los 4 `.pyc` del grupo C, autorizados) del repositorio al reorganizar: todo lo que no es duplicado idéntico queda en `raspberry-panel/`, `esp32/` o `archivo/`; el plan esperaba 104 archivos en `archivo/` al cerrar F5 y ese número se recalcula sobre `f25ee46` (RS-7) | usuario (P-10); decisiones-arquitectura.md Nota 2026-11-15 |
| RNF-4 | Firmware ESP32 tras moverlo | RAM 48 728 B (14,9 %) y flash 890 553 B (67,9 %), iguales a la línea base | decisiones-arquitectura.md, línea base F0 |
| RNF-5 | Arranque y reinicio del servicio | Espera de 4 s antes de arrancar, reinicio a los 10 s de caer y apagado a las 5 h del encendido: sin cambio | `panel/panel.service:7-10`; `panel/apagado.sh:2` |
| RNF-6 | Pruebas sin hardware | 0 librerías de hardware necesarias para ejecutarlas; se ejecutan en Windows con Python 3.11 o superior | panel-raspberry.md D-2 y C-1 a C-4; PA-5 |
| RNF-7 | Trazabilidad de vuelta atrás | 1 commit por fase de la reorganización, reversible con `git revert` | decisiones-arquitectura.md, Fases |
| RNF-8 | Compatibilidad de Python | El código y las dependencias funcionan con Python 3.11 o superior | usuario (PA-5, 2026-11-22; elevado de 3.10 a 3.11 por el usuario en la arquitectura, PQ-1, 2026-11-22) |

## Seguridad

No aplica (firmware). Origen: usuario (encargo del 2026-11-22: embebido en la Raspberry Pi, no aplicación empresarial; confirmado el 2026-11-22 el motivo real: sin usuarios, datos personales ni servicio de red). `apagado.sh` usa `sudo shutdown`: el README de RF-15 recomienda el mínimo privilegio (una línea de sudoers que solo permita `/sbin/shutdown` al usuario `pi`, que ejecuta el servicio) en vez de sudo sin contraseña general.

Dónde se comprueban los UAT: automáticos, sin hardware y en Windows (tira simulada, `time.sleep` simulado): UAT-5 a UAT-11, UAT-13, UAT-14, UAT-18 (simulación) y UAT-19. Por el usuario en la Pi: UAT-12, UAT-15 y UAT-17 (UAT-11 no se hace en la Pi: tiene 2 paneles). Por el usuario en PC: UAT-18 (ventana de `DEBUG` = 1). UAT-1 a UAT-4 y UAT-16: órdenes de solo lectura sobre el repositorio. UAT-9 añade un `.gif` truncado y un directorio vacío; UAT-7 usa un GIF de 1 frame en modo paleta.

## Restricciones

| ID | Restricción | Origen |
|---|---|---|
| RS-1 | Orden de trabajo: primero la reorganización (RF-1 a RF-4), después las pruebas de caracterización (RF-5), después los arreglos (RF-6 a RF-15, RF-18 y RF-19) | usuario (2026-11-22); panel-raspberry.md «Cómo trabajar con este código» |
| RS-2 | Solo arreglar: sin funcionalidad nueva, sin refactors, sin tocar RU-3, Z-6, Z-10 ni Z-13 | usuario (2026-11-22) |
| RS-3 | Python en la Pi con venv `/home/pi/venv` y servicio systemd con el usuario `pi`; las rutas de despliegue `/home/pi/...` de `panel.service` y `directorio` (en `configuracion.json`) no cambian | panel-raspberry.md «Despliegue»; P-2; PA-7 |
| RS-4 | Cada eliminación se anuncia y la autoriza el usuario; ya está autorizada la lista del plan, no otras; la salida del índice de los 12 `.pyc` rastreados (RN-13) la decidió el usuario | proceso-comun.instructions.md, punto 3; decisiones-arquitectura.md; PA-4 |
| RS-5 | La verificación en la placa la hace el usuario; no hay acceso a la Pi desde el repositorio | panel-raspberry.md («comparar con `/home/pi/panel`» sin hacer) |
| RS-6 | Línea base: el HEAD `f25ee46` («REBASE»). El historial se reescribió y `e23949d` no existe (el Orquestador lo comprobó con git: «Not a valid object name»); historial actual: `276dd31`, `9856e7a`, `ba19afa`, `4e6b690`, `3f6f7b6`, `bf1a3fc`, `f25ee46`. El plan de reorganización se recuenta sobre esa línea base y lo que solo existía en `e23949d` (p. ej. `navidad/1.bat`) se da por perdido | usuario (PA-4, 2026-11-22) |
| RS-7 | Antes de F1 hay un paso previo (F0-bis, solo lectura): regenerar el manifiesto sobre `f25ee46` (o el HEAD de ese momento), recontar eliminados y archivados, recompilar el ESP32 o demostrar que `src/`, `data/` y `platformio.ini` no cambiaron, reescribir F1 sobre el `.gitignore` actual (10 líneas, no 5), listar con `git ls-files "*__pycache__*"` todo `.pyc` rastreado (esperados 12, RN-13; si hay otros se informa al usuario, no se decide) y comprobar la dependencia C1 (zonas de escritura en `.agentes/politica.json`, que el Cuestionador no vio) | Acta del Cuestionador, objeción 1; PA-4 |
| RS-8 | La rotación del log (RN-7) es una excepción decidida por el usuario a `python-logging.instructions.md`, que pide rotación diaria y por tamaño y configuración única con `dictConfig` en el punto de entrada; la excepción cubre solo la rotación diaria: cómo se cumple el resto de la práctica con un único manejador lo valora el Ingeniero de diseño | Acta del Cuestionador, objeción 11; usuario (PA-6) |
| RS-9 | El modo simulación y el modo `DEBUG` de PC no se rompen: los arreglos (rutas fijas Z-8 incluidas) los respetan | usuario (PA-7, 2026-11-22) |

## UAT

| ID | RF | Dado | Cuando | Entonces | Resultado en fallo |
|---|---|---|---|---|---|
| UAT-1 | RF-1 | El plan F4 aplicado | Se lista el repositorio | Existen `raspberry-panel/panel/` y `raspberry-panel/ficheros/` y no `panel/` ni `ficheros/` en la raíz; `git ls-files "*.pyc"` no lista ninguno | La Pi se despliega desde rutas que ya no existen |
| UAT-2 | RF-2 | F2 aplicada | Se recalcula el sha256 de cada par eliminado = conservado | Coincide en todos los pares del manifiesto de F0-bis; si el recuento difiere de 141, F0-bis explica la diferencia | Se perdió una imagen: se revierte esa fase |
| UAT-3 | RF-3 | F5 aplicada | Se busca cada archivo único del inventario de P-10 presente en la línea base | Está en `archivo/` con el mismo sha256 | Se perdió un original: se recupera con `git show` del commit base |
| UAT-4 | RF-4 | F3 y F4 aplicadas | Se compilan los `.py` y el firmware | Compilan; RAM y flash son los de la línea base | El producto cambió sin pretenderlo: se revierte el commit |
| UAT-5 | RF-5 | Código sin corregir | Se ejecutan las pruebas C-1 a C-4 | Pasan todas | Se está caracterizando un comportamiento mal: se corrige la prueba antes de arreglar nada |
| UAT-6 | RF-6 | Panel arrancado | Se abre el log | Tiene las líneas INFO de `Panel` | Las trazas siguen perdidas |
| UAT-7 | RF-7 | Un `.gif` de 1 frame de 48×18 o menor en la carpeta | El bucle llega a él | Se ve la imagen `repeticiones` veces | El panel lo salta sin aviso |
| UAT-8 | RF-8 | Un GIF animado de 100×100, otro de 100×40 y otro de 48×18, y un GIF no animado de 100×100 | Se reproducen | El de 100×100 se ve de 18×18, el de 100×40 de 45×18, ambos arriba a la izquierda y sin píxeles en filas ajenas; el no animado de 100×100 igual que el animado; el de 48×18 igual que hoy | Se ven píxeles del borde derecho en el borde izquierdo de la fila siguiente |
| UAT-9 | RF-9 | Un `.png` corrupto y un `.gif` truncado entre dos válidos; después, un directorio vacío | El bucle los carga | El log da la causa con la ruta de cada uno; el resto del bucle sigue; con el directorio vacío hay 1 ERROR y una espera de 10 s por vuelta | El servicio cae y se relanza en bucle cada 10 s sin decir por qué |
| UAT-10 | RF-10 | Un PNG de paleta de 408×18, un PNG RGBA con un píxel rojo transparente y `banner1..12.png` | Se generan y se pintan | 73 frames RGB y sin excepción en el de paleta; el LED del píxel transparente apagado; los frames de las 12 pancartas idénticos a los de antes | `TypeError` en `colourTuple`, o una pancarta cambia de aspecto |
| UAT-11 | RF-11 | Configuración de 6 paneles | Se ejecuta la prueba de paneles y un frame | Sin `IndexError` y 6 paneles encendidos 2 s cada uno | El arranque cae con `IndexError` |
| UAT-12 | RF-12 | Código copiado a una carpeta que no es `/home/pi/panel` | Se ejecuta | Lee su `configuracion.json`; `panel.service` dice `User=pi` | Error de archivo no encontrado en `/home/pi/panel/` |
| UAT-13 | RF-13 | Panel en marcha | Se cuentan los gestores de archivo | Hay uno, y la excepción de rotación está escrita con fecha | Dos gestores rotan a la vez y corrompen el log |
| UAT-14 | RF-14 | Venv nuevo con Python 3.11 o superior | Se instalan las dependencias | Panel y pruebas arrancan | Falta una librería en un equipo limpio |
| UAT-15 | RF-15 | Repositorio reorganizado | Se abre `raspberry-panel/` | Hay servicio de apagado y su permiso está documentado | Reinstalar no reproduce el apagado |
| UAT-16 | RF-16 | Cierre | Se siguen los enlaces de los README | Todos existen | Enlaces rotos |
| UAT-17 | RF-17 | Arreglos aplicados, en la Pi | Prueba de paneles y 12 pancartas | Con el `panel.service` del repositorio instalado (`User=pi`; antes, `systemctl show panel -p User` da `pi`, si no, se para y se pregunta), panel 0 rojo y panel 1 verde; las 12 pancartas se ven igual y con los mismos tiempos | Colores o tiempos cambiaron: se revierte el arreglo |
| UAT-18 | RF-18 | Windows sin librerías de hardware y un `configuracion.json` local | Se arranca con `DEBUG` = 0 y luego con `DEBUG` = 1 | Con 0: sin escritura a LEDs y sin excepción; con 1: una ventana por frame ×10 | El modo de PC deja de funcionar y no se puede desarrollar sin la Pi |
| UAT-19 | RF-19 | Sin `configuracion.json`, y con una tira simulada que lanza una excepción al pintar | Se arranca el panel | El log tiene ERROR o superior con la traza, el proceso termina con código ≠ 0 y el error sale por stderr | La causa de la caída solo está en el journal |

## Trazabilidad

| RF | RN | UAT |
|---|---|---|
| RF-1 | RN-11, RN-13 | UAT-1 |
| RF-2 | RN-11 | UAT-2 |
| RF-3 | RN-11 | UAT-3 |
| RF-4 | RN-11, RN-13 | UAT-4 |
| RF-5 | RN-1, RN-8, RN-12 | UAT-5 |
| RF-6 | RN-7 | UAT-6 |
| RF-7 | RN-9 | UAT-7 |
| RF-8 | RN-3, RN-8 | UAT-8 |
| RF-9 | RN-5 | UAT-9 |
| RF-10 | RN-1, RN-4 | UAT-10 |
| RF-11 | RN-6 | UAT-11 |
| RF-12 | — | UAT-12 |
| RF-13 | RN-7 | UAT-13 |
| RF-14 | — | UAT-14 |
| RF-15 | — | UAT-15 |
| RF-16 | — | UAT-16 |
| RF-17 | RN-1, RN-2, RN-8, RN-10, RN-12 | UAT-17 |
| RF-18 | — | UAT-18 |
| RF-19 | RN-14 | UAT-19 |

## Riesgos y dependencias

| ID | Riesgo o dependencia | Probabilidad (A/M/B) | Impacto (A/M/B) | Mitigación |
|---|---|---|---|---|
| RI-1 | El historial se reescribió y `e23949d` no existe: la comprobación de blobs del plan perdió su base (materializado) | A | A | Línea base `f25ee46` y F0-bis (RS-6, RS-7); lo que solo estaba en `e23949d` se da por perdido por decisión del usuario |
| RI-2 | Al arreglar Z-2 y Z-4 cambia lo que se ve en pantalla con ciertas imágenes (transparencias, GIF grandes) | M | M | RN-3 y RN-4 decididas; comparar `banner1..12` antes y después (RF-10); pruebas C-2 y C-4 |
| RI-3 | Omitir un archivo roto (RN-5) esconde un error si nadie mira el log | B | M | El log lo registra en nivel ERROR con la causa (RF-9) |
| RI-4 | El servicio de apagado se reconstruye sin el original (SP-5) y no se puede probar sin la Pi | A | M | Marcarlo como reconstruido; lo valida el usuario en la Pi (RS-5) |
| RI-5 | OneDrive bloquea archivos al mover | M | M | Pausar la sincronización entre F2 y F5 (riesgo 1 del plan) |
| RI-6 | El plan de reorganización incluye mover el ESP32 (F3); es un producto aparte | B | M | SP-1 confirmado: va en esta tanda |
| RI-7 | Dependencia: Pillow ≥ 9.1 (el modo prueba usa `Image.Resampling`) | B | B | Declararlo en las dependencias (RF-14) |
| RI-8 | Las versiones de las librerías de la Pi no se conocen (sin `pip freeze`): una versión distinta puede cambiar el comportamiento | M | M | SP-4: se comprueban al desplegar; Python 3.11 o superior (RNF-8) |
| RI-9 | Los arreglos de RF-7, RF-8, RF-10 y la rotación (RF-13) tocan código que también usa el modo debug de PC | M | M | RF-18 y UAT-18 lo vigilan; RS-9 |
| RI-10 | Si hubiera `.pyc` rastreados, `__pycache__/` en `.gitignore` no los deja de rastrear | B | B | Cerrado el 2026-11-22: los 12 rastreados salen del índice (RN-13); en `tools/` no hay ninguno; F0-bis lo reconfirma (RS-7) |

## Fuera de alcance

- Funcionalidad nueva y mejoras: «solo arreglar» (usuario, 2026-11-22). Los RF-18 y RF-19 no son mejoras: el primero evita una regresión y el segundo es decisión expresa del usuario (PA-8).
- RU-3 (orden de color configurable), Z-6 (código engañoso de color; no se toca `colourTuple` ni la creación del NeoPixel), Z-10 (código antiguo, que va a `archivo/`) y Z-13 (horas del log).
- Los bytes nulos del log, atribuidos a cortes de corriente: no se corrigen.
- Cambiar el formato del log, el nivel o la rotación (solo se unifica el gestor).
- Cambiar `directorio` en `configuracion.json`, las rutas `/home/pi/...` de los servicios o las 5 horas de `apagado.sh`.
- Corregir el firmware ESP32 (Z-n de `esp32-gif-visualizer.md`): solo se mueve de carpeta.
- Decidir si las imágenes de `archivo/` se borran: lo decidirá el usuario más adelante.
- Instalar o probar nada en la Pi desde el repositorio.
- Comparar con la copia real de `/home/pi/panel` (sigue pendiente, sin bloquear).
- Recuperar lo que solo existía en `e23949d` (p. ej. `navidad/1.bat`).
- Fijar versiones de librerías con `pip freeze`: no hay.

## Preguntas abiertas

| ID | Pregunta | Bloquea |
|---|---|---|
| — | Ninguna (PA-1 a PA-8 respondidas el 2026-11-22; ver «Cambios») | — |

## Supuestos

| ID | Supuesto | Confirmado |
|---|---|---|
| SP-1 | La reorganización de esta tanda es el plan F0 a F7 ya autorizado el 2026-11-14 completo, incluido mover el ESP32 a `esp32/` (opción A), sobre la línea base `f25ee46` (F0-bis recuenta) | sí |
| SP-2 | Un `.gif` no animado se trata como un PNG: si cabe en el panel, un solo frame con `repeticiones` repeticiones; si es mayor, manda PA-1 (RN-3: se reduce, no se desplaza) | sí |
| SP-3 | Con más de 4 paneles, los colores de la prueba se repiten cíclicamente (panel n usa el color n mod 4) | sí |
| SP-4 | `requirements.txt` sin versiones fijas, salvo Pillow ≥ 9.1; Python 3.11 o superior (decisión del usuario, PA-5, elevada a 3.11 en la arquitectura, PQ-1); las versiones de las librerías y `python3 --version` del venv de la Pi se comprueban al desplegar | sí |
| SP-5 | El servicio de apagado se reconstruye con lo conocido (arranca al encender la Pi y ejecuta `apagado.sh`; P-9) porque el original no está en el repositorio; el usuario puede aportar el original | sí |
| SP-6 | Las pruebas de caracterización C-1 a C-4 de `panel-raspberry.md` son el conjunto mínimo de RF-5; cada arreglo añade la prueba de su RF | sí |

## Glosario

- **Panel:** cada módulo de 24×18 LEDs WS2812; el panel completo son 2 módulos (48×18, 864 LEDs).
- **Pancarta:** PNG ancho que se desplaza horizontalmente.
- **Caracterización:** prueba que fija lo que el código hace hoy, para detectar cambios no queridos.
- **Línea base:** estado del repositorio contra el que se comprueba que no se pierde nada (`f25ee46`).
- **Modo simulación:** ejecución sin librerías de hardware (D-2, F-8). **Modo debug:** `DEBUG` = 1, ventana por frame (F-7).
- **RU-3, Z-n, C-n, P-n, R-n, F-n, D-n:** identificadores de [panel-raspberry.md](../diseno/panel-raspberry.md) e [indice.md](../diseno/indice.md).

## Cambios

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-11-22 | Creación del análisis en estado `borrador` | Encargo del Orquestador, modo analizar |
| 2026-11-22 | Ronda 1 del Cuestionador incorporada (16 objeciones): RS-7 y RS-8, PA-4 a PA-8, RF-2, RF-6, RF-9, RF-10, RF-14, RF-17, RN-5, CU-6, UAT «dónde», seguridad. RF-12 queda sujeto a PA-7 (`User=` según el dato de la Pi) y su README documenta `journalctl -u panel`. No hubo ronda 2 | Acta del Cuestionador técnico, ronda 1 |
| 2026-11-22 | Respuestas del usuario incorporadas. PA-4: línea base `f25ee46`, `e23949d` no existe (RS-6, RS-7, RI-1), 4 `.pyc` de `panel/` fuera de git (RN-13). PA-1: GIF mayor, animado o no, se reduce (RN-3, RF-7, RF-8, SP-2). PA-2: RN-5 con espera de 10 s. PA-3: RN-4 sobre negro con comprobación previa de `banner1..12` (RF-10). PA-5: sin `pip freeze`, Python 3.10 o superior (RF-14, RNF-8, SP-4, RI-8). PA-6: excepción a python-logging (RN-7, RS-8, RF-13). PA-7: `User=pi` confirmado (RF-12). PA-8: toda excepción no capturada al log (RF-19, RN-14). Nuevo RF-18 (modo simulación y debug en PC, RS-9, UAT-18, CU-8). SP-1 a SP-6 confirmados. Seguridad «no aplica» confirmada. Estado a `en revisión` | Encargo del Orquestador, modo incorporar respuestas |
| 2026-11-22 | Ronda 2 del Cuestionador incorporada (11 objeciones, 0 bloqueantes): alcance de RN-4 a todo PNG y GIF por PA-3 y comparación por LED de la tira simulada (RF-10); «reproducir» definido y CU-8 remitido a RN-5; comprobaciones de `User`, Python y copia de PC fuera del repositorio (RF-12, UAT-17, RF-18, UAT-18 acotado a 2 vueltas); criterio de RF-13 ejecutable por los agentes (excepción en RN-7 y en la memoria de decisiones); RF-1 y RN-13 en términos de `git ls-files` y fase F1; redondeo y filtro en RN-3; motivo corregido en RF-19 (código 1, `Restart=always`); UAT-2 coherente con RF-2. Estado a `cuestionado` | Acta del Cuestionador técnico, ronda 2 |
| 2026-11-22 | Aprobación del usuario («Aprobado»); estado a `aprobado`, sin nueva ronda del Cuestionador (cambio mínimo). Decisiones del usuario: (1) **comité de decisión omitido**: `check_umbral_comite.py` indicaba convocar (19 RF > 8) y el usuario decide saltarlo, por ser arreglos acotados sin funcionalidad nueva; (2) **objeción 6 (RF-9) descartada entera**: un GIF truncado o corrupto se registra y se salta como cualquier archivo que falla, sin reproducir frames parciales, aceptando que cambia el comportamiento actual; (3) los 8 `.pyc` de Python 3.7 de `navidad/` salen también del índice con `git rm --cached`, sin borrarlos del disco (RN-13, RF-1, RF-4, RS-4, RS-7, RI-10, UAT-1) | Respuestas del Orquestador, modo incorporar respuestas |
| 2026-11-22 | **Python mínimo de 3.10 a 3.11** (RNF-6, RNF-8, RF-14, UAT-14, RI-8, SP-4 y la comprobación de `python3 --version` de RF-12/UAT-17). El análisis sigue `aprobado` | Decisión del usuario en la arquitectura (PQ-1): Python 3.10 está fuera de soporte desde 2026-10-01 y Pillow 13 exige 3.11; eligió «3.11 o superior». Encargo del Orquestador, modo incorporar respuestas |

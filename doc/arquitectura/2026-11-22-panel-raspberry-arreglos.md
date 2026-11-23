# Arquitectura: Panel Raspberry Pi, reorganización y arreglos

- **Análisis de origen:** `doc/analisis/2026-11-22-panel-raspberry-arreglos.md` (aprobado el 2026-11-22)
- **Documento de diseño:** `doc/diseno/panel-raspberry.md` (validado el 2026-11-14) e `doc/diseno/indice.md`
- **Estado:** aprobado
- **Fecha:** 2026-11-22

## Contexto y alcance

El sistema es el programa Python de la Raspberry Pi que pinta en bucle los PNG y GIF de una carpeta en un panel WS2812 de 48×18 (864 LEDs, GPIO18), lanzado por systemd. Hoy son cinco módulos planos en `panel/` (`LedMatrixAnimation.py`, `Config.py`, `Panel.py`, `Animation.py`, `AnimationServer.py`) que se importan por nombre, más `configuracion.json`, `panel.service` y `apagado.sh`.

Este documento cubre:

- La **reorganización opción A** ya decidida el 2026-11-14 (`doc/decisiones-arquitectura.md`), con los ajustes del análisis (línea base `f25ee46`, paso F0-bis, salida del índice de 12 `.pyc`).
- Los **arreglos** Z-1, Z-2, Z-3, Z-4, Z-5, Z-7, Z-8, Z-9, Z-11 y Z-12, y las decisiones RF-18 (modo PC) y RF-19 (excepción no capturada al log).
- Las **pruebas sin hardware** (RF-5) y la **declaración de dependencias** (RF-14).

Queda fuera, por el análisis: funcionalidad nueva, RU-3, Z-6, Z-10, Z-13, el firmware ESP32 (solo se mueve), cambiar formato, nivel o tamaño de rotación del log, las rutas `/home/pi/...` y las 5 h de `apagado.sh`.

Criterio que manda en todo el documento, pedido por el usuario el 2026-11-22: **lo más simple que funcione**. Cada arreglo vive en el módulo que ya tiene esa responsabilidad. No se añaden módulos, capas, abstracciones ni dependencias de ejecución.

## Atributos de calidad

| ID | Atributo | Prioridad | Qué significa aquí | Origen |
|---|---|---|---|---|
| AC-1 | Corrección sin regresión | 1 | C-1 a C-4 pasan antes y después de los arreglos sin tocarlas. Las 12 pancartas dan el mismo valor en cada uno de los 864 LED de la tira simulada en cada frame. Frames y duraciones son iguales a los del log de diciembre de 2025 (250 ms por frame de PNG, 100 ms por defecto en GIF) | Análisis RF-17, RF-10, RNF-2; RS-2 |
| AC-2 | Conservación del contenido | 2 | Al reorganizar no desaparece ningún archivo de contenido distinto. Solo se eliminan los duplicados por sha256 y los 4 `.pyc` del grupo C. Cada fase va en 1 commit que se puede revertir con `git revert` | Análisis RNF-3, RNF-7, RN-11 |
| AC-3 | Simplicidad | 3 | 0 módulos, clases de servicio, capas o dependencias de ejecución nuevas. Lo único nuevo en el código es un tipo de excepción, dos funciones privadas de `Animation.py`, la constante de configuración del log y las dos constantes de versión (DA-14). Cada arreglo toca como mucho 2 de los 5 módulos. La excepción es DA-3, que quita la configuración del log de los 4 módulos que la tienen | Usuario, 2026-11-22 («lo más simple que funcione», «solo arreglar»); análisis RS-2 |
| AC-4 | Robustez ante las imágenes de la carpeta | 4 | Ninguna entrada de DE-4 a DE-6 tumba el servicio ni pinta un LED fuera de su sitio. Para cada imagen válida, `Animation` no lanza `ImageLoadError` y entrega frames RGB que caben en el panel. Cuentan como válidas: los modos `1`, `L`, `LA`, `P`, `P` con transparencia, `RGB` y `RGBA`, y los GIF de 1 frame y animados, menores, iguales y mayores que el panel. Para un archivo de DE-6, `Animation` lanza `ImageLoadError` con `__cause__` y el bucle sigue. Así, un fallo de programación de la carga se ve en las pruebas y no queda escondido como archivo omitido | Análisis RF-7 a RF-11, RN-3, RN-5, RN-8; acta del Cuestionador, ronda 1, objeción 3 |
| AC-5 | Diagnóstico por el log | 5 | Un solo `animation_panel.log` recoge las trazas de los 5 módulos. Todo archivo omitido deja una línea ERROR con ruta, tipo y mensaje de la causa. Toda excepción no capturada deja su traza antes de terminar | Análisis RF-6, RF-9, RF-13, RF-19; CU-6 |
| AC-6 | Compatibilidad de plataforma | 6 | El código corre con Python 3.11 o superior (usuario, PQ-1, 2026-11-22; sustituye al «3.10 o superior» de RNF-8). En Windows y sin librerías de hardware, `DEBUG` = 0 completa 2 vueltas sin excepción y `DEBUG` = 1 abre una ventana por frame | Análisis RNF-8, RF-18, RS-9 |
| AC-7 | Pruebas sin hardware | 7 | `pytest` corre en Windows con Python 3.11 o superior, sin `neopixel`, `board` ni `rpi_ws281x`, y sin cambiar el código de producción para poder probarlo | Análisis RNF-6, RF-5; SP-6 |
| AC-8 | Despliegue reproducible | 8 | Con solo el repositorio se reinstalan en una Pi limpia el panel y el apagado: dos unidades systemd, un archivo de dependencias y el README | Análisis RF-12, RF-14, RF-15 |

## Restricciones

| ID | Restricción | Origen |
|---|---|---|
| RS-1 | Orden: primero la reorganización (RF-1 a RF-4), después la caracterización (RF-5) y después los arreglos. RF-6 va con RF-13 o después | Análisis RS-1, RF-6 |
| RS-2 | Solo arreglar. No se tocan RU-3, Z-6, Z-10 ni Z-13. `colourTuple` y la creación del NeoPixel no cambian (RN-12) | Análisis RS-2, RN-12 |
| RS-3 | En la Pi: venv `/home/pi/venv`, usuario `pi` y systemd. No cambian las rutas `/home/pi/panel` y `/home/pi/ficheros` | Análisis RS-3; P-2 |
| RS-4 | Hardware fijo: WS2812 en `board.D18`, 2 paneles de 24×18 encadenados en serpentina, primer LED abajo | `doc/diseno/panel-raspberry.md`, «Contratos externos» |
| RS-5 | Los módulos se importan por nombre plano desde su carpeta. Es un proyecto plano existente y no se migra a `src/` sin autorización | `doc/diseno/panel-raspberry.md`, «Cómo trabajar»; `python-proyecto.instructions.md` |
| RS-6 | Línea base `f25ee46`. `e23949d` no existe. Antes de F1 va F0-bis, solo de lectura | Análisis RS-6, RS-7 |
| RS-7 | La verificación en la placa la hace el usuario; desde el repositorio no hay acceso a la Pi | Análisis RS-5 |
| RS-8 | Logging con `dictConfig` en el punto de entrada y un logger por módulo, con la excepción de la rotación diaria que decidió el usuario (RN-7) | `python-logging.instructions.md`; análisis RS-8, RN-7 |
| RS-9 | Zonas del arnés (leídas en `.agentes/politica.json` el 2026-11-22): `programador-python` y `programador-arduino` escriben en `**`, así que la condición C1 de la reorganización queda cubierta. El `probador-funcional` solo escribe `**/test_*.py`, `**/conftest.py` y `tests/**` de la raíz | `.agentes/politica.json` |
| RS-10 | Excepciones concretas; un `except Exception` amplio solo en el borde del programa o en el bucle de servicio; toda traducción se encadena con `from`. Hay una salvedad: la captura que traduce en `Animation.loadFile` (DA-5, PQ-7) | `python-basico.instructions.md`, «Errores y excepciones» |

## Plataformas y versiones

| Plataforma | Versión | Tipo de soporte | Fuente y fecha | Motivo |
|---|---|---|---|---|
| Python en la Pi (venv `/home/pi/venv`) | 3.11 o superior | impuesta por el proyecto | Usuario, PQ-1 (2026-11-22), que sustituye a PA-5. devguide.python.org/versions, consultado el 2026-11-22: la 3.10 está en fin de vida desde el 2026-10-01 y la 3.11 tiene soporte de seguridad hasta 2027-10 | La versión del venv de la Pi no se conoce. Al desplegar se comprueba que Raspberry Pi OS trae la 3.11 o superior; si no, se para y se pregunta (RF-12) |
| Python en el PC (Windows, pruebas y modo PC) | 3.15 | estable sin LTS | devguide.python.org/versions, 2026-11-22: rama *bugfix*, publicada el 2026-10-09. Pillow 13.0.0 y pytest 9.2.0 declaran soporte para 3.15 (PyPI, 2026-11-22) | Es la última rama con soporte activo y todas las dependencias de prueba la soportan (`python-version.instructions.md`). El código no usa sintaxis posterior a la 3.11 (AC-6) |
| Pillow | `>=9.1`, sin tope | impuesta por el proyecto | Análisis SP-4 y RI-7. PyPI (pypi.org/pypi/pillow/json), 2026-11-22: la última es 13.0.0, que exige Python 3.11 o superior y por tanto se instala en la Pi y en el PC | `Image.Resampling` exige 9.1 o superior. Se usa en el modo `DEBUG` y en el ajuste de GIF (DA-7) |
| pytest | `>=9.2,<10` | estable sin LTS | PyPI (pypi.org/pypi/pytest/json), 2026-11-22: 9.2.0 del 2026-10-27, Python 3.10 o superior | Herramienta de pruebas de RF-14. Política de línea mayor |
| adafruit-circuitpython-neopixel | sin fijar | impuesta por el proyecto | Análisis SP-4. PyPI, 2026-11-22: la última es 6.4.2, del 2026-04-23 | Ya la usa el código (`AnimationServer.py:23`). La versión de la Pi se comprueba al desplegar (SP-4) |
| adafruit-blinka, rpi_ws281x | sin fijar | impuesta por el proyecto | Análisis SP-4 (2026-11-22). No consultadas: se comprueban al desplegar | Ya las usa el código (`AnimationServer.py:24`, `:35-37`) |
| systemd y Raspberry Pi OS | las de la Pi | impuesta por el proyecto | `doc/diseno/panel-raspberry.md`, «Despliegue» (2026-11-14) | No se cambian |

## Alternativas

| ID | Alternativa | A favor | En contra | Veredicto |
|---|---|---|---|---|
| ALT-1 | Lo más simple que podría funcionar: arreglos puntuales dentro de los 5 módulos actuales, cada uno en el módulo que ya tiene esa responsabilidad, más los archivos de despliegue y de pruebas que faltan | Cambia lo mínimo y mantiene las firmas, los imports planos y la estructura (AC-3). C-1 a C-4 se escriben contra el código de hoy y siguen valiendo después (AC-1). Cada arreglo se prueba y se revierte solo | Se quedan sin limpiar el código muerto (`colour`, `colourrgb`, `ORDER`) y los nombres engañosos (Z-6), porque no se piden | elegida |
| ALT-2 | Mantener lo que hay: solo reorganizar, sin arreglos | Riesgo cero de regresión | No cumple RF-6 a RF-19, que el usuario ha pedido | descartada: no cumple el análisis (AC-4, AC-5, AC-8) |
| ALT-3 | Reestructurar en un paquete `src/` instalable con `pyproject.toml`, con un cargador de imágenes, un renderizador abstracto con NeoPixel y simulación, y la tira inyectada por constructor | Más fácil de probar por inyección, y cumple al pie de la letra `python-proyecto` (un único `pyproject.toml`) | Es una reestructuración no pedida (RS-2, RS-5). Rompe C-1 a C-4 y la comparación antes y después (AC-1). Exige construir e instalar el paquete en la Pi. Las pruebas ya se pueden escribir sin ella (DA-13) | descartada: va contra AC-1 y AC-3, y ningún atributo la exige |
| ALT-4 | Arreglar solo en el borde de pintado: convertir, recortar y comprobar límites en `AnimationServer.startAnimation`, sin tocar `Animation` | Un solo módulo tocado | Repite la conversión en cada frame y en cada repetición. No arregla Z-3 (el GIF estático no genera frames) ni RF-9 (la carga). El modo `DEBUG` (`startAnimationTest`) seguiría recibiendo frames sin normalizar. Mezcla pintar con decodificar | descartada: no cubre RF-7, RF-9 ni RF-18 (AC-4, AC-6) |

## Decisiones

| ID | Decisión | Justifican | Alternativa descartada | Consecuencias | Reversibilidad |
|---|---|---|---|---|---|
| DA-1 | **Arreglos dentro de los módulos actuales.** Se mantienen los 5 módulos planos, sus firmas públicas y sus imports por nombre. Lo único nuevo en el código es la excepción `ImageLoadError` y dos funciones privadas de normalización en `Animation.py` (DA-6 y DA-7) | AC-1, AC-3 | ALT-3: paquete `src/` con capas | El código muerto y los nombres engañosos de Z-6 siguen como están. Cada tarea toca 1 o 2 módulos | fácil |
| DA-2 | **Reorganización opción A, como se decidió el 2026-11-14,** con los ajustes del análisis: F0-bis recuenta sobre `f25ee46`, y F1 añade `__pycache__/` al `.gitignore` y saca del índice los 12 `.pyc` con `git rm --cached` (RN-13). Dentro de `raspberry-panel/`, lo que se despliega está en `panel/`; las pruebas y las dependencias de prueba quedan fuera de esa carpeta | AC-2, AC-8 | Rehacer el plan desde cero: la estructura y las eliminaciones ya están autorizadas; solo cambia la línea base | Ver «Estructura» en «Componentes». Para desplegar se copia `raspberry-panel/panel/` entera a `/home/pi/panel` sin arrastrar pruebas | fácil |
| DA-3 | **Logging: una sola configuración en el punto de entrada.** La configuración es una constante de módulo `LOGGING_CONFIG` en `LedMatrixAnimation.py`, que solo define un diccionario y no tiene efectos al importar. El bloque `if __name__ == "__main__":` se reduce a `logging.config.dictConfig(LOGGING_CONFIG)` y `main()`. La constante pone un único `RotatingFileHandler`, con clave `archivo`, en el logger raíz: `animation_panel.log` junto a `LedMatrixAnimation.py`, 26 214 400 B, 5 copias, el formato de hoy, nivel INFO, `encoding` utf-8 y `disable_existing_loggers: False`. Los 5 módulos solo hacen `logger = logging.getLogger(__name__)`, sin gestores ni `setLevel`. Se quitan los 3 bloques de configuración (`LedMatrixAnimation.py:17-26`, `Animation.py:9-18`, `AnimationServer.py:9-18`) y `from venv import logger` (`Panel.py:2`). No hay rotación diaria (excepción RN-7). Tamaño y copias quedan en ese diccionario, que es código, y no en `configuracion.json`. Si se leyeran de allí, no se podría registrar en el archivo el fallo de esa misma configuración (RF-19). Esto es una excepción a `python-logging` («en la configuración, nunca en el código») que el usuario aceptó el 2026-11-22 (PQ-5) | AC-5, AC-3, AC-7 | (a) Mantener un gestor por módulo, que es la causa de Z-7. (b) Un módulo nuevo `log_config.py`, que añade un sexto módulo para cuatro líneas. (c) `basicConfig`, que va contra `python-logging`. (d) Configurar al importar `LedMatrixAnimation`, que ensucia cualquier prueba que lo importe. (e) Leer tamaño y copias de `configuracion.json`, que deja sin log el caso de RF-19 | Las pruebas aplican la constante real, con `filename` redirigido a `tmp_path`, y así comprueban RG-1 contra lo que corre en producción. Las trazas de `Panel` llegan al log con el nombre `Panel` (RF-6), unas 40 líneas más por arranque. Los nombres de logger no cambian (`__main__`, `Animation`, `AnimationServer`, `Panel`). Importar un módulo ya no crea el log. Los mensajes que `AnimationServer` emite al importarse (`:28`, `:33`) salen antes de configurar el log: el INFO de Windows se pierde y el WARNING de la Pi va a stderr, es decir, al journal (RG-2) | fácil |
| DA-4 | **Excepción no capturada (RF-19).** Dentro de `main()`, todo su cuerpo va en `try:` / `except Exception: logger.exception(...)` / `raise`. Así se prueba llamando a `main()` con `Config` parcheado, sin lanzar el script. El `raise` conserva la traza en stderr y el código de salida 1. `KeyboardInterrupt` y `SystemExit` no son `Exception` y no generan la línea | AC-5, AC-3 | `sys.excepthook` propio: menos visible y hay que acordarse de llamar al anterior para seguir escribiendo en stderr | Una caída deja la traza en el log y en el journal. systemd relanza a los 10 s como hoy | fácil |
| DA-5 | **Errores de carga (RF-9, RN-5).** `Animation.loadFile` cambia su `except:` por `except Exception as err: raise ImageLoadError(f"{ruta}: {type(err).__name__}: {err}") from err`. Se captura `Exception` porque Pillow no tiene un conjunto cerrado de errores de decodificación (`OSError`, `SyntaxError`, `ValueError`, `EOFError`, `DecompressionBombError`, `struct.error`…). Aquí solo se traduce y se encadena, no se traga. Se acepta que esta captura también convierta en archivo omitido un fallo de programación de la propia carga (DA-6 y DA-7): AC-4 (que una imagen rara no deje el servicio en un bucle de reinicios) pesa más que distinguirlo en ejecución. Ese fallo se detecta en las pruebas, que exigen que ninguna imagen válida dé `ImageLoadError` (AC-4). Es una excepción razonada a `python-basico`, que solo admite capturas amplias en el borde. El usuario la aceptó el 2026-11-22 (PQ-7) y queda en la memoria de decisiones. `ImageLoadError(Exception)` se define en `Animation.py`. `loadAnimatedGif` deja de capturar errores, para que un GIF truncado se descarte entero. En `MainClass.start`, solo la construcción de `Animation` va dentro de `try … except ImageLoadError`, que registra con `logger.exception` y pasa al siguiente archivo. `startAnimation` queda fuera del `try`: un fallo de la tira se propaga (DA-4). Si en una vuelta no se reproduce ningún archivo, se registra 1 ERROR con el directorio y si existe, y se espera 10 s (constante con nombre en `LedMatrixAnimation.py`, que llama a `time.sleep` a través del módulo `time`) | AC-4, AC-5, AC-3 | (a) Capturar `Exception` en el bucle alrededor de la construcción, sin tipo propio. El bucle también atraparía un fallo de la tira si alguien moviera `startAnimation` dentro del `try`, y la excepción no nombraría la ruta, que es lo que pide RF-9. (b) Una lista cerrada de excepciones de Pillow: incompleta y frágil entre versiones | Cambia el tipo de excepción de `Animation` de `Exception` a una subclase, compatible con quien capture `Exception`. Los frames parciales de un GIF roto ya no se ven (cambio aceptado, PA-2). Desaparece el bucle vacío al 100 % de CPU cuando no hay archivos. Un archivo roto deja una traza en cada vuelta (RG-8) | fácil |
| DA-6 | **Normalización a RGB sobre negro (RF-10, RN-4).** Una función privada de `Animation.py` recibe una imagen y devuelve una RGB. Si la imagen tiene alfa (`RGBA`, `LA`, `PA`) o `transparency` en `info`, la pasa a RGBA y la compone sobre un fondo negro `(0,0,0)` con su alfa. Si no, la pasa con `convert("RGB")`. Se aplica una vez a la imagen entera al empezar `generateFrames`, antes de recortar, y a cada frame en `loadAnimatedGif` en lugar de `convert("RGB")` | AC-4, AC-1, AC-6 | ALT-4: convertir al pintar. Repite el trabajo en cada repetición y el modo `DEBUG` no lo recibiría | Todos los frames que salen de `Animation` son RGB de 3 canales, también para `startAnimationTest`. Un píxel transparente queda apagado. Una pancarta RGB no cambia. Antes de aceptar el cambio se comparan `banner1..12` (RF-10) | fácil |
| DA-7 | **Ajuste de los GIF (RF-7, RF-8, RN-3, RN-9).** En `loadFile`, para un `.gif`, si ancho > `ancho_total` o alto > `altura_total`, todos sus frames se reducen al mismo tamaño con `Image.Resampling.NEAREST`. Ese filtro no crea colores que no estén en el GIF. La escala es `s = min(ancho_total/w, altura_total/h)` y el tamaño es `(round(w·s), round(h·s))`, limitado a `[1, ancho_total] × [1, altura_total]`. El tamaño final se calcula una vez, con el tamaño del GIF. En un GIF animado, `loadAnimatedGif` procesa cada frame en orden: lo normaliza (DA-6), lo ajusta y lo guarda. Así nunca guarda frames a tamaño original y la memoria queda acotada al tamaño del panel por frame; el GIF tiene `is_animated` = True. Un GIF no animado se ajusta en `loadFile` y sigue por `generateFrames` como un PNG, que lo normaliza una sola vez: como ya cabe, da 1 frame de `velocidad` × 1000 ms, con `is_animated` = False y por tanto `repeticiones` | AC-4, AC-3, AC-1 | (a) Recortar el GIF al panel: pierde parte de la imagen y va contra PA-1. (b) Un camino propio para el GIF estático: duplica lo que ya hace `generateFrames` | 100×100 da 18×18, 100×40 da 45×18, 100×37 da 48×18 y 30×10 no se toca. Un GIF estático o un PNG que cabe se ve `velocidad` (250 ms) × `repeticiones`, igual que un PNG hoy. El usuario lo confirmó el 2026-11-22 (PQ-4) y se comprueba en UAT-7 | fácil |
| DA-8 | **Límites al pintar (RF-8, RN-8).** `startAnimation` recorre solo `0 ≤ x < min(frame.width, ancho_total)` y `0 ≤ y < min(frame.height, altura_total)`. Esto sustituye a la comprobación `matrix_index < len(panel.matriz)`, que deja pasar el desborde a la fila siguiente | AC-4, AC-1 | Fiarse solo de DA-7: un frame mayor por cualquier otro camino volvería a desbordar sin que nadie lo vea | RN-8 se cumple en el único punto que escribe LEDs. C-4 no cambia, porque los frames de hoy ya caben | fácil |
| DA-9 | **Cualquier número de paneles (RF-11, RN-6).** `testPanels` usa `colores[n % 4]` y el nombre del color con el mismo índice. El contador de `startAnimation` tiene un elemento por panel (`paneles_horizontal × paneles_vertical`), y la línea «Frame 0 - LEDs encendidos por panel» lista todos los paneles | AC-4, AC-3 | Ampliar la lista de colores a N fijos: vuelve a fallar con N + 1 | Con 2 paneles, esa línea del log da P0 y P1 en vez de P0 a P3. No afecta a RF-17, que compara frames y duraciones | fácil |
| DA-10 | **`configuracion.json` de la carpeta del código (RF-12, Z-8).** `Config` abre `os.path.join(os.path.dirname(os.path.abspath(__file__)), jsonfile)`. Firma y claves no cambian. Por la semántica de `os.path.join`, una ruta absoluta en `jsonfile` se usa tal cual: es lo que usan las pruebas | AC-6, AC-8, AC-7 | (a) Directorio de trabajo: depende de desde dónde se lance; en la Pi vale por `WorkingDirectory`, pero en el PC no. (b) Argumento de línea de órdenes o variable de entorno: es una interfaz nueva que no se pide | En `/home/pi/panel` lee el mismo archivo que hoy. Si falta, `FileNotFoundError` nombra la ruta buscada y DA-4 la registra | fácil |
| DA-11 | **Unidades systemd (RF-12, RF-15).** En `panel.service` solo cambia `User=owner` a `User=pi`. Nuevo `raspberry-panel/panel/apagado.service`: `Type=simple`, `User=pi`, `ExecStart=/bin/bash /home/pi/panel/apagado.sh`, `WantedBy=multi-user.target`, con un comentario que dice que está reconstruido y no copiado de la Pi. Con `/bin/bash` explícito no depende del bit de ejecución, que Windows y git pueden perder. `apagado.sh` no cambia. El README pide comprobar `sudo -l` como `pi`. Si `pi` ya tiene `NOPASSWD: ALL` (lo habitual en Raspberry Pi OS, `/etc/sudoers.d/010_pi-nopasswd`), no se toca sudoers. En ese caso, el mínimo privilegio solo existe si el usuario retira ese archivo, y es decisión suya. Si `pi` no tiene sudo sin contraseña, se añade con `visudo` una línea limitada a `shutdown`. El README también pide comprobar que `apagado.sh` y las dos unidades llegan a la Pi con finales de línea LF (PQ-6) | AC-8, AC-3 | `User=root` sin sudoers: más simple de instalar, pero un servicio de root que ejecuta un script que `pi` puede editar da a `pi` root sin límites, y el análisis recomienda el mínimo privilegio | Al reinstalar hacen falta `daemon-reload` y `enable` de las dos unidades. Si en la Pi existe el servicio original con otro nombre, habría dos apagados (RG-12) | fácil |
| DA-12 | **Dependencias en dos archivos de requisitos (RF-14).** `raspberry-panel/panel/requirements.txt` lleva lo de ejecución en la Pi: `Pillow>=9.1`, `adafruit-circuitpython-neopixel`, `adafruit-blinka` y `rpi_ws281x`, sin fijar (SP-4). Viaja con el código. `raspberry-panel/requirements-dev.txt` lleva lo de prueba, instalable en Windows: `Pillow>=9.1` y `pytest>=9.2,<10`. No incluye el primero, porque `rpi_ws281x` no se instala en Windows. Los dos llevan en la cabecera un comentario con la versión mínima de Python (3.11), que también figura en el README. El README recomienda guardar `pip freeze` del venv de la Pi después de desplegar, solo como registro de lo instalado, sin fijar nada | AC-8, AC-7, AC-3 | `pyproject.toml` con `[project]` y grupos de dependencias, como pide `python-proyecto`. El proyecto no es un paquete. Instalar solo dependencias necesita un backend de construcción o `pip install --group` (pip 25.1 o superior), y la versión de pip de la Pi no se conoce. RF-12 y SP-4 ya hablan de `requirements.txt` | `Pillow>=9.1` figura en dos archivos (dos líneas). Es una desviación de `python-proyecto` que el usuario aceptó el 2026-11-22 (PQ-2) | fácil |
| DA-13 | **Pruebas en `raspberry-panel/tests/`, sin puntos de inyección nuevos (RF-5).** Un `conftest.py` añade `raspberry-panel/panel` a `sys.path`. Los dobles se ponen con `monkeypatch` sobre lo que ya existe: `AnimationServer.HARDWARE_AVAILABLE`, el atributo `LedStrip` (con `fill`, `__setitem__` y `show`) y `time.sleep` en `AnimationServer` y en `LedMatrixAnimation`. El bucle infinito se corta con un doble de `startAnimation` que lanza `KeyboardInterrupt` tras N llamadas. Las imágenes se sintetizan en `tmp_path`, las pancartas se leen de `raspberry-panel/ficheros/` y los datos esperados van dentro de los `test_*.py`. Se lanzan con `py -3 -m pytest raspberry-panel/tests` | AC-7, AC-1, AC-3 | (a) Pruebas dentro de `panel/`: se copiarían a la Pi. (b) Inyectar la tira por constructor: es un cambio de diseño solo para probar, y ALT-3 ya está descartada | `HARDWARE_AVAILABLE`, `LedStrip` y el `time` del módulo pasan a ser contrato con las pruebas (ver «Interfaces y contratos»). Hasta RF-13, importar `Animation` o `AnimationServer` en una prueba crea `animation_panel.log` en `panel/`, ignorado por git tras F1 (RG-7) | fácil |
| DA-14 | **Versión SemVer propia del panel (PQ-3).** La versión 1.0.0 nace en el primer commit de la fase de arreglos; los commits de la reorganización siguen con la excepción C2. Hay un único juego de versión y fecha, en dos sitios que sincroniza `tools/version.py`. El primero son dos constantes de módulo en `raspberry-panel/panel/LedMatrixAnimation.py`: `__version__ = "1.0.0"` y `__date__ = "AAAA-MM-DD"`. Viajan a la Pi con el código. El segundo es la línea `**Versión:** X.Y.Z · **Fecha:** AAAA-MM-DD` de `raspberry-panel/README.md`. El registro es `raspberry-panel/CHANGELOG.md`, con una entrada `## [X.Y.Z] - AAAA-MM-DD` por versión. `.agentes/version.json` lo crea el usuario. Las constantes no se registran en el log ni se usan en otro sitio | AC-8, AC-3 | La versión solo en el README y en el CHANGELOG: no llega a la Pi, porque allí solo se copia `panel/`, y en la Pi no se sabría qué versión corre | Cada commit de arreglos sube al menos PATCH y la fecha, con `py -3 tools/version.py --write` (proceso común, «Versión y fecha del producto»). El ESP32 se queda sin sitio en `version.json` (RG-15) | fácil |
| DA-15 | **Finales de línea LF (PQ-6).** En la fase de arreglos, en una tarea propia, se crea `.gitattributes` en la raíz con `*.sh text eol=lf` y `*.service text eol=lf`. Si F0-bis da `i/crlf`, en la misma tarea se ejecuta `git add --renormalize` de `apagado.sh` y de las dos unidades. La tarea está hecha cuando `git ls-files --eol` da `i/lf` en los tres archivos | AC-8, AC-1 | Solo la comprobación de LF en el README: la causa sigue y cada copia desde Windows puede volver a traer CRLF | Los tres archivos de la Pi salen siempre con LF, también `apagado.service`, que se escribe en Windows. No va en la reorganización, porque RF-4 solo admite renombrados en esas fases (RG-16) | fácil |

## Componentes

| ID | Componente | Responsabilidad | Depende de | Ubicación |
|---|---|---|---|---|
| C-1 | Principal | Punto de entrada: configura el log (DA-3), registra la excepción no capturada (DA-4), carga la configuración, prueba los paneles y recorre los archivos, omitiendo los que no cargan (DA-5) | C-2, C-3, C-4, C-5 | `raspberry-panel/panel/LedMatrixAnimation.py` |
| C-2 | Configuración | Lee `configuracion.json` de su propia carpeta (DA-10) | — | `raspberry-panel/panel/Config.py`, `configuracion.json` |
| C-3 | Geometría | Tabla píxel → LED y tamaños del panel. Solo cambia su logger (DA-3) | — | `raspberry-panel/panel/Panel.py` |
| C-4 | Animación | Carga una imagen y entrega frames RGB que caben en el panel, con sus duraciones; traduce los errores de carga (DA-5 a DA-7) | — | `raspberry-panel/panel/Animation.py` |
| C-5 | Salida | Pinta frames en la tira dentro de los límites del panel, prueba N paneles y muestra frames en el modo `DEBUG` (DA-8, DA-9) | C-3, C-4 | `raspberry-panel/panel/AnimationServer.py` |
| C-6 | Despliegue | Unidades systemd del panel y del apagado, dependencias de ejecución, versión del producto y su documentación (DA-11, DA-12, DA-14) | C-1 | `raspberry-panel/panel/panel.service`, `apagado.service`, `apagado.sh`, `requirements.txt`; `raspberry-panel/README.md`, `raspberry-panel/CHANGELOG.md` |
| C-7 | Pruebas | Caracterización C-1 a C-4 y una prueba por arreglo, sin hardware (DA-13) | C-1, C-2, C-3, C-4, C-5 | `raspberry-panel/tests/`, `raspberry-panel/requirements-dev.txt` |
| C-8 | Estructura del repositorio | Árbol de la opción A, `.gitignore`, `.gitattributes`, `archivo/` y los README de la raíz y de `archivo/` (DA-2, DA-15) | — | `.gitignore`, `.gitattributes`, `README.md`, `esp32/`, `raspberry-panel/`, `archivo/` |

Estructura resultante (DA-2):

```
raspberry-panel/
  panel/            ← se copia entera a /home/pi/panel
    LedMatrixAnimation.py  Config.py  Panel.py  Animation.py  AnimationServer.py
    configuracion.json  panel.service  apagado.service  apagado.sh  requirements.txt
  ficheros/         ← banner1..12.png e iconos; se copia el primer nivel a /home/pi/ficheros
  tests/            ← conftest.py y test_*.py (zona del Probador)
  requirements-dev.txt
  README.md  CHANGELOG.md
esp32/  archivo/  README.md  .gitignore  .gitattributes
```

## Interfaces y contratos

Lo que no puede cambiar sin que se diga:

- **`LedMatrixAnimation` y las pruebas:** la constante `LOGGING_CONFIG` (con el gestor `archivo` y su `filename`), `main()` con su `try/except/raise` y el uso de `time.sleep` a través del módulo `time` son contrato con las pruebas (DA-3, DA-4, DA-5).
- **Ejecución:** `python3 LedMatrixAnimation.py`, sin argumentos. Código de salida 0 en una parada normal (`KeyboardInterrupt`, `SystemExit`) y 1 con una excepción no capturada, que además sale por stderr y queda en el log (DA-4).
- **`Config(jsonfile)`:** una ruta relativa se busca en la carpeta de `Config.py`; una absoluta se usa tal cual (DA-10). Las claves de DE-1 no cambian.
- **`Animation(fichero, alto, ancho, velocidad)`:** firma sin cambios. Después de construirse:
  - `frames` es una lista no vacía de imágenes en modo `RGB`, cada una de como mucho `ancho` × `alto`.
  - `frame_durations` está en ms, uno por frame.
  - `is_animated` es True solo en un GIF de 2 frames o más.
  - Si no puede cargar, lanza `ImageLoadError` (subclase de `Exception`) con el mensaje `«<ruta>: <TipoOriginal>: <mensaje>»` y `__cause__` = la excepción original (DA-5).
- **`AnimationServer`:** no cambian las firmas de `testPanels`, `startAnimation` ni `startAnimationTest`. `startAnimation` no escribe ningún LED fuera de RN-8 (DA-8). Las pruebas dependen de tres cosas, que no se renombran sin avisar al Probador: la global de módulo `HARDWARE_AVAILABLE`, el atributo `LedStrip` (con `fill`, `__setitem__` y `show`) y el uso de `time.sleep` a través del módulo `time` (DA-13).
- **`Panel`:** firma, `matriz`, `ancho_total`, `altura_total` y `total_leds_panel` sin cambios. Logger `Panel`.
- **Log:** `animation_panel.log` junto a `LedMatrixAnimation.py`. Formato `%(asctime)s - %(name)s - %(levelname)s - %(message)s`, nivel INFO, un solo gestor de 26 214 400 B con 5 copias, en utf-8 (DA-3).
- **Hardware:** sin cambios. GPIO18, 864 LEDs, entero de color `0xRRGGBB` con `colourTuple` y NeoPixel sin `pixel_order` (RN-12).
- **systemd:**
  - `panel.service`: solo cambia `User=pi`. Se mantienen `ExecStartPre` de 4 s, `Restart=always` y `RestartSec=10` (RNF-5).
  - `apagado.service`: nuevo (DA-11).
- **Dependencias:** `requirements.txt` (ejecución, en `panel/`) y `requirements-dev.txt` (prueba) (DA-12).
- **Versión:** `__version__` y `__date__` en `LedMatrixAnimation.py` y la línea `**Versión:** … · **Fecha:** …` del README de `raspberry-panel/`. Solo las cambia `tools/version.py`, con las expresiones de `.agentes/version.json` (DA-14).

## Datos

No hay datos persistentes ni esquema: no interviene el Experto en bases de datos.

- `configuracion.json` mantiene sus claves y sus valores, incluido `directorio` = `/home/pi/ficheros` (RF-12). Su dueño es el propietario de la Pi.
- `animation_panel.log` es la única salida escrita. Su dueño es C-1, a través del gestor único. El log de diciembre de 2025 pasa a `archivo/raspberry-panel/` en F4 y sigue rastreado, como evidencia de RF-17.
- Las imágenes se leen y no se escriben.
- Migración: ninguna. En la Pi basta copiar la carpeta, instalar las unidades y hacer `daemon-reload` (RF-12).

## Errores, concurrencia y seguridad

- **Errores, por orden de detección:**
  1. Configuración que falta o está mal formada: la excepción sube hasta el punto de entrada y DA-4 la registra con su traza. Sale con código 1 y systemd relanza a los 10 s.
  2. Imagen que no carga: `ImageLoadError`. El bucle la registra con `logger.exception`, que deja la causa y la traza, y sigue con el siguiente archivo (DA-5).
  3. Vuelta sin ningún archivo reproducido: 1 ERROR con el directorio y si existe, y 10 s de espera (RN-5).
  4. Fallo de la tira o de `show()`: no se captura y llega a DA-4.
  5. `KeyboardInterrupt` y `SystemExit`: como hoy, se registra «Stopped» y el programa sale con 0. `startAnimation` y `testPanels` siguen tragándose `KeyboardInterrupt` por dentro; no se toca (RS-2).
- **Concurrencia:** ninguna. Un solo hilo y un solo proceso, con un único gestor de log que es dueño del archivo. Desaparecen los tres gestores que rotaban a la vez (Z-7).
- **Recursos:** un GIF animado se guarda frame a frame, ya ajustado al panel (DA-7, RG-14). Un PNG se decodifica entero, como hoy. Una imagen gigantesca la corta Pillow con `DecompressionBombError`, que DA-5 traduce y omite.
- **Seguridad:** no aplica como aplicación (análisis, «Seguridad»). No hay red, usuarios ni secretos. Las imágenes de `directorio` son la única entrada externa; se validan en la carga (DA-5 y DA-6) y en el pintado (DA-8). El apagado corre con `User=pi`, no con root. En Raspberry Pi OS, `pi` suele tener ya sudo sin contraseña para todo, así que el diseño no añade privilegios, pero tampoco los limita. Una línea de sudoers limitada a `shutdown` solo se usa si `pi` no tiene ya ese permiso (DA-11). El log solo lleva rutas de imágenes y valores de configuración; no hay secretos que registrar.

## Trazabilidad

| Requisito | Componentes |
|---|---|
| RF-1 | C-8 |
| RF-2 | C-8 |
| RF-3 | C-8 |
| RF-4 | C-8, C-1, C-2, C-3, C-4, C-5 |
| RF-5 | C-7, C-3, C-4, C-5 |
| RF-6 | C-3, C-1 |
| RF-7 | C-4, C-1 |
| RF-8 | C-4, C-5 |
| RF-9 | C-4, C-1 |
| RF-10 | C-4, C-7 |
| RF-11 | C-5 |
| RF-12 | C-2, C-6 |
| RF-13 | C-1, C-3, C-4, C-5 |
| RF-14 | C-6, C-7 |
| RF-15 | C-6 |
| RF-16 | C-8, C-6 |
| RF-17 | C-7, C-3, C-4, C-5 |
| RF-18 | C-1, C-2, C-4, C-5, C-7 |
| RF-19 | C-1 |

## Impacto en lo existente

**Zonas frágiles que se tocan:**

| Zona | Arreglo | Caracterización previa |
|---|---|---|
| Z-1 | DA-3 | C-1 |
| Z-2 | DA-6 | C-2 y comparación de `banner1..12` por LED (RF-10) |
| Z-3 y Z-4 | DA-7 y DA-8 | C-2 y C-4 |
| Z-5 | DA-9 | C-4 |
| Z-7 | DA-3 | — |
| Z-8 | DA-10 y DA-11 | — |
| Z-9 | DA-5 | — |
| Z-11 | DA-12 y DA-13 | — |
| Z-12 | DA-11 | — |

- Según «Cómo trabajar con este código», C-1 y C-4 van antes de tocar `Panel` o `startAnimation`, y C-3 antes de cualquier cambio cerca del color. RS-1 ya fija ese orden. Z-6 no se toca.
- **Compatibilidad:**
  - No cambia ninguna firma pública.
  - El tipo de excepción de `Animation` pasa a una subclase de `Exception`.
  - Cambia lo que se ve, con aceptación del usuario: la transparencia se compone sobre negro, un GIF grande se reduce, un GIF estático se ve y un GIF roto se descarta entero.
  - Cambia el log: aparecen las trazas de `Panel` y la línea de LEDs por panel lista N paneles.
  - El archivo de log se escribe en utf-8 (en la Pi ya lo era por la configuración regional).
- **Despliegue:**
  - Al copiar la nueva versión a la Pi, `panel.service` cambia de usuario y hay que hacer `daemon-reload`.
  - El servicio de apagado se instala desde el repositorio. Antes hay que comprobar que no existe ya el original (RG-12).
  - Las rutas `/home/pi/...` no cambian.
- **Reorganización:** la que está escrita en `doc/decisiones-arquitectura.md` (2026-11-14 y nota del 2026-11-15), recontada en F0-bis. La condición C1 (zonas) está cubierta por `escribe: ["**"]` de los dos programadores (RS-9); F0-bis lo reconfirma.
- **Grafo:** no existe `graphify-out/`; queda para F7, como dice el plan.

## Riesgos

| ID | Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|---|
| RG-1 | `dictConfig` desactiva por defecto los loggers que ya existen. Como los módulos se importan antes, sus trazas se perderían en silencio | alta | alto | `disable_existing_loggers: False` fijado en DA-3. Las pruebas de RF-6 y RF-13 aplican la constante real `LOGGING_CONFIG` con el archivo redirigido a `tmp_path` y comprueban que la línea de `Panel` está en el log y que hay un solo gestor |
| RG-2 | Los mensajes de `AnimationServer` al importarse (`:28`, `:33`) salen antes de configurar el log | media | bajo | El WARNING de la Pi sale por stderr gracias al gestor de último recurso de `logging` y llega al journal. `AnimationServer.__init__` ya deja en el log «Modo simulación - hardware no disponible». Se acepta perder el INFO de Windows |
| RG-3 | Alguna pancarta en modo `P` o `RGBA` cambia de aspecto con DA-6 | baja | medio | F0-bis registra el modo de cada banner. RF-10 compara por LED antes y después; si alguna difiere, se para y se pregunta |
| RG-4 | El Raspberry Pi OS de la Pi trae Python 3.10 o anterior, o la Pi y el PC acaban con Pillow de distinta línea mayor porque las dependencias no se fijan (PQ-2) | media | medio | Al desplegar se comprueban Python 3.11 o superior y las versiones de las librerías; si Python no llega, se para y se pregunta (RF-12, SP-4, PQ-1). Las pruebas de pancartas en la Pi las valida el usuario (UAT-17) |
| RG-5 | La línea de sudoers no coincide con la ruta que resuelve `sudo` (`/sbin/shutdown` o `/usr/sbin/shutdown` en Raspberry Pi OS con `/usr` unificado) y el apagado falla | baja | medio | En el caso habitual (`NOPASSWD: ALL`) no se toca sudoers (DA-11). Si hace falta la línea, se escribe con `visudo` y se comprueba con `sudo -l`, y luego se prueba el apagado en la Pi. Lo valida el usuario (UAT-15, RS-7) |
| RG-13 | `apagado.sh` y `panel.service` tienen finales CRLF en la copia de Windows. `apagado.sh` funciona por casualidad, porque los CR caen en comentarios, y `apagado.service` se escribirá en Windows | media | medio | F0-bis comprueba `git ls-files --eol` de esos archivos. DA-15 añade `.gitattributes` y renormaliza en la fase de arreglos, no en la de movimiento, por RF-4 (PQ-6). El README pide comprobar LF en la Pi |
| RG-14 | Un GIF grande y largo ocupa mucha memoria al decodificarse | baja | medio | DA-7 ajusta cada frame antes de guardarlo: la memoria queda acotada al tamaño del panel por frame |
| RG-6 | Un GIF estático que cabe se ve solo `velocidad` × `repeticiones` (250 ms con la configuración actual) y en UAT-7 parece que no sale | media | bajo | Es lo que dice SP-2 («se trata como un PNG») y lo confirmó el usuario el 2026-11-22 (PQ-4). UAT-7 lo comprueba con esa expectativa |
| RG-7 | Antes de RF-13, las pruebas de caracterización crean `animation_panel.log` en `raspberry-panel/panel/` al importar los módulos | alta | bajo | F1 ignora `*.log`. Tras DA-3, importar ya no crea el log |
| RG-8 | Un archivo roto en la carpeta deja una traza en cada vuelta y el log crece | media | bajo | Rotación a 25 MB con 5 copias (RN-7). Es lo que pide `python-logging` (`logger.exception`) |
| RG-9 | El Probador no puede escribir en `raspberry-panel/tests/` otros archivos que no sean `test_*.py` y `conftest.py` | alta | bajo | Los datos esperados (matriz de C-1, huellas de las pancartas) van dentro de los `test_*.py` (DA-13). Si hiciera falta un archivo de datos, se pide al usuario ampliar la zona |
| RG-10 | El panel no tiene versión ni CHANGELOG, y la regla de versión del proceso pide subir versión y fecha en cada commit. `.agentes/version.json` no existe y solo admite un producto | alta | medio | Resuelto con DA-14 (PQ-3). El primer commit de arreglos espera a que el usuario cree `.agentes/version.json` |
| RG-15 | `.agentes/version.json` solo admite un producto. Al ocuparlo el panel, la propuesta para el ESP32 (memoria, 2026-11-14, «Versión») ya no cabe | alta | medio | Hoy no se versiona el ESP32: en esta tanda solo se mueve. Cuando haga falta, el usuario decide si amplía `tools/version.py` a varios productos o si usa un segundo archivo. Queda anotado en la memoria de decisiones |
| RG-16 | `git add --renormalize` cambia los bytes de `apagado.sh` y `panel.service` (CRLF a LF) y el diff parece un cambio de contenido | media | bajo | DA-15 lo deja en su propia tarea de la fase de arreglos. La tarea está hecha cuando `git diff --ignore-cr-at-eol` no muestra cambios en esos archivos y `git ls-files --eol` da `i/lf` |
| RG-11 | Un cambio de nombre de `HARDWARE_AVAILABLE`, de `LedStrip` o del uso de `time` rompe las pruebas sin que cambie el comportamiento | baja | bajo | Están en «Interfaces y contratos» como contrato con las pruebas |
| RG-12 | En la Pi ya existe el servicio de apagado original con otro nombre y, al instalar el nuevo, hay dos | media | bajo | El README pide buscarlo antes (`systemctl list-unit-files`) y desactivar uno. Lo valida el usuario |

## Lo que no se decide aquí

- Nombres de las funciones privadas de DA-6 y DA-7 y de la constante de 10 s (`LOGGING_CONFIG` y su gestor `archivo` sí quedan fijados, porque son contrato con las pruebas), y el texto de los mensajes nuevos del log. Las líneas nuevas usan argumentos diferidos (`%s`); las existentes no se reescriben (RS-2).
- La forma exacta de componer sobre negro (`paste` con máscara o `alpha_composite`). Las dos cumplen RN-4.
- La organización interna de las pruebas: archivos, *fixtures* y cómo se guardan las huellas de las 12 pancartas (por ejemplo, un sha256 de la secuencia de valores por LED). Es del Probador, dentro de DA-13.
- El texto de los README y la línea exacta de sudoers (RG-5).
- El orden y el corte de las tareas: es del Faseador, con RS-1.

## Preguntas abiertas

Ninguna. Todas respondidas por el usuario el 2026-11-22:

| ID | Pregunta | Respuesta del usuario (2026-11-22) | Dónde se aplica |
|---|---|---|---|
| PQ-1 | ¿Mínimo Python 3.10 (fuera de soporte desde el 2026-10-01) o 3.11 en la Pi? | 3.11 o superior en la Pi, no 3.10. Al desplegar se comprueba que Raspberry Pi OS la trae | Plataformas y versiones, AC-6, AC-7, DA-12, RG-4 |
| PQ-2 | ¿Se acepta la excepción a `python-proyecto` (dos `requirements*.txt` sin bloquear, `requires-python` como comentario)? | Aceptada | DA-12 |
| PQ-3 | ¿Excepción de versión o SemVer propia del panel? | SemVer propia: `raspberry-panel/CHANGELOG.md` con 1.0.0 y `.agentes/version.json`, que crea el usuario | DA-14, RG-10, RG-15 |
| PQ-4 | ¿Un GIF estático o un PNG que cabe se ve `velocidad` × `repeticiones` (250 ms)? | Confirmado; se comprueba en UAT-7 | DA-7, RG-6 |
| PQ-5 | ¿Se acepta la excepción a `python-logging` (tamaño y copias en `LOGGING_CONFIG`)? | Aceptada | DA-3 |
| PQ-6 | ¿Se añade `.gitattributes` con `eol=lf` para `*.sh` y `*.service`? | Sí, y se renormaliza, en la fase de arreglos | DA-15, RG-13 |
| PQ-7 | ¿Se acepta la excepción a `python-basico` (`except Exception` traductor en `loadFile`)? | Aceptada | DA-5, RS-10 |

## Cambios

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-11-22 | Creación del documento en estado `borrador` | Encargo del Orquestador, modo diseñar |
| 2026-11-22 | Ronda 1 del Cuestionador (7 objeciones, 0 bloqueantes), aceptadas las 7. (1) `LOGGING_CONFIG` como constante de módulo y `try/except/raise` dentro de `main()`; contrato con las pruebas ampliado (DA-3, DA-4, Interfaces, RG-1). (2) Tamaño y copias en el diccionario, declarados como excepción (PQ-5). (3) Motivo de DA-5 corregido, nueva medida de AC-4 y excepción a `python-basico`. (4) PQ-2 ampliada a dependencias sin bloquear y a `requires-python`. (5) Orden de ajuste por frame en DA-7 (RG-14). (6) Sudoers según `sudo -l` y finales LF (DA-11, Seguridad, RG-5, RG-13, PQ-6). (7) Medida de AC-3 | Acta del Cuestionador técnico, ronda 1 |
| 2026-11-22 | Ronda 2: las 7 objeciones quedan cerradas. Se aplican los hallazgos finales sin ronda nueva: PQ-7 y la salvedad en RS-10 (8), «Recursos» coherente con DA-7 (9) y renormalización en PQ-6 (10). Estado a `cuestionado` | Acta del Cuestionador técnico, ronda 2 (final) |
| 2026-11-22 | Respuestas del usuario a PQ-1 a PQ-7 incorporadas: Python 3.11 o superior en la Pi y en las pruebas (sustituye a los «3.10 o superior» del análisis, RNF-6, RNF-8, RF-12 y RF-14). Nuevas DA-14 (versión SemVer del panel) y DA-15 (`.gitattributes`), y nuevos RG-15 y RG-16. Aprobación expresa del usuario («Aprobada»): estado a `aprobado`, sin ronda nueva del Cuestionador (cambio mínimo, decidido por el usuario) | Respuestas del usuario, vía Orquestador |

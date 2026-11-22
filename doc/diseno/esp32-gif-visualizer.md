# Diseño: Visualizador de GIFs para ESP32 (firmware PlatformIO)

- **Alcance analizado:** `platformio.ini`, `src/main.cpp`, `src/gif_player.h`, `src/gif_player.cpp`, `data/index.html`, `README.md`, `.gitignore`; consulta puntual de `.pio/libdeps/esp32dev/AnimatedGIF` para contrastar su API.
- **Commit analizado:** `e23949d` (instantánea inicial, 2026-11-14); el código leído el 2026-11-14 es el de ese commit.
- **Estado:** validado
- **Aprobación:** 2026-11-14, aprobado por el usuario tras dos rondas con el Cuestionador técnico (0 objeciones abiertas)
- **Última sesión:** 2026-11-14

Índice y diagnóstico del repositorio: [indice.md](indice.md). El otro sistema: [panel-raspberry.md](panel-raspberry.md).

## Finalidad

- Firmware para ESP32 (`esp32dev`) que sirve una web de configuración y reproduce GIFs animados en un panel WS2812 (uno o varios paneles encadenados). `leído`: `README.md:4-15`, `src/main.cpp:1-9`.
- Gobierna además un relé por horario diario con hora NTP. `leído`: `src/main.cpp:83-88`, `src/main.cpp:123-138`, `src/main.cpp:507-515`. El relé corta y da la alimentación de la tira o panel LED (`confirmado`, P-6, 2026-11-14): cubre la misma necesidad que `apagado.sh` en la Pi, no tener el panel encendido todo el rato (`deducido` de P-6 y P-9).
- Iba a sustituir a la Raspberry Pi (`confirmado`, P-7, 2026-11-14). El usuario duda de que el ESP32 tenga potencia y capacidad para hacer lo mismo: es una duda abierta para el análisis y el diseño futuros, no se resuelve aquí. Hechos medidos en [indice.md](indice.md#dudas-abiertas-para-el-análisis).
- Lo usa una persona desde el navegador (red local o AP del ESP32): red, horario, geometría del panel y gestión de GIFs. `leído`: `data/index.html:30-36`.
- El código actual compila. `observado`: `pio run -e esp32dev` (2026-11-14) termina en SUCCESS.
- Fue una prueba que el usuario abandonó; el producto sigue vivo. `confirmado`: P-1, 2026-11-14.
- Si llegó a grabarse y a funcionar: desconocido; el usuario no lo sabe (P-1, P-4). Por el código, la reproducción no puede funcionar tal como está (F-13, `deducido`, Z-1 a Z-5). Antes de la compilación del 2026-11-14 no había artefactos en `.pio/build/` (solo `libdeps`). Lo confirmaría grabarlo y observar C-5 en placa.
- Requisitos expresados por el usuario para el futuro análisis (no son comportamiento actual): tamaño del panel y pin de datos configurables (RU-1 y RU-2 de [indice.md](indice.md)). El código actual ya los guarda desde la web (`led.panelWidth`, `led.panelHeight`, `led.pin`; `leído`, `src/main.cpp:181-214`), sin observar en placa.
- No comparte código con el visualizador Python de la Raspberry Pi. `deducido`: nada en `src/` ni `data/` referencia `panel/`, `ficheros/` ni `navidad/`.

## Contexto y límites

| Entra / sale | Qué | Dónde |
|---|---|---|
| Entra | HTTP en el puerto 80 (UI y API JSON) | `src/main.cpp:21`, `src/main.cpp:483-497` |
| Entra | GIF subidos por multipart/form-data | `src/main.cpp:345-371` |
| Entra | Hora NTP (opcional) | `src/main.cpp:93-104` |
| Sale | Datos WS2812 (800 kHz, GRB) en el GPIO configurado | `src/gif_player.cpp:47` |
| Sale | HIGH/LOW en el GPIO del relé, que alimenta la tira o panel LED (P-6) | `src/main.cpp:83-88` |
| Sale | Trazas serie a 115200 | `platformio.ini:15`, `src/main.cpp:465` |
| Persistencia | NVS, espacio `config`, clave `cfg`, JSON | `src/main.cpp:24`, `src/main.cpp:146`, `src/main.cpp:211` |
| Persistencia | SPIFFS: `/index.html` y `/gifs/*.gif` | `src/main.cpp:251`, `src/main.cpp:341-343` |
| Externo | Bootstrap 5.3.2 desde `cdn.jsdelivr.net` | `data/index.html:7`, `data/index.html:270` |

## Módulos

| ID | Módulo | Ruta | Responsabilidad | Certeza | Cobertura |
|---|---|---|---|---|---|
| M-1 | Configuración y red | `src/main.cpp:31-247` | `Config`, carga y guarda en NVS, AP o STA, IP estática, mDNS | leído | entendido |
| M-2 | API HTTP | `src/main.cpp:249-497` | Endpoints de configuración, NTP y GIFs; sirve la UI | leído | entendido |
| M-3 | Horario, relé y NTP | `src/main.cpp:83-138`, `src/main.cpp:503-525` | Sincroniza la hora y decide el relé cada segundo | leído | entendido |
| M-4 | Reproductor `GifPlayer` | `src/gif_player.h`, `src/gif_player.cpp` | Decodifica con AnimatedGIF y pinta en NeoPixel con mapeo XY | leído | entendido |
| M-5 | Interfaz web | `data/index.html` | Formularios por pestañas, vista previa del orden de LEDs, gestión de GIFs | leído | entendido |
| M-6 | Build | `platformio.ini` | `espressif32`, `esp32dev`, Arduino, 3 librerías; compila (ver «Cómo trabajar») | observado | entendido |

## Funcionalidades

| ID | Funcionalidad (comportamiento observable) | Dónde | Certeza | Evidencia |
|---|---|---|---|---|
| F-1 | Guarda la configuración como un JSON en NVS y la recupera al arrancar | `src/main.cpp:143-214` | leído | `prefs.putString("cfg", out)` en `src/main.cpp:211` |
| F-2 | Modo AP con el SSID configurado; abierto si la contraseña tiene menos de 8 caracteres | `src/main.cpp:224-228` | leído | `src/main.cpp:226-227` |
| F-3 | Modo STA con espera máxima de 15 s; IP estática opcional | `src/main.cpp:229-241` | leído | `src/main.cpp:237` |
| F-4 | mDNS opcional | `src/main.cpp:242-245` | leído | `src/main.cpp:243` |
| F-5 | GET `/api/config`: configuración, versión 0.3, si hay hora y la hora actual | `src/main.cpp:260-294` | leído | `src/main.cpp:263`, `src/main.cpp:289-290` |
| F-6 | POST `/api/config` guarda y reaplica la red | `src/main.cpp:296-336` | leído | `src/main.cpp:332-334` |
| F-7 | POST `/api/ntp_sync` reconfigura NTP, espera 2 s y responde hora o 500 | `src/main.cpp:452-459` | leído | `src/main.cpp:456` |
| F-8 | Relé encendido en la franja `[inicio, fin)`, también si cruza medianoche | `src/main.cpp:123-138` | leído | `src/main.cpp:133-137` |
| F-9 | Reintento NTP cada 60 s mientras no haya hora | `src/main.cpp:517-524` | leído | `src/main.cpp:519` |
| F-10 | Subida de GIF a `/gifs/<nombre>` | `src/main.cpp:345-371` | leído | `src/main.cpp:350` |
| F-11 | Lista de GIFs (`GET /api/gifs`) | `src/main.cpp:373-389` | leído | `src/main.cpp:379-386` |
| F-12 | Reproducir (bucle por defecto) y detener | `src/main.cpp:391-425` | leído | `src/main.cpp:399` |
| F-13 | Reproducción del GIF en el panel | `src/gif_player.cpp:54-167` | deducido | Por el código y la API de la librería no puede funcionar tal como está (Z-1 a Z-5); sin observar en placa. Compila (observado), así que los defectos serían de ejecución. Además, el panel solo tiene alimentación dentro del horario (R-13) |
| F-14 | Toda ruta desconocida devuelve `index.html` | `src/main.cpp:249-258` | leído | `src/main.cpp:251-255` |
| F-15 | Vista previa web del orden de LEDs | `data/index.html:503-573` | leído | `data/index.html:531-556` |
| F-16 | Botón «Delete» sin efecto | `data/index.html:466-475` | deducido | Llama a `DELETE /gifs/<nombre>`, que el firmware no registra (`src/main.cpp:439-447`) |

## Flujos

**Arranque** (`src/main.cpp:464-501`): serie → GPIO 2 a LOW → SPIFFS (formatea si falla) → `loadConfig()` → `applyNetworkConfig()` → NTP (dos veces: `src/main.cpp:246` y `src/main.cpp:481`) → rutas → `server.begin()`.

**Bucle** (`src/main.cpp:503-525`): HTTP → un frame de GIF → cada 1000 ms horario y relé → reintento NTP cada 60 s.

**Reproducir un GIF** (`src/main.cpp:391-419`, `src/gif_player.cpp:39-167`): POST play → `setPanelConfig` + `begin` (recrea NeoPixel) → `playGif` lee el archivo entero a RAM, cierra el archivo, `open(buffer, size)`, `free(buffer)` → en cada `loop()`, `playFrame(false)` → la librería llama a `GIFDrawCallback` una vez por línea → `xyToIndex` y `strip.show()`. Que se vea algo depende además de que el relé alimente el panel: solo dentro de la franja del horario activado y con hora válida (R-13, `deducido`).

**Guardar** (`data/index.html:357-406` → `src/main.cpp:296-336`): los tres botones «Guardar» envían todo el formulario → NVS → reaplica red → `{"result":"ok"}`.

## Datos y estado

- `Config` global (`src/main.cpp:33-51`), dueño `main.cpp`; la escriben `loadConfig()` y `handlePostConfig()`.
- JSON en NVS (`src/main.cpp:181-214`): `apMode`, `sta_ssid`, `sta_password`, `useStaticIP`, `staticIP`, `gateway`, `subnet`, `mdnsEnabled`, `mdnsName`, `ntpEnabled`, `ntpServer`, `timezoneOffsetMinutes`, `schedule{enabled,start,end}`, `relayPin`, `led{pin,panelWidth,panelHeight,chainX,chainY,firstCorner,serpentine}`. Búfer de 2048 bytes.
- `LedPanelCfg` (`src/gif_player.h:17-25`) sin valores por defecto: en el global queda a cero (pin 0, tamaño 0). `deducido`. Los valores visibles (pin 4, 8×8, TL, serpentina) solo los pone la web (`data/index.html:335-341`).
- Estado del reproductor (`src/gif_player.h:60-73`) con puntero estático `instance` para el callback C.
- La contraseña Wi-Fi se guarda en claro y la API la devuelve (Z-9).

## Contratos externos

- API HTTP (`README.md:36-44`): `GET/POST /api/config`, `POST /api/ntp_sync`, `POST /api/gifs/upload` (campo `file`), `GET /api/gifs` → `{"gifs":[...]}`, `POST /api/gifs/play` `{"name","loop"}`, `POST /api/gifs/stop`, `GET /gifs/<archivo>`.
- `GET /gifs/<archivo>` se registra con `"^/gifs/.*"` (`src/main.cpp:446`). En el `WebServer` de arduino-esp32 una cadena se compara literalmente; las regex piden `UriRegex`. `supuesto`: si es así, la ruta nunca coincide y devuelve `index.html`. Lo confirma C-2.
- Pines: relé GPIO 2 por defecto (`src/main.cpp:27-29`), activo por HIGH (`src/main.cpp:86`); panel en el GPIO configurado, la web propone el 4. El relé conmuta la alimentación de la tira o panel LED (`confirmado`, P-6, 2026-11-14). Qué módulo de relé, en qué pin y con qué polaridad: el usuario no lo ha dicho (P-6). Queda `supuesto` que es el GPIO 2 activo por HIGH, como en el código; lo confirmaría mirar el cableado o C-6 en placa.
- Hardware del panel (`confirmado`, P-4, 2026-11-14): tira WS2812 continua, hecha a mano en serpentina. El usuario tiene un panel de 24×18 y otros de 32×32. Con el código actual, un panel así se describiría con `chainX` = `chainY` = 1 y `serpentine` = true (`deducido` de `src/gif_player.cpp:169-199`); la esquina de inicio de cada panel no se conoce.
- `firstCorner`: TL, TR, BL, BR (`src/gif_player.cpp:177-178`).
- Librerías declaradas: ArduinoJson ^6.21.0, Adafruit NeoPixel ^1.11.1, AnimatedGIF 1.4.7 (`platformio.ini:18-21`). Resueltas en la compilación del 2026-11-14 (`observado`): ArduinoJson 6.21.6, Adafruit NeoPixel 1.15.5, AnimatedGIF 1.4.7; plataforma Espressif 32 6.13.0 con `framework-arduinoespressif32` 3.20017.241212 (arduino-esp32 2.0.17), toolchain xtensa-esp32 8.4.0. Con los rangos `^`, otra máquina puede resolver otras versiones menores.

## Reglas implícitas

| ID | Regla | Dónde | Certeza | Evidencia |
|---|---|---|---|---|
| R-1 | Hora sincronizada si el año es mayor que 2016 | `src/main.cpp:109` | leído | `tm_year + 1900 > 2016` |
| R-2 | Franja `[inicio, fin)`; inicio > fin cruza medianoche; inicio = fin nunca enciende | `src/main.cpp:133-137` | leído | Comparaciones `>=` y `<` |
| R-3 | El relé solo se escribe cuando cambia el estado deseado. Con horario desactivado o sin hora, el estado deseado es «apagado», igual que el inicial (`relayState = false`), así que `setRelay` nunca se llama. Si `relayPin` es el 2 (valor por defecto, `src/main.cpp:49`), `setup()` lo pone como salida a LOW (R-7); si es otro, no llega a ponerse como salida (corregido el 2026-11-14: antes decía «se fuerza a apagado cada segundo») | `src/main.cpp:56`, `src/main.cpp:124-126`, `src/main.cpp:510-514` | leído | `if (shouldBeOn != relayState)` |
| R-4 | Zona horaria fija en minutos, sin horario de verano | `src/main.cpp:99-102` | leído | `configTime(offsetSeconds, 0, ...)` |
| R-5 | AP abierto si la contraseña tiene menos de 8 caracteres | `src/main.cpp:226-227` | leído | `length() >= 8` |
| R-6 | En POST, los booleanos ausentes se guardan como false; el resto conserva su valor | `src/main.cpp:303-313` | leído | `.as<bool>()` frente a valor por defecto |
| R-7 | Al arrancar se pone a LOW el GPIO 2, no el pin de relé configurado | `src/main.cpp:469-470`, `src/main.cpp:85` | leído | `RELAY_PIN` frente a `config.relayPin` |
| R-8 | Paneles numerados por filas (`prow * chainX + pcol`), cada uno con su esquina y serpentina | `src/gif_player.cpp:169-199` | leído | `src/gif_player.cpp:195` |
| R-9 | Frames sin respetar el retardo del GIF | `src/gif_player.cpp:107` | leído | `playFrame(false, NULL)` |
| R-10 | Subir con el mismo nombre sobrescribe | `src/main.cpp:352` | leído | `SPIFFS.remove(path)` |
| R-11 | Sin hora válida el relé queda apagado. La única fuente de hora es NTP: con `ntpEnabled` = false, o en modo AP (sin salida a Internet), la tira no recibe alimentación nunca aunque el horario esté activado | `src/main.cpp:95-98`, `src/main.cpp:126`, `src/main.cpp:246`, `src/main.cpp:481`, `src/main.cpp:518-523` | deducido | Leído: `if (!getLocalTime(&timeinfo)) return false` y ningún endpoint fija la hora a mano; en AP, `setupNTP()` se salta al arrancar pero el bucle lo reintenta cada 60 s. Que en AP no llegue a sincronizar se deduce de que el AP no tiene ruta a Internet |
| R-12 | El relé es activo por HIGH (HIGH = alimentación del panel encendida) | `src/main.cpp:86` | leído | `on ? HIGH : LOW`. Si el módulo de relé real es activo por LOW, la lógica se invierte (Z-15) |
| R-13 | El panel solo recibe alimentación si a la vez el horario está activado, hay hora válida (STA con NTP, R-11) y se está dentro de la franja. Con el horario desactivado, que es el valor por defecto, y un relé activo por HIGH, el panel no se alimenta nunca y ningún GIF puede verse, aunque se corrigieran Z-1 a Z-5; con un relé activo por LOW, se alimenta siempre. Esto vale si `relayPin` es el 2 (por defecto, el único que `setup()` pone a LOW); con otro pin, la salida queda sin inicializar y depende del módulo (Z-15) | `src/main.cpp:31`, `src/main.cpp:124`, `src/main.cpp:510-514` | deducido | Leído: `ScheduleEntry.enabled = false`, `if (!config.schedule.enabled) return false` y `setRelay` solo al cambiar el estado; la consecuencia sobre el panel se deduce de P-6 y R-12 |

## Decisiones deducidas

| ID | Qué parece decidido | Porqué probable | Certeza |
|---|---|---|---|
| D-1 | `WebServer` síncrono en lugar de asíncrono | Sin dependencias extra | supuesto |
| D-2 | Configuración como un único JSON en NVS | Simplicidad | deducido |
| D-3 | GIF cargado entero en RAM | Evitar los callbacks de lectura de AnimatedGIF | supuesto |
| D-4 | Código generado o reescrito por un asistente en varias iteraciones | Comentarios «ensure build compiles» (`src/gif_player.cpp:41-42`) y «¿Siguientes pasos que puedo hacer por ti?» (`README.md:55`) | deducido |

## Zonas frágiles

| ID | Zona | Riesgo | Dónde |
|---|---|---|---|
| Z-1 | Paleta RGB565 leída como RGB888 | Error aparente: `pPalette` es `uint16_t*` por defecto (`AnimatedGIF.h:107`, `AnimatedGIF.h:172`); colores incorrectos. Compila porque `uint32_t rgb = pDraw->pPalette[idx]` ensancha el `uint16_t` sin aviso (`src/gif_player.cpp:150`, observado en `pio run`) | `src/gif_player.cpp:23`, `src/gif_player.cpp:149-152` |
| Z-2 | Callback recorre el frame entero | Error aparente: la librería llama una vez por línea (`AnimatedGIF.h:103`); lectura fuera del búfer y `show()` por línea | `src/gif_player.cpp:145-166` |
| Z-3 | Resultado de `open()` al revés | Error aparente: devuelve 1 si va bien (`gif.inl:245`) | `src/gif_player.cpp:78`, `src/gif_player.cpp:124` |
| Z-4 | `size()` tras `close()` y búfer liberado en uso | Error aparente: la librería guarda el puntero (`AnimatedGIF.cpp:37-38`) | `src/gif_player.cpp:75-83` |
| Z-5 | Bucle sobre archivo cerrado; fin solo con `r < 0` | Error aparente | `src/gif_player.cpp:108-129` |
| Z-6 | Primer arranque sin configuración | No abre AP: inaccesible salvo por serie | `src/main.cpp:34-35`, `src/main.cpp:229-241` |
| Z-7 | POST config reaplica la red antes de responder | La respuesta puede perderse | `src/main.cpp:332-334` |
| Z-8 | Subida de archivos | Sin autenticación, límite ni saneado de nombre; respuesta enviada dos veces | `src/main.cpp:345-371`, `src/main.cpp:441-442` |
| Z-9 | Secretos | La API devuelve la contraseña Wi-Fi; ningún endpoint autenticado | `src/main.cpp:266`, `data/index.html:310` |
| Z-10 | UI depende de Internet | Bootstrap por CDN: en AP las pestañas no funcionan | `data/index.html:7`, `data/index.html:270` |
| Z-11 | Campos web sin efecto | «Pin del relé — referencia» no se guarda; «Delete» sin endpoint | `data/index.html:203`, `data/index.html:466-475` |
| Z-12 | Bloqueos del bucle | `delay(2000)` en NTP y hasta 15 s al reconectar | `src/main.cpp:456`, `src/main.cpp:237` |
| Z-13 | Pin 0 y tamaño 0 sin configurar | GPIO 0 es pin de arranque | `src/gif_player.h:17-25` |
| Z-14 | Sin pruebas | No hay `test/` ni entorno `native` | `platformio.ini:11-21` |
| Z-15 | Relé que alimenta el panel (P-6) | Hardware: pin y polaridad reales desconocidos. Si el pin configurado no es el GPIO 2, al arrancar se pone a LOW el GPIO 2 (R-7) y el pin real queda sin inicializar hasta el primer cambio de horario (R-3): su nivel en ese tiempo depende del módulo. Con un módulo activo por LOW, la tira estaría alimentada fuera del horario (R-12). En modo AP con horario, nunca se alimenta (R-11). Con el horario desactivado (valor por defecto) y relé activo por HIGH, tampoco (R-13) | `src/main.cpp:27-29`, `src/main.cpp:56`, `src/main.cpp:83-88`, `src/main.cpp:469-470`, `src/main.cpp:510-514` |
| Z-16 | `getLocalTime` sin hora válida | Bloqueo posible del bucle (web y reproducción): `getLocalTime` de arduino-esp32 espera hasta 5 s por omisión si no hay hora. Se llama en la comprobación del horario (cada segundo, si está activado) y en `isTimeSynced()` en cada vuelta del bucle con NTP activado y sin sincronizar; `GET /api/config` lo llama dos veces (`isTimeSynced()` y `currentTimeString()`), hasta unos 10 s por petición si el supuesto se confirma. `supuesto`: lo confirma leer `esp32-hal-time.c` del framework 2.0.17 o medir el tiempo del bucle en placa sin NTP | `src/main.cpp:108`, `src/main.cpp:126`, `src/main.cpp:508-510`, `src/main.cpp:518`, `src/main.cpp:289-290` |

## Preguntas abiertas

| ID | Pregunta | Por qué importa | Bloquea | Respuesta |
|---|---|---|---|---|
| P-4 | ¿Se compiló y grabó alguna vez? ¿Funcionó la reproducción? ¿Qué hardware: tamaño del panel, GPIO de datos, relé (pin y si es activo por HIGH o LOW)? | El código indica que la reproducción no puede funcionar | F-13, M-4 | 2026-11-14: Fue una prueba abandonada; no sabe si llegó a funcionar (P-1). El panel es una tira WS2812 continua en serpentina hecha a mano; tiene un panel de 24×18 y otros de 32×32. El tamaño del panel y el pin de datos deben ser configurables (requisitos RU-1 y RU-2, no comportamiento actual). Del relé no dijo nada: desconocido (pasa a P-6). |
| P-6 | ¿Para qué sirve el relé y el horario? ¿Qué relé hay, en qué pin y si es activo por HIGH o LOW? (lo del relé quedó sin respuesta en P-4) | Da sentido a R-3 y R-7 | M-3 | 2026-11-14: El pin que se enciende y se apaga es el que controla la tira o panel LED (su alimentación). No dio pin ni nivel activo: desconocido, queda `supuesto` GPIO 2 activo por HIGH (Contratos externos, Z-15, C-6) |
| P-7 | ¿El ESP32 iba a sustituir a la Raspberry Pi o es independiente? | Decide si los proyectos deben converger | M-4, M-5 | 2026-11-14: Sí, la idea era que el ESP32 sustituyera a la Raspberry Pi, pero el usuario no tiene claro que tenga potencia de proceso y capacidad para hacer lo mismo. Duda de viabilidad abierta para el análisis y el diseño futuros (V-1 de [indice.md](indice.md)); no bloquea la descripción del código |

P-1, P-2, P-3 y P-5 son comunes y están en [indice.md](indice.md) (respondidas el 2026-11-14).

## Pruebas de caracterización

| ID | Comportamiento que fija | Zona | Cómo | Estado |
|---|---|---|---|---|
| C-1 | Tabla `xyToIndex` para TL/TR/BL/BR, con y sin serpentina, 1×1 y 2×1, frente a la vista previa web | Z-2 | Unitaria en entorno `native` o comparación de salidas | propuesta |
| C-2 | Contrato HTTP: campos de `/api/config`, errores de `play`, `GET /gifs/<archivo>` | Z-8 | API contra la placa | propuesta |
| C-3 | `isNowInSchedule` con franja normal, que cruza medianoche y con inicio = fin | Z-12 | Unitaria `native` | propuesta |
| C-4 | Arranque con NVS vacía | Z-6 | Placa | propuesta |
| C-5 | GIF de colores puros en el panel | Z-1 | Placa, observación manual | propuesta |
| C-6 | Nivel del pin del relé y estado de la alimentación del panel: al arrancar, con horario desactivado, dentro y fuera de la franja, y en modo AP | Z-15 | Placa, polímetro u observación del panel | propuesta |

## Cómo trabajar con este código

- Compilar y grabar (`leído` en `README.md:27-33`, sin observar): `platformio run --target uploadfs`, `platformio run --target upload`, `platformio device monitor`. Grabar siempre se pregunta.
- Comprobar que compila: `pio run -e esp32dev` (`observado` el 2026-11-14): SUCCESS en 31 s; escribe en `.pio/build/esp32dev/` (`bootloader.bin`, `partitions.bin`, `firmware.bin`). Uso: RAM 14,9 % (48 728 de 327 680 B) y flash 67,9 % (890 553 de 1 310 720 B, partición de aplicación por defecto). En la salida no detallada no aparece ningún aviso de `src/gif_player.cpp` ni de `src/main.cpp`; `build_flags` solo define `CORE_DEBUG_LEVEL=0`, así que la ausencia de avisos no prueba que el código esté bien.
- Avisos del entorno al compilar (`observado`): «Obsolete PIO Core v6.1.19 is used (previous was 6.2.0)», es decir, hay varias instalaciones de PlatformIO Core; la orden reinstaló `tool-scons` 4.40801.0 en la instalación de PlatformIO del usuario.
- Versión en tres sitios sin sincronizar: `src/main.cpp:25`, `README.md:2`, `data/index.html:23`.
- No tocar `GifPlayer` ni el flujo de red sin C-1, C-4 y C-5.
- El README está envuelto en un bloque de código (`README.md:1`, `README.md:60`).

## Sesiones

| Fecha | Analizado | Queda pendiente |
|---|---|---|
| 2026-11-14 | Explorar: `src/`, `data/`, `platformio.ini`, README; contraste con AnimatedGIF 1.4.7 | Respuestas P-1 a P-7; compilar para pasar F-13 y la ruta `/gifs/` a observado |
| 2026-11-14 | Profundizar con órdenes autorizadas: instantánea git `e23949d`; `pio run -e esp32dev` (compila); versiones resueltas de librerías y plataforma | Respuestas P-1 a P-7. F-13, Z-1 a Z-5 y la ruta `/gifs/` (C-2) solo se pueden observar en placa: grabar es otra orden que hay que autorizar |
| 2026-11-14 | Incorporar respuestas P-1 y P-4: prueba abandonada sin saber si funcionó; hardware del panel confirmado; requisitos RU-1 y RU-2 anotados | P-6 (relé y horario, ampliada con lo del relé que P-4 no respondió) y P-7. F-13, Z-1 a Z-5 y C-2 solo en placa |
| 2026-11-14 | Incorporar respuestas P-6 y P-7: el relé alimenta el panel; el ESP32 iba a sustituir a la Pi (duda de viabilidad V-1 al índice, sin resolver). Relectura del relé: R-3 corregida, nuevos R-11, R-12, Z-15, Z-16 y C-6. 6 de 6 módulos entendidos. Propuesto `validado`, con el Cuestionador | Aprobación del usuario; pin y polaridad del relé (supuesto), Z-16 (supuesto), D-1 y D-3 (supuestos); F-13, Z-1 a Z-5, C-2 y C-6 solo en placa |
| 2026-11-14 | Cuestionamiento en dos rondas: R-13 nueva, R-3 y Z-16 matizadas; acta con 0 objeciones abiertas. Propuesto `validado` | Aprobación del usuario; pin y polaridad del relé, Z-16, D-1 y D-3 (supuestos); F-13, Z-1 a Z-5, C-2 y C-6 solo en placa |
| 2026-11-14 | Aprobación del usuario: documento `validado` | Pin y polaridad del relé, Z-16, D-1 y D-3 (supuestos); F-13, Z-1 a Z-5, C-2 y C-6 solo en placa |

## Cambios

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-11-14 | Creación del documento | Encargo del Orquestador, modo explorar |
| 2026-11-14 | Commit analizado `e23949d`; compilación observada; versiones resueltas; matiz en Z-1 y F-13 | Encargo del Orquestador, modo profundizar (órdenes autorizadas) |
| 2026-11-14 | Finalidad y contratos actualizados con P-1 y P-4; P-4 respondida; P-6 ampliada con el relé | Encargo del Orquestador, modo incorporar respuestas |
| 2026-11-14 | P-6 y P-7 respondidas; finalidad y contratos con el relé de alimentación y la sustitución de la Pi. **R-3 corregida**: decía que el relé se fuerza a apagado cada segundo, pero solo se escribe al cambiar (`src/main.cpp:511`). Nuevos R-11, R-12, Z-15, Z-16 y C-6 | Encargo del Orquestador, modo incorporar respuestas; relectura de `src/main.cpp:56-126`, `src/main.cpp:220-247`, `src/main.cpp:464-525` |
| 2026-11-14 | Nueva R-13 (sin horario activado el panel no se alimenta), citada en el flujo «Reproducir un GIF», F-13 y Z-15; R-3 matizada (pin 2 por defecto sí se pone como salida); Z-16 incluye `GET /api/config` | Acta del Cuestionador técnico, objeción 3; comprobado en `src/main.cpp:31`, `:49`, `:124`, `:289-290`, `:510-514` |
| 2026-11-14 | R-13 limitada a `relayPin` = 2; con otro pin remite a Z-15 | Acta del Cuestionador técnico, ronda 2, menor 5 |
| 2026-11-14 | Estado `en curso` → `validado` | Aprobación expresa del usuario («sí, aprobados»), transmitida por el Orquestador, modo actualizar |

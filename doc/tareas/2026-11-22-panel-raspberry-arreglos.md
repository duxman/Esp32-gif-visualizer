# Tareas: Panel Raspberry Pi, reorganización y arreglos

- **Análisis de origen:** `doc/analisis/2026-11-22-panel-raspberry-arreglos.md` (arquitectura: `doc/arquitectura/2026-11-22-panel-raspberry-arreglos.md`)
- **Estado del documento:** aprobado
- **Creado:** 2026-11-22
- **Cuestionamiento:** pendiente (el acta se copia a `doc/decisiones-arquitectura.md` al aprobarse)

## Resumen

Se reorganiza el repositorio (opción A ya autorizada, sobre la línea base `f25ee46`), se fijan con pruebas sin hardware los comportamientos del panel de la Raspberry Pi y después se arreglan los defectos Z-1, Z-2, Z-3, Z-4, Z-5, Z-7, Z-8, Z-9, Z-11 y Z-12, el modo de PC (RF-18) y la excepción no capturada (RF-19). Se deja el despliegue reproducible y la documentación al día. Solo se arregla: sin funcionalidad nueva, y lo más simple que funcione (cada arreglo vive en el módulo que ya tiene esa responsabilidad).

## Alcance

**Incluye:** reorganización del repositorio (RF-1 a RF-4), pruebas de caracterización (RF-5), los arreglos RF-6 a RF-15, RF-18 y RF-19, la documentación vigente (RF-16) y la comprobación de que no hay regresión (RF-17).
**No incluye:** funcionalidad nueva, RU-3, Z-6, Z-10, Z-13; corregir el firmware ESP32 (solo se mueve); instalar o probar nada en la Pi desde el repositorio (lo hace el usuario); cambiar `directorio`, las rutas `/home/pi/...` ni las 5 horas de `apagado.sh`; recuperar lo que solo existía en `e23949d`; el cierre en la memoria de decisiones y la actualización del grafo, que son del cierre de fase del Orquestador.

## Requisitos

| ID | Requisito | Origen en el análisis |
|---|---|---|
| RF-1 | El código vigente de la Pi vive en `raspberry-panel/panel/` y las imágenes originales en `raspberry-panel/ficheros/`; los `.pyc` dejan de rastrearse | §Requisitos funcionales RF-1 |
| RF-2 | Una sola carpeta de imágenes: se eliminan las copias idénticas por sha256 | RF-2 |
| RF-3 | Lo que no tiene copia se archiva en `archivo/` sin borrarse, con `archivo/README.md` | RF-3 |
| RF-4 | La reorganización no cambia ningún comportamiento; el firmware ESP32 pasa a `esp32/` | RF-4 |
| RF-5 | Pruebas automáticas sin hardware que fijan el comportamiento actual (C-1 a C-4) antes de corregir nada | RF-5 |
| RF-6 | Las trazas de `Panel` llegan al log de la aplicación (Z-1) | RF-6 |
| RF-7 | Un `.gif` no animado que cabe en el panel se muestra como imagen estática (Z-3) | RF-7 |
| RF-8 | Ningún píxel se pinta fuera de su sitio y un GIF mayor que el panel se reduce hasta caber (Z-4) | RF-8 |
| RF-9 | Un archivo que no se puede cargar deja su causa en el log y se omite (Z-9) | RF-9 |
| RF-10 | Toda imagen se reproduce en RGB, con la transparencia compuesta sobre negro (Z-2) | RF-10 |
| RF-11 | La prueba de paneles y el contador de LEDs admiten cualquier número de paneles (Z-5) | RF-11 |
| RF-12 | Despliegue reproducible: configuración de la carpeta del código, `User=pi` y documentación de instalación (Z-8) | RF-12 |
| RF-13 | Un único registro de log con rotación (Z-7), con la excepción a la práctica de logging escrita | RF-13 |
| RF-14 | Dependencias de ejecución y de prueba declaradas por separado (Z-11) | RF-14 |
| RF-15 | El servicio que ejecuta `apagado.sh` figura en el repositorio (Z-12) | RF-15 |
| RF-16 | La documentación vigente refleja el nuevo estado | RF-16 |
| RF-17 | Sin regresión: colores, tiempos, mapeo de LEDs y orden de reproducción no cambian | RF-17 |
| RF-18 | El modo simulación y el modo `DEBUG` = 1 siguen funcionando en PC (Windows) | RF-18 |
| RF-19 | Toda excepción no capturada se registra con su traza antes de terminar el proceso | RF-19 |

## Decisiones técnicas

| ID | Decisión | Alternativa descartada y por qué |
|---|---|---|
| DT-1 | Arreglos dentro de los 5 módulos actuales, sin módulos ni capas nuevos: ver DA-1 | Ver DA-1 (ALT-3) |
| DT-2 | Reorganización opción A sobre `f25ee46`, con la salida del índice de los 12 `.pyc`: ver DA-2 | Ver DA-2 |
| DT-3 | Log único con `LOGGING_CONFIG` y excepción no capturada registrada en `main()`: ver DA-3 y DA-4 | Ver DA-3 y DA-4 |
| DT-4 | Errores de carga con `ImageLoadError` y omisión en el bucle: ver DA-5 | Ver DA-5 |
| DT-5 | Normalización RGB sobre negro, ajuste de GIF y límites al pintar: ver DA-6, DA-7 y DA-8 | Ver DA-6 a DA-8 |
| DT-6 | N paneles y configuración de la carpeta del código: ver DA-9 y DA-10 | Ver DA-9 y DA-10 |
| DT-7 | Unidades systemd, dependencias, versión SemVer y finales LF: ver DA-11, DA-12, DA-14 y DA-15 | Ver DA-11, DA-12, DA-14 y DA-15 |
| DT-8 | Pruebas en `raspberry-panel/tests/` sin puntos de inyección nuevos: ver DA-13 | Ver DA-13 |
| DT-9 | Orden de fases según RS-1: línea base, reorganización, caracterización, arreglos (log, imágenes, despliegue) y documentación. Cada tarea de la reorganización es un commit (RNF-7), reversible con `git revert`. Los arreglos de más riesgo para lo que se ve (imágenes) van antes que los de despliegue | Una fase por cada fase del plan F0 a F7: más fases sin entregable propio. Un solo commit para toda la reorganización: no es reversible por partes |
| DT-10 | Las pruebas de caracterización (C-1 a C-4, huellas de pancartas, modo DEBUG) las escribe **antes** el `probador-funcional` (modo pruebas unitarias) en archivos propios `raspberry-panel/tests/test_caracterizacion_*.py` que ninguna tarea posterior amplía, y pasan desde el primer momento: llevan «Pruebas: no aplica (caracterización sin rojo)» y no pasan por `tools/tdd.py` (el Orquestador las encarga primero al Probador, no al programador). Si una falla sobre el código sin corregir, la tarea queda `bloqueada` y vuelve al Probador. Al cerrar T-13 se anota el sha256 de esos archivos en «Ejecución» y cada rojo desde T-15 los incluye en `--pruebas`, de modo que `tdd.py verde` falla si cambian dentro de una tarea. `conftest.py` entra en el conjunto congelado (si una tarea posterior necesita fixtures nuevas, van en archivos propios). Como `tdd.py` solo compara del rojo al verde de cada tarea, la «Verificación de fase» de F3, F4 y F5 comprueba además que `git log --oneline -- raspberry-panel/tests/test_caracterizacion_*.py raspberry-panel/tests/conftest.py` solo muestra el commit de F2 (o el de T-14 si PA-1 no amplía C2) y que `git status --porcelain` sobre esas rutas sale vacío. Los arreglos sí llevan «Pruebas: tdd» | Marcarlas «tdd»: `tools/tdd.py rojo` rechaza unas pruebas que pasan («ROJO NO VÁLIDO»). Dejarlas sin congelar: nada detectaría un cambio posterior |
| DT-11 | La comparación de compilación del ESP32 de F0-bis (RS-7) se hace dentro de T-05, por el programador-arduino, que es quien puede compilar. T-01 queda de solo lectura | Que T-01 compile el ESP32: no es de su rol |
| DT-12 | El modo `DEBUG` = 1 se caracteriza antes de los arreglos (T-13), porque RF-7, RF-8, RF-10 y la rotación tocan código que ese modo usa (RI-9). El caso de `DEBUG` = 0 con dos vueltas se prueba en T-25, porque necesita la configuración de la carpeta del código | Probar RF-18 solo al final: un arreglo podría romperlo sin que nadie lo vea |
| DT-13 | La versión 1.0.0 nace en T-14, la primera tarea de los arreglos (DA-14); los commits de la reorganización siguen con la excepción C2. Los commits de F2 (solo pruebas, ningún producto cambia) y el de T-34 (README del ESP32) se tratan como la reorganización si el usuario amplía C2 (PA-1); si no, F2 no tiene commits propios hasta T-14 | Subir la versión en cada commit de la reorganización: ya está decidido que no. Mover T-14 a F2: contradice DA-14 |
| DT-14 | El tablero exige roles `programador-…` (`check_tareas.py`). Las tareas de caracterización (T-09 a T-13) las ejecuta programador-python, que solo verifica y marca, con las pruebas escritas por el Probador (DT-10). El contenido de `doc/diseno/` (T-33) lo escribe el `ingeniero-inverso` por encargo del Orquestador, porque la política no deja a programador-python escribir ahí; programador-python solo verifica rutas y enlaces y marca la tarea | Que programador-python escriba `doc/diseno/`: el guardián lo bloquea. Sacar T-33 del tablero: pierde la trazabilidad de RF-16 |
| DT-15 | Cada commit de tarea se hace con `git add -- <rutas de la tarea>`, sin `doc/tareas/**` ni `doc/pruebas/**` (que `gestor_tareas.py` y el registro de pruebas modifican durante la tarea y se confirman en el commit de cierre de fase). Toda comprobación de `git status` o de «solo renombrados» se acota a las rutas de la tarea | Comprobar sobre todo el árbol: nunca saldría limpio |
| DT-16 | El entorno de la Pi (Python, Pillow, usuario del servicio, apagado existente, sudo) se consulta antes de usarlo (PA-2: requisito previo de T-19, T-26 y T-27; no bloquea la reorganización), no al desplegar, porque T-19 usa `Image.Resampling` (Pillow ≥ 9.1) en el código que corre en la Pi | Mirarlo solo en F5/F6: un Pillow antiguo convertiría en omitidos todos los GIF grandes sin que UAT-17 lo viera |

## Preguntas abiertas

| ID | Pregunta | Bloquea |
|---|---|---|
| PA-1 | ¿Se amplía la excepción C2 (commits sin subir versión) a los commits de F2 y T-34, y crea el usuario `.agentes/version.json` (dos sitios: constantes de `LedMatrixAnimation.py` y línea de versión del README) antes de empezar F3? | T-14 (y los commits de F2 si no se amplía) |
| PA-2 | ¿Ejecuta el usuario en la Pi, una vez y de solo lectura, `/home/pi/venv/bin/python3 --version`, `/home/pi/venv/bin/python3 -c "import PIL; print(PIL.__version__)"`, `systemctl show panel -p User`, `systemctl list-unit-files` (buscar apagado) y `sudo -l`, y pasa la salida? | T-19, T-26, T-27 (no bloquea la reorganización ni T-01) |

## Fases

| Fase | Objetivo | Entregable comprobable | Verificación de fase | Entregable | Estado |
|---|---|---|---|---|---|
| F0 | Fijar la línea base y los recuentos antes de mover nada | Nota F0-bis en la memoria de decisiones y documentos previos en un commit | Solo lectura; sin casos de prueba | no | cerrada |
| F1 | Reorganizar el repositorio sin cambiar comportamiento | Árbol `esp32/`, `raspberry-panel/`, `archivo/`; duplicados eliminados; firmware compila igual | UAT-1 a UAT-4 (casos PF-n que preparará el Probador funcional) | no | cerrada |
| F2 | Fijar con pruebas el comportamiento actual del panel | `raspberry-panel/tests/` con C-1 a C-4, huellas de las 12 pancartas y modo DEBUG, todo en verde sobre el código sin corregir | UAT-5 (casos PF-n que preparará el Probador funcional) | no | pendiente |
| F3 | Un único log y toda caída registrada | Log único con las trazas de los 5 módulos y la excepción no capturada registrada; versión 1.0.0 declarada | UAT-6, UAT-13 y UAT-19, más la comprobación de `git log` sobre las pruebas de caracterización (DT-10) (casos PF-n que preparará el Probador funcional) | no | pendiente |
| F4 | Todas las imágenes se muestran bien y un archivo roto no tumba el servicio | PNG y GIF de cualquier modo y tamaño se pintan dentro del panel; los rotos se omiten con su causa; N paneles | UAT-7 a UAT-11, más la comprobación de `git log` de DT-10 (casos PF-n que preparará el Probador funcional) | no | pendiente |
| F5 | Despliegue reproducible y modo de PC intacto | Configuración de la carpeta del código, servicios, dependencias y README de despliegue | UAT-12, UAT-14, UAT-15 y UAT-18, más la comprobación de `git log` de DT-10 (casos PF-n que preparará el Probador funcional) | no | pendiente |
| F6 | Documentación vigente y comprobación final en la Pi | READMEs, documento de diseño actualizado y UAT en la Pi | UAT-16 y UAT-17 (con un GIF animado mayor que el panel y un GIF de 1 frame en la Pi) más la regresión de F1 a F5 (casos PF-n que preparará el Probador funcional) | sí | pendiente |

## Tablero

| ID | Fase | Tarea | Rol | Nivel | Depende de | Estado |
|---|---|---|---|---|---|---|
| T-01 | F0 | Recontar la reorganización sobre la línea base | programador-python | normal | — | hecha |
| T-02 | F0 | Registrar los documentos previos en un commit | programador-python | normal | T-01 | hecha |
| T-03 | F1 | Sacar los .pyc del índice y ampliar .gitignore | programador-python | normal | T-02 | hecha |
| T-04 | F1 | Eliminar los archivos duplicados | programador-python | relevante | T-03 | hecha |
| T-05 | F1 | Mover el firmware ESP32 a esp32/ | programador-arduino | relevante | T-04 | hecha |
| T-06 | F1 | Mover el panel de la Raspberry a raspberry-panel/ | programador-python | relevante | T-05 | hecha |
| T-07 | F1 | Archivar los archivos sin copia | programador-python | relevante | T-06 | hecha |
| T-08 | F2 | Declarar las dependencias de prueba | programador-python | normal | T-07 | pendiente |
| T-09 | F2 | Caracterizar la matriz de LEDs y el color | programador-python | normal | T-08 | pendiente |
| T-10 | F2 | Caracterizar la generación de frames | programador-python | normal | T-08 | pendiente |
| T-11 | F2 | Caracterizar el pintado en la tira simulada | programador-python | normal | T-08 | pendiente |
| T-12 | F2 | Fijar las huellas de las doce pancartas | programador-python | normal | T-10, T-11 | pendiente |
| T-13 | F2 | Caracterizar el modo DEBUG de PC | programador-python | normal | T-08 | pendiente |
| T-14 | F3 | Declarar la versión 1.0.0 del panel | programador-python | normal | T-09, T-10, T-11, T-12, T-13 | pendiente |
| T-15 | F3 | Unificar el registro del log | programador-python | relevante | T-14 | pendiente |
| T-16 | F3 | Registrar toda excepción no capturada | programador-python | normal | T-15 | pendiente |
| T-17 | F4 | Convertir toda imagen a RGB sobre negro | programador-python | normal | T-16 | pendiente |
| T-18 | F4 | Mostrar un GIF no animado como imagen estática | programador-python | normal | T-17 | pendiente |
| T-19 | F4 | Reducir al panel los GIF mayores | programador-python | normal | T-18 | pendiente |
| T-20 | F4 | Limitar el pintado a los límites del panel | programador-python | normal | T-19 | pendiente |
| T-21 | F4 | Traducir los errores de carga de imágenes | programador-python | normal | T-20 | pendiente |
| T-22 | F4 | Omitir los archivos que no cargan | programador-python | normal | T-21 | pendiente |
| T-23 | F4 | Esperar cuando una vuelta no reproduce ningún archivo | programador-python | normal | T-22 | pendiente |
| T-24 | F4 | Admitir cualquier número de paneles | programador-python | normal | T-23 | pendiente |
| T-25 | F5 | Leer la configuración de la carpeta del código | programador-python | normal | T-24 | pendiente |
| T-26 | F5 | Cambiar el usuario de panel.service a pi | programador-python | normal | T-25 | pendiente |
| T-27 | F5 | Crear el servicio de apagado | programador-python | normal | T-26 | pendiente |
| T-28 | F5 | Declarar las dependencias de ejecución | programador-python | normal | T-27 | pendiente |
| T-29 | F5 | Fijar los finales de línea LF de los servicios | programador-python | normal | T-27 | pendiente |
| T-30 | F5 | Escribir el README de despliegue de raspberry-panel | programador-python | normal | T-28, T-29 | pendiente |
| T-31 | F6 | Escribir el README de la raíz | programador-python | normal | T-30 | pendiente |
| T-32 | F6 | Escribir el README de archivo | programador-python | normal | T-30 | pendiente |
| T-33 | F6 | Actualizar el documento de diseño del panel | programador-python | normal | T-30 | pendiente |
| T-34 | F6 | Ajustar el README del ESP32 a su carpeta | programador-arduino | normal | T-30 | pendiente |

## Fichas

### T-01 · Recontar la reorganización sobre la línea base

- **Requisitos:** habilitadora
- **Objetivo:** existe una nota escrita con los recuentos y comprobaciones de la reorganización sobre `f25ee46` (F0-bis, RS-7), de solo lectura, que las tareas T-03 a T-07 usan como lista vigente.
- **Archivos:** modificar `doc/decisiones-arquitectura.md` (añadir una nota «F0-bis · 2026-11-22» al final, sin tocar lo escrito) · no tocar nada más
- **Hecho cuando:**
  - [x] La nota contiene el recuento sobre `f25ee46` (`git ls-tree -r`) de archivos a eliminar (el plan decía 141), a archivar (104) y a conservar, con la diferencia explicada si no coinciden y la lista de rutas vigente de cada grupo (A1 a B3 y C). Entrega dos listas: los 12 `.pyc` que salen del índice en T-03 y los archivos que T-04 elimina con `git rm` (A1 a B3 sin los 4 `.pyc` de `navidad/ficheros navidad/panel/__pycache__/`, que están en B3 y entre los 12, con la cifra recalculada).
  - [x] La nota contiene la salida de `git ls-files "*__pycache__*"` (se esperan 12 `.pyc`); si hay otros, la tarea queda `bloqueada` y se informa al usuario, no se decide.
  - [x] La nota contiene la salida de `git ls-files --eol` de `panel/apagado.sh` y `panel/panel.service`, las líneas actuales de `.gitignore` (10, no 5) y la confirmación de que `.agentes/politica.json` da `escribe: ["**"]` a `programador-python` y `programador-arduino` (condición C1).
  - [x] La nota registra `Image.open(p).mode` de `ficheros/banner1.png` a `banner12.png`; si no hay Pillow en el equipo, lo anota y el registro pasa a T-12.
- **Pruebas:** no aplica: es solo lectura y documentación
- **Verificación:** manual · `git status --porcelain -- doc/decisiones-arquitectura.md` lo muestra modificado; la nota contiene los cuatro apartados
- **Riesgo y autorización:** ninguno de borrado. Órdenes de solo lectura: `git ls-tree`, `git ls-files`, `git ls-files --eol`, `git log`. Si el recuento exige un script de solo lectura, se ejecuta como tal.
- **Notas:** `e23949d` no existe: la línea base es `f25ee46` (RS-6). Los 141 eliminados eran 137 por sha256 idéntico más 4 `.pyc` (grupo C) que tras T-03 ya no se rastrean y no se borran del disco. `doc/decisiones-arquitectura.md` ya está modificado sin confirmar por el usuario: se añade al final de su estado actual. Las listas del plan están en `doc/decisiones-arquitectura.md` (sección «Lista exacta de eliminaciones» y «Nota 2026-11-15»).
- **Ejecución:** 2026-11-23 · Nota «F0-bis · 2026-11-22» al final de doc/decisiones-arquitectura.md (7 apartados). Recuento sobre f25ee46 por sha256: 137 a eliminar (133 con git rm en T-04 + 4 .pyc de B3), C 4, archivar 104, conservar 52; total 301 (288 en ficheros/navidad, cuadra con el plan; la Nota 2026-11-15 olvidaba los 4 banners antiguos). Nuevo: panel/__pycache__ (4 cpython-313) rastreado, por eso 12 .pyc. eol i/lf w/crlf; .gitignore 10 líneas; C1 cumplida. Sin Pillow: modos a T-12 (IHDR orientativo: 11 RGB, banner6 RGBA). PA-2 pasa a T-19, T-26 y T-27 (apartado 7). Verificación: git status --porcelain muestra M doc/decisiones-arquitectura.md; la nota contiene los apartados. Sin commit (T-02).

### T-02 · Registrar los documentos previos en un commit

- **Requisitos:** habilitadora
- **Objetivo:** el árbol queda limpio para la reorganización, con el análisis, la arquitectura y la memoria de decisiones en un commit (el documento de tareas lo confirma el cierre de fase, DT-15).
- **Archivos:** modificar el índice de git con `doc/analisis/`, `doc/arquitectura/` y `doc/decisiones-arquitectura.md` · no tocar `.agentes/`, `tools/` ni código
- **Hecho cuando:**
  - [x] Existe un commit que contiene solo esos tres grupos de archivos (DT-15: `doc/tareas/` no va en este commit).
  - [x] `git status --porcelain -- doc/analisis doc/arquitectura doc/decisiones-arquitectura.md` sale vacío.
- **Pruebas:** no aplica: solo registra documentos
- **Verificación:** manual · `git show --stat HEAD` lista solo archivos de `doc/`; `git status --porcelain -- doc/analisis doc/arquitectura doc/decisiones-arquitectura.md` vacío
- **Riesgo y autorización:** necesita `git add` y `git commit` (siempre preguntan). Sin borrados. No se hace `git add -A`: solo esas rutas.
- **Notas:** el árbol puede tener cambios del usuario en `.agentes/` o `tools/`: no se incluyen (C4 del plan). Regla común DT-15 para todos los commits de tarea: `git add -- <rutas de la tarea>` y comprobaciones acotadas a esas rutas.
- **Ejecución:** 2026-11-23 · Commit 0059118 «T-02: análisis, arquitectura y memoria de decisiones de los arreglos del panel»: 3 archivos (doc/analisis/2026-11-22-panel-raspberry-arreglos.md, doc/arquitectura/2026-11-22-panel-raspberry-arreglos.md, doc/decisiones-arquitectura.md), solo doc/. git status --porcelain de esas rutas vacío. doc/tareas/ fuera del commit (DT-15). Sin push.

### T-03 · Sacar los .pyc del índice y ampliar .gitignore

- **Requisitos:** RF-1
- **Objetivo:** los 12 `.pyc` rastreados salen del índice sin borrarse del disco y git ignora `__pycache__/` y el resto de archivos generados (RN-13).
- **Archivos:** modificar `.gitignore` · sacar del índice con `git rm --cached` los 12 `.pyc` listados en T-01 · no tocar código ni archivos del disco
- **Hecho cuando:**
  - [x] `.gitignore` conserva sus líneas y añade `__pycache__/`, `*.py[cod]`, `*.log`, `*.log.*`, `.idea/`, `desktop.ini` y `Thumbs.db`; no ignora `*.pdn`.
  - [x] `git ls-files "*.pyc"` no devuelve ninguno.
  - [x] Los 12 archivos siguen en el disco.
  - [x] Existe 1 commit con solo esos cambios.
- **Pruebas:** no aplica: configuración y salida del índice, sin comportamiento
- **Verificación:** manual · `git ls-files "*.pyc"` vacío; `git check-ignore -v panel/__pycache__/Panel.cpython-313.pyc` lo muestra ignorado; `git show --stat HEAD` solo muestra `.gitignore` y las 12 bajas del índice; `git status --porcelain -- .gitignore panel navidad` vacío (DT-15)
- **Riesgo y autorización:** `git rm --cached` de 12 archivos: autorizado por el usuario (RN-13, RS-4, 2026-11-22). Necesita `git commit`. Antes de cualquier `git restore`, `git status --porcelain -- .gitignore panel navidad` debe mostrar solo lo de la tarea (C4, DT-15).
- **Notas:** el log `animation_panel.log` de `panel/` sigue rastreado: lo ignorado por `*.log` no deja de rastrearse y T-06 lo mueve a `archivo/`. Los 4 `.pyc` de `navidad/panel/__pycache__/` (grupo C) y los 4 de `navidad/ficheros navidad/panel/__pycache__/` (que también figuran en B3) quedan sin seguimiento y sin borrar: T-04 no los toca con `git rm` y viajan con `navidad/` a `archivo/` en T-07, salvo que el usuario autorice borrarlos del disco.
- **Ejecución:** 2026-11-23 · Commit b7cc635 «T-03: sacar los 12 .pyc del índice y ampliar .gitignore»: .gitignore (+7 líneas, conserva las 10) y 12 .pyc fuera del índice con git rm --cached. Verificación: git ls-files "*.pyc" vacío; git check-ignore -v da .gitignore:11:__pycache__/ para panel/__pycache__/Panel.cpython-313.pyc; *.pdn no ignorado; git status --porcelain -- .gitignore panel navidad vacío; los 12 siguen en disco. git show --stat: 13 archivos (.gitignore + 12 bajas). doc/tareas y doc/pruebas fuera (DT-15). Sin push.

### T-04 · Eliminar los archivos duplicados

- **Requisitos:** RF-2
- **Objetivo:** solo queda una carpeta de imágenes originales: se eliminan los archivos cuyo sha256 es idéntico al de otro que se conserva (RN-11).
- **Archivos:** eliminar con `git rm` los grupos A1 a B3 de la segunda lista de T-01 (sin los `.pyc` que T-03 ya sacó del índice; su sha256 se comprueba igualmente como duplicados) · no tocar los archivos que se conservan ni el grupo C (sus `.pyc` ya no se rastrean y siguen en disco) · `navidad/3/` y `navidad/5/` vacías se quitan con `rmdir`
- **Hecho cuando:**
  - [x] Antes de eliminar cada grupo, un script de solo lectura comprueba el sha256 de cada par eliminado = conservado y aborta ese grupo si alguno no coincide.
  - [x] Todos los archivos de la lista de T-01 están eliminados del índice; el recuento coincide con el de T-01.
  - [x] Cada archivo eliminado tiene un par idéntico por sha256 en el árbol, comprobado con la lista de T-01.
  - [x] Existe 1 commit con solo esas eliminaciones.
- **Pruebas:** no aplica: eliminación de duplicados, sin comportamiento
- **Verificación:** manual · el script de sha256 sale con 0 diferencias; `git show --stat HEAD` solo muestra bajas; `git ls-tree -r HEAD -- ficheros panel` sigue mostrando `ficheros/banner1.png` a `banner12.png` y los 5 `.py` de `panel/`
- **Riesgo y autorización:** borrado de unos 137 archivos (cifra de T-01): la lista del plan ya está autorizada (usuario, 2026-11-14), no otras (RS-4, RN-11). Si algún sha256 no coincide, se aborta ese grupo y no se elimina nada de él. Necesita `git rm`, `rmdir` y `git commit`. Pausar la sincronización de OneDrive entre esta tarea y T-07 (RI-5).
- **Notas:** supera el límite de archivos por ser una sola funcionalidad (limpieza por duplicado): partirla en grupos dejaría commits no reversibles de una vez. El script de solo lectura se guarda en el scratchpad. Rutas con espacios y acentos entre comillas (`ficheros - copia`, `Sin título.png`).
- **Ejecución:** 2026-11-23 · Commit b70b25d «T-04: eliminar los 133 archivos duplicados por sha256»: 133 bajas, ninguna otra cosa (git show --name-status: 0 líneas que no sean D). Script de sha256 de solo lectura por grupo: A1 6, A2 1, A3 6, A4 6, A5 12, A6 38, A7 42, B1 12, B2 1, B3 9, todos con 0 diferencias; los 4 .pyc de B3 son iguales a los del grupo C. git rm --pathspec-from-file, primero en simulación (133). Quedan 156 rastreados en ficheros/navidad/panel (301-12-133); HEAD conserva ficheros/banner1-12.png y los 5 .py de panel/. rmdir navidad/3 navidad/5 (vacías). Desviación de la ficha: el script está en tools/t04_verificar_duplicados.py (y sus rutas en tools/t04_rutas.txt), dentro del repo y sin rastrear, en vez de en el scratchpad, porque el arnés bloquea escribir fuera del repositorio; decisión del usuario 2026-11-23. Se borran al terminar T-07. RI-5 no aplica: la carpeta no está en OneDrive (usuario). Sin push.

### T-05 · Mover el firmware ESP32 a esp32/

- **Requisitos:** RF-4
- **Objetivo:** el firmware ESP32 vive en `esp32/` y compila con los mismos recursos que antes de moverlo (RNF-4).
- **Archivos:** crear `esp32/.gitignore` (plantilla de PlatformIO: `.pio` y las 4 líneas de `.vscode/`) · mover con `git mv` `platformio.ini`, `src`, `data` y `README.md` a `esp32/` · mover `.pio` a `esp32/.pio` · no tocar el contenido de `src/`, `data/` ni `platformio.ini`
- **Hecho cuando:**
  - [x] Antes de mover, `pio run -e esp32dev` en la raíz da SUCCESS y se anota RAM y flash; si no son RAM 48 728 B y flash 890 553 B, se para y se pregunta al usuario.
  - [x] Tras mover, `pio run -d esp32 -e esp32dev` da SUCCESS con RAM 48 728 B (14,9 %) y flash 890 553 B (67,9 %).
  - [x] `git show --stat -M HEAD` solo muestra renombrados al 100 % y `A esp32/.gitignore`.
  - [x] Existe 1 commit con solo esos cambios.
- **Pruebas:** no aplica: movimiento de carpeta sin cambio de código; lo comprueba la compilación
- **Verificación:** compilación · `pio run -e esp32dev` antes y `pio run -d esp32 -e esp32dev` después; RAM y flash iguales
- **Riesgo y autorización:** mueve el firmware (varios archivos, hardware afectado solo si cambia el binario). Órdenes: `mkdir`, `git mv`, `mv .pio esp32/.pio`, `pio run`, `git commit`. Si PlatformIO no acepta `.pio` movida y redescarga las `lib_deps`, es red: se pregunta al usuario. Esta tarea es la parte de compilación de F0-bis (DT-11).
- **Notas:** el firmware no se versiona en esta tanda (RG-15). Vuelta atrás: `git revert <commit>` o los `git mv` inversos, `mv esp32/.pio .pio`.
- **Ejecución:** 2026-11-23 · commit af2050d · antes (raiz): pio run -e esp32dev SUCCESS, RAM 48728 B (14,9 %), flash 890553 B (67,9 %) · despues: pio run -d esp32 -e esp32dev SUCCESS, RAM 48728 B (14,9 %), flash 890553 B (67,9 %), identicos · git show --stat -M HEAD: 6 renombrados al 100 % y A esp32/.gitignore · .pio NO movida (mv no autorizado en el encargo): PlatformIO descargo las lib_deps en esp32/.pio (ArduinoJson 6.21.6, Adafruit NeoPixel 1.15.5, AnimatedGIF 1.4.7); la .pio vieja sigue en la raiz, ignorada por .gitignore · el usuario confirmo (2026-11-23) que la descarga de lib_deps por red estaba autorizada (autorizacion general) · la .pio de la raiz la borra el programador-python con autorizacion del usuario

### T-06 · Mover el panel de la Raspberry a raspberry-panel/

- **Requisitos:** RF-1, RF-4
- **Objetivo:** el código vigente de la Pi y sus imágenes viven en `raspberry-panel/`, sin que cambie ningún archivo de contenido (opción A, DA-2).
- **Archivos:** crear `raspberry-panel/` y `archivo/raspberry-panel/` · mover con `git mv` `panel/animation_panel.log` a `archivo/raspberry-panel/animation_panel.log`, `panel` a `raspberry-panel/panel` y `ficheros` a `raspberry-panel/ficheros` · no tocar el contenido de ningún archivo
- **Hecho cuando:**
  - [x] Existen `raspberry-panel/panel/` con los 5 `.py`, `configuracion.json`, `panel.service` y `apagado.sh`, y `raspberry-panel/ficheros/banner1.png` a `banner12.png`.
  - [x] `git ls-files panel ficheros` no devuelve nada y `animation_panel.log` solo está rastreado en `archivo/raspberry-panel/`.
  - [x] Los 5 `.py` compilan y `import Config, Panel` funciona desde `raspberry-panel/panel`.
  - [x] `git show --stat -M HEAD` solo muestra renombrados al 100 %.
  - [x] Si queda `panel/__pycache__/` en disco, se movió (no se borró) a `raspberry-panel/panel/__pycache__/`.
- **Pruebas:** no aplica: movimiento sin cambio de contenido; lo comprueban la compilación y la importación
- **Verificación:** compilación · `py -3 -m py_compile raspberry-panel/panel/*.py`; en `raspberry-panel/panel`: `py -3 -c "import Config, Panel"` (no se importan los módulos que crean el log); `git show --stat -M HEAD`
- **Riesgo y autorización:** mueve el código vigente (varios módulos). Órdenes: `mkdir -p`, `git mv`, `py -3`, `git commit`. Sin borrados. Si queda un `__pycache__` en disco que no se pueda mover, quitarlo lo autoriza el usuario.
- **Notas:** el log de diciembre de 2025 va a `archivo/` rastreado como evidencia de RF-17 (T-12 lo usa). Vuelta atrás: `git revert <commit>`.
- **Ejecución:** 2026-11-23 · Commit 82b5411 «T-06: mover el panel de la Raspberry a raspberry-panel/»: 57 renombrados al 100 % (git show --stat -M), 0 inserciones y 0 borrados. git mv de panel/animation_panel.log a archivo/raspberry-panel/, de panel a raspberry-panel/panel y de ficheros a raspberry-panel/ficheros. git ls-files panel ficheros vacío; el log solo está rastreado en archivo/raspberry-panel/. py -3 -m py_compile de los 5 .py: compilan; py -3 -c 'import Config, Panel' en raspberry-panel/panel: OK, sin crear log. panel/__pycache__/ (4 .pyc cpython-313, sin rastrear) se movió con la carpeta, no se borró; py_compile añadió .pyc cpython-315, ignorados. Sin push.

### T-07 · Archivar los archivos sin copia

- **Requisitos:** RF-3
- **Objetivo:** lo que no tiene copia (imágenes del juego, `navidad/1/`, iconos, `globos/`, `.pdn`, `banner7-1`, `banner8-1`, banners antiguos, código antiguo y el log) queda en `archivo/` con su contenido intacto (P-10).
- **Archivos:** crear `archivo/banners-antiguos/` · mover con `git mv` `raspberry-panel/ficheros/iconos/banners/old/banner1.png`, `banner7.png`, `banner8.png` y `banner9.png` a `archivo/banners-antiguos/` y `navidad` a `archivo/navidad` · quitar con `rmdir` `navidad/3` y `navidad/5` si siguen · no tocar `raspberry-panel/ficheros/banner*.png`
- **Hecho cuando:**
  - [x] Cada archivo único del inventario de T-01 que existe en la línea base está en `archivo/` con el mismo sha256 que el original.
  - [x] El recuento de `archivo/` coincide con el recalculado en T-01 (el plan esperaba 104).
  - [x] `raspberry-panel/ficheros/` conserva `banner1.png` a `banner12.png` en su primer nivel.
  - [x] `git show --stat -M HEAD` solo muestra renombrados al 100 %.
  - [x] Existe 1 commit con solo esos cambios.
- **Pruebas:** no aplica: movimiento de archivos sin comportamiento
- **Verificación:** manual · script de solo lectura con sha256 de cada archivo único (0 diferencias) y `git ls-tree` de comprobación de blobs; `git show --stat -M HEAD`
- **Riesgo y autorización:** mueve más de 100 archivos y no borra ninguno. Órdenes: `mkdir`, `git mv`, `rmdir`, `git commit`, script de solo lectura. El `archivo/README.md` lo escribe T-32, no esta tarea.
- **Notas:** supera el límite de archivos por ser un solo movimiento de carpeta (`git mv navidad`). Lo que solo existía en `e23949d` (p. ej. `navidad/1.bat`) se da por perdido y no se exige (RS-6). Los `.pyc` del grupo C van con la carpeta, ya sin seguimiento. Cuando esta tarea esté hecha se puede reanudar la sincronización de OneDrive.
- **Ejecución:** 2026-11-23 · Commit f66f0f4 «T-07: archivar en archivo/ los archivos sin copia»: 103 renombrados al 100 % (99 de navidad/ a archivo/navidad/ y banner1, 7, 8 y 9 de raspberry-panel/ficheros/iconos/banners/old/ a archivo/banners-antiguos/), 0 inserciones y 0 borrados. archivo/ tiene 104 rastreados (con el log de T-06), como en T-01. sha256 de contenidos, sin script nuevo: 'git ls-files -z -- <rutas> | xargs -0 sha256sum | cut -c1-64 | sort | sha256sum' da adbb01f7…aa016 antes (navidad, banners/old, archivo) y después (archivo). Contra la línea base (objeción 3 del Cuestionador): 'git diff --find-renames=100% --diff-filter=AMT --name-status f25ee46 HEAD' solo muestra M .gitignore, A doc/analisis/…, A doc/arquitectura/…, M doc/decisiones-arquitectura.md y A esp32/.gitignore; nada bajo archivo/ ni raspberry-panel/. raspberry-panel/ficheros conserva banner1-12.png. navidad/3 y navidad/5 ya no existían (T-04). Los .pyc sin rastrear de navidad viajaron con la carpeta. Sin push. Limpieza del cierre de F1 (autorizada por el usuario el 2026-11-23, objeciones 1 y 2 del Cuestionador): borrados tools/t04_verificar_duplicados.py, tools/t04_rutas.txt, la carpeta vacía raspberry-panel/ficheros/iconos/banners/old/ y la .pio de la raíz (esp32/.pio se conserva); nada estaba rastreado y git status no muestra cambios en archivos rastreados.

### T-08 · Declarar las dependencias de prueba

- **Requisitos:** RF-14
- **Objetivo:** existe `raspberry-panel/requirements-dev.txt` y un venv de Windows con Python 3.11 o superior desde el que `pytest` arranca sin librerías de hardware.
- **Archivos:** crear `raspberry-panel/requirements-dev.txt` · no tocar `raspberry-panel/panel/`
- **Hecho cuando:**
  - [ ] El archivo contiene `Pillow>=9.1` y `pytest>=9.2,<10`, sin `rpi_ws281x` ni `adafruit-*`, y un comentario de cabecera con «Python 3.11 o superior».
  - [ ] En un venv de Windows con Python 3.11 o superior, `py -3 -m pytest --version` da 9.x.
- **Pruebas:** no aplica: declaración de dependencias
- **Verificación:** manual · `py -3 -m pytest --version` dentro del venv con el archivo instalado
- **Riesgo y autorización:** instalar paquetes es red y siempre se pregunta: lo hace el usuario (`py -3 -m venv` y `pip install -r raspberry-panel/requirements-dev.txt`) o lo autoriza para este encargo.
- **Notas:** Python 3.11 o superior (RNF-8, PA-5 elevado en la arquitectura). `Pillow>=9.1` figura también en `requirements.txt` (T-28): es la excepción aceptada de DA-12 (PQ-2).
- **Ejecución:** —

### T-09 · Caracterizar la matriz de LEDs y el color

- **Requisitos:** RF-5
- **Objetivo:** hay pruebas que fijan lo que hace hoy `Panel.calculateMatrix` y `colourTuple` (C-1 y C-3), en verde sobre el código sin corregir.
- **Archivos:** crear `raspberry-panel/tests/conftest.py` y `raspberry-panel/tests/test_caracterizacion_*.py` (los escribe el Probador funcional, no el programador) · no tocar `raspberry-panel/panel/`
- **Hecho cuando:**
  - [ ] C-1: con 24×18, 2 paneles, `LEFT` y primer LED abajo, la matriz es la esperada, guardada como dato dentro del `test_caracterizacion_*.py` (no se importa código antiguo).
  - [ ] C-3: `colourTuple((255, 0, 0))` da `0xFF0000`.
  - [ ] Las pruebas pasan sin `neopixel`, `board` ni `rpi_ws281x`.
- **Pruebas:** no aplica: son pruebas de caracterización que pasan desde el primer momento (DT-10); las escribe el Probador funcional (modo pruebas unitarias)
- **Verificación:** unitaria · `py -3 -m pytest raspberry-panel/tests`: todas pasan
- **Riesgo y autorización:** ninguno; no se toca código de producción. Importar `Panel` crea `animation_panel.log` en `raspberry-panel/panel/` hasta T-15 (ignorado por `*.log`).
- **Notas:** `conftest.py` añade `raspberry-panel/panel` a `sys.path` (DA-13). El programador-python solo ejecuta la verificación y marca la tarea. Los datos esperados van dentro de los `test_caracterizacion_*.py`.
- **Ejecución:** —

### T-10 · Caracterizar la generación de frames

- **Requisitos:** RF-5
- **Objetivo:** hay una prueba que fija lo que hace hoy `generateFrames` con una pancarta (C-2), en verde sobre el código sin corregir.
- **Archivos:** crear o ampliar `raspberry-panel/tests/test_caracterizacion_*.py` (lo escribe el Probador funcional) · no tocar `raspberry-panel/panel/`
- **Hecho cuando:**
  - [ ] C-2: una imagen de 408×18 con panel de 48 de ancho da 73 frames de 48×18 y 250 ms por frame con `velocidad` 0,25.
  - [ ] La imagen se sintetiza en `tmp_path`.
- **Pruebas:** no aplica: caracterización que pasa desde el primer momento (DT-10)
- **Verificación:** unitaria · `py -3 -m pytest raspberry-panel/tests`: todas pasan
- **Riesgo y autorización:** ninguno
- **Notas:** RN-1: 5 px por frame, y se generan frames mientras `x + ancho_recorte ≤ ancho_imagen`.
- **Ejecución:** —

### T-11 · Caracterizar el pintado en la tira simulada

- **Requisitos:** RF-5, RF-17
- **Objetivo:** hay una prueba que fija a qué LED llega cada píxel de un frame (C-4), con una tira simulada, en verde sobre el código sin corregir.
- **Archivos:** crear o ampliar `raspberry-panel/tests/test_caracterizacion_*.py` (lo escribe el Probador funcional) · no tocar `raspberry-panel/panel/`
- **Hecho cuando:**
  - [ ] C-4: con un frame de 48×18, cada píxel `(x, y)` llega al LED `matriz[y*48+x]` de la tira simulada y el negro puro `(0,0,0)` no se pinta.
  - [ ] La tira se simula con `monkeypatch` sobre `HARDWARE_AVAILABLE`, `LedStrip` y `time.sleep` de `AnimationServer`, y el bucle se corta con una excepción tras una vuelta.
- **Pruebas:** no aplica: caracterización que pasa desde el primer momento (DT-10)
- **Verificación:** unitaria · `py -3 -m pytest raspberry-panel/tests`: todas pasan
- **Riesgo y autorización:** ninguno
- **Notas:** el contrato con las pruebas es `HARDWARE_AVAILABLE`, el atributo `LedStrip` (con `fill`, `__setitem__` y `show`) y el uso de `time.sleep` a través del módulo `time` (DA-13).
- **Ejecución:** —

### T-12 · Fijar las huellas de las doce pancartas

- **Requisitos:** RF-10, RF-17
- **Objetivo:** hay una huella de lo que llega a cada uno de los 864 LED en cada frame de `banner1.png` a `banner12.png`, y sus frames y duraciones coinciden con el log de diciembre de 2025, para detectar cualquier cambio de color o de tiempo.
- **Archivos:** crear o ampliar `raspberry-panel/tests/test_caracterizacion_*.py` (lo escribe el Probador funcional) · no tocar `raspberry-panel/panel/`
- **Hecho cuando:**
  - [ ] Para cada banner, la prueba guarda dentro del `test_caracterizacion_*.py` una huella (p. ej. sha256 de la secuencia de valores por LED, con `colourTuple` o 0 si no se pinta) calculada con la tira simulada.
  - [ ] El número de frames de cada banner es igual al de las líneas «Generados N frames» del log archivado en `archivo/raspberry-panel/animation_panel.log`, tomando solo las sesiones con ancho total 48 (sin la primera, de 2025-12-06 15:59 a 16:01, que da 77 en `banner1` frente a 73); la duración es `velocidad` × 1000 (de la línea «Imagen : …»). Si una pancarta tiene más de un valor en las sesiones elegidas, se para y se pregunta.
  - [ ] El modo de cada banner (`Image.open(p).mode`) queda anotado; un banner que hoy no se puede pintar (paleta) se señala y no cuenta como cambio.
- **Pruebas:** no aplica: caracterización que pasa desde el primer momento (DT-10)
- **Verificación:** unitaria · `py -3 -m pytest raspberry-panel/tests`: todas pasan sobre el código sin corregir; `grep` del log archivado por pancarta en esas sesiones: un solo valor por banner
- **Riesgo y autorización:** ninguno. Si un banner da error de paleta hoy, queda señalado y se informa; no se corrige aquí.
- **Notas:** si T-01 no pudo registrar los modos por falta de Pillow, se registran aquí. Esta huella es la referencia «antes» de RF-10 (T-17).
- **Ejecución:** —

### T-13 · Caracterizar el modo DEBUG de PC

- **Requisitos:** RF-18
- **Objetivo:** hay una prueba que fija que con `DEBUG` = 1 `startAnimationTest` abre una ventana por frame escalado ×10, en verde sobre el código sin corregir.
- **Archivos:** crear o ampliar `raspberry-panel/tests/test_caracterizacion_*.py` (lo escribe el Probador funcional) · no tocar `raspberry-panel/panel/`
- **Hecho cuando:**
  - [ ] Para una imagen conocida, `startAnimationTest` muestra una ventana por frame y la imagen mostrada mide el frame ×10 (con `Image.show` o el equivalente simulado, sin abrir ventanas reales).
  - [ ] La prueba pasa en Windows sin librerías de hardware.
- **Pruebas:** no aplica: caracterización que pasa desde el primer momento (DT-10, DT-12)
- **Verificación:** unitaria · `py -3 -m pytest raspberry-panel/tests`: todas pasan
- **Riesgo y autorización:** ninguno. La comprobación visual de la ventana real la hace el usuario en la verificación de F5 (UAT-18).
- **Notas:** va antes de los arreglos porque RF-7, RF-8, RF-10 y la rotación del log tocan código que ese modo usa (RI-9). Al cerrar esta tarea se anota en «Ejecución» el sha256 de los `test_caracterizacion_*.py` (T-09 a T-13) y cada rojo desde T-15 los lista en `--pruebas` (DT-10).
- **Ejecución:** —

### T-14 · Declarar la versión 1.0.0 del panel

- **Requisitos:** habilitadora
- **Objetivo:** el panel tiene versión SemVer y fecha en los sitios que `tools/version.py` sincroniza, y un CHANGELOG (DA-14).
- **Archivos:** modificar `raspberry-panel/panel/LedMatrixAnimation.py` (añadir `__version__ = "1.0.0"` y `__date__ = "AAAA-MM-DD"`) · crear `raspberry-panel/README.md` (solo título y la línea `**Versión:** 1.0.0 · **Fecha:** AAAA-MM-DD`; T-30 lo completa) · crear `raspberry-panel/CHANGELOG.md` con `## [1.0.0] - AAAA-MM-DD` · no tocar nada más
- **Hecho cuando:**
  - [ ] `LedMatrixAnimation.py` define `__version__` y `__date__`, sin usarlas en otro sitio ni registrarlas en el log.
  - [ ] `raspberry-panel/README.md` tiene la línea de versión con el formato exacto de DA-14.
  - [ ] `CHANGELOG.md` tiene la entrada `## [1.0.0] - AAAA-MM-DD`.
  - [ ] Con `.agentes/version.json` creado por el usuario, `py -3 tools/version.py --check` da que los sitios coinciden y que el CHANGELOG tiene la entrada.
- **Pruebas:** no aplica: constantes de versión sin comportamiento
- **Verificación:** manual · `py -3 tools/version.py --check`; `py -3 -m pytest raspberry-panel/tests` sigue en verde
- **Riesgo y autorización:** el programador no puede crear `.agentes/version.json` (zona protegida): lo crea el usuario con los dos sitios (la constante `__version__` y `__date__` de `LedMatrixAnimation.py` y la línea del README) y las expresiones de DA-14; el último criterio queda a la espera de ese paso. Necesita `py -3 tools/version.py`.
- **Notas:** la fecha es la del día de la tarea (ISO 8601). Los commits de F1 siguen con la excepción C2; desde esta tarea cada commit sube al menos PATCH y la fecha con `py -3 tools/version.py --write`. El ESP32 queda sin sitio en `version.json` (RG-15).
- **Ejecución:** —

### T-15 · Unificar el registro del log

- **Requisitos:** RF-6, RF-13
- **Objetivo:** un solo gestor con rotación escribe `animation_panel.log` y las trazas de los 5 módulos, incluida `Panel`, llegan a él (DA-3).
- **Archivos:** modificar `raspberry-panel/panel/LedMatrixAnimation.py`, `Panel.py`, `Animation.py` y `AnimationServer.py` · no tocar `Config.py` ni `colourTuple` ni la creación del NeoPixel
- **Hecho cuando:**
  - [ ] `LedMatrixAnimation.py` define la constante de módulo `LOGGING_CONFIG` con un único `RotatingFileHandler` de clave `archivo` en el logger raíz: `animation_panel.log` junto al código, 26 214 400 B, 5 copias, formato `%(asctime)s - %(name)s - %(levelname)s - %(message)s`, nivel INFO, utf-8 y `disable_existing_loggers: False`; el bloque `__main__` queda en `logging.config.dictConfig(LOGGING_CONFIG)` y `main()`.
  - [ ] Los 5 módulos solo hacen `logging.getLogger(__name__)`, sin gestores ni `setLevel`, y no queda `from venv import logger`.
  - [ ] Con `LOGGING_CONFIG` aplicada y `filename` en `tmp_path`, crear un `Panel` deja la línea INFO «Total LEDs in panel: 864» con el logger `Panel`.
  - [ ] Los gestores de archivo de los loggers del panel son uno solo, sobre `animation_panel.log`.
  - [ ] La excepción a la rotación diaria figura con fecha en la entrada del 2026-11-22 de `doc/decisiones-arquitectura.md` («Excepciones a prácticas declaradas») y en RN-7 del análisis; se comprueba con `Grep`, no se reescribe.
- **Pruebas:** tdd
- **Verificación:** unitaria · `py -3 tools/tdd.py verde doc/tareas/2026-11-22-panel-raspberry-arreglos.md T-15`; `py -3 -m pytest raspberry-panel/tests` con C-1 a C-4 y las huellas sin tocar
- **Riesgo y autorización:** cambia el registro de varios módulos (relevante); la arquitectura ya está cuestionada. Sin borrados de funcionalidad: se quitan los 3 bloques de configuración duplicados y `from venv import logger`, que es la corrección pedida. Órdenes: `py -3 -m pytest`, `py -3 tools/tdd.py`.
- **Notas:** `LOGGING_CONFIG`, el gestor `archivo` y su `filename` son contrato con las pruebas (DA-3). Se aceptan las excepciones a `python-logging` (rotación solo por tamaño y valores en el código), decididas por el usuario el 2026-11-22 (PQ-5). Importar un módulo ya no crea el log. Los mensajes de importación de `AnimationServer` (`:28`, `:33`) salen antes de configurar el log: se acepta (RG-2). Supera el límite de archivos por ser un solo arreglo que quita lo mismo de 4 módulos.
- **Ejecución:** —

### T-16 · Registrar toda excepción no capturada

- **Requisitos:** RF-19
- **Objetivo:** cualquier excepción no prevista deja su traza en `animation_panel.log` antes de que el proceso termine con código 1 (DA-4).
- **Archivos:** modificar `raspberry-panel/panel/LedMatrixAnimation.py` · no tocar otros módulos
- **Hecho cuando:**
  - [ ] Dentro de `main()`, todo el cuerpo va en `try:` / `except Exception: logger.exception(...)` / `raise`.
  - [ ] Con `Config` parcheado para fallar (falta de archivo o de clave), `main()` deja una línea ERROR con la traza completa en el log y relanza la excepción (código de salida 1, error por stderr).
  - [ ] Con una tira simulada que lanza al pintar, el log tiene ERROR con la traza y la excepción se propaga.
  - [ ] `KeyboardInterrupt` y `SystemExit` no generan esa línea.
- **Pruebas:** tdd
- **Verificación:** unitaria · `py -3 tools/tdd.py verde doc/tareas/2026-11-22-panel-raspberry-arreglos.md T-16`; `py -3 -m pytest raspberry-panel/tests`
- **Riesgo y autorización:** ninguno de borrado. Órdenes: `py -3 -m pytest`, `py -3 tools/tdd.py`.
- **Notas:** `startAnimation` y `testPanels` siguen tragándose `KeyboardInterrupt` por dentro: no se toca (RS-2). Con `Restart=always` systemd relanza a los 10 s con cualquier código.
- **Ejecución:** —

### T-17 · Convertir toda imagen a RGB sobre negro

- **Requisitos:** RF-10
- **Objetivo:** toda imagen que sale de `Animation` está en modo RGB, con la transparencia compuesta sobre negro (DA-6, RN-4).
- **Archivos:** modificar `raspberry-panel/panel/Animation.py` (una función privada de normalización, aplicada al empezar `generateFrames` y a cada frame de `loadAnimatedGif`) · no tocar `colourTuple` ni `AnimationServer.py`
- **Hecho cuando:**
  - [ ] Un PNG de paleta de 408×18 genera 73 frames en modo RGB y `startAnimation` los pinta sin excepción.
  - [ ] Un PNG RGBA con un píxel rojo totalmente transparente deja ese LED apagado.
  - [ ] Un GIF de 1 frame en modo paleta genera frames RGB, y un GIF animado con transparencia compone sus frames sobre negro.
  - [ ] Las huellas de `banner1.png` a `banner12.png` de T-12 y C-1 a C-4 pasan sin tocarlas; si una huella difiere, se para y se pregunta al usuario antes de seguir (RN-4).
- **Pruebas:** tdd
- **Verificación:** unitaria · `py -3 tools/tdd.py verde doc/tareas/2026-11-22-panel-raspberry-arreglos.md T-17`; `py -3 -m pytest raspberry-panel/tests`
- **Riesgo y autorización:** cambia lo que se ve con transparencias: aceptado por el usuario (PA-3, RN-4). Las huellas de T-12 son la comprobación de que las 12 pancartas no cambian. Órdenes: `py -3 -m pytest`, `py -3 tools/tdd.py`.
- **Notas:** `Panel.py` y `colourTuple` no se tocan (RN-12). El PNG de paleta de las pruebas se sintetiza en `tmp_path`.
- **Ejecución:** —

### T-18 · Mostrar un GIF no animado como imagen estática

- **Requisitos:** RF-7
- **Objetivo:** un `.gif` de un solo frame que cabe en el panel se muestra como una imagen estática, `repeticiones` veces (DA-7, RN-9).
- **Archivos:** modificar `raspberry-panel/panel/Animation.py` · no tocar `AnimationServer.py`
- **Hecho cuando:**
  - [ ] Un `.gif` de 48×18 o menor y de 1 frame genera 1 frame, con `is_animated` = False y duración `velocidad` × 1000 ms (250 ms).
  - [ ] El frame se pinta arriba a la izquierda y se repite `repeticiones` veces, no `repeticiones_gif`.
  - [ ] Un GIF animado se reproduce igual que antes, con `repeticiones_gif`.
- **Pruebas:** tdd
- **Verificación:** unitaria · `py -3 tools/tdd.py verde doc/tareas/2026-11-22-panel-raspberry-arreglos.md T-18`; `py -3 -m pytest raspberry-panel/tests`
- **Riesgo y autorización:** ninguno de borrado. Órdenes: `py -3 -m pytest`, `py -3 tools/tdd.py`.
- **Notas:** un GIF no animado se trata como un PNG: la pasa por `generateFrames`, que ya lo normaliza (T-17). Se ve 250 ms × `repeticiones` (confirmado por el usuario, PQ-4; riesgo RG-6). Un GIF no animado mayor que el panel lo cubre T-19.
- **Ejecución:** —

### T-19 · Reducir al panel los GIF mayores

- **Requisitos:** RF-8
- **Objetivo:** un GIF, animado o no, mayor que el panel se reduce hasta caber, en la esquina superior izquierda (DA-7, RN-3).
- **Archivos:** modificar `raspberry-panel/panel/Animation.py` (`loadFile` y `loadAnimatedGif`) · no tocar `AnimationServer.py`
- **Hecho cuando:**
  - [ ] Con panel de 48×18, un GIF de 100×100 da frames de 18×18, uno de 100×40 da 45×18 y uno de 100×37 da 48×18.
  - [ ] Un GIF de 30×10 o de 48×18 no se toca.
  - [ ] Todos los frames de un GIF tienen el mismo tamaño final, calculado una vez con el tamaño del GIF (`s = min(ancho_total/w, altura_total/h)`, lados redondeados y limitados a `[1, ancho_total] × [1, altura_total]`), con el filtro `Image.Resampling.NEAREST`.
  - [ ] Un GIF animado se procesa frame a frame (normaliza, ajusta y guarda), sin guardar frames a tamaño original, y un GIF no animado mayor se reduce igual.
  - [ ] Los PNG no se reducen: siguen RN-1.
- **Pruebas:** tdd
- **Verificación:** unitaria · `py -3 tools/tdd.py verde doc/tareas/2026-11-22-panel-raspberry-arreglos.md T-19`; `py -3 -m pytest raspberry-panel/tests`
- **Riesgo y autorización:** cambia lo que se ve con GIF grandes: aceptado por el usuario (PA-1 del análisis). Órdenes: `py -3 -m pytest`, `py -3 tools/tdd.py`.
- **Notas:** `Image.Resampling` exige Pillow ≥ 9.1 en la Pi. Requisito previo (PA-2, DT-16): antes de empezar, el usuario pasa la salida de `/home/pi/venv/bin/python3 --version` y `/home/pi/venv/bin/python3 -c "import PIL; print(PIL.__version__)"`, que se anota en el apartado 7 de la nota F0-bis de `doc/decisiones-arquitectura.md`; si Python < 3.11 o Pillow < 9.1, la tarea queda `bloqueada` y se pregunta al usuario. NEAREST porque no crea colores que no estén en el GIF. Un GIF no animado reducido sigue por `generateFrames` como un PNG y da 1 frame con `repeticiones`.
- **Ejecución:** —

### T-20 · Limitar el pintado a los límites del panel

- **Requisitos:** RF-8
- **Objetivo:** `startAnimation` no escribe ningún LED con un píxel fuera del panel (DA-8, RN-8).
- **Archivos:** modificar `raspberry-panel/panel/AnimationServer.py` · no tocar `Animation.py`
- **Hecho cuando:**
  - [ ] `startAnimation` recorre solo `0 ≤ x < min(frame.width, ancho_total)` y `0 ≤ y < min(frame.height, altura_total)`, y sustituye a la comprobación `matrix_index < len(panel.matriz)`.
  - [ ] Con un frame de 100×100 sintético sobre un panel de 48×18, ningún píxel con `x ≥ 48` o `y ≥ 18` llega a un LED, y el píxel `(47, 0)` sí llega a `matriz[47]`.
  - [ ] C-4 pasa sin tocarla.
- **Pruebas:** tdd
- **Verificación:** unitaria · `py -3 tools/tdd.py verde doc/tareas/2026-11-22-panel-raspberry-arreglos.md T-20`; `py -3 -m pytest raspberry-panel/tests`
- **Riesgo y autorización:** toca el único punto que escribe LEDs (zona frágil con C-4 hecha en T-11). Órdenes: `py -3 -m pytest`, `py -3 tools/tdd.py`.
- **Notas:** es la segunda defensa de RF-8: aunque T-19 reduzca los GIF, un frame mayor por otro camino no debe desbordar.
- **Ejecución:** —

### T-21 · Traducir los errores de carga de imágenes

- **Requisitos:** RF-9
- **Objetivo:** un archivo que no se puede cargar lanza `ImageLoadError` con la ruta y la causa original, y un GIF roto se descarta entero (DA-5).
- **Archivos:** modificar `raspberry-panel/panel/Animation.py` (definir `ImageLoadError(Exception)`; `loadFile` cambia su `except:` por `except Exception as err: raise ImageLoadError(f"{ruta}: {type(err).__name__}: {err}") from err`; `loadAnimatedGif` deja de capturar errores) · no tocar `LedMatrixAnimation.py`
- **Hecho cuando:**
  - [ ] Un `.png` con contenido corrupto lanza `ImageLoadError` cuyo mensaje es `«<ruta>: <TipoOriginal>: <mensaje>»` y cuyo `__cause__` es la excepción original.
  - [ ] Un `.gif` truncado o corrupto lanza `ImageLoadError` y no entrega frames parciales.
  - [ ] Un archivo de longitud 0 lanza `ImageLoadError`.
  - [ ] Ninguna imagen válida de las de DE-4 a DE-5 (modos `1`, `L`, `LA`, `P`, `P` con transparencia, `RGB` y `RGBA`; GIF de 1 frame y animados, menores, iguales y mayores que el panel) lanza `ImageLoadError`.
- **Pruebas:** tdd
- **Verificación:** unitaria · `py -3 tools/tdd.py verde doc/tareas/2026-11-22-panel-raspberry-arreglos.md T-21`; `py -3 -m pytest raspberry-panel/tests`
- **Riesgo y autorización:** cambia el comportamiento de un GIF roto (hoy muestra los frames ya leídos): aceptado por el usuario (PA-2 del análisis y decisión del 2026-11-22). El `except Exception` traductor es una excepción razonada a `python-basico` aceptada el 2026-11-22 (PQ-7). Órdenes: `py -3 -m pytest`, `py -3 tools/tdd.py`.
- **Notas:** hasta T-22, un archivo roto sigue tumbando el bucle (como hoy, ahora con mejor mensaje). La última condición hace visible un fallo de programación de la carga que esta captura escondería (AC-4).
- **Ejecución:** —

### T-22 · Omitir los archivos que no cargan

- **Requisitos:** RF-9
- **Objetivo:** el bucle registra la causa de un archivo que no carga y sigue con el siguiente, sin que el servicio caiga (DA-5, RN-5).
- **Archivos:** modificar `raspberry-panel/panel/LedMatrixAnimation.py` (`MainClass.start`) · no tocar `Animation.py`
- **Hecho cuando:**
  - [ ] Solo la construcción de `Animation` va dentro de `try … except ImageLoadError`, que llama a `logger.exception` y pasa al siguiente archivo.
  - [ ] Dado un `.png` corrupto y un `.gif` truncado entre dos archivos válidos, el log tiene una línea ERROR por cada uno, con la ruta, el tipo y el mensaje originales, y los dos válidos se reproducen.
  - [ ] Un fallo de la tira (`startAnimation`) no se captura y llega a `main()`.
- **Pruebas:** tdd
- **Verificación:** unitaria · `py -3 tools/tdd.py verde doc/tareas/2026-11-22-panel-raspberry-arreglos.md T-22`; `py -3 -m pytest raspberry-panel/tests`
- **Riesgo y autorización:** ninguno de borrado. Órdenes: `py -3 -m pytest`, `py -3 tools/tdd.py`.
- **Notas:** «se reproduce» = se carga sin error, con al menos 1 frame, y se entrega a `startAnimation` o `startAnimationTest`, haya hardware o no (RN-5). Un archivo roto deja una traza en cada vuelta (RG-8).
- **Ejecución:** —

### T-23 · Esperar cuando una vuelta no reproduce ningún archivo

- **Requisitos:** RF-9
- **Objetivo:** si una vuelta completa no reproduce ningún archivo, se registra 1 ERROR y se espera 10 s antes de repetir, en lugar de girar al 100 % de CPU (RN-5).
- **Archivos:** modificar `raspberry-panel/panel/LedMatrixAnimation.py` (constante con nombre para los 10 s y `time.sleep` a través del módulo `time`) · no tocar otros módulos
- **Hecho cuando:**
  - [ ] Con un directorio vacío, inexistente o con todos los archivos rotos, cada vuelta deja 1 ERROR que nombra el directorio y si existe, y llama a `time.sleep` con 10 s.
  - [ ] Tras la espera se repite la misma lista de archivos, sin volver a buscar en el directorio.
  - [ ] Una vuelta que reproduce al menos un archivo no espera.
- **Pruebas:** tdd
- **Verificación:** unitaria · `py -3 tools/tdd.py verde doc/tareas/2026-11-22-panel-raspberry-arreglos.md T-23`; `py -3 -m pytest raspberry-panel/tests`
- **Riesgo y autorización:** ninguno de borrado. Órdenes: `py -3 -m pytest`, `py -3 tools/tdd.py`.
- **Notas:** los 10 s igualan `RestartSec` de systemd. El Probador dobla `time.sleep` por el módulo `time` (contrato de DA-13).
- **Ejecución:** —

### T-24 · Admitir cualquier número de paneles

- **Requisitos:** RF-11
- **Objetivo:** `testPanels` y el contador de LEDs encendidos funcionan con cualquier número de paneles, sin `IndexError` (DA-9, RN-6).
- **Archivos:** modificar `raspberry-panel/panel/AnimationServer.py` · no tocar `Panel.py`
- **Hecho cuando:**
  - [ ] Con 3 paneles horizontales × 2 verticales (6 paneles), `testPanels` y `startAnimation` no lanzan `IndexError`.
  - [ ] Cada panel se enciende 2 s con el color `colores[n % 4]` (rojo, verde, azul, amarillo, y vuelta a empezar) y su nombre con el mismo índice.
  - [ ] El log da los LEDs encendidos de los 6 paneles, y el contador tiene un elemento por panel (`paneles_horizontal × paneles_vertical`).
  - [ ] Con 2 paneles, el panel 0 es rojo y el 1 verde, como hoy.
- **Pruebas:** tdd
- **Verificación:** unitaria · `py -3 tools/tdd.py verde doc/tareas/2026-11-22-panel-raspberry-arreglos.md T-24`; `py -3 -m pytest raspberry-panel/tests`
- **Riesgo y autorización:** ninguno de borrado. Con 2 paneles, la línea «Frame 0 - LEDs encendidos por panel» lista P0 y P1 en vez de P0 a P3 (cambio de log aceptado, DA-9). Órdenes: `py -3 -m pytest`, `py -3 tools/tdd.py`.
- **Notas:** SP-3: con más de 4 paneles los colores se repiten cíclicamente. La prueba de 6 paneles es solo automática: la Pi tiene 2 paneles.
- **Ejecución:** —

### T-25 · Leer la configuración de la carpeta del código

- **Requisitos:** RF-12, RF-18
- **Objetivo:** el panel lee `configuracion.json` de su propia carpeta, en la Pi y en PC (DA-10), y el modo simulación con `DEBUG` = 0 completa 2 vueltas.
- **Archivos:** modificar `raspberry-panel/panel/Config.py` · no tocar `configuracion.json` ni sus valores (`directorio` sigue siendo `/home/pi/ficheros`)
- **Hecho cuando:**
  - [ ] `Config` abre `os.path.join(os.path.dirname(os.path.abspath(__file__)), jsonfile)`; una ruta absoluta en `jsonfile` se usa tal cual; firma y claves no cambian.
  - [ ] Si falta el archivo, `FileNotFoundError` nombra la ruta buscada.
  - [ ] En Windows, sin librerías de hardware y con un `configuracion.json` local cuyo `directorio` existe, con `DEBUG` = 0 el programa completa 2 vueltas (cada archivo aparece 2 veces con «preparamos imagen» en el log), no escribe en ningún LED y no lanza excepción.
- **Pruebas:** tdd
- **Verificación:** unitaria · `py -3 tools/tdd.py verde doc/tareas/2026-11-22-panel-raspberry-arreglos.md T-25`; `py -3 -m pytest raspberry-panel/tests`
- **Riesgo y autorización:** cambia de dónde se lee la configuración; en `/home/pi/panel` es el mismo archivo que hoy. Órdenes: `py -3 -m pytest`, `py -3 tools/tdd.py`.
- **Notas:** en PC se trabaja sobre una copia de `raspberry-panel/panel/` fuera del repositorio con su propio `configuracion.json`; la prueba lo hace en `tmp_path`. La ventana de `DEBUG` = 1 se comprueba a mano en UAT-18. RS-3: no cambian las rutas `/home/pi/...`.
- **Ejecución:** —

### T-26 · Cambiar el usuario de panel.service a pi

- **Requisitos:** RF-12
- **Objetivo:** `panel.service` arranca el panel con el usuario `pi`, el que lo ejecuta en la Pi (Z-8).
- **Archivos:** modificar `raspberry-panel/panel/panel.service` (solo `User=owner` a `User=pi`) · no tocar el resto del archivo
- **Hecho cuando:**
  - [ ] `panel.service` dice `User=pi`.
  - [ ] `ExecStartPre` de 4 s, `Restart=always` y `RestartSec=10` no han cambiado (RNF-5).
- **Pruebas:** no aplica: archivo de configuración sin lógica
- **Verificación:** manual · `git diff --ignore-cr-at-eol -- raspberry-panel/panel/panel.service` muestra solo ese cambio; el usuario comprueba en la Pi `systemctl show panel -p User` (UAT-17)
- **Riesgo y autorización:** cambia el usuario del servicio: antes de instalarlo en la Pi se comprueba que hoy corre con `pi` (si no, se para y se pregunta); lo hace el usuario (RS-5).
- **Notas:** confirmado por el usuario el 2026-11-22 (P-2, PA-7). Requisito previo (PA-2, DT-16): antes de empezar, el usuario pasa la salida de `systemctl show panel -p User`, que se anota en el apartado 7 de la nota F0-bis; si no da `pi`, la tarea queda `bloqueada` y se pregunta.
- **Ejecución:** —

### T-27 · Crear el servicio de apagado

- **Requisitos:** RF-15
- **Objetivo:** el servicio que ejecuta `apagado.sh` al encender la Pi está en el repositorio (DA-11).
- **Archivos:** crear `raspberry-panel/panel/apagado.service` · no tocar `apagado.sh`
- **Hecho cuando:**
  - [ ] El archivo define `Type=simple`, `User=pi`, `ExecStart=/bin/bash /home/pi/panel/apagado.sh` y `WantedBy=multi-user.target`.
  - [ ] Un comentario dice que el archivo está reconstruido y no copiado de la Pi.
- **Pruebas:** no aplica: archivo de configuración sin lógica
- **Verificación:** manual · lectura del archivo contra los cuatro valores; el usuario lo valida en la Pi (UAT-15, RS-5)
- **Riesgo y autorización:** servicio reconstruido sin el original (RI-4): no se puede probar sin la Pi. Si en la Pi ya existe el servicio original con otro nombre, habría dos apagados (RG-12): lo comprueba el usuario al instalar.
- **Notas:** `apagado.sh` usa `sudo shutdown` y apaga a las 5 h; no se cambia. Con `/bin/bash` explícito no depende del bit de ejecución. Requisito previo (PA-2, DT-16): antes de empezar, el usuario pasa la salida de `systemctl list-unit-files` (buscar un apagado ya existente) y `sudo -l`, que se anota en el apartado 7 de la nota F0-bis; si ya existe un servicio de apagado, la tarea queda `bloqueada` y se pregunta.
- **Ejecución:** —

### T-28 · Declarar las dependencias de ejecución

- **Requisitos:** RF-14
- **Objetivo:** `raspberry-panel/panel/requirements.txt` declara lo que el panel necesita en la Pi (DA-12).
- **Archivos:** crear `raspberry-panel/panel/requirements.txt` · no tocar `requirements-dev.txt`
- **Hecho cuando:**
  - [ ] El archivo contiene `Pillow>=9.1`, `adafruit-circuitpython-neopixel`, `adafruit-blinka` y `rpi_ws281x`, sin versiones fijas salvo Pillow.
  - [ ] Un comentario de cabecera dice «Python 3.11 o superior».
- **Pruebas:** no aplica: declaración de dependencias
- **Verificación:** manual · lectura del archivo; el usuario instala en un venv nuevo de la Pi y el panel arranca (UAT-14)
- **Riesgo y autorización:** instalar en la Pi lo hace el usuario (red). Las versiones de las librerías de la Pi se comprueban al desplegar (SP-4, RI-8).
- **Notas:** `rpi_ws281x` no se instala en Windows: por eso no figura en `requirements-dev.txt`.
- **Ejecución:** —

### T-29 · Fijar los finales de línea LF de los servicios

- **Requisitos:** RF-12, RF-15
- **Objetivo:** `apagado.sh`, `panel.service` y `apagado.service` salen siempre con finales LF, también al copiarlos desde Windows (DA-15).
- **Archivos:** crear `.gitattributes` en la raíz con `*.sh text eol=lf` y `*.service text eol=lf` · renormalizar con `git add --renormalize` los tres archivos de `raspberry-panel/panel/` · no tocar su contenido
- **Hecho cuando:**
  - [ ] `.gitattributes` contiene esas dos líneas.
  - [ ] `git ls-files --eol` da `i/lf` en los tres archivos.
  - [ ] `git diff --ignore-cr-at-eol` no muestra cambios de contenido en esos archivos.
- **Pruebas:** no aplica: configuración de git sin comportamiento
- **Verificación:** manual · `git ls-files --eol -- raspberry-panel/panel/apagado.sh raspberry-panel/panel/panel.service raspberry-panel/panel/apagado.service`; `git diff --ignore-cr-at-eol --stat`
- **Riesgo y autorización:** `git add --renormalize` cambia los bytes de `apagado.sh` y `panel.service`: el diff parece un cambio de contenido y no lo es (RG-16). Órdenes: `git add`, `git ls-files`. Si T-01 dio `i/lf` en `apagado.sh` y `panel.service`, solo se renormaliza lo que haga falta.
- **Notas:** va en los arreglos y no en la reorganización porque RF-4 solo admite renombrados en esas fases (PQ-6). Un archivo nuevo en la raíz: `.gitattributes`.
- **Ejecución:** —

### T-30 · Escribir el README de despliegue de raspberry-panel

- **Requisitos:** RF-12, RF-14, RF-15
- **Objetivo:** el README de `raspberry-panel/` permite reinstalar el panel y su apagado en una Pi limpia solo con el repositorio.
- **Archivos:** modificar `raspberry-panel/README.md` (creado en T-14, conserva su línea de versión) · no tocar el código
- **Hecho cuando:**
  - [ ] Describe copiar `raspberry-panel/panel/` a `/home/pi/panel` y los PNG y GIF del primer nivel de `ficheros/` a `/home/pi/ficheros`, crear el venv con `requirements.txt`, e instalar las dos unidades (con `daemon-reload` y `enable`).
  - [ ] Pide comprobar antes `/home/pi/venv/bin/python3 --version` (3.11 o superior; si no, se para y se pregunta), buscar un servicio de apagado ya existente con `systemctl list-unit-files`, y comprobar que `apagado.sh` y las dos unidades llegan con finales LF.
  - [ ] Explica el permiso de `shutdown`: comprobar `sudo -l` como `pi`; si ya tiene `NOPASSWD: ALL` no se toca sudoers; si no, una línea con `visudo` limitada a `shutdown`, y dice que `apagado.service` está reconstruido, no copiado de la Pi.
  - [ ] Explica consultar el log con `journalctl -u panel` y `animation_panel.log`, trabajar en PC sobre una copia de `panel/` fuera del repositorio con su propio `configuracion.json`, y instalar `requirements-dev.txt` y lanzar `py -3 -m pytest raspberry-panel/tests`.
  - [ ] Recomienda guardar `pip freeze` del venv de la Pi como registro, sin fijar nada.
- **Pruebas:** no aplica: documentación
- **Verificación:** manual · lectura contra los cinco apartados; las rutas que cita existen
- **Riesgo y autorización:** ninguno
- **Notas:** la línea exacta de sudoers y la ruta de `shutdown` (`/sbin` o `/usr/sbin`) las valida el usuario en la Pi (RG-5). Con `autorizar_todo` no se cambia nada de sudoers desde el repositorio.
- **Ejecución:** —

### T-31 · Escribir el README de la raíz

- **Requisitos:** RF-16
- **Objetivo:** el `README.md` de la raíz describe el repositorio reorganizado con sus dos productos.
- **Archivos:** crear o sustituir `README.md` de la raíz · no tocar `LICENSE`
- **Hecho cuando:**
  - [ ] Describe los dos productos (`esp32/` y `raspberry-panel/`), la estructura del repositorio y `archivo/` con su regla.
  - [ ] Da la orden `pio run -d esp32` y remite al README de `raspberry-panel/` para desplegar la Pi.
  - [ ] Enlaza a `doc/diseno/` y menciona que `LICENSE` es GPL v3 y el README del ESP32 decía MIT (solo se documenta).
  - [ ] Todos los enlaces relativos existen.
- **Pruebas:** no aplica: documentación
- **Verificación:** manual · se abre cada enlace relativo del README
- **Riesgo y autorización:** ninguno
- **Notas:** el README raíz anterior se sustituye; lo que dijera del ESP32 está en `esp32/README.md` (T-34). El README no es una segunda memoria de decisiones: enlaza a `doc/decisiones-arquitectura.md`.
- **Ejecución:** —

### T-32 · Escribir el README de archivo

- **Requisitos:** RF-3, RF-16
- **Objetivo:** `archivo/README.md` dice qué hay en `archivo/`, su regla y cómo recuperarlo.
- **Archivos:** crear `archivo/README.md` · no tocar el resto de `archivo/`
- **Hecho cuando:**
  - [ ] Dice el origen (`navidad/`, banners antiguos y el log de diciembre de 2025) y la regla («lo único que no tenía copia; no se borra sin decisión del usuario»).
  - [ ] Dice cómo recuperarlo con `git show <commit>:<ruta>` usando la línea base `f25ee46`, y que lo que solo existía en `e23949d` se da por perdido.
  - [ ] Sus rutas existen.
- **Pruebas:** no aplica: documentación
- **Verificación:** manual · se abren las rutas que cita
- **Riesgo y autorización:** ninguno
- **Notas:** decidir si las imágenes de `archivo/` se borran queda para más adelante, del usuario.
- **Ejecución:** —

### T-33 · Actualizar el documento de diseño del panel

- **Requisitos:** RF-16
- **Objetivo:** `doc/diseno/panel-raspberry.md` y `doc/diseno/indice.md` reflejan las rutas nuevas y los defectos arreglados como resueltos.
- **Archivos:** modificar `doc/diseno/panel-raspberry.md` y `doc/diseno/indice.md`, que escribe el `ingeniero-inverso` por encargo del Orquestador (DT-14; programador-python no puede escribir ahí y solo verifica rutas y enlaces y marca la tarea) · no tocar el resto de `doc/`
- **Hecho cuando:**
  - [ ] Las rutas `panel/` y `ficheros/` pasan a `raspberry-panel/panel/` y `raspberry-panel/ficheros/`, y sus enlaces existen.
  - [ ] Z-1, Z-2, Z-3, Z-4, Z-5, Z-7, Z-8, Z-9, Z-11 y Z-12 figuran como resueltos, con la tarea que los arregló; Z-6, Z-10 y Z-13 siguen abiertos.
  - [ ] Las pruebas de caracterización C-1 a C-4 figuran como `hecha`.
- **Pruebas:** no aplica: documentación
- **Verificación:** manual · se abren las rutas y se compara cada Z-n con su tarea
- **Riesgo y autorización:** ninguno
- **Notas:** la ruta de salida del log de `Panel`, `LOGGING_CONFIG` y los demás cambios de comportamiento (transparencia, GIF reducido, GIF roto descartado) se describen como el nuevo estado.
- **Ejecución:** —

### T-34 · Ajustar el README del ESP32 a su carpeta

- **Requisitos:** RF-16
- **Objetivo:** `esp32/README.md` queda desenvuelto del bloque de código y con sus órdenes ajustadas a `esp32/`, sin cambiar su contenido técnico.
- **Archivos:** modificar `esp32/README.md` · no tocar `esp32/src`, `data` ni `platformio.ini`
- **Hecho cuando:**
  - [ ] El README ya no está envuelto en un bloque de código.
  - [ ] Sus órdenes usan `esp32/` (`pio run -d esp32 -e esp32dev`) y sus enlaces relativos existen.
  - [ ] El contenido técnico (pines, versión, funciones) no cambia.
- **Pruebas:** no aplica: documentación
- **Verificación:** manual · `git diff -- esp32/README.md` muestra solo el desenvuelto y las rutas
- **Riesgo y autorización:** ninguno
- **Notas:** al abrir la raíz, PlatformIO IDE deja de ver el proyecto: abrir `esp32/` o usar `pio run -d esp32`; el README lo dice. El firmware no se versiona en esta tanda. Su commit va con la documentación de T-31 a T-33 o sigue C2 (DT-13), y no sube la versión del panel.
- **Ejecución:** —

## Bitácora

- **2026-11-23 · Aprobación.** El usuario aprueba el documento («Aprobado»). Autoriza para todo el documento: los `git commit` de T-02 a T-07 (uno por tarea, solo con sus rutas). No autoriza por adelantado: `git mv`/`git rm`/`rmdir` de la reorganización, `pio run` (T-05) ni la ampliación de la excepción C2 (PA-1): se piden al llegar a su tarea. Carpeta fuera de OneDrive: no hace falta pausar sincronización. Avisos de `check_tareas.py` sobre T-01, T-14 y T-19 «inexistentes»: falsos positivos (las tareas existen).
- **2026-11-23 · Autorización general.** El usuario: «adelante con todas las tareas sin autorizaciones». Se entiende autorizado de forma expresa para todo el documento: `git commit` por tarea, `git mv`/`git rm`/`rmdir` de la reorganización según la lista vigente de T-01, `pio run` (T-05) y la ampliación de la excepción C2 a F2 y T-34 (PA-1). No cubre lo que el arnés pregunta siempre (borrar, `git commit`, instalar, red): esas preguntas las hace el arnés y no se rodean. Siguen necesitando al usuario: datos de la Pi (PA-2), crear `.agentes/version.json` antes de F3 y la UAT de F6.
- **2026-11-23 · Refaseo.** El criterio 5 de T-01 (datos de la Pi, PA-2) pasa a T-19, T-26 y T-27, para no parar la reorganización (Faseador).
- **2026-11-23 · Cierre de F0.** Fase intermedia. T-01 hecha (nota F0-bis en `doc/decisiones-arquitectura.md`: 133 eliminados, 12 `.pyc`, 104 a archivar, 52 a conservar; C1 cumplida); T-02 hecha (commit `0059118`). (1) Verificar: sin tareas relevantes, no aplica el Cuestionador. (2) Probar: la fase no tiene casos (solo lectura); el plan de pruebas del documento se encarga ahora al Probador (debió encargarse al aprobar). (3) Documentar: la fase no cambia nada del producto; manual, funcional y técnico sin cambios. (5) Desarrollo: la nota F0-bis queda en la memoria de decisiones. Escalera: sin decisiones automáticas (`decision_auto.py resumen --fase F0`).

### 2026-11-23 · Cierre de F0

Entrada con el formato del validador; el detalle está en la línea anterior «Cierre de F0» (las cuatro líneas de arriba no siguen el formato «### AAAA-MM-DD · Hito» y la bitácora solo crece). F0 cerrada: fase intermedia, sin casos; siguiente F1, T-03.

### 2026-11-23 · Cierre de F1

Fase intermedia. T-03 `b7cc635`, T-04 `b70b25d`, T-05 `af2050d`, T-06 `82b5411`, T-07 `f66f0f4`, todas hechas. (1) Verificar: Cuestionador *verificar* F1 conforme con condiciones, 0 bloqueantes; objeción 1 (restos `tools/t04_*`) cerrada con su borrado autorizado; objeción 2 (red y `.pio` de T-05) cerrada: el usuario confirma la red y autoriza borrar la `.pio` de la raíz; objeción 3 resuelta. (2) Probar: plan aprobado (`doc/pruebas/2026-11-23-panel-raspberry-arreglos/plan.md`); informe `informe-2026-11-23-135646.md`: APTO, 10 pasan, PF-08 aplazado (en entrega), 0 defectos. (3) Documentar: manual `doc/usuario/esp32-gif-visualizer.md` verificado (`check_manual.py` 0 avisos); funcional y técnico no se crean en F1 (sin cambio de comportamiento). (5) Desarrollo: grafo pendiente (`graphify update .`, el código cambió de ruta); versión sin subir en F1 (excepción C2). Decisiones del usuario: plantilla de PlatformIO sin rastrear en la raíz se deja. Escalera: sin decisiones automáticas. Siguiente: F2, T-08.

## Cambios

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-11-22 | Creación del documento en estado `borrador` | Encargo del Orquestador, modo fasear |
| 2026-11-22 | Ronda 1 del Cuestionador (1 bloqueante, 6 importantes, 1 menor), las 8 adoptadas: T-33 por el ingeniero-inverso (DT-14); commits con rutas de la tarea (DT-15); listas separadas de `.pyc` y de eliminaciones (T-01, T-03, T-04); entorno de la Pi consultado en F0 (DT-16, PA-2, T-01, T-19, UAT-17); caracterización en `test_caracterizacion_*.py`, congelada con sha256 y encargada primero al Probador (DT-10, T-13); referencia única del log para T-12; PA-1 sobre C2 y `version.json` (DT-13); T-34 sin subir versión. Estado a `cuestionado` | Acta del Cuestionador técnico, ronda 1 |
| 2026-11-22 | Ronda 2 (replicar) aplicada: salto de línea de T-33; T-02 y T-03 coherentes con DT-15; caracterización en `test_caracterizacion_*.py` con `conftest.py` congelado y comprobación de `git log` en la verificación de F3 a F5; PA-1/PA-2 del análisis distinguidas en T-19 y T-21. Sin tercera ronda (máximo dos) | Acta del Cuestionador técnico, ronda 2 |
| 2026-11-23 | Refaseo: se saca de T-01 el criterio 5 (salida de las órdenes de la Pi, PA-2); queda con 4 criterios. PA-2 pasa a bloquear T-19 (Python y Pillow), T-26 (`User`) y T-27 (apagado existente y `sudo -l`) como requisito previo en sus Notas; DT-16 ajustada. No cambian dependencias, estados ni alcance | Encargo del Orquestador, modo refasear: la reorganización no necesita el dato de la Pi |

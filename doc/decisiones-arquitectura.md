# Memoria de decisiones

Registro de las decisiones importantes del repositorio (`proceso-comun.instructions.md`, «Memoria del repositorio»). Las entradas se añaden; no se reescriben las anteriores. Si una decisión sustituye a otra, la nueva lo dice.

---

## 2026-11-14 · Reorganización del repositorio (opción A)

**Estado:** en curso (F0).
**Nivel:** relevante (mueve dos productos, elimina 137 archivos y cambia la estructura del repositorio).
**Propuesto por:** Programador Python, tras dos rondas con el Cuestionador técnico. Autorizado por el usuario el 2026-11-14.

### Decisiones del usuario (2026-11-14)

- Autoriza el plan F0–F7, las 137 eliminaciones (A1–A7, B1–B3), las órdenes por fase y crear `doc/decisiones-arquitectura.md` (C3).
- C2: excepción puntual de versión y fecha para los commits de la reorganización (no cambia ningún producto). `.agentes/version.json` se crea después de F3, en el primer cambio funcional del firmware (propuesta abajo).
- P-R1: sacar `ficheros/iconos/banners/old` de los originales: banner1/7/8/9 → `archivo/banners-antiguos/`; banner2–6 y 10 se eliminan (A1).
- P-R3: sí se elimina el grupo C: los 4 `.pyc` de `navidad/panel/__pycache__/`. Los `.idea/{.gitignore,panel.iml}` de «ficheros navidad/panel» se conservan; `navidad/3/` y `navidad/5/` (vacías, sin rastrear) se quitan con rmdir.
- P-R4: LICENSE es GPL v3 y el README del ESP32 dice MIT: solo se documenta.
- C1 (zonas en `.agentes/politica.json`): la hace el usuario antes de F1.

### Plan final

#### Estructura final

- **raíz:** arnés (`.agentes`, `.claude`, `.github`, `tools`, `doc`, `CLAUDE.md`, `LICENSE`), `README.md` nuevo, `.gitignore`, `.vscode/` (`settings.json` es configuración del arnés para Copilot: se queda).
- **`esp32/`:** `platformio.ini`, `src/`, `data/`, `README.md` (el actual, sin el bloque de código que lo envuelve), `.gitignore` nuevo, `.pio/` sin rastrear.
- **`raspberry-panel/`:** `panel/` (código vigente, sin el log), `ficheros/` (imágenes originales), `README.md` nuevo.
- **`archivo/`:** `README.md` nuevo, `banners-antiguos/banner{1,7,8,9}.png`, `raspberry-panel/animation_panel.log`, `navidad/` (lo único, con sus rutas originales).

`archivo/navidad/` queda con 107 archivos: `1.png`, `2.jpeg`, `3.jpeg`, `4.jpeg`, `5.jpeg`, `6.png`, `7.png`; `1/` (17); `globos/` (3); `ficheros/banner7-1.png` y `ficheros/banner8-1.png`; `ficheros navidad/`: 11 imágenes del juego y `.pdn`, `iconos/` (41) y `panel/.idea/{.gitignore,panel.iml}`; `iconos/todos_capas.pdn` e `iconos/banners/old/{banner7.png, logo.png, Sin título.png}`; `panel/`: el código antiguo (7 archivos), `.idea/` (5) y `__pycache__/` (4) [nota: el usuario autorizó eliminar esos 4 `.pyc`, grupo C].

Cuenta (rastreados en `ficheros/` y `navidad/`): 44 conservados + 107 archivados + 137 eliminados = 288.

El código antiguo de Python va a `archivo/navidad/panel/`, una sola copia; la segunda copia es idéntica en código y se elimina (B3).

En la Pi no cambia nada: rutas absolutas (`/home/pi/panel` en `Config.py:33`, `/home/pi/ficheros` en `configuracion.json`, y las de `panel.service`). El panel solo muestra PNG y GIF del primer nivel de `ficheros/` (`LedMatrixAnimation.py:87-89`).

#### Lista exacta de eliminaciones

137, todas idénticas por sha256 a un archivo que se conserva; rutas de `e23949d`, porque F2 va antes de mover.

**A. Idénticos a un original de `ficheros/` (111):**

- A1 `ficheros/iconos/banners/old/banner{2,3,4,5,6,10}.png` (6) = `ficheros/banner{n}.png`
- A2 `navidad/banner1.png` (1) = `ficheros/banner1.png`
- A3 `navidad/ficheros - copia/banner{2,3,4,5,6,10}.png` (6) = `ficheros/banner{n}.png`
- A4 `navidad/ficheros navidad/banner{2,3,4,5,6,10}.png` (6) = `ficheros/banner{n}.png`
- A5 `navidad/ficheros/banner{1..12}.png` (12) = `ficheros/banner{n}.png`
- A6 `navidad/ficheros/iconos/`: `{1..28}_18px.png`, `todos_capas.pdn`, `banners/{banner1.png, example1.gif, example2.gif}`, `banners/old/banner{2,3,4,5,6,10}.png` (38) = el mismo nombre en `ficheros/iconos/`, o `ficheros/banner{n}.png`
- A7 `navidad/iconos/`: `{1..28}_18px.png`, `banners/{banner1.png, example1.gif, example2.gif}`, `banners/old/banner{1,2,3,4,5,6,8,9,10,11,12}.png` (42); los «old» de esta carpeta son iguales a los vigentes de `ficheros/`

**B. Idénticos a lo que se conserva en `archivo/` (26):**

- B1 de `banner{1,7,8,9}.png` se conserva la copia de `ficheros/iconos/banners/old/` (pasa a `archivo/banners-antiguos/`); se eliminan sus copias en `navidad/ficheros - copia/`, `navidad/ficheros navidad/` y `navidad/ficheros/iconos/banners/old/` (12)
- B2 `navidad/1/2 (20).png` = `navidad/1/2 (15).png` (1)
- B3 en `navidad/ficheros navidad/panel/`: los 5 `.py`, `configuracion.json`, `panel.service`, `.idea/modules.xml`, `.idea/inspectionProfiles/profiles_settings.xml` y `__pycache__/{Animation,AnimationServer,Config,Panel}.cpython-37.pyc` (13) = los de la misma ruta en `navidad/panel/`

**C. No idénticos:** `navidad/panel/__pycache__/*.pyc` (4): **el usuario autorizó eliminarlos**. `navidad/ficheros navidad/panel/.idea/{.gitignore,panel.iml}` (2): se conservan. `navidad/3/`, `navidad/5/` vacías: rmdir.

#### Fases

Un commit por fase; vuelta atrás nunca `git reset --hard`; antes de cada `git restore`, `git status --porcelain -- <rutas de la fase>` debe mostrar solo lo de la fase (C4); tras el commit, `git revert <commit>`.

- **F0 Línea base** (Programador Python): commit de `doc/diseno/*` y del borrado de `navidad/1.bat` (sin cambios del usuario en `.agentes/` ni `tools/`); `pio run -e esp32dev` en HEAD, guardar RAM y flash; manifiesto `git ls-tree -r HEAD` en el scratchpad. Verificación: `git status` solo muestra lo del usuario.
- **F1 `.gitignore` raíz** (Programador Python): añade `__pycache__/`, `*.py[cod]`, `*.log`, `*.log.*`, `.idea/`, `desktop.ini`, `Thumbs.db`; conserva sus 5 líneas; no ignora `*.pdn`; lo rastreado sigue rastreado. Verificación: `git check-ignore -v` y `panel/__pycache__/` deja de aparecer en `git status`. Vuelta atrás: `git restore --staged --worktree -- .gitignore`.
- **F2 Eliminar duplicados** (Programador Python): antes de cada grupo, script de solo lectura que recalcula sha256 de cada par eliminado=conservado y aborta si no coincide; `git rm -- "<rutas>"` grupo a grupo A1 a B3 (y C). Verificación: todos los blobs de `git ls-tree -r e23949d -- ficheros navidad panel` siguen en HEAD salvo `navidad/1.bat` y C. Vuelta atrás: `git restore --staged --worktree -- ficheros navidad`.
- **F3 ESP32 a `esp32/`** (programador-arduino, objeción 2): `mkdir esp32`; `git mv platformio.ini src data README.md esp32/`; crear `esp32/.gitignore` con la plantilla de PlatformIO (`.pio` y las 4 líneas de `.vscode/`, que en la raíz están ancladas y no cubren `esp32/.vscode`); `mv .pio esp32/.pio` para no volver a descargar lib_deps (si PlatformIO no la acepta, la redescarga: es red y se pregunta). Verificación: solo R100 más `A esp32/.gitignore`, y `pio run -d esp32 -e esp32dev` da las mismas RAM y flash que F0. Vuelta atrás: git mv inversos, quitar `esp32/.gitignore`, `mv esp32/.pio .pio`.
- **F4 Raspberry a `raspberry-panel/`** (Programador Python): `mkdir -p raspberry-panel archivo/raspberry-panel`; `git mv panel/animation_panel.log archivo/raspberry-panel/animation_panel.log` (sigue rastreado: `doc/diseno` lo cita como evidencia; en `panel/` cada ejecución lo modificaría); `git mv panel raspberry-panel/panel`; `git mv ficheros raspberry-panel/ficheros`. Verificación: solo R100; `py -3 -m py_compile` de los 5 `.py`; `cd raspberry-panel/panel && py -3 -c "import Config, Panel"` (no se importan los módulos que crean el log); en el primer nivel de `ficheros/` siguen `banner1..12.png`; comprobación de blobs. Vuelta atrás: git mv inversos.
- **F5 Archivar** (Programador Python): `mkdir archivo/banners-antiguos`; `git mv raspberry-panel/ficheros/iconos/banners/old/banner{1,7,8,9}.png archivo/banners-antiguos/`; `git mv navidad archivo/navidad`; rmdir de `3/` y `5/` si siguen. Verificación: solo R100, 107 + 4 + 1 archivos en `archivo/` (menos los 4 `.pyc` del grupo C si ya se eliminaron), comprobación de blobs. Vuelta atrás: git mv inversos.
- **F6 Documentación:** Programador Python: `README.md` raíz (los dos productos, estructura, `pio run -d esp32`, despliegue de la Pi, `archivo/` y su regla, enlaces a `doc/diseno/`, discrepancia de licencia); `raspberry-panel/README.md` (copiar `panel/` a `/home/pi/panel` y los PNG/GIF del primer nivel a `/home/pi/ficheros`, venv, servicio, aviso de Z-8 `User=owner` sin corregirlo); `archivo/README.md` (origen, regla, recuperar con `git show e23949d:<ruta>`); completar `doc/decisiones-arquitectura.md` con el cierre (C3). programador-arduino: desenvolver `esp32/README.md` y ajustar sus órdenes a `esp32/` sin cambiar contenido técnico. Verificación: los enlaces relativos existen.
- **F7 Cierre:** el Ingeniero inverso actualiza las rutas de `doc/diseno/`; `graphify update .` (no existe `graphify-out/`; si no está o falla, es un incumplimiento que decide el usuario); Cuestionador en modo verificar.

**Qué no se toca:** código ni configuración de ejecución de ningún producto (ninguna corrección de Z-n, `User=owner` ni `gif_player.cpp`), el arnés, `.vscode/` de la raíz y `LICENSE`.

#### Versión

Excepción puntual (C2, aprobada). Propuesta de `.agentes/version.json` para el firmware, a crear por el usuario después de F3 (hoy «0.3» no es SemVer y `tools/version.py:134` lo rechaza; normalizar exige editar el firmware, fuera de alcance):

```json
{"changelog": "esp32/CHANGELOG.md", "sitios": [
 {"archivo": "esp32/src/main.cpp", "version": "(FIRMWARE_VERSION\\s*=\\s*\")([^\"]+)"},
 {"archivo": "esp32/src/main.cpp", "version": "(ESP32 Configurator v)(\\d+\\.\\d+(?:\\.\\d+)?)"},
 {"archivo": "esp32/README.md", "version": "(ESP32 GIF Visualizer — v)(\\d+\\.\\d+(?:\\.\\d+)?)"},
 {"archivo": "esp32/data/index.html", "version": "(id=\"versionBadge\"[^>]*>v)([^<]+)"}]}
```

La Pi no tiene versión y el formato solo admite un producto: limitación anotada.

#### Riesgos

1. OneDrive puede bloquear archivos o tenerlos solo en la nube: pausar la sincronización entre F2 y F5.
2. Nombres con espacios y acentos (`ficheros - copia`, `Sin título.png`): rutas entre comillas.
3. VS Code: al abrir la raíz, PlatformIO IDE deja de ver el proyecto; abrir `esp32/` o usar `pio run -d esp32`; al abrir `esp32/` no se carga `.vscode/settings.json` del arnés; se documenta.
4. `doc/diseno` queda con rutas desfasadas hasta F7.
5. El historial sigue pesando (blobs en `e23949d`); aceptado, se descarta purgar.
6. Licencia GPL v3 vs MIT.

#### Alternativas descartadas

- Organizar `archivo/` por tipo: más renombres, se pierde la correspondencia con la tabla de hashes de `indice.md` y con `e23949d`.
- Un solo commit con todo: no verificable ni reversible por partes.
- Sacar el log con `git rm --cached`: es evidencia que cita `doc/diseno`.
- `git filter-repo`: irreversible, nadie lo pidió.
- Dejar `ficheros/` en la raíz: es solo de la Pi (H-1).
- Archivar `navidad/` entera sin eliminar: más simple, pero el usuario pidió eliminar los idénticos.

#### Órdenes por fase

- F0: `git add doc/diseno navidad/1.bat`, `git commit`, `pio run -e esp32dev`, `git ls-tree -r HEAD > <scratchpad>`.
- F1: edición de `.gitignore`, `git add .gitignore`, `git commit`, `git check-ignore -v ...`.
- F2: `py -3 <scratchpad>/verifica_hashes.py` (solo lectura), `git rm -- "<ruta>"` A1–B3 y C, `git commit`, comprobación de blobs con `git ls-tree`.
- F3 (programador-arduino): `mkdir esp32`, `git mv platformio.ini src data README.md esp32/`, crear `esp32/.gitignore`, `mv .pio esp32/.pio`, `pio run -d esp32 -e esp32dev`, `git commit`.
- F4: `mkdir -p raspberry-panel archivo/raspberry-panel`, los 3 git mv, `py -3 -m py_compile raspberry-panel/panel/*.py`, `py -3 -c "import Config, Panel"` en `raspberry-panel/panel`, `git commit`.
- F5: `mkdir archivo/banners-antiguos`, git mv de banner1/7/8/9 y de `navidad`, `rmdir navidad/3 navidad/5`, `git commit`.
- F6: escritura de los 4 README y de `doc/decisiones-arquitectura.md`, `git commit`.
- F7: `graphify update .`.
- Vuelta atrás: `git restore --staged --worktree -- <rutas>` o `git revert <commit>`.

### Acta del Cuestionador técnico

**Ronda 1:** 2 bloqueantes, 3 importantes, 3 menores:

1. `reset --hard` como vuelta atrás [bloqueante].
2. El Programador Python movía el firmware, que no es su zona [bloqueante].
3. Las zonas de escritura del arnés no cubren las rutas nuevas.
4. Commits sin subir versión ni fecha.
5. El grafo no podía quedar pendiente.
6. Faltaba una línea base de compilación.
7. Eliminar después de mover no cuadraba con la lista.
8. Faltaba `*.log.*`.

**Ronda 2 (replicar):** el programador aceptó las 8 y replanteó; las 8 cerradas. **Veredicto:** se sostiene con condiciones:

- C1. Zonas antes de F1: el Cuestionador leyó `.agentes/politica.json` y `tools/guardia.py:649-702`; las órdenes de shell no se comprueban contra las zonas, y con `autorizar_todo: true` un git mv pasaría sin preguntar; `.gitignore` no está en la zona de ningún rol. Añadir zonas o autorizar por escrito los git mv fuera de ellas.
- C2. La excepción de versión la decide el usuario; `version.json` después de F3.
- C3. Crear `doc/decisiones-arquitectura.md`.
- C4. Árbol limpio en las rutas de la fase antes de cada restore.

**Sin verificar:** que PlatformIO acepte libdeps movida; que git mv arrastre el `__pycache__` sin rastrear (se comprueba en F4); la codificación UTF-8 de los sitios de versión; que graphify esté instalado; el Cuestionador no recalculó los hashes.

**Nota:** no se usó el canal `contrato` con programador-arduino (exige referencia T-n y no hay documento de tareas).

### Línea base (F0)

Compilación `pio run -e esp32dev` sobre código igual a `e23949d`: **SUCCESS**.

| Recurso | Uso | Total | % |
|---|---|---|---|
| RAM | 48728 B | 327680 B | 14.9 % |
| Flash | 890553 B | 1310720 B | 67.9 % |

Manifiesto de HEAD tras el commit de F0 (`git ls-tree -r HEAD`): en el scratchpad de la sesión, `manifiesto-F0.txt`. Es temporal: si se pierde, se regenera con `git ls-tree -r` sobre el commit de F0.

### Nota 2026-11-15 · Recuentos corregidos

Los recuentos del plan de 2026-11-14 tenían dos errores; esta nota los corrige y manda sobre ellos (el plan no se reescribe):

- **`archivo/navidad/`:** 103 archivos, no 107 («11 imágenes del juego y `.pdn`» son 11 en total). Como el grupo C (4 `.pyc` de `navidad/panel/__pycache__/`) se elimina en F2, quedan **99**.
- **Eliminaciones:** **141** = 137 (A1–A7, B1–B3) + 4 (C).
- **Verificación de F5:** se esperan **104** archivos en `archivo/` = 99 (`navidad/`) + 4 (`banners-antiguos/`) + 1 (`raspberry-panel/animation_panel.log`).
- La cuenta total del plan (44 + 107 + 137 = 288) queda afectada: con los 4 `.pyc` contados una sola vez, 44 + 99 + 141 = 284. Esta nota no la recalcula contra `e23949d`; la comprobación de blobs de F2 y F5 es la que manda.

### Seguimiento

- **F0: cerrada** (2026-11-15), commit «F0: documentos de diseño y eliminación de navidad/1.bat», hijo de `e23949d` (el hash no puede figurar en el propio commit: `git log --oneline -1 --grep "^F0:"`): `doc/diseno/*`, esta memoria y el borrado de `navidad/1.bat`. Línea base de compilación y manifiesto arriba.
- **Siguiente: F1** (`.gitignore` raíz, Programador Python). **Bloqueada por C1:** antes de F1 el usuario añade a `.agentes/politica.json` las zonas de escritura `.gitignore`, `raspberry-panel/**` y `archivo/**` para `programador-python`, y `esp32/**` para `programador-arduino`. Sin C1 no se empieza F1.
- Los cambios sin preparar del arnés (`.agentes/`, `.claude/settings.json`, `tools/`, `.github/instructions/proceso-comun.instructions.md`) son del usuario y **no entran** en ningún commit de la reorganización. `panel/__pycache__/` (sin rastrear) lo resuelve F1.
- El cierre completo (bloque de cierre, acta de verificación) se añade en F6/F7.

---

## 2026-11-22 · Arquitectura de los arreglos del panel de la Raspberry Pi

**Estado:** aprobada por el usuario el 2026-11-22 («Aprobada»). Sin ronda nueva del Cuestionador tras las respuestas: es un cambio mínimo y lo decidió el usuario.
**Nivel:** relevante.
**Propuesto por:** el Ingeniero de diseño, tras dos rondas con el Cuestionador técnico.
**Documento:** `doc/arquitectura/2026-11-22-panel-raspberry-arreglos.md` (DA-1 a DA-15).
**Análisis:** `doc/analisis/2026-11-22-panel-raspberry-arreglos.md`.

**Relación con decisiones anteriores:**
- Mantiene la reorganización opción A del 2026-11-14, con los ajustes que fijó el análisis: línea base `f25ee46` (`e23949d` ya no existe), paso F0-bis de solo lectura, y F1 saca del índice los 12 `.pyc` con `git rm --cached`.
- La propuesta de `.agentes/version.json` para el ESP32 (2026-11-14, «Versión») queda sustituida: ese archivo lo ocupa ahora el panel (DA-14, RG-15).
- El mínimo de Python pasa de 3.10 o superior (PA-5) a **3.11 o superior** (PQ-1).

### Bloque de cierre

- **Decisión:**
  - **DA-1:** los arreglos van dentro de los 5 módulos planos actuales, sin módulos, capas ni dependencias de ejecución nuevas.
  - **DA-2:** reorganización opción A. En `raspberry-panel/panel/` va solo lo que se despliega; las pruebas y `requirements-dev.txt` quedan fuera.
  - **DA-3:** un único `RotatingFileHandler` en el logger raíz, configurado con `dictConfig` a partir de la constante `LOGGING_CONFIG` de `LedMatrixAnimation.py`. Lleva `disable_existing_loggers: False`, 26 214 400 B, 5 copias, el formato y el nivel de hoy y utf-8. Los módulos solo hacen `getLogger(__name__)`.
  - **DA-4:** `try / except Exception / logger.exception / raise` dentro de `main()`.
  - **DA-5:** `loadFile` traduce cualquier error de carga a `ImageLoadError` con `from`. El bucle solo omite `ImageLoadError`. Si una vuelta no reproduce nada, se registra 1 ERROR y se espera 10 s.
  - **DA-6:** normalización a RGB, con la transparencia compuesta sobre negro.
  - **DA-7:** un GIF mayor que el panel se reduce con NEAREST, frame a frame. Un GIF estático sigue por `generateFrames`.
  - **DA-8:** al pintar, `x` e `y` se limitan al panel.
  - **DA-9:** los colores de la prueba de paneles se repiten con `n % 4` y el contador tiene N paneles.
  - **DA-10:** `configuracion.json` se lee de la carpeta de `Config.py`.
  - **DA-11:** `User=pi` en `panel.service` y un `apagado.service` reconstruido. Sudoers solo se toca si `sudo -l` lo exige.
  - **DA-12:** `panel/requirements.txt` y `requirements-dev.txt`, sin bloquear.
  - **DA-13:** pruebas en `raspberry-panel/tests/` con `monkeypatch`, sin puntos de inyección nuevos.
  - **DA-14:** versión SemVer propia del panel, desde 1.0.0 en el primer commit de arreglos. Constantes `__version__` y `__date__` en `LedMatrixAnimation.py`, línea de versión en el README y `raspberry-panel/CHANGELOG.md`.
  - **DA-15:** `.gitattributes` con `eol=lf` para `*.sh` y `*.service`, y renormalización, en la fase de arreglos.
- **Motivo:** el usuario pidió «solo arreglar» y «lo más simple que funcione». Cada arreglo vive en el módulo que ya tiene esa responsabilidad, no cambia ninguna firma y las pruebas de caracterización C-1 a C-4 siguen valiendo antes y después (AC-1, AC-3).
- **Impacto:**
  - Se corrigen Z-1 a Z-5, Z-7 a Z-9, Z-11 y Z-12.
  - Cambia lo que se ve, con aceptación del usuario: transparencia sobre negro, GIF grande reducido, GIF estático visible y GIF roto descartado entero.
  - Cambia el log: aparecen las trazas de `Panel` y la línea de LEDs por panel lista N paneles.
  - En la Pi hay que hacer `daemon-reload` e instalar el servicio de apagado.
- **Archivos o módulos:**
  - Cambian los 5 `.py` de `raspberry-panel/panel/` y `panel.service`.
  - Se crean `apagado.service`, `requirements.txt`, `raspberry-panel/requirements-dev.txt`, `raspberry-panel/tests/`, `raspberry-panel/README.md`, `raspberry-panel/CHANGELOG.md` y `.gitattributes`.
  - No se tocan `colourTuple`, la creación del NeoPixel, `apagado.sh` ni `configuracion.json`.
- **Documentación:** el documento de arquitectura (`aprobado`) y esta entrada. Los README y el CHANGELOG llegarán en sus tareas.
- **Grafo:** no existe `graphify-out/`; queda pendiente `graphify update .` en F7.
- **Riesgos y seguimiento:**
  - RG-1 a RG-16 del documento.
  - Antes del primer commit de arreglos, el usuario crea `.agentes/version.json`. La propuesta está en la entrega del Ingeniero de diseño del 2026-11-22.
  - Al desplegar se comprueba que Raspberry Pi OS trae Python 3.11 o superior.
  - Siguiente paso: faseo.

### Excepciones a prácticas declaradas (aceptadas por el usuario el 2026-11-22)

- **`python-logging`, rotación diaria (RN-7, RF-13):** la rotación es solo por tamaño, porque con la hora falsa al encender (R-8) la rotación diaria rotaría en cada sesión.
- **`python-logging`, «tamaño y copias en la configuración, nunca en el código» (PQ-5):** van en `LOGGING_CONFIG`, en el punto de entrada. Si se leyeran de `configuracion.json`, no se podría registrar en el log el fallo de esa misma configuración (RF-19). Los valores son 26 214 400 B y 5 copias.
- **`python-proyecto`, «un único `pyproject.toml`» y «dependencias bloqueadas» (PQ-2):** hay dos `requirements*.txt` sin bloquear. Solo se acotan `Pillow>=9.1` y `pytest>=9.2,<10`, y `requires-python` figura como comentario y en el README. Se acepta que la Pi y el PC puedan tener líneas mayores distintas de Pillow (RG-4).
- **`python-basico`, «`except Exception` solo en el borde» (PQ-7):** `Animation.loadFile` captura `Exception` solo para traducirla a `ImageLoadError` con `from`. Así, un fallo de programación de la carga también se convierte en un archivo omitido en ejecución. Las pruebas lo detectan porque exigen que ninguna imagen válida dé `ImageLoadError` (AC-4).

### Alternativas descartadas

- **ALT-2, mantener lo que hay:** no cumple RF-6 a RF-19.
- **ALT-3, paquete `src/` con `pyproject.toml`, capas e inyección de la tira:** va contra AC-1 y AC-3, rompe C-1 a C-4 y obliga a empaquetar en la Pi.
- **ALT-4, normalizar y recortar solo al pintar:** no arregla Z-3 ni RF-9, y el modo `DEBUG` no lo recibiría.
- **Por decisión:**
  - Un gestor por módulo (es Z-7).
  - `log_config.py`.
  - `basicConfig`.
  - Leer la rotación de `configuracion.json`.
  - `sys.excepthook`.
  - `except Exception` en el bucle sin tipo propio.
  - Lista cerrada de excepciones de Pillow.
  - `Image.thumbnail`: crea colores y redondea distinto de RN-3.
  - Recortar el GIF.
  - Leer la configuración del directorio de trabajo o de un argumento.
  - `User=root` para el apagado.
  - `pyproject.toml` con grupos de dependencias.
  - Pruebas dentro de `panel/`.
  - Inyectar la tira por constructor.
  - Versión solo en el README.
  - Solo comprobar LF en el README.

#### Acta de cuestionamiento · 2026-11-22 · Arquitectura de los arreglos del panel de la Raspberry Pi (rondas 1 y 2)

Decisión cuestionada: arreglar Z-1 a Z-5, Z-7 a Z-9, Z-11 y Z-12 dentro de los 5 módulos planos, sin capas ni dependencias de ejecución nuevas, junto con la reorganización opción A (DA-1 a DA-13; DA-14 y DA-15 se añadieron después, con las respuestas del usuario y sin ronda nueva).
Problema que resuelve: el panel pierde trazas (Z-1, Z-7), no muestra o pinta mal algunas imágenes (Z-2 a Z-5), oculta los errores de carga (Z-9), no se puede reinstalar desde el repositorio (Z-8, Z-12) y no se puede probar sin hardware (Z-11).
Mejor argumento a favor: cada arreglo vive en el módulo que ya tiene esa responsabilidad y no cambia ninguna firma, así que C-1 a C-4 valen antes y después. Las pruebas entran por globales que ya existen. El punto de entrada se prueba sin lanzar el script.
Porqués: `disable_existing_loggers: False` es imprescindible, porque los loggers se crean al importar (razonado). Pillow no tiene un conjunto cerrado de errores (razonado). NEAREST no crea colores (documentado). Un `pyproject.toml` exige un backend de construcción o pip 25.1 o superior (razonado, PEP 735). Mínimo privilegio en el apagado: corregido a «no añade privilegios, pero tampoco los limita» (supuesto hasta `sudo -l`).
Alternativas: ALT-1 (elegida), ALT-2, ALT-3 y ALT-4 (descartadas, ver arriba). Además, un `RotatingFileHandler` a mano con `except Exception` en el bucle, sin tipo propio: va contra `python-logging` y contra RF-9.
Intentos de refutación: 1) configurar el log antes de importar para no necesitar `disable_existing_loggers`: obliga a mover los imports, y resiste DA-3; 2) leer la rotación de `configuracion.json`: deja sin log el caso de RF-19, y resiste el diccionario; 3) gestor en el logger raíz a nivel INFO: Pillow emite a DEBUG, y resiste; 4) GIF estático por `generateFrames`: da 1 frame y `repeticiones`, con 100×37 → 48×18, 100×40 → 45×18, 100×100 → 18×18 y 30×10 sin cambio, y resiste; 5) `Image.thumbnail` en lugar de la fórmula propia: crea colores, y resiste DA-7; 6) DA-8 como defensa doble: sustituye una comprobación que ya existe y está mal, y resiste; 7) un solo `requirements.txt` con marcadores de plataforma: no compensa, y resiste DA-12; 8) pruebas sin puntos de inyección: basta construir con `HARDWARE_AVAILABLE` a False y asignar `LedStrip`, y resiste; 9) `raise` sin argumentos conserva traza y código 1, y resiste DA-4; 10) `os.path.join` con una ruta absoluta, y resiste DA-10; 11) `.gitattributes` en la fase de movimiento: rompería RF-4, y se lleva a la fase de arreglos.

| # | Gravedad | Objeción | Solución propuesta | Réplica | Estado | Decisión sobre la solución |
|---|---|---|---|---|---|---|
| 1 | Importante | La configuración del log y el `try/except` dentro de `__main__` no se pueden probar contra la configuración real (RG-1). El `time.sleep` de `LedMatrixAnimation` no estaba en el contrato | `LOGGING_CONFIG` como constante de módulo, el `try/except/raise` dentro de `main()` y el contrato con las pruebas ampliado | Aplicada en DA-3, DA-4, «Interfaces» y RG-1 | resuelta | adoptada |
| 2 | Importante | Tamaño y copias en un literal de código, presentados como si fueran configuración | Declararlo como excepción a `python-logging` y preguntar al usuario | PQ-5; el usuario la aceptó el 2026-11-22 | resuelta | adoptada |
| 3 | Importante | El tipo propio no distingue un error de carga de un fallo de programación dentro de `loadFile`, y la medida de AC-4 dejaba de verse | Corregir el motivo, cambiar la medida de AC-4 y declarar la excepción a `python-basico` | Aplicada en DA-5 y AC-4; PQ-7, aceptada | resuelta | adoptada |
| 4 | Importante | PQ-2 no cubría las dependencias sin bloquear ni `requires-python`, y RG-4 se aceptaba sin decirlo | Ampliar PQ-2, poner `requires-python` como comentario y en el README, y `pip freeze` como registro opcional | Aplicada en PQ-2 y DA-12; aceptada | resuelta | adoptada |
| 5 | Menor | El orden del ajuste del GIF no estaba fijado: se guardaban los frames a tamaño original | En `loadAnimatedGif`, normalizar, ajustar y guardar cada frame; en el GIF estático, ajustar y normalizar una sola vez | Aplicada en DA-7 y RG-14 | resuelta | adoptada |
| 6 | Menor | Se afirmaba un mínimo privilegio que no lo era. CRLF en `apagado.sh` y en `panel.service` | `sudo -l` y `visudo` solo si hace falta; comprobar LF o un `.gitattributes` | Aplicada en DA-11, «Seguridad», RG-5 y RG-13; PQ-6 aceptada, lo que da DA-15 | resuelta | adoptada |
| 7 | Menor | La medida de AC-3 («2 módulos por arreglo») no la cumple DA-3 | Añadir la salvedad de DA-3 a la medida | Aplicada en AC-3 | resuelta | adoptada |
| 8 | Menor | La excepción a `python-basico` no tenía pregunta al usuario | Crear PQ-7 y añadir la salvedad a RS-10 | Aplicada tras la ronda 2; aceptada | resuelta | adoptada |
| 9 | Menor | «Recursos» contradecía DA-7 | Reescribir «Recursos» | Aplicada tras la ronda 2 | resuelta | adoptada |
| 10 | Menor | `.gitattributes` no renormaliza por sí solo lo que ya está en el índice | `git add --renormalize`, con «hecho cuando» `git ls-files --eol` da `i/lf` | Aplicada en PQ-6 y DA-15 | resuelta | adoptada |

Descartadas por falta de solución: RG-2. El WARNING de `AnimationServer.py:28` sale antes de `dictConfig` y no llega al archivo; va por stderr al journal. Configurar el log antes de importar es peor. Queda como riesgo aceptado.
Riesgos aceptados: RG-2 y RG-4 (dependencias sin bloquear).
Veredicto: se sostiene con condiciones. Las condiciones eran las respuestas del usuario a PQ-2, PQ-5 y PQ-7; se cumplieron el 2026-11-22.
Sin verificar:
- Que `resize` en modo P conserve `transparency`. Lo comprueba una prueba de RF-10.
- Que Pillow entregue cada frame de un GIF al tamaño del lienzo. Lo comprueba una prueba de RF-7.
- Si los CRLF están en el índice (`git ls-files --eol` en F0-bis).
- Que systemd tolere CRLF.
- Que exista `010_pi-nopasswd` en la Pi (`sudo -l`).
- Que los loggers de Pillow y de Adafruit no emitan a INFO.
- Que Raspberry Pi OS traiga Python 3.11 o superior.
Verificación de cierre: pendiente (al cerrar la fase de arreglos).
Decide: el usuario (decidido el 2026-11-22: aprobada).

---

## F0-bis · 2026-11-22 · Recuentos de la reorganización sobre `f25ee46`

**Tarea:** T-01 de `doc/tareas/2026-11-22-panel-raspberry-arreglos.md` (RS-7). Ejecutada el 2026-11-23 por el Programador Python, solo lectura. **Manda** sobre los recuentos del plan de 2026-11-14 y de la «Nota 2026-11-15» (que no se reescriben): T-03 a T-07 usan las listas de esta nota.

**Línea base:** `f25ee46` (`f25ee46a93ac02e775ab41a64106c340d63025c1`, «REBASE»), que es HEAD. `e23949d` no existe (RS-6). En `ficheros/`, `navidad/` y `panel/` el árbol de trabajo coincide con la línea base (`git status --porcelain -- ficheros panel navidad` vacío), así que los sha256 se calcularon sobre el disco.

**Método:** `git ls-files -z -- ficheros navidad panel | xargs -0 sha256sum`, agrupando por sha256. Se marcan como supervivientes `ficheros/**` (salvo A1), `navidad/1/2 (15).png` y `navidad/panel/**`, y se comprueba que **cada grupo de sha256 repetido tiene exactamente un superviviente**: se cumple en los 62 grupos repetidos (199 archivos), así que cada eliminado tiene un par idéntico por sha256 que se conserva o se archiva. Excepción ya autorizada: el par de los 4 `.pyc` de B3 son los 4 `.pyc` del grupo C, que también salen del índice.

### 1. Recuento sobre `f25ee46`

Rastreados en `ficheros/` (54), `navidad/` (234) y `panel/` (13): **301**.

| Grupo | Plan | Recalculado | Destino |
|---|---|---|---|
| Eliminar (A1–A7, B1–B3) | 137 | **137** (A 111 + B 26) | 133 con `git rm` en T-04 + 4 `.pyc` de B3 fuera del índice en T-03 |
| Grupo C (`.pyc` de `navidad/panel/__pycache__/`) | 4 | **4** | fuera del índice en T-03, siguen en disco |
| `.pyc` de `panel/__pycache__/` (`cpython-313`) | no estaba | **4** | fuera del índice en T-03, siguen en disco |
| Archivar | 104 | **104** = 99 (`navidad/`) + 4 (`banners-antiguos/`) + 1 (log) | `archivo/` en T-06/T-07 |
| Conservar | 44 (+ código de `panel/`) | **52** = 44 (`ficheros/`) + 8 (`panel/`) | `raspberry-panel/` en T-06 |

Cuadre: 137 + 4 + 4 + 104 + 52 = **301**. Solo `ficheros/` y `navidad/`: 44 + 103 + 141 = **288** (103 = 99 de `navidad/` + 4 de `banners-antiguos/`), que es lo que decía el plan de 2026-11-14.

**Diferencias explicadas:**

- La «Nota 2026-11-15» daba 284 (44 + 99 + 141) porque contaba en «archivados» solo los 99 de `navidad/` y olvidaba los 4 `banner{1,7,8,9}.png` de `ficheros/iconos/banners/old/`, que salen de `ficheros/` hacia `archivo/banners-antiguos/`. Con ellos, 288: no falta ni sobra ningún archivo.
- **Nuevo respecto al plan:** en `f25ee46` están rastreados los 4 `panel/__pycache__/*.cpython-313.pyc` (el plan de 2026-11-14 los daba por sin rastrear). Por eso salen del índice **12** `.pyc`, no 8. No se borran del disco (T-03).
- Recuento por grupo: A1 6, A2 1, A3 6, A4 6, A5 12, A6 38, A7 42, B1 12, B2 1, B3 13. Coincide uno a uno con la «Lista exacta de eliminaciones» del plan.
- Lo que sale del índice en F1: 12 (T-03) + 133 (T-04) = 145 = 141 del plan + 4 `.pyc` de `panel/`.

### 2. Lista 1 · los 12 `.pyc` que salen del índice en T-03 (`git ls-files "*__pycache__*"`)

Salida literal (12, las esperadas; ninguna otra):

```text
navidad/ficheros navidad/panel/__pycache__/Animation.cpython-37.pyc
navidad/ficheros navidad/panel/__pycache__/AnimationServer.cpython-37.pyc
navidad/ficheros navidad/panel/__pycache__/Config.cpython-37.pyc
navidad/ficheros navidad/panel/__pycache__/Panel.cpython-37.pyc
navidad/panel/__pycache__/Animation.cpython-37.pyc
navidad/panel/__pycache__/AnimationServer.cpython-37.pyc
navidad/panel/__pycache__/Config.cpython-37.pyc
navidad/panel/__pycache__/Panel.cpython-37.pyc
panel/__pycache__/Animation.cpython-313.pyc
panel/__pycache__/AnimationServer.cpython-313.pyc
panel/__pycache__/Config.cpython-313.pyc
panel/__pycache__/Panel.cpython-313.pyc
```

Las 4 primeras son las de B3; las 4 siguientes, el grupo C; las 4 últimas, las de `panel/`.

### 3. Lista 2 · los 133 archivos que T-04 elimina con `git rm`

A1 a B3 sin los 4 `.pyc` de B3 (rutas de `f25ee46`; entre paréntesis, el par idéntico por sha256 que se conserva o archiva):

```text
# A1 (6) = ficheros/banner{n}.png
ficheros/iconos/banners/old/banner2.png
ficheros/iconos/banners/old/banner3.png
ficheros/iconos/banners/old/banner4.png
ficheros/iconos/banners/old/banner5.png
ficheros/iconos/banners/old/banner6.png
ficheros/iconos/banners/old/banner10.png
# A2 (1) = ficheros/banner1.png
navidad/banner1.png
# A3 (6) = ficheros/banner{n}.png
navidad/ficheros - copia/banner2.png
navidad/ficheros - copia/banner3.png
navidad/ficheros - copia/banner4.png
navidad/ficheros - copia/banner5.png
navidad/ficheros - copia/banner6.png
navidad/ficheros - copia/banner10.png
# A4 (6) = ficheros/banner{n}.png
navidad/ficheros navidad/banner2.png
navidad/ficheros navidad/banner3.png
navidad/ficheros navidad/banner4.png
navidad/ficheros navidad/banner5.png
navidad/ficheros navidad/banner6.png
navidad/ficheros navidad/banner10.png
# A5 (12) = ficheros/banner{n}.png
navidad/ficheros/banner1.png
navidad/ficheros/banner2.png
navidad/ficheros/banner3.png
navidad/ficheros/banner4.png
navidad/ficheros/banner5.png
navidad/ficheros/banner6.png
navidad/ficheros/banner7.png
navidad/ficheros/banner8.png
navidad/ficheros/banner9.png
navidad/ficheros/banner10.png
navidad/ficheros/banner11.png
navidad/ficheros/banner12.png
# A6 (38) = mismo nombre en ficheros/iconos/ o ficheros/banner{n}.png
navidad/ficheros/iconos/1_18px.png
navidad/ficheros/iconos/2_18px.png
navidad/ficheros/iconos/3_18px.png
navidad/ficheros/iconos/4_18px.png
navidad/ficheros/iconos/5_18px.png
navidad/ficheros/iconos/6_18px.png
navidad/ficheros/iconos/7_18px.png
navidad/ficheros/iconos/8_18px.png
navidad/ficheros/iconos/9_18px.png
navidad/ficheros/iconos/10_18px.png
navidad/ficheros/iconos/11_18px.png
navidad/ficheros/iconos/12_18px.png
navidad/ficheros/iconos/13_18px.png
navidad/ficheros/iconos/14_18px.png
navidad/ficheros/iconos/15_18px.png
navidad/ficheros/iconos/16_18px.png
navidad/ficheros/iconos/17_18px.png
navidad/ficheros/iconos/18_18px.png
navidad/ficheros/iconos/19_18px.png
navidad/ficheros/iconos/20_18px.png
navidad/ficheros/iconos/21_18px.png
navidad/ficheros/iconos/22_18px.png
navidad/ficheros/iconos/23_18px.png
navidad/ficheros/iconos/24_18px.png
navidad/ficheros/iconos/25_18px.png
navidad/ficheros/iconos/26_18px.png
navidad/ficheros/iconos/27_18px.png
navidad/ficheros/iconos/28_18px.png
navidad/ficheros/iconos/todos_capas.pdn
navidad/ficheros/iconos/banners/banner1.png
navidad/ficheros/iconos/banners/example1.gif
navidad/ficheros/iconos/banners/example2.gif
navidad/ficheros/iconos/banners/old/banner2.png
navidad/ficheros/iconos/banners/old/banner3.png
navidad/ficheros/iconos/banners/old/banner4.png
navidad/ficheros/iconos/banners/old/banner5.png
navidad/ficheros/iconos/banners/old/banner6.png
navidad/ficheros/iconos/banners/old/banner10.png
# A7 (42) = mismo nombre en ficheros/iconos/ o ficheros/banner{n}.png
navidad/iconos/1_18px.png
navidad/iconos/2_18px.png
navidad/iconos/3_18px.png
navidad/iconos/4_18px.png
navidad/iconos/5_18px.png
navidad/iconos/6_18px.png
navidad/iconos/7_18px.png
navidad/iconos/8_18px.png
navidad/iconos/9_18px.png
navidad/iconos/10_18px.png
navidad/iconos/11_18px.png
navidad/iconos/12_18px.png
navidad/iconos/13_18px.png
navidad/iconos/14_18px.png
navidad/iconos/15_18px.png
navidad/iconos/16_18px.png
navidad/iconos/17_18px.png
navidad/iconos/18_18px.png
navidad/iconos/19_18px.png
navidad/iconos/20_18px.png
navidad/iconos/21_18px.png
navidad/iconos/22_18px.png
navidad/iconos/23_18px.png
navidad/iconos/24_18px.png
navidad/iconos/25_18px.png
navidad/iconos/26_18px.png
navidad/iconos/27_18px.png
navidad/iconos/28_18px.png
navidad/iconos/banners/banner1.png
navidad/iconos/banners/example1.gif
navidad/iconos/banners/example2.gif
navidad/iconos/banners/old/banner1.png
navidad/iconos/banners/old/banner2.png
navidad/iconos/banners/old/banner3.png
navidad/iconos/banners/old/banner4.png
navidad/iconos/banners/old/banner5.png
navidad/iconos/banners/old/banner6.png
navidad/iconos/banners/old/banner8.png
navidad/iconos/banners/old/banner9.png
navidad/iconos/banners/old/banner10.png
navidad/iconos/banners/old/banner11.png
navidad/iconos/banners/old/banner12.png
# B1 (12) = ficheros/iconos/banners/old/banner{1,7,8,9}.png (pasa a archivo/banners-antiguos/)
navidad/ficheros - copia/banner1.png
navidad/ficheros - copia/banner7.png
navidad/ficheros - copia/banner8.png
navidad/ficheros - copia/banner9.png
navidad/ficheros navidad/banner1.png
navidad/ficheros navidad/banner7.png
navidad/ficheros navidad/banner8.png
navidad/ficheros navidad/banner9.png
navidad/ficheros/iconos/banners/old/banner1.png
navidad/ficheros/iconos/banners/old/banner7.png
navidad/ficheros/iconos/banners/old/banner8.png
navidad/ficheros/iconos/banners/old/banner9.png
# B2 (1) = navidad/1/2 (15).png
navidad/1/2 (20).png
# B3 (9 de 13; los 4 .pyc van en la lista 1) = misma ruta en navidad/panel/
navidad/ficheros navidad/panel/Animation.py
navidad/ficheros navidad/panel/AnimationServer.py
navidad/ficheros navidad/panel/Config.py
navidad/ficheros navidad/panel/LedMatrixAnimation.py
navidad/ficheros navidad/panel/Panel.py
navidad/ficheros navidad/panel/configuracion.json
navidad/ficheros navidad/panel/panel.service
navidad/ficheros navidad/panel/.idea/modules.xml
navidad/ficheros navidad/panel/.idea/inspectionProfiles/profiles_settings.xml
```

Total: 6 + 1 + 6 + 6 + 12 + 38 + 42 + 12 + 1 + 9 = **133**.

### 4. Lo que se archiva (104) y lo que se conserva (52)

- **Archivar, `navidad/` (99):** `1.png`, `2.jpeg`, `3.jpeg`, `4.jpeg`, `5.jpeg`, `6.png`, `7.png` (7); `1/` (17: `1 ({1,6,11,16,21,22,23,24,25}).png` y `2 ({5,10,15,21,22,23,24,25}).png`); `globos/{1,2,3}.png` (3); `ficheros/banner7-1.png`, `ficheros/banner8-1.png` (2); `ficheros navidad/`: `cambiar.png`, `ladron.pdn`, `ladron.png`, `pasar.png`, `premio.png`, `regalo cambio.png`, `regalo robo.png`, `regalo.png`, `robo.png`, `todo.pdn`, `todo.png` (11), `iconos/` (41: `1 ({2,3,4,5,7,8,9,10,12,13,14,15,17,18,19,20}).png`, `2 ({1,2,3,4,6,7,8,9,11,12,13,14,16,17,18,19}).png`, `3 ({1..9}).png`) y `panel/.idea/{.gitignore,panel.iml}` (2); `iconos/todos_capas.pdn` e `iconos/banners/old/{banner7.png, logo.png, Sin título.png}` (4); `panel/`: los 5 `.py`, `configuracion.json`, `panel.service` (7) y `.idea/{.gitignore, inspectionProfiles/profiles_settings.xml, misc.xml, modules.xml, panel.iml}` (5).
- **Archivar, fuera de `navidad/` (5):** `ficheros/iconos/banners/old/banner{1,7,8,9}.png` → `archivo/banners-antiguos/`; `panel/animation_panel.log` → `archivo/raspberry-panel/`.
- **Conservar (52):** `ficheros/banner{1..12}.png` (12), `ficheros/iconos/{1..28}_18px.png` (28), `ficheros/iconos/banners/{banner1.png, example1.gif, example2.gif}` (3), `ficheros/iconos/todos_capas.pdn` (1); `panel/{Animation,AnimationServer,Config,LedMatrixAnimation,Panel}.py`, `panel/apagado.sh`, `panel/configuracion.json`, `panel/panel.service` (8).

Los 4 `.pyc` del grupo C salen del índice en T-03 y siguen en el disco dentro de `navidad/panel/__pycache__/` (sin rastrear); T-07 tiene que tenerlo en cuenta al mover `navidad/`.

### 5. Finales de línea, `.gitignore` y zonas (C1)

`git ls-files --eol -- panel/apagado.sh panel/panel.service`:

```text
i/lf    w/crlf  attr/                 	panel/apagado.sh
i/lf    w/crlf  attr/                 	panel/panel.service
```

En el índice ya están en LF (el CRLF es solo de la copia de trabajo de Windows, sin atributo). T-29 solo tiene que fijar el atributo; no hay que renormalizar el contenido del índice de estos dos.

`.gitignore` actual: **10 líneas** (con CRLF), no 5:

```text
.pio
.vscode/.browse.c_cpp.db*
.vscode/c_cpp_properties.json
.vscode/launch.json
.vscode/ipch
.claude
.github
.agentes
tools
.vscode
```

**C1:** `.agentes/politica.json` da `"escribe": ["**"]` a `programador-python` (línea 157) y a `programador-arduino` (línea 187): condición C1 cumplida. Ojo: `programador-python` tiene en `no_escribe` `tests/**`, `**/test_*.py` y `**/conftest.py` (zona del Probador, DT-10) y las carpetas de `doc/` de otros roles.

### 6. Modo de las pancartas (`Image.open(p).mode`)

**No hay Pillow en este equipo** (`python`, `py -3` (3.15) y `py -3.12` dan `ModuleNotFoundError: No module named 'PIL'`). El registro con Pillow **pasa a T-12**, como dice la ficha.

Dato orientativo, no sustituye al de Pillow: la cabecera IHDR de los PNG (`od` de los bytes 16 a 25) y la ausencia de bloque `tRNS` dan 18 px de alto, 8 bits por canal y tipo de color 2 (RGB) en `banner1-5` y `banner7-12`, y tipo 6 (RGBA) en `banner6`. Anchos: 408 (1, 7, 11), 271 (2), 324 (3), 379 (4), 305 (5), 612 (6, 8, 9, 10), 800 (12). Pillow abriría por tanto 11 en `RGB` y `banner6` en `RGBA`; T-12 lo confirma.

### 7. Pi (PA-2): se completa en T-19, T-26 y T-27

El Faseador sacó de T-01 el criterio de la Pi: la salida de las cinco órdenes de solo lectura de PA-2 (`/home/pi/venv/bin/python3 --version`, `/home/pi/venv/bin/python3 -c "import PIL; print(PIL.__version__)"`, `systemctl show panel -p User`, `systemctl list-unit-files` y `sudo -l`) se registra y se valora en T-19 (Python y Pillow), T-26 (usuario del servicio) y T-27 (servicio de apagado y sudo).

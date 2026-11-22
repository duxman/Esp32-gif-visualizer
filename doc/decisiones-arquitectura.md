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

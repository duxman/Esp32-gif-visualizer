#!/usr/bin/env python3
"""Pruebas funcionales: Panel Raspberry Pi, reorganización y arreglos.

Versión: 1.0.0
Fecha: 2026-11-23 11:25 +01:00
Función: ejecuta los casos PF-n del plan de pruebas funcionales del panel de la Raspberry (F1 programada).

Plan: doc/pruebas/2026-11-23-panel-raspberry-arreglos/plan.md
Programados: PF-01 a PF-10 (F1, reorganización). Los de F2 a F6 se programan al abrir su fase;
mientras tanto, con --hasta-fase F1 quedan «fuera de ámbito».

    py -3 pruebas/funcionales/panel-raspberry-arreglos/run.py --hasta-fase F1 --nivel fase --no-interactivo

Los casos de F1 solo leen el repositorio (índice de git). PF-07 trabaja en una copia temporal y
PF-08 compila con PlatformIO en esp32/.pio (ignorado). Sin secretos.
"""
from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "tools"))
from arnes_pruebas import Bloqueo, Suite  # noqa: E402

PLAN = RAIZ / "doc" / "pruebas" / "2026-11-23-panel-raspberry-arreglos" / "plan.md"
s = Suite("Panel Raspberry Pi: reorganización y arreglos", plan=str(PLAN), salida=str(PLAN.parent))

# Recuentos de la nota F0-bis de doc/decisiones-arquitectura.md, sobre la línea base f25ee46.
BASE_POR_DEFECTO = "f25ee46"
ELIMINADOS, ARCHIVADOS, CONSERVADOS, PYC, TOTAL = 133, 104, 52, 12, 301
PY_PANEL = ["Animation.py", "AnimationServer.py", "Config.py", "LedMatrixAnimation.py", "Panel.py"]
OTROS_PANEL = ["configuracion.json", "panel.service", "apagado.sh"]
CARPETAS_BASE = ("ficheros/", "navidad/", "panel/")
BANNERS_ANTIGUOS = {f"ficheros/iconos/banners/old/banner{n}.png" for n in (1, 7, 8, 9)}
COMPILAR = "import sys\nfor f in sys.argv[1:]:\n    compile(open(f, encoding='utf-8').read(), f, 'exec')\n"
_SHA: dict[str, str] = {}


# --- git, en bruto y sin shell -------------------------------------------------------------
def _git(*args, entrada: bytes | None = None, codigos=(0,)) -> subprocess.CompletedProcess:
    try:
        r = subprocess.run(["git", "-c", "core.quotepath=off", *args], cwd=RAIZ, input=entrada, capture_output=True)
    except FileNotFoundError as e:
        raise Bloqueo("no se encuentra git") from e
    if r.returncode not in codigos:
        raise Bloqueo(f"git {' '.join(args[:3])} falló ({r.returncode}): {r.stderr.decode('utf-8', 'replace')[:200]}")
    return r


def _base(ctx) -> str:
    base = ctx.config.get("base", BASE_POR_DEFECTO)
    _git("cat-file", "-e", f"{base}^{{commit}}")
    return base


def arbol_base(base: str) -> dict[str, str]:
    out = {}
    for e in _git("ls-tree", "-r", "-z", base).stdout.decode("utf-8").split("\0"):
        if e:
            meta, ruta = e.split("\t", 1)
            out[ruta] = meta.split()[2]
    return out


def arbol_actual() -> dict[str, str]:
    out = {}
    for e in _git("ls-files", "-s", "-z").stdout.decode("utf-8").split("\0"):
        if e:
            meta, ruta = e.split("\t", 1)
            out[ruta] = meta.split()[1]
    return out


def sha256_de(ids) -> dict[str, str]:
    """sha256 del contenido de cada blob (por su id de git)."""
    faltan = sorted({i for i in ids if i not in _SHA})
    if faltan:
        datos = _git("cat-file", "--batch", entrada=("\n".join(faltan) + "\n").encode()).stdout
        pos = 0
        for i in faltan:
            fin = datos.index(b"\n", pos)
            cab = datos[pos:fin].split()
            if len(cab) < 3 or cab[1] != b"blob":
                raise Bloqueo(f"git no devolvió el blob {i}")
            tam = int(cab[2])
            _SHA[i] = hashlib.sha256(datos[fin + 1:fin + 1 + tam]).hexdigest()
            pos = fin + 1 + tam + 1
    return {i: _SHA[i] for i in ids}


def destino(p: str) -> str:
    """Dónde debe quedar un archivo de la línea base tras la reorganización (T-04 a T-07)."""
    if p == "panel/animation_panel.log":
        return "archivo/raspberry-panel/animation_panel.log"
    if p in BANNERS_ANTIGUOS:
        return "archivo/banners-antiguos/" + p.rsplit("/", 1)[1]
    if p.startswith(("ficheros/", "panel/")):
        return "raspberry-panel/" + p
    return "archivo/" + p


def clasificar(base: dict[str, str], actual: dict[str, str]) -> dict[str, list[str]]:
    g = {"eliminados": [], "archivados": [], "conservados": [], "pyc": []}
    for p in base:
        if not p.startswith(CARPETAS_BASE):
            continue
        if p.endswith(".pyc"):
            g["pyc"].append(p)
        elif destino(p) in actual:
            g["archivados" if destino(p).startswith("archivo/") else "conservados"].append(p)
        else:
            g["eliminados"].append(p)
    return g


def _shas_destino(actual: dict[str, str]) -> set[str]:
    ids = [b for p, b in actual.items() if p.startswith(("raspberry-panel/", "archivo/")) and not p.endswith(".pyc")]
    return set(sha256_de(ids).values())


# --- comprobaciones compartidas (PF-07, PF-09 y PF-10) -----------------------------------
def _compila_e_importa(ctx) -> None:
    panel = RAIZ / "raspberry-panel" / "panel"
    fuentes = sorted(panel.glob("*.py"))
    ctx.igual([f.name for f in fuentes], sorted(PY_PANEL), "los 5 .py están en raspberry-panel/panel")
    r = ctx.ejecutar([ctx.config.get("python", sys.executable), "-B", "-c", COMPILAR, *map(str, fuentes)], cwd=RAIZ)
    ctx.comprobar(r.returncode == 0, "los 5 .py compilan", (r.stderr or r.stdout)[-300:])
    with tempfile.TemporaryDirectory(prefix="panel copia ñ ", ignore_cleanup_errors=True) as tmp:
        copia = Path(tmp) / "panel"
        shutil.copytree(panel, copia, ignore=shutil.ignore_patterns("__pycache__", "*.log", "*.pyc"))
        r = ctx.ejecutar([ctx.config.get("python", sys.executable), "-B", "-c", "import Config, Panel"], cwd=copia)
    ctx.comprobar(r.returncode == 0, "import Config, Panel funciona desde la carpeta del código", r.stderr[-300:])


def _identidad(ctx) -> int:
    base, actual = arbol_base(_base(ctx)), arbol_actual()
    pares = {}
    for p in base:
        if p == "platformio.ini" or p.startswith(("src/", "data/")):
            pares[p] = "esp32/" + p
    for n in range(1, 13):
        pares[f"ficheros/banner{n}.png"] = f"raspberry-panel/ficheros/banner{n}.png"
    ctx.comprobar(len([p for p in pares if p.startswith("ficheros/")]) == 12, "los 12 banners están en la línea base")
    ausentes = [d for d in pares.values() if d not in actual]
    ctx.comprobar(not ausentes, "todos están en su sitio nuevo", ausentes[:10])
    shas = sha256_de([base[p] for p in pares] + [actual[d] for d in pares.values() if d in actual])
    distintos = [p for p, d in pares.items() if shas[base[p]] != shas[actual[d]]]
    ctx.comprobar(not distintos, f"{len(pares)} archivos con el mismo sha256 que en la línea base", distintos[:10])
    return len(pares)


# --- F1 ---------------------------------------------------------------------------------------
@s.caso("PF-01", "Estructura nueva sin restos", requisitos=["RF-1"])
def pf01(ctx):
    actual = arbol_actual()
    for nombre in PY_PANEL + OTROS_PANEL:
        ctx.comprobar(f"raspberry-panel/panel/{nombre}" in actual, f"rastreado raspberry-panel/panel/{nombre}")
    faltan = [n for n in range(1, 13) if f"raspberry-panel/ficheros/banner{n}.png" not in actual]
    ctx.comprobar(not faltan, "banner1.png a banner12.png en raspberry-panel/ficheros/", faltan)
    viejos = [p for p in actual if p.startswith(("panel/", "ficheros/"))]
    ctx.comprobar(not viejos, "nada rastreado bajo panel/ ni ficheros/ de la raíz", viejos[:5])
    for carpeta in ("panel", "ficheros"):
        ctx.comprobar(not (RAIZ / carpeta).exists(), f"no existe {carpeta}/ en la raíz del disco")
    ctx.comprobar("raspberry-panel/panel/animation_panel.log" not in actual, "el log no está rastreado en raspberry-panel/panel/")
    ctx.comprobar("archivo/raspberry-panel/animation_panel.log" in actual, "el log está rastreado en archivo/raspberry-panel/")
    pyc = [p for p in actual if p.endswith(".pyc")]
    ctx.comprobar(not pyc, "git ls-files '*.pyc' no devuelve ninguno", pyc[:5])


@s.caso("PF-02", "El .gitignore con rutas difíciles", requisitos=["RF-1"])
def pf02(ctx):
    se_ignoran = [
        "raspberry-panel/panel/__pycache__/Panel.cpython-313.pyc",
        "archivo/navidad/ficheros navidad/panel/__pycache__/Config.cpython-37.pyc",
        "archivo/navidad/ñandú ç/__pycache__/a.cpython-37.pyc", "x/modulo.pyo", "x/modulo.pyd",
        "raspberry-panel/panel/animation_panel.log", "raspberry-panel/panel/animation_panel.log.1",
        ".idea/a", "desktop.ini", "Thumbs.db",
    ]
    no_se_ignoran = ["archivo/navidad/ficheros navidad/imagen.pdn", "raspberry-panel/ficheros/banner1.png",
                     "raspberry-panel/panel/Panel.py"]
    for ruta in se_ignoran:
        r = _git("check-ignore", "-q", "--no-index", "--", ruta, codigos=(0, 1))
        ctx.comprobar(r.returncode == 0, f"se ignora «{ruta}»")
    for ruta in no_se_ignoran:
        r = _git("check-ignore", "-q", "--no-index", "--", ruta, codigos=(0, 1))
        ctx.comprobar(r.returncode == 1, f"NO se ignora «{ruta}»")
    antiguas = _git("show", f"{_base(ctx)}:.gitignore").stdout.decode("utf-8", "replace").splitlines()
    actuales = (RAIZ / ".gitignore").read_text(encoding="utf-8-sig").splitlines()
    perdidas = [l for l in antiguas if l.strip() and l not in actuales]
    ctx.comprobar(not perdidas, "el .gitignore conserva las líneas de la línea base", perdidas)


@s.caso("PF-03", "Cada eliminado tiene un par idéntico", requisitos=["RF-2"])
def pf03(ctx):
    base, actual = arbol_base(_base(ctx)), arbol_actual()
    elim = clasificar(base, actual)["eliminados"]
    ctx.igual(len(elim), ELIMINADOS, "archivos eliminados (sin .pyc)")
    shas = sha256_de([base[p] for p in elim])
    destinos = _shas_destino(actual)
    sin_par = [p for p in elim if shas[base[p]] not in destinos]
    ctx.comprobar(not sin_par, f"los {len(elim)} eliminados tienen un par con el mismo sha256", sin_par[:10])


@s.caso("PF-04", "Cada archivo único está archivado", requisitos=["RF-3"])
def pf04(ctx):
    base, actual = arbol_base(_base(ctx)), arbol_actual()
    arch = clasificar(base, actual)["archivados"]
    ctx.igual(len(arch), ARCHIVADOS, "archivos archivados")
    shas = sha256_de([base[p] for p in arch] + [actual[destino(p)] for p in arch])
    distintos = [p for p in arch if shas[base[p]] != shas[actual[destino(p)]]]
    ctx.comprobar(not distintos, "mismo sha256 que en la línea base", distintos[:10])


@s.caso("PF-05", "Partición exacta, con nombres difíciles", requisitos=["RF-2", "RF-3"])
def pf05(ctx):
    base, actual = arbol_base(_base(ctx)), arbol_actual()
    g = clasificar(base, actual)
    en_carpetas = [p for p in base if p.startswith(CARPETAS_BASE)]
    ctx.igual(len(en_carpetas), TOTAL, "archivos de la línea base en ficheros/, navidad/ y panel/")
    cuenta = {k: len(v) for k, v in g.items()}
    ctx.igual(cuenta, {"eliminados": ELIMINADOS, "archivados": ARCHIVADOS, "conservados": CONSERVADOS, "pyc": PYC},
              "recuento por grupo")
    ctx.comprobar(sum(cuenta.values()) == TOTAL, "133 + 104 + 52 + 12 = 301")
    ctx.comprobar(any(" " in p for p in en_carpetas), "el conjunto incluye nombres con espacios")
    ctx.comprobar(any(not p.isascii() for p in en_carpetas), "el conjunto incluye nombres con caracteres no ASCII")


@s.caso("PF-06", "La comprobación de pares no es vacía", requisitos=["RF-2", "RF-3"])
def pf06(ctx):
    base, actual = arbol_base(_base(ctx)), arbol_actual()
    g = clasificar(base, actual)
    ctx.comprobar(len(g["archivados"]) == ARCHIVADOS, "punto de partida correcto")
    # (a) un archivado con el contenido sustituido por otro: debe detectarse como distinto
    victima = g["archivados"][0]
    otro = next(b for p, b in actual.items() if p.startswith("archivo/") and b != actual[destino(victima)])
    ctx.comprobar(sha256_de([otro])[otro] != sha256_de([base[victima]])[base[victima]],
                  "un archivado con otro contenido se detecta como distinto")
    # (b) un destino quitado: el archivo pasa a «eliminado» y deja de contar como archivado
    sin = {p: b for p, b in actual.items() if p != destino(victima)}
    g2 = clasificar(base, sin)
    ctx.comprobar(victima in g2["eliminados"] and len(g2["archivados"]) == ARCHIVADOS - 1,
                  "un destino quitado cambia el recuento y lo hace fallar")
    # (c) un eliminado cuyo único par se quita: se queda sin par
    elim = g["eliminados"][0]
    par = sha256_de([base[elim]])[base[elim]]
    resto = {p: b for p, b in actual.items() if sha256_de([b])[b] != par}
    ctx.comprobar(par not in _shas_destino(resto), "un eliminado sin su par se detecta")


@s.caso("PF-07", "Compila e importa", requisitos=["RF-4"])
def pf07(ctx):
    _compila_e_importa(ctx)


@s.caso("PF-08", "El firmware compila igual", requisitos=["RF-4"])
def pf08(ctx):
    pio = shutil.which(ctx.config.get("pio", "pio"))
    if not pio:
        ctx.bloquear("PlatformIO (pio) no está instalado o no está en el PATH; PF-09 comprueba por contenido")
    ini = (RAIZ / "esp32" / "platformio.ini").read_text(encoding="utf-8", errors="replace")
    plataformas = list((Path.home() / ".platformio" / "platforms").glob("espressif32*"))
    if not plataformas or ("lib_deps" in ini and not (RAIZ / "esp32" / ".pio" / "libdeps" / "esp32dev").is_dir()):
        ctx.bloquear("faltan la plataforma o las librerías en caché: compilar exigiría red; se pregunta al usuario")
    r = ctx.ejecutar([pio, "run", "-d", "esp32", "-e", "esp32dev"], timeout=1200, cwd=RAIZ)
    salida = r.stdout + r.stderr
    if re.search(r"Downloading|Installing|Resolving|ConnectionError|HTTPClientError", salida):
        ctx.bloquear("PlatformIO usó la red durante la compilación; se avisa al usuario")
    ctx.contiene(salida, "SUCCESS", "la compilación termina bien")
    ram = re.search(r"RAM:.*?used (\d+) bytes", salida)
    flash = re.search(r"Flash:.*?used (\d+) bytes", salida)
    ctx.comprobar(bool(ram and flash), "la salida da RAM y flash", salida[-300:])
    ctx.igual(int(ram.group(1)), int(ctx.config.get("esp32_ram", 48728)), "RAM usada en bytes")
    ctx.igual(int(flash.group(1)), int(ctx.config.get("esp32_flash", 890553)), "flash usada en bytes")


@s.caso("PF-09", "Contenido intacto de firmware y banners", requisitos=["RF-4"])
def pf09(ctx):
    _identidad(ctx)


@s.caso("PF-10", "Disco intacto y sin efectos", requisitos=["RF-4"])
def pf10(ctx):
    rutas = ["raspberry-panel", "esp32", "archivo", ".gitignore"]
    sucio = _git("status", "--porcelain=v1", "-z", "--", *rutas).stdout.decode("utf-8", "replace")
    ctx.comprobar(not sucio, "git status de las rutas del producto vacío (ni modificados ni sin rastrear)", sucio[:300])
    base, actual = arbol_base(_base(ctx)), arbol_actual()
    faltan = [destino(p) for p in clasificar(base, actual)["pyc"] if not (RAIZ / destino(p)).is_file()]
    ctx.comprobar(not faltan, f"los {PYC} .pyc siguen en el disco, sin borrar, en su destino", faltan[:6])

    def ignorados() -> str:
        return _git("status", "--porcelain=v1", "-z", "--ignored=matching", "--", *rutas).stdout.decode("utf-8", "replace")
    antes = ignorados()
    _compila_e_importa(ctx)
    ctx.igual(ignorados(), antes, "compilar e importar no deja archivos nuevos (ni ignorados) en el repositorio")


def _commit(ctx, tarea: str) -> str:
    r = _git("log", "--format=%H", "-E", f"--grep=^{tarea}:")
    hashes = r.stdout.decode().split()
    if not hashes:
        ctx.bloquear(f"no hay un commit cuyo mensaje empiece por «{tarea}:»")
    return hashes[-1]


def _cambios(c: str) -> list[tuple[str, list[str]]]:
    toks = _git("diff", "--name-status", "-M100%", "-z", f"{c}^", c).stdout.decode("utf-8").split("\0")
    out, i = [], 0
    while i < len(toks) and toks[i]:
        n = 2 if toks[i][0] in "RC" else 1
        out.append((toks[i], toks[i + 1:i + 1 + n]))
        i += 1 + n
    return out


@s.caso("PF-37", "Cada commit de movimiento solo hace lo autorizado", requisitos=["RF-4", "RF-2"])
def pf37(ctx):
    base, actual = arbol_base(_base(ctx)), arbol_actual()
    g = clasificar(base, actual)
    c3 = _cambios(_commit(ctx, "T-03"))
    ctx.igual(sorted((e, r[0]) for e, r in c3 if e == "M"), [("M", ".gitignore")], "T-03 solo modifica .gitignore")
    ctx.igual(sorted(r[0] for e, r in c3 if e == "D"), sorted(g["pyc"]), "T-03 solo saca del índice los 12 .pyc de la lista")
    ctx.comprobar(all(e in ("M", "D") for e, _ in c3), "T-03 no hace nada más", [e for e, _ in c3 if e not in ("M", "D")])
    c4 = _cambios(_commit(ctx, "T-04"))
    ctx.comprobar(all(e == "D" for e, _ in c4), "T-04 solo elimina", sorted({e for e, _ in c4}))
    ctx.igual(sorted(r[0] for _, r in c4), sorted(g["eliminados"]), "T-04 elimina exactamente la lista autorizada (133)")
    for t in ("T-05", "T-06", "T-07"):
        c = _cambios(_commit(ctx, t))
        extra = [(e, r) for e, r in c if e != "R100" and not (t == "T-05" and e == "A" and r == ["esp32/.gitignore"])]
        ctx.comprobar(not extra, f"{t} solo tiene renombrados al 100 %", extra[:5])


if __name__ == "__main__":
    raise SystemExit(s.ejecutar())

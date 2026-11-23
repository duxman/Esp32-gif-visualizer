# Graph Report - Esp32-gif-visualizer  (2026-11-23)

## Corpus Check
- 32 files · ~66,430 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 6, .pdn 4, .service 2)

## Summary
- 461 nodes · 617 edges · 24 communities (16 shown, 8 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 18 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `47422dc0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.cpp
- raspberry-panel/panel/AnimationServer.py
- GifPlayer
- run.py
- Fichas
- Diseño: Panel LED de Navidad en Raspberry Pi (Python)
- F0-bis · 2026-11-22 · Recuentos de la reorganización sobre `f25ee46`
- Casos
- AnimationServer
- Análisis: Panel Raspberry Pi, reorganización del repositorio y arreglos
- Arquitectura: Panel Raspberry Pi, reorganización y arreglos
- Config
- Manual de usuario: Esp32-gif-visualizer
- navidad/panel/LedMatrixAnimation.py
- Tareas: Panel Raspberry Pi, reorganización y arreglos
- AnimationServer
- Informe de pruebas funcionales: Panel Raspberry Pi: reorganización y arreglos
- navidad/panel/Config.py
- Agentes de este repositorio
- Estado del proyecto
- Panel
- Panel
- apagado.sh

## God Nodes (most connected - your core abstractions)
1. `Fichas` - 35 edges
2. `GifPlayer` - 28 edges
3. `Config` - 20 edges
4. `Análisis: Panel Raspberry Pi, reorganización del repositorio y arreglos` - 19 edges
5. `Arquitectura: Panel Raspberry Pi, reorganización y arreglos` - 17 edges
6. `Diseño: Visualizador de GIFs para ESP32 (firmware PlatformIO)` - 16 edges
7. `Diseño: Panel LED de Navidad en Raspberry Pi (Python)` - 16 edges
8. `Casos` - 15 edges
9. `LedPanelCfg` - 14 edges
10. `_git()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `Cómo trabajar con este código` --references--> `GifPlayer`  [INFERRED]
  doc/diseno/esp32-gif-visualizer.md → esp32/src/gif_player.h
- `Módulos` --references--> `GifPlayer`  [INFERRED]
  doc/diseno/esp32-gif-visualizer.md → esp32/src/gif_player.h
- `Flujos` --references--> `GIFDrawCallback()`  [INFERRED]
  doc/diseno/esp32-gif-visualizer.md → esp32/src/gif_player.cpp
- `Datos y estado` --references--> `LedPanelCfg`  [INFERRED]
  doc/diseno/esp32-gif-visualizer.md → esp32/src/gif_player.h
- `Reglas implícitas` --references--> `setRelay()`  [INFERRED]
  doc/diseno/esp32-gif-visualizer.md → esp32/src/main.cpp

## Import Cycles
- None detected.

## Communities (24 total, 8 thin omitted)

### Community 0 - "main.cpp"
Cohesion: 0.07
Nodes (39): Cambios, Contexto y límites, Contratos externos, Cómo trabajar con este código, Datos y estado, Decisiones deducidas, Diseño: Visualizador de GIFs para ESP32 (firmware PlatformIO), Finalidad (+31 more)

### Community 1 - "raspberry-panel/panel/AnimationServer.py"
Cohesion: 0.06
Nodes (4): Animation, Animation, main(), MainClass

### Community 2 - "GifPlayer"
Cohesion: 0.07
Nodes (22): GifPlayer::loop(), GifPlayer::stop(), GIFDrawCallback(), GifPlayer, cfg, currentPath, gif, gifFile (+14 more)

### Community 3 - "run.py"
Cohesion: 0.16
Nodes (24): arbol_actual(), arbol_base(), _base(), _cambios(), clasificar(), _commit(), _compila_e_importa(), destino() (+16 more)

### Community 4 - "Fichas"
Cohesion: 0.06
Nodes (35): Fichas, T-01 · Recontar la reorganización sobre la línea base, T-02 · Registrar los documentos previos en un commit, T-03 · Sacar los .pyc del índice y ampliar .gitignore, T-04 · Eliminar los archivos duplicados, T-05 · Mover el firmware ESP32 a esp32/, T-06 · Mover el panel de la Raspberry a raspberry-panel/, T-07 · Archivar los archivos sin copia (+27 more)

### Community 5 - "Diseño: Panel LED de Navidad en Raspberry Pi (Python)"
Cohesion: 0.07
Nodes (25): Cambios, Comandos ejecutados, Diagnóstico, Dudas abiertas para el análisis, Duplicados de imágenes, Opciones de reorganización (decide el usuario), Preguntas comunes, Requisitos expresados por el usuario (para el análisis futuro) (+17 more)

### Community 6 - "F0-bis · 2026-11-22 · Recuentos de la reorganización sobre `f25ee46`"
Cohesion: 0.07
Nodes (28): 1. Recuento sobre `f25ee46`, 2026-11-14 · Reorganización del repositorio (opción A), 2026-11-22 · Arquitectura de los arreglos del panel de la Raspberry Pi, 2. Lista 1 · los 12 `.pyc` que salen del índice en T-03 (`git ls-files "*__pycache__*"`), 3. Lista 2 · los 133 archivos que T-04 elimina con `git rm`, 4. Lo que se archiva (104) y lo que se conserva (52), 5. Finales de línea, `.gitignore` y zonas (C1), 6. Modo de las pancartas (`Image.open(p).mode`) (+20 more)

### Community 7 - "Casos"
Cohesion: 0.09
Nodes (22): Cambios, Casos, Entorno y precondiciones, Fuera de alcance, Inventario de entradas, PF-01 · Estructura nueva sin restos, PF-02 · `.gitignore` con rutas difíciles, PF-03 · Cada eliminado tiene un par idéntico (+14 more)

### Community 9 - "Análisis: Panel Raspberry Pi, reorganización del repositorio y arreglos"
Cohesion: 0.11
Nodes (19): Actores, Análisis: Panel Raspberry Pi, reorganización del repositorio y arreglos, AS-IS y TO-BE, Cambios, Casos de uso, Entradas y datos, Fuera de alcance, Glosario (+11 more)

### Community 10 - "Arquitectura: Panel Raspberry Pi, reorganización y arreglos"
Cohesion: 0.11
Nodes (17): Alternativas, Arquitectura: Panel Raspberry Pi, reorganización y arreglos, Atributos de calidad, Cambios, Componentes, Contexto y alcance, Datos, Decisiones (+9 more)

### Community 11 - "Config"
Cohesion: 0.12
Nodes (16): Config, apMode, gateway, led, mdnsEnabled, mdnsName, ntpEnabled, ntpServer (+8 more)

### Community 12 - "Manual de usuario: Esp32-gif-visualizer"
Cohesion: 0.13
Nodes (14): Abrir el código del panel de la Raspberry Pi, Abrir el firmware del ESP32, Antes de empezar, Cambios, Encontrar un archivo antiguo, Introducción, Limitaciones conocidas, Manual de usuario: Esp32-gif-visualizer (+6 more)

### Community 14 - "Tareas: Panel Raspberry Pi, reorganización y arreglos"
Cohesion: 0.15
Nodes (12): 2026-11-23 · Cierre de F0, 2026-11-23 · Cierre de F1, Alcance, Bitácora, Cambios, Decisiones técnicas, Fases, Preguntas abiertas (+4 more)

### Community 16 - "Informe de pruebas funcionales: Panel Raspberry Pi: reorganización y arreglos"
Cohesion: 0.20
Nodes (9): Avisos, Cobertura de requisitos, Fallos y bloqueos, Informe de pruebas funcionales: Panel Raspberry Pi: reorganización y arreglos, Pendientes, Por clase de prueba, Resultados, Resumen (+1 more)

### Community 18 - "Agentes de este repositorio"
Cohesion: 0.25
Nodes (7): Agentes de este repositorio, Arnés, Datos de este proyecto, Dos modos, elegidos con la barra, En modo `/orquestador`, En modo `/poc`, Gasto de contexto

### Community 19 - "Estado del proyecto"
Cohesion: 0.29
Nodes (6): Diseño de código existente, Dónde estamos, Estado del proyecto, Manuales de usuario, Tareas: Panel Raspberry Pi, reorganización y arreglos, Última prueba funcional

## Knowledge Gaps
- **33 isolated node(s):** `pin`, `panelWidth`, `panelHeight`, `chainX`, `chainY` (+28 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 291 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Diseño: Visualizador de GIFs para ESP32 (firmware PlatformIO)` connect `main.cpp` to `Diseño: Panel LED de Navidad en Raspberry Pi (Python)`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `GifPlayer` (e.g. with `Cómo trabajar con este código` and `Módulos`) actually correct?**
  _`GifPlayer` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `pin`, `panelWidth`, `panelHeight` to the rest of the system?**
  _33 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `main.cpp` be split into smaller, more focused modules?**
  _Cohesion score 0.07013574660633484 - nodes in this community are weakly interconnected._
- **Why does `AnimationServer` connect `AnimationServer` to `raspberry-panel/panel/AnimationServer.py`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Should `raspberry-panel/panel/AnimationServer.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06025369978858351 - nodes in this community are weakly interconnected._
- **Why does `GifPlayer` connect `GifPlayer` to `main.cpp`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
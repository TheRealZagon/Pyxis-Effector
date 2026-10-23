<p align="center">
  <img src="PyxisNodes/web/icon.png" alt="Pyxis Effector Logo" width="128" height="128">
</p>

<h1 align="center">Pyxis Effector</h1>

<p align="center">
  <strong>Motor Visual Basado en Nodos para la Automatización de Efectos de Karaoke en Aegisub</strong>
</p>

<p align="center">
  <a href="https://github.com/Mandholine/Pyxis-Effector/releases">
    <img src="https://img.shields.io/badge/version-1.1.5-blue.svg" alt="Versión">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-GPL--3.0-green.svg" alt="Licencia GPL-3.0">
  </a>
  <img src="https://img.shields.io/badge/Aegisub-Automation%204-orange.svg" alt="Aegisub">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB.svg?logo=python&logoColor=white" alt="Python 3.12">
</p>

<p align="center">
  <a href="https://discord.gg/fsxRESeQZN">
    <img src="https://img.shields.io/badge/Discord-Comunidad-5865F2.svg?logo=discord&logoColor=white" alt="Discord">
  </a>
  <a href="https://x.com/PyxisEffector">
    <img src="https://img.shields.io/badge/X-@PyxisEffector-000000.svg?logo=x&logoColor=white" alt="X (Twitter)">
  </a>
  <a href="https://github.com/Mandholine/Pyxis-Effector">
    <img src="https://img.shields.io/badge/GitHub-Repositorio-181717.svg?logo=github&logoColor=white" alt="GitHub">
  </a>
  <a href="mailto:pyxiseffector@gmail.com">
    <img src="https://img.shields.io/badge/Email-Contacto-EA4335.svg?logo=gmail&logoColor=white" alt="Email">
  </a>
</p>

<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/Idioma-Espa%C3%B1ol-2563EB.svg" alt="Español"></a>
  <a href="README.en.md"><img src="https://img.shields.io/badge/Language-English-6B7280.svg" alt="English"></a>
</p>
<p align="center">
  <strong>Español</strong> &bull; <a href="README.en.md">Read in English (en-GB)</a>
</p>

---

## Filosofía y Origen

**Pyxis Effector** parte de la arquitectura del proyecto legacy **Kara Effector 3.6** y reemplaza sus scripts secuenciales por un entorno visual basado en grafos acíclicos dirigidos (DAG). Tiene un núcleo en Python 3.12, aceleración por GPU, renderizado WebAssembly en tiempo real y manipulación vectorial de subtítulos Advanced SubStation Alpha (ASS).

El nombre viene de la constelación de **Pyxis** (la Brújula náutica), y alude a la orientación técnica y a la unión de tipografía cinética, álgebra espacial, cinemática temporal y lógica algorítmica.

---

## Características Principales

* **Editor visual en grafo (DAG):** Los efectos se componen conectando puertos de datos y de contexto, sin tener que escribir código.
* **Ejecución híbrida:** Núcleo en Python 3.12 con evaluación paralela multiproceso y aceleración por GPU mediante OpenCL.
* **Previsualización en tiempo real:** Reproductor sincronizado integrado en el canvas, con renderizado WebAssembly (JASSUB/libass) y ArtPlayer.js.
* **Morfología vectorial y polígonos:** Conversión de glifos a contornos vectoriales, vectorización ráster con Potrace y operaciones booleanas (unión, diferencia, intersección, xor, offsetting) con Clipper2.
* **Procesamiento de audio:** Envolventes de amplitud RMS, picos, filtrado por bandas y Transformada Rápida de Fourier (FFT) sobre el audio del proyecto.
* **Scripting en Python y Lua:** Los nodos imperativos `System/Script Code` ejecutan Python 3.12 y Lua 5.1/LuaJIT a través de un puente bidireccional en C (Lupa).
* **Linter previo a la generación:** Validador estático (`node_validator.py`) con análisis AST en tiempo real de Dark Tags ASS, variables no declaradas e integridad topológica.
* **Telemetría y perfilado de renderizado ASS (`libass` + QPC):** Mide fotograma a fotograma, en varios procesos, el coste de renderizado, el consumo de Frame Budget y la memoria de mapas de bits, con un mapa de calor interactivo en el reproductor. Nativo en Windows; en Linux y macOS se ejecuta mediante Wine (solución provisional).
* **Persistencia y plantillas:** Exportación e importación de grafos completos, aislamiento de sesiones y almacenamiento de plantillas en `%APPDATA%\PyxisNodes\` (Windows) o `~/.local/share/PyxisNodes` (Linux/macOS).

---

## Manual Técnico Oficial

La documentación técnica está dividida en 12 volúmenes, en [`PyxisNodes/docs/es/`](PyxisNodes/docs/es/) (versión en inglés británico en [`PyxisNodes/docs/en/`](PyxisNodes/docs/en/)):

| Volumen | Título | Ámbito Técnico Principal |
| :---: | :--- | :--- |
| **01** | [Paradigma Visual y Arquitectura](PyxisNodes/docs/es/01%20Paradigma%20visual.md) | Principios de grafo DAG, ciclo de vida del contexto, tipificación de expresiones y perfilado de renderizado con `libass`. |
| **02** | [Anatomía de la Interfaz](PyxisNodes/docs/es/02%20Anatomia%20de%20la%20interfaz.md) | Barra de herramientas, panel de navegación, lienzo de nodos, modales y atajos de teclado. |
| **03** | [Nodos Básicos y Tipos Primitivos](PyxisNodes/docs/es/03%20Basics.md) | `Number`, `String`, `Text`, `Color Picker`, `Math`, `MultiRandom`, `Concatenate`, `Dynamic Format`, `MultiTag`, `Only`, `Once`. |
| **04** | [Nodos de Sistema y Pipeline](PyxisNodes/docs/es/04%20System.md) | `Output`, `Previewer`, `Script Code`, `Benchmark Math`, pipeline de renderizado y ordenamiento de colas. |
| **05** | [Bucles y Control de Iteración](PyxisNodes/docs/es/05%20Loops.md) | `Main Loop` (sílabas, palabras, caracteres), `MaxLoop` (FBF y partículas) y operador `Module`. |
| **06** | [Geometría y Morfología Vectorial](PyxisNodes/docs/es/06%20Shapes.md) | Primitivas, `Library`, `IMG to Shape`, `Stroke`, `Walker`, `Slicer`, `Array`, `Concentric`, `Multi`, `Manipulator`, `Transform`, `Filter`, `Clipper`, `Union & Divide`. |
| **07** | [Temporalización e Interpolación](PyxisNodes/docs/es/07%20Times.md) | Fases de retiming, desfases `Lead In`/`Out`, sincronización inter-línea `Synced`, deltas `Middle`, bucles `Loop`, conversiones de tiempo y curvas `Ipol`. |
| **08** | [Funciones Cinemáticas y Moduladores](PyxisNodes/docs/es/08%20Functions.md) | `Tag Manipulator`, `Tag Oscillator`, `Glitter`, `Conditioner`, `Animation`, `Color Gradient`, `Clip Gradient`, `IMG to pixels`, `Polar to Cartesian`, splines `Bezier`, partículas y texto vectorial. |
| **09** | [Variables y Gestión de Contexto](PyxisNodes/docs/es/09%20Variables.md) | Jerarquía métrica formal, aislamiento de iteradores DAG, `Sys Var`, `Define Vars`, `Get Var`, `Memory` y tipificación Tipos A/B/C. |
| **10** | [Procesamiento y Reactividad de Audio](PyxisNodes/docs/es/10%20Audio.md) | Decodificación PCM, cálculo $\mathcal{O}(1)$ de RMS mediante Prefix Sums, picos, envolventes, FFT y modos `Modulator` / `Waveform`. |
| **11** | [Entorno Base y Renderizado Autónomo](PyxisNodes/docs/es/11%20Entorno%20base%20y%20personalizacion.md) | Modo Base independiente de Aegisub, ventana cinemática con margen de 2000 ms, plantillas de lienzo e invalidación SHA-256. |
| **12** | [Scripting y Programación Avanzada](PyxisNodes/docs/es/12%20Scripting%20y%20programacion%20avanzada.md) | Entorno dual Python/Lua, generadores funcionales de tags ASS, cinemática, persistencia y motor determinista `by.<iter>.<R>`. |

---

## Instalación y Uso Rápido

La instalación es igual en todas las plataformas:

1. Descarga [`pyxis.NodeEngine.lua`](https://github.com/Mandholine/Pyxis-Effector/releases/latest/download/pyxis.NodeEngine.lua) (se adjunta a cada release en [**Releases**](https://github.com/Mandholine/Pyxis-Effector/releases)).
2. Cópialo en la carpeta `automation/autoload` de Aegisub (ver la tabla).
3. Abre Aegisub y ejecuta **Automatización** $\to$ **Pyxis Node Engine**. La primera vez, la macro ofrece descargar el motor (`PyxisNodes/`) automáticamente.

Si prefieres instalarlo a mano o sin conexión, descarga de [**Releases**](https://github.com/Mandholine/Pyxis-Effector/releases) el paquete de tu plataforma y descomprímelo en esa misma carpeta (crea `PyxisNodes/`). Cada paquete incluye su propio Python y ffmpeg, así que no hace falta instalar nada más.

| Plataforma | Paquete | Carpeta `autoload` de Aegisub |
| :--- | :--- | :--- |
| Windows 10 / 11 (64-bit) | `PyxisEffector-v<versión>-win64.zip` | `%APPDATA%\Aegisub\automation\autoload\` (usuario), `C:\Program Files\Aegisub\automation\autoload\` (sistema) o `<Carpeta_Aegisub>\automation\autoload\` (portable) |
| Linux x86-64 | `PyxisEffector-v<versión>-linux64.zip` | `~/.config/aegisub/automation/autoload/` |
| Linux ARM64 | `PyxisEffector-v<versión>-linux-arm64.zip` | `~/.config/aegisub/automation/autoload/` |
| macOS Apple Silicon | `PyxisEffector-v<versión>-macos-arm64.zip` | `~/Library/Application Support/Aegisub/automation/autoload/` |
| macOS Intel | `PyxisEffector-v<versión>-macos-x64.zip` | `~/Library/Application Support/Aegisub/automation/autoload/` |

> **Si tenías `Pyxis_engine.lua`** de una versión anterior, bórralo: es el mismo script con otro nombre y Aegisub cargaría la macro dos veces.

> ⚠️ **macOS sin probar:** los paquetes `macos-arm64` y `macos-x64` se construyen automáticamente pero **no se han probado en hardware Mac**. Si los usas, se agradecen informes de errores y contribuciones (issues y PRs).

**Requisitos:** Aegisub 3.2.x, 3.3.x o 3.4.x (Automation 4). En Windows, además, Microsoft Visual C++ Redistributable (2015-2022 x64); si falta Microsoft Edge WebView2 Runtime, Pyxis ofrece instalarlo en el primer arranque.

* Linux y macOS (dependencias del sistema, Gatekeeper, instalación desde el código fuente, datos de usuario, solución de problemas): [Linux](#linux) y [macOS](#macos), más abajo.
* Para construir los paquetes tú mismo (y para obtener o compilar ffmpeg): [tools/README.md](tools/README.md).

---

## Linux y macOS

### Linux

El paquete `linux64` o `linux-arm64` (ver la tabla de arriba) crea `PyxisNodes/` con su propio Python 3.12, las dependencias y Qt WebEngine para la interfaz. Solo hace falta lo que el paquete no puede llevar:

* `ffmpeg`: el paquete incluye uno (build GPL de BtbN con libx264, libass y libwebp, verificado por SHA-256). Si se construyó con `--no-ffmpeg`, instálalo con tu gestor de paquetes.
* Las bibliotecas de sistema que exige Qt WebEngine. En un escritorio normal ya están instaladas (`libnss3`, `libxkbcommon`, `libxcb-*`…).

El resto de esta sección describe la **instalación desde el código fuente**.

#### Requisitos del sistema (instalación desde el código fuente)

| Componente | Obligatorio | Propósito | Debian / Ubuntu | Arch |
|---|---|---|---|---|
| Python ≥ 3.10 | Sí | Motor de ejecución | `python3 python3-venv` | `python` |
| ffmpeg | Sí | Audio y vídeo | `ffmpeg` | `ffmpeg` |
| WebKitGTK 4.1 | Sí* | GUI (backend `gtk`) | `python3-gi gir1.2-webkit2-4.1` | `python-gobject webkit2gtk-4.1` |
| Qt WebEngine | Alternativa* | GUI (backend `qt`) | `python3-pyqt6.qtwebengine` | `python-pyqt6-webengine` |
| fontconfig | Recomendado | Resolución de fuentes | `fontconfig` | `fontconfig` |
| potrace | Opcional | Vectorización rápida de imágenes | `potrace` | `potrace` |
| tkinter | Opcional | Diálogos de archivo de respaldo | `python3-tk` | `tk` |
| wmctrl / xdotool | Opcional | Elevar el foco de la ventana | `wmctrl` / `xdotool` | igual |

\* Se necesita **uno** de los dos backends gráficos. GTK (WebKitGTK) es el recomendado.

Aegisub está disponible en la mayoría de distribuciones (`aegisub` o `aegisub-git`).

#### Instalación

```bash
git clone https://github.com/Mandholine/Pyxis-Effector.git
cd Pyxis-Effector/PyxisNodes
./install_linux.sh
```

El instalador crea un entorno virtual en `PyxisNodes/.venv`, instala las dependencias de Python (`requirements.txt`) y comprueba las dependencias del sistema.

Instalación manual equivalente:

```bash
cd PyxisNodes
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt
```

> `--system-site-packages` es necesario para que el entorno virtual vea los bindings GTK/Qt (`python-gobject` / PyQt) instalados por el gestor de paquetes de la distro.

#### Uso con Aegisub

1. Copia a tu carpeta de automation de Aegisub (`~/.config/aegisub/automation/autoload/` o `?user/automation/autoload` dentro de Aegisub):
   * `PyxisNodes/` (carpeta completa, con `.venv` incluido)
   * `pyxis.NodeEngine.lua`
2. En Aegisub: **Automatización → Pyxis Node Engine**.
3. La macro exporta las líneas seleccionadas, abre el editor visual y, al generar, inserta las capas de efectos (`pyxis_fx`) en los subtítulos.

El flujo es idéntico al de Windows:

* La macro busca el intérprete en este orden: `PyxisNodes/python/bin/python3` (paquete de release), `PyxisNodes/.venv/bin/python3`, `python3` del sistema y `python`.
* Si clonaste el repositorio, `PyxisNodes/python/` puede contener el runtime de Windows (`python.exe`); no se usa en Linux. Los paquetes de Linux se generan con `python tools/build_release.py` y no comparten ese directorio.
* El proceso se lanza desacoplado (`nohup … &`); el daemon HTTP local (`127.0.0.1:28723`) permite reaperturas instantáneas sin relanzar Python.
* Si el daemon detecta que Aegisub ha cerrado (PID), se apaga automáticamente.

Uso independiente (sin Aegisub):

```bash
cd PyxisNodes
.venv/bin/python main.py
```

#### Ubicación de datos (XDG)

Los datos de usuario viven en `$XDG_DATA_HOME/PyxisNodes` (por defecto `~/.local/share/PyxisNodes`):

| Ruta | Contenido |
|---|---|
| `~/.local/share/PyxisNodes/user_config.json` | Configuración, geometría de ventana |
| `~/.local/share/PyxisNodes/temp_cache/` | Puente temporal con Aegisub |
| `~/.local/share/PyxisNodes/temp/` | Temporales internos, caché de audio |
| `~/.local/share/PyxisNodes/templates/` | Plantillas de usuario |
| `~/.local/share/PyxisNodes/themes/` | Temas personalizados |

En Windows se mantiene el comportamiento histórico (`%APPDATA%\PyxisNodes`). macOS usa la misma ruta que Linux.

#### Paridad de funciones

El código sigue siendo compatible con Windows.

| Función | Windows | Linux |
|---|---|---|
| Editor de nodos, preview, partículas | ✔ | ✔ |
| Métricas y contornos tipográficos | Win32 GDI | **FreeType + fontconfig** (`freetype-py`) |
| Texto a forma vectorial (`text_to_shape`) | Contornos GDI | Contornos FreeType reales |
| Audio / vídeo | ffmpeg empaquetado | ffmpeg empaquetado en el paquete de release; del sistema si instalas desde el código fuente |
| Vectorización de imágenes | potrace.exe | potrace del sistema (fallback Python) |
| GPU OpenCL / CUDA | ✔ | ✔ (pyopencl / CPU fallback) |
| Telemetría libass (`libass_profiler`) | ✔ | ✔ mediante **Wine** (ver abajo); sin Wine, error controlado |
| Limpieza de procesos hijos | Job Object | `PR_SET_PDEATHSIG` |
| Descarga automática del motor desde la macro | ✔ (zip win64) | ✔ (zip linux64) o instalación manual |

* `bin/*.exe` no se usa en Linux, salvo `libass_profiler.exe` mediante Wine.
* Para obtener o compilar un ffmpeg propio desde el repositorio, consulta [tools/README.md](tools/README.md) (`python tools/get_ffmpeg.py` o `python tools/get_ffmpeg.py --build`).

#### Telemetría de renderizado (Wine, provisional)

`libass_profiler` solo existe como binario de Windows (`bin/libass_profiler.exe`). Si hay `wine` instalado, Pyxis lo ejecuta con él de forma automática (es una herramienta de consola, no necesita pantalla). Es una solución provisional hasta que exista un port nativo:

* La primera vez crea un prefijo de Wine propio en `~/.local/share/PyxisNodes/wine` (unos 10 s); las siguientes ejecuciones tardan fracciones de segundo.
* Los tiempos de render son orientativos: miden libass dentro de Wine, con su resolución de fuentes (DirectWrite sobre fontconfig) y sin los mismos cachés que Windows.
* Si colocas un `libass_profiler` nativo en `PyxisNodes/bin/` (o en el `PATH`), tiene prioridad y Wine deja de usarse.
* Variables de entorno: `PYXIS_DISABLE_WINE=1` (nunca usar Wine), `PYXIS_WINE=<ruta>` (otro ejecutable de wine), `PYXIS_WINEPREFIX=<dir>` (otro prefijo).
* Instalación de Wine: `sudo apt install wine` / `sudo pacman -S wine`.

#### Solución de problemas

* **«Backend gráfico NO disponible»** → instala `python3-gi gir1.2-webkit2-4.1` (GTK) o el paquete Qt WebEngine de tu distro, y vuelve a crear el venv con `--system-site-packages`.
* **La macro no encuentra Python** → ejecuta `install_linux.sh` para crear `PyxisNodes/.venv`, o instala `python3` en el PATH.
* **Tipografías con métricas imprecisas** → instala `fontconfig` y verifica que la familia existe (`fc-match "Nombre De La Fuente"`). Pyxis resuelve las fuentes igual que Aegisub: si una familia no existe, se usa la sustitución de fontconfig.
* **No se abre la ventana** → revisa `~/.local/share/PyxisNodes/temp/*_debug.log` (el arranque escribe ahí el traceback completo).
* **El audio no se procesa** → `ffmpeg` es obligatorio; comprueba con `ffmpeg -version`.

### macOS

Pyxis Effector funciona en macOS (Apple Silicon e Intel) con Cocoa/WebKit para la interfaz y la macro de Automation 4 de Aegisub.

> **Estado:** el soporte de macOS está implementado pero todavía no se ha probado en hardware Mac. Si encuentras un problema, abre una incidencia con el contenido de `~/.local/share/PyxisNodes/temp/` (registros de arranque).

#### Instalación (paquete de release, recomendado)

Instala como se indica en [Instalación y Uso Rápido](#instalación-y-uso-rápido), con `macos-arm64` para Macs con Apple Silicon (M1 o posterior) o `macos-x64` para Macs con Intel. El paquete incluye su propio Python 3.12 y todas las dependencias: no necesitas Homebrew ni instalar Python.

**Gatekeeper.** Los paquetes no están firmados con un certificado de Apple. Si los descargas con el navegador, macOS los pone en cuarentena y bloqueará el Python incluido. Quita la marca una vez:

```bash
xattr -dr com.apple.quarantine ~/Library/Application\ Support/Aegisub/automation/autoload/PyxisNodes
```

Si la macro descarga el motor por sí misma, ejecuta ese comando automáticamente.

**ffmpeg.** El paquete incluye un ffmpeg nativo para tu arquitectura (de [ffmpeg.martin-riedl.de](https://ffmpeg.martin-riedl.de), con libx264, libass, libwebp y VideoToolbox, verificado por SHA-256). Si se construyó con `--no-ffmpeg`, instálalo con Homebrew (`brew install ffmpeg`); Pyxis busca también en `/opt/homebrew/bin` y `/usr/local/bin`, aunque Aegisub se abra desde el Finder con un `PATH` mínimo. `potrace` es opcional (`brew install potrace`).

Para compilar tu propio ffmpeg desde el código fuente: [tools/README.md](tools/README.md).

#### Instalación desde el código fuente

```bash
brew install python ffmpeg        # Python ≥ 3.10; /usr/bin/python3 es demasiado antiguo
cd PyxisNodes && ./install_macos.sh
```

Después copia `PyxisNodes/` y `pyxis.NodeEngine.lua` a la carpeta `autoload` de Aegisub. La macro usa `PyxisNodes/.venv/bin/python3` si no hay un runtime en `PyxisNodes/python/`.

Uso independiente: `PyxisNodes/.venv/bin/python PyxisNodes/main.py`.

#### Diferencias respecto a Windows

| Función | macOS |
|---|---|
| Interfaz | Cocoa/WebKit (pywebview) |
| Métricas y contornos tipográficos | FreeType; las fuentes se localizan en `/System/Library/Fonts`, `/Library/Fonts` y `~/Library/Fonts` |
| Codificación de vídeo | `h264_videotoolbox` si ffmpeg lo incluye; si no, x264 |
| GPU OpenCL | Opcional (Apple lo considera obsoleto); si falla, se usa la CPU |
| Telemetría libass (`libass_profiler`) | Solo mediante Wine (ver abajo); sin Wine, error controlado |
| Limpieza de procesos hijos | Vigilancia del proceso padre en cada worker |

#### Telemetría con Wine (sin probar en macOS)

`libass_profiler` solo existe como binario de Windows. Pyxis intenta ejecutarlo con Wine si lo encuentra (`brew install --cask wine-stable`, Wine Stable/Staging/Devel o CrossOver en `/Applications`). **Esta vía no se ha probado en macOS** (en Linux sí): Wine en macOS solo existe para Intel, así que en Apple Silicon necesita Rosetta 2. Si no funciona, la telemetría se desactiva con un mensaje de error y el resto de Pyxis no se ve afectado. Los detalles (prefijo propio, variables `PYXIS_WINE`, `PYXIS_DISABLE_WINE`, precisión de los tiempos) son los mismos que en [Linux](#telemetría-de-renderizado-wine-provisional). Un `libass_profiler` nativo en `PyxisNodes/bin/` tendrá prioridad cuando exista.

#### Solución de problemas

* **«Faltan los bindings de Cocoa»** → reinstala con `pip install --force-reinstall pywebview`.
* **La macro no encuentra Python** → reinstala el paquete de release o ejecuta `install_macos.sh`.
* **«"python3" no puede abrirse porque no se puede verificar el desarrollador»** → ver *Gatekeeper*.
* **No se abre la ventana** → revisa `~/.local/share/PyxisNodes/temp/*_debug.log` y `preflight_debug.log`.
* **El audio no se procesa** → comprueba `ffmpeg -version` desde una Terminal.

---

## Equipo y Contribuciones

* **Trota** ([@mandholine](https://github.com/Mandholine)): Diseño e implementación de la interfaz gráfica de nodos, arquitectura del motor en Python, extensiones del ecosistema Kara Effector y documentación técnica.
* **Itachi / Effector** ([@effector2](https://github.com/effector2)): Diseño y desarrollo de bibliotecas de funciones en Lua, algoritmos cinemáticos y lógica de procesamiento. Coautor de Kara Effector legacy.
* **Zaph** ([@pholguinc](https://github.com/pholguinc)): Diseño arquitectónico inicial para el puente de comunicación e interoperabilidad entre Python y Lua.

---

## Agradecimientos Históricos

Gracias a los desarrolladores y colaboradores del proyecto histórico **Kara Effector 3.6 legacy**, cuyas ideas y algoritmos de automatización de subtítulos inspiraron esta arquitectura visual.

---

## Código Externo y Créditos de Terceros

Pyxis Effector usa las siguientes librerías y componentes de código abierto:

* [**LiteGraph.js**](https://github.com/jagenjo/litegraph.js): Motor de grafo de nodos y canvas visual interactivo (Licencia MIT).
* [**Ace Editor**](https://github.com/ajaxorg/ace): Editor de código embebido para nodos de scripting (Licencia BSD).
* [**ArtPlayer.js**](https://artplayer.org/): Reproductor multimedia HTML5 (Licencia MIT).
* [**JASSUB**](https://github.com/ThaUnknown/jassub) / [**libass**](https://github.com/libass/libass): Renderizado de subtítulos ASS compilado en WebAssembly (Licencias MIT / ISC / GPL).
* [**Clipper2**](https://github.com/AngusJohnson/Clipper2) / [**PyClipper**](https://github.com/fonttools/pyclipper): Motor de geometría poligonal, operaciones booleanas y cálculo de offset (Licencia BSL-1.0).
* [**Potrace**](https://potrace.sourceforge.net/): Vectorización y conversión de mapas de bits a trazados vectoriales (Licencia GPL v2+).
* [**KaTeX**](https://katex.org/): Renderizado tipográfico de fórmulas matemáticas en interfaz y documentación (Licencia MIT).
* [**Marked.js**](https://marked.js.org/): Compilador de Markdown para la documentación integrada y tooltips contextuales (Licencia MIT).
* [**Lupa**](https://github.com/scoder/lupa): Puente de comunicación bidireccional en C entre Python y LuaJIT / Lua 5.1 (Licencia MIT).
* [**PyWebView**](https://pywebview.flowrl.com/): Capa de ventana web nativa de escritorio para Windows, macOS y Linux (Licencia BSD-3).
* [**FFmpeg**](https://ffmpeg.org/): Decodificación multimedia, extracción de pistas PCM y procesado de vídeo. El núcleo es LGPL v2.1+, pero los paquetes incluyen compilaciones **GPL v2+** (con libx264, libass y libwebp) de [BtbN](https://github.com/BtbN/FFmpeg-Builds) (Windows y Linux) y de [martin-riedl.de](https://ffmpeg.martin-riedl.de) (macOS).
* [**Python**](https://www.python.org/) mediante [**python-build-standalone**](https://github.com/astral-sh/python-build-standalone): Intérprete independiente incluido en cada paquete (Licencia PSF).
* [**PyQt6**](https://www.riverbankcomputing.com/software/pyqt/) / [**Qt WebEngine**](https://www.qt.io/): Interfaz gráfica incluida en los paquetes de Linux (Licencias GPL v3 / LGPL v3).
* [**FreeType**](https://freetype.org/) / [**freetype-py**](https://github.com/rougier/freetype-py): Métricas y contornos tipográficos en Linux y macOS (Licencias FreeType / BSD).
* [**NumPy**](https://numpy.org/) / [**Pillow**](https://python-pillow.org/): Motor de partículas, audio e imágenes (Licencias BSD-3 / HPND).
* [**Wine**](https://www.winehq.org/): Opcional; ejecuta `libass_profiler.exe` en Linux y macOS (Licencia LGPL v2.1+).
* [**Aegisub**](https://github.com/TypesettingTools/Aegisub): El icono de la interfaz para el modo de proyecto activo es `aegisub-icon-mk2.svg` (Licencia BSD-3-Clause, © 2004-2012 Aegisub Project).

---

## Declaración sobre el Uso de Inteligencia Artificial

* El desarrollo técnico y la arquitectura de la interfaz web se hicieron con ayuda de **Google Gemini** a través de **Antigravity**.
* La compatibilidad con Linux y macOS (adaptación del motor, empaquetado con Python incluido, integración continua y herramientas de `tools/`) se desarrolló con ayuda de modelos de IA: **Claude** (Anthropic) y **MiMo 2.6 Pro** (Xiaomi), este último a través de **OpenCode Go**.

---

## Licencia

Copyright (C) 2026 @mandholine, @effector2, @pholguinc y los contribuidores de Pyxis Effector.

Este proyecto está distribuido bajo los términos de la **GNU General Public License v3.0 (GPL-3.0)**. El texto completo se encuentra disponible en el archivo [LICENSE](LICENSE).
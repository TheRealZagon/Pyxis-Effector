<p align="center">
  <img src="PyxisNodes/web/icon.png" alt="Pyxis Effector Logo" width="128" height="128">
</p>

<h1 align="center">Pyxis Effector</h1>

<p align="center">
  <strong>Visual Node-Based Karaoke Automation Engine for Aegisub</strong>
</p>

<p align="center">
  <a href="https://github.com/Mandholine/Pyxis-Effector/releases">
    <img src="https://img.shields.io/badge/version-1.1.5-blue.svg" alt="Version">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/licence-GPL--3.0-green.svg" alt="GPL-3.0 Licence">
  </a>
  <img src="https://img.shields.io/badge/Aegisub-Automation%204-orange.svg" alt="Aegisub">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB.svg?logo=python&logoColor=white" alt="Python 3.12">
</p>

<p align="center">
  <a href="https://discord.gg/fsxRESeQZN">
    <img src="https://img.shields.io/badge/Discord-Community-5865F2.svg?logo=discord&logoColor=white" alt="Discord">
  </a>
  <a href="https://x.com/PyxisEffector">
    <img src="https://img.shields.io/badge/X-@PyxisEffector-000000.svg?logo=x&logoColor=white" alt="X (Twitter)">
  </a>
  <a href="https://github.com/Mandholine/Pyxis-Effector">
    <img src="https://img.shields.io/badge/GitHub-Repository-181717.svg?logo=github&logoColor=white" alt="GitHub">
  </a>
  <a href="mailto:pyxiseffector@gmail.com">
    <img src="https://img.shields.io/badge/Email-Contact-EA4335.svg?logo=gmail&logoColor=white" alt="Email">
  </a>
</p>

<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/Language-Espa%C3%B1ol-6B7280.svg" alt="Español"></a>
  <a href="README.en.md"><img src="https://img.shields.io/badge/Language-English%20(en--GB)-2563EB.svg" alt="English (en-GB)"></a>
</p>
<p align="center">
  <a href="README.md">Leer en Español</a> &bull; <strong>English (en-GB)</strong>
</p>

---

## Philosophy and Origin

**Pyxis Effector** builds on the architecture of the legacy **Kara Effector 3.6** project and replaces its sequential scripts with a visual environment based on directed acyclic graphs (DAGs). It has a Python 3.12 core, GPU acceleration, real-time WebAssembly rendering, and vector manipulation of Advanced SubStation Alpha (ASS) subtitles.

The name comes from the **Pyxis** constellation (the Mariner's Compass), and refers to technical orientation and the combination of kinetic typography, spatial geometry, temporal kinematics, and algorithmic logic.

---

## Key Features

* **DAG Visual Editor:** Effects are built by connecting data and context ports, with no code required.
* **Hybrid Execution:** Python 3.12 core with multi-process parallel evaluation and OpenCL GPU acceleration.
* **Real-Time Preview:** Synchronised player built into the canvas, using WebAssembly ASS rendering (JASSUB/libass) and ArtPlayer.js.
* **Vector Morphology and Polygons:** Glyph outline conversion, bitmap vectorisation via Potrace, and boolean polygon operations (union, difference, intersection, xor, offsetting) via Clipper2.
* **Audio Analysis:** Root Mean Square (RMS) envelopes, peaks, frequency band filtering, and Fast Fourier Transform (FFT) on the project audio.
* **Python and Lua Scripting:** Imperative `System/Script Code` nodes run Python 3.12 and Lua 5.1/LuaJIT through a bidirectional C bridge (Lupa).
* **Pre-Generation Linter:** Static validator (`node_validator.py`) with real-time AST analysis of ASS Dark Tags, undeclared variables, and topological integrity.
* **ASS Render Telemetry and Profiling (`libass` + QPC):** Multi-process, frame-by-frame measurement of render cost, frame budget consumption, and bitmap memory, with an interactive heatmap in the player. Native on Windows; on Linux and macOS it runs through Wine (provisional workaround).
* **Persistence and Templates:** Full graph export/import, session isolation, and template storage in `%APPDATA%\PyxisNodes\` (Windows) or `~/.local/share/PyxisNodes` (Linux/macOS).

---

## Official Technical Manual

The technical manual is split into 12 volumes, in British English in [`PyxisNodes/docs/en/`](PyxisNodes/docs/en/) (Spanish version in [`PyxisNodes/docs/es/`](PyxisNodes/docs/es/)):

| Volume | Title | Primary Technical Scope |
| :---: | :--- | :--- |
| **01** | [Visual Paradigm and Architecture](PyxisNodes/docs/en/01%20Visual%20Paradigm.md) | DAG principles, context lifecycle, expression classification, and `libass` render telemetry. |
| **02** | [Interface Anatomy and Controls](PyxisNodes/docs/en/02%20Interface%20Anatomy.md) | Toolbar, navigation drawer, node canvas, modal dialogues, and keyboard shortcuts. |
| **03** | [Basic Nodes and Primitive Types](PyxisNodes/docs/en/03%20Basics.md) | `Number`, `String`, `Text`, `Color Picker`, `Math`, `MultiRandom`, `Concatenate`, `Dynamic Format`, `MultiTag`, `Only`, `Once`. |
| **04** | [System Nodes and Pipeline](PyxisNodes/docs/en/04%20System.md) | `Output`, `Previewer`, `Script Code`, `Benchmark Math`, rendering pipeline, and queue sorting. |
| **05** | [Loops and Iteration Control](PyxisNodes/docs/en/05%20Loops.md) | `Main Loop` (syllables, words, characters), `MaxLoop` (FBF and particles), and the `Module` operator. |
| **06** | [Vector Geometry and Morphology](PyxisNodes/docs/en/06%20Shapes.md) | Primitives, `Library`, `IMG to Shape`, `Stroke`, `Walker`, `Slicer`, `Array`, `Concentric`, `Multi`, `Manipulator`, `Transform`, `Filter`, `Clipper`, `Union & Divide`. |
| **07** | [Timing and Interpolation](PyxisNodes/docs/en/07%20Times.md) | Retiming phases, `Lead In`/`Out` offsets, `Synced` inter-line continuity, `Middle` intervals, `Loop` cycles, conversions, and `Ipol` curves. |
| **08** | [Kinematic Functions and Modulators](PyxisNodes/docs/en/08%20Functions.md) | `Tag Manipulator`, `Tag Oscillator`, `Glitter`, `Conditioner`, `Animation`, `Color Gradient`, `Clip Gradient`, `IMG to pixels`, `Polar to Cartesian`, `Bezier` splines, particles, and vector text. |
| **09** | [Variables and Context Management](PyxisNodes/docs/en/09%20Variables.md) | Formal metric hierarchy, DAG iterator isolation, `Sys Var`, `Define Vars`, `Get Var`, `Memory`, and Type A/B/C classification. |
| **10** | [Audio Processing and Reactivity](PyxisNodes/docs/en/10%20Audio.md) | PCM decoding, $\mathcal{O}(1)$ Prefix Sums RMS calculation, peaks, envelopes, FFT, and `Modulator` / `Waveform` modes. |
| **11** | [Base Environment and Standalone Rendering](PyxisNodes/docs/en/11%20Base%20Environment%20and%20Customisation.md) | Standalone Base Mode independent of Aegisub, kinematic window with 2000 ms padding, canvas templates, and SHA-256 cache invalidation. |
| **12** | [Scripting and Advanced Programming](PyxisNodes/docs/en/12%20Scripting%20and%20Advanced%20Programming.md) | Dual Python/Lua runtime, functional ASS tag generators, kinematics, persistent memory, and the deterministic `by.<iter>.<R>` dispatcher. |

---

## Quick Installation and Usage

Installation is the same on every platform:

1. Download [`pyxis.NodeEngine.lua`](https://github.com/Mandholine/Pyxis-Effector/releases/latest/download/pyxis.NodeEngine.lua) (it is attached to every release in [**Releases**](https://github.com/Mandholine/Pyxis-Effector/releases)).
2. Copy it into Aegisub's `automation/autoload` folder (see the table).
3. Open Aegisub and run **Automation** $\to$ **Pyxis Node Engine**. The first time, the macro offers to download the engine (`PyxisNodes/`) automatically.

If you would rather install it by hand or offline, download the package for your platform from [**Releases**](https://github.com/Mandholine/Pyxis-Effector/releases) and unzip it into that same folder (it creates `PyxisNodes/`). Each package ships its own Python and ffmpeg, so nothing else needs installing.

| Platform | Package | Aegisub `autoload` folder |
| :--- | :--- | :--- |
| Windows 10 / 11 (64-bit) | `PyxisEffector-v<version>-win64.zip` | `%APPDATA%\Aegisub\automation\autoload\` (user), `C:\Program Files\Aegisub\automation\autoload\` (system-wide) or `<Aegisub_Folder>\automation\autoload\` (portable) |
| Linux x86-64 | `PyxisEffector-v<version>-linux64.zip` | `~/.config/aegisub/automation/autoload/` |
| Linux ARM64 | `PyxisEffector-v<version>-linux-arm64.zip` | `~/.config/aegisub/automation/autoload/` |
| macOS Apple Silicon | `PyxisEffector-v<version>-macos-arm64.zip` | `~/Library/Application Support/Aegisub/automation/autoload/` |
| macOS Intel | `PyxisEffector-v<version>-macos-x64.zip` | `~/Library/Application Support/Aegisub/automation/autoload/` |

> **If you have `Pyxis_engine.lua`** from an earlier version, delete it: it is the same script under another name and Aegisub would load the macro twice.

> ⚠️ **Untested macOS:** the `macos-arm64` and `macos-x64` packages are built automatically but **have not been tested on Mac hardware**. If you use them, bug reports and contributions (issues and PRs) are welcome.

**Requirements:** Aegisub 3.2.x, 3.3.x or 3.4.x (Automation 4). On Windows, also the Microsoft Visual C++ Redistributable (2015-2022 x64); if the Microsoft Edge WebView2 Runtime is missing, Pyxis offers to install it on first launch.

* Linux and macOS (system dependencies, Gatekeeper, installing from source, user data, troubleshooting): [Linux](#linux) and [macOS](#macos), below.
* To build the packages yourself (and to download or compile ffmpeg): [tools/README.md](tools/README.md) (in Spanish).

---

## Linux and macOS

### Linux

The `linux64` or `linux-arm64` package (see the table above) creates `PyxisNodes/` with its own Python 3.12, the dependencies and Qt WebEngine for the interface. You only need what the package cannot carry:

* `ffmpeg`: the package includes one (a GPL build from BtbN with libx264, libass and libwebp, verified by SHA-256). If it was built with `--no-ffmpeg`, install it with your package manager.
* The system libraries Qt WebEngine requires. On a normal desktop they are already installed (`libnss3`, `libxkbcommon`, `libxcb-*`…).

The rest of this section covers **installing from source**.

#### System requirements (installing from source)

| Component | Required | Purpose | Debian / Ubuntu | Arch |
|---|---|---|---|---|
| Python ≥ 3.10 | Yes | Execution engine | `python3 python3-venv` | `python` |
| ffmpeg | Yes | Audio and video | `ffmpeg` | `ffmpeg` |
| WebKitGTK 4.1 | Yes* | GUI (`gtk` backend) | `python3-gi gir1.2-webkit2-4.1` | `python-gobject webkit2gtk-4.1` |
| Qt WebEngine | Alternative* | GUI (`qt` backend) | `python3-pyqt6.qtwebengine` | `python-pyqt6-webengine` |
| fontconfig | Recommended | Font resolution | `fontconfig` | `fontconfig` |
| potrace | Optional | Fast image vectorisation | `potrace` | `potrace` |
| tkinter | Optional | Fallback file dialogues | `python3-tk` | `tk` |
| wmctrl / xdotool | Optional | Raising window focus | `wmctrl` / `xdotool` | same |

\* You need **one** of the two graphical backends. GTK (WebKitGTK) is the recommended one.

Aegisub is available in most distributions (`aegisub` or `aegisub-git`).

#### Installation

```bash
git clone https://github.com/Mandholine/Pyxis-Effector.git
cd Pyxis-Effector/PyxisNodes
./install_linux.sh
```

The installer creates a virtual environment in `PyxisNodes/.venv`, installs the Python dependencies (`requirements.txt`) and checks the system dependencies.

Equivalent manual installation:

```bash
cd PyxisNodes
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt
```

> `--system-site-packages` is required so the virtual environment can see the GTK/Qt bindings (`python-gobject` / PyQt) installed by the distribution's package manager.

#### Using it with Aegisub

1. Copy these into your Aegisub automation folder (`~/.config/aegisub/automation/autoload/`, or `?user/automation/autoload` inside Aegisub):
   * `PyxisNodes/` (the whole folder, including `.venv`)
   * `pyxis.NodeEngine.lua`
2. In Aegisub: **Automation → Pyxis Node Engine**.
3. The macro exports the selected lines, opens the visual editor and, on generation, inserts the effect layers (`pyxis_fx`) into the subtitles.

The flow is identical to Windows:

* The macro looks for the interpreter in this order: `PyxisNodes/python/bin/python3` (release package), `PyxisNodes/.venv/bin/python3`, the system `python3`, and `python`.
* If you cloned the repository, `PyxisNodes/python/` may contain the Windows runtime (`python.exe`); it is not used on Linux. The Linux packages are built with `python tools/build_release.py` and do not share that directory.
* The process is launched detached (`nohup … &`); the local HTTP daemon (`127.0.0.1:28723`) allows instant reopening without relaunching Python.
* If the daemon detects that Aegisub has closed (by PID), it shuts itself down.

Standalone use (without Aegisub):

```bash
cd PyxisNodes
.venv/bin/python main.py
```

#### Data locations (XDG)

User data lives in `$XDG_DATA_HOME/PyxisNodes` (by default `~/.local/share/PyxisNodes`):

| Path | Contents |
|---|---|
| `~/.local/share/PyxisNodes/user_config.json` | Settings, window geometry |
| `~/.local/share/PyxisNodes/temp_cache/` | Temporary bridge with Aegisub |
| `~/.local/share/PyxisNodes/temp/` | Internal temporaries, audio cache |
| `~/.local/share/PyxisNodes/templates/` | User templates |
| `~/.local/share/PyxisNodes/themes/` | Custom themes |

Windows keeps its historical location (`%APPDATA%\PyxisNodes`). macOS uses the same path as Linux.

#### Feature parity

The code remains compatible with Windows.

| Feature | Windows | Linux |
|---|---|---|
| Node editor, preview, particles | ✔ | ✔ |
| Font metrics and outlines | Win32 GDI | **FreeType + fontconfig** (`freetype-py`) |
| Text to vector shape (`text_to_shape`) | GDI outlines | Real FreeType outlines |
| Audio / video | Bundled ffmpeg | Bundled ffmpeg in the release package; the system one if you install from source |
| Image vectorisation | potrace.exe | System potrace (Python fallback) |
| GPU OpenCL / CUDA | ✔ | ✔ (pyopencl / CPU fallback) |
| libass telemetry (`libass_profiler`) | ✔ | ✔ through **Wine** (see below); without Wine, a handled error |
| Child process cleanup | Job Object | `PR_SET_PDEATHSIG` |
| Automatic engine download from the macro | ✔ (win64 zip) | ✔ (linux64 zip) or manual installation |

* `bin/*.exe` is not used on Linux, except `libass_profiler.exe` through Wine.
* To obtain or build your own ffmpeg from the repository, see [tools/README.md](tools/README.md) (`python tools/get_ffmpeg.py` or `python tools/get_ffmpeg.py --build`).

#### Render telemetry (Wine, provisional)

`libass_profiler` exists only as a Windows binary (`bin/libass_profiler.exe`). If `wine` is installed, Pyxis runs it through Wine automatically (it is a console tool and needs no display). This is a provisional workaround until a native port exists:

* The first run creates a dedicated Wine prefix in `~/.local/share/PyxisNodes/wine` (about 10 s); later runs take a fraction of a second.
* Render times are indicative: they measure libass inside Wine, with its own font resolution (DirectWrite over fontconfig) and without the same caches as Windows.
* If you place a native `libass_profiler` in `PyxisNodes/bin/` (or on the `PATH`), it takes priority and Wine is no longer used.
* Environment variables: `PYXIS_DISABLE_WINE=1` (never use Wine), `PYXIS_WINE=<path>` (a different wine executable), `PYXIS_WINEPREFIX=<dir>` (a different prefix).
* Installing Wine: `sudo apt install wine` / `sudo pacman -S wine`.

#### Troubleshooting

* **"Graphical backend NOT available"** → install `python3-gi gir1.2-webkit2-4.1` (GTK) or your distribution's Qt WebEngine package, and recreate the venv with `--system-site-packages`.
* **The macro cannot find Python** → run `install_linux.sh` to create `PyxisNodes/.venv`, or install `python3` on the PATH.
* **Inaccurate font metrics** → install `fontconfig` and check that the family exists (`fc-match "Font Name"`). Pyxis resolves fonts the way Aegisub does: if a family does not exist, fontconfig's substitution is used.
* **The window does not open** → check `~/.local/share/PyxisNodes/temp/*_debug.log` (start-up writes the full traceback there).
* **Audio is not processed** → `ffmpeg` is mandatory; check with `ffmpeg -version`.

### macOS

Pyxis Effector runs on macOS (Apple Silicon and Intel) using Cocoa/WebKit for the interface and the Aegisub Automation 4 macro.

> **Status:** macOS support is implemented but has not yet been tested on Mac hardware. If you hit a problem, open an issue with the contents of `~/.local/share/PyxisNodes/temp/` (start-up logs).

#### Installation (release package, recommended)

Install as described in [Quick Installation and Usage](#quick-installation-and-usage), using `macos-arm64` for Apple Silicon Macs (M1 or later) or `macos-x64` for Intel Macs. The package ships its own Python 3.12 and all dependencies: you do not need Homebrew or a separate Python.

**Gatekeeper.** The packages are not signed with an Apple certificate. If you download them with a browser, macOS quarantines them and blocks the bundled Python. Remove the flag once:

```bash
xattr -dr com.apple.quarantine ~/Library/Application\ Support/Aegisub/automation/autoload/PyxisNodes
```

If the macro downloads the engine itself, it runs that command automatically.

**ffmpeg.** The package includes a native ffmpeg for your architecture (from [ffmpeg.martin-riedl.de](https://ffmpeg.martin-riedl.de), with libx264, libass, libwebp and VideoToolbox, verified by SHA-256). If it was built with `--no-ffmpeg`, install it with Homebrew (`brew install ffmpeg`); Pyxis also searches `/opt/homebrew/bin` and `/usr/local/bin`, even if Aegisub is launched from the Finder with a minimal `PATH`. `potrace` is optional (`brew install potrace`).

To build your own ffmpeg from source, see [tools/README.md](tools/README.md).

#### Installing from source

```bash
brew install python ffmpeg        # Python ≥ 3.10; /usr/bin/python3 is too old
cd PyxisNodes && ./install_macos.sh
```

Then copy `PyxisNodes/` and `pyxis.NodeEngine.lua` into Aegisub's `autoload` folder. The macro uses `PyxisNodes/.venv/bin/python3` if there is no runtime in `PyxisNodes/python/`.

Standalone use: `PyxisNodes/.venv/bin/python PyxisNodes/main.py`.

#### Differences from Windows

| Feature | macOS |
|---|---|
| Interface | Cocoa/WebKit (pywebview) |
| Font metrics and outlines | FreeType; fonts are located in `/System/Library/Fonts`, `/Library/Fonts` and `~/Library/Fonts` |
| Video encoding | `h264_videotoolbox` if ffmpeg includes it; otherwise x264 |
| GPU OpenCL | Optional (Apple has deprecated it); if it fails, the CPU is used |
| libass telemetry (`libass_profiler`) | Only through Wine (see below); without Wine, a handled error |
| Child process cleanup | Parent-process watchdog in each worker |

#### Telemetry through Wine (untested on macOS)

`libass_profiler` exists only as a Windows binary. Pyxis tries to run it through Wine if it finds it (`brew install --cask wine-stable`, Wine Stable/Staging/Devel, or CrossOver in `/Applications`). **This route has not been tested on macOS** (it has on Linux): Wine on macOS exists only for Intel, so on Apple Silicon it needs Rosetta 2. If it does not work, telemetry is disabled with an error message and the rest of Pyxis is unaffected. The details (dedicated prefix, the `PYXIS_WINE` and `PYXIS_DISABLE_WINE` variables, timing accuracy) are the same as on [Linux](#render-telemetry-wine-provisional). A native `libass_profiler` in `PyxisNodes/bin/` will take priority once one exists.

#### Troubleshooting

* **"Cocoa bindings missing"** → reinstall with `pip install --force-reinstall pywebview`.
* **The macro cannot find Python** → reinstall the release package or run `install_macos.sh`.
* **"'python3' cannot be opened because the developer cannot be verified"** → see *Gatekeeper*.
* **The window does not open** → check `~/.local/share/PyxisNodes/temp/*_debug.log` and `preflight_debug.log`.
* **Audio is not processed** → check `ffmpeg -version` from a Terminal.

---

## Team and Contributions

* **Trota** ([@mandholine](https://github.com/Mandholine)): Visual node UI design and implementation, Python engine architecture, Kara Effector ecosystem extensions, and technical documentation.
* **Itachi / Effector** ([@effector2](https://github.com/effector2)): Lua core function libraries, kinematic algorithms, and automation logic. Historical developer of legacy Kara Effector.
* **Zaph** ([@pholguinc](https://github.com/pholguinc)): Architectural design for the initial Python-Lua communication and interoperability bridge.

---

## Historical Acknowledgments

Thanks to the developers and contributors of the historical **Kara Effector 3.6 legacy** project, whose ideas and subtitle automation algorithms inspired this visual node architecture.

---

## Third-Party Code and External Credits

Pyxis Effector uses the following open-source libraries and components:

* [**LiteGraph.js**](https://github.com/jagenjo/litegraph.js): Interactive visual canvas and node graph execution engine (MIT Licence).
* [**Ace Editor**](https://github.com/ajaxorg/ace): Embedded code editor for scripting nodes (BSD Licence).
* [**ArtPlayer.js**](https://artplayer.org/): HTML5 multimedia video player (MIT Licence).
* [**JASSUB**](https://github.com/ThaUnknown/jassub) / [**libass**](https://github.com/libass/libass): WebAssembly-compiled ASS subtitle renderer (MIT / ISC / GPL Licences).
* [**Clipper2**](https://github.com/AngusJohnson/Clipper2) / [**PyClipper**](https://github.com/fonttools/pyclipper): Polygon clipping, boolean operations, and contour offsetting engine (BSL-1.0 Licence).
* [**Potrace**](https://potrace.sourceforge.net/): Bitmap-to-vector curve tracing utility (GPL v2+ Licence).
* [**KaTeX**](https://katex.org/): Maths typesetting for the interface and documentation (MIT Licence).
* [**Marked.js**](https://marked.js.org/): Markdown parser and compiler for integrated documentation and tooltips (MIT Licence).
* [**Lupa**](https://github.com/scoder/lupa): C bridge between Python and LuaJIT / Lua 5.1 (MIT Licence).
* [**PyWebView**](https://pywebview.flowrl.com/): Native desktop webview window for Windows, macOS and Linux (BSD-3 Licence).
* [**FFmpeg**](https://ffmpeg.org/): Multimedia decoding, PCM stream extraction, and video processing. The core is LGPL v2.1+, but the packages ship **GPL v2+** builds (with libx264, libass and libwebp) from [BtbN](https://github.com/BtbN/FFmpeg-Builds) (Windows and Linux) and [martin-riedl.de](https://ffmpeg.martin-riedl.de) (macOS).
* [**Python**](https://www.python.org/) via [**python-build-standalone**](https://github.com/astral-sh/python-build-standalone): Standalone interpreter bundled in every package (PSF Licence).
* [**PyQt6**](https://www.riverbankcomputing.com/software/pyqt/) / [**Qt WebEngine**](https://www.qt.io/): Graphical interface bundled in the Linux packages (GPL v3 / LGPL v3 Licences).
* [**FreeType**](https://freetype.org/) / [**freetype-py**](https://github.com/rougier/freetype-py): Font metrics and outlines on Linux and macOS (FreeType / BSD Licences).
* [**NumPy**](https://numpy.org/) / [**Pillow**](https://python-pillow.org/): Particle, audio and image processing (BSD-3 / HPND Licences).
* [**Wine**](https://www.winehq.org/): Optional; runs `libass_profiler.exe` on Linux and macOS (LGPL v2.1+ Licence).
* [**Aegisub**](https://github.com/TypesettingTools/Aegisub): The interface icon for the active-project mode is `aegisub-icon-mk2.svg` (BSD-3-Clause Licence, © 2004-2012 Aegisub Project).

---

## AI Disclosure

* The technical design and web interface architecture were developed with help from **Google Gemini** via **Antigravity**.
* Linux and macOS support (engine adaptation, packaging with a bundled Python, continuous integration and the `tools/` scripts) was developed with help from AI models: **Claude** (Anthropic) and **MiMo 2.6 Pro** (Xiaomi), the latter through **OpenCode Go**.

---

## Licence

Copyright (C) 2026 @mandholine, @effector2, @pholguinc and the Pyxis Effector contributors.

This project is distributed under the terms of the **GNU General Public License v3.0 (GPL-3.0)**. Full text is available in the [LICENSE](LICENSE) file.

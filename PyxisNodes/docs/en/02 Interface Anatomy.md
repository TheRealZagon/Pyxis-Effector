# Interface Anatomy

Pyxis Effector is a node-graph workspace: a main editing canvas surrounded by a few control panels.

---

## 1. General Workspace Layout

The main window has four zones:

```
+-------------------------------------------------------------------------------+
| [1] TOP BAR                                                                   |
+-------------------------------------------------------------------------------+
|                                                                               |
|                                                                               |
| [2] CANVAS WORKSPACE                                                          |
|     (Nodes, connection ports, data cables, and loop/flow links)               |
|                                                                               |
|                                                                               |
|                                                        +----------------------+
| [3] FLOATING CANVAS TOOLBAR                            | [4] TOAST SYSTEM     |
+-------------------------------------------------------------------------------+
```

1. **Top Bar:** Save/export, template library, global preferences, and layer generation.
2. **Canvas Workspace:** Two-dimensional area where you add, arrange, and connect nodes.
3. **Floating Canvas Toolbar:** Navigation, zoom, camera centring, and history (*undo/redo*).
4. **Toast Notification System:** Non-intrusive alerts in the bottom-right corner showing status, diagnostics, and processing times.

---

## 2. Top Bar and Generation Controls

The top bar is fixed along the top edge of the window:

```
+-------------------------------------------------------------------------------------------------+
| [1] Brand & Version | [2] Save | [3] Save as... | [4] Library | [5] Settings | [6] Generate Layers |
+-------------------------------------------------------------------------------------------------+
```

1. **Version Identifier:** Engine name and a version badge (`v<versión>`).

2. **Save (`Save` / `Ctrl+S`):** Saves changes to the currently open template or project file.

3. **Save As (`Save as...`):** Exports the whole graph to an external `.json` file for backup or distribution.

4. **Template Library (`Library`):** Opens a modal dialogue to search, tag, categorise, and load preset or user-created templates. Can filter by Favourites, Recents, and System Presets.

5. **Quick Save (`Quick Save`):** Becomes active when you modify a template loaded from the library, and overwrites it in one click.

6. **Settings (`Settings`):** Canvas theme, background (active Aegisub video, reference image, or solid colour), language, and hardware acceleration options.

7. **Generate Layers (`Generate Layers`):** Compiles the graph and writes the generated dialogue lines into Aegisub's active ASS script. Includes a progress bar.

8. **Workload Estimation Card:** Appears when you hover over **Generate Layers**:
   * **Lines to generate:** Estimated number of ASS dialogue events that will be written into the script.
   * **Input lines:** Number of subtitle lines selected in Aegisub for processing.
   * **Base units:** Total syllables, words, or characters, according to the active iterator in `Main Loop`.
   * **Heavy Load Warning:** Visual alert if the combined graph complexity exceeds the recommended computational thresholds.

---

## 3. Canvas Workspace

A two-dimensional editing space with free camera navigation, zoom, and multi-selection.

### 3.1. Visual Layer Architecture (*Z-Index Stacking*)
1. **Backdrop Layer:** Neutral background, static reference image, or a video frame loaded from Aegisub, for spatial alignment.
2. **Main Node Canvas Layer (`#node_canvas`):** Node containers, titles, connection ports, text fields, and interactive widgets.
3. **Foreground & Connection Layer (`#node_canvas_fg`):** Cable Bézier curves, multi-selection bounding boxes, and magnetic snapping guides.

### 3.2. Floating Canvas Toolbar
Located in the bottom-left corner of the canvas:

1. **Undo (`Undo` / `Ctrl+Z`):** Reverts the most recent canvas change.
2. **Redo (`Redo` / `Ctrl+Y`):** Restores the most recently undone action.
3. **Centre View (`Home` / `Reset View`):** Moves the camera to fit all nodes in the viewport at an optimal zoom.
4. **Zoom In (`Zoom In` / `+`):** Zooms in on the viewport centre.
5. **Zoom Out (`Zoom Out` / `-`):** Zooms out for an overview of the whole graph.
6. **Default Preset (`Default Preset`):** Resets the canvas to the initial graph (`Main Loop` $\to$ `Output`).

---

## 4. Structural Anatomy of a Node

Standard structure of a node on the canvas:

```
+-------------------------------------------------------------+
| [1] HEADER: Node Title             [4] Mode Selector [v]    |
+-------------------------------------------------------------+
| [2] INPUTS & INLINE FIELDS            |  [3] OUTPUT PORTS   |
| (o) [ Loop In                   ]     |        Loop Out (o) |
| (o) [ 100.0 (or placeholder)    ]     |          Result (o) |
| (o) [                           ]     |        Data Out (o) |
+-------------------------------------------------------------+
| [5] SELECTION BORDER & STATUS         [6] FOOTER / BADGES   |
+-------------------------------------------------------------+
```

1. **Node Header:**
   * Shows the node title in its category colour.
   * Drag it to move the node; double-click to collapse or expand the body.

2. **Input Ports with Inline Fields:**
   * Each input on the left has a circular socket `(o)` and an **editable text field**.
   * **Placeholder text:** When the field is empty, it shows the parameter name and default value in a subdued colour (e.g. `Min`, `Max`, `Delay (ms)`).
   * **Cable vs inline precedence:** A constant or expression typed into the field is evaluated by the node. If a cable is connected to the socket `(o)`, **the cable's data takes absolute precedence** and the inline field is ignored.
   * **Exception (`Output`):** The terminal `Output` node has no inline fields; it shows assignment label badges (`Loop / Domain`, `Layer`, `Start Time`, etc.).

3. **Output Ports (Right Margin):**
   * Circular sockets paired with the name of the value they emit (`Loop Out`, `Data`, `Result`, `Shape Out`, `\t Out`, etc.).

4. **Header Mode Combos:**
   * Dropdown menus in the top-right corner of the title bar.
   * Switch the node's algorithm or behaviour (e.g. `syl / char / word / line` in `Main Loop`, `Normal / FBF` in `MaxLoop`, modes in `Manipulator`, or `Python / Lua` in `Script Code`) and reconfigure the body inputs accordingly.

5. **Selection Border & Status:**
   * A glow around the node when it is selected or being edited.

6. **Footers and Badges:**
   * Show the iteration variables exposed to the execution context (`s_i, s_n` in Slicer, `a_i, a_n` in Array, `b_i, b_n` in Concentric Borders, `ish_i, ish_n` in IMG to Shape) or special node flags (`Single shape.`, `ALL`, `SELEC.`, `NO BLANK`).

---

## 5. Categories and Colour Coding

Pyxis has 67 nodes in 8 categories, each with its own colour:

| Category | Functional Role | Example Nodes | Colour |
| :--- | :--- | :--- | :--- |
| **`Basics`** | Numeric constants, strings, arithmetic, dynamic formatting, and basic routing. | `Math`, `Number`, `String`, `Text`, `Color Picker`, `MultiRandom`, `Concatenate`, `Once`, `Only` | Sky Blue (`#4A90E2`) |
| **`Shape`** | Vector primitives, boolean clipping (Clipper2), paths, affine transforms, morphing, and meshes. | `Library`, `Slicer`, `Manipulator`, `Transform`, `Filter`, `Concentric Borders`, `Stroke`, `Array`, `IMG to Shape` | Emerald Green (`#2ECC71`) |
| **`Time`** | Temporal synchronisation, accelerated timing (`\t`), parametric interpolation (`Ipol`), and offsets. | `Retime`, `Lead In`, `Lead Out`, `Synced`, `Middle 1/2`, `Loop 1/2`, `Ipol`, `Duration`, `Offset` | Golden Orange (`#F39C12`) |
| **`Functions`** | Tag modulators, wave oscillators, colour gradients, Bézier splines, and particle systems. | `Tag Manipulator`, `Tag Oscillator`, `Color Gradient`, `Clip Gradient`, `Bezier Curve`, `Particles`, `Text to Shape` | Violet Purple (`#9B59B6`) |
| **`Variables`** | ASS context variables, persistent key-value memory, and dynamic variable definitions. | `Sys Var`, `Define Vars`, `Get Var`, `Memory` | Turquoise (`#1ABC9C`) |
| **`Loops`** | Line decomposition, event multipliers, and modular steppers. | `Main Loop`, `MaxLoop`, `Module` | Coral Red (`#E74C3C`) |
| **`Audio`** | Spectral audio analysis (FFT), RMS/Peak envelope extraction, and vector waveforms. | `Modulator`, `Waveform` | Amber Yellow (`#F1C40F`) |
| **`System`** | Final ASS assembly, WASM-accelerated preview, custom code scripts, and math benchmarks. | `Output`, `Previewer`, `Script Code`, `Benchmark Math` | Steel Grey (`#7F8C8D`) |

---

## 6. Navigation, Gestures, and Keyboard Shortcuts

| Action | Mouse / Keyboard Control | Result |
| :--- | :--- | :--- |
| **Pan Canvas** | Middle Mouse Button (wheel click) or Right-click and drag | Pans the camera in any direction. |
| **Adjust Zoom** | Mouse Scroll Wheel | Smoothly zooms in or out. |
| **Select / Move Node** | Left-click header and drag | Selects and moves nodes individually. |
| **Box Multi-Selection** | Left-click and drag on empty canvas background | Draws a rectangular selection box. |
| **Create Connection (Cable)** | Drag from output socket `(o)` to input socket `(o)` | Connects two compatible nodes with an elastic wire. |
| **Disconnect Port** | Click on a connected socket | Detaches and removes the cable. |
| **Node Spawn Context Menu** | Right-click on empty canvas background | Opens the node catalogue and quick search palette. |
| **Delete Nodes / Cables** | `Delete` or `Backspace` key | Removes all selected elements. |
| **Duplicate Nodes** | `Ctrl + D` or `Ctrl + C` / `Ctrl + V` | Clones selected nodes, keeping their parameters. |
| **Save Project / Template** | `Ctrl + S` | Saves changes to the active graph. |
| **Undo / Redo** | `Ctrl + Z` / `Ctrl + Y` | Steps through the canvas history. |
| **Centre View on Graph** | `Home` key or Toolbar button | Fits all graph nodes in the viewport. |
| **Integrated Debug Console** | `F1` key (or `Esc` to close) | Opens the real-time log console (works even during window initialisation). |

---

## 7. Modal Windows and Dedicated Editors

1. **Script Code Editor (`Script Code`):**
   * Editor for Python and Lua with syntax highlighting, line numbers, and live error validation (unclosed `end` blocks, missing colons, mismatched delimiters).
   * Template manager to store and load reusable functions.

2. **Colour Picker (`Color Picker`):**
   * HSV/RGB colour wheel with alpha slider, predefined swatch palettes, and direct export to ASS (`&HBBGGRR&`) and web hex (`#RRGGBB`) formats.

3. **Debug Console (`Debug Console` — `F1`):**
   * Real-time backend log viewer, available at any time (including during window initialisation).
   * Live search filter, auto-scroll toggle, clipboard copy, and log clearing, none of which interrupts background execution or resizes the window.

4. **Template Library (`Library`):**
   * Catalogue with search by name or tags, node count previews, and safe loading with a graph integrity check.

5. **ASS Telemetry Panel and Workload Estimation (`Telemetry`):**
   * **Pre-generation workload tooltip (`Generate Layers`):** Hovering over the generation button shows estimated output lines, **Sweep-Line Concurrency**, **Expansion Ratio**, **Estimated ASS Weight** (`KB`/`MB`), badges for the active subsystems (`FBF`, `Slicer`, `Particles`, `Audio`, `Script`), the latest telemetry summary, and a button that opens `Telemetry`.
   * **Telemetry panel (16:9):** Split into three regions: a live video viewport with a per-frame telemetry HUD (top-left); the frame budget gauge (`Frame Budget %`), KPI cards, and critical hotspots list (top-right); and a full-width multi-metric chart with a minimap at the bottom and 2D navigation (`Scroll Wheel` X-zoom at cursor, `Ctrl/Shift + Wheel` Y-scale, `Middle Mouse Drag` 2D pan, `Left Click/Drag` video scrubbing, and `R`/`Home` to reset zoom).

---

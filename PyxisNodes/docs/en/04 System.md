# System

The **System** category contains the nodes that write the final events into Aegisub, preview them in real time with WebAssembly (JASSUB/libass), run Python and Lua code, and measure execution performance.

---

## 1. Node `System/Output` (Terminal Assembler and ASS Emitter)

The mandatory last node of a graph. It compiles the incoming events, resolves style and font-scale precedence, sorts the output into queues and writes the resulting dialogue lines into Aegisub's active subtitle script.

![System/Output](img/output.jpg)

### 1.1. Header Mode Combos
1. **`[2.1] Apply to` (`apply_to`):** Which dialogue lines of the Aegisub script the graph is applied to:
   * `Sel. Lines` (*Selected Lines*): Only the lines selected in the Aegisub grid.
   * `Style Lines`: Lines whose style matches that of the active selection.
   * `All Lines`: Every dialogue line in the subtitle file.

### 1.2. Input Ports
1. **`Loop / Domain`:** Main flow signal from the last node of the branch (`Main Loop`, `MaxLoop`, `Script Code`).
2. **`Layer`:** ASS layer number of the generated line (e.g. `0`, `1`, `5`). If unwired, it keeps the layer of the original line.
3. **`Start Time`:** Start time override in milliseconds. If unwired, it uses the `start_time` calculated by the active context.
4. **`End Time`:** End time override in milliseconds. If unwired, it uses the `end_time` calculated by the active context.
5. **`Tags`:** Consolidated ASS tag block (`{\pos...\1c...\blur...}`), written at the start of the dialogue event.
6. **`Return`:** Text of the event: plain dialogue or ASSdraw vector paths (`m ... l ... b ...`).
7. **`Queue ID`:** Optional alphanumeric identifier that groups the generated lines into a logical queue. It is written to the `Actor` field of each `Dialogue:` line.
8. **`Queue Order`:** Integer priority that sets where the queue is placed in the subtitle document.

### 1.3. Body Properties
1. **`[2.2] Queue ID` (`queue_id`):** Queue identifier used when the input port is unwired (default: `""` $\to$ `"default"` queue).
2. **`[2.3] Queue Order` (`queue_order`):** Queue priority used when the input port is unwired (default: `""` $\to$ order `0`).
3. **`origin_align`:** Numeric origin alignment used to compute anchors (default: `5` / Centre).

### 1.4. Output Ports
1. **`[1.1] Preview`:** Sends the compiled events to `System/Previewer`.

### 1.5. Compilation
For each line, the node:
1. Validates `start_time` and `end_time`, ensuring $t_{\text{end}} \ge t_{\text{start}}$.
2. Merges the tags received in `Tags`, removing direct syntactic duplicates.
3. Resolves **scale precedence (`\fscx`/`\fscy`)**. If the ASS style has a scale other than 100%, libass and VSFilter would distort vector paths defined in absolute coordinates. To avoid this, the engine applies four tiers:
   * **Tier 1 (Plain text or karaoke):** No scale tags are added. The text inherits the scale of the ASS style.
   * **Tier 2 (ASS Style):** Sets the baseline font scale.
   * **Tier 3 (Vector shapes):** If the payload is a vector path (`\p1`, ASSdraw `m ...`), the engine injects `\fscx100` and `\fscy100` to cancel the style scale and keep proportions 1:1 on screen.
   * **Tier 4 (Explicit user tag):** If `\fscx` or `\fscy` is wired or typed into `Tags`, it overrides the neutral default.
4. Tracks style state (`ActiveStyleState`):
   * **Fast path:** If the line has no override tags (plain karaoke such as `{\k50}`), the state machine is skipped.
   * **Per-syllable state machine:** If the line contains override tags (`\pos`, `\an`, `\fs`, `\fscx`, `\fscy`, `\fsp`, `\b`, `\i`, `\bord`, `\shad`, `\1c`..`\4c`, `\alpha`, `\1a`..`\4a`, `\frz`, `\r`), the modifications are accumulated block by block.
   * **Text measurement:** The `width` and `height` of each unit are measured with the font engine, using the active font size and format overrides.
   * **Positioning:** An explicit `\pos(x,y)` anchors the line to those coordinates according to the effective alignment `\an`. The derived coordinates are passed on to the child syllables and characters.
   * **Inheritance:** Context units (`syl`, `char`, `word`, `line`) resolve style properties in cascade: `Unit -> Line -> Style -> Defaults`.
   * **Spacing:** When the ASS style defines `Spacing > 0` or an inline `\fsp` tag is present, the effective horizontal spacing is $S_{\text{eff}} = \text{Spacing} \times \frac{\text{ScaleX}}{100} \times \text{FactorX}$. It is applied uniformly between adjacent syllables and between individual glyphs (`char.left`, `char.center`, `char.right`), matching libass/VSFilter alignment.
5. Writes the line in standard ASS format, with `Queue ID` in the `Actor` field:
   $$\texttt{Dialogue: } \text{Layer}, \, t_{\text{start}}, \, t_{\text{end}}, \, \text{Style}, \, \mathbf{Queue\_ID}, \, \text{MarginL}, \, \text{MarginR}, \, \text{MarginV}, \, \text{Effect}, \, \texttt{\{Tags\}} \text{Return}$$

Queues are sorted once all branches have finished:
* **Branch isolation:** Each `Output` node evaluates its branch with its own context container. It shares no variables or kinematic state with other terminal nodes.
* **Global order:** Lines are grouped by `Queue ID` and written into the ASS document using the key:
  $$\text{SortKey}(Q) = \left(\min_{l \in Q}(\text{queue\_order}_l), \, \text{qid}\right)$$
  * **1. Numeric priority:** Queues with a lower `Queue Order` come first.
  * **2. Alphabetical tiebreaker:** Queues with the same order are sorted alphabetically by `Queue ID`.
  * **3. Default queue:** An omitted identifier falls into the `"default"` queue.
  * **4. Order inside a queue:** Lines keep their original event sequence:
    $$\text{SortKey}(l) = (\text{queue\_order}_l, \, \text{line\_idx}_l)$$

### 1.6. Tips
* **Multilayer rendering:** Use separate `Output` nodes for separate layers (e.g. Layer 0 for shadows with `Queue Order = 1`, Layer 1 for the main text with `Queue Order = 2`).
* **Queue IDs as labels:** Descriptive identifiers such as `"FX_Outline"` or `"FX_Body"` make it easy to filter, inspect and toggle the generated lines in the Aegisub grid.

---

## 2. Node `System/Previewer` (WebAssembly Real-Time Player)

Plays video and subtitles in real time using WebAssembly (JASSUB/libass). Playback is limited to the time window of the effect and needs no pre-rendering.

![System/Previewer](img/previewer.jpg)

### 2.1. Input Ports
1. **`Output`:** Connects to the `Preview` port of one or more `Output` nodes. Several can be wired at once to preview multiple layers together.

### 2.2. Header Actions
1. **`[1.1] Source Toggle`:**
   * **Base Preset (CD icon / `preview_base.ass`):** Isolated sandbox with a preloaded video and template.
   * **Active Aegisub Project (Aegisub icon):** Loads the video, audio, styles and timing of the open Aegisub session.
2. **`[1.2] Pin / Detach Button`:**
   * Detaches the player into a floating window so it stays visible while you move around the canvas.
3. **`[1.3] Refresh Button`:**
   * Recompiles the branches wired to `Output`, updates the subtitle track in JASSUB/libass and profiles the generated lines.
   * **Scene coexistence:** Only the original lines replaced by the `Output` scope (`Sel. Lines`, `Style Lines`, `All Lines`) are commented out in the viewport. Other dialogue and signs stay visible.
4. **`[1.4] Hardsub Render Button (FFmpeg Export)`:**
   * Opens the export dialogue to burn the subtitles (*hardsub*) into an MP4 file with FFmpeg. Transcoding only runs when this button is used.

### 2.3. Transport Bar and Playback Controls
1. **`[2.1] Relative Scrubber Bar:`** Draggable timeline over the effect duration ($0 \dots T_{\text{dur}}$), synchronised per frame (`requestAnimationFrame`).
2. **`[2.2] Relative Timecode Display:`** Current position and total duration in `MM:SS`.
3. **`[2.3] Volume Controls:`** Mute button and gain slider.
4. **`[2.4] Previous Frame (-1 Frame):`** Steps back one frame.
5. **`[2.5] Jump Backward (-10s):`** Moves playback 10 seconds back within the effect window.
6. **`[2.6] Play / Pause Toggle`**
7. **`[2.7] Jump Forward (+10s):`** Moves playback 10 seconds forward within the effect window.
8. **`[2.8] Next Frame (+1 Frame):`** Steps forward one frame.
9. **`[2.9] Settings Menu:`** Loop toggle and playback speed ($0.25\times, 0.5\times, 1.0\times, 1.5\times, 2.0\times$).
10. **`[2.10] Fullscreen Toggle`**
11. **`[2.11] Solid Neutral Grey Background:`** Standalone audio tracks are shown over a neutral grey backdrop (`#2a2a2a`) so subtitles stay readable.
12. **`[2.12] Thermal Heatmap:`**
    * Plots the per-frame rendering cost of the generated lines as a spline curve, coloured against the frame budget ($\text{Budget}_{\text{ms}} = 1000 / \text{FPS}$): cyan (low load), green (moderate), orange (near the limit) and red (budget exceeded, $>100\%$).
    * Hovering over the seekbar expands the curve vertically and shows the reference grid, latency readouts (`MM:SS.mmm · X.X ms`) and a **`TELEMETRY ↗`** shortcut.

### 2.4. Viewport Zoom and Pan
1. **Mouse wheel:** Zooms in or out around the pointer, from $1.0\times$ to $8.0\times$.
2. **Middle mouse button:** Drag to pan the magnified viewport.
3. **`R` key:** Over the player, resets zoom to $1.0\times$ and centres the viewport.

### 2.5. Docking with the `Telemetry` Panel
Opening the **`Telemetry`** panel from the heatmap has two effects:
1. **Player transfer:** The active player moves into the panel, keeping the current frame, zoom level and playback state. Closing the panel returns it to the canvas.
2. **Bidirectional seeking:** Scrubbing the charts or clicking a critical event seeks the player to that frame.

### 2.6. Tips
* Wire `Preview` to check timing and look before writing lines into Aegisub.
* Peaks in the heatmap usually point to excessive blur (`\blur`) or complex clip masks (`\clip`).

---

## 3. Node `System/Script Code` (Embedded Python & Lua)

Runs inline Python 3.12 or Lua 5.1/LuaJIT code inside the graph, with access to the ASS context variables and to tag utility functions.

![System/Script Code](img/script_code.jpg)

### 3.1. Header Mode Combos
1. **`[1.1] Language` (`language`):** Execution engine:
   * `Python`: Native Python 3.12 with the standard modules `math`, `random` and `re`.
   * `Lua`: Standard Lua through Lupa/LuaJIT, compatible with traditional Aegisub macro syntax.

### 3.2. Ports
1. **`Loop In`:** Execution flow input.
2. **`In1`, `In2`, $\dots$, `InN`:** Dynamic data inputs, available in the script as `in1`, `in2`, etc.
3. **`[2.1] Loop Out`:** Passes the flow to the downstream nodes.
4. **`[2.2] Result`:** Emits the value assigned to `result` (text, ASS tags or vector paths).

### 3.3. Body Properties
1. **`script`:** Code to execute (default: `result = 'Hello Pyxis ' + str(in1 if in1 else syl.text)`).
2. **`inputs_count`:** Number of dynamic input sockets (default: `2`).

### 3.4. Variables and Functions in Scope

Python and Lua scripts both have access to:

| Variable / Object | Description | Primary Attributes |
| :--- | :--- | :--- |
| `syl` | Active context syllable | `x, y, center, middle, left, right, top, bottom, start_time, end_time, dur, text, text_stripped, i, n, prev, next, is_first, is_last, has_prev, has_next, ink` |
| `char` | Active context character | `x, y, center, middle, left, top, start_time, end_time, dur, text, i, n, prev, next, is_first, is_last, has_prev, has_next, ink` |
| `word` | Active context word | `x, y, center, start_time, end_time, dur, text, i, n, prev, next, is_first, is_last, has_prev, has_next, ink` |
| `line` / `l` | Complete dialogue line | `text, raw_text, style, layer, start_time, end_time, duration, margin_l, margin_r, margin_v, actor, effect, ink` |
| `prev` / `next` | Preceding and following neighbour units | Metrics and text of the adjacent units (`prev.text`, `prev.dur`, `prev.x`, `next.x`) |
| `is_first` / `is_last` | Boundary flags | `True` if the unit is first / last in the sequence |
| `has_prev` / `has_next`| Neighbour flags | `True` if an adjacent neighbour exists |
| `ink` | True ink contour metrics | `ink.width`, `ink.height`, `ink.center`, `ink.middle`, `ink.left`, `ink.right`, `ink.top`, `ink.bottom` |
| `fx` | Kinematic override structure | `pos_x, pos_y, org_x, org_y, start_time, end_time, dur, align, i, n` |
| `in1`, `in2`, $\dots$ | Connected data inputs | Values received at ports `In1`, `In2`, etc. |
| `outputs` / `out` | Multiple outputs | Assignment by name (`outputs["Custom"] = val`) or index (`out2 = val`). |
| `result` | Primary output | Content emitted through the `Result` port. |

#### Utility functions
* **ASS tag constructors:** `pos(x,y)`, `move(x1,y1,x2,y2[,t1,t2])`, `org(x,y)`, `fad(in,out)`, `fade(...)`, `clip(shp)`, `iclip(shp)`, `c1(col)`, `c2(col)`, `c3(col)`, `c4(col)`, `alpha(a)`, `trans(tags)`, `fscx(v)`, `fscy(v)`, `frz(v)`, `blur(v)`, `bord(v)`, `shad(v)`.
* **Interpolation and maths:** `clamp(v,min,max)`, `lerp(a,b,t)`, `map_range(v,in_min,in_max,out_min,out_max)`, `ease_in(t)`, `ease_out(t)`, `ease_in_out(t)`, `cubic_in(t)`, `cubic_out(t)`, `elastic(t)`, `bounce(t)`, `back(t)`.
* **Periodic waves:** `sine_wave(t,freq,amp,offset)`, `square_wave(...)`, `triangle_wave(...)`, `sawtooth_wave(...)`.
* **Time and text:** `time_to_frame(ms,fps)`, `duration(obj)`, `parse_ass_time(str)`, `format_ass_time(ms)`, `strip_tags(txt)`.

---

## 4. Node `System/Benchmark Math` (Performance Diagnostics)

Runs an intensive maths workload (trigonometry, prime sieve or matrix multiplication) and reports the elapsed time in milliseconds.

![System/Benchmark Math](img/benchmark_math.jpg)

### 4.1. Input Ports
1. **`Iterations`:** Number of iterations (default: `10000`). If unwired, the internal property is used.

### 4.2. Body Properties
1. **`[2.1] Complexity` (`complexity`):** Test algorithm:
   * `Heavy Math (Trig + Sqrt)`: Loops of trigonometric functions ($\sin, \cos$) combined with square roots ($\sqrt{x}$).
   * `Prime Sieve`: Prime number checking and sieving.
   * `Matrix Mult`: In-memory $25 \times 25$ matrix multiplication.
2. **`[2.2] Iterations` (`iterations`):** Repetition count (default: `10000`).

### 4.3. Output Ports
1. **`[1.1] Out`:** String with the input data received, or the elapsed time summary formatted as `[Bench: X.XXms]`.
2. **`[1.2] Time ms`:** Total calculation time in milliseconds, measured with `time.perf_counter()`.

### 4.4. Tips
* Insert `Benchmark Math` into large graphs to compare host execution speed before and after optimisations such as `Basics/Once`.

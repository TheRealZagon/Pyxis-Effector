# Variables

The **Variables** category reads values from the ASS context, defines local variables evaluated on every iteration, and stores values that persist between execution cycles.

### Contents
* **Context lifecycle:** time hierarchy, effect-relative timing ($ini$), DAG Trace nesting and iterator isolation.
* **Nodes:** [`Sys Var`](#1-node-variablessys-var-system-and-context-variables) (§1), [`Define Vars`](#2-node-variablesdefine-vars-local-variable-definition) (§2), [`Get Var`](#3-node-variablesget-var-context-variable-reader) (§3), [`Memory`](#4-node-variablesmemory-persistent-key-value-store) (§4).
* **Reference:** comparison table (§5), property types A/B/C and AST resolution (§6), scopes and name collisions (§7), best practices (§8).

---

## Variable Architecture and Context Lifecycle

Context data flows down through the iteration levels (`line` $\to$ `syl` $\to$ `word` $\to$ `char` $\to$ `sub-loops`):

```
+─────────────────────────────────────────────────────────────────────────────+
|                         GLOBAL / PROJECT ENVIRONMENT                        |
|  meta.res_x, meta.res_y, frame_dur, default_audio_source, video_fps         |
+──────────────────────────────────────┬──────────────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
|                            LINE LEVEL (line / l)                            |
|  l.text, l.start_time, l.end_time, l.dur, l.style, l.layer, l.margin_*, ... |
+──────────────────────────────────────┬──────────────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
|                    ACTIVE UNIT LEVEL (syl / word / char)                    |
|  syl.text, syl.x, syl.y, syl.dur, syl.left, syl.center, syl.i, syl.n, ...   |
+──────────────────────────────────────┬──────────────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
|                        LOOP / SUB-LOOP CHAIN LEVEL                          |
|  fx.i, fx.n, fx.pos_x, fx.pos_y, fx.dur, j, maxj, s_i, a_i, p_i, ratio       |
+──────────────────┬──────────────────────────────────────┬───────────────────+
                   │                                      │
                   ▼                                      ▼
+──────────────────────────────────────+ +────────────────────────────────────+
|     LOCAL STATE (Define Vars)        | |    PERSISTENT STATE (Memory)       |
|  Temporary injected variables valid  | |  Key-value store that persists     |
|  strictly within the active cycle.   | |  across all execution cycles.      |
+──────────────────────────────────────+ +────────────────────────────────────+
```

### 0.1. Time Hierarchy

`Dialogue` timestamps are on the global video timeline, but karaoke `\k` tags and `\t(t1, t2, tags)` transforms are relative to the start of the generated line ($[0, \text{fx.dur}]$).

Pyxis tracks time at these levels:

| Entity | Properties | Time base | Effect-Relative Variables ($ini = line.start\_time - fx.start\_time$) |
| :--- | :--- | :--- | :--- |
| **`line` / `l`** | `start_time`, `end_time`, `dur`, `mid_time` | **Global Video Timeline ($ms$)** | Absolute position of the event in the timeline. |
| **`syl`** | `start_time`, `end_time`, `dur`, `mid_time` | **Line-Relative ($[0, line.dur]$)** | $syl.syl\_start = ini + syl.start\_time$<br>$syl.syl\_end = syl.syl\_start + syl.dur$<br>$syl.syl\_mid = syl.syl\_start + \frac{syl.dur}{2}$ |
| **`char`** | `start_time`, `end_time`, `dur`, `mid_time` | **Syllable-Relative ($[0, syl.dur]$)** | $char.char\_start = syl.syl\_start + char.start\_time$<br>$char.char\_end = char.char\_start + char.dur$<br>$char.syl\_start = syl.syl\_start$<br>$char.syl\_end = syl.syl\_end$ |
| **`word`** | `start_time`, `end_time`, `dur`, `mid_time` | **Line-Relative ($[0, line.dur]$)** | $word.word\_start = ini + word.start\_time$<br>$word.word\_end = word.word\_start + word.dur$ |
| **`fx`** | `start_time`, `end_time`, `dur` | **Global Generated ASS Line** | The $[0, fx.dur]$ interval over which libass evaluates $\backslash\text{t}(t_1, t_2, \dots)$. |

#### Lead-in offset ($ini$)
If a timing node (`Time/Lead In`, `Time/Retime`) adds a lead-in $\Delta t_{\text{leadin}}$ to an event starting at $line.start\_time$, the output ASS line starts at:

$$fx.start\_time = line.start\_time - \Delta t_{\text{leadin}}$$

$ini$ is the offset between the two:

$$ini = line.start\_time - fx.start\_time = \Delta t_{\text{leadin}}$$

So a `\t` transform that spans exactly the time a syllable is sung uses:

$$t_1 = syl.syl\_start = ini + syl.start\_time, \quad t_2 = syl.syl\_end = syl.syl\_start + syl.dur$$

### 0.2. Sub-loop Nesting (DAG Trace)

When several piece or particle generators connect to `System/Output`, the engine resolves their dependencies at render time by walking the graph wiring in post-order (**DAG Trace**):

```
                                              ┌───────────────────────────────┐
                                              │     System/Output (Terminal)  │
                                              └───────▲───────────────▲───────┘
                                                      │               │
                                  Return Channel:     │               │ Tags Channel:
                                  Geometry / Pieces   │               │ Modifiers
                                                      │               │
                                          ┌────────────┴───┐       ┌───┴──────────┐
                                          │ Functions/     │       │ Basics/      │
                                          │ Particles      │       │ MultiTag     │
                                          └────────────▲───┘       └──────────────┘
                                                      │
                                          ┌────────────┴───┐
                                          │ Shape/Slicer   │
                                          │ (Outer Loop)   │
                                          └────────────────┘
```

1. **Channel 1 (`Output.Return`, port 5, geometry):** Traced recursively in post-order from the upstream root to the `Return` port. If `Slicer` feeds `Particles` and `Particles` connects to `Return`, `Slicer` is the outer loop ($s_i \in [1, s_n]$) and `Particles` the inner loop ($p_i \in [1, p_n]$ for each slice $s_i$).
2. **Channel 2 (`Output.Tags`, port 4, modifiers):** Traced in post-order following the input order (`In1`, `In2`, ...) and evaluated inside each geometry state emitted by `Return`.

#### Iterators by generator
Each generator family has its own iterator names, so nested generators don't collide:

| Generator Node Family | Ordinal Iterator | Unit Count | Expression Aliases |
| :--- | :---: | :---: | :--- |
| **`Shape/Slicer`** | `s_i` | `s_n`, `s_max` | `slice_i`, `slice_n`, `slice_max`, `col`, `row` |
| **`Shape/Union & Divide`** | `d_i` | `d_n`, `d_max` | `divide_i`, `divide_n`, `divide_max` |
| **`Shape/Concentric Borders`** | `b_i` | `b_n`, `b_max` | `ring_i`, `ring_n`, `ring_max` |
| **`Shape/Array`** | `a_i` | `a_n`, `a_max` | `array_i`, `array_n`, `array_max`, `col`, `row` |
| **`Shape/Multi`** | `m_i` | `m_n`, `m_max` | `multi_i`, `multi_n`, `multi_max` |
| **`Functions/Particles`** | `p_i` | `p_n`, `p_max` | `tp_i`, `tp_n`, `tp_max`, `text_p_i`, `text_p_n` |
| **`Functions/IMG to pixels`** | `ip_i` | `ip_n`, `ip_max` | `img_p_i`, `img_p_n`, `total_pixels` |
| **`Functions/Clip Gradient`** | `c_i` | `c_n`, `c_max` | `clip_i`, `clip_n`, `clip_max`, `c_col`, `c_row` |
| **`Functions/Animation`** | `an_i` | `an_n`, `an_max` | `anim_i`, `anim_n`, `anim_max`, `an_j` |
| **`Loops/MaxLoop`** | `j` | `maxj`, `maxloop` | `module`, `m`, `ratio` |

#### Conditional pruning
When tracing upstream, if the engine meets a conditional selector (`Basics/Only`, `Functions/Conditioner`, `Basics/Once`), it evaluates the condition against the current iteration context and follows only the active branch (`True` or `False`). This stops alternative generators from multiplying in series and inactive branches from running phantom iterations.

---

## 1. Node `Variables/Sys Var` (System and Context Variables)

Reads a value from the active context: coordinates, pixel dimensions, timestamps in milliseconds, iteration indices, ASS style properties, project resolution or vector path dimensions.

![Variables/Sys Var](img/sys_var.jpg)

> [!TIP]
> **Variable picker (SysVar Grid Picker):**
> Clicking or editing the **Variable** field opens a picker with live search and categories (*Line*, *Syllable*, *Character*, *Word*, *Effect/FX*, *Loops/Globals*, *Temporal Offset*, *Ink Metrics*, *Meta/Project*, *Neighbors & Context*). Variables are sorted alphabetically within each category, and you select one with a single click instead of typing it.

### 1.1. Header dropdown
The dropdown in the node header sets `var_name`. Pick a common variable or type any identifier.

### 1.2. Inputs and properties
1. **`Variable` (`var_name`):** Variable name or property path to read (e.g. `"syl.text"`, `"line.start_time"`, `"fx.pos_x"`, `"meta.res_x"`, `"shape.width"`). Default: `"syl.text"`.
   * Type C (plain text / identifier). It is not parsed with `ast.parse`, so it never raises false syntax errors.
   * The node has no input ports; the value comes straight from the execution context.

### 1.3. Outputs
1. **`[1.1] Data`:** The requested value, as text or a number. If the variable doesn't exist in the context, emits an empty string `""` or `0.0`.

### 1.4. Available variables

The tables below list the context variables you can use in `Sys Var`, in `Define Vars`, in `Script Code` scripts and in parenthesised `\tag(var)` expressions.

#### 1.4.1. Line (`line.` or `l.`) and original style
The active dialogue line and its style from the `[V4+ Styles]` section of the ASS script. Style properties reflect the base style (`StyleRef`) or any earlier inline overrides:

| Variable | Type | Description and Units |
| :--- | :---: | :--- |
| `line.text` / `l.text` | `string` | Dialogue text without override tags and karaoke markers. |
| `line.raw_text` / `l.raw_text` | `string` | Line text with all `{\...}` override tags and `\k` markers kept. |
| `line.start_time` / `l.start_time` | `int` | Line start timestamp in milliseconds ($ms$). |
| `line.end_time` / `l.end_time` | `int` | Line end timestamp in milliseconds ($ms$). |
| `line.dur` / `line.duration` / `l.dur` | `int` | Line duration in milliseconds: $t_{\text{end}} - t_{\text{start}}$. |
| `line.mid_time` / `l.mid_time` | `float` | Temporal midpoint of the line: $t_{\text{start}} + \frac{t_{\text{dur}}}{2}$. |
| `line.i` / `l.i` | `int` | Index of the active line in the batch ($1 \dots N$). |
| `line.n` / `l.n` | `int` | Number of selected lines in the batch. |
| `line.x`, `line.y` | `float` | Screen coordinates of the line centre (px). |
| `line.left`, `line.right` | `float` | Left and right horizontal boundaries of the line's bounding box (px). |
| `line.top`, `line.bottom` | `float` | Top and bottom vertical boundaries of the line's bounding box (px). |
| `line.middle`, `line.center` | `float` | Vertical and horizontal centre of the line (px). |
| `line.width`, `line.height` | `float` | Width and height of the line (px). |
| `line.descent`, `line.extlead` | `float` | Font descent and external leading (px). |
| `line.layer` / `l.layer` | `int` | ASS layer of the line (Z-order). |
| `line.style` / `line.style_name` | `string` | Name of the line's ASS style (e.g. `"Default"`, `"Romaji"`). |
| `line.actor` / `l.actor` | `string` | Actor / character field of the ASS dialogue line. |
| `line.effect` / `l.effect` | `string` | Special effect field of the ASS dialogue line. |
| `line.margin_l`, `line.margin_r`, `line.margin_v` | `int` | Left, right, and vertical margins defined on the line or style (px). |
| `line.margin_t`, `line.margin_b` | `int` | Top and bottom margins (px). |
| `line.fontname` | `string` | Font family name in the original style (e.g. `"Arial"`, `"Montserrat"`). |
| `line.fontsize` | `float` | Font size of the base style in points ($pt$). |
| `line.bold` | `bool` | Whether the original style is bold (`True` / `False`). |
| `line.italic` | `bool` | Whether the original style is italic (`True` / `False`). |
| `line.underline` | `bool` | Whether the original style is underlined (`True` / `False`). |
| `line.strikeout` | `bool` | Whether the original style is struck out (`True` / `False`). |
| `line.scale_x`, `line.scale_y` | `float` | Horizontal and vertical font scale of the base style ($100.0 = 100\%$). |
| `line.spacing` | `float` | Letter spacing in pixels (`\fsp`). |
| `line.outline` | `float` | Outline thickness in the original style, in pixels (`\bord`). |
| `line.shadow` | `float` | Shadow distance in the original style, in pixels (`\shad`). |
| `line.align` | `int` | Numpad alignment of the base style ($1 \dots 9$). |
| `line.color1` .. `line.color4` | `string` | Original style colours: primary (`\1c`), secondary/karaoke (`\2c`), outline (`\3c`), and shadow (`\4c`) in ASS `&HBBGGRR&` format. |
| `line.alpha1` .. `line.alpha4` | `string` | Original style alpha for the four colours in ASS `&HAA&` format ($0 \dots 255$). |
| `line.frz`, `line.frx`, `line.fry` | `float` | 3D rotation angles of the line or style, in degrees. |
| `line.fax`, `line.fay` | `float` | Horizontal and vertical shear factors. |
| `line.pos_x`, `line.pos_y` | `float` | Position of the line, absolute or overridden (`\pos`). |
| `line.org_x`, `line.org_y` | `float` | Rotation origin (`\org`). |

#### 1.4.2. Syllable (`syl.`), character (`char.`) and word (`word.`)
The syllables, characters and words produced by `Main Loop`. Each unit inherits the style and colour attributes of its parent line's base style or active overrides:

| Variable | Type | Description and Units |
| :--- | :---: | :--- |
| `syl.text` / `word.text` / `char.text` | `string` | Text content of the element stripped of override tags. |
| `syl.text_stripped` / `char.text_stripped` | `string` | Unit text with any embedded tags removed. |
| `syl.text_spacestripped` | `string` | Syllable text additionally stripped of leading and trailing whitespace. |
| `syl.dur` / `syl.duration` | `int` | Syllable duration in milliseconds ($ms$), from the `\k` tag. |
| `syl.start_time`, `syl.end_time` | `int` | Start and end timestamps relative to the **dialogue line** ($ms$). |
| `syl.mid_time` | `float` | Midpoint of the syllable, relative to the line: $t_{\text{start}} + \frac{t_{\text{dur}}}{2}$. |
| `syl.syl_start`, `syl.syl_end` | `int` | Start and end timestamps of the syllable relative to the generated **effect line `fx`** ($\text{ini} + \text{syl.start\_time}$). |
| `syl.syl_mid` | `float` | Midpoint timestamp of the syllable relative to effect line `fx`. |
| `syl.i` / `syl.n` | `int` | Syllable index within line ($1 \dots N$) and total syllables. |
| `syl.x`, `syl.y` | `float` | Screen coordinates of the syllable centre (px). |
| `syl.left`, `syl.right` | `float` | Left and right horizontal boundaries of the syllable bounding box (px). |
| `syl.top`, `syl.bottom` | `float` | Top and bottom vertical boundaries of the syllable bounding box (px). |
| `syl.center`, `syl.middle` | `float` | Horizontal $X$ and vertical $Y$ centre coordinates of the syllable (px). |
| `syl.width`, `syl.height` | `float` | Width and height of the syllable (px). |
| `syl.descent`, `syl.descend` | `float` | Font descent for the syllable (px). |
| `syl.extlead` | `float` | Font external leading (px). |
| `syl.prespace`, `syl.postspace` | `string` | Whitespace before and after the syllable. |
| `syl.prespacewidth`, `syl.postspacewidth` | `float` | Pixel width of the whitespace before and after the syllable. |
| `syl.fontname`, `syl.fontsize` | `string` / `float` | Inherited font family name and font size in points ($pt$). |
| `syl.bold`, `syl.italic` | `bool` | Inherited bold and italic boolean flags. |
| `syl.underline`, `syl.strikeout` | `bool` | Inherited underline and strikeout boolean flags. |
| `syl.scale_x`, `syl.scale_y` | `float` | Inherited font scale factors ($100.0 = 100\%$). |
| `syl.spacing`, `syl.outline`, `syl.shadow` | `float` | Inherited letter spacing (`\fsp`), border outline width (`\bord`), and shadow depth (`\shad`) (px). |
| `syl.color1` .. `syl.color4` | `string` | Primary, secondary, outline, and shadow colours assigned to the syllable (`&HBBGGRR&`). |
| `syl.alpha1` .. `syl.alpha4` | `string` | Primary, secondary, outline, and shadow alpha channels assigned to the syllable (`&HAA&`). |
| `syl.align` | `int` | Active numpad alignment ($1 \dots 9$). |
| `syl.pos_x`, `syl.pos_y` | `float` | Anchor position for the syllable (`\pos`). |
| `syl.org_x`, `syl.org_y` | `float` | Origin / rotation pivot for the syllable (`\org`). |
| `syl.actor`, `syl.style`, `syl.layer`, `syl.effect` | `str`/`int` | Metadata inherited from the parent dialogue line. |
| `char.dur` / `char.duration` | `int` | Duration of the character ($ms$). |
| `char.start_time`, `char.end_time` | `int` | Start and end timestamps relative to its **parent syllable** ($ms$). |
| `char.mid_time` | `float` | Midpoint of the character within its syllable: $t_{\text{start}} + \frac{t_{\text{dur}}}{2}$. |
| `char.char_start`, `char.char_end` | `int` | Start and end timestamps of the character relative to the generated **effect line `fx`** ($\text{syl.syl\_start} + \text{char.start\_time}$). |
| `char.syl_start`, `char.syl_end` | `int` | Start and end timestamps of the parent syllable relative to the generated **effect line `fx`**. |
| `char.i` / `char.n` | `int` | Character index within the line ($1 \dots N$) and total characters. |
| `char.syl_i` | `int` | Index of the character within its syllable ($1 \dots N_{\text{syl}}$). |
| `char.word_i` | `int` | Index of the character within its word. |
| `char.x`, `char.y` | `float` | Screen coordinates of the character centre (px). |
| `char.center`, `char.middle` | `float` | Centre of the character (px). |
| `char.left`, `char.right`, `char.top`, `char.bottom` | `float` | Bounding box of the character (px). |
| `char.width`, `char.height` | `float` | Width and height of the character (px). |
| `char.fontname`, `char.fontsize`, `char.color1`..`4` | `var` | Inherited font and colour properties. |
| `word.dur` / `word.duration` | `int` | Duration of the word ($ms$). |
| `word.start_time`, `word.end_time` | `int` | Start and end timestamps relative to the **dialogue line** ($ms$). |
| `word.word_start`, `word.word_end` | `int` | Start and end timestamps of the word relative to the generated **effect line `fx`** ($\text{ini} + \text{word.start\_time}$). |
| `word.i` / `word.n` | `int` | Word index within line ($1 \dots N$) and total words. |
| `word.x`, `word.y`, `word.center`, `word.middle` | `float` | Screen centre coordinates of the word (px). |
| `word.left`, `word.right`, `word.top`, `word.bottom` | `float` | Bounding box of the word (px). |
| `word.width`, `word.height` | `float` | Width and height of the word (px). |

#### 1.4.3. Neighbouring units and position flags (`prev.`, `next.`, `is_first`, `is_last`, `has_prev`, `has_next`)
Read the neighbouring elements in the chain without storing anything in `Memory`. The `prev` and `next` objects expose the metric, timing and style properties of the adjacent element:

| Variable | Type | Description |
| :--- | :---: | :--- |
| `prev.text`, `prev.text_stripped` | `string` | Text of the previous element in the sequence. |
| `prev.x`, `prev.y`, `prev.center`, `prev.middle` | `float` | Centre of the previous element (px). |
| `prev.left`, `prev.right`, `prev.top`, `prev.bottom` | `float` | Bounding box of the previous element (px). |
| `prev.width`, `prev.height` | `float` | Width and height of the previous element (px). |
| `prev.start_time`, `prev.end_time`, `prev.dur` | `int` | Start time, end time, and duration of the previous element ($ms$). |
| `prev.i`, `prev.n` | `int` | Index and total of the previous element. |
| `prev.fontname`, `prev.fontsize`, `prev.color1`..`4` | `var` | Font and style properties of the previous element. |
| `next.*` | `var` | The same properties for the **next element**. |
| `is_first` | `bool` | `True` if the active element is the first in the sequence (`i == 1` or without predecessor). Also accessible as `syl.is_first`, `char.is_first`, `word.is_first`. |
| `is_last` | `bool` | `True` if the active element is the last in the sequence (`i == n` or without successor). Also accessible as `syl.is_last`, `char.is_last`, `word.is_last`. |
| `has_prev` | `bool` | `True` if a valid predecessor unit exists in the line. |
| `has_next` | `bool` | `True` if a valid successor unit exists in the line. |

#### 1.4.4. Default and global variables
These are available in the evaluation context of every node (`Define Vars`, `MultiTag`, `Conditioner`, etc.) without a prefix:

| Variable | Type | Description and Formula |
| :--- | :---: | :--- |
| `frame_dur` / `fd` | `float` | Duration of one video frame in milliseconds ($\approx 41.67\text{ ms}$ at 23.976/24 FPS or $40.0\text{ ms}$ at 25 FPS). |
| `fps` | `float` | Frame rate of the active video in Aegisub (e.g. `23.976`, `24.0`, `29.97`, `60.0`). |
| `ini` | `float` | Offset between the dialogue line and the effect line: $\text{ini} = \text{line.start\_time} - \text{fx.start\_time}$. |
| `st`, `et` | `int` | Aliases for the active `start_time` and `end_time` ($ms$). |
| `dur` / `duration` | `int` | Duration of the active unit or frame in milliseconds ($ms$). |
| `time_start`, `time_end`, `time_dur` | `int` | Aliases for sub-element or frame timestamps. |
| `line_start_time`, `line_end_time`, `line_dur` | `int` | Start, end, and duration timestamps of the parent dialogue line ($ms$). |
| `syl_start_time`, `syl_end_time` | `int` | Start and end timestamps of the parent syllable ($ms$). |
| `i`, `n` | `int` | Iterator ($1 \dots N$) and total unit count in the main loop. |
| `rx`, `ry` | `float` | Relative or accumulated horizontal and vertical spatial offsets (px). |
| `ratio` | `float` | Active temporal or modular progress ratio. |
| `module` / `m` | `float` | Normalised sub-loop progress ratio: $\text{module} = \frac{j - 1}{\text{maxj} - 1} \in [0.0, 1.0]$. |
| `pos_x`, `pos_y` | `float` | Position calculated for the active element (px). |
| `center`, `middle` | `float` | Horizontal and vertical centre of the active element (px). |
| `left`, `right`, `top`, `bottom` | `float` | Bounding box coordinates of the active element (px). |
| `width`, `height` | `float` | Width and height of the active element (px). |
| `x`, `y` | `float` | Coordinates of the active element (px). |
| `result` | `string` | Return variable of `System/Script Code`; text or tags assigned to it are emitted on the `Result` pin. |

#### 1.4.5. Sub-iterators (pieces, particles, sub-loops)
Set when an iterative generator is wired to the `Return` port of `System/Output`:

| Variable | Type | Generator and Description |
| :--- | :---: | :--- |
| `j`, `maxj`, `maxloop` | `int` | Ordinal counter ($1 \dots N$) and total iterations configured in `Loops/MaxLoop`. |
| `s_i`, `s_n`, `s_max` | `int` | Active piece index ($1 \dots N$) and total piece count generated by `Shape/Slicer`. |
| `slice_i`, `slice_n`, `slice_max` | `int` | Aliases of `s_i` and `s_n` for use in expressions. |
| `col`, `row` | `int` | Spatial column and row coordinates in cellular matrix segmentations (`Slicer`, `Array`). |
| `a_i`, `a_n` | `int` | Ordinal index of active particle and total elements in `Shape/Array` matrices. |
| `p_i`, `p_n` | `int` | Ordinal index and total particle count in `Functions/Particles` swarms. |
| `c_i`, `c_n`, `c_max` | `int` | Ordinal index and total slice count in `Functions/Clip Gradient`. |
| `clip_i`, `clip_n`, `clip_max` | `int` | Aliases of `c_i` and `c_n` in `Functions/Clip Gradient`. |
| `d_i`, `d_n` | `int` | Ordinal index and count of polygons in `Shape/Union & Divide` partitions. |

#### 1.4.6. Shortcuts (`val_*`)
Direct access to the metrics of the current element in expressions and `Sys Var`:

| Variable | Type | Equivalent Metric |
| :--- | :---: | :--- |
| `val_x`, `val_y` | `float` | Cartesian coordinates of the active unit (`active_unit.x`, `active_unit.y`). |
| `val_left`, `val_right` | `float` | Left and right horizontal boundaries (`active_unit.left`, `active_unit.right`). |
| `val_top`, `val_bottom` | `float` | Top and bottom vertical boundaries (`active_unit.top`, `active_unit.bottom`). |
| `val_center`, `val_middle` | `float` | Horizontal and vertical centre coordinates (`active_unit.center`, `active_unit.middle`). |
| `val_width`, `val_height` | `float` | Dimensions (`active_unit.width`, `active_unit.height`). |
| `val_start` / `val_st` | `float` | Start timestamp in milliseconds (`active_unit.start_time`). |
| `val_end` / `val_et` | `float` | End timestamp in milliseconds (`active_unit.end_time`). |
| `val_dur` | `float` | Net duration in milliseconds (`active_unit.duration`). |
| `val_mid` | `float` | Temporal midpoint of the active unit: $t_{\text{start}} + \frac{t_{\text{dur}}}{2}$. |
| `val_i`, `val_n` | `int` | Ordinal index and total unit count of the active element. |

#### 1.4.7. Inter-line timing (`sync.*`)
`sync` gives the gap in milliseconds to neighbouring dialogue lines, so you can start an animation before the line begins or transition between lines without collisions:

| Variable | Type | Search Criterion and Description |
| :--- | :---: | :--- |
| `sync.next` / `sync.prev` | `float` | Temporal gap in milliseconds to the next or previous line according to standard chronological order (capped at `max_gap`, 2000 ms by default). |
| `sync.order_next`, `sync.order_prev` | `float` | Gap to the immediately contiguous line in the physical line order of the ASS file. |
| `sync.style_next`, `sync.style_prev` | `float` | Gap to the next or previous line sharing **the same style**. |
| `sync.actor_next`, `sync.actor_prev` | `float` | Gap to the next or previous line sharing **the same actor / character**. |
| `sync.effect_next`, `sync.effect_prev` | `float` | Gap to the next or previous line sharing **the same effect field**. |
| `sync.layer_next`, `sync.layer_prev` | `float` | Gap to the next or previous line located on **the same ASS layer**. |

> [!NOTE]
> **Sign of `sync` values:**
> * A **positive value ($> 0$)** is a pause between the two lines (e.g. $+850\text{ ms}$).
> * A **negative value ($< 0$)** means the two lines overlap in time.

#### 1.4.8. Timers and modifiers (`time.*`)
Per-syllable delays and phases for sequential animations, usable in expressions or through `Sys Var`:

| Variable | Type | Description |
| :--- | :---: | :--- |
| `time.lead_in` | `int` | Cumulative lead-in delay per syllable for anticipation animations (*lead-in*). |
| `time.lead_out` | `int` | Cumulative lead-out delay per syllable for exit animations (*lead-out*). |
| `time.middle_1` | `int` | Symmetrical delay calculated outward from the centre of the line towards the edges. |
| `time.middle_2` | `int` | Symmetrical delay calculated inward from the edges of the line towards the centre. |
| `time.loop_1` | `int` | Continuous cyclic animation timing in the entrance phase. |
| `time.loop_2` | `int` | Continuous cyclic animation timing in the exit phase. |

#### 1.4.9. Vector shape presets (`shape.*`)
The `shape` namespace holds the standard Pyxis vector paths in ASSdraw format (`m ... l ... b ...`), usable in clips, morphing transformations or code expressions:

| Preset | Identifier | Emitted Geometry |
| :--- | :--- | :--- |
| **Circle** | `shape.circle` | Normalised Bézier circle centred at $(0, 0)$. |
| **Square** | `shape.square` | Equilateral square centred at $(0, 0)$. |
| **Rectangle** | `shape.rect` / `shape.rectangle` | Parametric rectangle centred at $(0, 0)$. |
| **Triangle** | `shape.triangle` | Equilateral triangle with top apex at $(0, 0)$. |
| **Rhombus** | `shape.diamond` / `shape.rhombus` | Rhombus centred at $(0, 0)$. |
| **Rounded Corners** | `shape.rounded_corners` | Rectangle with Bézier-rounded corners on all four corners. |
| **Regular Polygons** | `shape.pentagon`, `shape.hexagon`, `shape.octagon` | Regular 5-, 6- and 8-sided polygons. |
| **Star** | `shape.star` | Symmetrical 5-pointed star. |
| **Heart** | `shape.heart` | Bicubic centred vector heart path. |
| **Sakura** | `shape.sakura` | Stylised Japanese cherry blossom petal. |
| **Symbols and Weather** | `shape.cross`, `shape.cloud`, `shape.sun`, `shape.moon`, `shape.flower` | Common icons for particle effects. |

#### 1.4.10. Project Metadata (`meta.`) and Context Shapes
| Variable | Type | Description |
| :--- | :---: | :--- |
| `meta.res_x`, `meta.res_y` | `int` | Script rendering resolution (`PlayResX`, `PlayResY`, e.g. `1280`, `720` or `1920`, `1080`). |
| `shape.width`, `shape.height` | `float` | Pixel width and height of the vector path in context. |
| `shape.left`, `shape.right` | `float` | Minimum and maximum horizontal extents of the vector path. |
| `shape.top`, `shape.bottom` | `float` | Minimum and maximum vertical extents of the vector path. |
| `shape.center_x`, `shape.center_y` | `float` | Centre of the path's bounding box: $(\frac{\text{left} + \text{right}}{2}, \frac{\text{top} + \text{bottom}}{2})$. |

#### 1.4.11. Visual Ink Metrics (`ink.`, `l.ink.`, `syl.ink.`, `char.ink.`, `word.ink.`)
Standard typographical metrics use the typographical bounding box, which includes side-bearings and the font's ascender/descender margins. **Ink Metrics** measure the actual vector outlines of the rendered glyphs (*visual ink bounds*):

| Variable | Type | Description |
| :--- | :---: | :--- |
| `ink.width`, `ink.height` | `float` | Pixel width and height of the rendered glyph outline of the active unit (px). |
| `ink.left`, `ink.right` | `float` | Left and right edges of the rendered ink on screen (px). |
| `ink.top`, `ink.bottom` | `float` | Top and bottom edges of the rendered ink on screen (px). |
| `ink.center`, `ink.middle` / `ink.x`, `ink.y` | `float` | Horizontal and vertical centre of the rendered ink (px). |
| `ink.l.*` / `l.ink.*` | `float` | Ink metrics for the active line. |
| `ink.syl.*` / `syl.ink.*` | `float` | Ink metrics for the active syllable. |
| `ink.char.*` / `char.ink.*` | `float` | Ink metrics for the active character. |
| `ink.word.*` / `word.ink.*` | `float` | Ink metrics for the active word. |

### 1.5. Lookup order

`Sys Var` and the expression engine resolve an identifier $V$ by checking these cases in order:

```
                  ┌───────────────────────────────┐
                  │      Starts with 'sync.'?     │ ──► [Yes] ──► Inter-line temporal synchronisation query
                  └──────────────┬────────────────┘
                                 │ [No]
                  ┌──────────────▼────────────────┐
                  │      Starts with 'ink.'?      │ ──► [Yes] ──► Real visual ink vector contour inspection
                  └──────────────┬────────────────┘
                                 │ [No]
                  ┌──────────────▼────────────────┐
                  │ Is 'is_first' / 'is_last' /   │ ──► [Yes] ──► Topological relative position flags
                  │    'has_prev' / 'has_next'?   │
                  └──────────────┬────────────────┘
                                 │ [No]
                  ┌──────────────▼────────────────┐
                  │   Prefix 'prev.' or 'next.'?  │ ──► [Yes] ──► Adjacent unit metrics and typography
                  └──────────────┬────────────────┘
                                 │ [No]
                  ┌──────────────▼────────────────┐
                  │      Starts with 'shape.'?    │ ──► [Yes] ──► Normalised vector shape presets
                  └──────────────┬────────────────┘
                                 │ [No]
                  ┌──────────────▼────────────────┐
                  │   Is 'frame_dur' or 'ratio'?  │ ──► [Yes] ──► Active global temporal or modular progress
                  └──────────────┬────────────────┘
                                 │ [No]
                  ┌──────────────▼────────────────┐
                  │      Starts with 'val_'?      │ ──► [Yes] ──► Fast direct active unit scalar mapping
                  └──────────────┬────────────────┘
                                 │ [No]
                  ┌──────────────▼────────────────┐
                  │   Prefix 'fx.' or 'time.'?    │ ──► [Yes] ──► Kinematic offsets and integrated timers
                  └──────────────┬────────────────┘
                                 │ [No]
                  ┌──────────────▼────────────────┐
                  │   Prefix 'line.' / 'syl.' /   │ ──► [Yes] ──► Hierarchical element introspection
                  │        'char.' / 'word.'?     │               and baseline style properties
                  └──────────────┬────────────────┘
                                 │ [No]
                  ┌──────────────▼────────────────┐
                  │  Exists in context or meta?   │ ──► [Yes] ──► User-defined identifier or resolution metadata
                  └──────────────┬────────────────┘
                                 │ [No]
                                 ▼
                         Returns empty string ("")
```

### 1.6. Example

Read the syllable's coordinates and duration to position it and pulse its scale while it is sung:

```
[Sys Var (var_name: syl.x)]   ──► [In1] ──┐
[Sys Var (var_name: syl.y)]   ──► [In2] ──┼──► [Dynamic Format] ──► Output.Tags
[Sys Var (var_name: syl.dur)] ──► [In3] ──┘
```

* **Template in `Dynamic Format`:**
  ```text
  {\an5\pos(%s, %s)\t(0, %s, \fscx125\fscy125\1c&H00FFFF&)}
  ```
* **Resulting ASS line:**
  ```ass
  Dialogue: 0,0:01:12.40,0:01:15.80,Romaji,,0,0,0,,{\an5\pos(412.5, 680.0)\t(0, 320, \fscx125\fscy125\1c&H00FFFF&)}Ka
  ```

---

## 2. Node `Variables/Define Vars` (Local Variable Definition)

Defines custom local variables, evaluated on every graph iteration. Use it for reusable intermediate calculations, so complex expressions don't need extra wires on the canvas.

![Variables/Define Vars](img/define_vars.jpg)

### 2.1. Editing
`Define Vars` works both as a **pass-through dataflow node** and as a **loop chain node**. Clicking the text area opens a multi-line code editor with syntax highlighting; write one assignment per line.

### 2.2. Inputs and properties
1. **`In` (`in_val`):** Pass-through input. Accepts any data type (ASS tag strings, vector geometry, numbers or text). If unwired, emits declared variables or an empty string.
2. **`Vars` (`variables`):** Multi-line block of declarations written as `key = expression`.
   * Type A (formula / evaluated expression). Evaluated line by line, in order, by the expression evaluator.
   * **Declaration syntax:**
     ```python
     radius = 50 + (syl.i * 10)
     angle = (j / maxj) * 360
     pos_x = syl.x + math.cos(math.radians(angle)) * radius
     pos_y = syl.y + math.sin(math.radians(angle)) * radius
     current_colour = "&H00FFFF&"
     ```

### 2.3. Outputs
1. **`[1.1] Out`:** Passes through the data received at `In` (*pass-through*), after adding all defined variables to the execution context.

#### Effect on the context
Every variable declared in `Vars` is registered in the context under its own name (`radius`, `angle`, `pos_x`, etc.) and is available to:
* Downstream `Variables/Get Var` nodes.
* `Basics/Dynamic Format` or `Basics/Math` nodes.
* Parenthesized `\tag(variable)` expressions in text strings and ASS override tag templates.

> [!NOTE]
> **Re-evaluation with Return iterators:**
> When a node connected to the `Return` port of `System/Output` (such as `Shape/Slicer`, `Shape/Array`, `Functions/Particles`, `Functions/IMG to pixels`) generates sub-iterations (`s_i`, `a_i`, `p_i`, `d_i`, etc.), Pyxis re-evaluates all active `Define Vars` declarations for each slice or particle before evaluating the tags connected to the `Tags` port. Expressions such as `by.s_i.R(-30, 30)`, or formulas that depend on `s_i`, therefore resolve to the per-piece value and not a stale outer-loop value. Variable definitions are also isolated per output queue (*Queue Isolation*), so multiple `Output` nodes don't affect each other.

### 2.4. How variables reach other nodes

```
                    +---------------------------+
                    | Loops/Main Loop (syl)     |
                    +-------------┬-------------+
                                  │
                                  ▼
                    +---------------------------+
                    | Variables/Define Vars     |
                    |   offset_x = syl.i * 12   |
                    |   rot = by.s_i.R(-20, 20) |
                    +-------------┬-------------+
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
      +---------------------------+ +---------------------------+
      | Variables/Get Var         | | Basics/Dynamic Format     |
      |   var_name: rot           | |   \frz(rot)\fscx(110)     |
      +---------------------------+ +---------------------------+
```

### 2.5. Example

Place each `Shape/Slicer` piece on a circular orbit around the syllable and rotate it per piece:

* **Declarations in `Define Vars` (`variables`):**
  ```python
  radius = 18 + (syl.i * 4)
  angle = (s_i / s_n) * 360
  pos_x = syl.x + math.cos(math.radians(angle)) * radius
  pos_y = syl.y + math.sin(math.radians(angle)) * radius
  rot = (s_i / s_n) * 180
  ```
* **Tags emitted by `Basics/Dynamic Format` to `Output.Tags`:**
  ```text
  \pos(pos_x, pos_y)\frz(rot)\t(0, syl.dur, \alpha&HFF&)
  ```
* **Resulting ASS line:**
  ```ass
  Dialogue: 0,0:01:12.40,0:01:15.80,Romaji,,0,0,0,,{\pos(425.2, 672.8)\frz(22.5)\t(0, 320, \alpha&HFF&)}Ka
  ```

---

## 3. Node `Variables/Get Var` (Context Variable Reader)

Outputs the current value of any context variable, looked up by name. It lets you pass values across a large graph without wires, and read loop iterators or dynamically injected variables.

![Variables/Get Var](img/get_var.jpg)

### 3.1. Lookup cost
Needs no input ports and resolves in $\mathcal{O}(1)$ with a direct hash-map lookup in the context.

### 3.2. Inputs and properties
1. **`Name` (`var_name`):** Variable to read (e.g. `"j"`, `"maxj"`, `"module"`, `"custom_val"`, `"offset_x"`). Default: `"j"`.
   * Type C (plain text / identifier). Not parsed with `ast.parse`.

### 3.3. Outputs
1. **`[1.1] Data`:** Value from the context. If the variable isn't defined in the active context, emits an empty string `""`.

### 3.4. Typical uses
* **Sub-iterators:** Read the secondary loop counters (`j`, `maxj`, `module`) from `Loops/MaxLoop` to feed interpolation or affine transform nodes.
* **Injected variables:** Read results computed by `Variables/Define Vars` or by scripts in `System/Script Code`.
* **Wireless routing:** Avoids long crossing wires in large graphs when one calculated value feeds several distant branches.

### 3.5. Example

Read the iterator `j` from `Loops/MaxLoop` to vary opacity and scale across duplicate layers:

* **Graph Connections:**
  ```
  [Loops/MaxLoop (iterations: 4)]
  [Variables/Get Var (var_name: "j")] ──► [In1] ──► [Dynamic Format] ──► Output.Tags
  ```
* **Template in `Dynamic Format`:**
  ```text
  {\pos(syl.x, syl.y)\fscx(%s)\fscy(%s)\alpha(%s)}
  ```
* **Resulting ASS line (iteration $j = 3$):**
  ```ass
  Dialogue: 0,0:01:12.40,0:01:15.80,Romaji,,0,0,0,,{\pos(412.5, 680.0)\fscx145\fscy145\alpha&H60&}Ka
  ```

---

## 4. Node `Variables/Memory` (Persistent Key-Value Store)

Persistent variable storage (*State Retention*) for the whole graph evaluation session. Ordinary context variables reset on each new syllable, line or frame, but `Memory` keeps its values between cycles. Use it for cumulative motion, numerical trajectory integration, min/max tracking ($\min / \max$) and conditional latches.

![Variables/Memory](img/memory.jpg)

### 4.1. Modes
1. **`remember` (`save` / `SAVE`):** Write mode. Stores the incoming data under the given key and passes it to the output, so it can be chained.
2. **`retrieve` (`load` / `LOAD`):** Read mode. Reads the value stored under the given key. If the key hasn't been set in the session, emits the fallback configured in `Value / Default`.

### 4.2. Inputs and properties
1. **`Key` (`key`):** Name under which the data is stored (e.g. `"prev_x"`, `"accum_rot"`, `"max_width"`).
   * Type C (plain text / identifier). Not parsed with `ast.parse`.
   * *Precedence:* Connected cable $\to$ Inline text field $\to$ Default `"ref"`.
2. **`Value` (`value` / `default`):**
   * In `remember` mode: Data to write to memory.
   * In `retrieve` mode: Fallback emitted if the key doesn't exist yet.
   * Type A / Type C (scalar numbers, coordinates, strings or vector shapes).
   * *Precedence:* Connected cable $\to$ Inline text field $\to$ Empty string `""`.

### 4.3. Outputs
1. **`[1.1] Data`:**
   * In `remember` mode: Emits the value just stored (write pass-through).
   * In `retrieve` mode: Emits the value read from memory, or `default` if the key wasn't found.

### 4.4. Persistence and accumulation

The engine keeps a persistent dictionary $\mathcal{M} = \{\text{key} \mapsto \text{value}\}$ for the whole render run.

#### 4.4.1. Position accumulator
To make each syllable $i$ start where the previous syllable $i-1$ ended:

$$\text{pos}_x(i) = \text{retrieve}(\text{"last\_x"}, \text{default} = X_0) + \Delta x_i$$
$$\text{remember}(\text{"last\_x"}, \text{pos}_x(i))$$

```
                               Syllable Cycle i-1                      Syllable Cycle i
                         ┌───────────────────────────┐           ┌───────────────────────────┐
                         │ Memory (remember)         │           │ Memory (retrieve)         │
                         │   key: "pos_x"            │           │   key: "pos_x"            │
                         │   val: 320.5 px           │           │   val => 320.5 px         │
                         └─────────────┬─────────────┘           └─────────────┬─────────────┘
                                       │                                       │
                                       ▼                                       ▼
                         ┌───────────────────────────────────────────────────────────┐
                         │             Persistent Memory Store (_memory)              │
                         │                   {"pos_x": 320.5}                        │
                         └───────────────────────────────────────────────────────────┘
```

#### 4.4.2. Velocity and gravity integrator
For particle simulations and discrete physics with `MaxLoop` sub-loops:

$$v_y(j) = \text{retrieve}(\text{"vel\_y"}, 0.0) + g \cdot \Delta t$$
$$y(j) = \text{retrieve}(\text{"pos\_y"}, Y_0) + v_y(j) \cdot \Delta t$$
$$\text{remember}(\text{"vel\_y"}, v_y(j)) \quad \land \quad \text{remember}(\text{"pos\_y"}, y(j))$$

Here $g$ is gravitational acceleration and $\Delta t$ is the integration time step in milliseconds.

### 4.5. Usage patterns

1. **Reset per line with `Basics/Once`:**
   For accumulators that run across a line, chain a `Basics/Once` node (`mode: line`) to reset the memory at the start of each line, so state from earlier lines doesn't leak into later ones:
   ```
   [Basics/Once (line)] ──► [Variables/Memory (remember: "accum_x" = 0.0)]
   ```

2. **Tracking extremes:**
   To find the maximum glyph width across a phrase as it is processed:
   ```
   [Math (max: syl.width, Memory.retrieve("max_w", 0))] ──► [Memory (remember: "max_w")]
   ```

3. **Sharing values between subgraphs:**
   An upstream typographic subgraph can store scale or colour parameters in memory for a downstream particle or glow subgraph to read, with no wires across the canvas.

### 4.6. Example

Horizontal accumulator that places each syllable after the previous one, for flowing spacing across a line:

* **Graph Connections:**
  ```
  [Basics/Once (line)] ──► [Memory (mode: remember, key: "last_x", value: line.left)]
  [Memory (mode: retrieve, key: "last_x", default: line.left)] ──► [Math (+ syl.width + 10)] ──► [Memory (mode: remember, key: "last_x")]
  ```
* **Resulting ASS line:**
  ```ass
  Dialogue: 0,0:01:12.40,0:01:15.80,Romaji,,0,0,0,,{\an7\pos(384.0, 680.0)}Ka
  Dialogue: 0,0:01:12.40,0:01:15.80,Romaji,,0,0,0,,{\an7\pos(424.0, 680.0)}ra
  Dialogue: 0,0:01:12.40,0:01:15.80,Romaji,,0,0,0,,{\an7\pos(462.5, 680.0)}o
  ```

---

## 5. Comparison of the Variable Nodes

| Node | Operating Mode | Lifecycle Scope | Complexity | Behaviour on Missing Key | Property type | Main use |
| :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| **`Sys Var`** | Environment query | Read-only (Native ASS context) | $\mathcal{O}(1)$ | Emits empty string `""` | Type C (`var_name`) | Reading syllable, line, resolution and time metrics. |
| **`Define Vars`** | Local injection | Active iteration cycle | $\mathcal{O}(K)$ | Assigns literal `val_expr` on failure | Type A (`variables`) | Intermediate variables and mathematical expressions. |
| **`Get Var`** | Dynamic query | Active context | $\mathcal{O}(1)$ | Emits empty string `""` | Type C (`var_name`) | Reading variables and loop iterators (`j`) without wires. |
| **`Memory`** | Write / Read | Persistent (Full session) | $\mathcal{O}(1)$ | Emits configured `default` value | Type C (`key`), Type A/C (`value`) | Accumulators, iterative motion and persistent state. |

---

## 6. Property Types (A, B and C) and AST Resolution

Every string property in Pyxis is one of three types, which determine how the engine, the string evaluator and the static linter treat it:

### 6.1. Type A: mathematical formulas and AST expressions

* **Runtime:** Evaluated numerically, line by line, by the Python expression engine. Supported syntax:
  * Arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.
  * Ternary conditionals: `value_a if condition else value_b`.
  * Maths functions: `math.sin()`, `math.cos()`, `math.radians()`, `math.sqrt()`, `abs()`, `min()`, `max()`, `round()`.
  * Deterministic random functions tied to iterators: `by.<iter>.R(min, max)`, `by.syl.R(min, max)`, `R()`, `Rm()`.
* **Linter:** Parsed statically with `ast.parse(mode="eval")`. The validator checks that identifiers are known global variables or were declared upstream in the graph, and warns about undeclared variables and syntax errors.
* **Examples:**
  * `Variables/Define Vars`: `variables` property (`Vars`).
  * `Basics/Math`: numerical inputs and fields `A`, `B`.
  * `Functions/Conditioner`: `condition` field.
  * `Basics/Only`: `condition` field.
  * `Shape/Filter`: `expr_x`, `expr_y` fields.

### 6.2. Type B: ASS tag templates and macros

* **Runtime:** Processed in order by the string evaluator (`string_evaluator.py`):
  * Variable substitution inside tag parentheses: `\pos(syl.x, syl.y)`, `\frz(rot)`, `\fscxy(scale)`.
  * Animation timing shortcuts: time modifiers (`2li`, `3lo`, `1m1`) and frame numbers (`10f`).
  * Dark Tag expansion (`~`, `\tagR(...)`).
  * Arithmetic subexpressions in parentheses, `\tag(subexpr)`, are passed to the Type A evaluator.
* **Linter:** Checked with ASS tag syntax validation (`_validate_tags`): balanced delimiters (`{`, `}`, `(`, `)`) and the expected argument count for each ASS tag. Numerical subexpressions are validated with the Type A rules.
* **Examples:**
  * `Basics/Dynamic Format`: `format` field.
  * `System/Output`: `Tags` and `Return` inputs.
  * `Basics/MultiTag`: tag prefix and suffix fields.

### 6.3. Type C: plain text, identifiers and pass-through

* **Runtime:** Treated as literal strings, with no expression parsing or evaluation.
* **Linter:** Only checks that `()` and `{}` are balanced, to avoid breaking the subtitle formatting in Aegisub. **Never passed to `ast.parse`**, to avoid false positives on arbitrary text or operator-like strings.
* **Examples:**
  * `Variables/Get Var`: `var_name` field.
  * `Variables/Memory`: `key` field.
  * `Basics/String`: `value` field.
  * `Basics/Text`: `text` field.
  * `Functions/Conditioner`: literal text fields `if_true`, `if_false` (when containing no ASS tags prefixed with `\`).

---

## 7. Scopes and Name Collisions

### 7.1. Scopes in nested loops

While processing subtitles, Pyxis descends through a hierarchy of contexts. A scope inherits the variables of the scopes above it, but local variables injected in a sub-loop don't leak upwards:

$$\text{Line (Global)} \longrightarrow \text{Primary Unit (Syllable / Char / Word)} \longrightarrow \text{Sub-Loop (MaxLoop)} \longrightarrow \text{Iterative Return (Piece / Particle)}$$

1. **Line Level:** `line.*`, `l.*`, `line_start_time`, `line_end_time`, `line_dur`, `meta.res_x`, `meta.res_y`.
2. **Primary Unit Level:** `syl.*`, `char.*`, `word.*`, `x`, `y`, `center`, `middle`, `left`, `right`, `top`, `bottom`, `width`, `height`, `i`, `n`, `dur`, `st`, `et`.
3. **Sub-Loop Level:** `j`, `maxj`, `module`, `maxloop`.
4. **Iterative Return Level:** `s_i`, `s_n` (Slicer), `a_i`, `a_n` (Array), `p_i`, `p_n` (Particles), `c_i`, `c_n` (Clip Gradient), `d_i`, `d_n` (Union & Divide).

### 7.2. Output queue isolation (*Queue Isolation*)

When the graph has several `System/Output` nodes, each render queue processes its subgraph in isolation. Variables declared with `Variables/Define Vars` in the Layer 1 branch don't leak into or interfere with those of the Layer 2 branch.

### 7.3. Avoiding name collisions

1. **Don't overwrite reserved identifiers:** Avoid assigning `x`, `y`, `i`, `n`, `dur`, `st` or `et` in `Define Vars`, unless you intentionally want to change the glyph's motion through the engine's property propagation (`_apply_fx_setting`).
2. **Use descriptive prefixes:** In complex effect chains, prefix your variables (e.g. `orb_rad`, `p_vel_x`, `wave_phase`) to avoid collisions with globals and keep the graph readable.
3. **Keep loop counters intact in nested structures:** When combining a `Loops/MaxLoop` sub-loop (`j`) with an iterative return generator such as `Shape/Slicer` (`s_i`), don't reassign `j` in `Define Vars`. Read `j` with `Variables/Get Var` or reference it directly in expressions.

---

## 8. Best Practices

### 8.1. Resetting `Memory` per line

`Variables/Memory` keeps its data for the whole render session, so an accumulator that sums displacements between syllables keeps growing unless it is reset. To limit it to one dialogue line, reset it with `Basics/Once`:

```
[Basics/Once (mode: line)] ──► [Variables/Memory (mode: remember, key: "acc_x", value: 0.0)]
```

When a new dialogue line begins, the `"acc_x"` key is set back to `0.0`, so no state carries over between lines.

### 8.2. Direct wire or `Get Var`

* **Direct wire:** Use it for local, immediate dependencies within the same visual subgraph. The data flow stays visible on the canvas.
* **`Get Var` node:** Use it when:
  * A value computed on one side of a large canvas must feed distant branches, which avoids long crossing wires (*wire clutter*).
  * You need to read injected iterators (`j`, `s_i`, `a_i`) that have no output pin on the loop node.
  * You are feeding nodes that only offer inline text fields.

### 8.3. Placing `Define Vars`

Place `Variables/Define Vars` **upstream** of the nodes that use its variables, so they are available on every iteration. The usual spot is on the pass-through path from `Loops/Main Loop` to `System/Output`.

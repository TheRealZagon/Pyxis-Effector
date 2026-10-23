# Visual Paradigm

Pyxis Effector is a node-graph environment for processing and generating subtitles in the ASS (*Advanced SubStation Alpha*) format. Iteration, numerical computation, geometric transformations and tag compilation are each handled by separate, interconnected nodes.

---

## 1. Graph Principles

The engine runs a directed acyclic graph (DAG) with two kinds of links:

```
[Main Loop] ---> [MaxLoop / Sub-iterator] ---> [Script / Transform] ---> [Output]
     │                                                ▲
     │ (Active Context)                               │ (Data evaluated on demand)
     └───────────────────> [Data Nodes / Tags] ───────┘
```

### 1.1. Flow Links (*Flow / Loop Links*)
Flow links set the order and nesting in which effect branches are evaluated, and how many times each branch runs (per dialogue line, syllable, character, sub-particle or video frame). They connect through the `Loop`, `Loop In` and `Loop Out` ports. The core flow nodes are:

* `Main Loop`: iterates over the base unit (line, word, syllable or character).
* `MaxLoop`: event multiplier or sub-frame *FBF* loop.
* `Script Code`: injects Python / Lua code.
* `Output`: assembles the result and emits the ASS dialogue lines.

### 1.2. Data Links (*Data Links*)
1. **Types:** numerical values (`float`/`int`), text strings, Cartesian coordinate pairs $(x, y)$, hexadecimal and ASS colours (`&HBBGGRR&`), ASSdraw vector paths (`m ... l ... b ...`) and formatted ASS tag blocks (`{\pos...\t...\clip}`).
2. **Lazy evaluation:** a data node is computed only when the active flow requests its value in the current iteration. A data branch that is not connected to an active flow node uses no CPU time or memory.
3. **Fan-out:** an output can feed several inputs at no extra cost, because results are memoised within each cycle.

---

## 2. Context Hierarchy and Data Lifecycle

An effect is processed in five phases:

```
[1. Selection in Aegisub]
           │
           ▼
[2. Base Domain: Main Loop] (line / syl / word / char)
           │
           ▼
[3. Sub-domain: MaxLoop] (Clones, Particles, FBF Frames)
           │
           ▼
[4. Data Transformation] (Vectors, Tags, Audio, Interpolations)
           │
           ▼
[5. Terminal Assembly: Output] ───> [New Layered ASS Dialogue Lines]
```

### Phase 1: Selection and Input Parsing
The engine reads the dialogue lines of the ASS file loaded in Aegisub, according to the scope set in `Output` (`apply_to`):
* `Sel. Lines`: only the lines selected in the Aegisub grid.
* `Style Lines`: all lines with the same style as the selection.
* `All Lines`: every dialogue line in the file.

Each line is parsed into its typographic metrics and karaoke timing markers (`\k`, `\kf`, `\ko`).

### Phase 2: Base Iteration (`Main Loop`)
`Main Loop` sets the base iteration unit (`iterator`):
* **`syl`:** one iteration per syllable, using the karaoke markers. Exposes the syllable's metrics and timing (`syl.start_time`, `syl.duration`, `syl.text`, etc.).
* **`char`:** one iteration per character, so each glyph can be animated independently.
* **`word`:** one iteration per whitespace-delimited word.
* **`line`:** one iteration per dialogue line.

The `blank_mode` property (`no_blank` / `with_blanks`) controls whether whitespace is skipped or processed as an element that has advance width but no visible glyph.

### Phase 3: Sub-loops (`MaxLoop`) and Generator Nesting
For motion trails, particle swarms, delayed echo copies or frame-by-frame *FBF* animations, the flow goes through one or more `MaxLoop` nodes. Each one multiplies the current unit by $N$ sub-iterations, exposes a local counter (by default `j`, from $1 \dots N$) and subdivides the time interval.

Within each leaf iteration of `Main Loop` / `MaxLoop`, the engine also walks the **sub-loop generator nodes** connected to `Output` (`Shape/Slicer`, `Shape/Union & Divide`, `Shape/Concentric Borders`, `Shape/Array`, `Shape/Multi`, `Functions/Particles`, `Functions/IMG to pixels`, `Functions/Clip Gradient`, `Functions/Animation`) in **topological post-order (root $\to$ leaf)**:
1. **Geometry channel (`Output.Return`):** generators wired in series (e.g. `Slicer` $\to$ `Particles`) nest their sub-loops ($s_i = 1 \dots S$ outer $\to$ $p_i = 1 \dots P_k$ inner). Anchor coordinates (`pos_x`, `pos_y`, `org_x`, `org_y`) pass from each parent piece to its child pieces or particles.
2. **Tags and clipping channel (`Output.Tags`):** runs as an inner sub-loop for each piece or particle emitted by `Output.Return`, in the port order `In1, In2, ...` of `Concatenate`. This lets you combine, for example, `Slicer` ($s_i$) on `Return` with `Clip Gradient` ($c_i$) and `Animation` ($an_i$) on `Tags` without counter collisions.

### Phase 4: Evaluation and Deformation
The connected data nodes compute `\pos` coordinates, vector deformations (slicing with `Slicer`, inflating/scaling with `Transform`, stroking/extruding with `Stroke`), colour gradients with `Color Gradient`, audio modulation with `Modulator`, and accelerated time transformations with `Retime` and `Ipol`.

### Phase 5: Assembly and Emission (`Output`)
`Output` gathers the processed streams, merges the tag blocks from the `Tags` port with the drawings/text from the `Return` port, resolves tag collisions, applies the rendering layers (`Layer`) and writes the resulting lines into the Aegisub document.

#### Multiple Outputs and Context Isolation
To produce several concurrent layers (for example a shadow, the glyph body and particles), place several `System/Output` nodes on the same canvas:
* **Independent branches:** each `Output` evaluates its own upstream tree.
* **Context isolation (`context`):** each branch and iteration gets a clean, private context. Local variables, temporary calculations and inline mutations in one `Output` branch never leak into another, even if the branches share the canvas or end up in the same subtitle track.

#### Output Queues (`Queue ID` and `Queue Order`)
Queues only sort and group lines after they have been generated. They do not affect how nodes are evaluated.
1. **`Queue ID` $\to$ ASS `Actor` field:**
   * The text in `Queue ID` is written into the `Actor` field of the resulting ASS event:
     $$\texttt{Dialogue: Layer}, \, t_{\text{start}}, \, t_{\text{end}}, \, \text{Style}, \, \mathbf{Queue\_ID}, \, \text{MarginL}, \, \text{MarginR}, \, \text{MarginV}, \, \text{Effect}, \, \text{Text}$$
   * This lets you sort and filter the generated layers in Aegisub's subtitle grid.
2. **`Queue Order`:**
   * Sets the order in which the line blocks are written into the final ASS document.
   * The engine groups lines by queue and emits **all queues with a lower `Queue Order`, across all dialogue lines, first**, then the queues with higher orders:
     $$\text{SortKey}(Q) = \left(\min_{l \in Q} (\text{queue\_order}_l), \, \text{qid}\right)$$
   * **Ties and fallbacks:**
     * *Equal or missing order:* queues without an explicit `Queue Order`, or with the same integer value, are sorted **alphabetically by `Queue ID`**.
     * *Both fields empty:* the lines go to the `"default"` queue, in the node's creation order (its `ID` on the canvas).
     * *Within a queue:* lines are ordered by dialogue line index (`line_idx`) and then by internal event order:
        $$\text{SortKey}(l) = (\text{queue\_order}_l, \, \text{line\_idx}_l)$$

---

## 3. State Persistence and Context Variables

Three nodes register, pass and accumulate state across evaluation phases:

1. **`Define Vars` (`Variables`):** adds custom variables to the execution context (e.g. `my_scale = 120`, `custom_color = "#FF00AA"`). Any downstream expression in the current iteration can use them immediately.
2. **`Get Var` (`Variables`):** reads and outputs any context variable (`i`, `j`, `N`, `syl.duration`, `line.start_time`, `fx.pos_x`, etc.).
3. **`Memory` (`Variables`):** persistent key-value store with two modes:
   * `remember`: stores the current value under a key.
   * `retrieve`: returns the last value saved under that key in previous iterations. Useful for position accumulators, continuous trajectories or reading earlier state.

---

## 4. ASS Context Variables Reference

Timing variables are relative to different origins depending on the unit:
* **`line` / `l`:** global, absolute video timestamps ($ms$).
* **`syl` / `word`:** relative to the start of the base dialogue line ($[0, \text{line.dur}]$).
* **`char`:** relative to the start of its parent syllable ($[0, \text{syl.dur}]$).
* **`fx`:** lifespan of the generated ASS line ($[0, \text{fx.dur}]$). To evaluate `\t(...)` blocks in effect time, use the offset $\text{ini} = \text{line.start\_time} - \text{fx.start\_time}$.

The following variables are available in any expression field, condition or script, grouped by domain.

### 4.1. Original Line (`line.` or `l.`)
The active dialogue line read from Aegisub: absolute timestamps, text, ASS header metadata, screen coordinates and margins.

| Variable | Type | Description and Unit | Usage Example |
| :--- | :---: | :--- | :--- |
| `line.start_time` / `l.start_time` | `int` | Absolute start timestamp of the line in the video ($ms$). | `line.start_time - 500` |
| `line.end_time` / `l.end_time` | `int` | Absolute end timestamp of the line in the video ($ms$). | `line.end_time + 300` |
| `line.dur` / `line.duration` / `l.dur` | `int` | Duration of the line ($ms$): $t_{\text{end}} - t_{\text{start}}$. | `line.dur / 2` |
| `line.mid_time` / `l.mid_time` | `float` | Midpoint of the line: $t_{\text{start}} + \frac{t_{\text{dur}}}{2}$. | `line.mid_time` |
| `line_start_time`, `line_end_time`, `line_dur` | `int` | Flat aliases without prefix for the line timestamps ($ms$). | `line_start_time` |
| `line.i` / `l.i` | `int` | Index of the active line in the processed batch ($1 \dots N$). | `line.i == 1` |
| `line.n` / `l.n` | `int` | Number of selected lines in the batch. | `line.i / line.n` |
| `line.text` / `l.text` | `string` | Text without style tags or karaoke markup. | `len(line.text)` |
| `line.raw_text` / `l.raw_text` | `string` | Original text, keeping `{\...}` tags and `\k` markup. | `line.raw_text` |
| `line.style` / `line.style_name` | `string` | Name of the ASS style assigned to the line in Aegisub. | `line.style == "Default"` |
| `line.actor` / `l.actor` | `string` | Actor field of the ASS line. | `line.actor` |
| `line.effect` / `l.effect` | `string` | Effect field of the ASS line. | `line.effect` |
| `line.layer` / `l.layer` | `int` | ASS layer of the line ($Z$ depth). | `line.layer + 1` |
| `line.center`, `line.middle` / `l.x`, `l.y` | `float` | Horizontal ($X$) and vertical ($Y$) centre of the line's bounding box (px). | `line.center, line.middle` |
| `line.left`, `line.right` | `float` | Left and right edges of the line (px). | `line.right - line.left` |
| `line.top`, `line.bottom` | `float` | Top and bottom edges of the line (px). | `line.bottom` |
| `line.width`, `line.height` | `float` | Width and height of the whole line's text (px). | `line.width` |
| `line.descent` (or `l.descend`), `line.extlead` | `float` | Font descent and external leading (px). | `line.bottom + line.descent` |
| `line.pos_x`, `line.pos_y` | `float` | Absolute position of the line (explicit `\pos` or calculated). | `line.pos_x, line.pos_y` |
| `line.org_x`, `line.org_y` | `float` | Rotation origin of the line (`\org` or metric centre). | `line.org_x, line.org_y` |
| `line.margin_l`, `line.margin_r`, `line.margin_v` | `int` | Left, right and vertical margins set on the line or style (px). | `line.margin_l` |
| `line.margin_t`, `line.margin_b` | `int` | Top and bottom margins (px). | `line.margin_t` |

### 4.2. Original Style (`line.<style_prop>`)
Font, colour, outline and alignment properties taken from the `[V4+ Styles]` header of the ASS file, or overridden on the line.

| Variable | Type | Description and Format | Usage Example |
| :--- | :---: | :--- | :--- |
| `line.fontname` | `string` | Font family of the original style (e.g. `"Arial"`, `"Montserrat"`). | `line.fontname` |
| `line.fontsize` | `float` | Font size of the base style ($pt$). | `line.fontsize * 1.5` |
| `line.bold` | `bool` | Bold flag of the style (`True` / `False`). | `line.bold` |
| `line.italic` | `bool` | Italic flag of the style (`True` / `False`). | `line.italic` |
| `line.underline` | `bool` | Underline flag of the style (`True` / `False`). | `line.underline` |
| `line.strikeout` | `bool` | Strikeout flag of the style (`True` / `False`). | `line.strikeout` |
| `line.align` | `int` | Numpad alignment of the style ($1 \dots 9$). | `line.align` |
| `line.scale_x`, `line.scale_y` | `float` | Horizontal and vertical scale of the base style ($100.0 = 100\%$). | `line.scale_x` |
| `line.spacing` | `float` | Letter spacing in pixels (`\fsp`). | `line.spacing` |
| `line.outline` / `line.bord` | `float` | Outline width of the style in pixels (`\bord`). | `line.outline` |
| `line.shadow` / `line.shad` | `float` | Shadow distance of the style in pixels (`\shad`). | `line.shadow` |
| `line.color1` | `string` | Primary colour of the style (`\1c`) in ASS format `&HBBGGRR&`. | `line.color1` |
| `line.color2` | `string` | Secondary / karaoke colour of the style (`\2c`) in ASS format `&HBBGGRR&`. | `line.color2` |
| `line.color3` | `string` | Outline colour of the style (`\3c`) in ASS format `&HBBGGRR&`. | `line.color3` |
| `line.color4` | `string` | Shadow colour of the style (`\4c`) in ASS format `&HBBGGRR&`. | `line.color4` |
| `line.alpha1` .. `line.alpha4` | `string` | Alpha channels (1: primary, 2: karaoke, 3: outline, 4: shadow) in ASS `&HAA&`. | `line.alpha1` |
| `line.angle` / `line.frz` | `float` | $Z$-rotation angle defined in the style, in degrees. | `line.frz` |
| `line.frx`, `line.fry` | `float` | 3D rotation angles of the line, in degrees. | `line.frx` |
| `line.fax`, `line.fay` | `float` | Shear factors along $X$ and $Y$. | `line.fax` |

### 4.3. Syllables (`syl`), Characters (`char`) and Words (`word`)
Units produced when `Main Loop` iterates in `syl`, `char` or `word` mode. Each unit inherits the font properties of the base style (`syl.fontname`, `syl.color1`..`4`, `syl.fontsize`, `char.fontname`, etc.).

| Unit | Variable | Description and Unit | Usage Example |
| :--- | :--- | :--- | :--- |
| **Syllable (`syl`)** | `syl.start_time`, `syl.end_time` | Start and end timestamps relative to the start of the line ($ms$). | `syl.start_time` |
| | `syl.dur` / `syl.duration` | Karaoke duration of the syllable ($ms$). | `syl.dur` |
| | `syl.mid_time` | Midpoint of the syllable, relative to the line: $t_{\text{start}} + \frac{t_{\text{dur}}}{2}$. | `syl.mid_time` |
| | `syl.syl_start`, `syl.syl_end`, `syl.syl_mid` | Time window of the syllable relative to the generated `fx` line ($\text{ini} + \text{syl.start\_time}$). | `\t(syl.syl_start, syl.syl_end, \tags)` |
| | `syl.i` / `syl.n` | Index of the syllable in the line ($1 \dots N$) and total syllables. | `syl.i / syl.n` |
| | `syl.text`, `syl.text_stripped` | Syllable text without tags or karaoke marks. | `syl.text` |
| | `syl.center`, `syl.middle` / `syl.x`, `syl.y` | Horizontal ($X$) and vertical ($Y$) centre of the syllable's bounding box (px). | `syl.center, syl.middle` |
| | `syl.left`, `syl.right`, `syl.top`, `syl.bottom` | Left, right, top and bottom edges of the syllable (px). | `syl.right - syl.left` |
| | `syl.width`, `syl.height` | Width and height of the syllable (px). | `syl.width` |
| | `syl.descent`, `syl.extlead` | Font descent and line spacing for the syllable (px). | `syl.descent` |
| | `syl.prespace`, `syl.postspace` | Whitespace before and after the syllable. | `syl.prespace` |
| | `syl.pos_x`, `syl.pos_y`, `syl.org_x`, `syl.org_y` | Position anchor and rotation origin of the syllable. | `syl.pos_x, syl.pos_y` |
| **Character (`char`)** | `char.start_time`, `char.end_time` | Start and end timestamps relative to the start of its **parent syllable** ($ms$). | `char.start_time` |
| | `char.dur` / `char.duration` | Calculated duration of the character ($ms$). | `char.dur` |
| | `char.mid_time` | Midpoint of the character within its syllable. | `char.mid_time` |
| | `char.char_start`, `char.char_end`, `char.char_mid` | Time window of the character relative to the generated `fx` line ($ms$). | `\t(char.char_start, char.char_end, \tags)` |
| | `char.syl_start`, `char.syl_end`, `char.syl_mid` | Time window of the parent syllable relative to the generated `fx` line ($ms$). | `\t(char.syl_start, char.syl_end, \tags)` |
| | `char.i` / `char.n` | Index of the character in the line ($1 \dots N$) and total characters. | `char.i` |
| | `char.syl_i`, `char.word_i` | Position of the character within its syllable and within its word. | `char.syl_i` |
| | `char.text` | The character itself. | `char.text` |
| | `char.center`, `char.middle` / `char.x`, `char.y` | Screen centre of the character (px). | `char.center, char.middle` |
| | `char.left`, `char.right`, `char.top`, `char.bottom` | Edges of the character's bounding box (px). | `char.left` |
| | `char.width`, `char.height` | Width and height of the character (px). | `char.width` |
| | `char.descent`, `char.extlead` | Font descent and spacing of the character (px). | `char.descent` |
| **Word (`word`)** | `word.start_time`, `word.end_time`, `word.dur`, `word.mid_time` | Start, end, duration and midpoint relative to the line ($ms$). | `word.start_time` |
| | `word.word_start`, `word.word_end`, `word.word_mid` | Start, end and midpoint relative to the generated `fx` line ($ms$). | `word.word_start` |
| | `word.i` / `word.n` | Index of the word in the line ($1 \dots N$) and total words. | `word.i` |
| | `word.text` | Word text without tags. | `word.text` |
| | `word.center`, `word.middle` / `word.x`, `word.y` | Horizontal ($X$) and vertical ($Y$) centre of the word on screen (px). | `word.center, word.middle` |
| | `word.left`, `word.right`, `word.top`, `word.bottom` | Edges of the word's bounding box (px). | `word.right` |
| | `word.width`, `word.height` | Width and height of the word (px). | `word.width` |
| | `word.descent`, `word.extlead` | Font descent and spacing of the word (px). | `word.descent` |

### 4.4. Ink Metrics (`ink`) and Neighbouring Units (`prev` / `next`)

| Category | Variable | Description | Usage Example |
| :--- | :--- | :--- | :--- |
| **Ink (`ink`)** | `ink.width`, `ink.height` | Width and height of the rendered glyph/contour, without the font box padding. | `ink.width` |
| | `ink.center`, `ink.middle` / `ink.x`, `ink.y` | Horizontal ($X$) and vertical ($Y$) centre based on the rendered ink contours. | `ink.center, ink.middle` |
| | `ink.left`, `ink.right`, `ink.top`, `ink.bottom` | Exact bounding box of the rendered ink pixels in screen coordinates. | `ink.left` |
| | `ink.l.*`, `ink.syl.*`, `ink.char.*`, `ink.word.*` | Ink metrics of the line, syllable, character or word, selected explicitly by scope. | `ink.syl.center` |
| **Neighbours (`prev` / `next`)** | `prev.*` / `next.*` | Access to the previous or next unit (`text`, `dur`, `start_time`, `x`, `y`, `width`, etc.). | `prev.width` |
| | `is_first`, `is_last` | Whether the unit is the first or last in the sequence. | `is_first` |
| | `has_prev`, `has_next` | `True` if a previous or next unit exists in the chain. | `has_prev` |

### 4.5. Sub-loops (`MaxLoop`), Generated Effect (`fx`) and Global Environment

| Category | Variable | Description and Formula | Usage Example |
| :--- | :--- | :--- | :--- |
| **Sub-loop (`MaxLoop`)**| `j` | Index of the active sub-iteration ($1 \dots N$). | `j` |
| | `maxj` / `maxloop` | Number of repetitions configured in the sub-loop. | `maxj` |
| | `module` / `m` / `ratio` | Normalised sub-loop progress: $\frac{j - 1}{\text{maxj} - 1} \in [0.0, 1.0]$. | `module` |
| **Effect (`fx`)** | `fx.pos_x`, `fx.pos_y` | Resolved anchor position of the active element on screen. | `fx.pos_x, fx.pos_y` |
| | `fx.start_time`, `fx.end_time` | Absolute start and end timestamps of the generated ASS line ($ms$). | `fx.start_time` |
| | `fx.dur` | Duration of the generated ASS line ($ms$). | `fx.dur` |
| **Global Environment** | `fps` | Frame rate of the active video in Aegisub (e.g. `23.976`, `60.0`). | `fps` |
| | `frame_dur` / `fd` | Duration of one video frame in milliseconds: $\frac{1000}{\text{fps}}$ (e.g. $41.708$ ms at $23.976$ fps). | `3 * fd` |
| | `ini` | Time offset: $\text{ini} = \text{line.start\_time} - \text{fx.start\_time}$ ($ms$). | `ini + syl.start_time` |
| | `st`, `et`, `dur` | Start, end and duration of the element being processed ($ms$). | `st, et` |
| | `maxgap` | Upper limit for inter-line measurements with `sync()` ($ms$, default `2000.0`). | `maxgap` |

---

## 5. Expression Evaluation and String Resolution

Text fields, string nodes and ASS tag blocks are processed by an internal evaluator (a numerical evaluator plus a template processor) that computes mathematical expressions, Python ternary operators and embedded variables.

### 5.1. Numerical and Algebraic Evaluation in Text Fields
Any numerical field (in `MultiTag`, `Math`, `Retime`, `Slicers`, `Particles`, etc.) evaluates maths in real time:
* **Algebra and functions:** `syl.center + (i * 15)`, `line.width / 2`, `math.sin(t) * 50`.
* **Frame and ratio shortcuts:** `3f` ($3 \times \text{frame\_dur}$), `0.5r` ($50\%$ of the duration).
* **ASS hexadecimals:** `&HFF&` evaluates to `255`.

### 5.2. Python Ternary Expressions
Variable nodes (`Define Vars`) and conditional fields accept Python ternary syntax:
```python
angle = 1.4 if l.layer == 1 else -1.4
color_fx = "&H00FF00&" if syl.i % 2 == 0 else "&H0000FF&"
```

### 5.3. String and ASS Tag Block Evaluation
Tag blocks in curly braces `{\...}` in any node that produces subtitles (including `Basics/String`, `Basics/MultiTag`, `System/Output`, vector transforms and kinematic layers) are processed by the template engine before the final export.

> [!IMPORTANT]
> **ASSdraw path isolation:** the evaluator only works inside curly-braced tag blocks `{\...}`. Plain text and vector drawing commands (`m 0 0 l 100 0 ...`) outside the braces are never touched, so geometric coordinates are not mistaken for identifiers or variables.

The template language has 4 resolution mechanisms:

1. **Algebraic expressions and variables inside tag parentheses (`\tag(...)`):**
   * Rotations and scales: `\frz(rot)`, `\frz(j * 15)`, `\fscxy(120 + i*5)`.
   * Positions and pivots: `\pos(syl.center + 10, syl.middle)`, `\org(fx.pos_x, fx.pos_y - 1000)`.
   * Alphas and colours: `\alpha(255)`, `\1a(128)`, `\1c(line.color1)`, `\1c(ass_color(255, 128, 0))`.
2. **Dynamic `\t(...)` transformations:**
   * Evaluated timestamps and tags: `\t(0, 150, \frz0)\t(fx.dur-150, fx.dur, \frz(rot))`.
3. **Standalone expressions, variables and ternaries in parentheses `(...)`:**
   * Variables, attributes and calculations outside tags: `(syl.text)`, `(syl.dur)`, `(fx.dur)`, `(j * 15)`, `(line.text)`.
   * Conditional tag or value selection inside the block: `(\blur3 if i == 1 else \blur0)`, `(Colores())`.
4. **Automatic conversion of decimal alphas to ASS hexadecimal:**
   * Integers are converted to ASS hex: `\4a100` $\to$ `\4a&H64&`, `\alpha255` $\to$ `\alpha&HFF&`, `\1a0` $\to$ `\1a&H00&`.

---

### 5.4. Dark Tags (Composite and Contextual Tags)

*Dark Tags* are compact macros that expand shorthand syntax into plain ASS sequences.

#### 5.4.1. Rotations with Auto-Origin (`\fr*o`)
These add an `\org(X, Y)` tag centred on the active element in the current frame (`fx.pos_x`, `fx.pos_y` or `syl.center`, `syl.middle`):

| Dark Tag | Direct Syntax | Evaluated Syntax | Emitted ASS Expansion |
| :--- | :--- | :--- | :--- |
| `\fro`, `\frzo` | `\fro45`, `\frzo-30` | `\fro(j * 15)` | `\org(X, Y)\frz<val>` |
| `\frxo` | `\frxo30` | `\frxo(syl.i * 5)` | `\org(X, Y)\frx<val>` |
| `\fryo` | `\fryo60` | `\fryo(sin(j) * 45)` | `\org(X, Y)\fry<val>` |
| `\frxyo` | `\frxyo45` | `\frxyo(15)` | `\org(X, Y)\frx<val>\fry<val>` |
| `\frxzo` | `\frxzo30` | `\frxzo(20)` | `\org(X, Y)\frx<val>\frz<val>` |
| `\fryzo` | `\fryzo45` | `\fryzo(25)` | `\org(X, Y)\fry<val>\frz<val>` |
| `\frxyzo` | `\frxyzo30` | `\frxyzo(10)` | `\org(X, Y)\frx<val>\fry<val>\frz<val>` |

#### 5.4.2. Scale and Font Size by Style Ratio (`\fsc*r`, `\fsr`)
These multiply the value defined in the Aegisub style (`style.scale_x`, `style.scale_y`, `style.fontsize`) by the given factor:

| Dark Tag | Direct Syntax | Evaluated Syntax | Emitted ASS Expansion |
| :--- | :--- | :--- | :--- |
| `\fscxr` | `\fscxr1.5` | `\fscxr(1.0 + 0.2*j)` | `\fscx(style.scale_x * ratio)` |
| `\fscyr` | `\fscyr0.8` | `\fscyr(cos(t))` | `\fscy(style.scale_y * ratio)` |
| `\fscxyr` | `\fscxyr2.0` | `\fscxyr(1.5)` | `\fscx(style.scale_x * ratio)\fscy(style.scale_y * ratio)` |
| `\fsr` | `\fsr1.2` | `\fsr(1.0 + syl.i * 0.1)` | `\fs(style.fontsize * ratio)` |

#### 5.4.3. Contextual Time Transformations (`\te`, `\ts`, `\tc`, `\tw`)
Timing shortcuts that adapt to the total effect duration or to the position of the element:

| Dark Tag | Usage Syntax | Resulting ASS Expansion | Description |
| :--- | :--- | :--- | :--- |
| `\te` | `\te(t1, t2, \tags)`<br>`\te(t1, t2, accel, \tags)`<br>`\te(t, \tags)` | `\t(fx.dur - t2, fx.dur - t1, \tags)`<br>`\t(fx.dur - t2, fx.dur - t1, accel, \tags)`<br>`\t(fx.dur - t, fx.dur, \tags)` | Animation timed backwards from the end of the line (`fx.dur`). |
| `\ts` | `\ts(t1, t2, \tags)`<br>`\ts(t1, t2, accel, \tags)`<br>`\ts(t, \tags)` | `\t(syl.start_time + t1, syl.start_time + t2, \tags)`<br>`\t(syl.start_time + t1, syl.start_time + t2, accel, \tags)`<br>`\t(syl.start_time, syl.start_time + t, \tags)` | Animation relative to the syllable start. |
| `\tc` | `\tc(t1, t2, \tags)`<br>`\tc(t1, t2, accel, \tags)`<br>`\tc(t, \tags)` | `\t(char.start_time + t1, char.start_time + t2, \tags)`<br>`\t(char.start_time + t1, char.start_time + t2, accel, \tags)`<br>`\t(char.start_time, char.start_time + t, \tags)` | Animation relative to the character start. |
| `\tw` | `\tw(t1, t2, \tags)`<br>`\tw(t1, t2, accel, \tags)`<br>`\tw(t, \tags)` | `\t(word.start_time + t1, word.start_time + t2, \tags)`<br>`\t(word.start_time + t1, word.start_time + t2, accel, \tags)`<br>`\t(word.start_time, word.start_time + t, \tags)` | Animation relative to the word start. |

#### 5.4.4. Multichannel and Grouped Tags
| Dark Tag | Direct ASS Expansion | Example |
| :--- | :--- | :--- |
| `\fscxy` | `\fscx<val>\fscy<val>` | `\fscxy150` $\to$ `\fscx150\fscy150` |
| `\faxy` | `\fax<val>\fay<val>` | `\faxy0.2` $\to$ `\fax0.2\fay0.2` |
| `\frxyz`, `\frxy`, `\frxz`, `\fryz` | Combined 3D rotations | `\frxyz45` $\to$ `\frx45\fry45\frz45` |
| `\xybord`, `\xyshad`, `\bs` | Border and shadow together | `\bs3` $\to$ `\bord3\shad3` |
| `\[1-4]+c` (e.g. `\134c`, `\13c`, `\234c`) | Several colours at once | `\134c&H00FFFF&` $\to$ `\1c&H00FFFF&\3c&H00FFFF&\4c&H00FFFF&` |
| `\[1-4]+a` (e.g. `\134a`, `\14a`, `\34a`) | Several alphas at once | `\134a&H80&` $\to$ `\1a&H80&\3a&H80&\4a&H80&` |

#### 5.4.5. Style Restoration (`\tag~`) and Random Values (`\tagR(...)`)
* **Restoration (`~`):** restores the value from the original style: `\c~` (primary colour), `\fscxy~` (base $X/Y$ scale), `\fs~` (font size), `\bs~` (base border and shadow), `\134c~`, `\134a~`, `\frxyz~`, `\blur~`.
* **Random (`R`):** generates continuous or discrete random variations: `\frzR(-30, 30)`, `\134cR()`, `\alphaR(0, 128)`, `\froR(-20, 20)`, `\fscxyrR(1.0, 1.5)`.

---

## 6. Inter-Line Synchronisation (`sync`)

`sync` measures the gap (in milliseconds) between the active dialogue line and the previous or next line, either in the original subtitle order or among lines that match a criterion.

### 6.1. The `sync()` Function
It can be used in timing expressions, node properties and script nodes:

```python
sync(direction="next", mode="order", max_gap=2000)
```

* **`direction` (1st parameter):** `next` or `prev`. Default: `next`.
* **`mode` (2nd parameter):** how the neighbouring line is matched:
  * `1` or `"order"` *(default)*: next/previous dialogue line in subtitle order (comment lines are ignored).
  * `2` or `"style"`: lines with the same ASS style (`line.style`).
  * `3` or `"actor"`: lines with the same actor (`line.actor`).
  * `4` or `"effect"`: lines with the same ASS Effect field (`line.effect`).
  * `5` or `"layer"`: lines with the same ASS layer (`line.layer`).
* **`max_gap` (3rd parameter):** upper limit in milliseconds (default: `2000.0` ms or the value defined in `maxgap`).

#### Examples:
```python
# Extends the effect end by half the gap to the next line (capped at 2000ms):
end_time = l.end_time + (sync(next, order) / 2)

# Advances effect start by half the gap to the previous line with matching style (capped at 1500ms):
start_time = l.start_time - (sync(prev, style, 1500) / 2)

# Numeric mode index invocation:
start_time = l.start_time - (sync(prev, 2) / 2)
```

### 6.2. The `sync.*` Namespace
In tag blocks (`\fad`, `\t`), the `sync` namespace exposes the same values as properties:

| Property | Direction | Mode Filter | Return Value |
| :--- | :---: | :---: | :--- |
| `sync.next` / `sync.order_next` | `next` | `order` | Gap to the next dialogue line in ms. |
| `sync.prev` / `sync.order_prev` | `prev` | `order` | Gap to the previous dialogue line in ms. |
| `sync.style_next` / `sync.style_prev` | `next` / `prev` | `style` | Gap to the adjacent line with the same style. |
| `sync.actor_next` / `sync.actor_prev` | `next` / `prev` | `actor` | Gap to the adjacent line with the same actor. |
| `sync.effect_next` / `sync.effect_prev` | `next` / `prev` | `effect` | Gap to the adjacent line with the same effect. |
| `sync.layer_next` / `sync.layer_prev` | `next` / `prev` | `layer` | Gap to the adjacent line with the same layer. |

#### Examples in ASS tags:
```ass
{\fad(sync.order_prev / 2, sync.order_next / 2)}
{\t(0, sync.style_next, \fscxy120)}
{\t(fx.dur - sync.next / 2, fx.dur, \alpha&HFF&)}
```

### 6.3. Overriding the Ceiling (`maxgap`)
The default 2000ms ceiling can be changed, globally or locally, for all `sync.*` evaluations by assigning `maxgap` in a `Define Vars` node or in a Python/Lua script:
```python
maxgap = 3500
```
Later evaluations of `sync.order_next` or `sync(next, order)` then use `3500.0` as the cap.

### 6.4. Overlaps and Boundaries
* **Overlapping lines ($\text{gap} < 0$):** if the two lines overlap, `sync` returns the exact negative value ($\Delta t < 0$), which is the length of the overlap.
* **No adjacent line (first/last):** if no line meets the criterion, `sync` returns the configured `maxgap` ceiling.

---

## 7. Performance Telemetry and Pre-Generation Estimation (`Telemetry`)

When a composition combines frame-by-frame loops (`MaxLoop` in `fbf` mode), polygonal slicing (`Shape/Slicer`), particles (`Functions/Particles`) or blurs (`\blur`), playback performance depends mostly on the cost of rasterising and compositing bitmaps in `libass` for each frame.

Diagnostics come in two stages: a **static estimate before generation** and **per-frame render telemetry**.

```
[Graph Topology + ASS Selection]
                 │
                 ├──► [1. Pre-Generation Estimation (Hover on Generate Layers)]
                 │      • Sweep-Line Concurrency (Peak Simultaneous Lines)
                 │      • Expansion Ratio & Estimated ASS Weight (KB / MB)
                 │      • Vector Render Profile (FBF / Slicer / Particles / Audio / Script)
                 │
                 └──► [2. Native libass Telemetry (Refresh in Previewer / Scan in Telemetry)]
                        • Parallel native C rendering + hardware QPC timer (1 µs)
                        • Integrated workload curve on the Previewer transport bar
                        • Diagnostic panel (4 overlaid metrics + 2D navigation)
```

### 7.1. Static Estimate Before Generation
Hovering over the **`Generate Layers`** button evaluates the graph topology and the input lines without compiling the effect:

1. **Estimated lines and expansion ratio:**
   The number of `Dialogue:` events that the connected `System/Output` nodes will emit ($\hat{N}_{\text{out}}$), and its ratio to the selected source lines ($N_{\text{in}}$):
   $$\text{Expansion Ratio} = \frac{\hat{N}_{\text{out}}}{\max(1, N_{\text{in}})}$$
2. **Maximum line concurrency (*Sweep-Line Peak Simultaneous Lines*):**
   Concurrency at a time $t$ is the number of layers on screen at once. The estimator runs an interval *sweep-line* over the projected $[t_{\text{start}}, t_{\text{end}})$ spans of each branch:
   $$L_{\text{peak}} = \max_{t} \sum_{k=1}^{\hat{N}_{\text{out}}} \mathbf{1}_{[t_{\text{start}, k},\, t_{\text{end}, k})}(t)$$
   This is the number of overlapping layers at the densest frame of the effect.
3. **Estimated ASS weight (`KB` / `MB`) and render profile:**
   The expected byte length of the lines, weighted by the operations in the graph (ASSdraw vector paths, `\clip` masks, `\t` transforms), plus badges for the active subsystems (`FBF`, `Slicer`, `Particles`, `Audio`, `Script`).

### 7.2. Native Multi-Process Telemetry (`libass` + QPC)
Running **`Refresh`** in the `System/Previewer` node (or **`Scan`** in the `Telemetry` panel) profiles rendering with the native `libass` C library:

1. **Only the effect is measured:**
   Telemetry renders **only the dialogue lines generated by the effect**, together with the script's styles and metadata. Unmodified lines are left out, so the metrics reflect the cost of the active graph.
2. **Parallel workers and hardware timing (`QPC`):**
   The frame range of the preview clip is split into batches across several parallel processes (`multiprocessing`). Each process creates a `libass` instance at the project resolution ($\text{PlayResX} \times \text{PlayResY}$) and calls `ass_render_frame` frame by frame, timing it with the hardware performance counter ($\text{QPC}$, $1\,\mu\text{s}$ resolution).
3. **Frame budget:**
   To play at video rate without dropped frames, the render time of each frame ($T_{\text{render}}$) must stay below the frame duration set by the video $\text{FPS}$:
   $$\text{Budget}_{\text{ms}} = \frac{1000}{\text{FPS}}, \qquad \text{Budget \%} = \frac{T_{\text{render}}}{\text{Budget}_{\text{ms}}} \times 100\%$$
   At $23.976\,\text{fps}$ the budget is $41.71\,\text{ms}$ per frame, and at $60\,\text{fps}$ it is $16.67\,\text{ms}$. Any frame that exceeds $\text{Budget}_{\text{ms}}$ ($\text{Budget \%} > 100\%$) is recorded as a potential frame drop.
4. **Bitmap memory and primitives (`ASS_Image`):**
   For every frame $f$, the engine walks the linked list of alpha bitmaps produced by `libass` ($\{I_1, I_2, \dots, I_M\}$) and extracts three metrics:
   * **`ASS Objects` ($M_f$):** number of image primitives composited in the frame.
   * **`Total Bitmap RAM`:** memory used by all bitmaps in the frame:
     $$\text{RAM}_{\text{total}}(f) = \frac{1}{1024} \sum_{m=1}^{M_f} \left( w_m \times h_m \right) \quad [\text{KB}]$$
   * **`Largest Bitmap`:** memory used by the largest single bitmap in the frame:
     $$\text{RAM}_{\text{max}}(f) = \frac{1}{1024} \max_{1 \le m \le M_f} \left( w_m \times h_m \right) \quad [\text{KB}]$$

### 7.3. Telemetry Panel and Navigation
The **`Telemetry`** panel (opened from the `Generate Layers` tooltip or by clicking the workload curve in the `Previewer`) has three synchronised regions:

1. **Video viewport and per-frame HUD (top left):**
   * The `System/Previewer` player docks into the viewport and keeps its playback position, subtitle track and focal zoom.
   * A resize control keeps the native video aspect ratio.
   * A HUD bar at the bottom shows the frame index (`F`), timecode (`MM:SS.mmm`), render time (`ms`), bitmap memory (`KB`/`MB`) and object count (`obj`).
2. **Budget gauge, KPI cards and critical points (top right):**
   * **Budget arc gauge (`Frame Budget %`):** semicircular gauge showing peak load as a percentage of the available frame budget.
   * **KPI cards:** values for the whole clip: `Peak Render Time` (frame and timestamp), `Average Render` (with `P95` percentile), `Frame Drops` (count and percentage of the clip), `Peak Bitmap RAM` (with `Max Single`) and `Peak ASS Objects`.
   * **Critical hotspots list:** local load peaks, ranked. Selecting one moves the video playhead and the chart to that frame.
3. **Overlaid chart and 2D navigation (bottom half):**
   * **4 metrics and scale multipliers ($1\times$ – $10\times$):** curves for `Render Time (ms)`, `Total Bitmap RAM`, `Largest Bitmap` and `ASS Objects`, with the horizontal budget limit (`FPS Budget Limit`). Each metric can be toggled individually, and the vertical scale can be multiplied (`1x`, `2x`, `5x`, `10x`).
   * **Navigation:**
     * **`Mouse Scroll Wheel`:** horizontal ($X$) zoom centred on the cursor.
     * **`Ctrl + Wheel` / `Shift + Wheel`:** vertical ($Y$) scale.
     * **`Middle Mouse Button + Drag`:** pan in $X$ and $Y$.
     * **`Left-Click + Drag`:** scrub the video, synchronised with the player.
     * **`R` / `Home` Key:** reset the view to $100\%$ of the time range.

> [!NOTE]
> **Clean per-session state:** both the `Telemetry` chart and the `Previewer` heatmap start empty when a new session is opened or a `Previewer` node is created. They fill only with live measurements after the current effect is applied or refreshed.

# Functions

The **Functions** category has 16 nodes for manipulating ASS tags, generating oscillations, branching on conditions, building colour gradients, and handling motion and vector geometry.

* **8.A, tag modulation, oscillators and conditions:** [`Tag Manipulator`](#1-node-functionstag-manipulator-ass-tag-manipulator) (§1), [`Tag Oscillator`](#2-node-functionstag-oscillator-periodic-tag-modulator) (§2), [`Glitter`](#3-node-functionsglitter-stochastic-sparkle-generator) (§3), [`Conditioner`](#4-node-functionsconditioner-logical-data-branching) (§4), [`Animation`](#8-node-functionsanimation-fbf-frame-switcher-and-alpha-modulator) (§8).
* **8.B, colour gradients, image sampling and kinematics:** [`Color Gradient`](#5-node-functionscolor-gradient-multi-stop-colour-gradient) (§5), [`Clip Gradient`](#6-node-functionsclip-gradient-clipping-bands-and-meshes-for-multi-layer-gradients) (§6), [`IMG to pixels`](#7-node-functionsimg-to-pixels-raster-sampling-to-particle-swarms) (§7), [`Polar to Cartesian`](#12-node-functionspolar-to-cartesian-polar-to-cartesian-converter) (§12), [`Interpolator`](#14-node-functionsinterpolator-polymorphic-parametric-interpolator) (§14).
* **8.C, Bézier curves, particles and vector text:** [`Bezier Curve`](#9-node-functionsbezier-curve-2d-bézier-splines-and-trajectories) (§9), [`Move Tag`](#10-node-functionsmove-tag-kinematic-ass-motion-sequences) (§10), [`Move Text`](#11-node-functionsmove-text-coordinated-inline-typographic-motion) (§11), [`Particles`](#13-node-functionsparticles-vector-particle-swarms) (§13), [`Text on Path`](#15-node-functionstext-on-path-text-flow-along-curved-paths) (§15), [`Text to Shape`](#16-node-functionstext-to-shape-typographic-glyph-vectorisation) (§16).

---

## 1. Node `Functions/Tag Manipulator` (ASS Tag Manipulator)

Transforms ASS tag strings. It can invert tags (complementary colours, inverted alpha, opposite rotations, inverse clips), reset tags to the active style defaults, or extract the value of a given tag.

![Functions/Tag Manipulator](img/tag_manipulator.jpg)

### Modes
**`Mode` (`mode`)** switches what the node does and reconfigures its sockets:
* **`invert` (INV):** inverts every ASS tag in the input string, including tags nested in `\t(...)` blocks.
* **`reset` (RESET):** reads the active subtitle style and generates override tags that restore its default values.
* **`extractor` (EXTRACT):** finds the last occurrence of the tag named in `Target Tag` and extracts its clean value, its numeric value and the raw matching block.

### Inputs

In `invert` and `reset` modes:
1. **`Tags In` (`tags`):** the ASS tags to process. Accepts static tags (e.g. `\frz45\1c&H0000FF&\alpha&H80&`) and `\t(...)` transformations (e.g. `\t(0,300,\frz-45\fscx150)`). In `reset` mode, `"all"` or blank regenerates the full baseline style. (Default: `""`).

In `extractor` mode:
1. **`Tags In` (`tags`):** the tag string to read from (e.g. `{\pos(320,240)\frz-35.5\1c&H00FF88&}`).
2. **`Target Tag` (`target_tag`):** name of the tag to look for, with or without the leading backslash. Accepts the usual ASS aliases such as `frz` / `fr`, `1c` / `c`, `alpha`, `fscx`, `pos`, `org`, `clip`, `blur`. (Default: `"frz"`).

### Outputs

In `invert` and `reset` modes:
1. **`[1.1] Tags Out`:** the inverted tags or the style reset tags.

In `extractor` mode:
1. **`[1.1] String`:** the value without tag prefix or enclosing parentheses (e.g. `"-35.5"`, `"320,240"`, `"&H00FF88&"`).
2. **`[1.2] Value`:** the value as a `float`. For composite coordinates (e.g. `320,240`) it returns the first component (`320.0`). For 1- or 2-digit hexadecimal colour/alpha channels it returns the decimal integer ($0 \dots 255$).
3. **`[1.3] Raw String`:** the full matching tag block as found in the input (e.g. `\frz-35.5`, `\pos(320,240)`).

### Inversion rules (`invert`)

| ASS Tag Family | Supported Tags | Inversion Rule | Example Input $\to$ Output |
| :--- | :--- | :--- | :--- |
| **Primary & Secondary Colours** | `\c`, `\1c`, `\2c`, `\3c`, `\4c` | **Negative RGB Complementary:**<br>$(R', G', B') = (255 - R, 255 - G, 255 - B)$ | `\1c&H0000FF&` $\to$ `\1c&HFFFF00&` (Blue $\to$ Yellow) |
| **Alpha Channels** | `\alpha`, `\1a`, `\2a`, `\3a`, `\4a` | **Hexadecimal Complement:**<br>$\alpha' = 255 - \alpha$ | `\alpha&H00&` $\to$ `\alpha&HFF&` (Opaque $\to$ Transparent) |
| **Rotations, Shearing & Shadows** | `\frz`, `\frx`, `\fry`, `\fr`, `\fax`, `\fay`, `\fsp`, `\xshad`, `\yshad` | **Arithmetic Sign Inversion:**<br>$V' = -V$ | `\frz35` $\to$ `\frz-35`<br>`\fax0.5` $\to$ `\fax-0.5` |
| **Borders, Blurs & Scalar Shadows** | `\bord`, `\xbord`, `\ybord`, `\blur`, `\be`, `\shad` | **Nullification / Zero Reset:**<br>$V' = 0$ | `\bord4\blur3` $\to$ `\bord0\blur0` |
| **Transformation Scales** | `\fscx`, `\fscy` | **Return to Baseline Scale:**<br>$V' = \text{Style.Scale}$ (or $100\%$) | `\fscx200` $\to$ `\fscx100` |
| **Vector Clipping Masks** | `\clip`, `\iclip` | **Inverse Mask Toggle:**<br>`\clip` $\longleftrightarrow$ `\iclip` | `\clip(m 0 0 ...)` $\to$ `\iclip(m 0 0 ...)` |

Inside `\t(t1, t2, [accel,] tags)` blocks, only the nested tags are inverted. The time interval and acceleration are left alone:

$$\text{\textbackslash t}(100, 400, 1.5, \text{\textbackslash frz45\textbackslash 1c\&H0000FF\&}) \quad \longrightarrow \quad \text{\textbackslash t}(100, 400, 1.5, \text{\textbackslash frz-45\textbackslash 1c\&HFFFF00\&})$$

### Style reset (`reset`)
The node looks up the `styleref` of the active context (`active_unit` or `line`) and takes the baseline values from the ASS header.
* If `Tags In` is empty, `"all"` or `"todo"`, it generates the full reset sequence:
  $$\text{\textbackslash 1c}\dots\text{\textbackslash 2c}\dots\text{\textbackslash 3c}\dots\text{\textbackslash 4c}\dots\text{\textbackslash 1a}\dots\text{\textbackslash 2a}\dots\text{\textbackslash 3a}\dots\text{\textbackslash 4a}\dots\text{\textbackslash alpha\&H00\&}\text{\textbackslash fscx}\dots\text{\textbackslash fscy}\dots\text{\textbackslash fs}\dots\text{\textbackslash fsp}\dots\text{\textbackslash bord}\dots\text{\textbackslash shad}\dots\text{\textbackslash frz}\dots$$
* If `Tags In` lists specific tags (e.g. `\1c\fscx`), it resets only those.

### Usage
* **Mirrored effects:** in twin loops or bidirectional particles, send one branch straight through and the other through `Tag Manipulator (INV)` to flip `\frz`, `\fax` and relative shadow offsets.
* **Coordinate extraction:** send the `String` output of `Tag Manipulator (EXTRACT)` with `Target Tag: pos` into a `Math` node to derive trajectories relative to the original glyph position.

### Example: mirrored layers
Two layers, the second one built by inverting the first:

```
[Basics/MultiTag: \frz30\fscx120] ──► Tags In ──► [System/Output (Layer 2)]
               │
               └──► Tags In ──► [Functions/Tag Manipulator: mode=invert] ──► Tags Out ──► [System/Output (Layer 1)]
```

* **Layer 2 (direct):** `{\an5\pos(syl.center, syl.middle)\frz30\fscx120}`.
* **Layer 1 (inverted):** `{\an5\pos(syl.center, syl.middle)\frz-30\fscx100}`. Rotation flips to $-30^\circ$ and scale returns to $100\%$.

---

## 2. Node `Functions/Tag Oscillator` (Periodic Tag Modulator)

Generates periodic, strobe, rhythmic or wave modulations of any ASS property. It compiles the sequence into `\t(...)` blocks covering the lifetime of the active element.

![Functions/Tag Oscillator](img/tag_oscillator.jpg)

### Modes
1. **`Oscillation Mode` (`mode`):** sets the transition profile:
   * **`wave` (Default):** smooth, continuous transition between the states in the tag list ($T_{\text{trans}} = S_i$).
   * **`steps` / `flashes` / `strobe`:** instant switches with no interpolation ($t_2 = t_1 + 1$).
   * **`pulses`:** the transition takes $50\%$ of the step and the rest stays static.
   * **`rhythmic`:** non-uniform steps, read in order from `Rhythm Pattern`.
   * **`noise`:** step variation with pseudo-random fluctuation.
2. **`Order Mode` (`order_mode`):** how tags are picked from the list:
   * **`sequential` (Default):** cycles through the list ($0, 1, 2, \dots, N-1, 0, 1, \dots$).
   * **`pingpong`:** forward then backward ($0, 1, 2, 1, 0, 1, \dots$).
   * **`random`:** a random tag at each step, from a deterministic seed.
   * **`shuffle`:** pseudo-random, never repeating the same tag twice in a row.

### Inputs
1. **`Start Time` (`start_time`):** start in milliseconds relative to the line; blank means `0.0 ms`. (Default: `""`).
2. **`End Time` (`end_time`):** end in ms; blank uses the duration of the active element (`fx.dur`, `syl.duration` or `line.duration`). (Default: `""`).
3. **`Step (ms)` (`step_ms`):** duration of each step/cycle in ms. (Default: `200.0`).
4. **`Trans (ms)` (`trans_ms`):** duration of the `\t` interpolation towards the next tag. (Default: `50.0`).
5. **`Duty Cycle` (`duty_cycle`):** ratio in $[0.01, 1.0]$. When connected or set, it overrides `Trans (ms)` with $T_{\text{trans}} = S_i \cdot \text{DutyCycle}$.
6. **`Tags` (`tags`):** comma- or newline-separated list of tag strings (e.g. `\frz30\fry20, \frz-20\fry-20` or `\1c&HFF0000&, \1c&H00FF00&, \1c&H0000FF&`).
7. **`Accel` (`accel`):** ASS acceleration exponent written into each `\t(...)`. (Default: `1.0`).
8. **`Dilate Step` (`dilat_step_ms`):** amount added to the step on each iteration: $S_i = S_0 + \Delta_{S} \cdot i$. (Default: `0.0`).
9. **`Dilate Trans` (`dilat_trans_ms`):** amount added to the transition on each iteration: $T_i = T_0 + \Delta_{T} \cdot i$. (Default: `0.0`).
10. **`Seq Offset` (`offset_seq_ms`):** extra pause after each full pass through the tag list. (Default: `0.0`).
11. **`Rhythm Pattern` (`rhythm_pattern`):** comma-separated durations (e.g. `100, 50, 200, 100`) used in `rhythmic` mode.

### Outputs
1. **`[1.1] Tag Out`:** the chain of `\t(t1, t2, [accel,] tags)` blocks covering the whole time span.
2. **`[1.2] Current Val`:** the tag active at the current frame time (`frame_time` or `fx_start_time`).
3. **`[1.3] Keyframes`:** list of all keyframes as tuples `[(t1, t2, tag_str, accel), ...]`.
4. **`[1.4] Values`:** list of the tag text at each step.

### Timing

```
Mode: wave (Continuous Transition)
Tags: [ Tag A, Tag B ]
───┬─────────────┬─────────────┬─────────────┬─────────────► Time (ms)
   │ \t(0,200,B) │\t(200,400,A)│\t(400,600,B)│\t(600,800,A)│
   0            200           400           600           800

Mode: steps / strobe (Instantaneous Switching)
───┬─────────────┬─────────────┬─────────────┬─────────────► Time (ms)
   │ \t(0,1,B)   │ \t(200,201,A) \t(400,401,B)│ \t(600,601,A)
   0            200           400           600           800
```

For each step $i \ge 0$:
1. **Step duration ($S_i$):**
   $$S_i = \begin{cases} \text{RhythmPattern}[i \pmod M] & \text{if } \text{rhythm\_pattern} \ne \emptyset \\ \max(5.0, S_{\text{step}} + \Delta_{\text{dilate\_step}} \cdot i) & \text{otherwise} \end{cases}$$
2. **Transition window ($T_i$):**
   $$T_i = \begin{cases} 0 & \text{if mode is } \text{steps/strobe/flashes} \\ S_i \cdot \text{clamp}(DC, 0.01, 1.0) & \text{if } \text{DutyCycle is defined} \\ \min(S_i, \max(0.0, T_{\text{trans}} + \Delta_{\text{dilate\_trans}} \cdot i)) & \text{in standard mode} \end{cases}$$
3. **Timestamps:**
   $$t_1 = \text{round}(T_{\text{start}} + t_{\text{curr}}), \quad t_2 = \begin{cases} t_1 + 1 & \text{if } T_i \le 0 \\ \min(t_{\text{end}}, \text{round}(t_1 + T_i)) & \text{otherwise} \end{cases}$$

### Usage
* **Vibrato:** `Tags` = `\frz-5, \frz5` with `Step: 60` and `Trans: 30` gives a subtle continuous vibrato on sung syllables.
* **Audio-synced pulsing:** use `Mode: rhythmic` and put intervals measured from the audio (`125, 250, 125, 375`) into `Rhythm Pattern`.

### Example: vibrato and scale wave on a sustained note
A wave over a $300\text{ ms}$ syllable:

```
[Functions/Tag Oscillator: mode=wave, step_ms=80, trans_ms=40] ──► Tag Out ──► Tags ──► [System/Output]
   tags: "\frz-4\fscy95, \frz4\fscy105"
```

`Tag Out` contains:
```ass
\t(0,40,\frz-4\fscy95)\t(80,120,\frz4\fscy105)\t(160,200,\frz-4\fscy95)\t(240,280,\frz4\fscy105)
```
The glyph alternates between a $\mp 4^\circ$ tilt and a $95\%$ to $105\%$ vertical stretch.

---

## 3. Node `Functions/Glitter` (Stochastic Sparkle Generator)

Emits random flashes, pulses, waves or noise on several ASS properties at once, to simulate shimmer and glitter without a predictable repeat.

![Functions/Glitter](img/glitter.jpg)

### Modes
**`Mode` (`mode` / `random_profile`)** selects the temporal envelope:
* **`flashes` (Default):** long random pause $\to$ very fast attack ($1 \dots 3\text{ ms}$) $\to$ short sustain ($5 \dots 15\text{ ms}$) $\to$ long decay ($40 \dots 100\text{ ms}$). Suited to sparkles and glitter.
* **`pulses`:** moderate pause $\to$ progressive rise ($150 \dots 250\text{ ms}$) $\to$ sustain $\to$ symmetrical fall with non-linear acceleration.
* **`waves`:** slow, continuous rise and fall ($250 \dots 400\text{ ms}$) with no sharp pauses.
* **`noise`:** very short steps ($15 \dots 50\text{ ms}$) with a random value per frame.

### Inputs
1. **`Start Time` (`start_time`):** start in ms. (Default: `"0"`).
2. **`End Time` (`end_time`):** end in ms or a context expression (e.g. `"fx.dur"`). (Default: `"fx.dur"`).
3. **`Density` (`density`):** frequency multiplier. Values $> 1.0$ shorten the pauses and give more sparkles per second; values $< 1.0$ space them out. (Default: `1.0`).
4. **`Seed` (`seed`):** integer seed for reproducible output. (Default: `0`).
5. **Expandable track inputs (`In 1`, `In 2`, ...):** each track has three fields:
   * **`Tag` (`tag_k`):** the ASS tag to animate (e.g. `\fscx`, `\1c`, `\blur`, `\alpha`, `\frz`).
   * **`Min` (`min_k`):** resting value (number, percentage, hex colour `#RRGGBB` or `&HBBGGRR&`).
   * **`Max` (`max_k`):** value at the peak of the flash.

`Tag` also accepts these grouped "dark tags":
* `\fscxy`: animates `\fscx` and `\fscy` with the same value.
* `\frxyz`: animates `\frx`, `\fry` and `\frz` together.
* `\134c`: animates primary (`\1c`), border (`\3c`) and shadow (`\4c`) colours together.
* `\xybord`: expands to `\xbord` and `\ybord`.
* `\bs`: animates border `\bord` and shadow `\shad` together.

### Outputs
1. **`[1.1] List`:** all `\t(...)` blocks from all tracks, synchronised at the same timestamps.
2. **`[1.2] TAG 1`:** the `\t(...)` blocks of the first track only.
3. **`[1.3] TAG 2` (expandable):** the same for the second track, and so on.

### How it works

```
Profile Envelope: flashes (Sparkle)
Max Value (Apex) ────────┐       /───\
                         │      /     \
                         │     /       \
Base Value (Rest) ───────┴────/         \──────────────
                         ▲    ▲ ▲     ▲ ▲
                         │    │ │     │ │
                         └──┬─┘ └─┬─┘ └─┬────────┘
                         Pause   Attack  Decay
                         (dens)  (1-3ms) (40-100ms)
```

1. **Seed per unit:** the random generator is seeded separately for each syllable or glyph ($i$):
   $$\text{Seed}_{\text{local}} = \text{Seed} \cdot 1000 + i + 1337$$
2. **Colours:** if `Min` and `Max` are colours, the channels $(R_1, G_1, B_1)$ and $(R_2, G_2, B_2)$ are interpolated in RGB space and written as `&HBBGGRR&`:
   $$R_{\text{rand}} = \text{round}(R_1 + (R_2 - R_1) \cdot \text{Factor}), \quad G_{\text{rand}} = \text{round}(G_1 + (G_2 - G_1) \cdot \text{Factor})$$

### Usage
* **Fairy dust:** `In 1` = `\fscxy` with `(100, 160)`, `In 2` = `\1c` with `(#FFFFFF, #FFE460)`. Connect `List` to `System/Output` for simultaneous scale and golden colour bursts.

### Example: golden sparkles
Random bursts on each character over $400\text{ ms}$:

```
[Functions/Glitter: mode=flashes, density=1.5, start=0, end=400] ──► List ──► Tags ──► [System/Output]
   In 1: tag=\fscxy, min=100, max=140
   In 2: tag=\1c, min=#FFFFFF, max=#FFD700
```

The node interpolates the RGB channels and expands `\fscxy`. `List` looks like this:
```ass
\t(83,85,\fscx133\fscy133\1c&H00D7FF&)\t(93,173,\fscx105\fscy105\1c&HFFFFFF&)\t(208,211,\fscx133\fscy133\1c&H00D7FF&)...
```
Each glyph gets its own timing from its index, so the flashes don't fire in unison.

---

## 4. Node `Functions/Conditioner` (Logical Data Branching)

Inline conditional ($A \text{ if } \text{Cond} \text{ else } B$). It picks one of two values (text, ASS tags, numbers or lists) depending on an expression evaluated against the subtitle context.

![Functions/Conditioner](img/conditioner.jpg)

### Inputs
1. **`Condition` (`condition`):** boolean expression. Accepts constants (`True`, `False`, `1`, `0`), comparisons (`syl.i % 2 == 0`, `char.i > 3`), membership checks (`line.style == "Romaji"`, `'kanji' in line.tags_str`), or a boolean cable. (Default: `"True"`).
2. **`If True` (`if_true`):** value emitted when the condition is true ($C = \text{True}$). Can be an ASS tag string, number, list or cable. (Default: `""`).
3. **`If False` (`if_false`):** value emitted when the condition is false ($C = \text{False}$). (Default: `""`).

### Outputs
1. **`[1.1] Out`:** the selected value. If it is a list or tuple, the elements are joined with `, `.

### Evaluation
The expression is evaluated in an isolated environment that exposes the following context variables:

| Injected Variable | Type | Description |
| :--- | :---: | :--- |
| `syl.i`, `char.i`, `word.i`, `fx.i`, `j`, `i` | `int` | Sequential index of the active element ($0$-based or $1$-based). |
| `syl.n`, `char.n`, `word.n`, `line.n` | `int` | Total unit count in the iteration group. |
| `line.style`, `line.actor`, `line.effect` | `str` | Original dialogue line metadata. |
| `line.duration`, `syl.duration`, `fx.dur` | `float` | Duration in milliseconds. |
| `syl.text`, `char.text` | `str` | Text content or phoneme of the active glyph. |

$$\text{Out} = \begin{cases} \text{If True} & \text{if } \text{eval}(\text{Condition}, \text{Context}) = \text{True} \\ \text{If False} & \text{otherwise} \end{cases}$$

### Usage
* **Alternating colours:** `Condition` = `syl.i % 2 == 0`, `If True` = `\1c&H00FFFF&` (cyan), `If False` = `\1c&HFF00FF&` (magenta).
* **Skipping whitespace:** `Condition: char.text.strip() == ""` lets you bypass heavy transformations on spaces.

### Example: even/odd characters
A different colour and scale for even and odd characters inside the main character loop:

```
[Loops/Main Loop: char] ──► char.i ───────────────────────────────┐
                                                                  ▼
[Functions/Conditioner: condition="char.i % 2 == 0"] ──► Out ──► Tags ──► [System/Output]
   If True:  "\1c&H00FFFF&\fscxy110"
   If False: "\1c&HFF0088&\fscxy90"
```

* **Even characters ($i \in \{2, 4, 6\}$):** `{\an5\pos(char.center, char.middle)\1c&H00FFFF&\fscx110\fscy110}`.
* **Odd characters ($i \in \{1, 3, 5\}$):** `{\an5\pos(char.center, char.middle)\1c&HFF0088&\fscx90\fscy90}`.

One node handles both cases, with no duplicate layers or empty events.

---

## 5. Node `Functions/Color Gradient` (Multi-Stop Colour Gradient)

Interpolates between several colour stops (*multi-stop gradient*) with an acceleration (easing) curve. It returns the colour at a position $t \in [0.0, 1.0]$, or batch colour lists and ASS tags for characters, syllables or particles.

![Functions/Color Gradient](img/color_gradient.jpg)

### Inputs
1. **`Progress (0-1)` (`prog`):** interpolation factor $t \in [0.0, 1.0]$. Accepts constants, cables or context expressions (e.g. `char.i / char.n`, `syl.i / syl.n`, `j / maxloop`). (Default: `"char.i / char.n"`).
2. **`Color List` (`colors_str`):** colour stops separated by commas, spaces or newlines. Accepts hex codes (`#RRGGBB`), HTML names or ASS codes (`&HBBGGRR&`). (Default: `"#95E648,#3E750C,#ED38CA"`).
3. **`Total (N)` (`total`):** number of samples for batch outputs (`Color List` or `Tags`). If $N > 1$, it generates $N$ evenly spaced samples from $t=0.0$ to $t=1.0$. (Default: `"1"`).
4. **`Accel` (`accel`):** acceleration exponent. `1.0` is linear; values $> 1.0$ weight the transition towards the end (*ease-in*); values $< 1.0$ weight it towards the start (*ease-out*). (Default: `"1.0"`).
5. **`Tag` (`tag_type`):** tag prefixed to the colour codes in the `Tags` output (`\1c`, `\2c`, `\3c`, `\4c` or `\c`). (Default: `"\1c"`).

### Outputs
1. **`[1.1] ASS Color`:** the colour `&HBBGGRR&` at progress $t$ from `Progress (0-1)`.
2. **`[1.2] Color List`:** comma-separated ASS colours for the $N$ steps if $N > 1$, or the single colour if $N = 1$.
3. **`[1.3] Tags`:** the same colours with the tag prefix (e.g. `\1c&H48E695&` for $N=1$, or `\1c&H48E695&, \1c&H0C753E&, \1c&HCADB38&` for $N > 1$).

### How it works

```
Stops:    C1 (#95E648)          C2 (#3E750C)          C3 (#ED38CA)
          ├──────────────────────────┼──────────────────────────┤
Progress: t = 0.0                  t = 0.5                  t = 1.0
Segment:  └────── Segment 0 ───────┘└────── Segment 1 ───────┘
```

**Easing.** Before interpolating colours, the progress $t \in [0.0, 1.0]$ goes through the acceleration function:

$$t_{\text{eased}} = \begin{cases} t^{\text{accel}} & \text{if } \text{accel} > 1.0 \\ 1.0 - (1.0 - t)^{1.0 / \text{accel}} & \text{if } 0.0 < \text{accel} < 1.0 \\ t & \text{if } \text{accel} = 1.0 \end{cases}$$

**Segment mapping and RGB interpolation.** With $K$ colour stops $\{C_0, C_1, \dots, C_{K-1}\}$:
1. Find the segment ($K-1$ in total):
   $$\text{pos} = t_{\text{eased}} \cdot (K - 1), \quad \text{idx} = \min(K - 2, \lfloor \text{pos} \rfloor), \quad t_{\text{local}} = \text{pos} - \text{idx}$$
2. Take the RGB channels of the adjacent stops $C_{\text{idx}} = (R_1, G_1, B_1)$ and $C_{\text{idx}+1} = (R_2, G_2, B_2)$.
3. Interpolate each channel linearly:
   $$R = \text{round}(R_1 + (R_2 - R_1) \cdot t_{\text{local}})$$
   $$G = \text{round}(G_1 + (G_2 - G_1) \cdot t_{\text{local}})$$
   $$B = \text{round}(B_1 + (B_2 - B_1) \cdot t_{\text{local}})$$
4. Write the result in ASS BGR hex format: `&HBBGGRR&`.

### Usage
* **Per-character gradient:** keep `Progress: char.i / char.n` and connect `Tags` to `System/Output`. Each character gets its own colour.
* **Colour keyframes with `Concatenate (Zip)`:** set `Total: 5`, connect `Tags` to Input 1 of `Basics/Concatenate (Zip)` and a time sequence `\t(0,200,), \t(200,400,), ...` to Input 2.

### Example: three-colour gradient across a line
Three stops (`#FF4500` orange-red, `#FFD700` gold, `#00FFFF` cyan) with ease-in acceleration, one colour per character:

```
[Loops/Main Loop: mode=char] ──► char.i / char.n ─────────────────────┐
                                                                       ▼
[Functions/Color Gradient: accel=1.0] ──► Tags (\1c) ──────────────► Tags In ──► [System/Output]
   colors: "#FF4500, #FFD700, #00FFFF"
```

* **First character ($t=0.0$):** `{\an5\pos(320, 240)\1c&H0045FF&}` (orange-red).
* **Middle character ($t \approx 0.5$):** `{\an5\pos(420, 240)\1c&H00D7FF&}` (gold).
* **Last character ($t=1.0$):** `{\an5\pos(520, 240)\1c&HFFFF00&}` (cyan).

---

## 6. Node `Functions/Clip Gradient` (Clipping Bands and Meshes for Multi-Layer Gradients)

Splits the visible ink area (*glyph ink bounding box*) of the active element into stripes or a $C \times R$ grid of cells with sub-pixel overlap. The grid fits the real glyph contour instead of the empty typographic margins. Used for multi-layer colour gradients, angled wipes and cell transitions in libass without visible seams.

![Functions/Clip Gradient](img/clip_gradient.jpg)

### Modes
**`Mode` (`out_mode`)** sets the output syntax:
* **`\clip` (`clip`, Default):** emits `\clip(x1,y1,x2,y2)` for rectangles, or the vector form `\clip(m x1 y1 l x2 y2 ...)`.
* **`\iclip` (`iclip`):** emits inverse clips `\iclip(...)`.
* **`Shape` (`shape`):** emits plain ASSdraw path code (`m ... l ...`) centred on the local origin `(0, 0)`, to feed geometry nodes.

### Inputs
1. **`Cols` (`cols`, slot `0`):** number of columns. (Default: `"5"`).
2. **`Rows` (`rows`, slot `1`):** number of rows. `Rows: 1` gives vertical stripes, `Cols: 1` gives horizontal stripes, and larger values in both give a 2D grid ($N = \text{Cols} \times \text{Rows}$). (Default: `"1"`).
3. **`Angle` (`angle`, slot `2`):** tilt of the grid or stripes in degrees ($0^\circ \dots 360^\circ$). $0^\circ$ gives rectangular cells; other angles give rotated quadrilaterals. (Default: `"0"`).
4. **Padding cross (no socket, 5 inline text boxes):** expands the clip area beyond the glyph ink edges, per direction or uniformly:
   * **`Pad Top` (`pad_top`):** extra pixels upwards. (Default: `"0"`).
   * **`Pad Left` (`pad_left`):** extra pixels to the left. (Default: `"0"`).
   * **`Padding` (`padding`, centre):** pixels added in all 4 directions on top of each directional value ($\text{eff}_{\text{dir}} = \text{padding} + \text{pad}_{\text{dir}}$). (Default: `"0"`).
   * **`Pad Right` (`pad_right`):** extra pixels to the right. (Default: `"0"`).
   * **`Pad Bottom` (`pad_bottom`):** extra pixels downwards. (Default: `"0"`).
5. **`Overlap` (`overlap`, slot `3`):** sub-pixel growth in pixels applied to each cell to hide libass anti-aliasing seams. (Default: `"0.5"`).
6. **`Order` (`order`, slot `4`):** 2D ordering (Numpad, radial or random): `"79"`, `"97"`, `"13"`, `"31"`, `"71"`, `"17"`, `"93"`, `"39"`, `"5"`, `"-5"`, `"cw"`, `"ccw"`, `"rand"`. (Default: `"79"`).

### Outputs
1. **`[1.1] Output`:** the `\clip(...)` / `\iclip(...)` tag or ASSdraw path for the active cell.
2. **`[1.2] Progress (0-1)`:** progress of the current cell:
   $$\text{Progress} = \frac{k}{N - 1} \in [0.0, 1.0]$$
3. **`[1.3] Index`:** index of the active cell ($1$-based: $1 \dots N$).
4. **`[1.4] Total`:** total cell count ($N = \text{Cols} \times \text{Rows}$).
5. **`[1.5] Col`:** column of the active cell ($1 \dots \text{Cols}$).
6. **`[1.6] Row`:** row of the active cell ($1 \dots \text{Rows}$).

Context variables injected:
* **`c_i` / `clip_i`:** index of the active cell.
* **`c_n` / `clip_n` / `clip_max`:** total number of cells ($N$).
* **`c_col` / `col`:** current column ($1$-based).
* **`c_row` / `row`:** current row ($1$-based).

### Geometry

```
1D Stripes (Cols: 4, Rows: 1)      2D Mesh (Cols: 3, Rows: 2)        Rotated Mesh (Angle θ)
┌───┬───┬───┬───┐                 ┌─────┬─────┬─────┐                ┌───────/───────┐
│   │   │   │   │                 │ 0,0 │ 1,0 │ 2,0 │               / 0,0   / 1,0   /
│ 0 │ 1 │ 2 │ 3 │                 ├─────┼─────┼─────┤              /───────/───────/
│   │   │   │   │                 │ 0,1 │ 1,1 │ 2,1 │             / 0,1   / 1,1   /
└───┴───┴───┴───┘                 └─────┴─────┴─────┘            └───────/───────┘
```

**Angle $0^\circ$.** The node outputs plain axis-aligned `\clip(x1, y1, x2, y2)` rectangles, which are the cheapest for libass to rasterise:
$$W_{\text{cell}} = \frac{B_{\text{width}}}{C}, \quad H_{\text{cell}} = \frac{B_{\text{height}}}{R}$$
$$x_1 = B_{\text{left}} + c \cdot W_{\text{cell}} - \text{ov}, \quad x_2 = B_{\text{left}} + (c + 1) \cdot W_{\text{cell}} + \text{ov}$$
$$y_1 = B_{\text{top}} + r \cdot H_{\text{cell}} - \text{ov}, \quad y_2 = B_{\text{top}} + (r + 1) \cdot H_{\text{cell}} + \text{ov}$$

**Any other angle ($\theta$).** The cell dimensions are projected onto the rotated axes $u$ and $v$, and the 4 cell vertices are rotated around the centre $(C_x, C_y)$:
$$P_x = C_x + u \cos \theta - v \sin \theta, \quad P_y = C_y + u \sin \theta + v \cos \theta$$
The result is a closed 4-point path: `\clip(m p1_x p1_y l p2_x p2_y l p3_x p3_y l p4_x p4_y)`.

### Ink measurement and alignment (`\an1` .. `\an9`)
The node checks what the graph returns (`Return` on the `Output` node) and the active `\an` alignment, so the clip lands on the real ink:
* **Shape** (ASSdraw path, shape library or slicer pieces): detected from the ASSdraw commands or from shape generator nodes (`Shape/Library`, `Shape/Manipulator`, `Shape/Slicer`, etc.). The ink bounding box of the contours is computed directly.
* **Text:** the ink contour (*glyph ink contour*) of the active unit or karaoke line is measured. If a different custom text is passed to the return port, the node vectorises it with the font vector engine to get its exact ink bounds.
* **Alignment:** `\an5` is assumed unless another alignment comes from the `Output` node's alignment widget, context tags or properties.
  * With `\an7` (the usual convention for particle systems and slicer pieces rotated around their own local axes), the clip's top-left corner sits at `\pos(x, y)` (`left = pos_x`, `top = pos_y`), so it fits without offsets. With `\an1` it aligns to the bottom-left corner (`top = pos_y - h`), and likewise for the other numpad positions.

### Usage
* **Multi-layer gradient in `MaxLoop`:** use `Loops/MaxLoop` with `Total: 10`, `Clip Gradient` with `Rows: 10` (horizontal stripes), and send `Progress (0-1)` into `Functions/Color Gradient (Progress)`. Each layer gets its stripe and the matching colour.

### Example: vertical gradient in 5 stripes
The text is split into 5 horizontal stripes with `overlap=0.5`, and each stripe gets a colour interpolated between magenta (`#FF007F`) and violet (`#7F00FF`):

```
[Loops/MaxLoop: total=5] ──► j ───────────────────────────────┐
                                                               ▼
[Functions/Clip Gradient: cols=1, rows=5] ──► Progress (0-1) ─► Prog ──► [Functions/Color Gradient]
   out_mode: "\clip", overlap: 0.5                             colors: "#FF007F, #7F00FF"
                                  │                                           │
                                  ▼ Output (\clip)                            ▼ Tags (\1c)
                               Tags In ──────────────────────────────────── Tags In ──► [System/Output]
```

* **$j=1$ (top stripe):** `{\clip(300, 199.5, 450, 208.5)\1c&H7F00FF&}`.
* **$j=3$ (middle stripe):** `{\clip(300, 215.5, 450, 224.5)\1c&HBF00BF&}`.
* **$j=5$ (bottom stripe):** `{\clip(300, 231.5, 450, 240.5)\1c&HFF007F&}`.

The $0.5\text{ px}$ overlap absorbs libass sub-pixel rounding, so no seams show.

---

## 7. Node `Functions/IMG to pixels` (Raster Sampling to Particle Swarms)

Samples an image file (PNG, JPG, WEBP, animated GIF) and turns its opaque pixels into vector particles. Each particle has the sampled colour `\1c`, alpha `\alpha`, screen position `\pos(x, y)` and a Numpad order. It uses GPU acceleration and a global cache.

![Functions/IMG to pixels](img/img_to_pixels.jpg)

### Inputs
1. **`Image Path` (`image_path`):** absolute path to the image or animated GIF.
2. **`Particle` (`particle_shape`):** ASSdraw shape used for each pixel. If empty, a micro-square scaled to the step size is used: `m 0 0 l s 0 l s s l 0 s`.
3. **`Frame` (`frame_idx` / `frame`):** frame to sample in animated GIFs ($1$-based). (Default: `"1"`).
4. **`Step` (`step`):** sampling stride in pixels. `1` samples every pixel; `2` samples 1 pixel in every $2 \times 2$ block, which cuts the number of ASS lines a lot while keeping the silhouette. (Default: `2`).
5. **`Alpha` (`alpha_threshold`):** alpha cutoff ($0 \dots 255$). Pixels with lower opacity are discarded as background. (Default: `128`).
6. **`Scale` (`scale`):** multiplier for coordinates and image size. (Default: `1.0`).
7. **`Anchor` (`anchor`):** reference point (`center`, `topleft`, `topright`, `bottomleft`, `bottomright`). (Default: `"center"`).
8. **`Order` (`order`):** 2D ordering code (`79`, `97`, `13`, `31`, `71`, `17`, `93`, `39`, `5`, `-5`, `cw`, `ccw`, `rand`). (Default: `"79"`).

> [!TIP]
> **Double-click the preview card** (centre thumbnail) to open the OS file dialogue and pick an image (`.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`). It updates `image_path` and shows the texture immediately.

### Outputs
1. **`[1.1] Shp Out`:** ASSdraw code of the active particle.
2. **`[1.2] Color Arr`:** the colour `&HBBGGRR&` sampled from the image.
3. **`[1.3] \pos Tag`:** the `\pos(x, y)` tag, computed by adding the pixel offset to the element centroid.
4. **`[1.4] X Arr`:** absolute horizontal screen coordinate $X$ in pixels.
5. **`[1.5] Y Arr`:** absolute vertical screen coordinate $Y$ in pixels.
6. **`[1.6] Total`:** number of sampled particles ($N$).
7. **`[1.7] Pixels Array`:** list of all sampled pixels `[(x, y, r, g, b, alpha), ...]`.

Context variables injected:
* **`ip_i` / `img_p_i`:** index of the active particle ($1 \dots N$).
* **`ip_n` / `img_p_n` / `total_pixels` / `maxloop`:** total particle count.
* **`fx_pos_x`, `fx_pos_y`, `x`, `y`:** absolute particle coordinates.

### How it works

```
Raster Image (Pillow / NumPy)           ASS Vector Swarm
┌────────────────────────┐              ┌────────────────────────┐
│  Pixels with α ≥ 128   │  Sampling    │  ASSdraw Particles     │
│  (x % step == 0)       │ ───────────► │  \pos(x, y)            │
│  (y % step == 0)       │   Step = 2   │  \1c&HBBGGRR&          │
└────────────────────────┘              └────────────────────────┘
```

1. **Mask:** the image is loaded as a NumPy RGBA array of shape $(H, W, 4)$ and filtered with vectorised indexing:
   $$\text{Mask} = (\text{Alpha} \ge \text{Threshold}) \land (X \pmod{\text{Step}} = 0) \land (Y \pmod{\text{Step}} = 0)$$
2. **Cache:** parsed arrays are cached in memory by `(path, frame, step, threshold, scale, anchor, order)`, so render loops don't re-read the file.
3. **GPU (OpenCL/CUDA):** when the GPU backend is active, coordinate translation, scaling and Numpad sorting run as OpenCL kernels.

### Usage
* **Logo disintegration:** send `IMG to pixels` into `Loops/MaxLoop (total_pixels)`, connect `\pos Tag` to `Functions/Move Tag (Trajectory)` with a per-particle offset (`ip_i`), and output to `System/Output`.
* **Performance:** for high-resolution images ($1920 \times 1080$) use `Step: 4` or `Step: 6` to keep the particle count between $500 \dots 2000$ and 60 FPS playback in the WebAssembly player.

### Example: emblem as a swarm of 2x2 particles
A local PNG sampled with `step=2`, alpha threshold $128$ and centred anchor:

```
[Functions/IMG to pixels: step=2, anchor=center] ──► Total (N) ──► Total ──► [Loops/MaxLoop]
   image_path: "C:/assets/logo_spark.png"                                         │
      │                                                                           │ j (ip_i)
      ├─► Shp Out (m 0 0 l 2 0...) ───────────────► Shape / Text ◄────────────────┘
      ├─► Color Arr (&HBBGGRR&) ──────────────────► Tags In
      └─► \pos Tag (\pos(x, y)) ──────────────────► Tags In ──► [System/Output]
```

* **Particle 1 ($x=620, y=340$):** `{\an5\pos(620, 340)\1c&H22AAFF&\1a&H00&\p1}m 0 0 l 2 0 l 2 2 l 0 2`.
* **Particle 250 ($x=640, y=360$):** `{\an5\pos(640, 360)\1c&HFFFFFF&\1a&H00&\p1}m 0 0 l 2 0 l 2 2 l 0 2`.

Each micro-square keeps its sampled texture colour. The output is exactly $N$ events, one per opaque pixel, with transparent regions skipped.

---

## 8. Node `Functions/Animation` (FBF Frame Switcher and Alpha Modulator)

Cycles through a list of ASSdraw shapes, glyphs or text strings. It either switches frames one by one (*FBF*, frame-by-frame) with synchronised frame indices, or toggles visibility with `\t` blocks on the alpha channel (`\alpha` or `\1a..\4a`) compiled into one subtitle line.

![Functions/Animation](img/animation.jpg)

### Modes
1. **`FBF` (*Frame-by-Frame*):** each main-loop iteration (`an_i` or `j`) picks the active shape in the sequence. `Shape` emits the vector path with `{\an7}`.
2. **`Alpha`:** compiles `\t` visibility cycles that switch opacity between visible (`&H00&`) and transparent (`&HFF&`) at the computed times.

### Inputs
1. **`Frames / Text` (`frames`):** the sequence of shapes or text. Accepts:
   * Library primitive names (e.g. `"Circle, Star, Heart"`).
   * JSON arrays (e.g. `["m 0 0 l 10 10", "m 0 0 l 20 20"]`).
   * Delimited lists (commas, semicolons `;` or newlines `\n`).
   * Plain text (converted to vector glyphs).
   * Context variable references (e.g. `Shapes1`, `my_frames`).
2. **`Step ms` (`step_ms`):** duration of each frame in ms ($41.7\text{ ms} \approx 24\text{ FPS}$; $33.3\text{ ms} \approx 30\text{ FPS}$; $16.6\text{ ms} \approx 60\text{ FPS}$). (Default: `41.7`).
3. **`Start Time` (`start_time`):** start in ms (`0` or blank uses the effect start `fx.st` / `syl.start_time`).
4. **`End Time` (`end_time`):** end in ms (`fx.dur` or blank uses the full duration).
5. **`Alpha Tag` (`alpha_tag`):** [Alpha mode] the transparency tag to modulate, or a composite dark tag: `\alpha`, single channels `\1a`, `\2a`, `\3a`, `\4a`, pairs `\12a`, `\13a`, `\14a`, `\23a`, `\24a`, `\34a`, triples `\123a`, `\124a`, `\134a`, `\234a`, or all four `\1234a`. This lets you switch only some channels (e.g. `\13a` modulates fill and border without touching the `\4a` shadow). (Default: `"\alpha"`).
6. **`Variable Prefix` (`var_name`):** prefix for the loop context variables. (Default: `"an"`).

### Outputs

In FBF mode:
1. **`[1.1] Shape`:** ASSdraw code of the active frame, prefixed with `{\an7}`.
2. **`[1.2] Frame`:** active frame index (1-based integer: $1, 2, \dots, N$).
3. **`[1.3] Frames List`:** array of all processed paths.

In Alpha mode:
1. **`[1.1] Shape`:** the active shape wrapped in its visibility tags `{\an7\alpha&HFF&\t(...)\p1}...`.
2. **`[1.2] Tags`:** the tag string alone (`\an7\alpha&HFF&\t(...)`), without drawing commands.
3. **`[1.3] Frame`:** active frame index (1-based).
4. **`[1.4] Frames List`:** array of all paths.

Context variables exposed:
* `{var_name}_i` / `an_i`: active frame index ($1 \dots K$).
* `{var_name}_n` / `an_n`: number of unique frames ($K$).
* `an_total_cycles`: number of full animation cycles completed within the total duration.

### How it works
Given $K$ frames $\{F_0, F_1, \dots, F_{K-1}\}$, frame interval $\Delta t_{\text{frame}} = \text{step\_ms}$, and interval $[t_{\text{start}}, t_{\text{end}}]$ with duration $D = t_{\text{end}} - t_{\text{start}}$:

```
Frame Index:     F0       F1       F2       F0       F1       F2
Time (ms):    ├───Δt───┼───Δt───┼───Δt───┼───Δt───┼───Δt───┼───Δt───┤
Cycle:        └─────── Cycle 1 ──────────┘└─────── Cycle 2 ──────────┘
```

**FBF mode.** For iteration $j \ge 1$:
$$\text{active\_idx} = (j - 1) \pmod K$$
$$\text{Frame} = \text{active\_idx} + 1$$
Frames needed to cover the duration:
$$N_{\text{total}} = \left\lceil \frac{D}{\Delta t_{\text{frame}}} \right\rceil$$

**Alpha mode.** For each cycle $k \in [0, N_{\text{cycles}}]$ and local frame $i$:
$$t_1 = \Delta t_{\text{frame}} \cdot (K \cdot k + i)$$
$$t_2 = t_1 + 1.0$$
$$t_3 = \Delta t_{\text{frame}} \cdot (K \cdot k + i + 1)$$
$$t_4 = \min(D, t_3 + 1.0)$$
Each frame gets the visibility pair:
$$\backslash\text{t}(t_1, t_2, \text{tag}\&H00\&)\backslash\text{t}(t_3, t_4, \text{tag}\&HFF\&)$$

### Usage
* **GIFs and spritesheets:** send `Shapes Array` from `Shape/IMG to Shape` into `Frames / Text` to play back the frames of a GIF.
* **`Loops/MaxLoop (fbf)`:** set `MaxLoop` to `fbf` mode and it iterates exactly as many frames as the karaoke line duration needs.

### Example: vector frame cycle at 24 FPS
Cycling `circle`, `star`, `heart` at 24 FPS ($41.7\text{ ms}$ per frame):

```
[Loops/MaxLoop: mode=fbf, step_ms=41.7] ──► j ────────────────────────┐
                                                                       ▼
[Functions/Animation: mode=FBF, step_ms=41.7] ──► Shape ──► Shape / Text ──► [System/Output]
   frames: "circle, star, heart"
```

* **$j=1$:** `{\an7}m 50 0 b 22 0 0 22 0 50 ...` (library circle).
* **$j=2$:** `{\an7}m 38 36 l 0 36 l 31 59 ...` (star).
* **$j=3$:** `{\an7}m 50 25 b 50 10 35 0 20 0 ...` (heart).
* **$j=4$:** wraps back to frame $1$, and keeps cycling for the whole subtitle.

---

## 9. Node `Functions/Bezier Curve` (2D Bézier Splines and Trajectories)

Generates, evaluates and interpolates 2D Bézier curves. It uses De Casteljau's algorithm for quadratic, cubic and $N$-degree curves. It also offers constant speed by numerical arc-length integration, tangent and normal extraction, curve subdivision, and smooth random trajectories.

![Functions/Bezier Curve](img/bezier_curve.jpg)

### Modes
1. **`Cubic 2D`:** cubic Bézier curve from 4 control points ($P_0, P_1, P_2, P_3$).
2. **`Quadratic 2D`:** quadratic Bézier curve from 3 control points ($P_0, P_1, P_2$).
3. **`N-Degree`:** curve of degree $N$ from the list in `Points` ($P_0, P_1, \dots, P_N$).
4. **`Constant Speed`:** arc-length corrected mapping of $t \in [0.0, 1.0]$ using Simpson's rule, for uniform speed in pixels/second.
5. **`Shape Contour`:** samples an ASSdraw path connected to `Shape` by parameter.
6. **`Subdivide`:** splits the curve at parameter $t$ into two independent splines (`Spline L` and `Spline R`).
7. **`Trajectory`:** generates smooth random paths from linked cubic splines (`Free Wander`, `Bounded`, `Closed Loop`).

### Inputs
1. **`Origin` (`origin`):** coordinate $(X_0, Y_0)$ added as an offset to all control points. (Default: `"0,0"`).
2. **`P0, P1, P2, P3` (`p0`, `p1`, `p2`, `p3`):** control point coordinates $(X, Y)$. Accepts tuples separated by commas or spaces, or cables.
3. **`t` (`t`):** evaluation parameter $t \in [0.0, 1.0]$. Accepts context variables such as `j / maxloop` or `char.i / char.n`. (Default: `"0.5"`).
4. **`Subdivs` (`subdivs`):** number of steps for contour sampling and arc-length integration. (Default: `"100"`).
5. **`Shape` (`shape`):** ASSdraw path for `Shape Contour` and `Trajectory` modes.
6. **`Points` (`points`):** control points for `N-Degree` mode (e.g. `"0,0; 50,100; 150,100; 200,0"`).
7. **`Trajectory Mode` (`traj_mode`):** trajectory type (`"Free Wander"`, `"Bounded"`, `"Closed Loop"`).
8. **`Dist Range` (`dist_range`):** min/max distance between random spline nodes (e.g. `"50,120"`).
9. **`Seed` (`seed`):** pseudo-random seed for trajectory generation. (Default: `"1"`).
10. **`Loops` (`loops`):** number of chained cubic segments in the trajectory. (Default: `"8"`).

### Outputs
1. **`[1.1] \pos`:** the `\pos(X, Y)` tag at parameter $t$.
2. **`[1.2] X`:** horizontal coordinate $X(t)$ (integer or 2-decimal float).
3. **`[1.3] Y`:** vertical coordinate $Y(t)$.
4. **`[1.4] Tan`:** tangent angle $\theta \in [0^\circ, 360^\circ)$ in degrees, handy for `\frz`.
5. **`[1.5] Norm`:** perpendicular normal angle $(\theta + 90^\circ) \pmod{360^\circ}$.
6. **`[1.6] Spline`:** ASSdraw path of the whole curve (e.g. `m X0 Y0 b X1 Y1 X2 Y2 X3 Y3`).
7. **`[1.7] Spline L`:** [Subdivide mode] ASSdraw path of the left segment $[0.0, t]$.
8. **`[1.8] Spline R`:** [Subdivide mode] ASSdraw path of the right segment $[t, 1.0]$.

### Maths

```
P1 (50, 100)                     P2 (150, 100)
    ●───────────────────────────────●
   /                                 \
  /           B(t) (X, Y)             \
 /                 ● ───> Tangent      \
●                  │                    ●
P0 (0, 0)          ▼ Normal             P3 (200, 0)
```

**De Casteljau's algorithm (degree $N$).** Given $n+1$ control points $\{P_0, P_1, \dots, P_n\}$ with $P_i \in \mathbb{R}^2$:
$$P_i^{(0)} = P_i \quad \forall i \in \{0, \dots, n\}$$
$$P_i^{(r)} = (1 - t) P_i^{(r-1)} + t P_{i+1}^{(r-1)} \quad \forall r \in \{1, \dots, n\}, \, i \in \{0, \dots, n-r\}$$
The point on the curve is $B(t) = P_0^{(n)}$.

For a cubic curve ($n=3$):
$$B(t) = (1-t)^3 P_0 + 3(1-t)^2 t P_1 + 3(1-t) t^2 P_2 + t^3 P_3$$

**Derivative, tangent and normal.** The first derivative $B'(t) = (dx/dt, dy/dt)$ of a degree-$n$ curve is a Bézier curve of degree $n-1$:
$$B'(t) = n \sum_{i=0}^{n-1} (P_{i+1} - P_i) \cdot b_{i, n-1}(t)$$
From the velocity vector $(dx, dy)$:
$$\theta_{\text{tan}} = \left( \operatorname{atan2}(dy, dx) \cdot \frac{180}{\pi} + 360^\circ \right) \pmod{360^\circ}$$
$$\theta_{\text{norm}} = (\theta_{\text{tan}} + 90^\circ) \pmod{360^\circ}$$

**Arc-length correction (Constant Speed).** The arc length $s(t)$ is integrated with the composite Simpson rule:
$$s(t) = \int_0^t \sqrt{\left(\frac{dx}{du}\right)^2 + \left(\frac{dy}{du}\right)^2} \, du$$
To evaluate at the target distance $s_{\text{target}} = t \cdot s(1.0)$, the equation $s(t^*) = s_{\text{target}}$ is solved by bisection until convergence ($\epsilon < 10^{-5}$).

**Subdivision.** At parameter $t$, the intermediate points of the De Casteljau pyramid are the new control polygons:
* **Left segment ($[0, t]$):** $\{P_0^{(0)}, P_0^{(1)}, P_0^{(2)}, \dots, P_0^{(n)}\}$.
* **Right segment ($[t, 1]$):** $\{P_0^{(n)}, P_1^{(n-1)}, P_2^{(n-2)}, \dots, P_n^{(0)}\}$.

### Usage
* **Auto-oriented particles:** send `\pos` to the position and `Tan` to `\frz` so moving elements rotate to follow the path.
* **Animated stroke drawing with `Shape/Walker`:** connect `Spline` to `Path` on `Shape/Walker` to draw the curve progressively.

### Example: point and heading on a cubic spline
Four control points $P_0(100, 300), P_1(200, 100), P_2(400, 100), P_3(500, 300)$ evaluated at $t=0.5$:

```
[Functions/Bezier Curve: mode=cubic_2d, t=0.5] ──► \pos ──────┐
   p0: "100,300", p1: "200,100", p2: "400,100", p3: "500,300" │
                                         └──► Tan ───┐        ▼
                                                     └──► Tags In ──► [System/Output]
                                                                      Return: "m 0 0 l 20 0 l 20 20 l 0 20"
```

* **Point at $t=0.5$:**
  $$B(0.5) = (1-0.5)^3 P_0 + 3(1-0.5)^2(0.5) P_1 + 3(1-0.5)(0.5)^2 P_2 + 0.5^3 P_3$$
  $$B(0.5) = 0.125(100, 300) + 0.375(200, 100) + 0.375(400, 100) + 0.125(500, 300) = (300.0, 150.0)$$
* **Tangent at the apex:**
  $$B'(0.5) = 3(0.25)(P_1 - P_0) + 6(0.25)(P_2 - P_1) + 3(0.25)(P_3 - P_2) = (450.0, 0.0) \implies \theta = 0^\circ$$
* **Resulting ASS line:**
  `Dialogue: 0,0:00:01.00,0:00:03.00,Default,,0,0,0,,{\an5\pos(300,150)\frz0\p1}m 0 0 l 20 0 l 20 20 l 0 20{\p0}`

---

## 10. Node `Functions/Move Tag` (Kinematic ASS Motion Sequences)

Generates ASS motion override blocks (`\pos`, `\fscx`, `\fscy`, `\t`) from vector paths, Cartesian waypoints or random jitter. It resamples the trajectory at a uniform step (`step_px`), applies a non-linear acceleration curve and recentres the coordinates.

![Functions/Move Tag](img/move_tag.jpg)

### Modes
1. **`Trajectory` (`SMOVE`):** takes an ASSdraw path (`Shape`), computes its total length and divides it into segments of at most `step_px`, for smooth continuous motion.
2. **`Waypoints` (`PMOVE`):** takes discrete points (`Points` or `Shape`) and generates linear or interpolated transitions between them.
3. **`Jitter` (`RMOVE`):** generates pseudo-random jitter within $(\pm \Delta X, \pm \Delta Y)$ at regular intervals (`dur` ms), reproducible with a seed.

### Inputs
1. **`Tags` (`tags`):** extra ASS tags added to the final block (e.g. `\1c&HFFFFFF&\blur2`).
2. **`Shape (d)` (`shape`):** ASSdraw path defining the route (e.g. `"m 0 0 b 50 100 150 100 200 0"`).
3. **`Step (px)` (`step_px`):** maximum distance in pixels between consecutive samples. Smaller values are smoother but produce more `\t` tags. (Default: `7.5`).
4. **`Anchor` (`anchor`):** centring mode:
   * `"center"`: centres the trajectory on the midpoint of its bounding box $(B_{\text{centre}} = (0, 0))$.
   * `"origin"` / `"first_point"`: fixes the start of the path at $(0, 0)$.
5. **`Start Time (t1)` (`t1`):** motion start in ms. (Default: `0`).
6. **`End Time (t2)` (`t2`):** motion end in ms. (Default: `"fx.dur"`).
7. **`Acceleration` (`accel`):** acceleration exponent ($1.0 = \text{linear}$; $> 1.0 = \text{ease-in}$; $< 1.0 = \text{ease-out}$). (Default: `1.0`).

### Outputs
1. **`[1.1] Data`:** the finished ASS tag string:
   $$\backslash\text{an7}\backslash\text{q2}\backslash\text{pos}(X_0, Y_0)\backslash\text{fscx}P_{x0}\backslash\text{fscy}P_{y0}\backslash\text{t}(t_{s1}, t_{e1}, \backslash\text{fscx}P_{x1}\backslash\text{fscy}P_{y1})\dots\backslash\text{p1}\}m\dots\{\backslash\text{p0}$$

### How it works

```
Vector Route:     P0 (0,0) ─────── P1 (7.5px) ─────── P2 (15px) ─────── P3 (22.5px)
Mapped Time:      t1               st1 ─── et1        st2 ─── et2       t2
Normal Progress:  0.0              (d1/D)^accel       (d2/D)^accel      1.0
```

Given $M$ sampled points $\{P_0, P_1, \dots, P_{M-1}\}$ with cumulative distances $d_k$ and total distance $D = d_{M-1}$:
1. For each segment $k \in [1, M-1]$:
   $$\tau_1 = \left(\frac{d_{k-1}}{D}\right)^{\text{accel}}, \quad \tau_2 = \left(\frac{d_k}{D}\right)^{\text{accel}}$$
   $$s_t = \text{round}(t_1 + (t_2 - t_1) \cdot \tau_1)$$
   $$e_t = \text{round}(t_1 + (t_2 - t_1) \cdot \tau_2)$$
2. Write the transition:
   $$\backslash\text{t}(s_t, e_t, \backslash\text{fscx}P_{x,k}\backslash\text{fscy}P_{y,k})$$

### Usage
* **Path following:** send `Spline` from `Bezier Curve` into `Shape (d)` to move glyphs along a Bézier spline with acceleration control.

### Example: quadratic easing along a 3-point route
A route over $300\text{ ms}$ with quadratic easing ($\text{accel}=2.0$) from $(100, 200)$ to $(250, 250)$, sampled every $50\text{ px}$:

```
[Functions/Move Tag: mode=trajectory, step_px=50, accel=2.0, t1=0, t2=300]
   shape: "m 100 200 l 170 200 l 250 250" ──► Data ──► Tags In ──► [System/Output]
                                                                   Return: "Text"
```

* **Sampling ($\Delta t = 300\text{ ms}$, $D = 164.34\text{ px}$):**
  * Segment 0 ($d_0 = 0.0$): $\tau_0 = 0.0 \to t = 0\text{ ms}$, coordinates $(100.0, 200.0)$.
  * Segment 1 ($d_1 = 70.0$): $\tau_1 = (70.0 / 164.34)^2 \approx 0.181 \to s_{t1} = 54\text{ ms}$, coordinates $(170.0, 200.0)$.
  * Segment 2 ($d_2 = 164.34$): $\tau_2 = 1.0 \to s_{t2} = 300\text{ ms}$, coordinates $(250.0, 250.0)$.
* **Emitted tag block:**
  `{\an7\q2\pos(100.00,200.00)\fscx100.00\fscy100.00\t(0,54,2.00,\fscx170.00\fscy200.00)\t(54,300,2.00,\fscx250.00\fscy250.00)\p1}m 0 0 m 100 100 {\p0}Text`

---

## 11. Node `Functions/Move Text` (Coordinated Inline Typographic Motion)

Moves text without breaking the paragraph layout or changing the font metrics. It compensates on two axes: font spacing (`\fsp`) for X and vertical scale (`\fscy`) for Y, with the text enclosed between invisible anchors.

![Functions/Move Text](img/move_text.jpg)

### Inputs
1. **`Text` (`text`):** text string or ASSdraw shape. If empty, it takes the text of the active syllable or character.
2. **`Delta X` (`dx`):** total displacement along X (px).
3. **`Delta Y` (`dy`):** total displacement along Y (px).
4. **`Offset X` (`ox`):** fixed initial offset along X (px).
5. **`Offset Y` (`oy`):** fixed initial offset along Y (px).
6. **`Shape (d)` (`shape` / `trajectory`):** optional ASSdraw path that replaces $\Delta X, \Delta Y$ for curved trajectories.
7. **`Points` (`points`):** list of control points for waypoint routing.
8. **`Step (px)` (`step_px`):** resampling step for vector paths. (Default: `7.5`).
9. **`Start Time (t1)` (`t1`):** motion start (ms). (Default: `0`).
10. **`End Time (t2)` (`t2`):** motion end (ms). (Default: `"fx.dur"`).
11. **`Acceleration` (`accel`):** acceleration exponent. (Default: `1.0`).

### Outputs
1. **`[1.1] Text`:** the ASS text structure with horizontal and vertical compensation blocks:
   $$\text{Block}_{V1} \cdot \text{Block}_{H1} \cdot \{\backslash\text{r}\text{tags}\backslash\text{q2}\}\text{Text} \cdot \text{Block}_{H2} \cdot \text{Block}_{V2}$$

### How it works

```
Generated Structure:
[ Compensating Linebreak \N Y1 ]
[ Hidden Dot '.' with \fspX1 ] ─── [ PRIMARY TEXT ] ─── [ Hidden Dot '.' with \fspX2 ]
[ Compensating Linebreak \N Y2 ]
```

The text moves without affecting neighbouring characters and without using screen-space `\pos`:
1. **Horizontal axis ($X$):** two transparent dots `.` (`\alpha&HFF&`) are placed on either side of the text. Animating `\fsp` with doubled offsets $2 \cdot \Delta X$ shifts the text left or right and keeps the line width.
2. **Vertical axis ($Y$):** forced line breaks `\N` with micro-drawings scaled by `\fscy` shift the active line up or down without breaking the global baseline.

### Usage
* **Drop-in entrance:** `Delta Y = -30` and `Accel = 2.0` in the `presyl` phase make each syllable float down onto the baseline as it is sung.

### Example: syllable drop-in
A $25\text{ px}$ vertical drop over the first $250\text{ ms}$ of the syllable:

```
[Variables/Sys Var: var_name=syl.text] ──► Text ─────────────────┐
                                                                 ▼
[Functions/Move Text: dy=-25, t1=0, t2=250, accel=1.5] ──► Text ──► Return ──► [System/Output]
```

The node measures the width of the anchor glyph `.` ($w_{\text{dot}} = 7.5\text{ px}$), places the syllable text between two invisible characters with `\alpha&HFF&`, and compensates the vertical axis with a scaled `\fscy` block after a forced line break `\N`.

Generated line:
`Dialogue: 0,0:00:01.00,0:00:03.00,Default,,0,0,0,,{\p0\alpha&HFF&.}{\fscy100\t(0,250,1.5,\fscy0)\p1}m 0 0 l 1 0 l 1 25 l 0 25{\p0}\N{\r\q2}Ka{\p0\alpha&HFF&.}`

---

## 12. Node `Functions/Polar to Cartesian` (Polar to Cartesian Converter)

Converts a radius $r$ and angle $\theta$ into Cartesian coordinates $(X, Y)$ relative to an origin $(X_0, Y_0)$. It outputs a `\pos(X, Y)` tag and the numeric components.

![Functions/Polar to Cartesian](img/polar_to_certesian.jpg)

### Inputs
1. **`Origin X` (`x`):** origin coordinate $X_0$. Accepts constants or context expressions like `syl.x`, `line.x`, `char.x`. (Default: `"0"`).
2. **`Origin Y` (`y`):** origin coordinate $Y_0$ (e.g. `syl.y`, `line.y`). (Default: `"0"`).
3. **`Angle (°)` (`angle`):** angle $\theta$ in degrees ($0^\circ \dots 360^\circ$). $0^\circ$ points along $+X$ (right); $90^\circ$ points along $+Y$ (down in the ASS coordinate system). (Default: `"0"`).
4. **`Radius` (`radius`):** radius $r$ in pixels. (Default: `"100"`).

### Outputs
1. **`[1.1] \pos Tag`:** the `\pos(X, Y)` tag.
2. **`[1.2] X`:** absolute coordinate $X = X_0 + \Delta X$.
3. **`[1.3] Y`:** absolute coordinate $Y = Y_0 + \Delta Y$.
4. **`[1.4] dX`:** relative horizontal displacement $\Delta X = r \cos(\theta)$.
5. **`[1.5] dY`:** relative vertical displacement $\Delta Y = r \sin(\theta)$.

### Maths

```
               (X0, Y0)
                  ● ─────────────> X Axis (θ = 0°)
                  │ \
                  │  \  Radius (r)
                  │   \
                  │ θ  \
                  ▼     ● (X, Y)
                Y Axis
```

The angle in degrees $\theta$ is converted to radians:
$$\theta_{\text{rad}} = \theta \cdot \frac{\pi}{180}$$

Offsets and absolute coordinates:
$$\Delta X = r \cdot \cos(\theta_{\text{rad}})$$
$$\Delta Y = r \cdot \sin(\theta_{\text{rad}})$$
$$X = X_0 + \Delta X$$
$$Y = Y_0 + \Delta Y$$

Values are written as integers when the fractional part is zero, otherwise rounded to 2 decimals to keep the ASS file small.

### Usage
* **Radial bursts:** connect an iterator such as `Basics/MultiRandom`, or the expression `j * (360 / maxloop)`, to `Angle (°)`, set `Radius: 80`, and route `\pos Tag` to `System/Output` to get a ring of particles.
* **Inward spirals:** drive `Angle (°)` with `Time/Ipol` while decreasing `Radius` over time.

### Example: ring of 8 particles around a syllable
8 elements spaced $45^\circ$ apart at a radius of $60\text{ px}$ from the syllable centre:

```
[Loops/MaxLoop: total=8] ──► j ──► Angle: (j - 1) * 45 ────────┐
                                                               ▼
[Shape/Library: "Star"] ──► Shape ──► Shape / Text ──► [Functions/Polar to Cartesian: radius=60]
                                                          Origin X: syl.x, Origin Y: syl.y
                                                               │
                                                               ▼ \pos Tag (\pos(X, Y))
                                                            Tags In ──► [System/Output]
```

Assuming `syl.x = 320, syl.y = 240`:
* **$j=1$ ($\theta = 0^\circ$):** $\Delta X = 60, \Delta Y = 0 \to$ `{\an5\pos(380, 240)\p1}m 0 0 ...` (right).
* **$j=3$ ($\theta = 90^\circ$):** $\Delta X = 0, \Delta Y = 60 \to$ `{\an5\pos(320, 300)\p1}m 0 0 ...` (bottom).
* **$j=5$ ($\theta = 180^\circ$):** $\Delta X = -60, \Delta Y = 0 \to$ `{\an5\pos(260, 240)\p1}m 0 0 ...` (left).
* **$j=7$ ($\theta = 270^\circ$):** $\Delta X = 0, \Delta Y = -60 \to$ `{\an5\pos(320, 180)\p1}m 0 0 ...` (top).

---

## 13. Node `Functions/Particles` (Vector Particle Swarms)

Samples the contours or interior of text glyphs or ASSdraw shapes to produce a swarm of particles. Each sampled point can be replaced with a custom vector particle, ordered with Numpad notation and jittered randomly.

![Functions/Particles](img/particles.jpg)

### Modes
1. **`Outline` (`outline_v2` / `border`):** samples equidistant points along the outline.
2. **`Inner Fill` (`inner_fill`):** generates a regular grid of points inside the shape, testing inclusion with ray-casting parity.

### Inputs
1. **`Path / Origin` (`shape`):** base ASSdraw path (`m ...`) or primitive name. If empty or plain text, the glyph outlines are taken from the active context (`syl` or `char`).
2. **`Particle` (`particle_shape`):** vector shape for each particle (e.g. `"Circle"`, `"Star"`, `"Heart"`, or raw ASSdraw). If empty, a $2 \times 2\text{ px}$ square (`m 0 0 l 2 0 l 2 2 l 0 2`).
3. **`Density` (`density`):** sampling stride in pixels. In `Outline` mode it is the spacing along the contour; in `Inner Fill` it is the grid cell step. (Default: `5.0`).
4. **`RedrawDist` (`redraw_dist`):** range of uniform random jitter $(\pm \Delta x, \pm \Delta y)$ in pixels applied to each particle. (Default: `0.0`).
5. **`Seed` (`seed`):** seed for the jitter. (Default: `1`).
6. **`Scale` (`scale`):** multiplier for the swarm coordinates. (Default: `1.0`).
7. **`Anchor` (`anchor`):** cycling button, the same *Piece Anchor* profile used by the tessellation nodes (`Slicer`, `Array`, `Union & Divide`). It controls how local particle coordinates and the rotation origin `\org` are projected onto the canvas:
   * **`pieces` (default):** each particle is placed at its own screen coordinates `\pos(x, y)` relative to the glyph or path centroid, with `\org(x, y)` set at its own centre. Later transformations (`\frz` spins, `\fscx/\fscy` scaling, shearing) then rotate each particle around its own pivot.
   * **`relative`:** keeps coordinates relative to the centroid of the parent text or shape, without setting `pos_overridden`.
   * **`parent_org`:** places the particle at its absolute screen coordinates `\pos(x, y)` but pins `\org` to the origin of the parent text or line (`parent_x, parent_y`), for orbital rotations around the source glyph.
   * **`pos`:** places the particle at its absolute screen coordinates `\pos(x, y)` without an explicit `\org` (`has_org = False`).
   * **`absolute`:** writes the screen coordinates into the path vertices (`m x y ...`), pins `\pos` to the parent origin and clears `pos_overridden`.
8. **`Order` (`order`):** cycling button for 2D ordering (*Numpad Order*), which sets the index `p_i`:
   * `"79"`: Top-Left to Bottom-Right (*TL $\to$ BR*).
   * `"97"`: Top-Right to Bottom-Left (*TR $\to$ BL*).
   * `"13"`: Bottom-Left to Top-Right (*BL $\to$ TR*).
   * `"31"`: Bottom-Right to Top-Left (*BR $\to$ TL*).
   * `"71"`: left column, top to bottom.
   * `"17"`: left column, bottom to top.
   * `"93"`: right column, top to bottom.
   * `"39"`: right column, bottom to top.
   * `"5"`: from the centre outwards (*Inside-Out*).
   * `"-5"`: from the edge inwards (*Outside-In*).
   * `"cw"`: clockwise.
   * `"ccw"`: counter-clockwise.
   * `"rand"`: pseudo-random shuffle.
   * `"path"`: **along the contour.** Keeps the arc-length order ($s \in [0, L]$) along the linear and Bézier boundary segments. It works like an embedded *Walker*, so later tag cascades, reveals or transformations follow the actual calligraphic stroke.
   * `"path_inv"`: **contour in reverse** ($s \in [L, 0]$).

### Outputs
1. **`[1.1] Shp Out`:** position tag and particle drawing together: `{\pos(X, Y)}particle_shape`.
2. **`[1.2] \pos Tag`:** the `\pos(X, Y)` tag.
3. **`[1.3] X Arr`:** horizontal coordinate $X$ of the active particle (px).
4. **`[1.4] Y Arr`:** vertical coordinate $Y$ of the active particle (px).
5. **`[1.5] Total`:** particle count $N$.

Context variables injected:
* `p_i` / `tp_i`: index of the active particle ($1 \dots N$).
* `p_n` / `tp_n` / `maxloop`: total particle count ($N$).
* `x, y` / `fx_pos_x, fx_pos_y`: absolute coordinates of the active particle.

### How it works

```
Outline Mode (Perimeter):             Inner Fill Mode (Ray-Casting):
      ● ─── ● ─── ●                        ●   ●   ●   ●   ● (Outside)
     /             \                     ┌───────────────────┐
    ●               ●                    │   ●   ●   ●   ●   │ (Inside: Crossings = 1)
     \             /                     │   ●   ●   ●   ●   │
      ● ─── ● ─── ●                      └───────────────────┘
```

**Outline (arc-length sampling).** For each closed contour $C = \{V_0, V_1, \dots, V_m, V_0\}$:
1. Compute the segment lengths:
   $$d_k = \|V_{k+1} - V_k\|, \quad D_{\text{total}} = \sum_{k=0}^m d_k$$
2. Generate equidistant targets $s_j = j \cdot \text{density}$ for $j \in \left[0, \lfloor D_{\text{total}} / \text{density} \rfloor \right]$.
3. Interpolate each target on its segment and add random jitter if $\text{RedrawDist} > 0$:
   $$P_j = P_{\text{interp}} + \begin{pmatrix} U(-\text{redraw\_dist}, \text{redraw\_dist}) \\ U(-\text{redraw\_dist}, \text{redraw\_dist}) \end{pmatrix} \cdot \text{scale}$$

**Inner Fill (ray-casting).**
1. Take the bounding box $(X_{\min}, Y_{\min}) \to (X_{\max}, Y_{\max})$ of all contours.
2. Build a regular grid with cell size $\Delta = \text{density}$.
3. For each grid node $(g_x, g_y)$, cast a ray towards $+X$ and count the polygon edges it crosses:
   $$\text{inside} = \left(\sum \text{intersections}(g_x, g_y, \text{Edges})\right) \pmod 2 \equiv 1$$
   Points with odd parity are added to the swarm.

### Usage
* **Particle dissolve:** connect `Functions/Particles` to a `Loops/MaxLoop` that iterates $N$ times (`p_n`), and animate the dispersal with `Time/Ipol` or `Functions/Polar to Cartesian`.
* **Calligraphic write-on (embedded Walker):** with `order="path"`, particles are not sorted into Cartesian or radial bins. They are indexed along the contour ($s = 0 \to L$). Modulate opacity or scale through `Tags` (e.g. `\alpha!by.p_i.ipol(0, 255, 0, fx.dur)!` or `\t((p_i/p_n)*syl.dur, ((p_i+1)/p_n)*syl.dur, \alpha&H00&)`) and the particles light up one after another along the glyph outline, without a separate `Shape/Walker` node.

### Example: particle burst from a glyph outline
A glyph contour sampled every $8\text{ px}$, each point replaced with a micro-star, ordered from the centre outwards (order `"5"`):

```
[Shape/Library: "Star"] ──► Particle ────────────────────────────┐
                                                                 ▼
[Functions/Particles: mode=outline_v2, density=8.0, order="5"] ──► Shp Out ──► Return ──► [System/Output]
   Path / Origin: syl.shape
```

The engine finds `Particles` along the `Output.Return` dataflow, extracts $N=24$ perimeter points from the glyph, injects the loop variables `p_i` ($1 \dots 24$) and `p_n` ($24$), and sorts the points radially by distance from the character centroid.

Line for the first particle ($p_i=1$, closest to the centroid):
`Dialogue: 0,0:00:01.00,0:00:03.00,Default,,0,0,0,,{\an5\pos(320.50,238.20)\p1}m 0 0 l 2 0 l 2 2 l 0 2{\p0}`

---

## 14. Node `Functions/Interpolator` (Polymorphic Parametric Interpolator)

Interpolates between two or more values ($V_1 \to V_2$) and adapts to the data type: numbers, colours (hex/ASS), alpha, ASS tag blocks, or whole vector shapes (*vector morphing* with resampling).

![Functions/Interpolator](img/interpolador.jpg)

### Inputs
1. **`Iterator` (`iterator`):** current iteration index or progress value. Accepts:
   * Context iterator names (e.g. `"i"`, `"j"`, `"char.i"`, `"syl.i"`, `"a_i"`).
   * A normalised progress value $t \in [0.0, 1.0]$.
2. **`Total` (`total`):** number of steps used to normalise the iterator ($N$). Accepts `"N"`, `"maxloop"`, `"char.n"`, `"syl.n"`. (Default: `"N"`).
3. **`Accel` (`accel`):** acceleration / easing exponent ($1.0 = \text{linear}$; $> 1.0 = \text{ease-in}$; $< 1.0 = \text{ease-out}$). (Default: `"1.0"`).
4. **`V1` (`v1`):** value at $t=0.0$. Accepts numbers, colours (`#FF0000`, `&H0000FF&`), tags (`\blur0\fscx100`) or ASSdraw paths (`m 0 0 l 50 0...`).
5. **`V2` (`v2`):** value at $t=1.0$. Also accepts comma-separated multi-stop strings or JSON arrays for multi-stage keyframes ($V_1 \to V_2 \to V_3 \dots$).

### Outputs
1. **`[1.1] Data`:** the interpolated value for the current progress $t$.
2. **`[1.2] Batch / List`:** comma-separated list of all $N$ interpolated values, for batch assignments.

### How it works

```
Normalised Progress:   t = (Iterator - 1) / (Total - 1)   ───>   t_eased = t^Accel
                                                                     │
              ┌───────────────────┬───────────────────┬──────────────┴──────────────┐
              ▼                   ▼                   ▼                             ▼
       [ Scalars ]          [ Colours ]         [ ASS Tags ]              [ ASSdraw Morphing ]
      V1 + (V2-V1)·t       RGB Interpolated   Keyframe Blending         Equidistant Resampling
```

**Normalisation and easing.** With iterator $i$ and total $N$:
$$t = \begin{cases} i & \text{if } 0.0 \le i \le 1.0 \text{ and } N=1 \\ \frac{i - 1}{N - 1} & \text{if } N > 1 \\ 0.0 & \text{otherwise} \end{cases}$$
$$t_{\text{eased}} = \begin{cases} t^{\text{accel}} & \text{if } \text{accel} > 1.0 \\ 1.0 - (1.0 - t)^{1.0 / \text{accel}} & \text{if } 0.0 < \text{accel} < 1.0 \\ t & \text{if } \text{accel} = 1.0 \end{cases}$$

**By data type:**
1. **ASSdraw shapes (morphing):**
   * Contours are extracted from both shapes with Clipper2.
   * Both are resampled to the same vertex count $M = \max(|C_1|, |C_2|, 30)$, evenly spaced by arc length.
   * Vertex pairs are interpolated linearly:
     $$P_k(t) = (1 - t_{\text{eased}}) \cdot P_{1,k} + t_{\text{eased}} \cdot P_{2,k}$$
   * The ASSdraw path is rebuilt.
2. **Hex / ASS colours:** the channels $(R_1, G_1, B_1)$ and $(R_2, G_2, B_2)$ are interpolated linearly in RGB.
3. **ASS tag blocks (keyframing):** numeric tags (`\fscx`, `\fscy`, `\frz`, `\alpha`, `\blur`, etc.) are parsed and interpolated numerically.
4. **Numbers:** $V(t) = V_1 + (V_2 - V_1) \cdot t_{\text{eased}}$, written as integers where possible.

### Usage
* **Vector morphing:** connect the `"Circle"` primitive to `V1` and `"Star"` to `V2`, and send `Data` to `System/Output` inside a `Loops/MaxLoop`.

### Example: circle to star in 10 steps
Two primitives resampled with Clipper2 and interpolated with `accel=1.5`:

```
[Loops/MaxLoop: total=10] ──► j ──► Iterator ──────────────────┐
                                                               ▼
[Functions/Interpolator: total=10, accel=1.5] ──► Data ──► Shape / Text ──► [System/Output]
   v1: "m 50 0 b 22 0...", v2: "m 50 0 l 61 35..."
```

* **$j=1$ ($t=0.0$):** `{\an5\pos(320, 240)\p1}m 50 0 l 44.8 0.5 ...` (the circle resampled to 30 nodes).
* **$j=6$ ($t \approx 0.556, t_{\text{eased}} \approx 0.415$):** an intermediate shape with bulging edges.
* **$j=10$ ($t=1.0$):** `{\an5\pos(320, 240)\p1}m 50 0 l 61 35 l 98 35 ...` (the full star).

Because vertices correspond 1:1, the path doesn't collapse or self-intersect during the morph.

---

## 15. Node `Functions/Text on Path` (Text Flow Along Curved Paths)

Places and spaces text or single glyphs along an ASSdraw path or curve. At each point it computes the coordinates and the tangent rotation (`\frz`) so the text follows the curvature.

![Functions/Text on Path](img/text_on_path.jpg)

### Modes
1. **`Center`:** centres the whole text on the midpoint of the path length.
2. **`Left`:** starts the text at the path origin ($d=0$) plus `Offset`.
3. **`Right`:** ends the text at the end of the path ($d=L_{\text{total}}$), minus the text width.
4. **`Justified`:** spreads characters or syllables evenly over the whole path ($0.0 \to L_{\text{total}}$).
5. **`Animated`:** maps `Offset` to the normalised range $0.0 \to 1.0$ so the text flows along the curve.

### Inputs
1. **`Path / Shape` (`shape`):** ASSdraw path used as the guide.
2. **`Offset` (`offset`):** displacement along the path in pixels (or progress $0.0 \to 1.0$ in `Animated` mode). (Default: `"0"`).
3. **`Extra Angle` (`extra_angle`):** angle in degrees added to the computed tangent angle. (Default: `"0"`).
4. **`Subdivs` (`subdivs`):** number of subdivisions for the internal Bézier sampling. (Default: `"30"`).

### Outputs
1. **`[1.1] Tag Out`:** position and rotation tags together: `\pos(X, Y)\frz(Angle)`.
2. **`[1.2] \pos Tag`:** `\pos(X, Y)` alone.
3. **`[1.3] Angle (\frz)`:** `\frz(Angle)` alone.
4. **`[1.4] X`:** horizontal coordinate $X$ on the path (px).
5. **`[1.5] Y`:** vertical coordinate $Y$ on the path (px).
6. **`[1.6] Length`:** total arc length $L_{\text{total}}$ of the path in pixels.

### How it works

```
                 P_tangent (X, Y)
                        ● ───> Tangent Vector (dx, dy)
                       / \
                      /   \ θ = atan2(dx, dy) - 90°
                     /     \
Guide Route: P_start ●       ● P_end (L_total)
```

1. **Character position along the line.** With total text width $L_{\text{line}}$ and the character's relative position $d_{\text{char}} = X_{\text{char}} - X_{\text{start}}$:
   $$d_{\text{target}} = \text{lineoffset} + d_{\text{char}}$$
2. **Path lookup.** The node finds the segment $S_k$ containing $d_{\text{target}}$, clamped to $[0, L_{\text{total}}]$, and gets the point $(X, Y)$ and the velocity vector $(dx, dy)$.
3. **Heading.**
   $$\theta_{\text{base}} = \left( \operatorname{atan2}(dx, dy) \cdot \frac{180}{\pi} - 90^\circ \right) + \text{extra\_angle}$$
   Angles are wrapped into $(-180^\circ, 180^\circ]$ to avoid sudden 360-degree flips in libass.

### Usage
* **Text on a moving spline:** send `Spline` from `Functions/Bezier Curve` into `Path / Shape`, and link `Offset` to a time oscillator to get a sinusoidal wave of text.

### Example: justified text on an arc
The characters of a word placed along the path `m 100 250 b 200 150 300 150 400 250` in `justified` mode:

```
[Shape/Library: "Arc"] ──► Path / Shape ────────────────────────┐
                                                                ▼
[Functions/Text on Path: mode=justified, subdivs=30] ──► Tag Out ──► Tags In ──► [System/Output]
                                                                                  Return: char.text
```

For a 3-character word with iterator `char.i` ($1, 2, 3$):
* Character 1 ($d=0\text{ px}$, start of the arc): $P_1(100.0, 250.0)$, ascending tangent $\theta = 45^\circ \to$ `{\pos(100,250)\frz45}K`.
* Character 2 ($d=L/2$, top of the arc): $P_2(250.0, 175.0)$, horizontal tangent $\theta = 0^\circ \to$ `{\pos(250,175)\frz0}a`.
* Character 3 ($d=L$, end of the arc): $P_3(400.0, 250.0)$, descending tangent $\theta = -45^\circ \to$ `{\pos(400,250)\frz-45}r`.

---

## 16. Node `Functions/Text to Shape` (Typographic Glyph Vectorisation)

Converts TrueType/OpenType glyphs into ASSdraw vector paths (`m ... b ... l ...`). Syllable text, line text or constant strings become vector geometry for boolean operations, slicers (*Slicer*), border extrusion or particle sampling.

![Functions/Text to Shape](img/text_to_shape.jpg)

### Inputs
1. **`Text` (`text`):** the text to vectorise. If empty, it takes the stripped text of the active syllable or line (`syl.text_stripped` or `line.text_stripped`).
2. **`Font` (`font_name`):** font family name (e.g. `"Arial"`, `"Montserrat"`, `"Impact"`). If empty, it uses the font of the active ASS style.
3. **`Size` (`font_size`):** font size in points. If empty, it uses the size of the active ASS style.
4. **`Scale` (`scale`):** scale multiplier applied to the generated coordinates. (Default: `"1.0"`).
5. **`Bold` (`bold`):** [Property] bold toggle (`true` / `false`).
6. **`Italic` (`italic`):** [Property] italic toggle (`true` / `false`).

### Outputs
1. **`[1.1] Shape Out`:** closed, centred ASSdraw path with `m`, `l` and cubic Bézier `b` commands.
2. **`[1.2] Width`:** bounding box width in pixels ($W$).
3. **`[1.3] Height`:** bounding box height in pixels ($H$).

### How it works

```
TrueType/OpenType Font ───> FontVectorEngine (Win32 GDI 64x Subpixel) ───> FontVectorMetrics (Lossless)
                                                                               │
               ┌───────────────────────────────────────────────────────────────┴───────────────────────────────────────────────────────────────┐
               ▼                                                                                                                               ▼
  [ ASSdraw Path `m...b...l...` ]                                                                                     [ Integral Metric Record (O(1)) ]
     For Slicer, Array, Morphs                                                                                    advance_width, cell_height, ascent, descent,
                                                                                                                  lsb, rsb, ink_bbox, delta_x, delta_y
```

1. **Vector extraction at 64x subpixel resolution.** `FontVectorEngine` reads the glyph contours through the Win32 GDI API at native 64x subpixel resolution (`ExtTextOutW` inside a path bracket with `BeginPath`) and converts the quadratic and cubic font splines into normalised ASSdraw cubic Béziers (`b cp1x cp1y cp2x cp2y endx endy`).
2. **Metrics (`FontVectorMetrics`).** Unlike ordinary rasterisers, `FontVectorEngine` keeps the cell metrics:
   * **Side bearings:** Left Side Bearing ($\text{LSB}$) and Right Side Bearing ($\text{RSB}$), related by:
     $$\text{Advance Width} = \text{LSB} + \text{Ink Width} + \text{RSB}$$
   * **Offset ($\Delta X, \Delta Y$):** the displacement between the pen advance centre and the visual ink centroid:
     $$\Delta X = \frac{\text{LSB} - \text{RSB}}{2}$$
   * **Cell height and baseline:** $\text{ascent}$, $\text{descent}$ and $\text{cell\_height}$, for exact vertical registration.
3. **Anchor modes:**
   * **`typographic` (Default):** origin at the typographic advance centre, giving a 1:1 pixel match with libass `\pos(line.center, line.middle)`.
   * **`ink`:** origin at the centroid of the drawn ink's bounding box, suited to particle generation and slicing.
   * **`baseline` / `origin`:** origin on the typographic baseline.

### Usage
* **Voronoi shatter with `Shape/Slicer`:** chain `Text to Shape` $\to$ `Shape/Slicer (Voronoi)` to break glyphs into polygonal shards for 3D explosion animations.
* **Single-line fusion with `Shape/Union & Divide (FUSION)`:** connect `Text to Shape` to `Union & Divide` in `FUSION` mode to emit a single optimised vector line without overloading libass.

### Example: vectorise and extrude an outline
The active syllable is converted to ASSdraw geometry, then `Shape/Stroke` extrudes a continuous outline:

```
[Variables/Sys Var: var_name=syl.text] ──► Text ─────────────────┐
                                                                 ▼
[Functions/Text to Shape: font_name="Arial", font_size="50"] ──► Shape Out ──► Shape / Text ──► [Shape/Stroke: width=4.0]
                                                                                                  │
                                                                                                  ▼ Shape Out
                                                                                               Return ──► [System/Output]
```

`FontVectorEngine` vectorises the glyphs at 64x subpixel resolution into normalised cubic curves `m ... b ...`, measures $W = 42\text{ px}, H = 48\text{ px}$, and keeps the barycentric offset.

Emitted line:
`Dialogue: 0,0:00:01.00,0:00:03.00,Default,,0,0,0,,{\an5\pos(320,240)\p1}m 0 25 b 0 10 12 0 25 0 b 38 0 50 10 50 25 ...{\p0}`

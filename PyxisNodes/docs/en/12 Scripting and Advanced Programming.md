# Scripting and Advanced Programming (`System/Script Code`)

The **`System/Script Code`** node runs Python or Lua code to process data, compute motion and generate ASS override tags or vector paths. This page covers its ports, the variables injected into the script, the built-in function catalogue and the deterministic `by` dispatcher.

---

## 1. Ports and Properties

```
┌─────────────────────────────────────────────────────────────┐
│ System/Script Code                   [ Language: Python v ] │
├─────────────────────────────────────────────────────────────┤
│ (o) [0] Loop In                             [0] Loop Out (o)│
│ (o) [1] In1                                   [1] Result (o)│
│ (o) [2] In2                                     [2] Out1 (o)│
│ (o) [3] In3                                     [3] Out2 (o)│
├─────────────────────────────────────────────────────────────┤
│ Inputs Count: [ 2                                         ] │
│ Script Editor: [ Ace Code Editor                          ] │
└─────────────────────────────────────────────────────────────┘
```

### 1.1. Input Ports (*Inputs*)
1. **`[0] Loop In` (Control / Context):** Receives the active iteration stream (`line`, `syl`, `word`, `char`, `MaxLoop`, `Slicer`), which gives the script the timing and metrics of the current unit and keeps the chain connected to `System/Output`.
2. **`[1] In1`, `[2] In2`, ..., `[N] InN` (Data):** Dynamic inputs (1 to 16), exposed in the script as the globals `in1`, `in2`, ..., `inN` (or under the name of the upstream wire). An unplugged input takes the value typed into the node's inline text widget.

### 1.2. Output Ports (*Outputs*)
1. **`[0] Loop Out` (Control / Context):** Forwards the iteration context. Any ASS tags or variables the script generates travel through this port to downstream nodes or to `System/Output`.
2. **`[1] Result` (String / Data):** The main script output: the value assigned to `result`, or the value of the last expression.
3. **`[2] Out1` ... `[N] OutN` (Optional):** Created when the script assigns values to the `outputs` dictionary (Python: `outputs['out1'] = ...` or `out1 = ...`; Lua: `outputs.out1 = ...` or `out1 = ...`).

### 1.3. Body Properties (*Properties*)
1. **`language` (`Language`):** `"Python"` or `"Lua"`. Type C (literal selector).
2. **`inputs_count` (`Inputs Count`):** Number of dynamic input slots (1 to 16). Type C (integer).
3. **`script` (`Script Code`):** The source code. Type A (evaluated and AST-validated source code).

---

## 2. Execution and Preprocessing

### 2.1. Result and Automatic Tag Merging
The script's output is taken from one of two places:
1. **Explicit assignment:** `result = ...` (Python or Lua).
2. **Last expression:** If the last line of the script is a bare expression (e.g. `pos(syl.x, syl.y) + fscxy(120)`), the engine assigns its value to `result`.

> [!IMPORTANT]
> **Automatic tag merging:** If the string in `result` contains ASS tag syntax (`\` or `{...}`), Pyxis merges it into `context["loop_tags"]` with `merge_ass_tags`. You don't need to wire a tag combiner node: tags returned from the script end up in the dialogue line produced by `System/Output`.

### 2.2. Mixed Output: Tags plus Shape or Text in `result`

What happens when the script emits tags and printable content together (e.g. `result = f"{{{pos(syl.x, syl.y)}\\p1}}{shape_star()}"` or `result = "{\\c&HFF&}Text"`)? It depends on how the node is wired to `System/Output`.

1. **Script Code is only in the loop stream (`Loop In` $\to$ `Loop Out`), `Result` not wired:**
   * Pyxis detects the `\` or `{` characters and merges the string into `context["loop_tags"]` via `merge_ass_tags`.
   * `merge_ass_tags` takes the blocks inside `{...}` for the tag header but **does not replace the printable body of the line**.
   * The `Return` port of `System/Output` (default: the original syllable text `syl.text_stripped`) still decides the line's text or drawing. A vector shape returned outside braces in `result` does not override the syllable text.

2. **`Result` wired to the `Return` port (port 5) of `System/Output`:**
   * The whole string goes straight into the final rendering step.
   * `System/Output` processes it with **`evaluate_ass_line_tag_blocks()`**, which:
     - detects `\p1` or ASSdraw commands (`m `, `l `, `b `, etc.);
     - validates, cleans and merges the `{...}` tag blocks;
     - leaves the trailing vector drawing or plain text **100% intact**.
   * Resulting ASS dialogue line:
     ```ass
     Dialogue: 0,0:00:01.00,0:00:03.00,Default,,0,0,0,,{\pos(640,360)\p1\1c&HFFFFFF&}m 0 0 l 50 0 l 25 -50
     ```

#### Three Ways to Emit Tags plus Shape/Text
* **Method A (full line in `Result` $\to$ wire to `Return`):**
  ```python
  tags = pos(syl.x, syl.y) + r"\p1" + c1(syl.color1)
  drawing = shape_star()
  result = f"{{{tags}}}{drawing}"
  # Connection: Result -> Return port (5) of System/Output
  ```
* **Method B (split via `outputs`, recommended):**
  ```python
  # Tags dispatched automatically via Loop Out
  result = pos(syl.x, syl.y) + r"\p1" + c1("&H00FFFF&") + fscxy(120)
  # Vector drawing dispatched via sub-output
  outputs['out1'] = shape_circle()
  # Connection: Out1 -> Return port (5) of System/Output
  ```
* **Method C (direct context injection):**
  ```python
  context["return_raw"] = shape_heart()
  result = pos(syl.x, syl.y) + r"\p1" + c1("&H0000FF&")
  ```

### 2.3. Lexical Shorthands
Before compiling, the engine rewrites a few shorthand notations with regular expressions:
* **Timing multipliers:**
  * `2li` $\to$ `2 * li`
  * `-1.5lo` $\to$ `-1.5 * lo`
  * `3m1` $\to$ `3 * m1`
* **Frames and ratios:**
  * `10f` $\to$ `(10 * frame_dur)` (10 video frames in milliseconds at the project FPS).
  * `1.5r` $\to$ `(1.5 * ratio)` (scales spatial magnitudes by the active aspect ratio or module).

---

## 3. Injected Variables

The script receives these read-only values for the unit being processed.

### 3.1. Syllable (`syl`)
The current syllable in the karaoke timing sequence:

| Property | Type | Description |
| :--- | :--- | :--- |
| `syl.text` | `str` | Clean text of the syllable (without karaoke and formatting tags). |
| `syl.text_stripped` | `str` | Syllable text without redundant whitespace or newline characters. |
| `syl.i` | `int` | 1-based index of the syllable within the line ($1 \le i \le n$). |
| `syl.n` | `int` | Total syllable count in the line. |
| `syl.duration` / `syl.dur` | `int` | Syllable duration in milliseconds ($\backslash k$ timing). |
| `syl.start_time` / `syl.st` | `int` | Absolute start time in milliseconds. |
| `syl.end_time` / `syl.et` | `int` | Absolute end time in milliseconds. |
| `syl.mid_time` | `float` | Absolute midpoint ($\frac{st + et}{2}$). |
| `syl.syl_start` | `int` | Start offset in milliseconds from the line start time. |
| `syl.syl_end` | `int` | End offset in milliseconds from the line start time. |
| `syl.x`, `syl.y` | `float` | Screen coordinates $(X, Y)$ computed from the alignment and typographic baseline. |
| `syl.center`, `syl.middle` | `float` | Centre coordinates of the syllable box. |
| `syl.left`, `syl.right` | `float` | Horizontal bounds of the box. |
| `syl.top`, `syl.bottom` | `float` | Vertical bounds of the box. |
| `syl.width`, `syl.height` | `float` | Typographic dimensions from GDI/FreeType raster metrics. |
| `syl.color1` ... `syl.color4` | `str` | Base style ASS colours (`&HBBGGRR&`). |
| `syl.fontsize` | `float` | Nominal font size in points/pixels. |
| `syl.fontname` | `str` | Font family name. |
| `syl.bold`, `syl.italic` | `bool` | Bold and italic flags. |
| `syl.is_first`, `syl.is_last` | `bool` | `True` if the syllable is the first or last in the line. |
| `syl.has_prev`, `syl.has_next` | `bool` | `True` if there is a syllable before or after this one. |

### 3.2. Dialogue Line (`line` / `l`)
The parent dialogue line from Aegisub:
* `line.text`: Full line text without override tags.
* `line.raw_text`: Original string with all ASS override blocks.
* `line.start_time`, `line.end_time`, `line.duration`: Absolute line timing (ms).
* `line.i`, `line.n`: 1-based line index and total selected line count.
* `line.layer`: ASS layer (integer).
* `line.style`: Name of the assigned Aegisub style.
* `line.actor`, `line.effect`: Actor and Effect fields of the line.
* `line.margin_l`, `line.margin_r`, `line.margin_v`: Configured screen margins.
* `line.width`, `line.height`: Typographic dimensions of the rendered line.
* `line.center`, `line.middle`, `line.left`, `line.right`, `line.top`, `line.bottom`: Spatial bounds of the line.

### 3.3. Character (`char`) and Word (`word`)
When the loop iterates over characters or words, `char` and `word` expose the same metric and spatial properties as `syl`:
* Position: `char.x`, `char.y`, `char.center`, `char.middle`, `char.width`, `char.height`.
* Timing: `char.start_time`, `char.end_time`, `char.duration`, `char.char_start`, `char.char_end`.
* Indices: `char.i`, `char.n`, `char.is_first`, `char.is_last`.

### 3.4. Effect Frame (`fx`)
Applies when kinematic nodes or particle emitters move the render position away from the original layout:
* `fx.pos_x`, `fx.pos_y` (or `fx.x`, `fx.y`): Current origin of the emitted unit.
* `fx.org_x`, `fx.org_y`: Pivot for rotation and scaling ($\backslash org$).
* `fx.start_time`, `fx.end_time`, `fx.dur`: Active time window of the resulting dialogue line.
* `fx.i`, `fx.n`: Particle index and total count within the emission cluster.

### 3.5. Ink Bounding Box (`ink`)
The nominal dimensions (`syl.width`, `syl.height`) include whitespace, ascender reserves and tracking margins. `ink` is instead the **actual bounding box of the drawn vector contours**:
* `ink.width`, `ink.height`: Drawn width and height of the glyph outlines.
* `ink.center`, `ink.middle`: Geometric centroid of the rendered glyphs.
* `ink.left`, `ink.right`, `ink.top`, `ink.bottom`: Outer bounds of the vector path.

### 3.6. Neighbouring Units (`prev` and `next`)
Inspect the previous or next unit, e.g. for chain reactions or relative timing offsets:
* `prev.text`, `prev.x`, `prev.y`, `prev.start_time`, `prev.duration`
* `next.text`, `next.x`, `next.y`, `next.start_time`, `next.duration`
* At the boundaries (first or last syllable), `prev` and `next` return proxy objects with neutral defaults (`0`, `""`), so no `NullReferenceException` or `AttributeError` is raised.

### 3.7. Global Iterators and Slicing Variables
* `s_i`, `s_n`: Current piece index and total piece count generated by `Shape/Slicer`.
* `col`, `row`: Column and row indices in 2D cell meshes.
* `j`, `maxloop`: Iteration index and cycle count from `Loops/MaxLoop`.
* `a_i`, `a_n`: Item index and array length in array operations.
* `frame_dur` (alias `fd`): Duration in ms of one video frame ($1000 / FPS$, typically $41.7\,\text{ms}$ at 23.976 fps or $16.6\,\text{ms}$ at 60 fps).
* `fps`: Video frame rate.

---

## 4. Built-in Functions

These helpers reproduce the behaviour of the native Pyxis nodes.

### 4.1. ASS Tag Generators

All tag functions format numbers with up to 3 decimals and drop trailing zeros (e.g. `pos(100.0, 200.5)` $\to$ `\pos(100,200.5)`):

| Function | Generated Tag Output | Description |
| :--- | :--- | :--- |
| `pos(x, y)` | `\pos(x,y)` | Absolute screen position. |
| `move(x1, y1, x2, y2, [t1, t2])` | `\move(...)` | Linear movement between two points. |
| `org(x, y)` | `\org(x,y)` | Pivot for rotation ($\backslash frz, \backslash frx, \backslash fry$) and scaling. |
| `fad(tin, tout)` | `\fad(tin,tout)` | Fade in/out durations in milliseconds. |
| `fade(a1, a2, a3, t1, t2, t3, t4)` | `\fade(...)` | Fade with 3 alpha values and 4 timestamps. |
| `clip(x1, y1, x2, y2)` | `\clip(x1,y1,x2,y2)` | Rectangular clip. |
| `clip(shape_str)` | `\clip(drawing)` | Vector clip. |
| `iclip(...)` | `\iclip(...)` | Inverse clip (rectangular or vector). |
| `c1(col)`, `c2(col)`, `c3(col)`, `c4(col)` | `\1c...`, `\2c...`, etc. | Primary, karaoke, outline and shadow colours (`&HBBGGRR&` or `#RRGGBB`). |
| `a1(val)`, `a2(val)`, `a3(val)`, `a4(val)` | `\1a...`, `\2a...`, etc. | Per-channel opacity (`&HAA&`, 0 to 255). |
| `alpha(val)` | `\alpha&HAA&` | Opacity of the whole element. |
| `fscx(v)`, `fscy(v)` | `\fscx...`, `\fscy...` | Horizontal and vertical scale percentage ($100 = 100\%$). |
| `fscxy(x, [y])` | `\fscx...\fscy...` | Both scale tags at once. |
| `frz(deg)` | `\frz...` | Z-axis rotation in degrees. |
| `frx(deg)`, `fry(deg)` | `\frx...`, `\fry...` | 3D rotation around the X and Y axes. |
| `fax(v)`, `fay(v)` | `\fax...`, `\fay...` | Shear factors. |
| `bord(px)` | `\bord...` | Outline thickness in pixels. |
| `shad(px)` | `\shad...` | Shadow offset in pixels. |
| `blur(sigma)` | `\blur...` | Gaussian blur (sigma in pixels). |
| `an(numpad)` | `\an...` | Numpad alignment (1 to 9). |
| `trans([t1, t2], [accel], tags)` | `\t(...)` | Animates tags between $t_1$ and $t_2$ with optional easing. |
| `ass_color(r, g, b)` | `&HBBGGRR&` | Converts decimal RGB ($0-255$) to ASS hexadecimal BGR. |
| `ass_alpha(val)` | `&HAA&` | Converts opacity ($0-255$) to ASS hexadecimal alpha. |
| `random_color()` | `&HBBGGRR&` | Random colour string in ASS format. |
| `random_alpha()` | `&HAA&` | Random alpha string in ASS format. |

### 4.2. Math, Kinematics and Interpolation

| Function | Behaviour |
| :--- | :--- |
| `clamp(val, min_v, max_v)` | Limits $val$ to the closed interval $[min\_v, max\_v]$. |
| `lerp(a, b, t)` | Linear interpolation: $a + (b - a) \cdot t$ for $t \in [0.0, 1.0]$. |
| `map_range(v, in_min, in_max, out_min, out_max)` | Linearly remaps a value from one range to another. |
| `ease_in(t)`, `ease_out(t)`, `ease_in_out(t)` | Standard quadratic acceleration and deceleration curves. |
| `cubic_in(t)`, `cubic_out(t)` | Cubic acceleration and deceleration curves ($t^3$). |
| `elastic(t)` | Oscillating spring curve with decaying damping. |
| `bounce(t)` | Bouncing curve with natural decay. |
| `back(t)` | Easing curve with anticipation and overshoot. |
| `ipol(t, a, b, curve)` | Interpolates between $a$ and $b$ using the named curve (`"ease_in"`, `"cubic_out"`, `"bounce"`). |
| `bezier(t, p0, p1, p2, p3)` | 1D cubic Bézier evaluated at $t$. |
| `polar(angle_deg, dist)` | Converts polar coordinates $(\theta, r)$ to Cartesian: $x = r \cos(\theta)$, $y = r \sin(\theta)$. |

### 4.3. Oscillators
Periodic functions of time $t$, frequency $freq$, amplitude $amp$ and phase $offset$:
* `sine_wave(t, freq=1.0, amp=1.0, offset=0.0)`: Sine wave.
* `square_wave(t, freq=1.0, amp=1.0, offset=0.0)`: Square wave ($\pm amp$).
* `triangle_wave(t, freq=1.0, amp=1.0, offset=0.0)`: Triangle wave with linear ramps.
* `sawtooth_wave(t, freq=1.0, amp=1.0, offset=0.0)`: Sawtooth wave (periodic linear ramp).

### 4.4. Timing and Line Synchronisation

| Function | Description |
| :--- | :--- |
| `time_lead_in(delay, [base])` (or `li(delay)`) | Staggered entrance time in milliseconds. |
| `time_lead_out(delay, [base])` (or `lo(delay)`) | Staggered exit time in milliseconds. |
| `time_middle_1(delay, [base])` (or `m1(delay)`) | Radial sequence from the line centre outwards. |
| `time_middle_2(delay, [base])` (or `m2(delay)`) | Radial sequence from the line edges inwards. |
| `time_loop_1(delay, [mode])` (or `l1(delay)`) | Cyclic loop sequence for sustained entrance animations. |
| `time_loop_2(delay, [mode])` (or `l2(delay)`) | Cyclic loop sequence for sustained exit animations. |
| `time_to_frame(ms, [fps])` | Converts milliseconds to an integer frame count. |
| `duration(obj)` | Duration in ms of the given object or the active context. |
| `parse_ass_time("0:01:23.45")` | Converts an ASS timestamp string to milliseconds. |
| `format_ass_time(ms)` | Converts milliseconds to an ASS timestamp (`H:MM:SS.cs`). |
| `sync.next`, `sync.prev` | Gap in milliseconds to the next or previous dialogue line. |
| `sync.style_next`, `sync.actor_next` | Gap in milliseconds to the next line with the same style or actor. |
| `calculate_sync_gap(dir, mode, max_gap)` | General helper that measures gaps and overlaps between lines. |

### 4.5. Vector Shapes

The script can emit drawing strings directly, for use as shapes, particles or clips:
* `shape_circle()`, `shape_square()`, `shape_rectangle()`
* `shape_triangle()`, `shape_rhombus()`, `shape_rounded_corners()`
* `shape_pentagon()`, `shape_hexagon()`, `shape_octagon()`
* `shape_star()`, `shape_heart()`
* `resolve_shape(name)`: Looks up any preset drawing registered in the shape library.

### 4.6. Audio Analysis
* `audio_rms(start_ms, end_ms, [path])`: RMS power of the audio over the window ($0.0 \dots 1.0$).
* `audio_peak(start_ms, end_ms, [path])`: Peak amplitude within the window ($0.0 \dots 1.0$).
* `audio_band(start_ms, end_ms, min_hz, max_hz, [path])`: Energy within a frequency band (e.g. sub-bass from 20 Hz to 120 Hz).
* `audio_fft(start_ms, end_ms, num_bands, min_hz, max_hz, [path])`: Normalised array of spectral band values from a Fast Fourier Transform.

### 4.7. Persistent Memory and Shared State
* `remember(key, value)`: Stores a value in persistent memory. It persists across syllable, character and dialogue line passes.
* `recall(key, default=None)`: Returns the stored value, or `default` if the key has not been set yet.
* `tag_only(condition, tag_str)`: Returns `tag_str` if `condition` is true, otherwise an empty string.

---

## 5. Deterministic Random (`R` and the `by` Dispatcher)

Plain pseudo-random functions with no fixed seed give a different value on every evaluation or frame, which makes positions jitter.

Pyxis uses a **deterministic pseudo-random engine whose seed is derived from the node topology and the iteration indices**, so the same unit always gets the same value.

### 5.1. Random Modes

* `R(min, max)`: Deterministic uniform integer or stepped float, bounded by context.
* `Rs(min, max)`: **Symmetric bipolar random**, generating values across $\pm [min, max]$.
* `Rc(min, max)` / `Rcs(min, max)`: Random with 2 decimal places.
* `Rd(min, max)` / `Rds(min, max)`: Random with 1 decimal place.
* `Rm(min, max)` / `Rms(min, max)`: Random with 3 decimal places.
* `Rr(min, max)`: Random value scaled proportionally to the video output resolution.
* `Rstep(min, max, step)`: Random value snapped to multiples of `step` (e.g. `Rstep(0, 360, 45)`).
* `R2d(min, max)`: Independent coordinate pair `"X,Y"`.
* `Rbool(prob=50)`: `True` with the given percentage probability ($0-100\%$).
* `Rcolor(c1, c2)`: Random ASS colour interpolated along the hue range between two colours.
* `Re("optA, optB, optC")`: Picks one item at random from a comma-separated list.

### 5.2. The `by` Dispatcher

To evaluate a random value **exactly once per syllable, particle or sub-loop iteration**, use:

$$\text{by}.\langle \text{iterator} \rangle.\langle \text{R\_mode} \rangle(\text{args})$$

**Examples:**
```python
# A stable rotation angle per syllable (persists unchanged across nested loops)
ang = by.syl.R(-45, 45)

# A unique velocity offset per Slicer polygonal piece
vel_x = by.s_i.Rms(-150, 150)

# A distinct vertical jitter per MaxLoop clone index (j)
offset_y = by.j.Rs(20, 80)
```

---

## 6. Python vs Lua

| Aspect | Python Mode (`language: "Python"`) | Lua Mode (`language: "Lua"`) |
| :--- | :--- | :--- |
| **Array Indexing** | Zero-based ($0 \dots N-1$) for native lists. | One-based ($1 \dots N$) for tables. |
| **Metric Indices** | `syl.i`, `line.i` are 1-based integers in both. | `syl.i`, `line.i` are 1-based integers in both. |
| **Data Structures** | Dictionaries `{}` and Lists `[]`. | Numeric and associative Tables `{}`. |
| **Main Return Value** | `result = ...` or trailing expression. | `result = ...` or `return ...`. |
| **Multiple Outputs** | `outputs['out1'] = val` or `out1 = val`. | `outputs.out1 = val` or `out1 = val`. |
| **Ternary Logic** | `x = a if cond else b` | `x = cond and a or b` |
| **String Concatenation** | `+` operator or f-strings `f"{a}{b}"` | `..` operator |
| **Math Library** | `math.sin`, `math.pi`, `abs`, etc. | `math.sin`, `math.pi`, `math.abs`, etc. |
| **Null Representation**| `None` | `nil` |

---

## 7. Do's and Don'ts

### ✅ Good uses:
1. **Custom kinematics and simulation:** Gravity, orbital trajectories, harmonic oscillation, spring damping.
2. **Building ASS tags:** Clean, transform and combine tag strings with the native helpers (`merge_ass_tags`, `strip_tags`, `pos`, `move`).
3. **Conditional styling:** Branch on actor name, layer index, syllable timing or the gap to the next line.
4. **Fan-out:** Assign to `outputs['out1']`, `outputs['out2']`, etc. to send coordinates or metrics to several graph branches at once.
5. **State:** Keep counters, trail emitters or inter-line buffers with `remember()` and `recall()`.

### ❌ Avoid:
1. **Blocking file I/O:** Don't call `open()` or inspect the disk on every syllable or particle iteration. Read the file once and cache the contents with `recall()` or a memory buffer.
2. **Mutating engine internals:** Don't overwrite internal dictionary bindings or host engine references (`context["_engine"] = None`). The context is for reading metrics and publishing tags.
3. **Non-numeric values in numeric tags:** Don't inject `None`, `nil` or unvalidated strings into numeric ASS tags (e.g. `\pos(None, 20)`). The Pyxis helpers (`pos()`, `fscx()`) sanitise their arguments and avoid syntax errors.
4. **Expensive code in nested loops:** Inside multi-level iterators (`Slicer` $\times$ `MaxLoop`), the script runs $P \times J$ times per syllable. Keep each iteration $\mathcal{O}(1)$ and don't use `while` loops without a strict termination bound.
5. **Inconsistent Python indentation:** The real-time linter checks the script before evaluation, and irregular indentation shows a diagnostic in the node header.

---

## 8. Recipes

### 8.1. Recipe A: Elastic Pop-In with Anticipation (Python)

Replaces a whole chain of retimer, interpolator and tag-assembler nodes:

```python
# Compute normalised parametric progression t based on syllable lead-in
t_in = clamp((line.start_time + syl.syl_start - fx.start_time) / 300.0, 0.0, 1.0)

# Apply elastic spring curve to horizontal and vertical scale
scale = lerp(0.0, 100.0, elastic(t_in))

# Z-rotation with subtle anticipation settling smoothly at 0 degrees
rot = lerp(by.syl.Rs(30, 60), 0.0, back(t_in))

# Opacity fade in
alpha_val = lerp(255, 0, t_in)

# Assemble and return sanitised ASS override tags
result = pos(syl.x, syl.y) + fscxy(scale) + frz(rot) + alpha(ass_alpha(alpha_val))
```

### 8.2. Recipe B: Particle Dispersion with Gravity (Lua)

Scatters the particles produced by `Slicer` or `MaxLoop`:

```lua
-- Physical kinematics evaluated via the deterministic 'by' dispatcher
local ang = by.s_i.R(0, 360)
local speed = by.s_i.R(80, 250)
local gravity = 120.0

-- Normalised time elapsed since syllable activation
local t = clamp((fx.start_time - syl.start_time) / syl.duration, 0.0, 1.0)

-- Cartesian trajectory integration
local rad = math.rad(ang)
local dx = math.cos(rad) * speed * t
local dy = (math.sin(rad) * speed * t) + (0.5 * gravity * t * t)

-- Cumulative rotation throughout descent
local rz = by.s_i.Rs(90, 360) * t

-- Stream output directly into the ASS rendering pipeline
result = pos(syl.x + dx, syl.y + dy) .. frz(rz) .. fad(0, 150)
```

### 8.3. Recipe C: Audio-Reactive Bass Pulse (Python)

Reads the energy of the linked project audio track:

```python
# Extract acoustic energy in the bass frequency band (30 Hz to 120 Hz)
bass_energy = audio_band(syl.start_time, syl.end_time, min_hz=30, max_hz=120)

# Remap acoustic energy (0.0..1.0) to scale expansion and blur bloom
scale_boost = map_range(bass_energy, 0.0, 1.0, 100.0, 160.0)
blur_amount = map_range(bass_energy, 0.0, 1.0, 1.0, 6.0)

# Add subtle harmonic wave oscillation
wave = sine_wave(syl.i * 0.2, freq=2.0, amp=15.0)

# Emit animated ASS overrides
result = pos(syl.x, syl.y + wave) + fscxy(scale_boost) + blur(blur_amount)
```

---

## 9. Diagnostics and Debugging

1. **Linter:** While you type in the node's Ace editor, Python (`ast.parse`) and Lua syntax errors are underlined and listed with suggestions in the diagnostics drawer.
2. **Autocompletion (`Ctrl + Space`):** The editor knows the context variables (`syl.*`, `char.*`, `line.*`, `ink.*`), the tag generator functions and the `by.<iterator>.*` shortcuts, and shows HTML documentation tooltips.
3. **Error handling:** If the user code raises an unhandled exception during generation, Pyxis catches it and prints a diagnostic message (`[Err Python Script: ...]` or `[Err Lua Script: ...]`) to the debug console, so Aegisub doesn't freeze or crash.

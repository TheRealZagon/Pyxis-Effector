# Basics

The **Basics** category holds the nodes for generating, transforming, formatting and routing primitive data (numbers, strings, colours, expressions and conditionals) used to build ASS subtitle effects.

---

## 1. Node `Basics/Number` (Numeric Constant and Expressions)

Emits a number. The value can be a constant, an ASS context variable or an algebraic expression, and it is evaluated on every iteration.

![Basics/Number](img/number.jpg)

**Output**
1. **`[1.1] Number`:** The result as a text string. Exact integers have no decimal places (e.g. `10`). Fractional results are rounded to at most 4 decimal places with trailing zeroes removed (e.g. `12.5`).

**Properties**
1. **`[2.1] Value` (`value`):** Accepts plain numbers (`100`, `-45.2`), ASS context variables (`syl.x`, `line.width`, `j`, `i`, `char.n`) and expressions (`syl.width / 2 + 10`, `sin(j * 0.1) * 50`).

Identifiers registered in the active context (`syl`, `line`, `char`, `video_fps`, etc.) are replaced by their numeric values before the calculation. Both decimal points (`12.5`) and decimal commas (`12,5`) are accepted.

**Tips**
* Connect `Number` to `Basics/MultiTag` inputs or to template placeholders in `Basics/Dynamic Format` to drive numeric tags such as `\fscx<val>`, `\fscy<val>`, `\blur<val>` or a position like `\pos(syl.center, <val>)`.
* Timing ports (`Start Time`, `End Time`) accept expressions relative to the context, e.g. `syl.start_time - 150` or `line.duration + 200`.

---

## 2. Node `Basics/String` (Literal Text String)

Emits a fixed text string, optionally containing context macros. Use it for dialogue text, style names, drawing commands or ASS escape sequences.

![Basics/String](img/string.jpg)

**Output**
1. **`[1.1] String`:** The text configured in the node body.

**Properties**
1. **`[2.1] Text` (`value`):** Accepts plain text, ASS line break and space escapes (`\N`, `\h`), tag blocks (`{\an5\bord0\shad0}`) and vector drawing paths (`m 0 0 l 100 0 100 100 0 100`). Inside `{\...}` blocks, the Pyxis string evaluator resolves expressions and context variables within the tag parentheses (e.g. `{\pos(syl.center, syl.middle)}` or `\fscx(100 + 20 * i)`) and leaves the surrounding literal text untouched.

**Tips**
* Connect `String` to `Basics/Concatenate` or `Output (Tags)` to prepend a fixed header such as `{\an5\bord1\blur1.5}`.
* Keep vector code in a single `String` node wired to the `Draw Code` input of `Shape/Slicer` or `Shape/Transform`, so long paths are not duplicated across the graph.

---

## 3. Node `Basics/Text` (String Manipulation and Processing)

Applies text operations to an arbitrary string or to the active context unit: tag stripping, case changes, search and replace, Japanese transliteration and syllable splitting.

![Basics/Text](img/text.jpg)

**Input**
1. **`Text`:** The string to process. If disconnected, the node takes the text of the active context unit, in this order of priority: `active_unit.text_stripped` $\to$ `syl.text` $\to$ `char.text` $\to$ `line.text`.

**Output**
1. **`[1.1] Out`:** The result of the selected operation.

### Operations (`operation`)

| Operation (`operation`) | Description | Behaviour & Auxiliary Parameters |
| :--- | :--- | :--- |
| `strip_tags` | Remove ASS tags | Removes all `{\...}` blocks, turns `\N`, `\n` and `\h` into normal spaces, and trims leading and trailing whitespace. |
| `uppercase` | Uppercase | Converts the whole string to uppercase (`str.upper()`). |
| `lowercase` | Lowercase | Converts the whole string to lowercase (`str.lower()`). |
| `clean_spaces` | Collapse spaces | Replaces runs of spaces and tabs with a single space (`[ \t]+` $\to$ `" "`). |
| `replace` | Replace substring | Replaces every occurrence of `Search` with `Replace With`. |
| `substring` | Extract | Extracts `Length` characters starting at index `Start` (0-based). |
| `length` | String length | Returns the number of characters as a string. |
| `contains` | Substring check | Emits `"1"` if the string contains `Search`, otherwise `"0"`. |
| `kana` | Japanese transliteration | Converts between Romaji, Hiragana and Katakana using an equivalence table. Handles digraphs and geminate consonants with sokuon (`っ` / `ッ`). |
| `romaji_to_karaoke` | Automatic syllable splitting | Splits Romaji words into syllables and generates timed karaoke tags (`\k<dur>`, `\kf<dur>`, `\ko<dur>`), dividing the line duration evenly between the syllables. |

#### `kana`
Phonetic patterns are matched longest first, so trigraphs and digraphs (`kya`, `tsu`, `chi`, `sha`) take precedence over single vowels or consonants (`ka`, `ta`, `sa`, `a`). The `Mode` options are:
* `Romaji to Hiragana`: e.g. `"sakura"` $\to$ `"さくら"`, `"gakkou"` $\to$ `"がっこう"`.
* `Romaji to Katakana`: e.g. `"karaoke"` $\to$ `"カラオケ"`.
* `Hiragana to Katakana`
* `Katakana to Hiragana`
* `Kana to Romaji`: converts Hiragana or Katakana to standard Romaji.

#### `romaji_to_karaoke`
Splits the input into words and then into the syllables of the romanised Japanese. For a line of total duration $T$ in centiseconds and $N$ detected syllables:
$$\text{Duration per syllable } d_i = \left\lfloor \frac{T}{N} \right\rfloor + (1 \text{ if } i < (T \bmod N))$$

The tag set in `K Mode` (`\k`, `\kf`, `\ko`, `\K`) is inserted before each syllable with its duration in centiseconds (e.g. `{\k15}sa{\k20}ku{\k15}ra`).

**Tips**
* Run `strip_tags` before the `Text` input of `Basics/Text to Shape`, so the vector engine only receives glyphs and no ASS control codes.
* Wire `contains` into `Basics/Only` to choose a style path based on keywords in the dialogue.

---

## 4. Node `Basics/Color Picker` (Colour Selector and Palettes)

Colour picker and palette manager that converts between ASS BGR (`&HBBGGRR&`) and web hexadecimal (`#RRGGBB`).

![Basics/Color Picker](img/color_picker.jpg)

**Outputs**
1. **`[1.1] Color List`:** All colours of the active palette as a comma-separated string, each in the output format set on its swatch (e.g. `"&H5500FF&, &HFF9900&, #FFFFFF"`).
2. **`[1.2] ASS Color`:** The first swatch (Slot 0) in ASS BGR syntax `&HBBGGRR&`.

**Controls**
* Clicking a swatch opens the picker, with sliders, a live preview and an output format selector.
* You can add swatches and set each one to export as `ASS` or `HEX`.

### Colour conversion
Pyxis converts between the usual RGB channel order and the BGR order that Aegisub and libass use:

$$\text{RGB: } (R, G, B) \implies \text{ASS Colour: } \&\text{H}B_{\text{hex}}G_{\text{hex}}R_{\text{hex}}\&$$

* **`ASS`:** swaps the red and blue channels to match libass. For example:
  * Pure red ($R=255, G=0, B=0$) $\implies$ `&H0000FF&`
  * Pure blue ($R=0, G=0, B=255$) $\implies$ `&HFF0000&`
  * Pure yellow ($R=255, G=255, B=0$) $\implies$ `&H00FFFF&`
* **`HEX`:** keeps the standard `#RRGGBB` web format, for use with external tools.

**Tips**
* Connect `ASS Color` to the primary (`\1c`) or border (`\3c`) colour inputs of `Basics/MultiTag`.
* Connect `Color List` to the matching port of `Functions/Color Gradient` or `Shape/Concentric Borders` for multi-colour transitions.

---

## 5. Node `Basics/Math` (Mathematical Engine and Curves)

Evaluates arithmetic, trigonometry, easing curves, periodic waves and range utilities, grouped into 8 families.

![Basics/Math](img/math.jpg)

**Header combos**
1. **`[2.1] Category` (`category`):** The family:
   * `basic`: elementary arithmetic.
   * `trig`: direct and inverse trigonometry, and angle conversions.
   * `rounding`: nearest integer, floor and ceiling.
   * `clamping`: range bounding and comparisons.
   * `easing`: normalised acceleration and deceleration curves ($t \in [0.0, 1.0]$).
   * `waves`: periodic waveform oscillators.
   * `random`: pseudo-random numbers with an optional deterministic seed.
   * `utilities`: linear range re-mapping and interpolation.
2. **`[2.2] Operation` (`operation`):** The function to run within the selected family.

**Inputs**
1. **`A`:** Main operand, progress factor $t$, angle or base value. If disconnected, uses the value set in the node's internal property.
2. **`B`:** Second operand, upper bound, frequency or target value.

**Output**
1. **`[1.1] Out`:** The scalar result. Exact integers have no decimal places (e.g. `25`); fractional results have at most 4 decimal places (e.g. `0.7071`).

### `basic` (arithmetic)
* **`add` ($A + B$):** Addition.
* **`sub` ($A - B$):** Subtraction.
* **`mul` ($A \cdot B$):** Multiplication.
* **`div` ($A / B$):** Division. Returns `0.0` if $B = 0$.
* **`mod` ($A \pmod B$):** Remainder. Returns `0.0` if $B = 0$.
* **`pow` ($A^B$):** Exponentiation.
* **`abs` ($|A|$):** Absolute value.
* **`neg` ($-A$):** Sign change.

### `trig` (trigonometry)
The direct functions (`sin`, `cos`, `tan`) take the angle $A$ in **degrees** ($0^\circ \dots 360^\circ$), the same unit as the ASS rotation tags (`\frz`, `\frx`, `\fry`). The inverse functions return degrees.

* **`sin`:** $\sin\left(\frac{A \cdot \pi}{180}\right)$
* **`cos`:** $\cos\left(\frac{A \cdot \pi}{180}\right)$
* **`tan`:** $\tan\left(\frac{A \cdot \pi}{180}\right)$
* **`asin` / `arcsin`:** $\arcsin(\text{clamp}(A, -1, 1)) \cdot \frac{180}{\pi} \in [-90^\circ, 90^\circ]$
* **`acos` / `arccos`:** $\arccos(\text{clamp}(A, -1, 1)) \cdot \frac{180}{\pi} \in [0^\circ, 180^\circ]$
* **`atan` / `arctan`:** $\arctan(A) \cdot \frac{180}{\pi} \in (-90^\circ, 90^\circ)$
* **`atan2`:** $\text{atan2}(Y, X) \cdot \frac{180}{\pi}$ where $Y = A$ and $X = B$, in range $[-180^\circ, 180^\circ]$
* **`rad` / `radians`:** Degrees to radians: $A \cdot \frac{\pi}{180}$.
* **`deg` / `degrees`:** Radians to degrees: $A \cdot \frac{180}{\pi}$.

### `rounding`
* **`round`:** Rounds $A$ to the nearest integer.
* **`floor`:** Largest integer less than or equal to $A$ ($\lfloor A \rfloor$).
* **`ceil`:** Smallest integer greater than or equal to $A$ ($\lceil A \rceil$).

### `easing` (progression curves)
Takes a progress factor $t = \text{clamp}(A, 0.0, 1.0)$ and returns the transformed value in $[0.0, 1.0]$:

* **`ease_in`:** Quadratic acceleration: $f(t) = t^2$.
* **`ease_out`:** Quadratic deceleration: $f(t) = 1 - (1 - t)^2$.
* **`ease_in_out`:** Acceleration, then deceleration:
  $$f(t) = \begin{cases} 2t^2 & \text{if } t < 0.5 \\ 1 - \frac{(-2t + 2)^2}{2} & \text{if } t \ge 0.5 \end{cases}$$
* **`cubic_in`:** Cubic acceleration: $f(t) = t^3$.
* **`cubic_out`:** Cubic deceleration: $f(t) = 1 - (1 - t)^3$.
* **`expo`:** Exponential: $f(t) = 2^{10(t - 1)}$ for $t > 0$.
* **`elastic`:** Damped elastic oscillation.
* **`bounce`:** Bounce in 4 segments.
* **`back`:** Overshoot: $f(t) = (c_1 + 1)t^3 - c_1 t^2$ where $c_1 = 1.70158$.

### `waves` (periodic oscillators)
Oscillations driven by $t = A$, frequency $f = \text{freq}$, amplitude $A_{\text{amp}} = \text{amp}$ and constant offset $\text{Offset}$:

* **`sine`:** $y(t) = A_{\text{amp}} \cdot \sin(2\pi \cdot f \cdot t) + \text{Offset}$
* **`square`:** Emits $+A_{\text{amp}} + \text{Offset}$ during positive half-cycles and $-A_{\text{amp}} + \text{Offset}$ during negative ones.
* **`triangle`:** For $\phi = (t \cdot f) \pmod 1$, $y(t) = A_{\text{amp}} \cdot (2|2\phi - 1| - 1) + \text{Offset}$.
* **`sawtooth`:** Rising ramp that drops instantly: for $\phi = (t \cdot f) \pmod 1$, $y(t) = A_{\text{amp}} \cdot (2\phi - 1) + \text{Offset}$.

### `utilities`, `clamping` and `random`
* **`clamp`:** Limits $A$ to the interval $[\text{Min}, \text{Max}]$.
* **`lerp`:** Linear interpolation between $A$ and $B$ for $t \in [0.0, 1.0]$: $\text{lerp}(A, B, t) = A + (B - A) \cdot t$.
* **`map_range`:** Re-maps $A$ proportionally from $[\text{MinIn}, \text{MaxIn}]$ to $[\text{MinOut}, \text{MaxOut}]$.
* **`min` / `max`:** The smaller or larger of $A$ and $B$.
* **`random`:** Uniform pseudo-random number in $[\text{Min}, \text{Max}]$ with an optional seed (`Seed`).

**Tips**
* Connect a `waves/sine` output to an `\frz` field in `Basics/Dynamic Format` for a rocking motion (e.g. `\frz(%s)` with an amplitude of $10^\circ$).
* Wire the `Out` port of an `easing/ease_out` curve into the `\fscx` and `\fscy` ports of `Basics/MultiTag` to animate a smooth entrance from 0% to 100%.

---

## 6. Node `Basics/MultiRandom` (Deterministic Random Generator)

Generates pseudo-random values or deterministic lists, for scattering, tag jitter and random sequences. It has 15 modes.

![Basics/MultiRandom](img/multirandom.jpg)

**Inputs**
1. **`Min`:** Lower bound of the range, start colour or option list.
2. **`Max`:** Upper bound of the range or end colour.
3. **`Step`:** Quantisation step between generated values.
4. **`Total (N)`:** Number of values to emit through the `Batch / List` output.
5. **`Iterator`:** Scope variable that controls memoisation (e.g. `s_i`, `j`, `syl`, `char`, `line`). If empty, a new value is calculated on every call.

**Outputs**
1. **`[1.1] Data`:** A single random value for the current iteration.
2. **`[1.2] Batch / List`:** A comma-separated list of $N$ random values (`v1, v2, v3, ...`), for parameter lists or particle arrays.

### Per-iterator values in expressions (`by.<iterator>.<R_mode>`)
To get a random value that stays fixed per iterator inside ASS expressions or Python scripts:
* **In ASS expressions:**
  ```text
  \frz(by.syl.Rs(15))
  \fscx(100 + by.char.R(0, 30))
  ```
* **In scripts (`Define Vars` / `Script Code`):**
  ```python
  angle = by.s_i.Rms(0.01, 0.02)            # Constant value during the active Slicer piece
  offset = by.j.Rs(10)                      # Constant value across the MaxLoop cycle
  colour = by.syl.Rcolor("#FFFFFF", "#0088FF") # Constant colour for the entire syllable
  ```
Within one cycle of the given iterator, repeated calls return the same stored value. When the iterator advances, a new value is calculated and stored.

### Modes (`mode`)

| Mode (`mode`) | Name | Description & Range | Example Output |
| :--- | :--- | :--- | :--- |
| `R` | Uniform | Random number between `Min` and `Max`, quantised to multiples of `Step`. If the bounds and step are integers, returns integers. | `42` |
| `Rs` | Symmetric | Uniform value with a random sign ($\pm 1$, equal probability): $\text{res} = R(\text{Min}, \text{Max}) \cdot (\pm 1)$. | `-35` or `35` |
| `Rr` | Resolution-relative | Scales the value by the script's horizontal resolution ($R_x$ relative to $1280\text{ px}$): $\text{res} = R \cdot \frac{R_x}{1280}$. | `68.5` |
| `Rd` | 1 decimal | Uniform float with 1 decimal place ($0.1$). | `14.3` |
| `Rc` | 2 decimals | Uniform float with 2 decimal places ($0.01$). | `87.25` |
| `Rm` | 3 decimals | Uniform float with 3 decimal places ($0.001$). | `3.142` |
| `Rds` | Signed 1 decimal | `Rd` with a random sign ($\pm$). | `-12.4` |
| `Rcs` | Signed 2 decimals | `Rc` with a random sign ($\pm$). | `-45.82` |
| `Rms` | Signed 3 decimals | `Rm` with a random sign ($\pm$). | `+0.915` |
| `Re` | Choice | Picks one element at random from the comma-separated list in `Options` (e.g. `\blur1, \blur3, \blur6`). | `\blur3` |
| `Rfake` | Deterministic hash | Congruential generator that depends only on the iteration counter ($i$ or $j$): $\text{Hash}(c) = (c \cdot 9301 + 49297) \pmod{233280}$. | `18` |
| `Rcolor` | Colour | Random colour interpolated uniformly between `Min` and `Max` in RGB space, or picked from a list if `Min` contains commas. | `&H7FA412&` |
| `R2d` | 2D coordinates | An independent Cartesian pair in `"X,Y"` format. | `120.5,-45.2` |
| `Rbool` | Probabilistic boolean | Returns `"True"` or `"False"` using the percentage $P \in [0, 100]$ in `Min` as the threshold. | `"True"` |
| `Rstep` | Quantised step | Values restricted to integer multiples of `Step` (e.g. rotations in multiples of $45^\circ$). | `180` |

**Tips**
* Wire a `Data` output in `Rs` mode with range $[2, 8]$ into a position offset $\Delta x$ to add a slight shake without hurting legibility.
* Use `Rcolor` scoped with `by.syl` and connected to the `\1c` input of `Basics/MultiTag` to give each syllable its own colour while its characters stay uniform.

---

## 7. Node `Basics/Concatenate` (Extensible Concatenator and Zip Mode)

Joins any number of text strings, ASS tags or vector commands into one string, either with a separator or by interleaving lists (`zip` mode).

![Basics/Concatenate](img/concatenate.jpg)

**Inputs**
* **`In1`, `In2`, $\dots$, `InN`:** Input sockets. Connecting a wire or clicking `(+)` adds more.
* A port with no wire uses the value typed into its inline text field.

**Output**
1. **`[1.1] String`:** The joined string.

### Separators (`separator`)

| Separator (`separator`) | Character | Use |
| :--- | :---: | :--- |
| `nil` / `none` / `""` | *(None)* | Direct join (e.g. merging tags into one block `\pos(X,Y)\blur2\1c&HFFFFFF&`). |
| `space` / `" "` | Space | Separating words or coordinates in ASSdraw instructions (`m 0 0 l 10 10`). |
| `comma` / `","` | Comma `,` | Building lists for palette nodes or value arrays. |
| `semicolon` / `";"` | Semicolon `;` | Grouping data parameters or script sequences. |
| `newline` / `"\n"` | Line break | Multi-line subtitles or stacked text blocks. |
| `zip` | *(Interleaved)* | Element-by-element combination of value lists. |

### `zip` mode
With `separator` set to `zip`, each input is treated as a comma-separated list and the lists are joined element by element:

$$\text{In}_1 = [A_1, A_2, A_3], \quad \text{In}_2 = [B_1, B_2, B_3] \implies \text{Out} = [A_1 B_1, \, A_2 B_2, \, A_3 B_3]$$

1. Each active input is split into tokens.
2. If a port's inline field contains a tag prefix (e.g. `\1c`, `\blur`), it is prepended to every token of that list.
3. Tokens are paired by position up to the length of the shortest list that has more than one item. The output is a comma-separated list of the merged keyframes.

**Tips**
* Set `separator` to `nil` when combining `MultiTag` outputs or literal strings, so no stray spaces end up in the tag block and affect libass rendering.
* Use `zip` to pair a colour list from `Functions/Color Gradient` with an alpha list for per-frame transitions.

---

## 8. Node `Basics/Dynamic Format` (Dynamic String Formatter)

Builds strings from a template with `printf`-style specifiers (`%s`, `%d`, `%f`, `%.2f`, `%04d`, `%x`). Comma-separated lists are handled automatically.

![Basics/Dynamic Format](img/dynamic_format.jpg)

**Inputs**
1. **`In1`, `In2`, $\dots$, `InN`:** Scalar values or lists, inserted in order into the template's `%...` specifiers.

**Output**
1. **`[1.1] String`:** The formatted string. If the inputs are lists, the formatted strings are joined with commas.

### Specifiers in `format`

| Specifier | Expected Type | Conversion | Example with Input `42.68` |
| :--- | :--- | :--- | :--- |
| `%s` | Any | Inserted as text. | `"42.68"` |
| `%d` / `%i` | Integer | Converted to integer. | `"42"` |
| `%04d` | Padded integer | Integer zero-padded to 4 digits. | `"0042"` |
| `%f` | Float | Standard floating-point representation. | `"42.680000"` |
| `%.2f` | Float, 2 decimals | Exactly 2 decimal places. | `"42.68"` |
| `%x` / `%X` | Hexadecimal | Integer in base 16, lowercase or uppercase. | `"2a"` / `"2A"` |

### Lists
If any input receives a comma-separated list (e.g. `In1 = "10, 20, 30"`, `In2 = "0.5, 1.0, 1.5"`), the template is repeated for each pair of elements:

$$\text{Template: } \texttt{\\blur\%s\\bord\%s} \implies \texttt{"\\blur10\\bord0.5, \\blur20\\bord1.0, \\blur30\\bord1.5"}$$

**Tips**
* Use `\pos(%.1f,%.1f)` or `\fscx%d\fscy%d` to control the precision of calculated values and avoid long decimals in the ASS file.
* A template like `\t(%d,%d,\fscx%d\fscy%d)` packs timing and scale calculations into a single node before the final output.

---

## 9. Node `Basics/MultiTag` (Universal ASS Tag Generator)

Generates ASS (*Advanced SubStation Alpha*) tags: position, motion, transforms, colours, alpha and vector clips.

![Basics/MultiTag](img/multitag.jpg)

**Header combos**
1. **`[2.1] Tag Type` (`tag_type`):** Selects the ASS tag and reconfigures the input ports:

```
[ \pos ] ───> Inputs: [ X, Y ]
[ \move ] ──> Inputs: [ X1, Y1, X2, Y2, T1, T2 ]
[ \org ] ───> Inputs: [ X, Y ]
[ \t ] ─────> Inputs: [ Tags, T1, T2, Accel ]
[ \clip ] ──> Inputs: [ Shape / Drawing ]
[ \1c..\4c ]> Inputs: [ Color ]
[ \alpha ] ─> Inputs: [ Alpha (0..255) ]
[ Scalar ] ─> Inputs: [ Value ] (e.g. \fscx, \frz, \blur, \bord)
```

2. **Tag catalogue:** Double-clicking the node body or clicking the mode pill in the header opens the visual ASS tag catalogue. You can search it by tag name, prefix or category (*Positioning, Kinematics, Colourimetry, Alpha, Scaling, Borders, Typography, Karaoke*).

**Output**
1. **`[1.1] String`:** The formatted tag with valid ASS syntax (e.g. `\pos(640,360)`, `\t(0,500,2.0,\fscx150\fscy150)`).

### Supported tags
* **`pos` $\to$ `\pos(X,Y)`:** Screen position.
* **`move` $\to$ `\move(X1,Y1,X2,Y2[,T1,T2])`:** Linear movement between two points.
* **`org` $\to$ `\org(X,Y)`:** Origin point for rotations (`\frz`) and shear transforms.
* **`t` $\to$ `\t([T1,T2,][Accel,]Tags)`:** Animates tags over time.
* **`fad` $\to$ `\fad(FadeIn,FadeOut)`:** Simple fade in and out, in milliseconds.
* **`fade` $\to$ `\fade(A1,A2,A3,T1,T2,T3,T4)`:** Timed 3-level alpha fade.
* **`clip` / `iclip` $\to$ `\clip(Shape)` / `\iclip(Shape)`:** Normal or inverted vector clip.
* **`1c` $\dots$ `4c` $\to$ `\1c&HBBGGRR&` $\dots$ `\4c&HBBGGRR&`:** Primary fill, inactive karaoke, border and shadow colours.
* **`alpha`, `1a` $\dots$ `4a` $\to$ `\alpha&HAA&` $\dots$ `\4a&HAA&`:** Global or per-channel opacity.
* **Scale and rotation:** `\fscx`, `\fscy`, `\frz`, `\frx`, `\fry`, `\fax`, `\fay`.
* **Border and shadow:** `\bord`, `\xbord`, `\ybord`, `\shad`, `\xshad`, `\yshad`.
* **Blur:** `\blur`, `\be`.
* **Typography and alignment:** `\an`, `\fs`, `\fsp`, `\q`.

**Tips**
* Wire numeric outputs (`Basics/Number` or `Basics/Math`) into `\fscx`, `\fscy` or `\frz` instead of concatenating strings by hand.
* Connect the `String` outputs of several `MultiTag` nodes to `Basics/Concatenate` with a `nil` separator to build the final `{\...}` override block before output.

---

## 10. Node `Basics/Only` (Conditional Branching and Filtering)

Routes or filters data depending on a condition evaluated against the active ASS context.

![Basics/Only](img/only_a.jpg)

**Header combos**
1. **`[2.1] Mode` (`mode`):** Sets the node's sockets:
   * `select` (*Selector / Ternary 2 $\to$ 1*): two inputs (`True`, `False`) and one output (`Out`). Emits the data from `True` if the condition is true, otherwise the data from `False`.
   * `split` (*Diverter 1 $\to$ 2*): one input (`In`) and two outputs (`True`, `False`). If the condition is true, sends the input to `True` and emits an empty string `""` on `False`. If it is false, emits `""` on `True` and sends the input to `False`.

![Basics/Only (Filter Mode)](img/only_b.jpg)

### Sockets by mode

#### `select` mode (2 $\to$ 1)
* **Inputs:**
  * `True`: Data emitted when the condition is true.
  * `False`: Data emitted when the condition is false.
* **Outputs:**
  * `[1.1] Out`: The selected value.

#### `split` mode (1 $\to$ 2)
* **Inputs:**
  * `In`: Data to route.
* **Outputs:**
  * `[1.1] True`: The input if the condition is true, otherwise `""`.
  * `[1.2] False`: The input if the condition is false, otherwise `""`.

**Properties**
1. **`[2.2] Condition` (`condition`):** Logical expression evaluated on every iteration (e.g. `char.i == 1`, `syl.duration > 300`, `j % 2 == 0`, `'kanji' in line.tags_str`). Default: `"True"`.

### Evaluation

$$\text{select mode:} \quad \text{Out} = \begin{cases} \text{Input}(\text{True}) & \text{if } \text{eval}(\text{condition}) = \text{True} \\ \text{Input}(\text{False}) & \text{if } \text{eval}(\text{condition}) = \text{False} \end{cases}$$

$$\text{split mode:} \quad (\text{Out}_{\text{True}}, \text{Out}_{\text{False}}) = \begin{cases} (\text{Input}, \texttt{""}) & \text{if } \text{eval}(\text{condition}) = \text{True} \\ (\texttt{""}, \text{Input}) & \text{if } \text{eval}(\text{condition}) = \text{False} \end{cases}$$

**Tips**
* Set `condition: char.i == 1` to give only the first letter of each word or line a larger font size (`\fs40`) or a different colour.
* In `select` mode, feed two colours into `True` and `False` with `condition: char.i % 2 == 0` to alternate colours between even and odd characters.

---

## 11. Node `Basics/Once` (Single Evaluation with Scope Cache)

Caches the value of its input so it is not recomputed within the same scope (line, word, syllable, character or sub-loop).

![Basics/Once](img/once.jpg)

**Header combos**
1. **`[2.1] Mode` (`mode`):** The scope of the cache:
   * `global`: evaluated once for the whole macro run over the script.
   * `line`: once at the start of each dialogue line.
   * `word`: once at the start of each word.
   * `syl`: once at the start of each karaoke syllable.
   * `char`: once per character.
   * `loop`: once per cycle of the sub-loop variable set in `iterator` (default: `j`).

**Input**
1. **`In`:** The data to cache (e.g. vector glyph paths from `Text to Shape`, `IMG to Shape`, or colour selections).

**Properties**
1. **`[2.2] Iterator` (`iterator`):** Name of the loop variable to watch when `mode = "loop"` (default: `"j"`).

**Output**
1. **`[1.1] Out`:** The cached value, without re-evaluating the upstream subgraph.

### Cache key
The cache key combines the node identifier and the scope key of the active mode:

$$\text{CacheKey} = \langle \text{NodeID}, \, \text{ScopeKey} \rangle$$

$\text{ScopeKey}$ depends on the mode:
* `global` $\to \texttt{"global"}$
* `line` $\to \texttt{"line\_" + LineID}$
* `word` $\to \texttt{"line\_" + LineID + "\_word\_" + WordID}$
* `syl` $\to \texttt{"line\_" + LineID + "\_syl\_" + SylID}$
* `char` $\to \texttt{"line\_" + LineID + "\_char\_" + CharID}$
* `loop` $\to \texttt{"line\_" + LineID + "\_loop\_" + IteratorName + "\_" + IteratorValue}$

If $\text{CacheKey}$ is already in memory, the stored value is returned in $\mathcal{O}(1)$ time and the upstream graph is not executed.

**Tips**
* Place a `Once (mode: char)` node after `Text to Shape` when driving multi-pass effects with `MaxLoop` or `Shape/Array`. The glyph geometry is then computed once per character instead of on every loop pass.
* Insert `Once (mode: syl)` after a random generator so that all fragments or particles from one syllable share the same random value.

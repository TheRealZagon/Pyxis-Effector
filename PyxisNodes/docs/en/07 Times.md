# Times

The **Time** category covers the timing of ASS events: shifting times relative to syllable or line phases, rescaling `\t` transforms, converting between milliseconds, ASS timecodes and frames, and stretching lines to bridge the gap to the next one.

* **Phases, retiming and inter-line sync:** `Time/Retime` (§1), `Time/Lead In` (§2), `Time/Lead Out` (§3), `Time/Synced` (§4).
* **Middle offsets, loops and durations:** `Time/Middle 1` (§5), `Time/Middle 2` (§6), `Time/Loop 1` (§7), `Time/Loop 2` (§8), `Time/Duration` (§14), `Time/Offset` (§15).
* **Conversion, frames and interpolation:** `Time/Parse ASS Time` (§9), `Time/Format ASS Time` (§10), `Time/Time to Frame` (§11), `Time/Frame to Time` (§12), `Time/Ipol` (§13).

---

## 1. `Time/Retime`

Shifts a time window relative to the phase of the active element (`syl`, `line`, `presyl`, `postsyl`, etc.) and rescales ASS `\t(...)` transforms to fit it. Supports additive offsets and non-linear acceleration.

![Time/Retime](img/retime.jpg)

### 1.1. Mode

**`[2.1] Mode` (`phase`):** selects the base interval. There are 10 modes:

| Mode (`phase`) | Base Interval [$T_1, T_2$] | Description |
| :--- | :--- | :--- |
| `syl` | $[T_{\text{syl\_start}}, T_{\text{syl\_end}}]$ | **Active syllable (default):** the syllable's or character's singing window. |
| `presyl` | $[T_{\text{syl\_start}}, T_{\text{syl\_start}}]$ | **Pre-syllable:** the syllable's start instant, for preparatory animations or lead-in transitions. |
| `postsyl` | $[T_{\text{syl\_end}}, T_{\text{syl\_end}}]$ | **Post-syllable:** the syllable's end instant, for decays after singing or immediate lead-outs. |
| `line` | $[T_{\text{line\_start}}, T_{\text{line\_end}}]$ | **Full line:** the whole duration of the dialogue line. |
| `preline` | $[T_{\text{line\_start}}, T_{\text{line\_start}}]$ | **Pre-line:** the line's start instant. |
| `postline` | $[T_{\text{line\_end}}, T_{\text{line\_end}}]$ | **Post-line:** the line's end instant. |
| `start2syl` | $[T_{\text{line\_start}}, T_{\text{syl\_start}}]$ | **Lead-in to syllable:** from line start until the active syllable begins. |
| `syl2end` | $[T_{\text{syl\_end}}, T_{\text{line\_end}}]$ | **Syllable to line end (lead-out):** from the end of the active syllable until the line ends. |
| `abs` | $[0, 0]$ | **Absolute:** not tied to syllable or line times; `Offset In` and `Offset Out` give the window directly in milliseconds. |
| `sylpct` | $[T_{\text{syl\_start}} + \frac{O_{\text{in}} \cdot D_{\text{syl}}}{100}, T_{\text{syl\_start}} + \frac{O_{\text{out}} \cdot D_{\text{syl}}}{100}]$ | **Syllable percentage:** `Offset In` and `Offset Out` are percentages ($0\% \dots 100\%$) of the syllable's duration. |

### 1.2. Inputs and Properties
1. **`Tags or \t` (`tags`):** ASS override tags. Accepts static tags (e.g. `\fscx150\fscy150\alpha&HFF&`) or existing `\t(...)` blocks.
2. **`Offset In (ms)` (`offset_in`):** shift applied to the start point $T_1$. Positive values delay, negative values advance; accepts variables and expressions (default: `0`).
3. **`Offset Out (ms)` (`offset_out`):** shift applied to the end point $T_2$ (default: `0`).
4. **`Accel` (`accel`):** acceleration exponent in the tag `\t(t1, t2, accel, \tags)`. `1.0` is linear; values $< 1.0$ decelerate (*ease-out*); values $> 1.0$ accelerate (*ease-in*) (default: `1.0`).

### 1.3. Outputs
1. **`[1.1] \t Out`:** tag block in ASS syntax `\t(t1, t2, [accel,] \tags)`. $t_1$ and $t_2$ are in the **line's local time** (relative to `0 ms` at the start of the generated line).
2. **`[1.2] Start Time`:** absolute start time $T_1$ in milliseconds on the video timeline.
3. **`[1.3] End Time`:** absolute end time $T_2$ in milliseconds on the video timeline.
4. **`[1.4] Duration`:** $D = \max(0, T_2 - T_1)$, in milliseconds.

### 1.4. How `\t` Is Mapped

```
   Line Start                                              Line End
   ├──────────────────────────┬─────────────────┬──────────────────┤
   │        start2syl         │  syl (active)   │     syl2end      │
   │                          ├────────┬────────┤                  │
   │                          │ presyl │ postsyl│                  │
───┴──────────────────────────┴────────┴────────┴──────────────────┴───► Time
   0 ms                      T_syl_st  T_syl_et  Line_dur
```

If `Tags or \t` already contains `\t(t_a, t_b, ...)` blocks, the node recalculates their times and keeps the internal sub-intervals:

$$\tilde{t}_1 = T_{\text{local\_1}} + t_a, \quad \tilde{t}_2 = T_{\text{local\_1}} + t_b$$

If a `\t(...)` has no times (e.g. `\t(\blur10)`), the node inserts the full phase window:

$$\text{\textbackslash t}(T_{\text{local\_1}}, T_{\text{local\_2}}, [a,] \text{\textbackslash blur10})$$

> [!IMPORTANT]
> * **`\t Out`** is always **relative to the start of the line** ($t=0\text{ ms}$), because the ASS `\t` tag measures offsets from the start of the subtitle line itself.
> * **`Start Time` and `End Time`** are **absolute video times**, needed when creating independent timed events in `System/Output`.

### 1.5. Usage
* **Separate lead-in and lead-out effects:** use two `Retime` nodes, one with `Mode: start2syl` for the entrance and another with `Mode: syl2end` or `postsyl` for the exit.
* **Building full lines:** send `\t Out` into `Concatenate` together with `\pos` and the base style tags to assemble the line in one stream.

### 1.6. Example
A lead-in where each syllable scales from 0% to 100% and fades from transparent to opaque before it is sung:

```
Tags In: \fscx100\fscy100\alpha&H00& ──► Tags or \t ──► [Time/Retime: start2syl, accel=0.8]
                                                              └──► \t Out ──► Tags ──► [System/Output]
```

With `Tags` in `System/Output` using the base style `{\an5\pos(syl.center, syl.middle)\fscx0\fscy0\alpha&HFF&}`, the node emits:
```
{\an5\pos(320, 240)\fscx0\fscy0\alpha&HFF&\t(0, 180, 0.8, \fscx100\fscy100\alpha&H00&)}
```
The syllable transitions over the lead-in window (*start2syl*) with an ease-out curve (`accel=0.8`).

---

## 2. `Time/Lead In`

Computes a stepped offset from the index $i$ of the active unit, so each syllable or character starts its animation a little after the previous one, all before it is sung.

![Time/Lead In](img/lead_in.jpg)

### 2.1. Inputs and Properties
1. **`Delay (ms)` (`delay_ms`):** delay step per unit, in milliseconds. Accepts constants, variables and inline expressions (default: `40`).

### 2.2. Outputs
1. **`[1.1] Data`:** the offset in milliseconds.

### 2.3. Model
For the active unit index $i \in \{1, \dots, N\}$ (1-based syllable or character index in the main loop), the node applies a fixed lookahead of $-200\text{ ms}$:

$$T_{\text{out}} = T_{\text{base}} + \Delta_{\text{delay}} \cdot (i - 1) - 200$$

* $T_{\text{base}}$ is the base reference time (default $0.0\text{ ms}$).
* $\Delta_{\text{delay}}$ is the value of `Delay (ms)`.
* $i$ is the unit index ($1$-based).
* $-200\text{ ms}$ is the lookahead constant.

Example ($N=4\text{ units}, \Delta=40\text{ ms}$):
* Unit $1$ ($i=1$): $40 \cdot (1 - 1) - 200 = -200\text{ ms}$
* Unit $2$ ($i=2$): $40 \cdot (2 - 1) - 200 = -160\text{ ms}$
* Unit $3$ ($i=3$): $40 \cdot (3 - 1) - 200 = -120\text{ ms}$
* Unit $4$ ($i=4$): $40 \cdot (4 - 1) - 200 = -80\text{ ms}$

### 2.4. Example
Connect `Data` to `Offset In (ms)` of a `Time/Retime` node (in `syl` or `start2syl` mode) so each letter starts animating progressively before it is sung:

```
[Time/Lead In: delay_ms=40] ──► Data ──► Offset In (ms) ──► [Time/Retime: syl, accel=1.0]
                                                                  └──► \t Out ──► Tags ──► [System/Output]
```

If `Tags or \t` of `Retime` receives `\fscx130\fscy130\1c&H00FFFF&`, then for a line with 4 syllables each element starts its accent $200 - 40 \cdot (i - 1)$ ms before it is sung, giving a wave that anticipates the vocals.

---

## 3. `Time/Lead Out`

Computes a stepped offset from the distance of the active unit to the end of the line ($i - n$), for progressive fades and exit sequences after singing.

![Time/Lead Out](img/lead_out.jpg)

### 3.1. Inputs and Properties
1. **`Delay (ms)` (`delay_ms`):** delay step for the exit sequence, in milliseconds (default: `40`).

### 3.2. Outputs
1. **`[1.1] Data`:** the offset in milliseconds.

### 3.3. Model
For unit $i$ out of $n$ units:

$$T_{\text{out}} = T_{\text{base}} + \Delta_{\text{delay}} \cdot (i - n - 1) + 200$$

* $n$ is the total number of units in the line (`syl.n`, `char.n`).
* $+200\text{ ms}$ is the post-sustain constant.

Example ($n=4\text{ units}, \Delta=40\text{ ms}$):
* Unit $1$ ($i=1$): $40 \cdot (1 - 4 - 1) + 200 = 40 \cdot (-4) + 200 = +40\text{ ms}$
* Unit $2$ ($i=2$): $40 \cdot (2 - 4 - 1) + 200 = 40 \cdot (-3) + 200 = +80\text{ ms}$
* Unit $3$ ($i=3$): $40 \cdot (3 - 4 - 1) + 200 = 40 \cdot (-2) + 200 = +120\text{ ms}$
* Unit $4$ ($i=4$): $40 \cdot (4 - 4 - 1) + 200 = 40 \cdot (-1) + 200 = +160\text{ ms}$

### 3.4. Example
Connect `Data` to `Offset Out (ms)` of a `Retime` node in `postsyl` mode (or `syl`), so earlier syllables fade out first and later ones stay on screen longer, following the reading order:

```
[Time/Lead Out: delay_ms=50] ──► Data ──► Offset Out (ms) ──► [Time/Retime: postsyl]
                                                                   └──► \t Out ──► Tags ──► [System/Output]
```

With `Tags or \t: \alpha&HFF&`, the first syllable starts fading shortly after it is sung, while the last ones stay visible longer, so the text does not vanish all at once.

---

## 4. `Time/Synced`

Computes extra display time between consecutive dialogue lines. It fills musical pauses, compensates for the on-screen distance between phrases, and smooths the transition to the next line.

![Time/Synced](img/synced.jpg)

### 4.1. Inputs and Properties
1. **`Mode` (`mode`):** how the current line is paired with the next line (`next_line`):
   * `order`: the next line in the list, with no filtering.
   * `style`: the next line with the same ASS style name (`style_name`).
   * `actor`: the next line with the same actor (`actor`).
   * `layer`: the next line with the same ASS layer (`layer`).
   * `effect`: the next line with the same ASS effect field (`effect`).
2. **`Constant` (`progression_const`):** progression multiplier based on character density (ms per glyph) (default: `0`).
3. **`Fade (ms)` (`fade_dur`):** duration of the planned fade-out, in milliseconds (default: `300`).
4. **`Max Extra` (`max_added_time`):** cap on the extra time, in milliseconds, that can be added to the line (default: `2000`).
5. **`Delay Line` (`delay_ms`):** minimum gap needed to treat the interval as a pause between lines (default: `250`).
6. **`Threshold` (`max_gap_threshold`):** maximum pause. If the pause between the current and next line exceeds it, the algorithm treats it as an independent long pause and does not stretch the line across it (default: `3000`).

### 4.2. Outputs
1. **`[1.1] Extra ms`:** the extra milliseconds calculated ($\Delta t_{\text{extra}}$).
2. **`[1.2] Sync End`:** the synchronised absolute end time ($T_{\text{line\_end}} + \Delta t_{\text{extra}}$), ready to use as the line's ASS end time.

### 4.3. Algorithm

```
  Current Line                      Inter-Line Gap               Next Line
├──────────────────────┤◄────────────────────────────────►├──────────────────────┤
0 ms               Curr_End                            Next_Start            Next_End
                       │                                  │
                       └───► [ Adaptive Synchronisation ] ◄──┘
                             • Spatial gap compensation (X jump)
                             • Character progression density
                             • Fade-out duration deduction
```

For every line, the node evaluates the following.

#### 1. Base progression of the current line ($P_{2,\text{curr}}$)
Computed from the element count $C_{\text{curr}}$:
$$P_{2,\text{curr}} = k_{\text{prog}} \cdot \max(0, C_{\text{curr}} - 1) + \Delta_{\text{delay}}$$

#### 2. Gap to the next line ($\Delta_{\text{gap}}$)
$$\Delta_{\text{gap}} = T_{\text{next, start}} - T_{\text{curr, end}}$$

* **Case A (isolated line, or last line with no successor):**
  $$\Delta t_{\text{extra}} = \min\left(M_{\text{max}}, \max(0, P_{2,\text{curr}})\right)$$

* **Case B (overlapping or contiguous lines, $\Delta_{\text{gap}} < \Delta_{\text{delay}}$):**
  $$\Delta t_{\text{extra}} = 0.0\text{ ms}$$

* **Case C (long silence, $\Delta_{\text{gap}} > \text{Threshold}$):**
  The line gets its normal progression, with no bridge to the next phrase:
  $$\Delta t_{\text{extra}} = \min\left(M_{\text{max}}, \max(0, P_{2,\text{curr}})\right)$$

* **Case D (standard bridge, $\Delta_{\text{delay}} \le \Delta_{\text{gap}} \le \text{Threshold}$):**
  The node compares the 2D footprint of both lines, using their glyph ink bounds or typographic boxes ($[X_{\text{min}}, X_{\text{max}}], [Y_{\text{min}}, Y_{\text{max}}]$) and their layout properties (`\pos`, `align`):

  1. **Subcase D.1 — separate screen areas:**
     The lines are not in the same vertical band (for instance a header in `\an8` and a footer in `\an2`, or $|Y_{\text{curr}} - Y_{\text{next}}| > 0.5 \cdot \text{height}$):
     * Character progression is ignored ($P_2 = 0$).
     * The current line is extended only to fill the gap until the next line appears, with its fade-out timed to finish then:
       $$T_{\text{ideal\_end}} = T_{\text{next, start}} - \text{Fade}_{\text{dur}}$$

  2. **Subcase D.2 — same space, shared anchor:**
     Both lines are in the same vertical band and share their horizontal origin or anchor (for example consecutive left-aligned `\an4` lines, right-aligned `\an6` lines, or centred lines replacing the same row, where $X_{\text{next, left}} - X_{\text{curr, right}} \le 0$):
     * The transition time is the average of both lines' progression:
       $$T_{\text{trans}} = \frac{P_{2,\text{curr}} + P_{2,\text{next}}}{2}$$
     * No spatial compensation is added ($\Delta t_{\text{spatial}} = 0.0\text{ ms}$):
       $$T_{\text{ideal\_end}} = T_{\text{next, start}} + T_{\text{trans}} - \text{Fade}_{\text{dur}}$$

  3. **Subcase D.3 — same row, next line further along:**
     Both lines are in the same vertical band and the next line sits further along the reading direction ($X_{\text{next, left}} > X_{\text{curr, right}}$):
     * The horizontal jump is:
       $$\text{Jump} = X_{\text{next, left}} - X_{\text{curr, right}}$$
       $$\Delta t_{\text{spatial}} = \left(\frac{\text{Jump}}{w_{\text{avg}}}\right) \cdot k_{\text{prog}}$$
     * $w_{\text{avg}}$ is sampled from the measured glyph advances (`line.chars` via `FontEngine`).
     * The ideal end time is:
       $$T_{\text{ideal\_end}} = T_{\text{next, start}} + T_{\text{trans}} + \Delta t_{\text{spatial}} - \text{Fade}_{\text{dur}}$$

  Finally, the extra time is capped:
  $$\Delta t_{\text{extra}} = \min\left(M_{\text{max}}, \max(0, T_{\text{ideal\_end}} - T_{\text{curr, end}})\right)$$

### 4.4. Usage
* **Filling gaps in continuous karaoke:** connect `Sync End` to the `End Time` port of `System/Output`. Subtitles stay visible across short pauses and finish fading out just as the next line appears.
* **With `Retime`:** send `Extra ms` into `Offset Out` of `Time/Retime` (in `line` or `postline` mode) to stretch background fx layers (*glow*, concentric outlines, particles) over the extended duration.

### 4.5. Example
Extending the line duration with `Synced` connected to `System/Output`:

```
[Time/Synced: mode=style, fade_dur=300, max_extra=2500] ──► Sync End ──► End Time ──► [System/Output]
```

In the ASS override block:
```
{\pos(line.center, line.bottom - 40)\fad(200, 300)}
```
If the next line starts 1200 ms later, `Synced` extends the end of the current line to $T_{\text{next, start}} - 300$, so the 300 ms fade-out finishes just as the next line appears.

---

## 5. `Time/Middle 1`

Computes a symmetric offset around the centre of the line. Entrance animations can converge from the edges towards the centre, or radiate from the centre outwards.

![Time/Middle 1](img/middle_1.jpg)

### 5.1. Inputs and Properties
1. **`Delay (ms)` (`delay_ms`):** delay in milliseconds per unit step towards or away from the centre. Accepts constants, variables and expressions (default: `30`).

### 5.2. Outputs
1. **`[1.1] Data`:** the offset in milliseconds, computed according to the half the active unit is in.

### 5.3. Model
The $n$ units are split into two halves around the central axis $\frac{n + 1}{2}$. For the active index $i \in \{1, \dots, n\}$:

$$\text{offset} = \begin{cases} 
\Delta_{\text{delay}} \cdot (i - 1) - 200, & \text{if } i \le \frac{n + 1}{2} \\[6pt]
\Delta_{\text{delay}} \cdot (n - i + 0.5) - 200, & \text{if } i > \frac{n + 1}{2}
\end{cases}$$

$$T_{\text{out}} = T_{\text{base}} + \text{offset}$$

* $i$ is the active index ($1 \le i \le n$).
* $n$ is the total unit count (`syl.n` or `char.n`).
* $\Delta_{\text{delay}}$ is the value of `Delay (ms)`.
* $-200\text{ ms}$ is the base lookahead.

Example ($n=4\text{ units}, \Delta=30\text{ ms}$, midpoint $= 2.5$):
* Unit $1$ ($i=1 \le 2.5$): $30 \cdot (1 - 1) - 200 = -200.0\text{ ms}$
* Unit $2$ ($i=2 \le 2.5$): $30 \cdot (2 - 1) - 200 = -170.0\text{ ms}$
* Unit $3$ ($i=3 > 2.5$): $30 \cdot (4 - 3 + 0.5) - 200 = 30 \cdot 1.5 - 200 = -155.0\text{ ms}$
* Unit $4$ ($i=4 > 2.5$): $30 \cdot (4 - 4 + 0.5) - 200 = 30 \cdot 0.5 - 200 = -185.0\text{ ms}$

### 5.4. Example
Connect `Data` to `Offset In (ms)` of `Time/Retime` (in `syl` or `start2syl` mode). The outer edges of the sentence animate first and converge towards the centre (a V or *chevron* entrance):

```
[Time/Middle 1: delay_ms=35] ──► Data ──► Offset In (ms) ──► [Time/Retime: start2syl, accel=0.8]
                                                                  └──► \t Out ──► Tags ──► [System/Output]
```

With `Tags or \t: \fscx100\fscy100\1c&H00FFFF&` and base style `{\an5\fscx0\fscy0\1c&HFFFFFF&}`, a line with 6 characters starts scaling at the outer glyphs ($i=1$ and $i=6$) and moves inwards until it reaches the centre pair ($i=3, 4$).

---

## 6. `Time/Middle 2`

Computes a symmetric offset anchored to the end of the line ($T_{\text{end}}$), so fade-outs and exit transitions work symmetrically towards or away from the centre of the sentence.

![Time/Middle 2](img/middle_2.jpg)

### 6.1. Inputs and Properties
1. **`Delay (ms)` (`delay_ms`):** delay in milliseconds for the symmetric exit sequence (default: `30`).

### 6.2. Outputs
1. **`[1.1] Data`:** the offset in milliseconds, relative to the end of the unit or line.

### 6.3. Model
`Middle 2` reverses the orientation so it is anchored to the end of the event:

$$\text{offset} = \begin{cases} 
\Delta_{\text{delay}} \cdot (i - n - 1) - 200, & \text{if } i \ge \frac{n + 1}{2} \\[6pt]
\Delta_{\text{delay}} \cdot (-i + 0.5) - 200, & \text{if } i < \frac{n + 1}{2}
\end{cases}$$

$$T_{\text{out}} = T_{\text{base}} + \text{offset}$$

Example ($n=4\text{ units}, \Delta=30\text{ ms}$, midpoint $= 2.5$):
* Unit $1$ ($i=1 < 2.5$): $30 \cdot (-1 + 0.5) - 200 = 30 \cdot (-0.5) - 200 = -215.0\text{ ms}$
* Unit $2$ ($i=2 < 2.5$): $30 \cdot (-2 + 0.5) - 200 = 30 \cdot (-1.5) - 200 = -245.0\text{ ms}$
* Unit $3$ ($i=3 \ge 2.5$): $30 \cdot (3 - 4 - 1) - 200 = 30 \cdot (-2) - 200 = -260.0\text{ ms}$
* Unit $4$ ($i=4 \ge 2.5$): $30 \cdot (4 - 4 - 1) - 200 = 30 \cdot (-1) - 200 = -230.0\text{ ms}$

### 6.4. Example
Connect `Data` to `Offset Out (ms)` of a `Time/Retime` node in `postsyl` mode, for dissolves or falling particles where the central characters vanish before or after the outer ones (a mirrored curtain exit):

```
[Time/Middle 2: delay_ms=40] ──► Data ──► Offset Out (ms) ──► [Time/Retime: postsyl]
                                                                   └──► \t Out ──► Tags ──► [System/Output]
```

With `Tags or \t: \alpha&HFF&`, the centre characters finish singing and start fading immediately, while the outer ones stay visible longer, like a curtain opening.

---

## 7. `Time/Loop 1`

Generates stepped or symmetric offsets for the iterations of a primary `Loops/MaxLoop` sub-loop (normal or FBF mode). It compares the local iteration index $j$ (`fx_i`) with the total repetitions $\text{maxj}$ (`fx_n`).

![Time/Loop 1](img/loop_1.jpg)

### 7.1. Mode

**`[2.1] Mode` (`mode`):** the distribution of offsets over the $j$ iterations:

| Mode (`mode`) | Offset Equation ($\text{offset}$) | Behaviour |
| :--- | :--- | :--- |
| `leadin` (Default) | $\Delta \cdot (j - 1) - 200$ | **Cascade:** each sub-layer $j$ starts after the previous one, with lookahead. |
| `leadout` | $\Delta \cdot (j - \text{maxj} - 1) + 200$ | **Stepped lead-out:** sub-layers end one after another after the event. |
| `middle1` | $\begin{cases} \Delta \cdot (j - 1) - 200, & j \le \frac{\text{maxj}+1}{2} \\ \Delta \cdot (\text{maxj} - j + 0.5) - 200, & j > \frac{\text{maxj}+1}{2} \end{cases}$ | **Symmetric lead-in:** layers converge from the outer iterations towards the centre. |
| `middle2` | $\begin{cases} \Delta \cdot (j - \text{maxj} - 1) - 200, & j \ge \frac{\text{maxj}+1}{2} \\ \Delta \cdot (-j + 0.5) - 200, & j < \frac{\text{maxj}+1}{2} \end{cases}$ | **Symmetric lead-out:** symmetric exit centred on the set of iterations. |

### 7.2. Inputs and Properties
1. **`Delay (ms)` (`delay_ms`):** offset step in milliseconds between consecutive sub-loop iterations (default: `30`).

### 7.3. Outputs
1. **`[1.1] Data`:** the offset in milliseconds for the active iteration $j$.

### 7.4. Context Variables
> [!NOTE]
> Unlike `Lead In` or `Middle 1`, which read the syllable/character index $i \in [1, n]$ from the `Main Loop`, `Time/Loop 1` reads the sub-loop context:
> * **$j$ (`fx_i`):** the active repetition index ($1, 2, \dots, \text{maxj}$).
> * **$\text{maxj}$ (`fx_n`):** the repetition limit set in `MaxLoop`.

### 7.5. Example
For ghost and echo trails, chain `Loops/Main Loop` $\to$ `Loops/MaxLoop (5 iterations)` $\to$ `Time/Loop 1 (Mode: leadin, Delay: 40ms)` $\to$ `Time/Retime`. Each of the 5 layers is shifted in time, producing motion trails.

A concrete case, 3 ghost layers trailing the main element:

```
[Loops/MaxLoop: count=3] ──► j ──► (Local context j)
                                         │
[Time/Loop 1: mode=leadin, delay_ms=45] ──► Data ──► Offset In (ms) ──► [Time/Retime: syl]
                                                                            └──► \t Out ──► Tags ──► [System/Output]
```

Combined with per-layer opacity `{\1a(120 + j * 40)}`, each iteration $j \in \{1, 2, 3\}$ is delayed 45 ms relative to the previous layer, forming a trail synchronised with the singing (the opacity evaluates to `\1a&HA0&`, `\1a&HC8&` and `\1a&HF0&`).

---

## 8. `Time/Loop 2`

Same formulas as `Time/Loop 1`, but for **second-level nested sub-loops**: it uses the uppercase iteration variable $J$ and the total $\text{maxJ}$.

![Time/Loop 2](img/loop_2.jpg)

### 8.1. Mode
**`[2.1] Mode` (`mode`):** same options as `Loop 1` (`leadin`, `leadout`, `middle1`, `middle2`).

### 8.2. Inputs and Properties
1. **`Delay (ms)` (`delay_ms`):** delay step in milliseconds between iterations $J$ (default: `30`).

### 8.3. Outputs
1. **`[1.1] Data`:** the offset in milliseconds for the active nested iteration $J$.

### 8.4. Iteration Scopes

| Timing Node | Index Variable | Total | Scope |
| :--- | :---: | :---: | :--- |
| `Lead In` / `Lead Out` / `Middle 1` / `Middle 2` | $i$ (`syl.i`, `char.i`) | $n$ (`syl.n`, `char.n`) | **Main loop (`Main Loop`):** iterates over syllables, characters, words or lines. |
| `Loop 1` | $j$ (`fx_i`) | $\text{maxj}$ (`fx_n`) | **Primary sub-loop (`MaxLoop` level 1):** multi-layer replicas or FBF frames. |
| `Loop 2` | $J$ | $\text{maxJ}$ | **Nested sub-loop (`MaxLoop` level 2):** fractals, nested swarms or compound subsampling. |

### 8.5. Example
For a particle grid where an outer `MaxLoop (X)` contains an inner `MaxLoop (Y)`, use `Time/Loop 1` for the column delay ($j$) and `Time/Loop 2` for the row delay ($J$), and add both outputs in a `Math (add)` node before `Time/Retime`:

```
[Loops/MaxLoop X: cols=4] ──► j
     └──► [Loops/MaxLoop Y: rows=3] ──► J
               │
[Time/Loop 1: leadin, delay=30] ──► Data ──► In 1 ──► [Basics/Math: add]
[Time/Loop 2: leadin, delay=60] ──► Data ──► In 2 ─────────┘   │
                                                               └──► Offset In (ms) ──► [Time/Retime: syl]
```

The summed delays make a diagonal wavefront ($30 \cdot (j-1) + 60 \cdot (J-1)$ ms) that triggers each cell of the grid in turn.

---

## 9. `Time/Parse ASS Time`

Converts an ASS timestamp (`H:MM:SS.CS` or `H:MM:SS.MMM`) into an integer number of milliseconds.

![Time/Parse ASS Time](img/parse_ass_time.jpg)

### 9.1. Inputs and Properties
1. **`ASS Time` (`ass_time`):** the timestamp to parse (e.g. `"0:01:23.45"` or `"1:12:05.120"`). If the port is unlinked and the field is blank, the node uses the start time of the active unit (`unit.start_str` $\to$ `line.start_str`) (default: `"0:00:00.00"`).

### 9.2. Outputs
1. **`[1.1] Time (ms)`:** the total as an integer number of milliseconds.

### 9.3. Model
For a timestamp with hours $H$, minutes $M$, seconds $S$ and centiseconds $CS$:

$$T_{\text{ms}} = (3600 \cdot H + 60 \cdot M + S) \cdot 1000 + CS \cdot 10$$

Example:
$$\text{"0:01:23.45"} \implies (0 + 60 + 23) \cdot 1000 + 45 \cdot 10 = 83000 + 450 = 83450\text{ ms}$$

### 9.4. Example
Decode raw timestamps to do arithmetic with `Basics/Math` or `Time/Offset`, then re-encode with `Time/Format ASS Time` or send them to `System/Output`. Here a fixed timecode is advanced by 500 ms:

```
[Time/Parse ASS Time: ass_time="0:01:15.50"] ──► Time (ms) ──► In 1 ──► [Basics/Math: add, in2=500]
                                                                              └──► In 1 ──► [Time/Format ASS Time]
                                                                                                  └──► ASS Time ──► "0:01:16.00"
```
The decoded value (75500 ms) becomes 76000 ms and is re-encoded in ASS format with no loss of precision.

---

## 10. `Time/Format ASS Time`

Converts a number of milliseconds into the ASS timestamp string (`H:MM:SS.CS`).

![Time/Format ASS Time](img/format_ass_time.jpg)

### 10.1. Inputs and Properties
1. **`Time (ms)` (`time`):** value in milliseconds (integer, float or evaluable expression). If the port is unlinked and the field is empty, it uses the start time of the active syllable or line (`unit.start_time` $\to$ `line.start_time`) (default: `"0"`).

### 10.2. Outputs
1. **`[1.1] ASS Time`:** zero-padded string in Aegisub / libass syntax, `H:MM:SS.CS` (2-digit centiseconds).

### 10.3. Model
From the total milliseconds $T_{\text{ms}}$:

$$H = \left\lfloor \frac{T_{\text{ms}}}{3600000} \right\rfloor$$
$$M = \left\lfloor \frac{T_{\text{ms}} \bmod 3600000}{60000} \right\rfloor$$
$$S = \left\lfloor \frac{T_{\text{ms}} \bmod 60000}{1000} \right\rfloor$$
$$CS = \left\lfloor \frac{T_{\text{ms}} \bmod 1000}{10} \right\rfloor$$

$$\text{ASS Time} = H : \text{pad}_2(M) : \text{pad}_2(S) . \text{pad}_2(CS)$$

$\text{pad}_2(x)$ prepends a zero if $x < 10$.

### 10.4. Example
Connect `ASS Time` to custom event builders in `Script Code`, or to dialogue string generators, when exporting multi-track `.ass` files outside the standard output stream. For example, turning a computed delayed time into an ASS timecode:

```
[Time/Offset: base=line.start_time, offset_ms=1200] ──► Time (ms) ──► Time (ms) ──► [Time/Format ASS Time]
                                                                                            └──► ASS Time
```
If `line.start_time` is 10000 ms, `Offset` yields 11200 ms and `Format ASS Time` outputs `"0:00:11.20"`.

---

## 11. `Time/Time to Frame`

Converts a time or duration in milliseconds into a video frame count or index ($f$), using the project's frame rate (*FPS*).

![Time/Time to Frame](img/time_to_frame.jpg)

### 11.1. Modes
1. **`[2.1] Mode` (`mode`):** how the frame number is rounded:
   * `round` (Default): nearest frame ($\lfloor x + 0.5 \rfloor$).
   * `floor`: round down ($\lfloor x \rfloor$), suited to 0-indexed frame indices on the timeline.
   * `ceil`: round up ($\lceil x \rceil$), suited to the total number of frames spanned by a non-zero duration.
2. **`[2.2] Source` (`source`):** where the time comes from:
   * `custom` (Default): the value in the `Time (ms)` port or inline property.
   * `start`: start time of the active unit (`unit.start_time` $\to$ `line.start_time`).
   * `end`: end time (`unit.end_time` $\to$ `line.end_time`).
   * `dur`: duration (`unit.duration` $\to$ `line.duration`).

### 11.2. Inputs and Properties
1. **`Time (ms)` (`time`):** time in milliseconds to convert. Accepts numbers, ASS timestamps `H:MM:SS.CS` and context variables.
2. **`Frame Dur (ms)` (`frame_dur`):** duration of one frame in milliseconds. If unlinked or empty, it uses the video loaded in Aegisub (default $41.708\text{ ms}$, i.e. $23.976\text{ fps}$).

### 11.3. Outputs
1. **`[1.1] Frames (f)`:** the resulting integer frame count.

### 11.4. Model
With frame duration $fd = \frac{1000}{\text{FPS}}$ and resolved time $T$:

$$f_{\text{ceil}} = \left\lceil \frac{T}{fd} \right\rceil, \quad f_{\text{floor}} = \left\lfloor \frac{T}{fd} \right\rfloor, \quad f_{\text{round}} = \left\lfloor \frac{T}{fd} + 0.5 \right\rfloor$$

Frame durations by FPS:

| Frame Rate (FPS) | Frame Duration ($fd$) | Frames for $1000\text{ ms}$ (Ceil) |
| :---: | :---: | :---: |
| **$23.976\text{ fps}$** | $\approx 41.7083\text{ ms}$ | $24\text{ frames}$ |
| **$24.000\text{ fps}$** | $\approx 41.6667\text{ ms}$ | $24\text{ frames}$ |
| **$29.970\text{ fps}$** | $\approx 33.3667\text{ ms}$ | $30\text{ frames}$ |
| **$30.000\text{ fps}$** | $\approx 33.3333\text{ ms}$ | $30\text{ frames}$ |
| **$60.000\text{ fps}$** | $\approx 16.6667\text{ ms}$ | $60\text{ frames}$ |

### 11.5. Example
Connect `Time to Frame` (with `Source: dur` and `Mode: ceil`) to the `Total` port or repetitions property of `Loops/MaxLoop (fbf)`, so the loop iterates exactly as many times as the syllable spans video frames. At 23.976 fps:

```
[Time/Time to Frame: source=dur, mode=ceil] ──► Frames (f) ──► Count / Reps ──► [Loops/MaxLoop: fbf]
```
For a 450 ms syllable with $fd \approx 41.708$ ms:
$$\left\lceil \frac{450}{41.708} \right\rceil = \lceil 10.789 \rceil = 11\text{ frames}$$
`MaxLoop` iterates exactly 11 times, covering the whole syllable with no missing or extra frames.

---

## 12. `Time/Frame to Time`

Multiplies a frame number or loop counter ($f$, $j$, $J$, $i$) by the frame duration to get the time in milliseconds, as an ASS timecode, or in seconds.

![Time/Frame to Time](img/frame_to_time.jpg)

### 12.1. Modes
1. **`[2.1] Format` (`format`):** format of the main output `[1.1] Time`:
   * `ms` (Default): milliseconds rounded to two decimal places (e.g. `2000.0`).
   * `hms`: string in ASS timecode syntax (e.g. `"0:00:02.00"`).
   * `sec`: seconds as a float with three decimal places (e.g. `2.000`).
2. **`[2.2] Source` (`source`):** where the frame index comes from:
   * `custom` (Default): the value in the `Frames (f)` port or inline property `frames`.
   * `iterator`: a custom iteration variable named in `iter_name` (e.g. `k`, `step_i`, or expressions like `k * 2`).
   * `j`: the active sub-loop counter `j` (`fx_i`).
   * `J`: the active nested sub-loop counter `J`.
   * `i`: the unit's sequential index `unit.i`.

### 12.2. Inputs and Properties
1. **`Frames (f)` (`frames`):** frame count or index, used when `Source` is `custom` (default: `1`).
2. **`Frame Dur (ms)` (`frame_dur`):** frame duration in milliseconds ($fd$). If omitted, it is inferred from the video ($41.708\text{ ms}$).

### 12.3. Outputs
1. **`[1.1] Time`:** the converted time in the format chosen in `Format` (`ms`, `hms` or `sec`).
2. **`[1.2] ASS Time`:** **always** the timecode in ASS format (`0:00:00.00`), whatever `Format` is set to.

### 12.4. Model
For frame number $f$ and frame duration $fd$:

$$T_{\text{ms}} = f \cdot fd$$

* If `Format` is `ms`: $T_{\text{out}} = \text{round}(T_{\text{ms}}, 2)$
* If `Format` is `sec`: $T_{\text{out}} = \text{round}\left(\frac{T_{\text{ms}}}{1000}, 3\right)$
* If `Format` is `hms`: $T_{\text{out}} = \text{format\_time}(T_{\text{ms}})$

### 12.5. Example
Inside a `Loops/MaxLoop (fbf)` loop, use `Frame to Time` with `Source: j` to get the time elapsed at each frame. The output can feed `Base (ms)` of `Time/Offset`, or the interpolation factor $t$ in Bézier curves and vector deformations:

```
[Loops/MaxLoop: fbf] ──► Context j
                              │
[Time/Frame to Time: source=j, format=ms] ──► Time ──► Base (ms) ──► [Time/Offset: offset_ms=syl.start_time]
                                                                           └──► Time (ms) ──► Start Time ──► [System/Output]
```
Each generated FBF line gets its absolute video start time ($T = T_{\text{syl\_start}} + j \cdot fd$), so animations are locked to frames in Aegisub.

---

## 13. `Time/Ipol`

Splits a total duration ($D_{\text{ms}}$) into an ordered sequence of sub-intervals $[t_0, t_1], [t_1, t_2], \dots$ and applies a power acceleration curve (`accel`) across a list of keyframes or control points.

![Time/Ipol](img/ipol.jpg)

### 13.1. Inputs and Properties
1. **`Duration (ms)` (`dur_ms`):** total duration to subdivide, in milliseconds. If empty or unlinked, it uses the active unit's duration (`unit.duration` $\to 1000\text{ ms}$) (default: `"syl.duration"`).
2. **`Points / Values` (`points`):** comma-separated scalar values that define the stages or keyframes (e.g. `"0, 100"` for $1$ segment; `"0, 50, 100"` for $2$ segments; `"0, 20, 80, 100"` for $3$ segments) (default: `"0, 100"`).
3. **`Acceleration` (`accel`):** curvature exponent, any decimal above zero (default: `1.0`):
   * $\text{accel} = 1.0$: linear interpolation (evenly spaced stages).
   * $\text{accel} > 1.0$: *ease-in* (slow start, accelerating towards the end).
   * $\text{accel} < 1.0$: *ease-out* (fast start, decelerating).

### 13.2. Outputs
1. **`[1.1] Data`:** string of the calculated sub-intervals in brackets, separated by commas (e.g. `"[0.0, 500.0], [500.0, 1000.0]"`).

### 13.3. Model
For a list of $M$ control points $\{p_0, p_1, \dots, p_M\}$, the number of segments is $K = M - 1$.

For each boundary index $k \in \{1, \dots, K\}$, the normalised fraction is:

$$u_k = \frac{k}{K}, \quad u_k \in (0.0, 1.0]$$

The end time $t_k$ of segment $k$ uses the acceleration power:

$$t_k = D_{\text{ms}} \cdot (u_k)^{\text{accel}}$$

The sub-intervals are:

$$I_k = [t_{k-1}, t_k] \quad \text{with } t_0 = 0.0\text{ ms}$$

```
t=0 ms                                                  t=D ms
├─────────────────────────┼───────────────────────────────────┤
   Interval 1: [t_0, t_1]        Interval 2: [t_1, t_2]
```

Examples ($D = 1000\text{ ms}$, Points $= \text{"0, 50, 100"}$, $K=2$ segments):
* **Linear ($\text{accel} = 1.0$):**
  * $k=1 \implies u_1 = 0.5 \implies t_1 = 1000 \cdot (0.5)^1 = 500.0\text{ ms} \implies [0.0, 500.0]$
  * $k=2 \implies u_2 = 1.0 \implies t_2 = 1000 \cdot (1.0)^1 = 1000.0\text{ ms} \implies [500.0, 1000.0]$
  * **Output `Data`:** `"[0.0, 500.0], [500.0, 1000.0]"`
* **Quadratic ease-in ($\text{accel} = 2.0$):**
  * $k=1 \implies u_1 = 0.5 \implies t_1 = 1000 \cdot (0.5)^2 = 250.0\text{ ms} \implies [0.0, 250.0]$
  * $k=2 \implies u_2 = 1.0 \implies t_2 = 1000 \cdot (1.0)^2 = 1000.0\text{ ms} \implies [250.0, 1000.0]$
  * **Output `Data`:** `"[0.0, 250.0], [250.0, 1000.0]"`

### 13.4. Example
Send `Data` to animation scripting or multi-phase `\t` builders to split a syllable's singing window into stages, such as a quick scale burst followed by a smooth return. Here a 600 ms syllable is split into two stages with `points="0, 30, 100"` and `accel=1.5`:

```
[Time/Ipol: dur_ms=600, points="0, 30, 100", accel=1.5] ──► Data
```
The node outputs the sub-intervals `[0.0, 212.1], [212.1, 600.0]`.
In the ASS override block:
```
{\t(0, 212, \fscx140\fscy140)\t(212, 600, 0.8, \fscx100\fscy100)}
```
The glyph jumps to 140% over the first 212 ms (impact phase) and eases back to 100% over the remaining 388 ms with a decelerating curve.

---

## 14. `Time/Duration`

Calculates the duration in milliseconds between two timestamps ($T_{\text{start}}$ and $T_{\text{end}}$), or returns the active unit's duration if the inputs are unwired.

![Time/Duration](img/duration.jpg)

### 14.1. Inputs and Properties
1. **`Start Time (ms)` (`start_time`):** start time in milliseconds or a context variable (e.g. `line.start_time`, `syl.start_time`) (default: `"line.start_time"`).
2. **`End Time (ms)` (`end_time`):** end time in milliseconds or a context variable (e.g. `line.end_time`, `syl.end_time`) (default: `"line.end_time"`).

### 14.2. Outputs
1. **`[1.1] Duration (ms)`:** the non-negative difference between both times, as an integer.

### 14.3. Model
For timestamps $T_{\text{start}}$ and $T_{\text{end}}$ evaluated in context:

$$D = \max\left(0, \text{round}(T_{\text{end}} - T_{\text{start}})\right)$$

If both inputs and inline fields are empty, the node falls back to the duration of the active element:

$$D = \text{unit.duration} \implies \text{syl.duration} \implies \text{line.duration} \implies 0\text{ ms}$$

### 14.4. Example
Connect the `Start Time` and `End Time` outputs of `Time/Retime` to `Time/Duration` to get the exact duration of a retimed phase, offsets included, before mapping it into Bézier curves or proportional scales. Here the duration drives a rotation speed:

```
[Time/Retime: syl] ──┬──► Start Time ──► Start Time (ms) ──► [Time/Duration]
                     └──► End Time   ──► End Time (ms)   ───────┘   │
                                                                    └──► Duration (ms) ──► In 1 ──► [Basics/Math: div, in2=100]
                                                                                                           └──► Rot Speed
```

A short 200 ms syllable gives quick `\frz` spins; on a sustained vowel (1200 ms) the rotation stretches over the whole interval without sudden acceleration.

---

## 15. `Time/Offset`

Adds or subtracts a number of milliseconds to a base timestamp. Positive values delay, negative values advance.

![Time/Offset](img/offset.jpg)

### 15.1. Inputs and Properties
1. **`Base (ms)` (`time_in` / `base`):** base timestamp in milliseconds. If unwired, it uses the start time of the active unit (`unit.start_time` $\to$ `line.start_time` $\to 0$).
2. **`Offset (ms)` (`offset_ms` / `offset`):** milliseconds to add to or subtract from the base. Accepts positive numbers, negative numbers and evaluable expressions (default: `"100"`).

### 15.2. Outputs
1. **`[1.1] Time (ms)`:** the timestamp after the offset.

### 15.3. Model
$$T_{\text{out}} = \text{round}(T_{\text{base}} + \Delta_{\text{offset}})$$

Examples:
* **Delay:** $T_{\text{base}} = 1000\text{ ms}, \Delta_{\text{offset}} = 250\text{ ms} \implies T_{\text{out}} = 1250\text{ ms}$
* **Advance:** $T_{\text{base}} = 1000\text{ ms}, \Delta_{\text{offset}} = -150\text{ ms} \implies T_{\text{out}} = 850\text{ ms}$

### 15.4. Usage
* **Shifting a time window:** connect it to the `End Time` output of `Time/Retime` with `Offset: 200` to keep a line on screen longer before passing it to `System/Output`.
* **Animation trigger times:** generate intermediate timestamps to synchronise sparkle bursts from `Functions/Glitter` or particle emissions just before or after a syllable starts.

### 15.5. Example
Keeping a drop shadow or outline visible after the dialogue line ends:

```
[Time/Retime: line] ──► End Time ──► Base (ms) ──► [Time/Offset: offset_ms=250]
                                                           └──► Time (ms) ──► End Time ──► [System/Output]
```

In the ASS override block:
```
{\pos(line.center, line.middle)\bord5\3c&H000000&\t(line.duration, line.duration + 250, \alpha&HFF&)}
```
The outline stays visible 250 ms after the main text disappears, then fades out to black.

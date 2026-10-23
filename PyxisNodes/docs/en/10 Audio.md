# Audio

The **Audio** category provides FFT spectral analysis, energy envelope extraction (RMS and Peak) and ASSdraw vector waveforms generated from the project's audio track. It contains the `Audio/Modulator` and `Audio/Waveform` nodes.

---

## Audio Decoding and Analysis

Pyxis Effector holds audio in contiguous NumPy float32 buffers normalised to $[-1.0, 1.0]$:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AUDIO TRACK RESOLUTION                             │
│  default_audio_source ──► audio_file / video_file ──► Local file / WAV      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PCM DECODING AND BUFFER (AudioData)                      │
│  Sampling Rate (Hz), Channels, float32 Normalisation [-1.0, 1.0]            │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
┌──────────────────────────────────────┐ ┌────────────────────────────────────┐
│        TEMPORAL ENERGY O(1)          │ │          FFT SPECTROMETRY          │
│  Prefix Sums (Cumulative squared sum │ │  Precalculated Hann window,        │
│  array _sq_cumsum)                   │ │  2048-point RFFT, LRU Cache        │
│  ──► Instantaneous RMS & Peak        │ │  ──► 16-64 Logarithmic Bands       │
└──────────────────┬───────────────────┘ └─────────────────┬──────────────────┘
                   │                                       │
                   ▼                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MODULATION AND RENDERING                             │
│  • Audio/Modulator ──► \t(t1,t2,\tag...) Tag Chains or Colour / Alpha Values│
│  • Audio/Waveform  ──► ASSdraw m...l... Vector Paths                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Node `Audio/Modulator` (Spectral ASS Tag Modulator)

Samples the audio energy inside a time window, filters it by frequency band and smooths it with a low-pass filter. The result drives any continuous ASS override tag (`\fscy`, `\fscx`, `\blur`, `\alpha`, `\1c`, `\3c`, `\frz`, `\bord`). It outputs a chain of `\t(t1, t2, \tag...)` transitions, or interpolated values for `Loops/MaxLoop` sub-loops.

![Audio/Modulator](img/modulator.jpg)

> [!NOTE]
> In `custom` mode, the interface shows the extra `[Min Hz]` and `[Max Hz]` fields for the analysis frequency range.

### 1.1. Header Mode Combos
1. **`rms` (`RMS` / `General Volume`):** Root-mean-square energy across the full audible spectrum. Suited to scale pulses, glow and general volume pumping.
2. **`peak` (`Peak` / `Peak Amplitude`):** Instantaneous absolute maximum amplitude. Suited to dry percussive transients such as snares and drum hits.
3. **`bass` (`Bass` / `20-250 Hz`):** Energy in the sub-bass and kick drum band ($20\text{ Hz} \dots 250\text{ Hz}$).
4. **`mids` (`Mids` / `250-4000 Hz`):** Lead vocals, brass and melodic instruments ($250\text{ Hz} \dots 4000\text{ Hz}$).
5. **`highs` (`Highs` / `4-16 kHz`):** Cymbals, hi-hats, sibilants and other high-frequency transients ($4000\text{ Hz} \dots 16000\text{ Hz}$).
6. **`custom` (`Custom` / `Custom Band`):** Enables the `Min Hz` and `Max Hz` cutoffs to isolate a specific frequency range.

### 1.2. Input Ports and Body Properties
Properties are Type A (evaluated expressions) unless marked otherwise.

1. **`Audio Path` (`audio_path`):** Path to the audio or video file. If unwired or empty, Pyxis uses the soundtrack loaded in the Aegisub project. Type C (plain text / filepath).
2. **`Tag` (`tag_name`):** ASS override tag to animate (e.g. `"fscy"`, `"fscx"`, `"blur"`, `"alpha"`, `"1c"`, `"3c"`, `"frz"`, `"bord"`). (Default: `"fscy"`). Type C (literal ASS tag identifier).
3. **`Min Val` (`min_val`):** Value at zero sound energy ($0.0$). Type A / Type C polymorphic.
   * *Scalar:* Baseline number (e.g. `100.0` for scale, `0.0` for blur).
   * *Alpha:* Baseline transparency hex code (e.g. `&HFF&` or `255`).
   * *Colour:* Baseline colour in Web Hex (`#RRGGBB`), ASS (`&HBBGGRR&`), or a comma-separated colour palette.
4. **`Max Val` (`max_val`):** Value at maximum energy ($1.0$). Type A / Type C polymorphic.
5. **`Gain` (`gain`):** Linear gain multiplier ($\ge 0.0$, default: `1.0`). Boosts quiet tracks.
6. **`Step ms` (`step_ms`):** Sampling interval in milliseconds ($\ge 10.0\text{ ms}$, default: `41.7\text{ ms}` $\approx 24\text{ FPS}$).
7. **`Smoothing` (`smoothing`):** Exponential smoothing coefficient $\alpha \in [0.0, 0.95]$ that filters abrupt jitter (Default: `0.2`).
8. **`Min Hz` / `Max Hz` (`min_hz`, `max_hz`):** Low and high frequency cutoffs in `custom` mode (Hz). (Default: `20.0` and `250.0`).
9. **`Start Time` / `End Time` (`start_time`, `end_time`):** Analysis window in milliseconds. If omitted, the interval of the active element is used (`fx.start_time`, `fx.end_time`).

### 1.3. Output Ports
1. **`[1.1] Tags Out`:** ASS tag string with the concatenated temporal transitions:
   $$\text{\textbackslash fscy100\textbackslash t}(0, 42, \text{\textbackslash fscy118})\text{\textbackslash t}(42, 83, \text{\textbackslash fscy152})\dots$$
2. **`[1.2] Current Value`:** Scalar value, ASS colour code or alpha hex at the active timestamp (`frame_time` or `fx.start_time`).
3. **`[1.3] Values Array`:** List of all values sampled across the analysis window.
4. **`[1.4] Average RMS`:** Average root-mean-square energy ($0.0 \dots 1.0$) over the window.

### 1.4. Algorithms

#### 1.4.1. $\mathcal{O}(1)$ RMS Energy (Prefix Sums)
Given the normalised sample array $x \in [-1.0, 1.0]$ and the cumulative squared sum vector $S_k = \sum_{j=0}^{k-1} x_j^2$:

$$\text{RMS}(t_0, t_1) = \sqrt{\frac{S_{\text{end}} - S_{\text{start}}}{\text{end} - \text{start}}} \cdot \text{Gain}$$

Where $\text{start} = \lfloor t_0 \cdot \frac{f_s}{1000} \rfloor$ and $\text{end} = \lfloor t_1 \cdot \frac{f_s}{1000} \rfloor$, with $f_s$ the PCM sample rate in Hz.

#### 1.4.2. Exponential Smoothing (Low-Pass Filter)
For a series of raw energy intensities $I_0, I_1, \dots, I_N$:

$$S_0 = I_0$$
$$S_k = S_{k-1} + (1 - \alpha) \cdot (I_k - S_{k-1}) \quad \forall k \ge 1$$

Where $\alpha \in [0.0, 0.95]$ is the `smoothing` parameter.

#### 1.4.3. Colour Palette Interpolation
If the target tag is a colour tag (`\1c`, `\2c`, `\3c`, `\4c`) and an $M$-colour palette $[C_0, C_1, \dots, C_{M-1}]$ is given:

$$p = \text{intensity} \cdot (M - 1), \quad \text{idx} = \lfloor p \rfloor, \quad f = p - \text{idx}$$
$$C(t) = C_{\text{idx}} + f \cdot (C_{\text{idx}+1} - C_{\text{idx}})$$

### 1.5. Example

Vertical scale `\fscy` driven by the bass and `\blur` driven by peak amplitude:

```
[Audio/Modulator (mode: bass, tag: "fscy", min: 100, max: 155, gain: 1.2)] ──► [In1] ──┐
[Audio/Modulator (mode: peak, tag: "blur", min: 0.5, max: 5.0)]             ──► [In2] ──┼──► [Dynamic Format] ──► Output.Tags
```

* **Template in `Dynamic Format`:**
  ```text
  {\pos(syl.center, syl.middle)%s%s}
  ```
* **Resulting compiled ASS line:**
  ```ass
  Dialogue: 0,0:01:12.40,0:01:15.80,Romaji,,0,0,0,,{\pos(412.5, 680.0)\fscy100\t(0, 42, \fscy148)\t(42, 83, \fscy112)\blur0.5\t(0, 42, \blur4.2)\t(42, 83, \blur1.1)}Ka
  ```

---

## 2. Node `Audio/Waveform` (Vector Oscilloscopes and Spectrograms)

Generates ASSdraw vector paths (`m ... l ...`) from the instantaneous audio signal. It can draw continuous ribbon oscilloscopes, spectral bar equalisers, baseline-filled waves, polar circular visualisers and reactive particle matrices.

![Audio/Waveform](img/waveform.jpg)

### 2.1. Header Mode Combos

```
1. Oscilloscope (Ribbon):            2. FFT Bars (Equaliser):
    ┌──┐   /\   ┌──┐                     ┌─┐   ┌─┐   ┌─┐
────┘  └──/  \──┘  └────                 │ │ ┌─┤ │ ┌─┤ │ ┌─┐
                                         │ │ │ │ │ │ │ │ │ │
3. Filled Wave (Baseline):           4. Radial (Polar Ring):
     /\     /\                                 ● ─── ●
    /  \   /  \                               /   ●   \
  ─/────\_/────\────────                     ●    |    ●
  ██████████████████████                      \   ●   /
                                               ● ─── ●
```

1. **`oscilloscope` (`Oscillo` / `Continuous Ribbon`):** Continuous ribbon path of uniform thickness (`Thickness`) that follows the waveform over time.
2. **`fftbars` (`Bars` / `Spectrum Bars`):** Equaliser bar chart calculated with an RFFT over frequency bands.
3. **`filledwave` (`Filled` / `Filled Wave`):** Closed polygon joining the wave contour to the bottom baseline.
4. **`radial` (`Radial` / `Circular Visualiser`):** Polar ring where frequencies or amplitudes modulate the outer radius around the centre.
5. **`points` (`Points` / `Particle Cloud`):** Disconnected rectangles centred on each wave sample.

### 2.2. Input Ports and Body Properties
Properties are Type A (evaluated expressions) unless marked otherwise.

1. **`Audio Path` (`audio_path`):** Path to the audio track, or automatic resolution from Aegisub. Type C (plain text / filepath).
2. **`Width` (`width`):** Total bounding box width in pixels (Default: `400.0 px`).
3. **`Height` (`height`):** Maximum graphic height in pixels (Default: `60.0 px`).
4. **`Samples` (`samples`):** Number of time samples or spectral bands ($4 \dots 512$, Default: `32`).
5. **`Gain` (`gain`):** Amplitude scaling factor ($\ge 0.01$, Default: `1.0`).
6. **`Thickness` (`thickness`):** Stroke width in pixels for `oscilloscope` and `points` modes ($\ge 1.0\text{ px}$, Default: `2.0 px`).
7. **`Scale` (`scale`):** Vertical deflection or radial expansion multiplier ($\ge 0.01$, Default: `1.0`).
8. **`Min Hz` / `Max Hz` (`min_hz`, `max_hz`):** Frequency range of the FFT analysis in `fftbars` and `radial` modes ($20\text{ Hz} \dots 16000\text{ Hz}$).
9. **`Start Time` / `End Time` (`start_time`, `end_time`):** Sample extraction window in milliseconds.

### 2.3. Output Ports
1. **`[1.1] Shape Out`:** Single closed ASSdraw path (`m ... l ...`), ready for `System/Output` or for `Shape` nodes.
2. **`[1.2] \pos Tag`:** ASS positioning tag at the geometric centre: `\pos(cx, cy)`.
3. **`[1.3] X Array`:** Horizontal $X$ coordinates of all generated vertices.
4. **`[1.4] Y Array`:** Vertical $Y$ coordinates of all generated vertices.
5. **`[1.5] Bands Array`:** Normalised spectral amplitudes or energies ($0.0 \dots 1.0$) of each band.

### 2.4. Geometry Formulas

#### 2.4.1. `Oscilloscope` (Dual-Polygon Ribbon)
For each time sample $s_i \in [-1.0, 1.0]$ with $i \in [0, N-1]$ and thickness $T$:

$$p_x(i) = \frac{i}{N - 1} \cdot W$$
$$p_y(i) = \frac{H}{2} - s_i \cdot \frac{H}{2} \cdot \text{Scale}$$
$$\text{Top}(i) = \left(p_x(i), p_y(i) - \frac{T}{2}\right), \quad \text{Bottom}(i) = \left(p_x(i), p_y(i) + \frac{T}{2}\right)$$

The path runs along all $\text{Top}$ points from left to right, then returns along the $\text{Bottom}$ points in reverse order:

$$\text{Shape} = \text{m } \text{Top}_0 \text{ l } \text{Top}_1 \dots \text{Top}_{N-1} \text{ l } \text{Bottom}_{N-1} \dots \text{Bottom}_0$$

#### 2.4.2. `Radial` (Polar Projection)
For $N$ samples spread uniformly around the circumference:

$$\theta_i = \frac{2\pi i}{N}, \quad R_i = R_{\text{base}} + \text{val}_i \cdot R_{\max} \cdot \text{Scale}$$
$$P_x(i) = c_x + R_i \cos(\theta_i), \quad P_y(i) = c_y + R_i \sin(\theta_i)$$

$$\text{Shape} = \text{m } P_0 \text{ l } P_1 \dots \text{ l } P_{N-1} \text{ l } P_0$$

#### 2.4.3. `FFT Bars` (Equaliser)
For $N$ logarithmic bands with slot width $W_{\text{slot}} = \frac{W}{N}$ and bar width $W_{\text{bar}} = 0.8 \cdot W_{\text{slot}}$:

$$x_0(i) = i \cdot W_{\text{slot}}, \quad x_1(i) = x_0(i) + W_{\text{bar}}$$
$$h_i = \max(1.0, \min(H, \text{val}_i \cdot H \cdot \text{Scale}))$$
$$y_0 = H, \quad y_1(i) = H - h_i$$

Each bar is written as an independent closed rectangle:

$$\text{Bar}_i = \text{m } x_0(i) \text{ } y_0 \text{ l } x_0(i) \text{ } y_1(i) \text{ l } x_1(i) \text{ } y_1(i) \text{ l } x_1(i) \text{ } y_0$$

### 2.5. Example

A reactive spectral equaliser generated frame by frame (FBF) with `Loops/MaxLoop`:

* **Graph connections:**
  ```
  [Loops/Main Loop (line)] ──► [Loops/MaxLoop (mode: fbf)] ──► [Audio/Waveform (mode: fftbars, samples: 16, width: 320, height: 40)] ──► Output.Tags
  ```
* **Resulting compiled ASS line (frame 1):**
  ```ass
  Dialogue: 0,0:01:12.40,0:01:12.44,Romaji,,0,0,0,,{\an5\pos(640, 680)\p1\1c&H00FFFF&}m 0 40 l 0 18.2 l 16 18.2 l 16 40 m 20 40 l 20 8.5 l 36 8.5 l 36 40
  ```

### 2.6. Combining with Other Nodes

1. **Frame-by-frame sub-loops (*FBF*) with `Loops/MaxLoop`:** Placing `Loops/MaxLoop (fbf)` before `Audio/Waveform` updates `fx.start_time` and `fx.end_time` on every video frame, which gives a reactive oscilloscope with no latency.
2. **Dynamic text clipping (`\clip`):** Connecting `Shape Out` to the `Clip` input of `Basics/MultiTag`, or routing it through `Functions/Clip Gradient`, creates clip masks that reveal karaoke text in sync with the music.
3. **Audio-reactive particles:** Connecting `Shape Out` to the `Path / Origin` input of `Functions/Particles` makes the swarm emit from the crests and transients of the wave.

---

## 3. Comparison of Audio Nodes

| Parameter / Feature | `Audio/Modulator` | `Audio/Waveform` |
| :--- | :--- | :--- |
| **Primary Output Type** | Animated ASS Tag Chains (`\t`) | ASSdraw Vector Paths (`m...l...`) |
| **Analysis Domain** | RMS, Peak, Bass, Mids, Highs, Custom Band | Time Domain (PCM) and Frequency Domain (RFFT) |
| **Available Topologies** | Scalar / Colour / Alpha / `\t` Chains | Oscilloscope, FFT Bars, Filled, Radial, Points |
| **Colour Palette Support** | Yes (continuous RGB/Hex interpolation) | N/A (Pure vector geometry) |
| **FBF Compatibility** | Yes (via `Current Value` [Slot 1.2]) | Native (Generates distinct geometry per frame) |
| **Input Property Typing** | Type A (numerics/expressions), Type C (tags/paths)| Type A (dimensions/frequencies), Type C (paths/modes) |
| **Primary FX Use Case** | Glow, bounce, scale, and colour pulsating to music | Visual equalisers, oscilloscopes, and reactive backdrops |

# Base Environment and Customisation

The **Base Environment** (`preview_base.ass`) is an isolated workspace for previewing and testing effects without using the subtitle script loaded in Aegisub.
This page covers the file's lifecycle in `%APPDATA%`, the temporal clip window, its style structure, and hot-reloading.

---

## 1. Architecture and Preview Modes

The **`System/Previewer`** node has a source toggle with two modes:

* **Active Project Mode (Aegisub Icon):** The player uses the video, audio, styles, and dialogue lines currently loaded in the active Aegisub session.
* **Base Preset Mode (CD Disc Icon):** The player detaches from Aegisub and renders the graph output over `preview_base.ass`, a fixed and reproducible test environment.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             PREVIEW MODES MATRIX                            │
├──────────────────────────────────────┬──────────────────────────────────────┤
│                                      │                                      │
│                 ┌────────────────────┴────────────────────┐                 │
│                 ▼                                         ▼                 │
│  ┌──────────────────────────────┐       ┌────────────────────────────────┐  │
│  │   AEGISUB MODE (Aegi Icon)   │       │    BASE MODE (CD Disc Icon)    │  │
│  │   • Active production script │       │    • Isolated %APPDATA% sandbox│  │
│  │   • Session video and audio  │       │    • Fixed laboratory media    │  │
│  │   • Live episode dialogues   │       │    • Controlled test template  │  │
│  └──────────────────────────────┘       └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Lifecycle and Persistence in `%APPDATA%`

### 2.1. Filesystem Location
The base script lives in the Windows user profile configuration directory:

```
%APPDATA%\PyxisNodes\preview_base.ass
```

*(Standard path: `C:\Users\<User>\AppData\Roaming\PyxisNodes\preview_base.ass`)*.

### 2.2. Zero-Overwrite Policy
Pyxis Effector never overwrites your copy of the file:
1. **First run:** If the file does not exist in `%APPDATA%\PyxisNodes\`, the engine copies the default template bundled with the installation.
2. **Upgrades:** Once created, **Pyxis never overwrites or deletes this file**. Your custom styles, canvas dimensions, video links, and test phrases belong to you and persist across releases.

### 2.3. SHA-256 Hash Invalidation (Hot-Reloading)
You do not need to restart the application or recreate the `System/Previewer` node after editing the base environment. The backend checks the file's hash instead:
* On each preview compilation request, the engine calculates the `SHA-256` checksum of `preview_base.ass` on disk.
* When you edit and save `preview_base.ass` in Aegisub or an external text editor, the changed hash invalidates the in-memory cache (`_cached_preview_base_info`).
* The player then updates the canvas resolution, frame rate, audio track, and typographic geometry immediately.

---

## 3. Temporal Clip Window

Pyxis does not limit playback to the syllable duration in the base script. It adds a **lead-in / lead-out buffer** so you can see entry and exit transitions in full.

### 3.1. Formulas

Let $\mathcal{D} = \{d_1, d_2, \dots, d_m\}$ be the set of dialogue lines in `preview_base.ass`, where each line has a start timestamp $t_{\text{start}}(d_i)$ and end timestamp $t_{\text{end}}(d_i)$ in milliseconds:

$$t_{\text{min}} = \min_{d \in \mathcal{D}} \big(t_{\text{start}}(d)\big)$$

$$t_{\text{max}} = \max_{d \in \mathcal{D}} \big(t_{\text{end}}(d)\big)$$

From these bounds, the engine computes the clip interval in seconds:

$$t_{\text{clip\_start}} = \max\left(0.0, \; \frac{t_{\text{min}} - 2000}{1000.0}\right)$$

$$t_{\text{clip\_end}} = \frac{t_{\text{max}} + 2000}{1000.0}$$

$$T_{\text{clip\_dur}} = \max\left(2.0, \; t_{\text{clip\_end}} - t_{\text{clip\_start}}\right)$$

$$t_{\text{clip\_start\_ms}} = \lfloor t_{\text{clip\_start}} \times 1000 \rfloor$$

### 3.2. What the 2000 ms Cushion Is For
* **`Time/Lead In` nodes:** Animations that start before the syllable (off-screen approaches, exponential velocity curves `accel`, progressive reveals) get up to 2000 ms of lead time.
* **`Time/Lead Out` nodes:** Transitions after the syllable (`\fad`, particle dispersion, alpha dissolve) get 2000 ms of trailing playback before the timeline loops.
* **Scrubber:** The `Previewer` scrubber maps relative position $00:00$ to $t_{\text{clip\_start\_ms}}$, so there is no dead time at the start of the timeline.

---

## 4. Structure of `preview_base.ass`

`preview_base.ass` is a standard ASS (*v4.00+*) file with four sections:

```ini
[Script Info]
; Canvas geometry and coordinate system
Title: Default Aegisub file
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 1000
PlayResY: 260

[Aegisub Project Garbage]
; Reference video and audio bindings
Last Style Storage: Default
Audio File: dummy-audio:silence?sr=44100&bd=16&ch=1&ln=396900000
Video File: ?dummy:23.976000:361:1000:260:150:150:150:c
Video AR Value: 3.846154
Video Zoom Percent: 1.187500
Active Line: 1
Video Position: 120

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,65,&H00FFFFFF,&H000000FF,&H007A3419,&H007A1C42,0,0,0,0,100,100,0,0,1,2,2,2,10,10,100,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,0:00:05.00,0:00:10.00,Default,,0,0,0,,{\k43}Ma{\k65}ry {\k44}te{\k87}nía {\k65}un {\k65}cor{\k44}de{\k43}ri{\k44}to
```

---

## 5. Customisation Guide

### 5.1. Step 1: Set the Canvas Resolution (`PlayResX` / `PlayResY`)
The script resolution defines the coordinate plane for absolute positions and relative anchor offsets:
* **Full HD (1080p):**
  ```ini
  PlayResX: 1920
  PlayResY: 1080
  ```
* **HD (720p):**
  ```ini
  PlayResX: 1280
  PlayResY: 720
  ```
> [!NOTE]
> The WebAssembly renderer (`JASSUB`) and ArtPlayer adapt automatically to the aspect ratio ($\text{AR} = \text{PlayResX} / \text{PlayResY}$) and scale the output to avoid anamorphic distortion.

### 5.2. Step 2: Configure Reference Media
Under `[Aegisub Project Garbage]`, set the test media you want to use:

#### Option A: Synthetic Dummy Video (Recommended)
Starts instantly at 23.976 or 60 FPS and needs no video file on disk:
```ini
Video File: ?dummy:23.976000:40000:1920:1080:26:26:26:
```
* **Syntax:** `?dummy:<FPS>:<FrameCount>:<Width>:<Height>:<R>:<G>:<B>:`
* The colour values `26:26:26:` give a neutral dark grey background that contrasts well with white particles, outline strokes, and glows.

#### Option B: Real Local Video and Audio
To calibrate lip sync, spectral envelope modulation with `Audio/Modulator`, or transient detection in `Audio/Waveform`, point to a local media file:
```ini
Video File: C:\KaraokeResources\test_track_1080p.mp4
Audio File: C:\KaraokeResources\test_track_1080p.mp4
```
> [!TIP]
> If the video file has an embedded audio track, setting `Video File` is enough; Pyxis decodes it and feeds the PCM buffer and spectral analyser automatically.

### 5.3. Step 3: Set the Baseline Style (`[V4+ Styles]`)
Pyxis reads `[V4+ Styles]` and uses the **first defined style** as the reference:
* **`Fontname`:** Font family installed on the system or located in `%APPDATA%\PyxisNodes\fonts\`.
* **`Fontsize`:** Text height in script pixels (e.g. `65` to `80` for 1080p).
* **`PrimaryColour` (`&HAABBGGRR&`):** Main glyph fill colour.
* **`Outline` and `OutlineColour`:** Outline width and colour, used by stroke nodes and concentric border rings.
* **`Alignment`:** Standard ASS alignment (`5` for screen centre, `2` for lower third).

### 5.4. Step 4: Define Test Karaoke Events (`[Events]`)
Use a phrase with varied syllable lengths and glyph shapes:
```ini
Dialogue: 0,0:00:03.00,0:00:09.00,Default,,0,0,0,,{\k45}Kyou{\k40}kai {\k60}no {\k50}Ka{\k55}na{\k70}ta
```
* **Short syllables ($\le 200\text{ ms}$):** Good for checking fast impacts, snap eases, and elastic rebounds.
* **Sustained syllables ($\ge 600\text{ ms}$):** Good for watching continuous oscillators (`Tag Oscillator`) or particle emission trails.
* **Complex glyphs:** Include dense Kanji or letters with enclosed counters (`B`, `P`, `o`, `8`) to check Clipper2 polygon orientation and winding rules.

---

## 6. Reference Template (Full HD 1080p)

A complete `preview_base.ass` for Full HD 1080p at 23.976 FPS with a high-contrast background:

```ini
[Script Info]
; Pyxis Effector - Customised Laboratory Sandbox
Title: Pyxis Sandbox Environment
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1920
PlayResY: 1080

[Aegisub Project Garbage]
Video File: ?dummy:23.976000:40000:1920:1080:24:28:32:
Audio File: ?dummy:23.976000:40000:1920:1080:24:28:32:

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Cinzel Decorative,76,&H00FFFFFF,&H000000FF,&H00141619,&H80000000,1,0,0,0,100,100,1.5,0,1,3.0,1.5,5,40,40,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:03.00,0:00:08.50,Default,,0,0,0,,{\k45}Py{\k35}xis {\k60}Ef{\k50}fec{\k40}tor {\k75}Nodes
```

---

## 7. Recommended Workflows

1. **Sharing templates:**
   * When publishing template graphs, set the base environment to `?dummy:...` so other users can preview your effects without missing-media alerts.
2. **Local fonts:**
   * For custom or display fonts, put your `.ttf` or `.otf` files in `%APPDATA%\PyxisNodes\fonts\`. Pyxis vectorises and renders them locally via FreeType/HarfBuzz and libass, with no system-wide installation.
3. **Factory reset:**
   * To restore the defaults, close Pyxis Effector, delete `%APPDATA%\PyxisNodes\preview_base.ass`, and relaunch; the engine writes a fresh copy.

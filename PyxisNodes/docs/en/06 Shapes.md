# Shapes

The **Shape** category contains nodes that generate, import, transform and slice vector drawings in ASSdraw format (`m`, `l`, `b`, `s`, `p`, `c`) and clipping masks (`\clip`, `\iclip`).

### Contents
* **6.A — Generation, tracing and import:** `Shape/Library` (§1), `Shape/Walker` (§7), `Shape/Stroke` (§8), `Shape/IMG to Shape` (§12).
* **6.B — Meshes, arrays and concentric patterns:** `Shape/Slicer` (§2), `Shape/Concentric Borders` (§6), `Shape/Array` (§11), `Shape/Multi` (§13).
* **6.C — Boolean operations and non-linear transforms:** `Shape/Manipulator` (§3), `Shape/Filter` (§4), `Shape/Transform` (§5), `Shape/Union & Divide` (§9), `Shape/Clipper` (§10).

---

## 1. Node `Shape/Library`

Emits predefined shapes normalised to a $[0, 100]$ bounding box and centred at the local origin `(0, 0)`.

![Shape/Library](img/library.jpg)

### 1.1. Preview card
The node body shows a live preview of the selected shape. Clicking the preview card, double-clicking the node body or clicking the shape pill in the header opens a catalogue of all 80 shapes, which you can browse by category or filter by text.

### 1.2. Shape catalogue (`shape`)
The 80 shapes are grouped into 10 categories, each identified by a lowercase name:
* **`shapes` (9):** `circle`, `triangle`, `rectangle`, `circangle`, `pixel`, `pentagon`, `hexagon`, `octagon`, `diamond`.
* **`hearts` (3):** `heart`, `heart2t`, `heartb`.
* **`shines` (4):** `shine1t`, `shine2t`, `shine3t`, `shine4t`.
* **`specials` (5):** `clover`, `feather`, `feather2`, `gear`, `bubble`.
* **`music` (4):** `note1t`, `note2t`, `note3t`, `note4t`.
* **`stars` (11):** `star`, `star1t`, `star2t`, `star3t`, `star4t`, `star5t`, `star6t`, `star7t`, `star8t`, `star9t`, `star10t`.
* **`sakura` (8):** `sakura`, `sakura1t`, `sakura2t`, `sakura3t`, `sakura4t`, `sakura5t`, `sakura6t`, `sakura7t`.
* **`snow` (3):** `snowflake1t`, `snowflake2t`, `snowflake3t`.
* **`flowers` (29):** `flower1t` to `flower29t` (daisies, chrysanthemums, sunflowers, mandalas and multilayered flowers).
* **`geometry` (4):** `crystal17`, `geometric10`, `diagonal13r`, `diagonal13l`.

### 1.3. Outputs
1. **`[1.1] Shape`:** ASSdraw code centred at `(0, 0)`, ready for `System/Output (Return)` or for other shape nodes (`Stroke`, `Manipulator`, `Slicer`).

### 1.4. Example
* **Star icon with rotation and scale:**
  Connect `Shape` to the `Return` socket of `System/Output`, with `category: stars`, `shape: star`:

  ```
  [Shape/Library: star] ──► Shape ──► Return ──► [System/Output]
  ```

  In a tag node wired to `System/Output (Tags)`:
  ```
  {\p1\pos(syl.center, syl.middle)\frz(i * 45)\fscx75\fscy75\1c&H00FFFF&\bord1\3c&H0055AA&}
  ```
  The shape is drawn over the syllable centre at 75% scale and rotated by $45^\circ \cdot i$.

---

## 2. Node `Shape/Slicer`

Cuts a shape or text glyph into independent pieces using *Clipper2* boolean operations. The node's inputs change with the selected slicing mode.

![Shape/Slicer](img/slicer.jpg)

---

### 2.1. Header
1. **`[1.1] Slicer`:** Node title.
2. **`[1.2] Slicing Mode` (`[Grid 田]`):** Clicking this button opens the mesh gallery (`pyxis-mesh-picker-dialog`).
   * Each of the 23 modes has a card with an SVG icon of its cut pattern (honeycomb for `hex`, triangular lattice for `tri`, isometric cubes for `rhombille`, Bézier waves for `bez`, PCB traces for `circuit`, organic tessellation for `voronoi`, etc.).
   * The modes are grouped into families:
     * **`Standard Grid`:** Uniform 1D/2D rectangular grid (`Grid 1D/2D`).
     * **`Polygonal & Organic`:** `hex`, `tri`, `dia`, `voronoi`, `delaunay`, `kagome`, `rhombille`, `octagon`.
     * **`Technology & Networks`:** `ring`, `jigsaw`, `circuit`, `ray`, `web`.
     * **`Architecture & Walls`:** `brick`, `mondrian`, `ashlar`, `quad`, `pattern`.
     * **`Waves & Art`:** `herringbone`, `truchet`, `scallop`, `bez`.
   * A search bar filters modes by name or description.
   * Picking a mode switches the algorithm, replaces the inputs and properties in the node body (e.g. `Cols/Rows` becomes `Cell Size/Seed/Jitter`) and resizes the node.
3. **`[1.3] Output Mode` (`[Loops]`):** Switches between iterating over the pieces one at a time (`Loops`) and emitting them all at once as a list/array (`Single / Array`).

---

### 2.2. Universal parameters
These apply to every slicing mode:

1. **`[2.1] Shape`:** ASSdraw path or text glyph to slice. If unwired and empty, it takes the shape of the active context (syllable, word or line).
2. **`[2.2] Text Scale`:** Scale factor applied to the shape before slicing.
3. **`[2.3] Pre-Offset`:** Perimeter offset (*dilation / erosion*) applied to the original contours before slicing.
4. **`[2.4] Anchor`:** Sets the local coordinate system of each piece and how `\pos(x,y)` and `\org(x,y)` are injected:
   * **`Piece` (`Pieces`):**
     * **`\pos`:** Moved to the piece's centroid on screen (`pos_x = parent_x + cx`, `pos_y = parent_y + cy`).
     * **`\org`:** `\org(pos_x, pos_y)`, the piece's own centroid.
     * **Path:** Re-centred at the local origin `(0, 0)` with offset `(-cx, -cy)`, so each fragment rotates and scales around its own centre of mass.
   * **`Relative`:**
     * **`\pos`:** Keeps the parent position (`parent_x`, `parent_y`).
     * **`\org`:** `\org(parent_x, parent_y)` at the parent centroid.
     * **Path:** Keeps the original coordinates relative to the parent origin; the piece is not re-centred.
   * **`Parent Org`:**
     * **`\pos`:** Piece centroid (`pos_x = parent_x + cx`, `pos_y = parent_y + cy`).
     * **`\org`:** `\org(parent_x, parent_y)`, forced to the parent origin.
     * **Path:** Re-centred at `(0, 0)`. All fragments rotate in orbit around the centre of the original word or syllable.
   * **`Pos`:**
     * **`\pos`:** Piece centroid (`pos_x = parent_x + cx`, `pos_y = parent_y + cy`).
     * **`\org`:** No `\org` tag is injected (`has_org = False`), so the renderer uses the standard `\an` alignment point.
     * **Path:** Re-centred at `(0, 0)`.
   * **`Absolute`:**
     * **`\pos`:** Keeps the parent coordinates (`parent_x`, `parent_y`).
     * **`\org`:** No `\org` tag is injected (`has_org = False`).
     * **Path:** Screen coordinates are baked into the ASSdraw code with offset `(+parent_x, +parent_y)`.
5. **`[2.5] Out:`:** Format emitted on the `Piece` port:
   * **`Shape`:** Raw ASSdraw code of the fragment (`m ... l ... b ...`).
   * **`\clip`:** Clipping tag `\clip(m ...)`.
   * **`\iclip`:** Inverted clipping tag `\iclip(m ...)`.
6. **`[2.6] Bleed`:** Overlap between adjacent fragments. Each piece is dilated to hide hairline seams between touching pieces.
7. **`[2.7] Order:`:** Iteration order, named after the numpad positions:
   * **`79 (TL->BR)`:** Top-left to bottom-right.
   * **`97 (TR->BL)`:** Top-right to bottom-left.
   * **`13 (BL->TR)`:** Bottom-left to top-right.
   * **`31 (BR->TL)`:** Bottom-right to top-left.
   * **`71 (TL->BL)`:** Column by column from left to right, top to bottom.
   * **`17 (BL->TL)`:** Column by column from left to right, bottom to top.
   * **`39 (BR->TR)`:** Column by column from right to left, bottom to top.
   * **`5 (Centre)`:** From the centroid of the original shape outwards.
8. **`[2.8] s_i, s_n`:** Iteration variables shown in the footer (`s_i` = current piece index $[1 \dots N]$, `s_n` = total number of pieces).

---

### 2.3. Outputs
1. **`[3.1] Piece`:** ASSdraw code or `\clip`/`\iclip` tag of the current piece.
2. **`[3.2] X`:** Horizontal coordinate of the piece centroid.
3. **`[3.3] Y`:** Vertical coordinate of the piece centroid.
4. **`[3.4] Col`:** Column index of the piece in the mesh.
5. **`[3.5] Row`:** Row index of the piece in the mesh.

---

### 2.4. Mode-specific inputs
Every mode also takes the universal parameters from §2.2.

#### 1. `Grid 1D/2D`
* **`Cols`:** Number of horizontal divisions.
* **`Rows`:** Number of vertical divisions.
* **`Angle`:** Tilt of the cutting grid in degrees.
* **`Bleed`:** Overlap between cells.
* **`Accel X` / `Accel Y`:** Non-linearity exponent along the horizontal / vertical axis.

#### 2. `Hex`
* **`Radius`:** Circumscribed radius of the honeycomb hexagons.

#### 3. `Tri`
* **`Radius`:** Half the side length of the equilateral triangles.

#### 4. `Dia` (diamonds)
* **`Radius`:** Major and minor semi-diagonal of the rhombus mesh.

#### 5. `Rings`
* **`Ring Width`:** Radial width in pixels of each concentric ring.

#### 6. `Ray`
* **`Step Angle` / `Rays`:** Angular step in degrees, or number of radial sectors from centre to perimeter.

#### 7. `Voronoi`
* **`Cell Size`:** Average cell size produced by the random site distribution.

#### 8. `Delaunay` (low-poly)
* **`Cell Size`:** Vertex density and spacing of the irregular Delaunay triangulation.

#### 9. `Brick`
* **`Size X` (width) / `Size Y` (height):** Size of each brick in pixels.

#### 10. `Ashlar` (irregular stonework)
* **`Min Width` / `Max Width`:** Random width range of the stone blocks.
* **`Row Height`:** Fixed height of each row.

#### 11. `Jigsaw`
* **`Piece Size`:** Base size of the puzzle pieces, which have Bézier tabs and sockets.

#### 12. `Bez` (Bézier waves)
* **`Wave Size`:** Cell size. Cells are bounded by sinusoidal Bézier curves with random organic perturbation.

#### 13. `Circuit`
* **`Grid Size`:** Pitch of the PCB grid.
* **`Trace Width`:** Width of the conductor traces.
* **`Via Prob`:** Probability of inserting a circular pad.

#### 14. `Truchet`
* **`Tile Size`:** Size of the square tiles that hold the tangent circular arcs.

#### 15. `Pattern` (custom pattern)
* **`Pattern Shape`:** ASSdraw shape used as a repeated cutting stamp.
* **`Size X` / `Size Y`:** Repetition spacing.

#### 16. `Mondrian`
* **`Min Size`:** Smallest rectangle that can still be split.
* **`Chaos`:** Probability of recursive splitting along $X$ and $Y$.

#### 17. `Herringbone`
* **`Length` / `Width`:** Length and width of the blocks, which interlock at $90^\circ$.

#### 18. `Kagome` (trihexagonal)
* **`Radius`:** Radius of the lattice of interlaced triangles and hexagons.

#### 19. `Rhombille`
* **`Radius`:** Radius of the $60^\circ$ rhombi that form the isometric 3D cube pattern.

#### 20. `Octagon`
* **`Radius`:** Size of the octagons, which are paired with small joining squares.

#### 21. `Scallop` (fish scales)
* **`Radius`:** Radius and curvature of the overlapping semicircular scales.

#### 22. `Web` (spiderweb)
* **`Cols` (rings) / `Rows` (rays):** Number of polygonal concentric rings and radial spokes.
* **`Chaos`:** Random irregularity of the nodes.

#### 23. `Quad` (quadtree)
* **`Min Size`:** Smallest cell size in the recursive quadtree partition.
* **`Chaos`:** Splitting probability threshold.

### 2.5. Example
* **Voronoi shatter:**
  Send the syllable outline to `Shape/Slicer` with `mode: voronoi`, `cell_size: 25`, `anchor: pieces`:

  ```
  [System/Input: Syl Shape] ──► Shape ──► [Shape/Slicer: voronoi, anchor=pieces]
                                                ├──► Piece ──► Return ──► [System/Output]
                                                └──► (s_i, s_n in context)
  ```

  In a tag node wired to `System/Output (Tags)`:
  ```
  {\p1\pos(syl.center, syl.middle)\t(0, 350, \frz(s_i * 20)\fscx0\fscy0\alpha&HFF&)}
  ```
  Each piece rotates around its own centroid, with a rotation proportional to `s_i`, and shrinks to nothing. The local anchor keeps the pieces from drifting away from the original drawing origin.

---

## 3. Node `Shape/Manipulator`

Scales, offsets, translates, rotates in 3D, resamples and mirrors a shape. The node body changes with the selected mode.

![Shape/Manipulator](img/manipulator.jpg)

---

### 3.1. Header and output
1. **`[1.1] Shape` (output):** The transformed ASSdraw path.
2. **`[1.2] Mode`:** Selects one of 8 modes (`Scale`, `Borders`, `Deform`, `Position`, `Redraw`, `3D Rotate`, `Reflect`, `Matrix`).

---

### 3.2. Common parameters
1. **`Shape / Text`:** ASSdraw path or text. If unwired, it takes the glyph of the active context (syllable, word or line).
2. **`Factor (t)`:** Progress ($0.0 \to 1.0$) used to animate the transformation.
3. **`Anchor`:** Reference point for the shape:
   * **`center`:** Centres the shape's ink centroid at `(0, 0)`.
   * **`origin`:** Puts the top-left corner of the ink bounding box at `(0, 0)`.
   * **`relative`:** Keeps the path's own origin `(0, 0)` without re-centring on the ink (useful for 1:1 alignment with typographic shapes).
   * **`absolute`:** Moves the geometry to the screen coordinates `(fx.pos_x, fx.pos_y)`.

---

### 3.3. Mode-specific inputs

#### 1. `Scale`
* **`Scale X` / `Scale Y`:** Independent horizontal and vertical scale in percent (default: `100`%).
* **`Factor (t)` / `Anchor`:** Common parameters.

#### 2. `Borders`
Expands or contracts closed contours with a Clipper offset.
* **`Offset (px)` (`offset_border`):** Offset distance in pixels (positive expands, negative contracts; default: `2.0`).
* **`Factor (t)` / `Anchor`:** Common parameters.

#### 3. `Deform`
Applies a directional distortion.
* **`Offset X` / `Offset Y`:** Horizontal and vertical components of the deformation vector.
* **`Def Factor` (`factor`):** Intensity of the distortion in percent (default: `100`%).
* **`Factor (t)` / `Anchor`:** Common parameters.

#### 4. `Position`
Translates the drawing coordinates in $X$ and $Y$ without touching the ASS `\pos` tag.
* **`Offset X` / `Offset Y`:** Horizontal and vertical offsets in pixels.
* **`Factor (t)` / `Anchor`:** Common parameters.

#### 5. `Redraw`
Resamples the vertices of Bézier curves, either to smooth them or to add points for later deformation.
* **`Density / Step` (`density`):** Sampling density (higher values add more interpolated control points; default: `2.0`).
* **`Factor (t)` / `Anchor`:** Common parameters.

#### 6. `3D Rotate`
Rotates the path in 3D with matrices and perspective projection.
* **`Rotate X` (`angle_x`):** Pitch, in degrees around the $X$ axis.
* **`Rotate Y` (`angle_y`):** Yaw, in degrees around the $Y$ axis.
* **`Rotate Z` (`angle_z`):** Roll in the screen plane, in degrees around the $Z$ axis (equivalent to `\frz`).
* **`Factor (t)` / `Anchor`:** Common parameters.

#### 7. `Reflect`
Mirrors the shape across an axis.
* **`Axis`:** `none` keeps the shape unmirrored, `x` flips left-right, `y` flips top-bottom, `xy` flips diagonally.
* **`Offset X` / `Offset Y`:** Displacement of the symmetry axis.
* **`Factor (t)` / `Anchor`:** Common parameters.

#### 8. `Matrix`
Applies all the transformations in a single pass, in this order:
$$\text{Clipper Offset (Offset Border)} \longrightarrow \text{Resampling (Density)} \longrightarrow \text{Scale} \longrightarrow \text{Shear (Skew)} \longrightarrow \text{3D Euler Rotation} \longrightarrow \text{Reflection} \longrightarrow \text{Translation (Offset)}$$

* **`Shape / Text`:** Input ASSdraw path or text.
* **`Factor (t)`:** Global interpolation factor ($0.0 \to 1.0$).
* **`Scale X` / `Scale Y`:** Independent horizontal and vertical scale in percent (default: `100`%).
* **`Skew X` / `Skew Y`:** Shear factors along $X$ and $Y$.
* **`Rotate X` / `Rotate Y` / `Rotate Z`:** Euler rotation angles in degrees on the 3 axes, with perspective projection ($fov$).
* **`Offset X` / `Offset Y`:** Translation in pixels.
* **`Offset Border`:** Clipper contour offset in pixels, applied first (positive expands, negative contracts; default: `0.0`).
* **`Axis`:** Mirror axis (`none`, `x`, `y`, `xy`).
* **`Density`:** Bézier resampling step, applied before the other transformations (default: `0` = disabled; $> 0$ subdivides with a step in px).
* **`Anchor`:** Reference point (`center`, `origin`, `relative`, `absolute`).

---

### 3.4. Example
* **Perspective rotation of a star:**
  Rotate a star from `Shape/Library` around the $Y$ axis (3D yaw) over the syllable time:

  ```
  [Shape/Library: star] ──► Shape ──► Shape / Text ──► [Shape/Manipulator: 3D Rotate, Rotate Y=70]
                                                             └──► Shape ──► Return ──► [System/Output]
  ```

  In a tag node wired to `System/Output (Tags)`:
  ```
  {\p1\pos(syl.center, syl.middle)\1c&H00FFFF&\bord1\3c&H003366&\t(0, syl.dur, \1c&HFF0088&)}
  ```
  The star rotates in 3D around its local centroid with perspective, and its colour changes without moving the syllable anchor.

---

## 4. Node `Shape/Filter`

Changes the vertex coordinates of an ASSdraw path with mathematical expressions, stepped per-subcontour transforms, or random perturbation (*jitter / noise*).

* **Theme colour:** `#0F766E` / `#5B2C6F`

![Shape/Filter](img/filter.jpg)

---

### 4.1. Header modes
A drop-down in the header selects the mode, which determines the inputs and properties shown:
1. **`Vertices`:** Applies expressions to each $(x, y)$ coordinate, using Cartesian, polar and contour-progress variables.
2. **`Group`:** Iterates over each closed subcontour or island (`m ...`) of a compound path, applying cumulative rotation, scale and offset per piece.
3. **`Noise`:** Displaces each vertex randomly within an elliptical or rectangular window, with a seed and optional prior subdivision.

---

### 4.2. Inputs and properties

#### 1. `Vertices` mode
Evaluates algebraic expressions in real time over each vertex $(x_k, y_k)$ of the path. Suitable for ripples, vortices, polar twists, ballistic dispersion and non-linear melting.

1. **`[2.1] Shape / Text` (`shape`):** Base ASSdraw path or text. If unwired, it takes the glyph of the active context (`syl.text` or `line.text`).
2. **`[2.2] Expr X` (`expr_x`):** Expression for the new horizontal position of the vertex (default: `x`).
3. **`[2.3] Expr Y` (`expr_y`):** Expression for the new vertical position of the vertex (default: `y`).
4. **`[2.4] Factor (t)` (`t`):** Interpolation factor ($0.0 \le t \le 1.0$) between the original and the calculated geometry (default: `1.0`).
5. **`[2.5] Subdivs` (`subdivs`):** Subdivision of Bézier curves and straight segments before the expressions are evaluated (default: `0`).

##### Variables available in `Expr X` and `Expr Y`
* **Absolute Cartesian coordinates:**
  * `x`, `y`: Current coordinates of the vertex in local space.
  * `cx`, `cy` (`Cx`, `Cy`): Centre of the shape's bounding box:
    $$cx = \frac{x_{\min} + x_{\max}}{2}, \quad cy = \frac{y_{\min} + y_{\max}}{2}$$
  * `width`, `height`: Size of the bounding box: $W = x_{\max} - x_{\min}$, $H = y_{\max} - y_{\min}$.
  * `minx`, `miny`, `maxx`, `maxy`: Bounding box extents.
* **Normalised coordinates $(0.0 \to 1.0)$:**
  * `mx`, `my` (`Mx`, `My`): Position of the vertex inside the bounding box:
    $$mx = \frac{x - x_{\min}}{\max(10^{-6}, W)}, \quad my = \frac{y - y_{\min}}{\max(10^{-6}, H)}$$
* **Polar metrics and distances:**
  * `do`, `Do`: Distance from the local origin `(0, 0)` to the vertex: $do = \sqrt{x^2 + y^2}$.
  * `dc`, `Dc`: Distance from the centroid `(cx, cy)` to the vertex: $dc = \sqrt{(x - cx)^2 + (y - cy)^2}$.
  * `ao`, `Ao`: Polar angle in degrees ($0^\circ \le ao < 360^\circ$) relative to the origin `(0, 0)`.
  * `ac`, `Ac`: Polar angle in degrees ($0^\circ \le ac < 360^\circ$) relative to the centroid `(cx, cy)`.
* **Sequence indices and contour progress:**
  * `k`, `i`, `Pk`: 1-based index of the vertex ($1 \le k \le N$).
  * `n`, `Pn`: Total number of vertices in the path.
  * `mp`, `Mp`: Progress of the vertex along the perimeter: $mp = \frac{k - 1}{N - 1}$ (or $0.0$ if $N \le 1$).
  * `t`: Current value of `Factor (t)`.
* **Functions:**
  * *Trigonometric:* `sin(rad)`, `cos(rad)`, `tan(rad)`, `asin(v)`, `acos(v)`, `atan2(y, x)`.
  * *Angle conversion and constants:* `rad(deg)` (degrees to radians), `deg(rad)` (radians to degrees), `pi`, `PI`.
  * *Algebra and exponentials:* `sqrt(v)`, `abs(v)`, `min(a, b)`, `max(a, b)`, `exp(v)`, `log(v)`.
  * *Rounding:* `floor(v)`, `ceil(v)`, `round(v)`.

> [!IMPORTANT]
> **Sandbox and fallback:**
> Expressions in `Vertices` mode run in a deterministic sandbox. Random functions such as `Rs()` or `R()` **do not exist** in this scope. If an expression uses an undefined symbol or has a syntax error, the node leaves the vertex unchanged ($x_{\text{final}} = x, y_{\text{final}} = y$) instead of raising an error in the graph. For random motion, use **`Noise`** mode, or a deterministic hash formula based on `k`.

---

#### 2. `Group` mode
Splits the shape into its independent closed subcontours or islands (delimited by `m ...` commands) and applies a cumulative transform to each piece.

1. **`[2.1] Shape / Text` (`shape`):** Compound path (e.g. glyphs such as "i", "j", "!", "?", kanji with several radicals, or shapes already fractured by *Slicer*).
2. **`[2.2] Factor (t)` (`t`):** Global interpolation factor ($0.0 \to 1.0$).
3. **`[2.3] Rotation Step` (`rot_step`):** Rotation added per piece, in degrees (default: `0.0`).
4. **`[2.4] Scale Step` (`scale_step`):** Scale added per piece, in percent (default: `100.0`%).
5. **`[2.5] Offset X` (`offset_x`):** Horizontal displacement added per piece, in pixels (default: `0.0`).
6. **`[2.6] Offset Y` (`offset_y`):** Vertical displacement added per piece, in pixels (default: `0.0`).
7. **`[2.7] Anchor` (`anchor`):** Pivot for rotating and scaling each island (`center`, `origin`, `relative`, `absolute`).

---

#### 3. `Noise` mode
Shifts each vertex by a uniform random amount within an elliptical or rectangular window. Useful for analogue looks such as line boil, chalk, fire jitter, electrical arcs, steam or organic disintegration.

1. **`[2.1] Shape / Text` (`shape`):** Base ASSdraw path.
2. **`[2.2] Radius X` (`radius_x`):** Maximum horizontal displacement in pixels: $\Delta x \in [-R_x, +R_x]$ (default: `5.0`).
3. **`[2.3] Radius Y` (`radius_y`):** Maximum vertical displacement in pixels: $\Delta y \in [-R_y, +R_y]$ (default: `5.0`).
4. **`[2.4] Subdivs` (`subdivs`):** Subdivision of Bézier curves and straight lines before the noise is applied (default: `2.0`).
5. **`[2.5] Seed` (`seed`):** Integer seed of the pseudo-random generator (default: `0`).

---

### 4.3. Outputs
1. **`[1.1] Shape`:** The modified ASSdraw code (`m ... l ... b ...`).

---

### 4.4. How it works

#### 4.4.1. Interpolation in `Vertices` mode
Given an original point $\vec{p} = (x, y)$ and the evaluated result $\vec{p}_{\text{calc}} = (\text{res}_x, \text{res}_y)$, the output is a linear blend:

$$\vec{p}_{\text{final}}(t) = \vec{p} + t \cdot (\vec{p}_{\text{calc}} - \vec{p}) = \begin{pmatrix} x + t \cdot (\text{res}_x - x) \\ y + t \cdot (\text{res}_y - y) \end{pmatrix}$$

With $t \in [0.0, 1.0]$: at $t = 0.0$ the geometry is unchanged and at $t = 1.0$ the calculated deformation is fully applied.

#### 4.4.2. `Subdivs`
Font outlines and primitives often describe a long straight span with just two endpoints (e.g. the stem of an "I" or the edges of a box). Without subdivision, a sine ripple or noise only moves the endpoints and the segment between them stays straight.
* **$\text{Subdivs} = 0$:** Keeps the original vertex count. Good for low-poly, faceted deformations.
* **$\text{Subdivs} \ge 1.0$:** Recursively splits each straight segment and cubic Bézier span into $2^{\text{subdivs}}$ pieces while preserving $C^1$ continuity. With more vertices, wave equations give smooth ripples and `Noise` gives fine-grained organic texture.

#### 4.4.3. `Group` mode
For a path split into $M$ subpieces indexed by $j \in [0, M - 1]$:
$$\theta_j = j \cdot \text{Rot Step} \cdot t$$
$$S_j = \max\left(0.001, \, 1.0 + j \cdot \left(\frac{\text{Scale Step} - 100.0}{100.0}\right) \cdot t\right)$$
$$\Delta x_j = j \cdot \text{Offset X} \cdot t, \quad \Delta y_j = j \cdot \text{Offset Y} \cdot t$$

Each subcontour is scaled and rotated around the pivot set in `Anchor`.

#### 4.4.4. `Noise` mode
Each vertex is shifted by independent uniform random variables:
$$x' = x + \Delta x, \quad \Delta x \sim \mathcal{U}(-R_x, \, +R_x)$$
$$y' = y + \Delta y, \quad \Delta y \sim \mathcal{U}(-R_y, \, +R_y)$$

* **Fixed `Seed`:** A frozen, reproducible jagged outline.
* **Variable `Seed`:** Feeding the frame iterator (`fx_i`, `j`, or a time-based variable from `st`) into `Seed` refreshes the noise every frame, giving the hand-drawn vibrating look (*line boil*).

---

### 4.5. Recipes

#### Recipe 1: Horizontal sine ripple (`Vertices`)
A travelling wave along the horizontal axis; subdivision lets the letter stems bend:
* **`Subdivs`:** `2`
* **`Expr X`:** `x`
* **`Expr Y`:** `y + sin(rad(x * 6 + t * 360)) * 12`

#### Recipe 2: Vortex / polar twist (`Vertices`)
Rotates the vertices around the centroid by an angle proportional to the distance $dc$:
* **`Subdivs`:** `1`
* **`Expr X`:** `cx + dc * cos(rad(ac + dc * 1.5 * t))`
* **`Expr Y`:** `cy - dc * sin(rad(ac + dc * 1.5 * t))`

#### Recipe 3: Deterministic pseudo-noise (`Vertices`)
Random-looking vertex shifts without any random call, using incommensurate sine and cosine frequencies over the vertex index $k$:
* **`Expr X`:** `x + sin(k * 12.9898) * 4 * t`
* **`Expr Y`:** `y + cos(k * 78.2330) * 4 * t`

#### Recipe 4: Line boil / chalk shimmer (`Noise`)
Makes vector text vibrate like chalk or an electrical outline:
* Graph: `Text to Shape` $\to$ `Shape/Filter (Noise)` $\to$ `Output (Return)`
* **`Radius X`:** `3.5`
* **`Radius Y`:** `3.5`
* **`Subdivs`:** `2`
* **`Seed`:** `fx_i` *(updates each frame in an FBF loop)*

---

## 5. Node `Shape/Transform`

Applies non-linear transforms to ASSdraw paths: radial inflation (*Inflate*), skew (*Skew*), corner rounding and bevelling (*Round Corners*), spline bending (*Flexor*), and morphing between two or three shapes (*Distort / Distort2*).

![Shape/Transform](img/transform.jpg)

---

### 5.1. Header and output
1. **`[1.1] Shape` (output):** The transformed ASSdraw path.
2. **`[1.2] Mode`:** Selects one of 6 modes (`Inflate`, `Skew`, `Round Corners`, `Flexor`, `Distort`, `Distort2`).

---

### 5.2. Common parameters and morph alignment
* **`Shape / Text`:** Input path or text.
* **`Factor (t)`:** Progress ($0.0 \to 1.0$) of the transition.
* **`Anchor`:** How the target shape is aligned over the source. The target is scaled proportionally and overlaid on the source, and the bounding box changes smoothly: $W(t) = W_A(1-t) + W_B(t)$ and $H(t) = H_A(1-t) + H_B(t)$.
  * **`center` (default):** Aligns the centroids $(\frac{x_{\min}+x_{\max}}{2}, \frac{y_{\min}+y_{\max}}{2})$ and centres the output at `(0, 0)`. With `\pos(x, y)` or centre alignment (`\an5`), the morph happens concentrically at the centre of the glyph or particle, expanding and contracting symmetrically.
  * **`origin`:** Aligns the top-left corners $(x_{\min}, y_{\min})$ and fixes `(0, 0)` at the top-left of the bounding box. With `\an7`, the transformation grows to the right and downwards and the shared top-left corner does not move.
  * **`absolute`:** Keeps the original glyph's screen position (`fx.pos_x`, `fx.pos_y`), so the morph stays at the subtitle's real location on the canvas.

---

### 5.3. Mode-specific inputs

#### 1. `Inflate`
* **`Ratio`:** Inflation strength (default: `1.0`).
* **`Inflate Mode`:** `Circle` (uniform, spherical) or `Ellipse` (proportional to the bounding box).
* **`Anchor`:** Centre of the expansion/contraction (`center`, `origin`, `absolute`).

#### 2. `Skew`
* **`Angle X` / `Angle Y`:** Horizontal and vertical shear angles in degrees.

#### 3. `Round Corners`
* **`Radius (px)` (`radius`):** Fillet radius or bevel depth in pixels (default: `10.0`).
* **`Corner Mode`:** `Round` (cubic Bézier arcs), `Bevel` (straight chamfer) or `Miter` (extended sharp corner).
* **`Anchor`:** `center`, `origin`, `relative`, `absolute`.

#### 4. `Flexor` / `Bend`
Bends the geometry along a numeric arc or a custom ASSdraw curve.
* **`Factor (t)` / `Bend (t)`:** Bend progress ($0.0 \to 1.0$).
* **`Curve / Angle` (`curve`):** Angle in degrees (e.g. `30`, `-45`) or a full ASSdraw spline (`m ... b ...`) onto which the drawing is projected.
* **`Axis`:** Bending axis (`x` for a horizontal curve, `y` for a vertical one).
* **`Anchor`:** `center`, `origin`, `relative`, `absolute`.

#### 5. `Distort` (2-shape morph)
Morphs the perimeter of the source into the target. Text is converted to vector on the fly.
* **`Shape / Text`:** Source path or text at $t = 0.0$. Text is vectorised automatically with the font and style of the line.
* **`Target Shape`:** Destination path or text glyph at $t = 1.0$.
* **`Energy`:** Elastic modulation of the intermediate Bézier handles ($\vec{p_1}, \vec{p_2}$), $W(t) = \sin(\pi \cdot t)$. It deforms the shape elastically without changing the match at $t = 0$ and $t = 1$ (default: `0.35`).
* **`Step (px)`:** Subdivision step in pixels. If `Step (px)` $> 0.05$, curves and segments are split every $N$ pixels ($\text{steps} = \max(1, \text{round}(L / s_{px}))$), giving uniform perimeter resampling before the vertices are matched (default `0` = adaptive).
* **`Anchor`:** `center`, `origin`, `relative`, `absolute`.

#### 6. `Distort2` (3-stage morph)
Continuous morph from Start ($t=0.0$) through Mid ($t=0.5$) to Target ($t=1.0$).
* **`Shape / Text`:** Initial path or text ($t = 0.0$).
* **`Mid Shape`:** Intermediate shape at $t = 0.5$.
* **`Target Shape`:** Final shape at $t = 1.0$.
* **`Energy`:** Modulation of the Bézier handles (default: `0.35`).
* **`Step (px)`:** Subdivision step in pixels (default: `0`).
* **`Anchor`:** `center`, `origin`, `relative`, `absolute`.

---

### 5.4. Example
* **Syllable to star morph:**
  Morph the syllable outline into a star from `Shape/Library` over the syllable's duration:

  ```
  [System/Input: Syl Shape] ──► Shape / Text ──┐
                                              ├──► [Shape/Transform: Distort, Energy=0.35]
  [Shape/Library: star] ────► Target Shape ───┘          └──► Shape ──► Return ──► [System/Output]
  ```

  Tie `Factor (t)` to the normalised syllable progress and set `System/Output (Tags)` to:
  ```
  {\p1\pos(syl.center, syl.middle)\1c&H00FFFF&\bord1\3c&H000000&\t(0, syl.dur, \1c&H0088FF&)}
  ```
  The syllable outline deforms gradually into the star contour around its local centroid, without moving the anchor.

---

## 6. Node `Shape/Concentric Borders`

Generates outward concentric rings, stepped contours or shockwave ripples from a base shape, using Clipper offset and boolean difference.

![Shape/Concentric Borders](img/concentric_borders.jpg)

---

### 6.1. Header
1. **`[1.1] Concentric Borders`:** Node title.
2. **`[1.2] Vector Output Mode` (`out_mode`):** Button in the top-right corner of the title bar. Sets the format emitted by the `Shape` port:
   * **`Shape`:** Raw ASSdraw code of the ring (`m ... l ... b ...`).
   * **`\clip` (`Clip`):** Clipping tag `\clip(m ...)` in screen coordinates.
   * **`\iclip` (`iClip`):** Inverted clipping tag `\iclip(m ...)`.

---

### 6.2. Inputs and properties
1. **`[2.1] Shape / Text`:** Base path or text. If unwired, it takes the shape of the active context element (syllable, word or line).
2. **`[2.2] Mode: [Hollow / Solid]`:** Button in the second slot of the node body that sets the layer topology:
   * **`Hollow (borders)`:** Every ring is a hollow band of constant width:
     $$\text{Ring}_i = \text{BooleanDifference}(\text{Outer}_i, \text{Inner}_i)$$
   * **`Solid (filled borders)`:** The first layer ($i = 1$) is filled; later layers ($i \ge 2$) are hollow rings around it.
3. **`[2.3] Max Rings` (`loop_count`):** Number of concentric layers (default: `5`). Sets `b_n` and `maxloop`.
4. **`[2.4] Separation (px)` (`separation`):** Dilation per ring. Accepts a single float (`5.0`) or a comma-separated list (`5, 2, 8, 3`) for an alternating rhythm.
5. **`[2.5] Overlap (px)` (`overlap`):** Overlap in pixels between adjacent layers (default: `0.5`), to avoid subpixel anti-aliasing gaps in libass.
6. **`[2.6] Anchor`:** Anchor point and reference coordinate system of the generated geometry (`Center`, `Relative`, `Absolute`, `Piece`).
7. **`[2.7] b_i, b_n`:** Footer iteration variables (`b_i` / `ring_i` = current ring index $[1 \dots N]$, `b_n` / `ring_n` = total rings).

---

### 6.3. Outputs
1. **`[3.1] Shape`:** ASSdraw path or `\clip`/`\iclip` tag of the current ring `b_i`.
2. **`[3.2] \pos`:** `\pos(x,y)` tag placing the ring centroid on the canvas.
3. **`[3.3] Index`:** Current ring index ($1 \dots \text{Max Rings}$).
4. **`[3.4] Total`:** Total number of rings ($b\_n$).

### 6.4. Example
* **Shockwave rings that fade out:**
  Send the syllable outline to `Shape/Concentric Borders` with `loop_count: 5`, `separation: 6`, `mode: hollow`:

  ```
  [System/Input: Syl Shape] ──► Shape / Text ──► [Shape/Concentric Borders: hollow, max=5]
                                                       ├──► Shape ──► Return ──► [System/Output]
                                                       └──► (b_i, b_n in context)
  ```

  In a tag node wired to `System/Output (Tags)`:
  ```
  {\p1\pos(syl.center, syl.middle)\1c&H00FFFF&\bord0\1a&H44&\t(0, 400, \fscx(100 + b_i * 15)\fscy(100 + b_i * 15)\1a&HFF&)}
  ```
  This produces 5 concentric bands, 6 px thick, that expand outward and fade out according to the index `b_i`.

---

## 7. Node `Shape/Walker`

Walks along an ASSdraw path and trims it to the interval $[start\_t, progress]$ of its arc length, for write-on effects. It also outputs the `\pos` tag and the tangent angle `\frz` at the leading tip.

![Shape/Walker](img/walker.jpg)

### 7.1. Header modes
1. **Integration mode (`mode`):**
   * `global`: Accumulates the arc length over all subcontours or path segments. The range $[0.0, 1.0]$ covers the whole compound geometry from start to end.
   * `piece`: Evaluates $[0.0, 1.0]$ independently on each `m` subcontour, all at once (e.g. a simultaneous write-on of every glyph in a word).
2. **Direction (`invert`):**
   * `normal`: Follows the vertices in their construction order.
   * `inverted`: Traverses the perimeter from end to start.

### 7.2. Inputs and properties
1. **`[2.1] Shape / Text`:** ASSdraw path or text glyph to walk.
2. **`[2.2] Progress (t)` (`progress`):** End of the trimmed segment ($t_2 \in [0.0, 1.0]$, default: `1.0`).
3. **`[2.3] Start (t)` (`start_t`):** Start of the segment ($t_1 \in [0.0, 1.0]$, default: `0.0`). Use it for travelling-window or trailing-ribbon effects.
4. **`[2.4] Subdivs` (`subdivs`):** Number of linear chords per Bézier segment used to integrate the arc length (default: `30`).
5. **`[2.5] Close Path` (`close_path`):** Boolean (default: `False`). When `True`, each contour that ends unclosed gets a final `l` command back to its initial `m` vertex.

### 7.3. Outputs
1. **`[1.1] Shape Out`:** The ASSdraw path trimmed between $t_1$ and $t_2$.
2. **`[1.2] \pos Tag`:** `\pos(x,y)` tag at the leading tip ($t_2$), in screen coordinates.
3. **`[1.3] Angle (\frz)`:** Angle in degrees of the path tangent at the leading tip.
4. **`[1.4] Length`:** Arc length in pixels of the emitted segment.
5. **`[1.5] Tip X`:** Absolute horizontal coordinate of the tip.
6. **`[1.6] Tip Y`:** Absolute vertical coordinate of the tip.

### 7.4. Algorithm
1. **Arc length:**
   For each cubic Bézier segment $\mathbf{B}(u) = (1-u)^3\mathbf{P}_0 + 3(1-u)^2u\mathbf{P}_1 + 3(1-u)u^2\mathbf{P}_2 + u^3\mathbf{P}_3$, the length is approximated with $S = \text{subdivs}$ chords:
   $$L_{\text{arc}} = \sum_{j=1}^{S} \|\mathbf{B}(j/S) - \mathbf{B}((j-1)/S)\|$$
2. **Trimming:**
   The target distances $s_1 = start\_t \cdot L_{\text{total}}$ and $s_2 = progress \cdot L_{\text{total}}$ locate the cut points, which are evaluated with De Casteljau's subdivision.
3. **Tangent angle and position:**
   $$\theta = \operatorname{atan2}\left(\frac{dy}{du}, \, \frac{dx}{du}\right) \cdot \frac{180}{\pi}$$
   $$\text{pos}_x = x_{\text{parent}} + \text{Tip X}, \quad \text{pos}_y = y_{\text{parent}} + \text{Tip Y}$$

### 7.5. Example
* **Write-on with a leading spark:**
  Feed `Progress (t)` from `Loops/Module` ($0.0 \to 1.0$):

  ```
  Line 1 (growing stroke):
  Route Shape Out to System/Output (Return)
  Tags: {\p1\pos(syl.center, syl.middle)\1c&H00FFFF&\bord0}

  Line 2 (spark anchored at the tip):
  Route Tip X, Tip Y and Angle (\frz) to Variables (or wire \pos Tag directly):
  Tags: {\p1\pos(tip_x, tip_y)\frz(angle)\1c&HFFFFFF&\bord0}
  Return: m -4 -4 l 4 0 l -4 4
  ```

---

## 8. Node `Shape/Stroke`

Turns open lines, skeletons and unfilled paths into closed outline polygons of a given thickness, with control over corner joins and end caps, using *Clipper2*.

![Shape/Stroke](img/stroke.jpg)

### 8.1. Inputs
1. **`Shape / Text`:** ASSdraw path of the open line, curve or text glyph to stroke.
2. **`Width (px)`:** Optional input that sets the stroke thickness in pixels. If unwired, the `width` property is used.

### 8.2. Properties
1. **`[2.1] Width (px)` (`width`):** Total stroke thickness in pixels (default: `4.0`, minimum: $0.01$).
2. **`[2.2] Join Mode` (`join_mode`):** Join type at corners:
   * `round`: Circular arc.
   * `miter`: Pointed join, truncated at the miter limit.
   * `bevel`: Flat chamfer.
3. **`[2.3] Cap Mode` (`cap_mode`):** Cap type at the ends of open lines:
   * `round`: Semicircle of radius $w/2$.
   * `bezier`: Rounded cap built from a smooth cubic Bézier.
   * `flat`: Flat cut perpendicular to the line at the endpoint.
   * `square`: Square cap extending $w/2$ beyond the endpoint.
4. **`[2.4] Miter Limit` (`miter_limit`):** Maximum ratio between miter length and stroke thickness before the join is bevelled (default: `2.0`, minimum: $1.0$).

### 8.3. Outputs
1. **`[1.1] Shape Out`:** The closed ASSdraw polygon (`m ... l ... b ...`) with stroke and caps applied, ready for `\p1`.
2. **`[1.2] Width`:** Stroke width in pixels actually applied.

### 8.4. How it works
Path offsetting is done by Clipper2's offset engine:
* Each open line segment becomes a rectangle of $L \times w$.
* At angle changes, polygonal wedges are inserted according to `join_mode`.
* If the input is already a closed polygon, `Stroke` produces a hollow ribbon of width $w$ centred on the original boundary.

### 8.5. Example
* **Thick outline with round joins on a primitive:**
  Stroke a linear path or a `Shape/Library` primitive:

  ```
  [Shape/Library: triangle] ──► Shape ──► Shape / Text ──► [Shape/Stroke: width=6, join=round] ──► Shape Out ──► Output (Return)
  ```

  In a tag node wired to `System/Output (Tags)`:
  ```
  {\p1\pos(syl.center, syl.middle)\1c&HFF0066&\bord1\3c&H000000&}
  ```
  This gives a hollow triangle with a 6 px thick outline and rounded corners.

---

## 9. Node `Shape/Union & Divide`

Multi-purpose Clipper node. It splits compound paths into real islands by analysing the polygon hierarchy (*PolyTree*), splits plain subpaths, merges shapes with a boolean union, or packs several pieces into a single ASS drawing line by interleaving style tag blocks, with keyframe interpolation.

![Shape/Union & Divide](img/union_&_divide.jpg)

---

### 9.1. Header
1. **`[1.1] Union & Divide`:** Node title.
2. **`[1.2] Mode Selector Button` (`mode`):** Button in the top-right corner of the title bar that switches between the 4 operations:
   * **`[DIVIDE]` (`PolyTree Divide`):** Splits the shape into closed islands, telling apart the inner holes (e.g. in "O", "B", "8" or kanji).
   * **`[UNION]` (`Boolean Union`):** Merges two shapes or lists of paths with a boolean union and removes the inner boundaries.
   * **`[SUB-PATHS]` (`Naive Sub-Paths`):** Splits at each `m ...` command, without computing the hole hierarchy.
   * **`[FUSION]` (`Tag Fusion with Keyframes`):** Packs several islands into a **single ASS dialogue line** (`{\tags1}m... {\tags2}m...`).

---

### 9.2. Mode-specific inputs

#### 1. `[DIVIDE]`
Analyses the nested path with Clipper's polygon tree (*PolyTree*). Unlike splitting at `m` commands, it tells outer contours from islands with inner holes (e.g. "O", "B", "A", "8" or complex kanji) and groups each outer figure with its holes into one closed piece.
* **`[2.1] Shape In`:** Input ASSdraw path or text.
* **`[2.2] Rule:` (`fill_type`):** Winding fill rule (`EvenOdd`, `NonZero`, `Positive`, `Negative`).
* **`[2.3] Clean:` (`clean_self_intersect`):** Automatic cleaning of self-intersecting edges (`Auto (1)`, `Off (0)`).
* **`[2.4] Anchor` (`Pieces`):** `Pieces` (re-centres each piece at its local centroid), `Relative`, `Parent Org`, `Pos`, `Absolute`.
* **`[2.5] Order:` (`order`):** Piece order (`79 (TL->BR)`, `97 (TR->BL)`, `13 (BL->TR)`, `31 (BR->TL)`, `71 (TL->BL)`, `17 (BL->TL)`, `93 (TR->BR)`, `39 (BR->TR)`, `5 (Centre)`, `-5 (Inverse)`, `cw` clockwise, `ccw` anticlockwise, `rand` random, `path` original drawing order, `path_inv` reversed drawing order).

#### 2. `[UNION]`
Combines two overlapping shapes into a single path, merging the masses and removing internal lines.
* **`[2.1] Shape In (A)`:** First shape (`shape`).
* **`[2.1b] Shape In (B)`:** Second shape (`shape_b`) to merge.
* **`[2.2] Rule:` (`fill_type`):** Fill rule (`EvenOdd`, `NonZero`).
* **`[2.3] Clean:` (`clean_self_intersect`):** Automatic cleaning of self-intersections (`Auto (1)`).
* **`[2.4] Anchor` (`Pieces`):** Anchor of the resulting shape.

#### 3. `[SUB-PATHS]`
Splits the drawing at each `m ...` command without computing holes. Suited to open shapes, simple silhouettes and calligraphy lines.
* **`[2.1] Shape In`:** ASSdraw path with several `m` subpaths.
* **`[2.2] Anchor` (`Pieces`):** Anchor of the resulting subpaths.
* **`[2.3] Order:` (`order`):** Subpath order (`79`, `97`, `13`, `31`, `71`, `17`, `93`, `39`, `5`, `-5`, `cw`, `ccw`, `rand`, `path`, `path_inv`).

#### 4. `[FUSION]`
Packs several islands into one ASS line (`{\tags1}m ... {\tags2}m ...`), which reduces the number of lines in the subtitle file. Each piece can be styled separately with tag blocks and colour transitions.
* **`[2.1] Shape In`:** Multi-path shape, text or list of independent shapes to merge.
* **`[2.2] Tag Mode:` (`tagmode`):**
  * **`ipol` (progressive interpolation):** Treats the tag list as *keyframes* and interpolates smoothly from start to end ($0.0 \to 1.0$), for colour gradients (`\1c`), rotations (`\frz`), alphas (`\alpha`) or blur (`\blur`).
  * **`line` (strict 1:1):** Maps tag blocks to pieces in order. Extra pieces receive `{\p1}`; excess tags are discarded.
* **`[2.3] Tags` (`tags`):** Comma-separated or block-separated ASS tags or hexadecimal colours (e.g. `\1c&H0000FF&, \1c&H00FF00&, \1c&HFF0000&` or `#87F337, #61FBC7, #AF6DF6`).
* **`[2.4] Anchor` (`Pieces`):** Spatial anchor.
* **`[2.5] Order:` (`order`):** Order in which the tags are assigned or interpolated over the pieces (`79`, `97`, `13`, `31`, `71`, `17`, `93`, `39`, `5`, `-5`, `cw`, `ccw`, `rand`, `path`, `path_inv`).

---

### 9.3. Outputs and footer
1. **`[3.1] Shape Out`:** The resulting ASSdraw path:
   * In the divide modes (`DIVIDE`, `SUB-PATHS`): the piece of the current iteration `d_i`.
   * In the union and fusion modes (`UNION`, `FUSION`): the single merged shape, or the composite string with interleaved tags.
2. **`[3.2] Out List`:** JSON list of all generated pieces, for batch processing downstream.
3. **`[3.3] BBox Data`:** Bounding box string (`min_x,min_y,max_x,max_y,cx,cy,width,height`).

* **Footer (`d_i, d_n`):** Context variables for the inner loop that `Union & Divide` generates (`d_i` = current piece index $[1 \dots N]$, `d_n` / `d_max` = total number of pieces or islands).

---

### 9.4. Combining with `Concatenate (Zip)`
`Union & Divide (FUSION)` combined with `Concatenate (Zip)` can generate several attributes in parallel (e.g. gradient colours, an oscillating `\blur` and `\fscx` offsets) in one compact ASS event, avoiding layer overlap artefacts.

---

### 9.5. Example
* **Island decomposition with a staggered drop:**
  Split a complex kanji or word into closed islands (`DIVIDE`) and offset the drop of each island in time by `d_i`:

  ```
  [System/Input: Syl Shape] ──► Shape In ──► [Shape/Union & Divide: DIVIDE, order=79, anchor=pieces]
                                                   ├──► Shape Out ──► Return ──► [System/Output]
                                                   └──► (d_i, d_n in context)
  ```

  In a tag node wired to `System/Output (Tags)`:
  ```
  {\p1\pos(syl.center, syl.middle)\t(d_i * 40, d_i * 40 + 300, \frz(d_i * 15)\fscx0\fscy0\alpha&HFF&)}
  ```
  Each island drops and rotates around its own centroid, starting 40 ms after the previous one. Inner holes are preserved (PolyTree) and the overall silhouette stays intact.

---

## 10. Node `Shape/Clipper`

Applies boolean operations (difference, intersection, union, XOR), perimeter offsets and Minkowski sum/difference between two closed or open shapes, using the high-precision Clipper2 engine. Outputs ASSdraw path commands (`Shape Out`) or clipping tags (`\clip`, `\iclip`).

![Shape/Clipper](img/clipper.jpg)

---

### 10.1. Header and operation modes (`mode`)
1. **`[1.1] Clipper`:** Node title.
2. **`[1.2] Mode Selector Button` (`mode`):**
   * **`difference` (`Difference / Subtraction A - B`):** Subtracts `Shape B (Clip)` from `Shape A (Subject)`. Good for punching holes and notches.
   * **`intersection` (`Intersection A ∩ B`):** Keeps only the region where both shapes overlap.
   * **`union` (`Union A ∪ B`):** Merges both shapes into one outline without inner seams.
   * **`xor` (`XOR / Symmetric Difference`):** Keeps the areas that belong to A or B but not to both.
   * **`offset` (`Offset / Perimetric Dilation`):** Expands ($\Delta > 0$) or contracts ($\Delta < 0$) the perimeter of `Shape A` by the distance in `Delta (px)`, with join and end-cap control.
   * **`minkowski_sum` (`Minkowski Sum A ⊕ B`):** Sweeps the outline of `Shape B` along the whole perimeter of `Shape A`, dilating it.
   * **`minkowski_diff` (`Minkowski Difference`):** Computes the morphological difference between the outlines of both shapes.

---

### 10.2. Inputs and controls
1. **`[2.1] Shape A (Subject)`:** Base shape the operation is applied to. If omitted, it uses the geometry of the active context.
2. **`[2.2] Shape B (Clip)`:** Second shape, used as cutting mask, Minkowski pattern or second operand.
3. **`[2.3] Subj Fill:` (`subj_fill`):** Cycle button for the winding fill rule of shape A (`EvenOdd`, `NonZero`, `Positive`, `Negative`).
4. **`[2.4] Clip Fill:` (`clip_fill`):** Cycle button for the winding fill rule of shape B (`EvenOdd`, `NonZero`, `Positive`, `Negative`).
5. **`[2.5] Delta (px):` (`delta`):** Offset distance in pixels for `offset` mode (positive dilates, negative erodes; accepts mathematical expressions).
6. **`[2.6] Join Mode:` (`join_type`):** Cycle button for the corner join style in offset mode (`Round`, `Miter`, `Square`, `Bevel`).
7. **`[2.7] End Mode:` (`end_type`):** Cycle button for the end style of open or closed paths (`Closed Polygon`, `Closed Line`, `Open Round`, `Open Square`, `Open Butt`).
8. **`[2.8] Miter Limit:` (`miter_limit`):** Maximum miter extension before sharp corners are chamfered (default: `2.0`).
9. **`[2.9] Post-Offset:` (`post_offset`):** Extra offset applied to the result of the boolean operations (`difference`, `intersection`, `union`, `xor`, `minkowski`). It expands ($\text{px} > 0$) or contracts ($\text{px} < 0$) the result without chaining a second Clipper node. Accepts mathematical expressions; empty or `0.0` applies no post-offset.
10. **`[2.10] Clean Dist:` (`clean_dist`):** Distance threshold in pixels for removing colinear or degenerate micro-vertices with `CleanPolygons` ($0.0 = \text{disabled}$).
11. **`[2.11] Simple:` (`strictly_simple`):** Toggle (`FALSE` / `TRUE`). Forces strictly simple polygons, without self-intersections or coincident vertices.
12. **`[2.12] Rev Subj:` (`reverse_subj`):** Toggle (`FALSE` / `TRUE`). Reverses the winding direction of the subject shape.
13. **`[2.13] Rev Clip:` (`reverse_clip`):** Toggle (`FALSE` / `TRUE`). Reverses the winding direction of the clipping shape.
14. **`[2.14] Anchor:` (`anchor`):** Drop-down (`center`, `origin`, `relative`, `absolute`). `relative` keeps the native coordinates without re-centring on the ink extremes.
15. **`[2.15] Out Mode:` (`out_mode`):** Cycle button for the output format (`Shape` plain ASSdraw code, `Clip` `\clip(...)` tag, `iClip` `\iclip(...)` tag).

---

### 10.3. Outputs
1. **`[1.1] Shape Out`:** The resulting ASSdraw path or the formatted `{\clip(...)}` / `{\iclip(...)}` tag.
2. **`[1.2] Out List`:** List of the resulting pieces or islands, for chaining or loops.
3. **`[1.3] BBox Data`:** Dictionary with the bounding box metrics (`x1`, `y1`, `x2`, `y2`, `cx`, `cy`, `w`, `h`).

---

### 10.4. Example
* **Star cut-out with a post-offset:**
  Subtract a star (`Shape B`) from the syllable glyph (`Shape A`) in `difference` mode, with a dilating post-offset:

  ```
  [System/Input: Syl Shape] ──► Shape A (Subject) ──┐
                                                    ├──► [Shape/Clipper: difference, Post-Offset=1.5]
  [Shape/Library: star] ────► Shape B (Clip) ─────┘          └──► Shape Out ──► Return ──► [System/Output]
  ```

  In a tag node wired to `System/Output (Tags)`:
  ```
  {\p1\pos(syl.center, syl.middle)\1c&HFFFFFF&\bord2\3c&HFF0055&}
  ```
  The star is punched out of the glyph, and the result is expanded by 1.5 px.

---

## 11. Node `Shape/Array`

Repeats a shape across a regular grid, hexagonal lattice, concentric rings, spiral, random scatter or a guide silhouette. It can iterate per piece (`LOOPS`) or build one combined drawing (`SHAPE`).

![Shape/Array](img/array.jpg)

---

### 11.1. Header buttons
1. **`[1.1] Array`:** Node title.
2. **`[1.2] Output / Execution Mode` (`out_mode`):**
   * **`[LOOPS]`:** Iterates one element at a time through the context variables `a_i` (current index) and `a_n` (total elements). Each cycle emits one particle on the `Piece` port, with its own `\pos(x,y)` tag, and exposes its `\frz` angle, column, row or ring. The footer shows `a_i, a_n`.
   * **`[SHAPE]`:** Merges all instances into a **single ASSdraw stream** (`m ... l ... b ... m ...`) and renames the first output port to `Shape Out`. If a list of tags is wired to the `Tags` port, it interleaves style blocks (`{\tags1}m... {\tags2}m...`). No duplicate lines are generated in the ASS file: it sets `a_i = 1`, `a_n = 1` and shows `Single shape.` in the footer.
3. **`[1.3] Geometric Formation Mode` (`mode`):** Selects one of 6 distributions:
   * **`[GRID]`:** 2D orthogonal grid of Columns $\times$ Rows, with independent spacing in $X$ and $Y$.
   * **`[FORM]`:** Lattice sampled along the vertices or fill of a guide shape/text.
   * **`[RINGS]`:** Concentric rings with radius steps and rotational offsets per ring.
   * **`[SPIRAL]`:** Parametric spiral with revolution and radius controls.
   * **`[SCATTER]`:** Pseudo-random scatter inside a rectangular area, with a reproducible seed.
   * **`[HEX]`:** Honeycomb grid with $60^\circ$ row offsets ($\Delta y = \Delta x \cdot \frac{\sqrt{3}}{2}$).

---

### 11.2. Universal parameters
1. **`[2.1] Particle`:** ASSdraw code of the shape or particle to replicate (e.g. a circle, star, diamond, polygon or vector fragment).
2. **`[2.6] Scale`:** Particle scale multiplier ($1.0 = 100\%$).
3. **`[2.7] Factor (t)` (`t` / `progress`):** Progress ($0.0 \to 1.0$) that sets how many particles are generated or visible, following the spatial order: $\text{Visible} = \text{round}(\text{Total} \cdot t)$. Use it to animate the formation appearing one particle at a time.
4. **`[2.8] Anchor`:**
   * **`Piece` (`Pieces`):** Centres each particle at its own centroid and injects `\pos(x_i, y_i)` and `\org(x_i, y_i)` with the absolute screen position of that cell.
   * **`Relative`:** Draws the particles relative to the parent centroid (`parent_x, parent_y`) without altering the line's base coordinates.
   * **`Parent Org`:** Puts `\org` at the centre of the parent text or syllable, so the whole set can rotate around the word while the pieces are scattered.
   * **`Pos`:** Injects only `\pos(x_i, y_i)` and disables the `\org` override.
   * **`Absolute`:** Projects the coordinates into absolute canvas space and fixes `\pos(0,0)`.
5. **`[2.9] Order:`:** Order of the indices $a\_i = 1 \dots N$ and of the appearance sequence when animating `Factor (t)`:
   * **Numpad:** `79 (TL->BR)` (left to right, top to bottom), `97` (right to left, top to bottom), `13` (left to right, bottom to top), `31` (right to left, bottom to top), `71` (by columns, top to bottom), `17` (by columns, bottom to top).
   * **Centre and radial:** `5` (from the centroid towards the edges), `cw` (clockwise), `ccw` (anticlockwise).
6. **`[2.10] Tags`:** ASS tag string or colours, for fusion with `out_mode = Shape` or for evaluating per instance.
7. **`[2.11] a_i, a_n`:** Footer iteration variables ($a\_i \in [1 \dots N]$).

---

### 11.3. Mode-specific inputs

#### 1. `[GRID]`
* **`[2.2] Cols`:** Number of columns (default: `5`).
* **`[2.3] Rows`:** Number of rows (default: `3`).
* **`[2.4] Spacing X`:** Horizontal gap in pixels between the centres of adjacent cells (default: `0`).
* **`[2.5] Spacing Y`:** Vertical gap in pixels between the centres of adjacent rows (default: `0`).

#### 2. `[FORM]`
* **`[2.2] Formation`:** Guide ASSdraw code or text, used as the silhouette on which the particles are sampled and placed.
* **`[2.3] Spacing`:** Sampling step between adjacent particles.

#### 3. `[RINGS]`
* **`[2.2] Rings`:** Number of concentric rings (default: `3`).
* **`[2.3] Count / Ring`:** Particles per ring (a single number such as `8`, or a comma-separated list such as `6, 12, 18, 24` for increasing density per layer). If empty, the optimal count is calculated from the perimeter of each ring:
  $$N_k = \text{round}\left(\frac{2 \pi \cdot R_k}{\text{Diameter} + \text{Spacing}}\right)$$
* **`[2.4] Radius`:** Radius of the first inner ring in pixels (default: `50.0`).
* **`[2.5] Radius Step`:** Radius increment between consecutive rings (default: `30.0`).
* **`[2.5b] Rotate Step`:** Angular offset in degrees applied to each successive ring, for interlaced or spiral patterns (default: `0.0`).

#### 4. `[SPIRAL]`
* **`[2.2] Count`:** Number of particles along the spiral (default: `20`).
* **`[2.3] Turns`:** Number of full $360^\circ$ revolutions (default: `2.0`).
* **`[2.4] Max Radius`:** Outer radius at the end of the spiral (default: `100.0`).
* **`[2.5] Angle Step`:** Fixed angular increment in degrees between consecutive particles. If `0`, the angle is computed uniformly from the total turns:
  $$\theta_i = t_i \cdot \text{Turns} \cdot 360^\circ \quad \text{where} \quad t_i = \frac{i}{N - 1}$$

#### 5. `[SCATTER]`
* **`[2.2] Count`:** Number of random particles (default: `20`).
* **`[2.3] Width` (`area_width`):** Width of the rectangular scatter area in pixels (default: `150.0`).
* **`[2.4] Height` (`area_height`):** Height of the rectangular scatter area in pixels (default: `100.0`).
* **`[2.5] Seed`:** Deterministic pseudo-random seed. The same seed gives exactly the same distribution on every frame.

#### 6. `[HEX]`
* **`[2.2] Cols`:** Number of columns (default: `5`).
* **`[2.3] Rows`:** Number of rows (default: `3`).
* **`[2.4] Spacing`:** Extra gap between hexagonal cells.

---

### 11.4. Outputs
1. **`[3.1] Piece` / `Shape Out`:** ASSdraw path emitted:
   * In `[LOOPS]`, named **`Piece`**: the ASSdraw code of the particle for iteration $a\_i$.
   * In `[SHAPE]`, named **`Shape Out`**: the combined path with all particles placed and merged.
2. **`[3.2] \pos Tag`:** The `\pos(x, y)` tag of the current particle.
3. **`[3.3] X` / `[3.4] Y`:** Absolute pixel coordinates of the current particle.
4. **`[3.5] Angle (\frz)`:** Tangential or rotation angle in degrees ($\theta$) of the particle (useful for orienting arrows or stars radially in `Rings` or `Spiral`).
5. **`[3.6] Index (a_i)` / `[3.7] Total (a_n)`:** Current index ($1 \dots a\_n$) and total number of particles in the formation.
6. **`[3.8] Col / Ring`:** Index of the active column (in `Grid` / `Hex`) or number of the current ring (in `Rings`).
7. **`[3.9] Row / IdxRing`:** Index of the active row (in `Grid` / `Hex`) or position of the element within its ring (in `Rings`).

### 11.5. Example
* **Ring of stars around the syllable:**
  A ring of 12 stars orbiting the syllable, each oriented along the tangent (`mode: rings, out_mode: loops, rings: 1, count: 12, radius: 45`):

  ```
  [Shape/Library: star] ──► Particle ──► [Shape/Array: rings, count=12, r=45]
                                               ├──► Piece ──► Return ──► [System/Output]
                                               ├──► \pos Tag ──► Tags ──► [System/Output]
                                               └──► Angle (\frz) ──► (angle)
  ```

  In a tag node wired to `System/Output (Tags)`:
  ```
  {\p1\pos(x, y)\frz(angle)\1c&H00FFFF&\bord0\t(0, 300, \fscx150\fscy150\1c&HFF0088&)}
  ```
  Each of the 12 stars sits on the circle and faces outward, following the computed tangent angle.

---

## 12. Node `Shape/IMG to Shape`

Vectorises raster images (PNG, JPG, WebP) or animated GIFs into ASSdraw paths (`m`, `l`, `b`), using the built-in Potrace engine, polygonal approximation (Douglas-Peucker) or gradient edge detection.

![Shape/IMG to Shape](img/img_to_shape.jpg)

### 12.1. Loading and frame navigation
1. **Loading a file:**
   Double-click the preview card or any empty area of the node body to open the system file picker (`select_image_dialog`) and choose a `.png`, `.jpg`, `.jpeg`, `.webp` or `.gif` file. The absolute path is written to `image_path`.
2. **Animated GIF controls:**
   If the file has more than one frame (`total_frames > 1`), transport controls appear:
   * Step buttons `[◀]` and `[▶]` to move frame by frame.
   * A horizontal scrubber to inspect all frames.

### 12.2. Vectorisation engines (`mode`)
1. **`potrace`:** Smooth splines made of cubic Bézier curves (`m`, `l`, `b`), built from an intermediate polygon, corner curvature calculation and subpixel smoothing.
2. **`polygon`:** Strictly linear polygon approximation (`m`, `l`) with the Douglas-Peucker algorithm. Reduces the vertex count while keeping sharp angles.
3. **`borders`:** Contour detection from luminance gradients (Sobel operator).

### 12.3. Binarisation modes (`bin_mode`)
1. **`luminance`:** Compares the greyscale brightness of each pixel with the `threshold` ($0 \dots 255$).
2. **`silhouette` / `alpha`:** Compares the alpha channel of transparent PNG/WebP images with the threshold.
3. **`borders`:** Binarises from the first derivatives of the intensity map.

### 12.4. Inputs and properties
1. **`[2.1] Image Path` (`image_path`):** Absolute or relative path to the image or animated GIF.
2. **`[2.2] Frame (j)` (`frame_idx`):** Index of the frame to decode ($1 \dots \text{Total Frames}$). If left empty, or `"1"` when loading a GIF, it binds to the loop variable `ish_i` or `j` to emit the whole animation.
3. **`[2.3] Threshold` (`threshold`):** Binarisation cut-off ($0 \dots 255$, default: `128`).
4. **`[2.4] Tolerance` (`tolerance`):** Simplification tolerance for intermediate vertices (default: `1.0`).
5. **`[2.5] Smoothing` (`alphamax`):** Potrace maximum corner curvature (default: `1.0`).
6. **`[2.6] Optimization` (`opttoler`):** Tolerance for merging collinear Bézier segments (default: `0.2`).
7. **`[2.7] Scale Out` (`out_scale`):** Scale multiplier for the output path (default: `1.0`).
8. **`[2.8] Width Out` (`out_w`) / `Height Out` (`out_h`):** Forced size in pixels. `0.0` keeps the native size.
9. **`[2.9] Offset X` (`offset_x`) / `Offset Y` (`offset_y`):** Shift in pixels applied to all vertices.
10. **`[2.10] Image Scale` (`img_scale`):** Scale applied to the bitmap before vectorisation.
11. **`[2.11] Binarize Mode` (`bin_mode`):** Segmentation method (`luminance`, `silhouette`, `borders`).
12. **`[2.12] Anchor` (`anchor`):**
    * `center`: Centres the drawing's centroid at `(0, 0)`.
    * `origin`: Puts the top-left corner at `(0, 0)`.
    * `relative`: Keeps the original raster coordinates.
    * `absolute`: Adds the context coordinates `(fx.pos_x, fx.pos_y)` to place it on screen.
13. **`invert` / `invert_img`:** Toggles that invert foreground/background, or invert the colour channels before binarisation.

### 12.5. Outputs
1. **`[1.1] Shape Out`:** ASSdraw path (`m ... l ... b ...`) of the vectorised frame.
2. **`[1.2] Width`:** Width in pixels of the resulting path.
3. **`[1.3] Height`:** Height in pixels of the resulting path.
4. **`[1.4] Points`:** Total number of vertices and Bézier control points.
5. **`[1.5] Shapes Array`:** Array of independent islands for piece-by-piece processing.
6. **`[1.6] Total Frames`:** Number of frames detected in the file. Sets `ish_n` and `ish_max` in the context.

### 12.6. Example
* **Animated GIF played back as vectors:**
  Chain `MaxLoop (fbf)` with `Shape/IMG to Shape`:

  ```
  [MaxLoop: fbf, step_ms=41.7] ──► Loop In ──► [System/Output]
                               ──► Counter ──► Frame (j) ──► [IMG to Shape: logo.gif] ──► Shape Out ──► Output (Return)
  ```

  In a tag node wired to `System/Output (Tags)`:
  ```
  {\p1\pos(syl.center, syl.middle)\1c&HFFFFFF&\bord0}
  ```
  Each video frame draws frame $j$ of the GIF as clean vector graphics, with no pixelation.

---

## 13. Node `Shape/Multi`

Generates nested polygon patterns, concentric grids and other parametric compound shapes.

![Shape/Multi](img/multi.jpg)

### 13.1. Generation engines (`mode`)
The node has 10 algorithms:
1. **`concentric_squares`:** Nested concentric squares with configurable thickness and step.
2. **`diagonal_stripes`:** Diagonal stripe hatching within a width `width` and height `height`.
3. **`concentric_rings`:** Concentric circular rings, or rings derived from a guide silhouette (`base_shape`).
4. **`polygonal_mosaic`:** Regular polygon mosaic defined by the number of sides (`sides`) and concentric layers (`n_layers`).
5. **`multi_shape_mosaic`:** Modular grid of shapes with translation steps (`dx`, `dy`).
6. **`segmented_border`:** Frame made of segments with regular gaps and notches of length `length`.
7. **`radial_rosette`:** Circular rosette of radial petals or sectors (`parts`, `r_out`, `r_in`).
8. **`tunnel_cascade`:** Tunnel of shrinking shapes (`size1`, `size2`), with loops (`loop`) and progressive rotation (`angle`).
9. **`banner`:** Decorative plaque or ribbon with selectable ends (`tip_style`: Arrow, Fold) and fold flaps.
10. **`gear`:** Cogwheel with tooth count (`teeth`), outer radius (`r_out`), inner radius (`r_in`) and central hole (`r_hole`).

### 13.2. Inputs and properties
1. **`Mode` (`mode`):** Selects the algorithm.
2. **`Size` (`size`):** Base size of the outer pattern (default: `100.0`).
3. **`Px Pattern` (`px_pattern`):** Sequence of thicknesses or separations (a number or a comma-separated list).
4. **`Separation` (`separation`):** Spacing, or dilation offset, between neighbouring elements.
5. **`Factor (t)` (`t`):** Progress ($0.0 \to 1.0$) for animating the emergence or scale of the layers.
6. **`Anchor` (`anchor`):**
   * **`center`:** Centres the generated geometry at `(0, 0)`.
   * **`origin`:** Puts the top-left corner of the bounding box at `(0, 0)`.
   * **`relative`:** Keeps the displacement relative to the parent, without re-centring on the ink.
   * **`absolute`:** Places the geometry at the screen coordinates `(fx.pos_x, fx.pos_y)`.
7. **`Tags` (`tags`):** ASS tags or colour attributes to interleave in the emitted code.
8. **`Out Mode` (`out_mode`):** Output format (`Shape`, `\clip`, `\iclip`).
9. **`Loop Mode` (`loop_mode`):** Switches between one combined drawing (`Shape`) and piece-by-piece iteration (`Loops`, which exposes the footer variables `m_i` and `m_n`).

### 13.3. Outputs
1. **`[3.1] Shape`:** Combined ASSdraw code (or the current piece in `Loops` mode).

### 13.4. Example
* **Backdrop plaque behind the dialogue:**
  Configure `Shape/Multi` with `mode: banner`, `width: 260`, `height: 48` and `anchor: center`:

  ```
  [Shape/Multi: banner, w=260, h=48] ──► Shape ──► Return ──► [System/Output]
  ```

  In a tag node wired to `System/Output (Tags)` on an underlay layer (`layer: 0`):
  ```
  {\p1\pos(line.center, line.middle)\1c&H1A1A2E&\bord2\3c&HE94560&}
  ```
  This draws a polygonal banner centred behind the dialogue line, working as a title plaque.

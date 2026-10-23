# Shapes

La categoría **Shape** contiene los nodos que generan, importan, transforman y cortan dibujos vectoriales en formato ASSdraw (`m`, `l`, `b`, `s`, `p`, `c`) y máscaras de recorte (`\clip`, `\iclip`).

### Contenido
* **6.A — Generación, trazado e importación:** `Shape/Library` (§1), `Shape/Walker` (§7), `Shape/Stroke` (§8), `Shape/IMG to Shape` (§12).
* **6.B — Mallas, matrices y patrones concéntricos:** `Shape/Slicer` (§2), `Shape/Concentric Borders` (§6), `Shape/Array` (§11), `Shape/Multi` (§13).
* **6.C — Operaciones booleanas y transformaciones no lineales:** `Shape/Manipulator` (§3), `Shape/Filter` (§4), `Shape/Transform` (§5), `Shape/Union & Divide` (§9), `Shape/Clipper` (§10).

---

## 1. Nodo `Shape/Library`

Emite formas predefinidas normalizadas en una caja de $[0, 100]$ y centradas en el origen local `(0, 0)`.

![Shape/Library](img/library.jpg)

### 1.1. Tarjeta de previsualización
El cuerpo del nodo muestra una previsualización en vivo de la forma seleccionada. Un clic en la tarjeta, un doble clic en el cuerpo del nodo o un clic en la píldora de forma de la cabecera abren el catálogo con las 80 formas, que se puede recorrer por categoría o filtrar por texto.

### 1.2. Catálogo de formas (`shape`)
Las 80 formas se agrupan en 10 categorías, identificadas con nombres en minúsculas:
* **`shapes` (9):** `circle`, `triangle`, `rectangle`, `circangle`, `pixel`, `pentagon`, `hexagon`, `octagon`, `diamond`.
* **`hearts` (3):** `heart`, `heart2t`, `heartb`.
* **`shines` (4):** `shine1t`, `shine2t`, `shine3t`, `shine4t`.
* **`specials` (5):** `clover`, `feather`, `feather2`, `gear`, `bubble`.
* **`music` (4):** `note1t`, `note2t`, `note3t`, `note4t`.
* **`stars` (11):** `star`, `star1t`, `star2t`, `star3t`, `star4t`, `star5t`, `star6t`, `star7t`, `star8t`, `star9t`, `star10t`.
* **`sakura` (8):** `sakura`, `sakura1t`, `sakura2t`, `sakura3t`, `sakura4t`, `sakura5t`, `sakura6t`, `sakura7t`.
* **`snow` (3):** `snowflake1t`, `snowflake2t`, `snowflake3t`.
* **`flowers` (29):** `flower1t` a `flower29t` (margaritas, crisantemos, girasoles, mandalas y flores multicapa).
* **`geometry` (4):** `crystal17`, `geometric10`, `diagonal13r`, `diagonal13l`.

### 1.3. Salidas
1. **`[1.1] Shape`:** Código ASSdraw centrado en `(0, 0)`, listo para `System/Output (Return)` o para otros nodos de formas (`Stroke`, `Manipulator`, `Slicer`).

### 1.4. Ejemplo
* **Icono de estrella con rotación y escala:**
  Conecta `Shape` al puerto `Return` de `System/Output`, con `category: stars`, `shape: star`:

  ```
  [Shape/Library: star] ──► Shape ──► Return ──► [System/Output]
  ```

  En un nodo de etiquetas conectado a `System/Output (Tags)`:
  ```
  {\p1\pos(syl.center, syl.middle)\frz(i * 45)\fscx75\fscy75\1c&H00FFFF&\bord1\3c&H0055AA&}
  ```
  La forma se dibuja sobre el centro de la sílaba al 75% de escala y rotada según el índice $i$.

---

## 2. Nodo `Shape/Slicer`

Corta una forma o glifo de texto en piezas independientes con operaciones booleanas de *Clipper2*. Las entradas del nodo cambian según el modo de corte elegido.

![Shape/Slicer](img/slicer.jpg)

### 2.1. Cabecera
1. **`[1.1] Slicer`:** Título del nodo.
2. **`[1.2] Modo de Corte` (`[Grid 田]`):** Un clic en este botón abre la galería de mallas (`pyxis-mesh-picker-dialog`).
   * Cada uno de los 23 modos tiene una tarjeta con un icono SVG de su patrón de corte (panal para `hex`, celosía triangular para `tri`, cubos isométricos para `rhombille`, ondas Bézier para `bez`, pistas PCB para `circuit`, teselación orgánica para `voronoi`, etc.).
   * Los modos se agrupan en familias:
     * **`Standard Grid`:** Cuadrícula rectangular uniforme 1D/2D (`Grid 1D/2D`).
     * **`Polygonal & Organic`:** `hex`, `tri`, `dia`, `voronoi`, `delaunay`, `kagome`, `rhombille`, `octagon`.
     * **`Technology & Networks`:** `ring`, `jigsaw`, `circuit`, `ray`, `web`.
     * **`Architecture & Walls`:** `brick`, `mondrian`, `ashlar`, `quad`, `pattern`.
     * **`Waves & Art`:** `herringbone`, `truchet`, `scallop`, `bez`.
   * Una barra de búsqueda filtra los modos por nombre o descripción.
   * Al elegir un modo cambia el algoritmo, se reemplazan las entradas y propiedades del cuerpo (por ejemplo, `Cols/Rows` pasa a `Cell Size/Seed/Jitter`) y el nodo se redimensiona.
3. **`[1.3] Modo de Salida` (`[Loops]`):** Alterna entre iterar pieza por pieza (`Loops`) y emitir todas las piezas a la vez como lista/array (`Single / Array`).

---

### 2.2. Parámetros universales
Se aplican a todos los modos de corte:

1. **`[2.1] Shape`:** Forma ASSdraw o glifo de texto a cortar. Si no está conectada y está vacía, toma la forma del contexto activo (sílaba, palabra o línea).
2. **`[2.2] Text Scale`:** Factor de escala aplicado a la forma antes del corte.
3. **`[2.3] Pre-Offset`:** Desplazamiento perimetral (*dilatación / erosión*) aplicado a los contornos originales antes del corte.
4. **`[2.4] Anchor`:** Define el sistema de coordenadas local de cada pieza y cómo se inyectan `\pos(x,y)` y `\org(x,y)`:
   * **`Piece` (`Piezas`):**
     * **`\pos`:** Se mueve al centroide de la pieza en pantalla (`pos_x = parent_x + cx`, `pos_y = parent_y + cy`).
     * **`\org`:** `\org(pos_x, pos_y)`, el centroide de la propia pieza.
     * **Trazado:** Se recentra en el origen local `(0, 0)` con el offset `(-cx, -cy)`, de modo que cada fragmento rota y escala sobre su propio centro de masa.
   * **`Relativo`:**
     * **`\pos`:** Mantiene la posición del padre (`parent_x`, `parent_y`).
     * **`\org`:** `\org(parent_x, parent_y)` en el centroide del padre.
     * **Trazado:** Conserva las coordenadas originales respecto al origen del padre; la pieza no se recentra.
   * **`Parent Org` (`Org Padre`, `parent_org`):**
     * **`\pos`:** Centroide de la pieza (`pos_x = parent_x + cx`, `pos_y = parent_y + cy`).
     * **`\org`:** `\org(parent_x, parent_y)`, forzado al origen del padre.
     * **Trazado:** Se recentra en `(0, 0)`. Todos los fragmentos rotan en órbita alrededor del centro de la palabra o sílaba original.
   * **`Pos`:**
     * **`\pos`:** Centroide de la pieza (`pos_x = parent_x + cx`, `pos_y = parent_y + cy`).
     * **`\org`:** No se inyecta `\org` (`has_org = False`), así que el renderizador usa el punto de alineación `\an` estándar.
     * **Trazado:** Se recentra en `(0, 0)`.
   * **`Absoluto`:**
     * **`\pos`:** Mantiene las coordenadas del padre (`parent_x`, `parent_y`).
     * **`\org`:** No se inyecta `\org` (`has_org = False`).
     * **Trazado:** Las coordenadas de pantalla se incorporan al código ASSdraw con el desplazamiento `(+parent_x, +parent_y)`.
5. **`[2.5] Out:`:** Formato emitido por el puerto `Piece`:
   * **`Shape`:** Código ASSdraw del fragmento (`m ... l ... b ...`).
   * **`\clip`:** Etiqueta de recorte `\clip(m ...)`.
   * **`\iclip`:** Etiqueta de recorte invertido `\iclip(m ...)`.
6. **`[2.6] Bleed`:** Solapamiento entre fragmentos adyacentes. Cada pieza se dilata para ocultar las costuras finas entre piezas contiguas.
7. **`[2.7] Order:`:** Orden de iteración, nombrado según las posiciones del teclado numérico:
   * **`79 (TL->BR)`:** De arriba-izquierda (*Top-Left*) a abajo-derecha (*Bottom-Right*).
   * **`97 (TR->BL)`:** De arriba-derecha (*Top-Right*) a abajo-izquierda (*Bottom-Left*).
   * **`13 (BL->TR)`:** De abajo-izquierda (*Bottom-Left*) a arriba-derecha (*Top-Right*).
   * **`31 (BR->TL)`:** De abajo-derecha (*Bottom-Right*) a arriba-izquierda (*Top-Left*).
   * **`71 (TL->BL)`:** Por columnas de izquierda a derecha, de arriba abajo.
   * **`17 (BL->TL)`:** Por columnas de izquierda a derecha, de abajo arriba.
   * **`39 (BR->TR)`:** Por columnas de derecha a izquierda, de abajo arriba.
   * **`5 (Centro)`:** Desde el centroide de la forma original hacia fuera.
8. **`[2.8] s_i, s_n`:** Variables de iteración del pie del nodo (`s_i` = índice de la pieza actual $[1 \dots N]$, `s_n` = total de piezas).

---

### 2.3. Salidas
1. **`[3.1] Piece`:** Código ASSdraw o etiqueta `\clip`/`\iclip` de la pieza actual.
2. **`[3.2] X`:** Coordenada horizontal del centroide de la pieza.
3. **`[3.3] Y`:** Coordenada vertical del centroide de la pieza.
4. **`[3.4] Col`:** Índice de columna de la pieza en la malla.
5. **`[3.5] Row`:** Índice de fila de la pieza en la malla.

---

### 2.4. Entradas específicas por modo
Todos los modos usan además los parámetros universales de §2.2.

#### 1. `Grid 1D/2D` (`Rejilla 1D/2D`)
* **`Cols`:** Número de divisiones horizontales.
* **`Rows`:** Número de divisiones verticales.
* **`Angle`:** Inclinación de la rejilla de corte, en grados.
* **`Bleed`:** Solapamiento entre celdas.
* **`Accel X` / `Accel Y`:** Exponente de no linealidad en el eje horizontal / vertical (hace las celdas progresivamente más densas o más espaciadas).

#### 2. `Hex` (`Hexagonal`)
* **`Radius`:** Radio circunscrito de los hexágonos del panal.

#### 3. `Tri` (`Triangular`)
* **`Radius`:** Mitad del lado de los triángulos equiláteros.

#### 4. `Dia` (`Diamante / Rombos`)
* **`Radius`:** Semidiagonal mayor y menor de la malla de rombos.

#### 5. `Rings` (`Anillos Concéntricos`)
* **`Ring Width`:** Ancho radial en píxeles de cada anillo.

#### 6. `Ray` (`Rayos Radiales`)
* **`Step Angle` / `Rays`:** Paso angular en grados, o número de sectores radiales del centro al perímetro.

#### 7. `Voronoi` (`Cristales / Voronoi`)
* **`Cell Size`:** Tamaño medio de las celdas generadas por la distribución aleatoria de sitios.

#### 8. `Delaunay` (`Low-Poly`)
* **`Cell Size`:** Densidad y distancia entre vértices de la triangulación de Delaunay irregular.

#### 9. `Brick` (`Ladrillos`)
* **`Size X` (Width):** Ancho en píxeles de cada ladrillo.
* **`Size Y` (Height):** Alto en píxeles de cada hilera.

#### 10. `Ashlar` (`Mampostería Irregular`)
* **`Min Width` / `Max Width`:** Rango de ancho aleatorio de los bloques de piedra.
* **`Row Height`:** Altura fija de cada hilera.

#### 11. `Jigsaw` (`Rompecabezas / Puzzle`)
* **`Piece Size`:** Tamaño base de las piezas del puzzle, con pestañas y huecos Bézier.

#### 12. `Bez` (`Ondas Bézier`)
* **`Wave Size`:** Tamaño de celda. Las celdas están delimitadas por curvas Bézier sinusoidales con perturbación orgánica aleatoria.

#### 13. `Circuit` (`Circuito Electrónico`)
* **`Grid Size`:** Paso de la cuadrícula de la placa.
* **`Trace Width`:** Grosor de las pistas conductoras.
* **`Via Prob`:** Probabilidad de insertar un pad circular (*pad / vía*).

#### 14. `Truchet` (`Tuberías / Laberinto`)
* **`Tile Size`:** Tamaño de los azulejos cuadrados (*Truchet Tiles*) con arcos de círculo tangentes.

#### 15. `Pattern` (`Patrón Personalizado`)
* **`Pattern Shape`:** Forma ASSdraw usada como sello de corte repetido.
* **`Size X` / `Size Y`:** Espaciado de repetición horizontal y vertical.

#### 16. `Mondrian` (subdivisión neoplástica)
* **`Min Size`:** Tamaño mínimo de los rectángulos que ya no se dividen.
* **`Chaos`:** Probabilidad de división recursiva en los ejes $X$ e $Y$.

#### 17. `Herringbone` (`Espiga / Zig-Zag`)
* **`Length` / `Width`:** Longitud y ancho de los bloques rectangulares, entrelazados a $90^\circ$.

#### 18. `Kagome` (`Trihexagonal`)
* **`Radius`:** Radio de la red de hexágonos y triángulos equiláteros entrelazados.

#### 19. `Rhombille` (`Cubos Isométricos`)
* **`Radius`:** Radio de los rombos a $60^\circ$ que forman los cubos 3D en perspectiva axonométrica.

#### 20. `Octagon` (`Mosaico Octogonal`)
* **`Radius`:** Tamaño de los octógonos, combinados con pequeños cuadrados de unión.

#### 21. `Scallop` (`Escamas de Pez`)
* **`Radius`:** Radio y curvatura de las escamas semicirculares superpuestas.

#### 22. `Web` (`Telaraña`)
* **`Cols` (Rings):** Número de anillos concéntricos poligonales.
* **`Rows` (Rays):** Número de filamentos radiales desde el centro.
* **`Chaos`:** Irregularidad aleatoria de los nudos.

#### 23. `Quad` (`Quadtree`)
* **`Min Size`:** Tamaño mínimo de celda en la subdivisión recursiva.
* **`Chaos`:** Umbral de probabilidad de división de cada cuadrante.

### 2.5. Ejemplo
* **Fragmentación Voronoi (*shatter*):**
  Conecta la silueta de la sílaba a `Shape/Slicer` con `mode: voronoi`, `cell_size: 25`, `anchor: pieces`:

  ```
  [System/Input: Syl Shape] ──► Shape ──► [Shape/Slicer: voronoi, anchor=pieces]
                                                ├──► Piece ──► Return ──► [System/Output]
                                                └──► (s_i, s_n en contexto)
  ```

  En un nodo de etiquetas conectado a `System/Output (Tags)`:
  ```
  {\p1\pos(syl.center, syl.middle)\t(0, 350, \frz(s_i * 20)\fscx0\fscy0\alpha&HFF&)}
  ```
  Cada fragmento rota sobre su propio centroide, con una rotación proporcional a `s_i`, y se encoge hasta desaparecer. El anclaje local evita que los fragmentos se desplacen respecto al origen del dibujo original.

---

## 3. Nodo `Shape/Manipulator`

Escala, desplaza, rota en 3D, remuestrea y refleja una forma. El cuerpo del nodo cambia según el modo elegido.

![Shape/Manipulator](img/manipulator.jpg)

### 3.1. Cabecera y salida
1. **`[1.1] Shape` (Output):** El trazado ASSdraw transformado.
2. **`[1.2] Mode`:** Elige uno de los 8 modos (`Scale`, `Borders`, `Deform`, `Position`, `Redraw`, `3D Rotate`, `Reflect`, `Matrix`).

---

### 3.2. Parámetros comunes
1. **`Shape / Text`:** Forma ASSdraw o texto. Si no está conectado, toma el glifo del contexto activo (sílaba, palabra o línea).
2. **`Factor (t)`:** Progresión ($0.0 \to 1.0$) para animar la transformación.
3. **`Anchor`:** Punto de referencia de la forma:
   * **`center`:** Centra el centroide de la tinta en `(0, 0)`.
   * **`origin`:** Pone la esquina superior izquierda de la caja de tinta (*bounding box*) en `(0, 0)`.
   * **`relative`:** Conserva el origen `(0, 0)` original del trazado sin recentrar sobre la tinta (útil para coincidir 1:1 con vectores tipográficos).
   * **`absolute`:** Traslada la geometría a las coordenadas de pantalla `(fx.pos_x, fx.pos_y)`.

---

### 3.3. Entradas específicas por modo

#### 1. `Scale` (escalado anamórfico)
Escala por separado los ejes horizontal y vertical.
* **`Scale X` / `Scale Y`:** Porcentaje de escala horizontal y vertical (default: `100`%).
* **`Factor (t)`:** Progresión de la escala ($0.0 \to 1.0$).
* **`Anchor`:** Punto de anclaje (`center`, `origin`, `absolute`).

#### 2. `Borders` (expansión / contracción del perímetro)
Dilata o erosiona los contornos cerrados con un offset morfológico de Clipper.
* **`Offset (px)` (`offset_border`):** Distancia del desplazamiento en píxeles (positivo expande, negativo contrae; default: `2.0`).
* **`Factor (t)` / `Anchor`:** Parámetros comunes.

#### 3. `Deform` (deformación direccional asimétrica)
Aplica una distorsión direccional.
* **`Offset X` / `Offset Y`:** Componentes horizontal y vertical del vector de deformación.
* **`Def Factor` (`factor`):** Intensidad de la distorsión en porcentaje (default: `100`%).
* **`Factor (t)` / `Anchor`:** Parámetros comunes.

#### 4. `Position` (desplazamiento cartesiano relativo)
Desplaza las coordenadas del dibujo en $X$ e $Y$ sin tocar la etiqueta ASS `\pos`.
* **`Offset X` / `Offset Y`:** Desplazamiento horizontal y vertical en píxeles.
* **`Factor (t)` / `Anchor`:** Parámetros comunes (`center`, `origin`, `relative`, `absolute`).

#### 5. `Redraw` (remuestreo y densidad Bézier)
Remuestrea los vértices de las curvas Bézier, para suavizar el contorno o para añadir puntos antes de una deformación posterior.
* **`Density / Step` (`density`):** Densidad de muestreo (valores más altos añaden más puntos de control interpolados; default: `2.0`).
* **`Factor (t)` / `Anchor`:** Parámetros comunes.

#### 6. `3D Rotate`
Rota el trazado en 3D con matrices y proyección en perspectiva.
* **`Rotate X` (`angle_x`):** Cabeceo, en grados sobre el eje $X$.
* **`Rotate Y` (`angle_y`):** Guiñada, en grados sobre el eje $Y$.
* **`Rotate Z` (`angle_z`):** Giro en el plano de pantalla, en grados sobre el eje $Z$ (equivale a `\frz`).
* **`Factor (t)` / `Anchor`:** Parámetros comunes (`center`, `origin`, `relative`, `absolute`). El anclaje es el centro del giro.

#### 7. `Reflect` (espejado)
Refleja la forma respecto a un eje.
* **`Axis`:** `none` conserva la forma sin reflejar, `x` invierte izquierda-derecha, `y` invierte arriba-abajo, `xy` invierte en diagonal.
* **`Offset X` / `Offset Y`:** Desplazamiento del eje de simetría.
* **`Factor (t)` / `Anchor`:** Parámetros comunes.

#### 8. `Matrix`
Aplica todas las transformaciones en una sola pasada, en este orden:
$$\text{Desfase Clipper (Offset Border)} \longrightarrow \text{Remuestreo (Density)} \longrightarrow \text{Escala} \longrightarrow \text{Cizallamiento (Skew)} \longrightarrow \text{Rotación 3D Euler} \longrightarrow \text{Reflexión} \longrightarrow \text{Traslación (Offset)}$$

* **`Shape / Text`:** Trazado ASSdraw o texto de entrada.
* **`Factor (t)`:** Factor de interpolación global ($0.0 \to 1.0$).
* **`Scale X` / `Scale Y`:** Porcentajes de escala horizontal y vertical independientes (default: `100`%).
* **`Skew X` / `Skew Y`:** Factores de cizallamiento (*shear*) en los ejes $X$ e $Y$.
* **`Rotate X` / `Rotate Y` / `Rotate Z`:** Ángulos de rotación en grados sobre los 3 ejes (Euler, con proyección en perspectiva $fov$).
* **`Offset X` / `Offset Y`:** Desplazamiento en píxeles.
* **`Offset Border`:** Desfase del contorno con Clipper en píxeles, aplicado primero (positivo expande, negativo contrae; default: `0.0`).
* **`Axis`:** Eje de reflexión (`none`, `x`, `y`, `xy`).
* **`Density`:** Remuestreo Bézier previo (default: `0` = desactivado; $> 0$ subdivide con paso en px).
* **`Anchor`:** Punto de referencia (`center`, `origin`, `relative`, `absolute`).

---

### 3.4. Ejemplo
* **Rotación en perspectiva de una estrella:**
  Rota una estrella de `Shape/Library` sobre el eje $Y$ (guiñada 3D) durante el tiempo de la sílaba:

  ```
  [Shape/Library: star] ──► Shape ──► Shape / Text ──► [Shape/Manipulator: 3D Rotate, Rotate Y=70]
                                                             └──► Shape ──► Return ──► [System/Output]
  ```

  En un nodo de etiquetas conectado a `System/Output (Tags)`:
  ```
  {\p1\pos(syl.center, syl.middle)\1c&H00FFFF&\bord1\3c&H003366&\t(0, syl.dur, \1c&HFF0088&)}
  ```
  La estrella rota en 3D sobre su centroide local con perspectiva, y su color cambia sin mover el anclaje de la sílaba.

---

## 4. Nodo `Shape/Filter`

Modifica las coordenadas de los vértices de un trazado ASSdraw con expresiones matemáticas, transformaciones escalonadas por subcontorno o perturbación aleatoria (*jitter / noise*).

* **Color temático:** `#0F766E` / `#5B2C6F`

![Shape/Filter](img/filter.jpg)

---

### 4.1. Modos de cabecera
Un desplegable en la cabecera elige el modo, que determina las entradas y propiedades del nodo:
1. **`Vertices`:** Aplica expresiones a cada coordenada $(x, y)$, usando variables cartesianas, polares y de progreso del contorno.
2. **`Group`:** Recorre cada subcontorno cerrado o isla (`m ...`) de un trazado compuesto y aplica rotación, escala y desplazamiento acumulativos por pieza.
3. **`Noise`:** Desplaza cada vértice al azar dentro de una ventana elíptica o rectangular, con semilla determinista y subdivisión previa opcional.

---

### 4.2. Entradas y propiedades

#### 1. Modo `Vertices`
Evalúa expresiones algebraicas en tiempo real sobre cada vértice $(x_k, y_k)$ del trazado. Sirve para ondulaciones, vórtices, torsiones polares, dispersiones balísticas y disoluciones no lineales.

1. **`[2.1] Shape / Text` (`shape`):** Trazado ASSdraw base o texto. Si no está conectado, toma el glifo del contexto activo (`syl.text` o `line.text`).
2. **`[2.2] Expr X` (`expr_x`):** Expresión de la nueva posición horizontal del vértice (default: `x`).
3. **`[2.3] Expr Y` (`expr_y`):** Expresión de la nueva posición vertical del vértice (default: `y`).
4. **`[2.4] Factor (t)` (`t`):** Factor de interpolación ($0.0 \le t \le 1.0$) entre la geometría original y la calculada (default: `1.0`).
5. **`[2.5] Subdivs` (`subdivs`):** Subdivisión previa de curvas Bézier y segmentos rectos antes de evaluar las expresiones (default: `0`).

##### Variables disponibles en `Expr X` y `Expr Y`
* **Coordenadas cartesianas absolutas:**
  * `x`, `y`: Coordenadas actuales del vértice en el espacio local.
  * `cx`, `cy` (`Cx`, `Cy`): Centro de la caja delimitadora de la forma:
    $$cx = \frac{x_{\min} + x_{\max}}{2}, \quad cy = \frac{y_{\min} + y_{\max}}{2}$$
  * `width`, `height`: Dimensiones de la caja delimitadora (*bounding box*): $W = x_{\max} - x_{\min}$, $H = y_{\max} - y_{\min}$.
  * `minx`, `miny`, `maxx`, `maxy`: Límites del *bounding box*.
* **Coordenadas normalizadas $(0.0 \to 1.0)$:**
  * `mx`, `my` (`Mx`, `My`): Posición del vértice dentro del *bounding box*:
    $$mx = \frac{x - x_{\min}}{\max(10^{-6}, W)}, \quad my = \frac{y - y_{\min}}{\max(10^{-6}, H)}$$
* **Métricas polares y distancias:**
  * `do`, `Do`: Distancia del origen local `(0, 0)` al vértice: $do = \sqrt{x^2 + y^2}$.
  * `dc`, `Dc`: Distancia del centroide `(cx, cy)` al vértice: $dc = \sqrt{(x - cx)^2 + (y - cy)^2}$.
  * `ao`, `Ao`: Ángulo polar en grados ($0^\circ \le ao < 360^\circ$) respecto al origen `(0, 0)`.
  * `ac`, `Ac`: Ángulo polar en grados ($0^\circ \le ac < 360^\circ$) respecto al centroide `(cx, cy)`.
* **Índices y progreso del contorno:**
  * `k`, `i`, `Pk`: Índice del vértice, empezando en 1 ($1 \le k \le N$).
  * `n`, `Pn`: Número total de vértices del trazado.
  * `mp`, `Mp`: Progreso del vértice a lo largo del perímetro: $mp = \frac{k - 1}{N - 1}$ (o $0.0$ si $N \le 1$).
  * `t`: Valor actual de `Factor (t)`.
* **Funciones:**
  * *Trigonométricas:* `sin(rad)`, `cos(rad)`, `tan(rad)`, `asin(v)`, `acos(v)`, `atan2(y, x)`.
  * *Conversión de ángulos y constantes:* `rad(deg)` (grados a radianes), `deg(rad)` (radianes a grados), `pi`, `PI`.
  * *Álgebra y exponenciales:* `sqrt(v)`, `abs(v)`, `min(a, b)`, `max(a, b)`, `exp(v)`, `log(v)`.
  * *Redondeo:* `floor(v)`, `ceil(v)`, `round(v)`.

> [!IMPORTANT]
> **Entorno aislado y tolerancia a fallos:**
> Las expresiones del modo `Vertices` se evalúan en un entorno aislado y determinista. Las funciones de azar como `Rs()` o `R()` **no existen** en este ámbito. Si una expresión usa funciones indefinidas o tiene errores de sintaxis, el nodo deja el vértice intacto ($x_{\text{final}} = x, y_{\text{final}} = y$) sin interrumpir el motor. Para deformaciones aleatorias, usa el modo **`Noise`** o funciones armónicas pseudoaleatorias basadas en `k`.

---

#### 2. Modo `Group`
Separa la forma en sus islas o subcontornos cerrados independientes (delimitados por comandos `m ...`) y aplica una transformación acumulativa a cada pieza.

1. **`[2.1] Shape / Text` (`shape`):** Trazado compuesto (por ejemplo glifos como "i", "j", "!", "¿", kanjis de varios trazos o formas ya fracturadas por *Slicer*).
2. **`[2.2] Factor (t)` (`t`):** Factor de interpolación global ($0.0 \to 1.0$).
3. **`[2.3] Rotation Step` (`rot_step`):** Rotación en grados que se suma por pieza (default: `0.0`).
4. **`[2.4] Scale Step` (`scale_step`):** Porcentaje de escala que se suma por pieza (default: `100.0`%).
5. **`[2.5] Offset X` (`offset_x`):** Desplazamiento horizontal en píxeles que se suma por pieza (default: `0.0`).
6. **`[2.6] Offset Y` (`offset_y`):** Desplazamiento vertical en píxeles que se suma por pieza (default: `0.0`).
7. **`[2.7] Anchor` (`anchor`):** Pivote de giro y escala de cada isla (`center`, `origin`, `relative`, `absolute`).

---

#### 3. Modo `Noise`
Desplaza cada vértice una cantidad aleatoria uniforme dentro de una ventana elíptica o rectangular. Sirve para efectos analógicos como *line boil*, tiza, fuego, arcos eléctricos, vapor o degradación orgánica.

1. **`[2.1] Shape / Text` (`shape`):** Trazado ASSdraw base.
2. **`[2.2] Radius X` (`radius_x`):** Desplazamiento horizontal máximo en píxeles: $\Delta x \in [-R_x, +R_x]$ (default: `5.0`).
3. **`[2.3] Radius Y` (`radius_y`):** Desplazamiento vertical máximo en píxeles: $\Delta y \in [-R_y, +R_y]$ (default: `5.0`).
4. **`[2.4] Subdivs` (`subdivs`):** Subdivisión previa de curvas Bézier y líneas rectas antes de aplicar el ruido (default: `2.0`).
5. **`[2.5] Seed` (`seed`):** Semilla entera del generador pseudoaleatorio (default: `0`).

---

### 4.3. Salidas
1. **`[1.1] Shape`:** El código ASSdraw modificado (`m ... l ... b ...`).

---

### 4.4. Cómo funciona

#### 4.4.1. Interpolación en el modo `Vertices`
Dada una coordenada original $\vec{p} = (x, y)$ y el resultado evaluado de las expresiones $\vec{p}_{\text{calc}} = (\text{res}_x, \text{res}_y)$, la posición final es una mezcla lineal:

$$\vec{p}_{\text{final}}(t) = \vec{p} + t \cdot (\vec{p}_{\text{calc}} - \vec{p}) = \begin{pmatrix} x + t \cdot (\text{res}_x - x) \\ y + t \cdot (\text{res}_y - y) \end{pmatrix}$$

Con $t \in [0.0, 1.0]$: en $t = 0.0$ el trazado no cambia y en $t = 1.0$ se aplica por completo la deformación calculada.

#### 4.4.2. `Subdivs`
Las tipografías y primitivas suelen describir un tramo recto largo con solo dos vértices (por ejemplo el asta de una "I" o los lados de un rectángulo). Sin subdivisión, una onda sinusoidal o el ruido solo mueven los extremos y el tramo central sigue recto.
* **$\text{Subdivs} = 0$:** Conserva el número original de vértices. Útil para deformaciones facetadas tipo *Low-Poly*.
* **$\text{Subdivs} \ge 1.0$:** Divide recursivamente cada segmento recto y cada arco Bézier en $2^{\text{subdivs}}$ tramos, preservando la continuidad $C^1$. Con más vértices, las ecuaciones de onda dan curvas suaves y `Noise` produce texturas rugosas de alta frecuencia.

#### 4.4.3. Modo `Group`
Para un trazado dividido en $M$ piezas con índice $j \in [0, M - 1]$:
$$\theta_j = j \cdot \text{Rot Step} \cdot t$$
$$S_j = \max\left(0.001, \, 1.0 + j \cdot \left(\frac{\text{Scale Step} - 100.0}{100.0}\right) \cdot t\right)$$
$$\Delta x_j = j \cdot \text{Offset X} \cdot t, \quad \Delta y_j = j \cdot \text{Offset Y} \cdot t$$

Cada subcontorno se escala y rota alrededor del pivote definido en `Anchor`.

#### 4.4.4. Modo `Noise`
Cada vértice se desplaza con variables aleatorias uniformes e independientes:
$$x' = x + \Delta x, \quad \Delta x \sim \mathcal{U}(-R_x, \, +R_x)$$
$$y' = y + \Delta y, \quad \Delta y \sim \mathcal{U}(-R_y, \, +R_y)$$

* **`Seed` fija:** Un contorno rasgado congelado y reproducible, útil para siluetas desgastadas.
* **`Seed` variable:** Si conectas el iterador de fotograma (`fx_i`, `j`, o una variable temporal basada en `st`) a `Seed`, el ruido cambia en cada fotograma y da la vibración característica del dibujo a mano (*line boil*).

---

### 4.5. Recetas

#### Receta 1: Ondulación sinusoidal horizontal (`Vertices`)
Una onda que viaja por el eje horizontal; la subdivisión permite flexionar las astas de las letras:
* **`Subdivs`:** `2`
* **`Expr X`:** `x`
* **`Expr Y`:** `y + sin(rad(x * 6 + t * 360)) * 12`

#### Receta 2: Vórtice / torsión polar (`Vertices`)
Gira los vértices alrededor del centroide con un ángulo proporcional a su distancia $dc$:
* **`Subdivs`:** `1`
* **`Expr X`:** `cx + dc * cos(rad(ac + dc * 1.5 * t))`
* **`Expr Y`:** `cy - dc * sin(rad(ac + dc * 1.5 * t))`

#### Receta 3: Pseudo-ruido determinista (`Vertices`)
Desplazamientos de aspecto aleatorio sin ninguna llamada a azar, usando frecuencias seno y coseno inconmensurables sobre el índice $k$ del vértice:
* **`Expr X`:** `x + sin(k * 12.9898) * 4 * t`
* **`Expr Y`:** `y + cos(k * 78.2330) * 4 * t`

#### Receta 4: Line boil / tiza vibrante (`Noise`)
Hace vibrar la tipografía vectorial como tiza o como un contorno eléctrico inestable:
* Encadenamiento: `Text to Shape` $\to$ `Shape/Filter (Noise)` $\to$ `Salida (Retorno)`
* **`Radius X`:** `3.5`
* **`Radius Y`:** `3.5`
* **`Subdivs`:** `2`
* **`Seed`:** `fx_i` *(varía en cada fotograma del bucle FBF)*

---

## 5. Nodo `Shape/Transform`

Aplica transformaciones no lineales a trazados ASSdraw: hinchado radial (*Inflate*), cizallamiento (*Skew*), redondeo y biselado de esquinas (*Round Corners*), flexión sobre splines (*Flexor*) y metamorfosis entre dos o tres formas (*Distort / Distort2*). Las entradas del cuerpo cambian según el modo.

![Shape/Transform](img/transform.jpg)

### 5.1. Cabecera y salida
1. **`[1.1] Shape` (Output):** El trazado ASSdraw transformado.
2. **`[1.2] Mode`:** Elige uno de los 6 modos (`Inflate`, `Skew`, `Round Corners`, `Flexor`, `Distort`, `Distort2`).

---

### 5.2. Parámetros comunes y alineación en la metamorfosis
1. **`Shape / Text`:** Forma ASSdraw o texto base. Si no está conectado, toma el glifo del contexto activo (sílaba, palabra o línea).
2. **`Factor (t)`:** Progresión ($0.0 \to 1.0$) de la transición desde el estado original hacia la forma transformada.
3. **`Anchor`:** Cómo se alinea la silueta objetivo sobre la de origen. Antes de interpolar los vértices, la silueta objetivo se escala proporcionalmente y se superpone a la base. Durante la animación ($t = 0.0 \to 1.0$), el *bounding box* cambia de forma continua: $W(t) = W_A(1-t) + W_B(t)$ y $H(t) = H_A(1-t) + H_B(t)$.
   * **`center` (por defecto):** Alinea los centroides $(\frac{x_{\min}+x_{\max}}{2}, \frac{y_{\min}+y_{\max}}{2})$ y centra el dibujo en `(0, 0)`. Con `\pos(x, y)` o alineación central (`\an5`), la metamorfosis ocurre concéntricamente en el centro del glifo o partícula, expandiéndose y contrayéndose de forma simétrica.
   * **`origin`:** Alinea los vértices superiores izquierdos $(x_{\min}, y_{\min})$ y fija `(0, 0)` en la esquina superior izquierda del *bounding box*. Con `\an7`, la transformación crece hacia la derecha y hacia abajo y la esquina común no se mueve.
   * **`absolute`:** Conserva la posición del glifo original en pantalla (`fx.pos_x`, `fx.pos_y`), de modo que la metamorfosis queda en la ubicación real del subtítulo.

---

### 5.3. Entradas específicas por modo

#### 1. `Inflate` (hinchado radial)
Desplaza los vértices hacia fuera o hacia dentro tomando como referencia una envolvente circular o elíptica centrada en la masa de la forma.
* **`Ratio`:** Intensidad del inflado (default: `1.0`).
* **`Inflate Mode`:** `Circle` (esferificación circular uniforme) o `Ellipse` (proporcional al ancho y alto del *bounding box*).
* **`Anchor`:** Centro de la expansión/contracción (`center`, `origin`, `absolute`).

#### 2. `Skew` (cizallamiento 2D)
Aplica una deformación oblicua que mantiene paralelas las líneas opuestas.
* **`Angle X`:** Ángulo de cizallamiento horizontal en grados (desliza las líneas horizontales sobre el eje $X$).
* **`Angle Y`:** Ángulo de cizallamiento vertical en grados (desliza las líneas verticales sobre el eje $Y$).
* **`Anchor`:** Punto base del cizallamiento.

#### 3. `Round Corners` (redondeo y biselado)
Detecta las esquinas agudas del trazado poligonal y las sustituye por arcos Bézier suaves o por chaflanes.
* **`Radius (px)` (`radius`):** Radio de curvatura o profundidad de corte de las esquinas en píxeles (default: `10.0`).
* **`Corner Mode`:** `Round` (arcos con curvas Bézier cúbicas), `Bevel` (chaflán recto) o `Miter` (inglete puntiagudo con límite de proyección).
* **`Anchor`:** `center`, `origin`, `relative`, `absolute`.

#### 4. `Flexor` / `Bend` (flexión sobre curvas)
Pliega la forma a lo largo de un arco numérico o de una curva ASSdraw personalizada.
* **`Factor (t)` / `Bend (t)`:** Progresión de la flexión ($0.0 \to 1.0$).
* **`Curve / Angle` (`curve`):** Ángulo de curvatura en grados (por ejemplo `30`, `45`, `-60`) o código ASSdraw completo de una curva guía (`m ... b ...`) sobre la que se proyecta el dibujo.
* **`Axis`:** Eje de flexión (`x` para doblar horizontalmente a lo largo del arco, `y` para doblar en vertical).
* **`Anchor`:** `center`, `origin`, `relative`, `absolute`.

#### 5. `Distort` (metamorfosis de 2 formas)
Interpola de forma continua y adaptativa el perímetro de la forma de origen (`Shape / Text`) hacia la forma objetivo (`Target Shape`). Admite dibujos ASSdraw y glifos de texto.
* **`Shape / Text`:** Trazado o texto de origen en $t = 0.0$. Si es texto, se vectoriza automáticamente con la tipografía y el estilo de la línea.
* **`Target Shape`:** Trazado o texto de destino en $t = 1.0$.
* **`Energy` (`Fluidez`):** Elasticidad de la transición ($0 < t < 1$). Aplica la onda $W(t) = \sin(\pi \cdot t)$ a las manetas Bézier intermedias ($\vec{p_1}, \vec{p_2}$), lo que da una deformación elástica sin alterar la coincidencia geométrica en $t = 0$ y $t = 1$ (default: `0.35`).
* **`Step (px)` (`Paso`):** Subdivisión métrica en píxeles. Si `Step (px)` $> 0.05$, divide curvas y segmentos cada $N$ píxeles ($\text{pasos} = \max(1, \text{round}(L / s_{px}))$), lo que da un remuestreo uniforme del perímetro antes de emparejar los vértices (default: `0` = cálculo adaptativo).
* **`Anchor`:** `center`, `origin`, `relative`, `absolute`.

#### 6. `Distort2` (metamorfosis de 3 etapas)
Transición continua de la forma inicial ($t = 0.0$) a la intermedia ($t = 0.5$) y a la final ($t = 1.0$).
* **`Shape / Text`:** Trazado o texto inicial ($t = 0.0$).
* **`Mid Shape`:** Trazado o texto intermedio, alcanzado al $50\%$ de la animación ($t = 0.5$).
* **`Target Shape`:** Trazado o texto final ($t = 1.0$).
* **`Energy` (`Fluidez`):** Modulación de las tangentes Bézier (default: `0.35`).
* **`Step (px)` (`Paso`):** Subdivisión métrica en píxeles para remuestreo uniforme del perímetro (default: `0`).
* **`Anchor`:** `center`, `origin`, `relative`, `absolute`.

---

### 5.4. Ejemplo
* **Metamorfosis de sílaba a estrella:**
  Transforma la silueta de la sílaba en una estrella de `Shape/Library` durante el tiempo activo de la nota:

  ```
  [System/Input: Syl Shape] ──► Shape / Text ──┐
                                              ├──► [Shape/Transform: Distort, Energy=0.35]
  [Shape/Library: star] ────► Target Shape ───┘          └──► Shape ──► Return ──► [System/Output]
  ```

  Enlaza `Factor (t)` al progreso normalizado del tiempo de la sílaba y configura `System/Output (Tags)`:
  ```
  {\p1\pos(syl.center, syl.middle)\1c&H00FFFF&\bord1\3c&H000000&\t(0, syl.dur, \1c&H0088FF&)}
  ```
  El contorno de la sílaba se deforma poco a poco hacia el de la estrella sobre su centroide local, sin mover el anclaje.

---

## 6. Nodo `Shape/Concentric Borders`

Genera anillos concéntricos, contornos escalonados u ondas expansivas a partir de una forma base, con dilatación de Clipper y diferencias booleanas.

![Shape/Concentric Borders](img/concentric_borders.jpg)

### 6.1. Cabecera
1. **`[1.1] Concentric Borders`:** Título del nodo.
2. **`[1.2] Modo de Salida Vectorial` (`out_mode`):** Botón de la esquina superior derecha de la barra de título. Define el formato que emite el puerto `Shape`:
   * **`Shape`:** Código ASSdraw del anillo (`m ... l ... b ...`).
   * **`\clip` (`Clip`):** Etiqueta de recorte `\clip(m ...)` con el trazado en coordenadas absolutas de pantalla.
   * **`\iclip` (`iClip`):** Etiqueta de recorte invertido `\iclip(m ...)`.

---

### 6.2. Entradas y propiedades
1. **`[2.1] Shape / Text`:** Contorno, silueta ASSdraw o texto base de las capas. Si no está conectado, toma la forma del elemento activo del contexto (sílaba, palabra o línea).
2. **`[2.2] Mode: [Hollow / Solid]`:** Botón del cuerpo del nodo (segunda ranura) que define la topología de las capas:
   * **`Hollow (borders)` / `Hollow`:** Todos los anillos son bandas huecas de grosor constante, calculadas como diferencia booleana entre el contorno exterior dilatado y el interior:
     $$\text{Ring}_i = \text{BooleanDifference}(\text{Outer}_i, \text{Inner}_i)$$
   * **`Solid (filled borders)` / `Solid`:** El primer elemento ($i = 1$) conserva el relleno sólido de la forma base; las capas siguientes ($i \ge 2$) son anillos huecos hacia fuera.
3. **`[2.3] Max Rings` (`loop_count`):** Número de capas concéntricas (default: `5`). Define `b_n` y `maxloop`.
4. **`[2.4] Separación (px)` (`separation`):** Dilatación por anillo. Admite un valor fijo (por ejemplo `5.0`) o una lista separada por comas (por ejemplo `5, 2, 8, 3`) para alternar el grosor.
5. **`[2.5] Solape (px)` (`overlap`):** Solapamiento en píxeles entre capas contiguas (default: `0.5`). Evita las costuras que provoca el antialiasing de libass/VSFilter al unir piezas adyacentes.
6. **`[2.6] Anchor` (`Center` / `Relativo` / `Absoluto` / `Piezas`):** Punto de anclaje y sistema de coordenadas de la geometría generada.
7. **`[2.7] b_i, b_n`:** Variables de iteración del pie del nodo (`b_i` / `ring_i` = índice del anillo actual $[1 \dots N]$, `b_n` / `ring_n` = total de anillos).

---

### 6.3. Salidas
1. **`[3.1] Shape`:** Trazado ASSdraw o etiqueta `\clip`/`\iclip` del anillo actual `b_i`.
2. **`[3.2] \pos`:** Etiqueta `\pos(x,y)` que coloca el centroide del anillo en el lienzo.
3. **`[3.3] Index`:** Índice del anillo actual ($1 \dots \text{Max Rings}$).
4. **`[3.4] Total`:** Número total de anillos ($b\_n$).

### 6.4. Ejemplo
* **Ondas concéntricas que se desvanecen:**
  Conecta la silueta de la sílaba a `Shape/Concentric Borders` con `loop_count: 5`, `separation: 6`, `mode: hollow`:

  ```
  [System/Input: Syl Shape] ──► Shape / Text ──► [Shape/Concentric Borders: hollow, max=5]
                                                       ├──► Shape ──► Return ──► [System/Output]
                                                       └──► (b_i, b_n en contexto)
  ```

  En un nodo de etiquetas conectado a `System/Output (Tags)`:
  ```
  {\p1\pos(syl.center, syl.middle)\1c&H00FFFF&\bord0\1a&H44&\t(0, 400, \fscx(100 + b_i * 15)\fscy(100 + b_i * 15)\1a&HFF&)}
  ```
  Genera 5 bandas concéntricas de 6 px de grosor que se expanden hacia fuera y se desvanecen según el índice `b_i`.

---

## 7. Nodo `Shape/Walker`

Recorre un trazado ASSdraw y lo recorta al intervalo $[start\_t, progress]$ de su longitud de arco, para efectos de escritura progresiva (*write-on*). También emite la etiqueta `\pos` y el ángulo tangencial `\frz` de la punta de avance.

![Shape/Walker](img/walker.jpg)

### 7.1. Modos de cabecera
1. **Modo de integración (`mode`):**
   * `global`: Acumula la longitud de arco de todos los subcontornos o trazos. El intervalo $[0.0, 1.0]$ recorre la geometría completa de principio a fin.
   * `piece`: Aplica el avance $[0.0, 1.0]$ de forma independiente y simultánea a cada subcontorno `m` (útil para escribir varios glifos en paralelo).
2. **Sentido (`invert`):**
   * `normal`: Recorre los vértices en el orden en que fueron creados.
   * `inverted`: Recorre el perímetro de fin a inicio.

### 7.2. Entradas y propiedades
1. **`[2.1] Shape / Text`:** Trazado ASSdraw o texto a recorrer.
2. **`[2.2] Progress (t)` (`progress`):** Final del segmento recortado ($t_2 \in [0.0, 1.0]$, defecto: `1.0`).
3. **`[2.3] Start (t)` (`start_t`):** Inicio del segmento ($t_1 \in [0.0, 1.0]$, defecto: `0.0`). Sirve para ventanas móviles o estelas.
4. **`[2.4] Subdivs` (`subdivs`):** Número de cuerdas lineales por curva Bézier para calcular la longitud de arco (defecto: `30`).
5. **`[2.5] Close Path` (`close_path`):** Booleano (defecto: `False`). Si es `True`, añade un comando `l` hacia el punto `m` inicial de cada contorno que termine abierto.

### 7.3. Salidas
1. **`[1.1] Shape Out`:** Trazado ASSdraw recortado entre $t_1$ y $t_2$.
2. **`[1.2] \pos Tag`:** Etiqueta `\pos(x,y)` en la punta de avance ($t_2$), en coordenadas de pantalla.
3. **`[1.3] Angle (\frz)`:** Ángulo en grados de la tangente del trazado en la punta de avance.
4. **`[1.4] Length`:** Longitud de arco en píxeles del segmento emitido.
5. **`[1.5] Tip X`:** Coordenada horizontal absoluta de la punta.
6. **`[1.6] Tip Y`:** Coordenada vertical absoluta de la punta.

### 7.4. Algoritmo
1. **Longitud de arco:**
   Para cada curva cúbica de Bézier $\mathbf{B}(u) = (1-u)^3\mathbf{P}_0 + 3(1-u)^2u\mathbf{P}_1 + 3(1-u)u^2\mathbf{P}_2 + u^3\mathbf{P}_3$, la longitud se aproxima con $S = \text{subdivs}$ cuerdas:
   $$L_{\text{arc}} = \sum_{j=1}^{S} \|\mathbf{B}(j/S) - \mathbf{B}((j-1)/S)\|$$
2. **Recorte:**
   Las distancias $s_1 = start\_t \cdot L_{\text{total}}$ y $s_2 = progress \cdot L_{\text{total}}$ fijan los puntos de corte, que se evalúan con el algoritmo de De Casteljau.
3. **Ángulo tangencial y posición:**
   $$\theta = \operatorname{atan2}\left(\frac{dy}{du}, \, \frac{dx}{du}\right) \cdot \frac{180}{\pi}$$
   $$\text{pos}_x = x_{\text{parent}} + \text{Tip X}, \quad \text{pos}_y = y_{\text{parent}} + \text{Tip Y}$$

### 7.5. Ejemplo
* **Escritura progresiva con una chispa guía:**
  Alimenta `Progress (t)` con la progresión de `Loops/Module` ($0.0 \to 1.0$):

  ```
  Línea 1 (trazo en crecimiento):
  Conectar Shape Out a System/Output (Return)
  Tags: {\p1\pos(syl.center, syl.middle)\1c&H00FFFF&\bord0}

  Línea 2 (chispa anclada a la punta):
  Conectar Tip X, Tip Y y Angle (\frz) a Variables (o pasar \pos Tag directo):
  Tags: {\p1\pos(tip_x, tip_y)\frz(angle)\1c&HFFFFFF&\bord0}
  Return: m -4 -4 l 4 0 l -4 4
  ```

---

## 8. Nodo `Shape/Stroke`

Convierte líneas abiertas, esqueletos y trazados sin relleno en polígonos cerrados con el grosor indicado, con control de uniones en las esquinas y de remates en los extremos, usando *Clipper2*.

![Shape/Stroke](img/stroke.jpg)

### 8.1. Entradas
1. **`Shape / Text`:** Trazado ASSdraw de la línea abierta, curva o texto al que se aplica el grosor.
2. **`Width (px)`:** Entrada opcional que fija el grosor en píxeles. Si no está conectada, se usa la propiedad `width`.

### 8.2. Propiedades
1. **`[2.1] Width (px)` (`width`):** Grosor total del trazo en píxeles (defecto: `4.0`, mínimo: $0.01$).
2. **`[2.2] Join Mode` (`join_mode`):** Tipo de unión en las esquinas:
   * `round`: Arco circular.
   * `miter`: Inglete puntiagudo, recortado según el límite de inglete.
   * `bevel`: Chaflán recto.
3. **`[2.3] Cap Mode` (`cap_mode`):** Tipo de remate en los extremos de líneas abiertas:
   * `round`: Semicírculo de radio $w/2$.
   * `bezier`: Remate redondeado con una curva cúbica Bézier suave.
   * `flat`: Corte plano perpendicular a la línea en el punto final.
   * `square`: Extremo cuadrado que sobresale $w/2$ del vértice final.
4. **`[2.4] Miter Limit` (`miter_limit`):** Relación máxima entre la longitud del inglete y el grosor del trazo antes de truncarlo en bisel (defecto: `2.0`, mínimo: $1.0$).

### 8.3. Salidas
1. **`[1.1] Shape Out`:** Polígono ASSdraw cerrado (`m ... l ... b ...`) con el grosor y los remates aplicados, listo para `\p1`.
2. **`[1.2] Width`:** Grosor en píxeles realmente aplicado.

### 8.4. Cómo funciona
El desplazamiento del trazado lo hace el motor de offset de Clipper2:
* Cada segmento recto abierto se convierte en un rectángulo de $L \times w$.
* En los cambios de ángulo se insertan cuñas poligonales según `join_mode`.
* Si la entrada ya es un polígono cerrado, `Stroke` genera una banda hueca de ancho $w$ centrada sobre el borde original.

### 8.5. Ejemplo
* **Contorno grueso con uniones redondeadas sobre una primitiva:**
  Aplica grosor a un trazado lineal o a una primitiva de `Shape/Library`:

  ```
  [Shape/Library: triangle] ──► Shape ──► Shape / Text ──► [Shape/Stroke: width=6, join=round] ──► Shape Out ──► Output (Return)
  ```

  En un nodo de etiquetas conectado a `System/Output (Tags)`:
  ```
  {\p1\pos(syl.center, syl.middle)\1c&HFF0066&\bord1\3c&H000000&}
  ```
  Da un triángulo hueco con un contorno de 6 px de grosor y esquinas redondeadas.

---

## 9. Nodo `Shape/Union & Divide`

Nodo de topología vectorial de Clipper con varias funciones. Descompone trazados compuestos en islas reales analizando la jerarquía de polígonos (*PolyTree*), separa subtrazados simples, une siluetas con una unión booleana o agrupa varias piezas en una sola línea de dibujo ASS intercalando bloques de etiquetas, con *keyframes* e interpolación.

![Shape/Union & Divide](img/union_&_divide.jpg)

---

### 9.1. Cabecera
1. **`[1.1] Union & Divide`:** Título del nodo.
2. **`[1.2] Botón Selector de Modo` (`mode`):** Botón de la esquina superior derecha de la barra de título que alterna entre las 4 operaciones:
   * **`[DIVIDE]` (`Dividir (PolyTree)`):** Divide la forma en islas cerradas e independientes, distinguiendo los agujeros internos.
   * **`[UNION]` (`Unir (Boolean Union)`):** Fusiona con una unión booleana dos formas o listas de trazados.
   * **`[SUB-PATHS]` (`Sub-Ruta (Naive)`):** Separa directamente por cada comando `m ...` de inicio de subtrazo.
   * **`[FUSION]` (`Fusión (Tags)`):** Agrupa varias piezas en una única línea de dibujo intercalando bloques de etiquetas ASS (`{\tags1}m... {\tags2}m...`).

---

### 9.2. Entradas específicas por modo

#### 1. `[DIVIDE]` (Dividir PolyTree)
Analiza el trazado anidado con el árbol de polígonos de Clipper (*PolyTree*). A diferencia de separar por comandos `m`, distingue los contornos exteriores de las islas con agujeros internos (por ejemplo en "O", "B", "A", "8" o kanjis complejos) y agrupa cada figura exterior con sus huecos en una pieza cerrada independiente.
* **`[2.1] Shape In`:** Trazado ASSdraw o texto a descomponer en islas.
* **`[2.2] Rule:` (`fill_type`):** Regla de devanado y relleno (`EvenOdd`, `NonZero`, `Positive`, `Negative`).
* **`[2.3] Clean:` (`clean_self_intersect`):** Limpieza automática de autointersecciones de bordes (`Auto (1)` activado, `Off (0)` desactivado).
* **`[2.4] Anchor` (`Pieces`):** `Pieces` (recentra cada pieza en su centroide local), `Relative`, `Parent Org` / `Org Padre`, `Pos`, `Absolute`.
* **`[2.5] Order:` (`order`):** Orden de iteración de las piezas (`79 (TL->BR)`, `97 (TR->BL)`, `13 (BL->TR)`, `31 (BR->TL)`, `71 (TL->BL)`, `17 (BL->TL)`, `93 (TR->BR)`, `39 (BR->TR)`, `5 (Centro)`, `-5 (Inverso)`, `cw` horario, `ccw` antihorario, `rand` aleatorio, `path` orden de dibujo original, `path_inv` orden invertido).

#### 2. `[UNION]` (Unir Boolean Union)
Combina dos siluetas superpuestas en un único trazado, uniendo las masas y eliminando las líneas internas.
* **`[2.1] Shape In (A)`:** Primera forma (`shape`).
* **`[2.1b] Shape In (B)`:** Segunda forma (`shape_b`) a fusionar con la primera.
* **`[2.2] Rule:` (`fill_type`):** Regla de relleno (`EvenOdd`, `NonZero`).
* **`[2.3] Clean:` (`clean_self_intersect`):** Limpieza automática de autointersecciones (`Auto (1)`).
* **`[2.4] Anchor` (`Pieces`):** Punto de anclaje de la figura resultante.

#### 3. `[SUB-PATHS]` (Sub-Ruta Naive)
Divide el dibujo por cada comando `m ...` sin calcular agujeros. Va bien para formas abiertas, siluetas simples o líneas de caligrafía.
* **`[2.1] Shape In`:** Trazado ASSdraw con varios comandos `m`.
* **`[2.2] Anchor` (`Pieces`):** Punto de anclaje de los subtrazados resultantes.
* **`[2.3] Order:` (`order`):** Orden de los subtrazados (`79`, `97`, `13`, `31`, `71`, `17`, `93`, `39`, `5`, `-5`, `cw`, `ccw`, `rand`, `path`, `path_inv`).

#### 4. `[FUSION]` (Fusión Tags con Keyframes)
Agrupa varias islas en una **única línea de dibujo ASS** (`{\tags1}m ... {\tags2}m ...`), lo que evita generar muchas líneas en el archivo de subtítulos. Cada pieza se puede estilizar por separado con bloques de etiquetas y transiciones de color.
* **`[2.1] Shape In`:** Trazado multitrazo, texto o lista de formas independientes a fusionar.
* **`[2.2] Tag Mode:` (`tagmode`):** Cómo se asignan las etiquetas:
  * **`ipol` (interpolado progresivo):** Trata la lista de etiquetas como *keyframes* e interpola suavemente los valores entre la primera y la última pieza ($0.0 \to 1.0$). Sirve para gradientes de color (`\1c`), rotaciones progresivas (`\frz`), transparencia (`\alpha`) o desenfoque (`\blur`).
  * **`line` (lineal 1:1 estricto):** Asigna cada bloque de etiquetas a su pieza, en orden. Si faltan etiquetas, el resto de piezas recibe `{\p1}`; si sobran, se descartan.
* **`[2.3] Tags` (`tags`):** Lista de etiquetas ASS o colores hexadecimales separados por comas o bloques (por ejemplo `\1c&H0000FF&, \1c&H00FF00&, \1c&HFF0000&` o `#87F337, #61FBC7, #AF6DF6`).
* **`[2.4] Anchor` (`Pieces`):** Anclaje espacial.
* **`[2.5] Order:` (`order`):** Orden en que se asignan o interpolan los tags sobre las piezas (`79`, `97`, `13`, `31`, `71`, `17`, `93`, `39`, `5`, `-5`, `cw`, `ccw`, `rand`, `path`, `path_inv`).

---

### 9.3. Salidas y pie del nodo
1. **`[3.1] Shape Out`:** El trazado ASSdraw resultante:
   * En los modos de división (`DIVIDE`, `SUB-PATHS`): la pieza individual de la iteración actual `d_i`.
   * En los modos de unión y fusión (`UNION`, `FUSION`): la forma única unificada o la cadena compuesta con etiquetas intercaladas.
2. **`[3.2] Out List`:** Lista JSON con todas las piezas generadas, para procesar por lotes o encadenar con otros nodos.
3. **`[3.3] BBox Data`:** Cadena con los datos del *bounding box* global (`min_x,min_y,max_x,max_y,cx,cy,width,height`).

* **Pie del nodo (`d_i, d_n`):** Variables de contexto del sub-bucle interno que genera `Union & Divide` (`d_i` = índice de la pieza actual $[1 \dots N]$, `d_n` / `d_max` = número total de piezas o islas).

---

### 9.4. Combinación con `Concatenate (Zip)`
`Union & Divide (FUSION)` combinado con `Concatenate (Zip)` permite generar varios atributos en paralelo (por ejemplo colores de gradiente, un `\blur` oscilante y desplazamientos de `\fscx`) en un único evento ASS compacto, sin artefactos de solapamiento de capas.

---

### 9.5. Ejemplo
* **Descomposición en islas con caída escalonada:**
  Divide un kanji o palabra compleja en piezas cerradas independientes (`DIVIDE`) y retrasa la caída de cada isla según `d_i`:

  ```
  [System/Input: Syl Shape] ──► Shape In ──► [Shape/Union & Divide: DIVIDE, order=79, anchor=pieces]
                                                   ├──► Shape Out ──► Return ──► [System/Output]
                                                   └──► (d_i, d_n en contexto)
  ```

  En un nodo de etiquetas conectado a `System/Output (Tags)`:
  ```
  {\p1\pos(syl.center, syl.middle)\t(d_i * 40, d_i * 40 + 300, \frz(d_i * 15)\fscx0\fscy0\alpha&HFF&)}
  ```
  Cada isla cae y rota sobre su propio centroide, 40 ms después de la anterior. Los agujeros internos se conservan (PolyTree) y la silueta general no se rompe.

---

## 10. Nodo `Shape/Clipper`

Aplica operaciones booleanas (diferencia, intersección, unión, XOR), desfases perimetrales y sumas/diferencias de Minkowski entre dos formas cerradas o abiertas, con el motor de alta precisión Clipper2. Emite código ASSdraw (`Shape Out`) o etiquetas de recorte (`\clip`, `\iclip`).

![Shape/Clipper](img/clipper.jpg)

---

### 10.1. Cabecera y modos de operación (`mode`)
1. **`[1.1] Clipper`:** Título del nodo.
2. **`[1.2] Botón Selector de Modo` (`mode`):**
   * **`difference` (`Diferencia / Sustracción A - B`):** Resta `Shape B (Clip)` de `Shape A (Subject)`. Útil para troquelar agujeros y mordiscos.
   * **`intersection` (`Intersección A ∩ B`):** Conserva solo la región donde ambas formas se superponen.
   * **`union` (`Unión A ∪ B`):** Une ambas formas en un único contorno, sin líneas internas.
   * **`xor` (`XOR / Diferencia Simétrica`):** Conserva las áreas que pertenecen a A o a B, pero no a ambas.
   * **`offset` (`Offset / Dilatación perimetral`):** Expande ($\Delta > 0$) o contrae ($\Delta < 0$) el contorno de `Shape A` la distancia indicada en `Delta (px)`, con control de uniones y remates.
   * **`minkowski_sum` (`Suma de Minkowski A ⊕ B`):** Desliza el contorno de `Shape B` a lo largo de todo el perímetro de `Shape A`, dilatándolo.
   * **`minkowski_diff` (`Diferencia de Minkowski`):** Calcula la diferencia morfológica entre los contornos de ambas formas.

---

### 10.2. Entradas y controles
1. **`[2.1] Shape A (Subject)`:** Forma principal sobre la que se aplica la operación. Si se omite, toma la geometría activa del contexto.
2. **`[2.2] Shape B (Clip)`:** Forma secundaria, usada como máscara de corte, patrón de Minkowski o segundo operando.
3. **`[2.3] Subj Fill:` (`subj_fill`):** Botón cíclico de la regla de relleno y devanado de la forma A (`EvenOdd`, `NonZero`, `Positive`, `Negative`).
4. **`[2.4] Clip Fill:` (`clip_fill`):** Botón cíclico de la regla de relleno y devanado de la forma B (`EvenOdd`, `NonZero`, `Positive`, `Negative`).
5. **`[2.5] Delta (px):` (`delta`):** Distancia del desplazamiento en píxeles para el modo `offset` (positivo dilata, negativo erosiona; admite expresiones matemáticas).
6. **`[2.6] Join Mode:` (`join_type`):** Botón cíclico del estilo de unión de esquinas en modo offset (`Round` redondeado, `Miter` inglete, `Square` cuadrado, `Bevel` biselado).
7. **`[2.7] End Mode:` (`end_type`):** Botón cíclico del remate de extremos de trazados abiertos o cerrados (`Closed Polygon`, `Closed Line`, `Open Round`, `Open Square`, `Open Butt`).
8. **`[2.8] Miter Limit:` (`miter_limit`):** Límite máximo de inglete antes de biselar las esquinas agudas (default: `2.0`).
9. **`[2.9] Post-Offset:` (`post_offset`):** Desfase adicional aplicado al resultado de las operaciones booleanas (`difference`, `intersection`, `union`, `xor`, `minkowski`). Expande ($\text{px} > 0$) o contrae ($\text{px} < 0$) el resultado sin encadenar un segundo nodo Clipper. Admite expresiones matemáticas; vacío o en `0.0` no aplica post-offset.
10. **`[2.10] Clean Dist:` (`clean_dist`):** Distancia umbral en píxeles para eliminar micro-vértices colineales o degenerados con `CleanPolygons` ($0.0 = \text{desactivado}$).
11. **`[2.11] Simple:` (`strictly_simple`):** Conmutador (`FALSE` / `TRUE`). Fuerza polígonos estrictamente simples, sin autointersecciones ni vértices coincidentes.
12. **`[2.12] Rev Subj:` (`reverse_subj`):** Conmutador (`FALSE` / `TRUE`). Invierte el sentido de devanado de la forma sujeto.
13. **`[2.13] Rev Clip:` (`reverse_clip`):** Conmutador (`FALSE` / `TRUE`). Invierte el sentido de devanado de la forma de corte.
14. **`[2.14] Anchor:` (`anchor`):** Desplegable de anclaje (`center`, `origin`, `relative`, `absolute`). En `relative` conserva el origen sin recentrar sobre los extremos de la tinta.
15. **`[2.15] Out Mode:` (`out_mode`):** Botón cíclico del formato de salida (`Shape` código ASSdraw plano, `Clip` etiqueta `\clip(...)`, `iClip` etiqueta `\iclip(...)`).

---

### 10.3. Salidas
1. **`[1.1] Shape Out`:** El código ASSdraw resultante o la etiqueta `{\clip(...)}` / `{\iclip(...)}`.
2. **`[1.2] Out List`:** Lista de las piezas o islas resultantes, para encadenar o procesar en bucles.
3. **`[1.3] BBox Data`:** Diccionario con las métricas del cuadro delimitador (`x1`, `y1`, `x2`, `y2`, `cx`, `cy`, `w`, `h`).

---

### 10.4. Ejemplo
* **Troquelado de una estrella con post-offset:**
  Resta una estrella (`Shape B`) del glifo de la sílaba (`Shape A`) en modo `difference`, con un post-offset de dilatación:

  ```
  [System/Input: Syl Shape] ──► Shape A (Subject) ──┐
                                                    ├──► [Shape/Clipper: difference, Post-Offset=1.5]
  [Shape/Library: star] ────► Shape B (Clip) ─────┘          └──► Shape Out ──► Return ──► [System/Output]
  ```

  En un nodo de etiquetas conectado a `System/Output (Tags)`:
  ```
  {\p1\pos(syl.center, syl.middle)\1c&HFFFFFF&\bord2\3c&HFF0055&}
  ```
  La estrella queda perforada en el glifo y el resultado se expande 1.5 px.

---

## 11. Nodo `Shape/Array`

Repite una forma en una rejilla regular, una malla hexagonal, anillos concéntricos, una espiral, una dispersión aleatoria o una silueta guía. Puede iterar pieza por pieza (`LOOPS`) o generar un único dibujo combinado (`SHAPE`).

![Shape/Array](img/array.jpg)

---

### 11.1. Botones de la cabecera
1. **`[1.1] Array`:** Título del nodo.
2. **`[1.2] Modo de Salida / Ejecución` (`out_mode`):**
   * **`[LOOPS]`:** Itera elemento por elemento con las variables de contexto `a_i` (índice actual) y `a_n` (total de elementos). En cada ciclo emite una partícula en el puerto `Piece`, con su `\pos(x,y)` individual, y expone su ángulo `\frz`, columna, fila o anillo. El pie del nodo muestra `a_i, a_n`.
   * **`[SHAPE]`:** Fusiona todas las instancias en una **única cadena ASSdraw continua** (`m ... l ... b ... m ...`) y renombra el primer puerto de salida a `Shape Out`. Si se conecta una lista de etiquetas al puerto `Tags`, hace una fusión vectorial intercalando bloques de estilos (`{\tags1}m... {\tags2}m...`). No se generan líneas duplicadas en el ASS: fija `a_i = 1`, `a_n = 1` y muestra `Single shape.` (*Un solo shape.*) en el pie del nodo.
3. **`[1.3] Modo de Formación Geométrica` (`mode`):** Elige una de las 6 distribuciones:
   * **`[GRID]` (rejilla ortogonal):** Matriz de columnas $\times$ filas con espaciado independiente en $X$ e $Y$.
   * **`[FORM]` (lattice sobre silueta guía):** Distribuye partículas sobre los vértices o el relleno de una forma o texto externo.
   * **`[RINGS]` (anillos concéntricos):** Anillos con paso de radio y rotación angular por anillo.
   * **`[SPIRAL]` (espiral paramétrica):** Distribución a lo largo de una espiral, con control de vueltas y radio máximo.
   * **`[SCATTER]` (dispersión aleatoria):** Nube de partículas pseudoaleatoria dentro de un área rectangular, con semilla reproducible.
   * **`[HEX]` (panal de abeja):** Rejilla hexagonal con filas impares desplazadas a $60^\circ$ ($\Delta y = \Delta x \cdot \frac{\sqrt{3}}{2}$).

---

### 11.2. Parámetros universales
1. **`[2.1] Particle`:** Código ASSdraw de la forma o partícula a replicar (por ejemplo círculo, estrella, diamante, polígono o fragmento vectorial).
2. **`[2.6] Scale`:** Multiplicador de escala de cada partícula ($1.0 = 100\%$).
3. **`[2.7] Factor (t)` (`t` / `progress`):** Progresión ($0.0 \to 1.0$) que controla cuántas partículas se generan o se ven, según el orden espacial:
   $$\text{Visibles} = \text{round}(\text{Total} \cdot t)$$
   Sirve para animar la aparición secuencial de la formación.
4. **`[2.8] Anchor`:**
   * **`Piece` (`Piezas`):** Centra cada partícula en su propio centroide e inyecta `\pos(x_i, y_i)` y `\org(x_i, y_i)` con la posición absoluta de esa celda en pantalla.
   * **`Relativo`:** Dibuja las partículas respecto al centroide del padre (`parent_x, parent_y`) sin alterar las coordenadas base de la línea.
   * **`Parent Org` (`Org Padre`, `parent_org`):** Pone el origen `\org` en el centro del texto o sílaba padre, para girar todo el conjunto alrededor de la palabra con las piezas dispersas.
   * **`Pos`:** Inyecta solo `\pos(x_i, y_i)` y desactiva la escritura de `\org`.
   * **`Absoluto`:** Proyecta las coordenadas en el espacio absoluto del lienzo y fija `\pos(0,0)`.
5. **`[2.9] Order:`:** Orden de los índices $a\_i = 1 \dots N$ y de aparición al animar `Factor (t)`:
   * **Teclado numérico:** `79 (TL->BR)` (izquierda a derecha, de arriba abajo), `97` (derecha a izquierda, de arriba abajo), `13` (izquierda a derecha, de abajo arriba), `31` (derecha a izquierda, de abajo arriba), `71` (por columnas, de arriba abajo), `17` (por columnas, de abajo arriba).
   * **Centro y radiales:** `5` (desde el centroide hacia los bordes), `cw` (sentido horario), `ccw` (sentido antihorario).
6. **`[2.10] Tags`:** Cadena de etiquetas ASS o colores para fusionar con `out_mode = Shape` o para evaluar por instancia.
7. **`[2.11] a_i, a_n`:** Variables de iteración del pie del nodo (`a_i` = índice del elemento actual $[1 \dots N]$, `a_n` = total de elementos de la formación).

---

### 11.3. Entradas específicas por modo

#### 1. `[GRID]`
* **`[2.2] Cols`:** Número de columnas (default: `5`).
* **`[2.3] Rows`:** Número de filas (default: `3`).
* **`[2.4] Spacing X`:** Espacio horizontal en píxeles entre centros de celdas contiguas (default: `0`).
* **`[2.5] Spacing Y`:** Espacio vertical en píxeles entre centros de filas contiguas (default: `0`).

#### 2. `[FORM]`
* **`[2.2] Formation`:** Código ASSdraw o texto guía, usado como silueta sobre la que se muestrean y colocan las partículas.
* **`[2.3] Spacing`:** Paso de muestreo entre partículas adyacentes.

#### 3. `[RINGS]`
* **`[2.2] Rings`:** Número de anillos concéntricos (default: `3`).
* **`[2.3] Count / Ring`:** Partículas por anillo. Puede ser un único valor (por ejemplo `8`) o una lista separada por comas para dar densidades crecientes por capa (por ejemplo `6, 12, 18, 24`). Si se deja vacío, el nodo calcula la cantidad óptima según el perímetro de cada anillo:
  $$N_k = \text{round}\left(\frac{2 \pi \cdot R_k}{\text{Diámetro} + \text{Spacing}}\right)$$
* **`[2.4] Radius`:** Radio del primer anillo interior en píxeles (default: `50.0`).
* **`[2.5] Radius Step`:** Incremento de radio entre anillos consecutivos (default: `30.0`).
* **`[2.5b] Rotate Step`:** Desfase angular en grados que se aplica a cada anillo sucesivo, para crear patrones entrelazados o en espiral (default: `0.0`).

#### 4. `[SPIRAL]`
* **`[2.2] Count`:** Número de partículas a lo largo de la espiral (default: `20`).
* **`[2.3] Turns`:** Número de vueltas completas de $360^\circ$ (default: `2.0`).
* **`[2.4] Max Radius`:** Radio exterior en el extremo de la espiral (default: `100.0`).
* **`[2.5] Angle Step`:** Incremento angular fijo en grados entre partículas consecutivas. Si es `0`, el ángulo se calcula uniformemente según las vueltas totales:
  $$\theta_i = t_i \cdot \text{Turns} \cdot 360^\circ \quad \text{donde} \quad t_i = \frac{i}{N - 1}$$

#### 5. `[SCATTER]`
* **`[2.2] Count`:** Número de partículas aleatorias (default: `20`).
* **`[2.3] Width` (`area_width`):** Ancho del área rectangular de dispersión en píxeles (default: `150.0`).
* **`[2.4] Height` (`area_height`):** Alto del área rectangular de dispersión en píxeles (default: `100.0`).
* **`[2.5] Seed`:** Semilla pseudoaleatoria determinista. La misma semilla genera exactamente la misma distribución en cada fotograma.

#### 6. `[HEX]`
* **`[2.2] Cols`:** Número de columnas (default: `5`).
* **`[2.3] Rows`:** Número de filas (default: `3`).
* **`[2.4] Spacing`:** Separación adicional entre celdas hexagonales.

---

### 11.4. Salidas
1. **`[3.1] Piece` / `Shape Out`:** Trazado ASSdraw emitido:
   * En `[LOOPS]`, con el nombre **`Piece`**: el código ASSdraw de la partícula de la iteración $a\_i$.
   * En `[SHAPE]`, con el nombre **`Shape Out`**: el trazado combinado con todas las partículas ya colocadas y fusionadas.
2. **`[3.2] \pos Tag`:** Etiqueta `\pos(x, y)` de la partícula actual.
3. **`[3.3] X`:** Coordenada $X$ absoluta en píxeles de la partícula actual.
4. **`[3.4] Y`:** Coordenada $Y$ absoluta en píxeles de la partícula actual.
5. **`[3.5] Angle (\frz)`:** Ángulo tangencial o de rotación en grados ($\theta$) de la partícula (útil para orientar flechas o estrellas en `Rings` o `Spiral`).
6. **`[3.6] Index (a_i)`:** Índice del elemento actual ($1 \dots a\_n$).
7. **`[3.7] Total (a_n)`:** Número total de partículas de la formación.
8. **`[3.8] Col / Ring`:** Índice de la columna activa (en `Grid` / `Hex`) o número del anillo actual (en `Rings`).
9. **`[3.9] Row / IdxRing`:** Índice de la fila activa (en `Grid` / `Hex`) o posición del elemento dentro de su anillo (en `Rings`).

### 11.5. Ejemplo
* **Anillo de estrellas alrededor de la sílaba:**
  Un anillo de 12 estrellas que orbitan la sílaba, cada una orientada según la tangente (`mode: rings, out_mode: loops, rings: 1, count: 12, radius: 45`):

  ```
  [Shape/Library: star] ──► Particle ──► [Shape/Array: rings, count=12, r=45]
                                               ├──► Piece ──► Return ──► [System/Output]
                                               ├──► \pos Tag ──► Tags ──► [System/Output]
                                               └──► Angle (\frz) ──► (angle)
  ```

  En un nodo de etiquetas conectado a `System/Output (Tags)`:
  ```
  {\p1\pos(x, y)\frz(angle)\1c&H00FFFF&\bord0\t(0, 300, \fscx150\fscy150\1c&HFF0088&)}
  ```
  Cada una de las 12 estrellas queda sobre la circunferencia y mira hacia fuera, siguiendo el ángulo tangencial calculado.

---

## 12. Nodo `Shape/IMG to Shape`

Vectoriza imágenes (PNG, JPG, WebP) o GIFs animados en trazados ASSdraw (`m`, `l`, `b`), con el motor Potrace integrado, aproximación poligonal (Douglas-Peucker) o extracción de contornos por gradiente.

![Shape/IMG to Shape](img/img_to_shape.jpg)

### 12.1. Carga de archivos y navegación de fotogramas
1. **Cargar un archivo:**
   Un doble clic en la tarjeta de previsualización (*Preview Card*) o en cualquier zona vacía del cuerpo del nodo abre el selector de archivos del sistema para elegir un `.png`, `.jpg`, `.jpeg`, `.webp` o `.gif`. La ruta seleccionada se escribe en `image_path`.
2. **Controles de GIF animado:**
   Si el archivo tiene varios fotogramas (`total_frames > 1`), aparecen los controles de transporte:
   * Botones de paso de cuadro `[◀]` y `[▶]`.
   * Barra horizontal de desplazamiento (*scrubber*) para revisar la vectorización cuadro a cuadro.

### 12.2. Modos de vectorización (`mode`)
1. **`potrace`:** Splines suaves de curvas Bézier cúbicas (`m`, `l`, `b`), construidas con una descomposición poligonal intermedia, cálculo de curvatura en las esquinas y aproximación subpíxel.
2. **`polygon`:** Aproximación poligonal rectilínea estricta (`m`, `l`) con el algoritmo de Douglas-Peucker. Reduce el número de vértices y conserva los ángulos nítidos.
3. **`borders`:** Detección de contornos a partir del gradiente de luminancia (operador Sobel).

### 12.3. Modos de binarización (`bin_mode`)
1. **`luminance`:** Compara el brillo en escala de grises de cada píxel con el umbral `threshold` ($0 \dots 255$).
2. **`silhouette` / `alpha`:** Compara el canal alfa de imágenes PNG/WebP transparentes con el umbral.
3. **`borders`:** Binariza a partir de las derivadas del mapa de intensidad.

### 12.4. Entradas y propiedades
1. **`[2.1] Image Path` (`image_path`):** Ruta absoluta o relativa a la imagen o GIF animado.
2. **`[2.2] Frame (j)` (`frame_idx`):** Índice del fotograma a decodificar ($1 \dots \text{Total Frames}$). Si se deja vacío o en `"1"` al cargar un GIF, se enlaza con la variable de iteración `ish_i` o `j` para emitir la animación completa en bucle.
3. **`[2.3] Threshold` (`threshold`):** Umbral de binarización ($0 \dots 255$, defecto: `128`).
4. **`[2.4] Tolerance` (`tolerance`):** Tolerancia de simplificación de vértices intermedios (defecto: `1.0`).
5. **`[2.5] Smoothing` (`alphamax`):** Curvatura máxima en esquinas para Potrace (defecto: `1.0`).
6. **`[2.6] Optimization` (`opttoler`):** Tolerancia para fusionar curvas Bézier (defecto: `0.2`).
7. **`[2.7] Scale Out` (`out_scale`):** Multiplicador de escala del trazado final (defecto: `1.0`).
8. **`[2.8] Width Out` (`out_w`) / `Height Out` (`out_h`):** Tamaño forzado en píxeles. Con `0.0` se respeta el tamaño original.
9. **`[2.9] Offset X` (`offset_x`) / `Offset Y` (`offset_y`):** Desplazamiento en píxeles aplicado a los vértices.
10. **`[2.10] Image Scale` (`img_scale`):** Reescalado del mapa de bits antes del análisis vectorial.
11. **`[2.11] Binarize Mode` (`bin_mode`):** Método de segmentación (`luminance`, `silhouette`, `borders`).
12. **`[2.12] Anchor` (`anchor`):**
    * `center`: Centra el centroide del trazado en `(0, 0)`.
    * `origin`: Pone la esquina superior izquierda en `(0, 0)`.
    * `relative`: Conserva las coordenadas originales del archivo.
    * `absolute`: Suma las coordenadas del contexto `(fx.pos_x, fx.pos_y)` para colocarlo en pantalla.
13. **`invert` / `invert_img`:** Conmutadores para invertir primer plano/fondo o invertir los canales de la imagen antes de binarizar.

### 12.5. Salidas
1. **`[1.1] Shape Out`:** Trazado ASSdraw (`m ... l ... b ...`) del fotograma procesado.
2. **`[1.2] Width`:** Ancho en píxeles del trazado resultante.
3. **`[1.3] Height`:** Alto en píxeles del trazado resultante.
4. **`[1.4] Points`:** Número total de vértices y puntos de control.
5. **`[1.5] Shapes Array`:** Lista de islas independientes, para procesar por piezas.
6. **`[1.6] Total Frames`:** Número de fotogramas detectados en el archivo. Define `ish_n` e `ish_max` en el contexto.

### 12.6. Ejemplo
* **GIF animado reproducido como vectores:**
  Encadena `MaxLoop (fbf)` con `Shape/IMG to Shape`:

  ```
  [MaxLoop: fbf, step_ms=41.7] ──► Loop In ──► [System/Output]
                               ──► Counter ──► Frame (j) ──► [IMG to Shape: logo.gif] ──► Shape Out ──► Output (Return)
  ```

  En un nodo de etiquetas conectado a `System/Output (Tags)`:
  ```
  {\p1\pos(syl.center, syl.middle)\1c&HFFFFFF&\bord0}
  ```
  Cada fotograma de vídeo dibuja el cuadro $j$ del GIF como gráfico vectorial, sin pixelado.

---

## 13. Nodo `Shape/Multi`

Genera patrones poligonales anidados, retículas concéntricas y otras formas compuestas paramétricas.

![Shape/Multi](img/multi.jpg)

### 13.1. Algoritmos de generación (`mode`)
El nodo incluye 10 algoritmos:
1. **`concentric_squares`:** Cuadrados concéntricos anidados, con grosor y paso configurables.
2. **`diagonal_stripes`:** Trama de franjas diagonales dentro de una caja de ancho `width` y alto `height`.
3. **`concentric_rings`:** Anillos circulares concéntricos, o basados en una silueta guía (`base_shape`).
4. **`polygonal_mosaic`:** Mosaico poligonal regular definido por el número de lados (`sides`) y de capas concéntricas (`n_layers`).
5. **`multi_shape_mosaic`:** Retícula modular de formas con paso de traslación horizontal y vertical (`dx`, `dy`).
6. **`segmented_border`:** Marco segmentado con intervalos regulares y muescas de longitud `length`.
7. **`radial_rosette`:** Roseta circular de pétalos o sectores radiales (`parts`, `r_out`, `r_in`).
8. **`tunnel_cascade`:** Túnel de formas de escala decreciente (`size1`, `size2`), con repeticiones (`loop`) y rotación progresiva (`angle`).
9. **`banner`:** Placa decorativa o cinta con terminales configurables (`tip_style`: Arrow, Fold) y pestañas laterales.
10. **`gear`:** Engranaje con número de dientes (`teeth`), radio exterior (`r_out`), radio interior (`r_in`) y orificio central (`r_hole`).

### 13.2. Entradas y propiedades
1. **`Mode` (`mode`):** Elige el algoritmo.
2. **`Size` (`size`):** Tamaño base del patrón exterior (default: `100.0`).
3. **`Px Pattern` (`px_pattern`):** Secuencia de grosores o separaciones (admite un número o una lista separada por comas).
4. **`Separation` (`separation`):** Separación entre capas o elementos adyacentes.
5. **`Factor (t)` (`t`):** Progresión ($0.0 \to 1.0$) para animar la aparición o la escala de las capas.
6. **`Anchor` (`anchor`):**
   * **`center`:** Centra la forma generada en `(0, 0)`.
   * **`origin`:** Pone la esquina superior izquierda de la caja delimitadora en `(0, 0)`.
   * **`relative`:** Conserva el desplazamiento relativo al padre, sin recentrar.
   * **`absolute`:** Coloca la forma en las coordenadas de pantalla `(fx.pos_x, fx.pos_y)`.
7. **`Tags` (`tags`):** Etiquetas ASS o colores a intercalar en el código emitido.
8. **`Out Mode` (`out_mode`):** Formato de salida (`Shape`, `\clip`, `\iclip`).
9. **`Loop Mode` (`loop_mode`):** Alterna entre un dibujo combinado (`Shape`) y la iteración pieza por pieza (`Loops`, que expone las variables de contexto `m_i` y `m_n`).

### 13.3. Salidas
1. **`[3.1] Shape`:** Código ASSdraw combinado (o la pieza activa en modo `Loops`).

### 13.4. Ejemplo
* **Placa decorativa detrás del diálogo:**
  Configura `Shape/Multi` con `mode: banner`, `width: 260`, `height: 48` y `anchor: center`:

  ```
  [Shape/Multi: banner, w=260, h=48] ──► Shape ──► Return ──► [System/Output]
  ```

  En un nodo de etiquetas conectado a `System/Output (Tags)` con una capa inferior (`layer: 0`):
  ```
  {\p1\pos(line.center, line.middle)\1c&H1A1A2E&\bord2\3c&HE94560&}
  ```
  Dibuja un estandarte poligonal centrado detrás de la línea de diálogo, que hace de placa de título.

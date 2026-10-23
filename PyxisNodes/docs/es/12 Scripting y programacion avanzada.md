# Scripting y Programación Avanzada (`System/Script Code`)

El nodo **`System/Script Code`** ejecuta código Python o Lua para procesar datos, calcular movimiento y generar etiquetas ASS o trazados vectoriales. Esta página describe sus puertos, las variables que se inyectan en el script, el catálogo de funciones incluidas y el despachador determinista `by`.

---

## 1. Puertos y Propiedades

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

### 1.1. Puertos de Entrada (*Inputs*)
1. **`[0] Loop In` (Control / Contexto):** Recibe el flujo de iteración activo (`line`, `syl`, `word`, `char`, `MaxLoop`, `Slicer`). Da al script acceso a los tiempos y métricas de la unidad actual y mantiene la cadena conectada con `System/Output`.
2. **`[1] In1`, `[2] In2`, ..., `[N] InN` (Datos):** Entradas dinámicas (de 1 a 16), disponibles en el script como las variables globales `in1`, `in2`, ..., `inN` (o con el nombre del cable entrante). Si no hay un cable conectado, toman el valor del campo de texto del nodo.

### 1.2. Puertos de Salida (*Outputs*)
1. **`[0] Loop Out` (Control / Contexto):** Reenvía el contexto de iteración. Cualquier etiqueta ASS o variable generada en el script viaja por este puerto hacia los nodos siguientes o hacia `System/Output`.
2. **`[1] Result` (Cadena / Dato):** Salida principal del script: el valor asignado a `result` o el de la última expresión.
3. **`[2] Out1` ... `[N] OutN` (Opcionales):** Se crean cuando el script asigna valores al diccionario `outputs` (en Python: `outputs['out1'] = ...` o `out1 = ...`; en Lua: `outputs.out1 = ...` o `out1 = ...`).

### 1.3. Propiedades del Cuerpo (*Properties*)
1. **`language` (`Language`):** `"Python"` o `"Lua"`. Tipo C (selector literal).
2. **`inputs_count` (`Inputs Count`):** Número de ranuras de entrada dinámicas (1 a 16). Tipo C (entero).
3. **`script` (`Script Code`):** Código fuente. Tipo A (código fuente evaluado y validado mediante AST).

---

## 2. Ejecución y Preprocesamiento

### 2.1. Resultado y Fusión Automática de Etiquetas
La salida del script se toma de uno de estos dos sitios:
1. **Asignación explícita:** `result = ...` (en Python o Lua).
2. **Última expresión:** Si la última línea del script es una expresión suelta (por ejemplo, `pos(syl.x, syl.y) + fscxy(120)`), el motor asigna su valor a `result`.

> [!IMPORTANT]
> **Fusión automática de etiquetas:** Si la cadena de `result` contiene sintaxis de etiquetas ASS (`\` o `{...}`), Pyxis la fusiona en `context["loop_tags"]` con `merge_ass_tags`. No hace falta conectar un nodo combinador de etiquetas: las etiquetas que devuelve el script acaban en la línea que genera `System/Output`.

### 2.2. Salida Mixta: Tags más Dibujo Vectorial o Texto en `result`

¿Qué ocurre cuando el script emite a la vez etiquetas y contenido imprimible (por ejemplo `result = f"{{{pos(syl.x, syl.y)}\\p1}}{shape_star()}"` o `result = "{\\c&HFF&}Texto"`)? Depende de cómo esté conectado el nodo a `System/Output`.

1. **Script Code solo está en el flujo del bucle (`Loop In` $\to$ `Loop Out`), sin cablear `Result`:**
   * Pyxis detecta los caracteres `\` o `{` y fusiona la cadena en `context["loop_tags"]` mediante `merge_ass_tags`.
   * `merge_ass_tags` toma los bloques dentro de `{...}` para el encabezado de etiquetas, pero **no sustituye el contenido imprimible de la línea**.
   * El puerto `Return` de `System/Output` (por defecto, el texto original de la sílaba `syl.text_stripped`) sigue decidiendo el texto o dibujo de la línea. Una forma vectorial devuelta fuera de las llaves en `result` no reemplaza a la sílaba.

2. **`Result` conectado al puerto `Return` (puerto 5) de `System/Output`:**
   * La cadena completa pasa directamente al renderizado final.
   * `System/Output` la procesa con **`evaluate_ass_line_tag_blocks()`**, que:
     - detecta `\p1` o comandos de dibujo ASSdraw (`m `, `l `, `b `, etc.);
     - valida, limpia y fusiona los bloques de tags `{...}`;
     - deja el trazado vectorial o el texto posterior **100% intacto**.
   * Línea de diálogo ASS resultante:
     ```ass
     Dialogue: 0,0:00:01.00,0:00:03.00,Default,,0,0,0,,{\pos(640,360)\p1\1c&HFFFFFF&}m 0 0 l 50 0 l 25 -50
     ```

#### Tres Formas de Emitir Tags más Shape/Texto
* **Método A (línea completa en `Result` $\to$ cable a `Return`):**
  ```python
  tags = pos(syl.x, syl.y) + r"\p1" + c1(syl.color1)
  dibujo = shape_star()
  result = f"{{{tags}}}{dibujo}"
  # Conexión: Result -> puerto Return (5) de System/Output
  ```
* **Método B (separación con `outputs`, recomendado):**
  ```python
  # Tags emitidos automáticamente por Loop Out
  result = pos(syl.x, syl.y) + r"\p1" + c1("&H00FFFF&") + fscxy(120)
  # Dibujo vectorial emitido por sub-salida
  outputs['out1'] = shape_circle()
  # Conexión: Out1 -> puerto Return (5) de System/Output
  ```
* **Método C (inyección directa en el contexto):**
  ```python
  context["return_raw"] = shape_heart()
  result = pos(syl.x, syl.y) + r"\p1" + c1("&H0000FF&")
  ```

### 2.3. Atajos Sintácticos
Antes de compilar, el motor reescribe algunos atajos mediante expresiones regulares:
* **Multiplicadores de tiempo:**
  * `2li` $\to$ `2 * li`
  * `-1.5lo` $\to$ `-1.5 * lo`
  * `3m1` $\to$ `3 * m1`
* **Frames y ratios:**
  * `10f` $\to$ `(10 * frame_dur)` (10 fotogramas en milisegundos según el FPS del proyecto).
  * `1.5r` $\to$ `(1.5 * ratio)` (escala la magnitud espacial según el ratio de aspecto o módulo activo).

---

## 3. Variables Inyectadas

El script recibe estos valores, de solo lectura, para la unidad que se está procesando.

### 3.1. Sílaba (`syl`)
La sílaba en curso dentro del bucle de karaoke:

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `syl.text` | `str` | Texto limpio de la sílaba (sin tags de karaoke ni de formato). |
| `syl.text_stripped` | `str` | Texto sin espacios ni saltos de línea superfluos. |
| `syl.i` | `int` | Índice de la sílaba dentro de la línea ($1 \le i \le n$). |
| `syl.n` | `int` | Número total de sílabas en la línea. |
| `syl.duration` / `syl.dur` | `int` | Duración de la sílaba en milisegundos (tiempo $\backslash k$). |
| `syl.start_time` / `syl.st` | `int` | Tiempo absoluto de inicio en milisegundos. |
| `syl.end_time` / `syl.et` | `int` | Tiempo absoluto de fin en milisegundos. |
| `syl.mid_time` | `float` | Punto medio absoluto ($\frac{st + et}{2}$). |
| `syl.syl_start` | `int` | Desfase de inicio en milisegundos respecto al inicio de la línea. |
| `syl.syl_end` | `int` | Desfase de fin en milisegundos respecto al inicio de la línea. |
| `syl.x`, `syl.y` | `float` | Posición $(X, Y)$ calculada según la alineación y estilo de la sílaba. |
| `syl.center`, `syl.middle` | `float` | Coordenadas del centro de la caja de la sílaba. |
| `syl.left`, `syl.right` | `float` | Límites horizontales (caja tipográfica envolvente). |
| `syl.top`, `syl.bottom` | `float` | Límites verticales (caja tipográfica envolvente). |
| `syl.width`, `syl.height` | `float` | Dimensiones tipográficas calculadas con métricas GDI/FreeType. |
| `syl.color1` ... `syl.color4` | `str` | Colores ASS del estilo base (`&HBBGGRR&`). |
| `syl.fontsize` | `float` | Tamaño nominal de la fuente en puntos. |
| `syl.fontname` | `str` | Nombre de la familia tipográfica. |
| `syl.bold`, `syl.italic` | `bool` | Banderas de negrita y cursiva. |
| `syl.is_first`, `syl.is_last` | `bool` | `True` si es la primera o la última sílaba de la línea. |
| `syl.has_prev`, `syl.has_next` | `bool` | `True` si hay una sílaba anterior o posterior. |

### 3.2. Línea de Diálogo (`line` / `l`)
La línea de subtítulo de Aegisub a la que pertenece la unidad:
* `line.text`: Texto completo sin tags ASS.
* `line.raw_text`: Cadena original con todos sus tags de formato y override.
* `line.start_time`, `line.end_time`, `line.duration`: Tiempos absolutos de la línea (en ms).
* `line.i`, `line.n`: Número correlativo de la línea y total de líneas seleccionadas.
* `line.layer`: Capa ASS del diálogo (entero).
* `line.style`: Nombre del estilo asignado en Aegisub.
* `line.actor`, `line.effect`: Campos Actor y Efecto de la línea.
* `line.margin_l`, `line.margin_r`, `line.margin_v`: Márgenes de pantalla configurados.
* `line.width`, `line.height`: Ancho y alto tipográfico de la línea renderizada.
* `line.center`, `line.middle`, `line.left`, `line.right`, `line.top`, `line.bottom`: Límites espaciales de la línea en pantalla.

### 3.3. Carácter (`char`) y Palabra (`word`)
Si el bucle itera por caracteres o palabras, `char` y `word` exponen las mismas propiedades métricas que `syl`:
* Posición: `char.x`, `char.y`, `char.center`, `char.middle`, `char.width`, `char.height`.
* Tiempos: `char.start_time`, `char.end_time`, `char.duration`, `char.char_start`, `char.char_end`.
* Índices: `char.i`, `char.n`, `char.is_first`, `char.is_last`.

### 3.4. Cuadro de Efecto (`fx`)
Se aplica cuando nodos cinemáticos o sistemas de partículas mueven la posición de renderizado respecto a la línea original:
* `fx.pos_x`, `fx.pos_y` (o `fx.x`, `fx.y`): Coordenadas actuales del punto de emisión.
* `fx.org_x`, `fx.org_y`: Centro de rotación y escalado ($\backslash org$).
* `fx.start_time`, `fx.end_time`, `fx.dur`: Ventana temporal activa de la línea resultante.
* `fx.i`, `fx.n`: Índice de la partícula o clon generado en la iteración y total del grupo de emisión.

### 3.5. Métricas de Tinta Real (`ink`)
Las dimensiones nominales (`syl.width`, `syl.height`) incluyen espacios en blanco, ascendentes y márgenes de interletraje. `ink` describe en cambio el **bounding box exacto de los vectores dibujados**:
* `ink.width`, `ink.height`: Anchura y altura real del glifo trazado.
* `ink.center`, `ink.middle`: Centroide geométrico del glifo real.
* `ink.left`, `ink.right`, `ink.top`, `ink.bottom`: Coordenadas absolutas de los bordes del dibujo.

### 3.6. Unidades Vecinas (`prev` y `next`)
Permiten leer la unidad anterior o siguiente, por ejemplo para efectos en cadena o desfases relativos:
* `prev.text`, `prev.x`, `prev.y`, `prev.start_time`, `prev.duration`
* `next.text`, `next.x`, `next.y`, `next.start_time`, `next.duration`
* Si no existe unidad previa o siguiente (primera o última sílaba), `prev` y `next` devuelven objetos proxy con valores neutros (`0`, `""`), de modo que no se lanza `NullReferenceException` ni `AttributeError`.

### 3.7. Variables Globales e Iteradores de Malla
* `s_i`, `s_n`: Índice y total de piezas generadas por el nodo `Shape/Slicer`.
* `col`, `row`: Columna y fila en mallas de corte 2D.
* `j`, `maxloop`: Índice y total de repeticiones en el nodo `Loops/MaxLoop`.
* `a_i`, `a_n`: Índice y total de elementos en matrices o partículas.
* `frame_dur` (alias `fd`): Duración en ms de un fotograma ($1000 / FPS$, típicamente $41.7\,\text{ms}$ a 23.976 fps o $16.6\,\text{ms}$ a 60 fps).
* `fps`: Tasa de fotogramas por segundo del proyecto.

---

## 4. Funciones Incluidas

Estas funciones replican el comportamiento de los nodos nativos de Pyxis.

### 4.1. Generadores de Etiquetas ASS

Todas las funciones de etiquetas formatean los números con hasta 3 decimales y omiten los ceros sobrantes (por ejemplo `pos(100.0, 200.5)` $\to$ `\pos(100,200.5)`):

| Función | Salida Generada | Descripción |
| :--- | :--- | :--- |
| `pos(x, y)` | `\pos(x,y)` | Posición absoluta en pantalla. |
| `move(x1, y1, x2, y2, [t1, t2])` | `\move(...)` | Desplazamiento lineal entre dos puntos con ventana de tiempo opcional. |
| `org(x, y)` | `\org(x,y)` | Punto de pivote para rotaciones ($\backslash frz, \backslash frx, \backslash fry$) y escalas. |
| `fad(tin, tout)` | `\fad(tin,tout)` | Desvanecimiento de entrada y salida en milisegundos. |
| `fade(a1, a2, a3, t1, t2, t3, t4)` | `\fade(...)` | Desvanecimiento con 3 alfas y 4 puntos temporales. |
| `clip(x1, y1, x2, y2)` | `\clip(x1,y1,x2,y2)` | Recorte rectangular. |
| `clip(shape_str)` | `\clip(dibu)` | Recorte vectorial según dibujo ASS. |
| `iclip(...)` | `\iclip(...)` | Recorte invertido (rectangular o vectorial). |
| `c1(col)`, `c2(col)`, `c3(col)`, `c4(col)` | `\1c...`, `\2c...`, etc. | Color primario, karaoke, borde y sombra (`&HBBGGRR&` o `#RRGGBB`). |
| `a1(val)`, `a2(val)`, `a3(val)`, `a4(val)` | `\1a...`, `\2a...`, etc. | Opacidad por canal (`&HAA&`, de 0 a 255). |
| `alpha(val)` | `\alpha&HAA&` | Opacidad global del elemento. |
| `fscx(v)`, `fscy(v)` | `\fscx...`, `\fscy...` | Escalado porcentual horizontal y vertical ($100 = 100\%$). |
| `fscxy(x, [y])` | `\fscx...\fscy...` | Ambas etiquetas de escala en una sola llamada. |
| `frz(deg)` | `\frz...` | Rotación sobre el eje Z (grados). |
| `frx(deg)`, `fry(deg)` | `\frx...`, `\fry...` | Rotación 3D sobre los ejes X e Y. |
| `fax(v)`, `fay(v)` | `\fax...`, `\fay...` | Deformación por cizallamiento (*shear*). |
| `bord(px)` | `\bord...` | Grosor del contorno en píxeles. |
| `shad(px)` | `\shad...` | Distancia de la sombra en píxeles. |
| `blur(sigma)` | `\blur...` | Desenfoque gaussiano (sigma en píxeles). |
| `an(numpad)` | `\an...` | Alineación del texto o forma (notación numpad del 1 al 9). |
| `trans([t1, t2], [accel], tags)` | `\t(...)` | Anima tags entre $t_1$ y $t_2$ con aceleración opcional. |
| `ass_color(r, g, b)` | `&HBBGGRR&` | Convierte RGB decimal ($0-255$) a hexadecimal BGR de ASS. |
| `ass_alpha(val)` | `&HAA&` | Convierte transparencia ($0-255$) a hexadecimal ASS. |
| `random_color()` | `&HBBGGRR&` | Color aleatorio en formato ASS. |
| `random_alpha()` | `&HAA&` | Alfa aleatorio en formato ASS. |

### 4.2. Matemáticas, Cinemática e Interpolación

| Función | Comportamiento |
| :--- | :--- |
| `clamp(val, min_v, max_v)` | Restringe $val$ al intervalo cerrado $[min\_v, max\_v]$. |
| `lerp(a, b, t)` | Interpolación lineal: $a + (b - a) \cdot t$ con $t \in [0.0, 1.0]$. |
| `map_range(v, in_min, in_max, out_min, out_max)` | Remapea linealmente un valor de un rango a otro. |
| `ease_in(t)`, `ease_out(t)`, `ease_in_out(t)` | Curvas de aceleración y desaceleración cuadráticas estándar. |
| `cubic_in(t)`, `cubic_out(t)` | Curvas de aceleración y desaceleración cúbicas ($t^3$). |
| `elastic(t)` | Curva oscilatoria con amortiguación de resorte. |
| `bounce(t)` | Curva de rebote con decaimiento progresivo. |
| `back(t)` | Curva con anticipación y sobreimpulso (*overshoot*). |
| `ipol(t, a, b, curve)` | Interpola entre $a$ y $b$ con la curva indicada (`"ease_in"`, `"cubic_out"`, `"bounce"`). |
| `bezier(t, p0, p1, p2, p3)` | Curva Bézier cúbica 1D evaluada en $t$. |
| `polar(angle_deg, dist)` | Convierte coordenadas polares $(\theta, r)$ a vector cartesiano $(x, y)$: $x = r \cos(\theta)$, $y = r \sin(\theta)$. |

### 4.3. Osciladores
Funciones periódicas del tiempo $t$, con frecuencia $freq$, amplitud $amp$ y fase $offset$:
* `sine_wave(t, freq=1.0, amp=1.0, offset=0.0)`: Onda senoidal.
* `square_wave(t, freq=1.0, amp=1.0, offset=0.0)`: Onda cuadrada ($\pm amp$).
* `triangle_wave(t, freq=1.0, amp=1.0, offset=0.0)`: Onda triangular con pendientes lineales.
* `sawtooth_wave(t, freq=1.0, amp=1.0, offset=0.0)`: Onda diente de sierra (rampa lineal periódica).

### 4.4. Tiempos y Sincronización entre Líneas

| Función | Descripción |
| :--- | :--- |
| `time_lead_in(delay, [base])` (o `li(delay)`) | Inicio escalonado de entrada de la unidad, en milisegundos. |
| `time_lead_out(delay, [base])` (o `lo(delay)`) | Fin escalonado de salida de la unidad, en milisegundos. |
| `time_middle_1(delay, [base])` (o `m1(delay)`) | Secuencia radial desde el centro de la línea hacia los extremos. |
| `time_middle_2(delay, [base])` (o `m2(delay)`) | Secuencia radial desde los extremos hacia el centro. |
| `time_loop_1(delay, [mode])` (o `l1(delay)`) | Bucle de tiempo cíclico para animaciones de entrada sostenidas. |
| `time_loop_2(delay, [mode])` (o `l2(delay)`) | Bucle de tiempo cíclico para animaciones de salida sostenidas. |
| `time_to_frame(ms, [fps])` | Convierte milisegundos al número entero de frame correspondiente. |
| `duration(obj)` | Duración en ms del objeto o contexto suministrado. |
| `parse_ass_time("0:01:23.45")` | Convierte una cadena de tiempo ASS a milisegundos. |
| `format_ass_time(ms)` | Convierte milisegundos al formato de tiempo de ASS (`H:MM:SS.cs`). |
| `sync.next`, `sync.prev` | Distancia en milisegundos hasta la siguiente o anterior línea de diálogo. |
| `sync.style_next`, `sync.actor_next` | Distancia en milisegundos hasta la siguiente línea con el mismo estilo o actor. |
| `calculate_sync_gap(dir, mode, max_gap)` | Función general para medir espacios y solapamientos entre diálogos. |

### 4.5. Formas Vectoriales

El script puede emitir directamente trazados vectoriales ASSdraw, para usarlos como siluetas, partículas o recortes:
* `shape_circle()`, `shape_square()`, `shape_rectangle()`
* `shape_triangle()`, `shape_rhombus()`, `shape_rounded_corners()`
* `shape_pentagon()`, `shape_hexagon()`, `shape_octagon()`
* `shape_star()`, `shape_heart()`
* `resolve_shape(name)`: Resuelve cualquier figura registrada en la biblioteca de formas.

### 4.6. Análisis de Audio
* `audio_rms(start_ms, end_ms, [path])`: Amplitud media cuadrática (RMS) del audio en la ventana temporal ($0.0 \dots 1.0$).
* `audio_peak(start_ms, end_ms, [path])`: Amplitud de pico en la ventana ($0.0 \dots 1.0$).
* `audio_band(start_ms, end_ms, min_hz, max_hz, [path])`: Energía acústica en una banda de frecuencias (por ejemplo, graves de 20 Hz a 120 Hz).
* `audio_fft(start_ms, end_ms, num_bands, min_hz, max_hz, [path])`: Devuelve una lista (o tabla Lua) con los valores normalizados de las bandas espectrales tras aplicar la Transformada Rápida de Fourier.

### 4.7. Memoria Persistente y Estado Compartido
* `remember(clave, valor)`: Guarda un valor en la memoria compartida del motor. El dato se conserva entre iteraciones de sílabas, caracteres y líneas completas.
* `recall(clave, default=None)`: Recupera el valor guardado o devuelve `default` si aún no se ha definido.
* `tag_only(condicion, tag_str)`: Devuelve `tag_str` si `condicion` es verdadera y una cadena vacía en caso contrario.

---

## 5. Aleatoriedad Determinista (`R` y el Despachador `by`)

Las funciones pseudoaleatorias estándar sin semilla fija dan un valor distinto en cada evaluación o fotograma, y eso hace que las posiciones tiemblen (*jittering*).

Pyxis usa un **motor pseudoaleatorio determinista con semilla derivada de la topología del nodo y de los índices de iteración**, de modo que una misma unidad siempre recibe el mismo valor.

### 5.1. Funciones Aleatorias Básicas

* `R(min, max)`: Entero aleatorio determinista o flotante escalonado, según el contexto.
* `Rs(min, max)`: Aleatorio **bipolar simétrico** (genera valores en $\pm [min, max]$).
* `Rc(min, max)` / `Rcs(min, max)`: Aleatorio con 2 decimales.
* `Rd(min, max)` / `Rds(min, max)`: Aleatorio con 1 decimal.
* `Rm(min, max)` / `Rms(min, max)`: Aleatorio con 3 decimales.
* `Rr(min, max)`: Aleatorio escalado según la resolución del video.
* `Rstep(min, max, step)`: Aleatorio ajustado a múltiplos de `step` (útil para ángulos: `Rstep(0, 360, 45)`).
* `R2d(min, max)`: Par de coordenadas independientes `"X,Y"`.
* `Rbool(prob=50)`: `True` con la probabilidad porcentual indicada ($0-100\%$).
* `Rcolor(c1, c2)`: Color ASS aleatorio interpolado entre dos tonos dados.
* `Re("opcionA, opcionB, opcionC")`: Elige al azar uno de los elementos de una lista separada por comas.

### 5.2. El Despachador `by`

Para que un valor aleatorio se evalúe **exactamente una vez por sílaba, partícula o sub-bucle**, se usa la sintaxis:

$$\text{by}.\langle \text{iterador} \rangle.\langle \text{modo\_R} \rangle(\text{args})$$

**Ejemplos:**
```python
# Un ángulo aleatorio estable por cada sílaba (no cambia si hay sub-bucles internos)
ang = by.syl.R(-45, 45)

# Una variación de velocidad única por cada pieza de slicer
vel_x = by.s_i.Rms(-150, 150)

# Un desplazamiento vertical por cada clon del nodo MaxLoop (j)
offset_y = by.j.Rs(20, 80)
```

---

## 6. Python frente a Lua

| Característica | Modo Python (`language: "Python"`) | Modo Lua (`language: "Lua"`) |
| :--- | :--- | :--- |
| **Indexación** | Basada en cero ($0 \dots N-1$) para listas nativas. | Basada en uno ($1 \dots N$) para tablas. |
| **Métricas** | `syl.i`, `line.i` son enteros 1-based en ambos. | `syl.i`, `line.i` son enteros 1-based en ambos. |
| **Estructuras de Datos** | Diccionarios `{}` y Listas `[]`. | Tablas `{}` asociativas y numéricas. |
| **Salida Principal** | `result = ...` o última expresión. | `result = ...` o `return ...`. |
| **Salidas Múltiples** | `outputs['out1'] = val` o `out1 = val`. | `outputs.out1 = val` o `out1 = val`. |
| **Condicionales** | `x = a if cond else b` | `x = cond and a or b` |
| **Concatenación** | `+` (cadenas) o f-strings `f"{a}{b}"` | `..` (operador de concatenación) |
| **Librería Matemática** | `math.sin`, `math.pi`, `abs`, etc. | `math.sin`, `math.pi`, `math.abs`, etc. |
| **Nil / None** | `None` | `nil` |

---

## 7. Qué Hacer y Qué Evitar

### ✅ Usos recomendados:
1. **Cinemática y física personalizadas:** Gravedad, trayectorias helicoidales, gravedad inversa, osciladores armónicos acoplados o resortes con amortiguación manual.
2. **Construcción de etiquetas ASS:** Limpiar, modificar o combinar etiquetas con las utilidades nativas (`merge_ass_tags`, `strip_tags`, `pos`, `move`).
3. **Estilo condicional:** Bifurcar según el actor, la capa, el número de sílaba, la posición en pantalla o el tiempo que falta para la próxima línea.
4. **Distribuir datos:** Usar `outputs['out1']`, `outputs['out2']`, etc., para enviar coordenadas calculadas a varios nodos del lienzo a la vez.
5. **Estado persistente:** Crear contadores acumulativos, estelas de partículas o memorias de posiciones previas con `remember()` y `recall()`.

### ❌ Evitar:
1. **I/O síncrono bloqueante dentro de iteraciones:** No abras archivos (`open()`) ni consultes bases de datos en cada evaluación de sílaba o partícula. Si necesitas leer un archivo externo, léelo una sola vez y guárdalo con `recall` o en memoria compartida.
2. **Modificar objetos del sistema en caliente:** No reasignes punteros internos ni mutes diccionarios inmutables del host (`context["_engine"] = None`). El contexto inyectado sirve para leer métricas y emitir etiquetas.
3. **Mezclar tipos en etiquetas numéricas:** No inyectes `None`, `nil` ni cadenas sin validar en etiquetas ASS numéricas (ej. `\pos(None, 20)`). Las funciones de Pyxis (`pos()`, `fscx()`) sanean los valores numéricos y evitan errores de sintaxis.
4. **Bucles infinitos o complejidad descontrolada:** Dentro de un bucle anidado (`Slicer` $\times$ `MaxLoop`), el script se ejecuta $P \times J$ veces por sílaba. Mantén cada iteración en complejidad constante $\mathcal{O}(1)$ y evita bucles `while` sin una cota estricta de salida.
5. **Indentación irregular en Python:** El linter en tiempo real valida el script antes de ejecutarlo, y un error de indentación muestra una advertencia en el panel de diagnósticos del nodo.

---

## 8. Ejemplos Prácticos

### 8.1. Ejemplo A: Aparición Elástica con Anticipación (Python)

Reemplaza una cadena completa de nodos de tiempo, interpolador, oscilador y tags:

```python
# Cálculo del factor paramétrico t según el tiempo de lead-in de la sílaba
t_in = clamp((line.start_time + syl.syl_start - fx.start_time) / 300.0, 0.0, 1.0)

# Curva de resorte elástico aplicada a la escala horizontal y vertical
scale = lerp(0.0, 100.0, elastic(t_in))

# Pequeña rotación Z con anticipación que se amortigua al asentarse
rot = lerp(by.syl.Rs(30, 60), 0.0, back(t_in))

# Desvanecimiento de entrada
alpha_val = lerp(255, 0, t_in)

# Generación y retorno de las etiquetas ASS limpias
result = pos(syl.x, syl.y) + fscxy(scale) + frz(rot) + alpha(ass_alpha(alpha_val))
```

### 8.2. Ejemplo B: Dispersión de Partículas con Gravedad (Lua)

Dispersa las partículas generadas con `Slicer` o `MaxLoop`:

```lua
-- Parámetros físicos evaluados con el despachador determinista 'by'
local ang = by.s_i.R(0, 360)
local speed = by.s_i.R(80, 250)
local gravity = 120.0

-- Tiempo normalizado desde el instante de activación de la sílaba
local t = clamp((fx.start_time - syl.start_time) / syl.duration, 0.0, 1.0)

-- Desplazamiento vectorial cartesiano
local rad = math.rad(ang)
local dx = math.cos(rad) * speed * t
local dy = (math.sin(rad) * speed * t) + (0.5 * gravity * t * t)

-- Rotación acumulada durante la caída
local rz = by.s_i.Rs(90, 360) * t

-- Resultado inyectado directamente al pipeline ASS
result = pos(syl.x + dx, syl.y + dy) .. frz(rz) .. fad(0, 150)
```

### 8.3. Ejemplo C: Pulso Reactivo a los Graves del Audio (Python)

Lee la energía de la pista de audio vinculada en Aegisub:

```python
# Analizar la energía en la banda de graves (bombos y bajos: 30 a 120 Hz)
bass_energy = audio_band(syl.start_time, syl.end_time, min_hz=30, max_hz=120)

# Remapear la energía acústica (0.0..1.0) a un incremento de escala y brillo
scale_boost = map_range(bass_energy, 0.0, 1.0, 100.0, 160.0)
blur_amount = map_range(bass_energy, 0.0, 1.0, 1.0, 6.0)

# Variación armónica adicional usando onda senoidal rápida
wave = sine_wave(syl.i * 0.2, freq=2.0, amp=15.0)

# Emitir transformaciones dinámicas
result = pos(syl.x, syl.y + wave) + fscxy(scale_boost) + blur(blur_amount)
```

---

## 9. Diagnóstico y Depuración

1. **Linter:** Al escribir en el editor Ace del nodo, los errores de sintaxis de Python (`ast.parse`) y de Lua se subrayan y se listan en el panel de diagnósticos con la línea y una sugerencia de corrección.
2. **Autocompletado (`Ctrl + Espacio`):** El editor reconoce las variables de contexto (`syl.*`, `char.*`, `line.*`, `ink.*`), los generadores de tags y los atajos `by.<iterador>.*`, y muestra ayuda contextual en HTML.
3. **Tolerancia a errores:** Si un script lanza una excepción durante la generación, Pyxis la captura y escribe un mensaje `[Err Python Script: ...]` o `[Err Lua Script: ...]` en la consola de depuración, para que Aegisub no se congele ni se cierre.

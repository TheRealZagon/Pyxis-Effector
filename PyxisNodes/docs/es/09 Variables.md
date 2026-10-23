# Variables

La categoría **Variables** lee valores del contexto ASS, define variables locales evaluadas en cada iteración y guarda valores que persisten entre ciclos de ejecución.

### Contenido
* **Ciclo de vida del contexto:** jerarquía de tiempos, tiempos relativos al efecto ($ini$), anidamiento DAG Trace y aislamiento de sub-iteradores.
* **Nodos:** [`Sys Var`](#1-nodo-variablessys-var-variables-del-sistema-y-contexto) (§1), [`Define Vars`](#2-nodo-variablesdefine-vars-definición-de-variables-locales) (§2), [`Get Var`](#3-nodo-variablesget-var-lector-de-variables-del-contexto) (§3), [`Memory`](#4-nodo-variablesmemory-memoria-persistente-clave-valor) (§4).
* **Referencia:** tabla comparativa (§5), tipos de propiedad A/B/C y resolución AST (§6), ámbitos y colisiones de nombres (§7), buenas prácticas (§8).

---

## Arquitectura de Variables y Ciclo de Vida del Contexto

La información de contexto desciende por los niveles de iteración (`line` $\to$ `syl` $\to$ `word` $\to$ `char` $\to$ `sub-bucles`):

```
+─────────────────────────────────────────────────────────────────────────────+
|                         ENTORNO GLOBAL / PROYECTO                          |
|  meta.res_x, meta.res_y, frame_dur, default_audio_source, video_fps         |
+──────────────────────────────────────┬──────────────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
|                          NIVEL DE LÍNEA (line / l)                          |
|  l.text, l.start_time, l.end_time, l.dur, l.style, l.layer, l.margin_*, ... |
+──────────────────────────────────────┬──────────────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
|                   NIVEL DE UNIDAD ACTIVA (syl / word / char)                 |
|  syl.text, syl.x, syl.y, syl.dur, syl.left, syl.center, syl.i, syl.n, ...   |
+──────────────────────────────────────┬──────────────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
|                        CADENA DE BUCLES / SUB-BUCLES                        |
|  fx.i, fx.n, fx.pos_x, fx.pos_y, fx.dur, j, maxj, s_i, a_i, p_i, ratio       |
+──────────────────┬──────────────────────────────────────┬───────────────────+
                   │                                      │
                   ▼                                      ▼
+──────────────────────────────────────+ +────────────────────────────────────+
|     LOCAL STATE (Define Vars)        | |    PERSISTENT STATE (Memory)       |
|  Variables temporales inyectadas     | |  Almacén clave-valor que perdura   |
|  válidas dentro del ciclo actual.    | |  a través de todos los ciclos.     |
+──────────────────────────────────────+ +────────────────────────────────────+
```

### 0.1. Jerarquía de Tiempos

Las marcas de tiempo de `Dialogue` están en la línea de tiempo global del vídeo, pero las marcas de karaoke `\k` y las transformaciones `\t(t1, t2, tags)` son relativas al inicio de la línea generada ($[0, \text{fx.dur}]$).

Pyxis maneja el tiempo en estos niveles:

| Entidad | Propiedades | Base temporal | Variables Relativas al Efecto ($ini = line.start\_time - fx.start\_time$) |
| :--- | :--- | :--- | :--- |
| **`line` / `l`** | `start_time`, `end_time`, `dur`, `mid_time` | **Global del Vídeo ($ms$)** | Posición absoluta del evento en el timeline. |
| **`syl`** | `start_time`, `end_time`, `dur`, `mid_time` | **Relativo a la Línea ($[0, line.dur]$)** | $syl.syl\_start = ini + syl.start\_time$<br>$syl.syl\_end = syl.syl\_start + syl.dur$<br>$syl.syl\_mid = syl.syl\_start + \frac{syl.dur}{2}$ |
| **`char`** | `start_time`, `end_time`, `dur`, `mid_time` | **Relativo a la Sílaba ($[0, syl.dur]$)** | $char.char\_start = syl.syl\_start + char.start\_time$<br>$char.char\_end = char.char\_start + char.dur$<br>$char.syl\_start = syl.syl\_start$<br>$char.syl\_end = syl.syl\_end$ |
| **`word`** | `start_time`, `end_time`, `dur`, `mid_time` | **Relativo a la Línea ($[0, line.dur]$)** | $word.word\_start = ini + word.start\_time$<br>$word.word\_end = word.word\_start + word.dur$ |
| **`fx`** | `start_time`, `end_time`, `dur` | **Global de la Línea Emitida en ASS** | Intervalo $[0, fx.dur]$ sobre el que libass evalúa $\backslash\text{t}(t_1, t_2, \dots)$. |

#### Desfase de anticipación ($ini$)
Si un nodo temporal (`Time/Lead In`, `Time/Retime`) añade un *lead-in* $\Delta t_{\text{leadin}}$ a un evento que empieza en $line.start\_time$, la línea ASS de salida empieza en:

$$fx.start\_time = line.start\_time - \Delta t_{\text{leadin}}$$

$ini$ es el desfase entre ambos:

$$ini = line.start\_time - fx.start\_time = \Delta t_{\text{leadin}}$$

Por tanto, un `\t` que abarque exactamente el tiempo de canto de una sílaba usa:

$$t_1 = syl.syl\_start = ini + syl.start\_time, \quad t_2 = syl.syl\_end = syl.syl\_start + syl.dur$$

### 0.2. Anidamiento de Sub-bucles (DAG Trace)

Cuando varios generadores de piezas o partículas se conectan a `System/Output`, el motor resuelve sus dependencias en tiempo de renderizado recorriendo los cables del grafo en post-orden (**DAG Trace**):

```
                                              ┌───────────────────────────────┐
                                              │     System/Output (Terminal)  │
                                              └───────▲───────────────▲───────┘
                                                      │               │
                                 Canal Return:        │               │ Canal Tags:
                                 Geometría / Piezas   │               │ Modificadores
                                                      │               │
                                         ┌────────────┴───┐       ┌───┴──────────┐
                                         │ Functions/     │       │ Basics/      │
                                         │ Particles      │       │ MultiTag     │
                                         └────────────▲───┘       └──────────────┘
                                                      │
                                         ┌────────────┴───┐
                                         │ Shape/Slicer   │
                                         │ (Bucle Exterior)
                                         └────────────────┘
```

1. **Canal 1 (`Output.Return`, puerto 5, geometría):** Se recorre recursivamente en post-orden desde la raíz *upstream* hasta el puerto `Return`. Si `Slicer` alimenta a `Particles` y este a `Return`, `Slicer` es el bucle exterior ($s_i \in [1, s_n]$) y `Particles` el interior ($p_i \in [1, p_n]$ para cada pieza $s_i$).
2. **Canal 2 (`Output.Tags`, puerto 4, modificadores):** Se recorre en post-orden siguiendo el orden de las entradas (`In1`, `In2`, ...) y se evalúa dentro de cada estado geométrico emitido por `Return`.

#### Iteradores por generador
Cada familia de generadores tiene sus propios nombres de iterador, de modo que los generadores anidados no colisionan:

| Familia de Nodo Generador | Iterador Ordinal | Total de Unidades | Alias de Expresión |
| :--- | :---: | :---: | :--- |
| **`Shape/Slicer`** | `s_i` | `s_n`, `s_max` | `slice_i`, `slice_n`, `slice_max`, `col`, `row` |
| **`Shape/Union & Divide`** | `d_i` | `d_n`, `d_max` | `divide_i`, `divide_n`, `divide_max` |
| **`Shape/Concentric Borders`** | `b_i` | `b_n`, `b_max` | `ring_i`, `ring_n`, `ring_max` |
| **`Shape/Array`** | `a_i` | `a_n`, `a_max` | `array_i`, `array_n`, `array_max`, `col`, `row` |
| **`Shape/Multi`** | `m_i` | `m_n`, `m_max` | `multi_i`, `multi_n`, `multi_max` |
| **`Functions/Particles`** | `p_i` | `p_n`, `p_max` | `tp_i`, `tp_n`, `tp_max`, `text_p_i`, `text_p_n` |
| **`Functions/IMG to pixels`** | `ip_i` | `ip_n`, `ip_max` | `img_p_i`, `img_p_n`, `total_pixels` |
| **`Functions/Clip Gradient`** | `c_i` | `c_n`, `c_max` | `clip_i`, `clip_n`, `clip_max`, `c_col`, `c_row` |
| **`Functions/Animation`** | `an_i` | `an_n`, `an_max` | `anim_i`, `anim_n`, `anim_max`, `an_j` |
| **`Loops/MaxLoop`** | `j` | `maxj`, `maxloop` | `module`, `m`, `ratio` |

#### Poda condicional
Al recorrer el grafo hacia aguas arriba, si el motor encuentra un selector condicional (`Basics/Only`, `Functions/Conditioner`, `Basics/Once`), evalúa la condición con el contexto de iteración actual y sigue solo la rama activa (`True` o `False`). Así los generadores alternativos no se multiplican en serie y las ramas inactivas no ejecutan iteraciones fantasma.

---

## 1. Nodo `Variables/Sys Var` (Variables del Sistema y Contexto)

Lee un valor del contexto activo: coordenadas, dimensiones en píxeles, tiempos en milisegundos, índices de iteración, propiedades de estilo ASS, resolución del proyecto o dimensiones de trazados vectoriales.

![Variables/Sys Var](img/sys_var.jpg)

> [!TIP]
> **Selector de variables (SysVar Grid Picker):**
> Al hacer clic o editar el campo **Variable** se abre un selector con búsqueda en tiempo real y categorías (*Line*, *Syllable*, *Character*, *Word*, *Effect/FX*, *Loops/Globals*, *Temporal Offset*, *Ink Metrics*, *Meta/Project*, *Neighbors & Context*). Dentro de cada categoría las variables están ordenadas alfabéticamente y se eligen con un solo clic, sin escribirlas.

### 1.1. Desplegable de cabecera
El desplegable de la cabecera del nodo fija `var_name`. Permite elegir una variable habitual o escribir cualquier identificador.

### 1.2. Entradas y propiedades
1. **`Variable` (`var_name`):** Nombre de la variable o ruta de propiedad a leer (ej. `"syl.text"`, `"line.start_time"`, `"fx.pos_x"`, `"meta.res_x"`, `"shape.width"`). Defecto: `"syl.text"`.
   * Tipo C (texto plano / identificador). No se analiza con `ast.parse`, así que no genera falsos errores de sintaxis.
   * El nodo no tiene puertos de entrada; el valor sale directamente del contexto de ejecución.

### 1.3. Salidas
1. **`[1.1] Data`:** El valor solicitado, como texto o número. Si la variable no existe en el contexto, emite una cadena vacía `""` o `0.0`.

### 1.4. Variables disponibles

Las tablas siguientes listan las variables de contexto que se pueden usar en `Sys Var`, en `Define Vars`, en scripts de `Script Code` y en expresiones entre paréntesis `\tag(var)`.

#### 1.4.1. Línea (`line.` o `l.`) y estilo original
La línea de diálogo activa y su estilo, definido en la sección `[V4+ Styles]` del script ASS. Las propiedades de estilo reflejan el estilo base (`StyleRef`) o cualquier sobreescritura previa:

| Variable | Tipo | Descripción y Unidad |
| :--- | :---: | :--- |
| `line.text` / `l.text` | `string` | Texto de la línea sin etiquetas de estilo ni marcas de karaoke. |
| `line.raw_text` / `l.raw_text` | `string` | Texto de la línea con las etiquetas `{\...}` y marcas `\k` intactas. |
| `line.start_time` / `l.start_time` | `int` | Tiempo inicial de la línea en milisegundos ($ms$). |
| `line.end_time` / `l.end_time` | `int` | Tiempo final de la línea en milisegundos ($ms$). |
| `line.dur` / `line.duration` / `l.dur` | `int` | Duración de la línea en milisegundos: $t_{\text{end}} - t_{\text{start}}$. |
| `line.mid_time` / `l.mid_time` | `float` | Punto medio de la línea: $t_{\text{start}} + \frac{t_{\text{dur}}}{2}$. |
| `line.i` / `l.i` | `int` | Índice de la línea activa en el lote ($1 \dots N$). |
| `line.n` / `l.n` | `int` | Número de líneas seleccionadas en el lote. |
| `line.x`, `line.y` | `float` | Coordenadas del centro de la línea en pantalla (px). |
| `line.left`, `line.right` | `float` | Límite horizontal izquierdo y derecho del cuadro delimitador (*Bounding Box*) de la línea (px). |
| `line.top`, `line.bottom` | `float` | Límite vertical superior e inferior del cuadro delimitador de la línea (px). |
| `line.middle`, `line.center` | `float` | Centro vertical y horizontal de la línea (px). |
| `line.width`, `line.height` | `float` | Anchura y altura de la línea (px). |
| `line.descent`, `line.extlead` | `float` | Descenso (*descent*) e interlineado externo (*external leading*) de la fuente (px). |
| `line.layer` / `l.layer` | `int` | Capa ASS de la línea (Z-order). |
| `line.style` / `line.style_name` | `string` | Nombre del estilo ASS de la línea (ej. `"Default"`, `"Romaji"`). |
| `line.actor` / `l.actor` | `string` | Campo de actor/personaje de la línea ASS. |
| `line.effect` / `l.effect` | `string` | Campo de efecto especial de la línea ASS. |
| `line.margin_l`, `line.margin_r`, `line.margin_v` | `int` | Márgenes izquierdo, derecho y vertical definidos en la línea o estilo (px). |
| `line.margin_t`, `line.margin_b` | `int` | Márgenes superior e inferior (px). |
| `line.fontname` | `string` | Familia tipográfica del estilo original (ej. `"Arial"`, `"Montserrat"`). |
| `line.fontsize` | `float` | Tamaño de fuente del estilo base en puntos ($pt$). |
| `line.bold` | `bool` | Si el estilo original es negrita (`True` / `False`). |
| `line.italic` | `bool` | Si el estilo original es cursiva (`True` / `False`). |
| `line.underline` | `bool` | Si el estilo original está subrayado (`True` / `False`). |
| `line.strikeout` | `bool` | Si el estilo original está tachado (`True` / `False`). |
| `line.scale_x`, `line.scale_y` | `float` | Escala horizontal y vertical de la fuente del estilo base ($100.0 = 100\%$). |
| `line.spacing` | `float` | Espaciado entre caracteres en píxeles (`\fsp`). |
| `line.outline` | `float` | Grosor del borde del estilo original, en píxeles (`\bord`). |
| `line.shadow` | `float` | Distancia de la sombra del estilo original, en píxeles (`\shad`). |
| `line.align` | `int` | Alineación Numpad del estilo base ($1 \dots 9$). |
| `line.color1` .. `line.color4` | `string` | Colores del estilo original: primario (`\1c`), karaoke/secundario (`\2c`), borde (`\3c`) y sombra (`\4c`) en formato ASS `&HBBGGRR&`. |
| `line.alpha1` .. `line.alpha4` | `string` | Alfa del estilo original para los cuatro colores en formato ASS `&HAA&` ($0 \dots 255$). |
| `line.frz`, `line.frx`, `line.fry` | `float` | Ángulos de rotación 3D de la línea o estilo, en grados. |
| `line.fax`, `line.fay` | `float` | Factores de cizallamiento (*shear*) horizontal y vertical. |
| `line.pos_x`, `line.pos_y` | `float` | Posición de la línea, absoluta o sobreescrita (`\pos`). |
| `line.org_x`, `line.org_y` | `float` | Origen de rotación de la línea (`\org`). |

#### 1.4.2. Sílaba (`syl.`), carácter (`char.`) y palabra (`word.`)
Las sílabas, caracteres y palabras que produce `Main Loop`. Cada unidad hereda las propiedades de estilo y color del estilo base de su línea o de las sobreescrituras activas:

| Variable | Tipo | Descripción y Unidad |
| :--- | :---: | :--- |
| `syl.text` / `word.text` / `char.text` | `string` | Texto del elemento sin etiquetas de estilo. |
| `syl.text_stripped` / `char.text_stripped` | `string` | Texto de la unidad sin ninguna etiqueta incrustada. |
| `syl.text_spacestripped` | `string` | Texto de la sílaba sin espacios iniciales ni finales. |
| `syl.dur` / `syl.duration` | `int` | Duración de la sílaba en milisegundos ($ms$), según la marca `\k`. |
| `syl.start_time`, `syl.end_time` | `int` | Tiempos de inicio y fin relativos a la **línea de diálogo** ($ms$). |
| `syl.mid_time` | `float` | Punto medio de la sílaba, relativo a la línea: $t_{\text{start}} + \frac{t_{\text{dur}}}{2}$. |
| `syl.syl_start`, `syl.syl_end` | `int` | Tiempos de inicio y fin de la sílaba relativos a la **línea de efecto `fx`** ($\text{ini} + \text{syl.start\_time}$). |
| `syl.syl_mid` | `float` | Punto medio de la sílaba relativo a la línea de efecto `fx`. |
| `syl.i` / `syl.n` | `int` | Índice de la sílaba en la línea ($1 \dots N$) y total de sílabas. |
| `syl.x`, `syl.y` | `float` | Coordenadas del centro de la sílaba en pantalla (px). |
| `syl.left`, `syl.right` | `float` | Coordenada $X$ izquierda y derecha del cuadro delimitador de la sílaba (px). |
| `syl.top`, `syl.bottom` | `float` | Coordenada $Y$ superior e inferior del cuadro delimitador de la sílaba (px). |
| `syl.center`, `syl.middle` | `float` | Centro horizontal $X$ y vertical $Y$ de la sílaba (px). |
| `syl.width`, `syl.height` | `float` | Anchura y altura de la sílaba (px). |
| `syl.descent`, `syl.descend` | `float` | Descenso de la fuente en la sílaba (px). |
| `syl.extlead` | `float` | Interlineado externo de la fuente (px). |
| `syl.prespace`, `syl.postspace` | `string` | Espacios en blanco antes y después de la sílaba. |
| `syl.prespacewidth`, `syl.postspacewidth` | `float` | Anchura en píxeles de los espacios antes y después de la sílaba. |
| `syl.fontname`, `syl.fontsize` | `string` / `float` | Familia tipográfica heredada del estilo y tamaño en puntos ($pt$). |
| `syl.bold`, `syl.italic` | `bool` | Banderas booleanas de negrita y cursiva heredadas del estilo. |
| `syl.underline`, `syl.strikeout` | `bool` | Banderas booleanas de subrayado y tachado heredadas del estilo. |
| `syl.scale_x`, `syl.scale_y` | `float` | Factores de escala tipográfica heredados ($100.0 = 100\%$). |
| `syl.spacing`, `syl.outline`, `syl.shadow` | `float` | Espaciado (`\fsp`), grosor de borde (`\bord`) y sombra (`\shad`) heredados (px). |
| `syl.color1` .. `syl.color4` | `string` | Colores primario, karaoke, borde y sombra asignados a la sílaba (`&HBBGGRR&`). |
| `syl.alpha1` .. `syl.alpha4` | `string` | Canales alfa primario, karaoke, borde y sombra asignados a la sílaba (`&HAA&`). |
| `syl.align` | `int` | Alineación Numpad activa ($1 \dots 9$). |
| `syl.pos_x`, `syl.pos_y` | `float` | Posición de anclaje de la sílaba (`\pos`). |
| `syl.org_x`, `syl.org_y` | `float` | Origen / centro de rotación de la sílaba (`\org`). |
| `syl.actor`, `syl.style`, `syl.layer`, `syl.effect` | `str`/`int` | Metadatos heredados de la línea contenedora. |
| `char.dur` / `char.duration` | `int` | Duración del carácter ($ms$). |
| `char.start_time`, `char.end_time` | `int` | Tiempos de inicio y fin relativos a su **sílaba contenedora** ($ms$). |
| `char.mid_time` | `float` | Punto medio del carácter dentro de su sílaba: $t_{\text{start}} + \frac{t_{\text{dur}}}{2}$. |
| `char.char_start`, `char.char_end` | `int` | Tiempos de inicio y fin del carácter relativos a la **línea de efecto `fx`** ($\text{syl.syl\_start} + \text{char.start\_time}$). |
| `char.syl_start`, `char.syl_end` | `int` | Tiempos de inicio y fin de la sílaba contenedora relativos a la **línea de efecto `fx`**. |
| `char.i` / `char.n` | `int` | Índice del carácter en la línea ($1 \dots N$) y total de caracteres de la línea. |
| `char.syl_i` | `int` | Índice del carácter dentro de su sílaba ($1 \dots N_{\text{syl}}$). |
| `char.word_i` | `int` | Índice del carácter dentro de su palabra. |
| `char.x`, `char.y` | `float` | Coordenadas del centro del carácter en pantalla (px). |
| `char.center`, `char.middle` | `float` | Centro del carácter (px). |
| `char.left`, `char.right`, `char.top`, `char.bottom` | `float` | Cuadro delimitador del carácter (px). |
| `char.width`, `char.height` | `float` | Anchura y altura del carácter (px). |
| `char.fontname`, `char.fontsize`, `char.color1`..`4` | `var` | Propiedades de fuente y color heredadas. |
| `word.dur` / `word.duration` | `int` | Duración total de la palabra ($ms$). |
| `word.start_time`, `word.end_time` | `int` | Tiempos de inicio y fin relativos a la **línea de diálogo** ($ms$). |
| `word.word_start`, `word.word_end` | `int` | Tiempos de inicio y fin relativos a la **línea de efecto `fx`** ($\text{ini} + \text{word.start\_time}$). |
| `word.i` / `word.n` | `int` | Índice de la palabra en la línea ($1 \dots N$) y total de palabras. |
| `word.x`, `word.y`, `word.center`, `word.middle` | `float` | Centro de la palabra (px). |
| `word.left`, `word.right`, `word.top`, `word.bottom` | `float` | Cuadro delimitador de la palabra (px). |
| `word.width`, `word.height` | `float` | Anchura y altura de la palabra (px). |

#### 1.4.3. Unidades vecinas y banderas de posición (`prev.`, `next.`, `is_first`, `is_last`, `has_prev`, `has_next`)
Permiten leer los elementos vecinos en la cadena de animación sin guardar nada en `Memory`. Los objetos `prev` y `next` exponen las propiedades métricas, temporales y de estilo del elemento adyacente:

| Variable | Tipo | Descripción |
| :--- | :---: | :--- |
| `prev.text`, `prev.text_stripped` | `string` | Texto del elemento previo en la secuencia. |
| `prev.x`, `prev.y`, `prev.center`, `prev.middle` | `float` | Centro del elemento anterior (px). |
| `prev.left`, `prev.right`, `prev.top`, `prev.bottom` | `float` | Cuadro delimitador del elemento anterior (px). |
| `prev.width`, `prev.height` | `float` | Anchura y altura del elemento anterior (px). |
| `prev.start_time`, `prev.end_time`, `prev.dur` | `int` | Tiempos de inicio, fin y duración del elemento anterior ($ms$). |
| `prev.i`, `prev.n` | `int` | Índice y total del elemento previo. |
| `prev.fontname`, `prev.fontsize`, `prev.color1`..`4` | `var` | Propiedades de fuente y estilo del elemento previo. |
| `next.*` | `var` | Las mismas propiedades del **siguiente elemento**. |
| `is_first` | `bool` | `True` si el elemento activo es el primero de la secuencia (`i == 1` o sin elemento previo). Accesible también como `syl.is_first`, `char.is_first`, `word.is_first`. |
| `is_last` | `bool` | `True` si el elemento activo es el último de la secuencia (`i == n` o sin elemento siguiente). Accesible también como `syl.is_last`, `char.is_last`, `word.is_last`. |
| `has_prev` | `bool` | `True` si existe una unidad precedente válida en la línea. |
| `has_next` | `bool` | `True` si existe una unidad sucesora válida en la línea. |

#### 1.4.4. Variables por defecto y globales
Están disponibles sin prefijo en el contexto de evaluación de cada nodo (`Define Vars`, `MultiTag`, `Conditioner`, etc.):

| Variable | Tipo | Descripción y Fórmula |
| :--- | :---: | :--- |
| `frame_dur` / `fd` | `float` | Duración de un fotograma de vídeo en milisegundos ($\approx 41.67\text{ ms}$ a 23.976/24 FPS o $40.0\text{ ms}$ a 25 FPS). |
| `fps` | `float` | Tasa de fotogramas del vídeo activo en Aegisub (ej. `23.976`, `24.0`, `29.97`, `60.0`). |
| `ini` | `float` | Desfase entre la línea de diálogo y la línea de efecto: $\text{ini} = \text{line.start\_time} - \text{fx.start\_time}$. |
| `st`, `et` | `int` | Alias de los `start_time` y `end_time` activos ($ms$). |
| `dur` / `duration` | `int` | Duración de la unidad o fotograma activo en milisegundos ($ms$). |
| `time_start`, `time_end`, `time_dur` | `int` | Alias de los tiempos del fotograma o sub-elemento. |
| `line_start_time`, `line_end_time`, `line_dur` | `int` | Tiempos de inicio, fin y duración de la línea contenedora ($ms$). |
| `syl_start_time`, `syl_end_time` | `int` | Tiempos de inicio y fin de la sílaba contenedora ($ms$). |
| `i`, `n` | `int` | Iterador ($1 \dots N$) y número total de unidades en el bucle principal. |
| `rx`, `ry` | `float` | Desplazamientos espaciales acumulados o relativos en los ejes $X$ e $Y$ (px). |
| `ratio` | `float` | Proporción de progreso temporal o modular activa. |
| `module` / `m` | `float` | Ratio normalizado de progreso del sub-bucle: $\text{module} = \frac{j - 1}{\text{maxj} - 1} \in [0.0, 1.0]$. |
| `pos_x`, `pos_y` | `float` | Posición calculada para el elemento activo (px). |
| `center`, `middle` | `float` | Centro horizontal y vertical del elemento activo (px). |
| `left`, `right`, `top`, `bottom` | `float` | Límites del cuadro delimitador del elemento activo (px). |
| `width`, `height` | `float` | Anchura y altura del elemento activo (px). |
| `x`, `y` | `float` | Coordenadas del elemento activo (px). |
| `result` | `string` | Variable de retorno de `System/Script Code`; el texto o tags asignados se emiten por el pin `Result`. |

#### 1.4.5. Sub-iteradores (piezas, partículas, sub-bucles)
Se definen cuando se conecta un generador iterativo al puerto `Return` de `System/Output`:

| Variable | Tipo | Generador y Descripción |
| :--- | :---: | :--- |
| `j`, `maxj`, `maxloop` | `int` | Contador ordinal ($1 \dots N$) y total de iteraciones configuradas en `Loops/MaxLoop`. |
| `s_i`, `s_n`, `s_max` | `int` | Índice de la pieza activa ($1 \dots N$) y total de piezas generadas por `Shape/Slicer`. |
| `slice_i`, `slice_n`, `slice_max` | `int` | Alias de `s_i` y `s_n` para usar en expresiones. |
| `col`, `row` | `int` | Coordenadas espaciales de columna y fila en segmentaciones matriciales (`Slicer`, `Array`). |
| `a_i`, `a_n` | `int` | Índice ordinal de la partícula activa y total de elementos en matrices de `Shape/Array`. |
| `p_i`, `p_n` | `int` | Índice ordinal y recuento total de partículas en enjambres de `Functions/Particles`. |
| `c_i`, `c_n`, `c_max` | `int` | Índice ordinal y recuento total de cortes en gradientes de `Functions/Clip Gradient`. |
| `clip_i`, `clip_n`, `clip_max` | `int` | Alias de `c_i` y `c_n` en `Functions/Clip Gradient`. |
| `d_i`, `d_n` | `int` | Índice ordinal y recuento de fragmentos en particiones de `Shape/Union & Divide`. |

#### 1.4.6. Atajos (`val_*`)
Acceso directo a las métricas del elemento en curso en expresiones y en `Sys Var`:

| Variable | Tipo | Métrica Equivalente |
| :--- | :---: | :--- |
| `val_x`, `val_y` | `float` | Coordenadas cartesianas de la unidad activa (`active_unit.x`, `active_unit.y`). |
| `val_left`, `val_right` | `float` | Límite horizontal izquierdo y derecho (`active_unit.left`, `active_unit.right`). |
| `val_top`, `val_bottom` | `float` | Límite vertical superior e inferior (`active_unit.top`, `active_unit.bottom`). |
| `val_center`, `val_middle` | `float` | Centro horizontal y vertical (`active_unit.center`, `active_unit.middle`). |
| `val_width`, `val_height` | `float` | Dimensiones (`active_unit.width`, `active_unit.height`). |
| `val_start` / `val_st` | `float` | Instante inicial en milisegundos (`active_unit.start_time`). |
| `val_end` / `val_et` | `float` | Instante final en milisegundos (`active_unit.end_time`). |
| `val_dur` | `float` | Duración neta en milisegundos (`active_unit.duration`). |
| `val_mid` | `float` | Instante medio de la unidad activa: $t_{\text{start}} + \frac{t_{\text{dur}}}{2}$. |
| `val_i`, `val_n` | `int` | Índice ordinal y total de unidades del elemento activo. |

#### 1.4.7. Sincronización entre líneas (`sync.*`)
`sync` da el hueco en milisegundos con las líneas de diálogo vecinas, para iniciar una animación antes de que empiece la línea o hacer transiciones entre líneas sin colisiones:

| Variable | Tipo | Criterio de Búsqueda y Descripción |
| :--- | :---: | :--- |
| `sync.next` / `sync.prev` | `float` | Hueco temporal en milisegundos con la siguiente o anterior línea según el orden cronológico estándar (acotado a `max_gap`, 2000 ms por defecto). |
| `sync.order_next`, `sync.order_prev` | `float` | Hueco con la línea inmediatamente contigua en el orden físico de las líneas del archivo ASS. |
| `sync.style_next`, `sync.style_prev` | `float` | Hueco con la siguiente o anterior línea que posea **el mismo estilo tipográfico**. |
| `sync.actor_next`, `sync.actor_prev` | `float` | Hueco con la siguiente o anterior línea que comparta **el mismo actor/personaje**. |
| `sync.effect_next`, `sync.effect_prev` | `float` | Hueco con la siguiente o anterior línea que posea **el mismo campo de efecto**. |
| `sync.layer_next`, `sync.layer_prev` | `float` | Hueco con la siguiente o anterior línea situada en **la misma capa ASS**. |

> [!NOTE]
> **Signo de los valores de `sync`:**
> * Un valor **positivo ($> 0$)** es una pausa entre ambas líneas (ej. $+850\text{ ms}$).
> * Un valor **negativo ($< 0$)** indica que las dos líneas se solapan en el tiempo.

#### 1.4.8. Temporizadores y modificadores (`time.*`)
Retardos y fases por sílaba para animaciones secuenciales, utilizables en expresiones o mediante `Sys Var`:

| Variable | Tipo | Descripción |
| :--- | :---: | :--- |
| `time.lead_in` | `int` | Retardo previo acumulado por sílaba para animaciones de entrada anticipada (*lead-in*). |
| `time.lead_out` | `int` | Retardo posterior acumulado por sílaba para animaciones de salida (*lead-out*). |
| `time.middle_1` | `int` | Retardo temporal simétrico calculado desde el centro de la línea hacia los extremos. |
| `time.middle_2` | `int` | Retardo temporal simétrico calculado desde los extremos de la línea hacia el centro. |
| `time.loop_1` | `int` | Temporización para bucles cíclicos continuos en la fase de entrada. |
| `time.loop_2` | `int` | Temporización para bucles cíclicos continuos en la fase de salida. |

#### 1.4.9. Presets de formas vectoriales (`shape.*`)
El espacio de nombres `shape` contiene los trazados vectoriales estándar de Pyxis en formato ASSdraw (`m ... l ... b ...`), utilizables en clips, transformaciones o expresiones de código:

| Preset | Identificador | Geometría Emitida |
| :--- | :--- | :--- |
| **Círculo** | `shape.circle` | Círculo Bézier normalizado centrado en $(0, 0)$. |
| **Cuadrado** | `shape.square` | Cuadrado equilátero centrado en $(0, 0)$. |
| **Rectángulo** | `shape.rect` / `shape.rectangle` | Rectángulo paramétrico centrado en $(0, 0)$. |
| **Triángulo** | `shape.triangle` | Triángulo equilátero con vértice superior en $(0, 0)$. |
| **Rombo** | `shape.diamond` / `shape.rhombus` | Rombo centrado en $(0, 0)$. |
| **Esquinas Redondeadas** | `shape.rounded_corners` | Rectángulo con las cuatro esquinas redondeadas con curvas Bézier. |
| **Polígonos Regulares** | `shape.pentagon`, `shape.hexagon`, `shape.octagon` | Polígonos regulares de 5, 6 y 8 lados. |
| **Estrella** | `shape.star` | Estrella simétrica de 5 puntas. |
| **Corazón** | `shape.heart` | Trazado vectorial de corazón bicúbico centrado. |
| **Sakura** | `shape.sakura` | Pétalo estilizado de flor de cerezo japonés. |
| **Símbolos y Clima** | `shape.cross`, `shape.cloud`, `shape.sun`, `shape.moon`, `shape.flower` | Iconos habituales para efectos de partículas. |

#### 1.4.10. Metadatos del Proyecto (`meta.`) y Formas del Contexto
| Variable | Tipo | Descripción |
| :--- | :---: | :--- |
| `meta.res_x`, `meta.res_y` | `int` | Resolución de renderizado del script ASS (`PlayResX`, `PlayResY`, ej. `1280`, `720` o `1920`, `1080`). |
| `shape.width`, `shape.height` | `float` | Anchura y altura en píxeles del trazado vectorial del contexto. |
| `shape.left`, `shape.right` | `float` | Límite horizontal mínimo y máximo del trazado vectorial. |
| `shape.top`, `shape.bottom` | `float` | Límite vertical superior e inferior del trazado vectorial. |
| `shape.center_x`, `shape.center_y` | `float` | Centro del cuadro delimitador del trazado: $(\frac{\text{left} + \text{right}}{2}, \frac{\text{top} + \text{bottom}}{2})$. |

#### 1.4.11. Métricas de tinta (`ink.`, `l.ink.`, `syl.ink.`, `char.ink.`, `word.ink.`)
Las métricas tipográficas estándar usan el cuadro delimitador tipográfico, que incluye los espacios laterales y los márgenes de ascenso/descenso de la fuente. Las **Ink Metrics** miden los contornos vectoriales reales de los glifos renderizados (*visual ink bounds*):

| Variable | Tipo | Descripción |
| :--- | :---: | :--- |
| `ink.width`, `ink.height` | `float` | Anchura y altura del contorno del glifo renderizado del elemento activo (px). |
| `ink.left`, `ink.right` | `float` | Bordes izquierdo y derecho de la tinta renderizada en pantalla (px). |
| `ink.top`, `ink.bottom` | `float` | Bordes superior e inferior de la tinta renderizada en pantalla (px). |
| `ink.center`, `ink.middle` / `ink.x`, `ink.y` | `float` | Centro horizontal y vertical de la tinta renderizada (px). |
| `ink.l.*` / `l.ink.*` | `float` | Métricas de tinta de la línea activa. |
| `ink.syl.*` / `syl.ink.*` | `float` | Métricas de tinta de la sílaba activa. |
| `ink.char.*` / `char.ink.*` | `float` | Métricas de tinta del carácter activo. |
| `ink.word.*` / `word.ink.*` | `float` | Métricas de tinta de la palabra activa. |

### 1.5. Orden de búsqueda

`Sys Var` y el evaluador de expresiones resuelven un identificador $V$ comprobando estos casos por orden:

```
                  ┌───────────────────────────────┐
                  │   ¿Comienza por 'sync.'?      │ ──► [Sí] ──► Consulta de desfase inter-línea
                  └──────────────┬────────────────┘
                                 │ [No]
                  ┌──────────────▼────────────────┐
                  │    ¿Comienza por 'ink.'?      │ ──► [Sí] ──► Inspección de contornos vectoriales reales
                  └──────────────┬────────────────┘
                                 │ [No]
                  ┌──────────────▼────────────────┐
                  │ ¿Es 'is_first' / 'is_last' /  │ ──► [Sí] ──► Banderas de posición topológica relativa
                  │    'has_prev' / 'has_next'?   │
                  └──────────────┬────────────────┘
                                 │ [No]
                  ┌──────────────▼────────────────┐
                  │ ¿Prefijo 'prev.' o 'next.'?   │ ──► [Sí] ──► Métricas y estilo de unidad contigua
                  └──────────────┬────────────────┘
                                 │ [No]
                  ┌──────────────▼────────────────┐
                  │   ¿Comienza por 'shape.'?     │ ──► [Sí] ──► Presets vectoriales normalizados
                  └──────────────┬────────────────┘
                                 │ [No]
                  ┌──────────────▼────────────────┐
                  │ ¿Es 'frame_dur' o 'ratio'?    │ ──► [Sí] ──► Métrica temporal global o modular activa
                  └──────────────┬────────────────┘
                                 │ [No]
                  ┌──────────────▼────────────────┐
                  │    ¿Comienza por 'val_'?      │ ──► [Sí] ──► Mapeo escalar directo de la unidad activa
                  └──────────────┬────────────────┘
                                 │ [No]
                  ┌──────────────▼────────────────┐
                  │  ¿Prefijo 'fx.' o 'time.'?    │ ──► [Sí] ──► Desfases cinemáticos y temporizadores
                  └──────────────┬────────────────┘
                                 │ [No]
                  ┌──────────────▼────────────────┐
                  │ ¿Prefijo 'line.' / 'syl.' /   │ ──► [Sí] ──► Introspección jerárquica de elementos
                  │        'char.' / 'word.'?     │              y propiedades tipográficas del estilo base
                  └──────────────┬────────────────┘
                                 │ [No]
                  ┌──────────────▼────────────────┐
                  │ ¿Existe en context o meta?    │ ──► [Sí] ──► Identificador de usuario o meta de resolución
                  └──────────────┬────────────────┘
                                 │ [No]
                                 ▼
                         Retorna cadena vacía ("")
```

### 1.6. Ejemplo

Se leen las coordenadas y la duración de la sílaba para posicionarla y hacer pulsar su escala mientras se canta:

```
[Sys Var (var_name: syl.x)]   ──► [In1] ──┐
[Sys Var (var_name: syl.y)]   ──► [In2] ──┼──► [Dynamic Format] ──► Output.Tags
[Sys Var (var_name: syl.dur)] ──► [In3] ──┘
```

* **Plantilla en `Dynamic Format`:**
  ```text
  {\an5\pos(%s, %s)\t(0, %s, \fscx125\fscy125\1c&H00FFFF&)}
  ```
* **Línea ASS resultante:**
  ```ass
  Dialogue: 0,0:01:12.40,0:01:15.80,Romaji,,0,0,0,,{\an5\pos(412.5, 680.0)\t(0, 320, \fscx125\fscy125\1c&H00FFFF&)}Ka
  ```

---

## 2. Nodo `Variables/Define Vars` (Definición de Variables Locales)

Define variables locales propias, evaluadas en cada iteración del grafo. Sirve para cálculos intermedios reutilizables, de modo que las expresiones complejas no necesiten más cables en el lienzo.

![Variables/Define Vars](img/define_vars.jpg)

### 2.1. Edición
`Define Vars` funciona tanto como **nodo de flujo de datos (*pass-through*)** como **eslabón en la cadena de bucles (*loop chain node*)**. Al hacer clic en el área de texto se abre un editor multilínea con resaltado de sintaxis; se escribe una asignación por línea.

### 2.2. Entradas y propiedades
1. **`In` (`in_val`):** Entrada de paso (*pass-through*). Acepta cualquier tipo de dato (cadenas de tags ASS, geometría vectorial, números o texto). Si no está conectada, emite el contenido declarado o una cadena vacía.
2. **`Vars` (`variables`):** Bloque multilínea de declaraciones con el formato `clave = expresión`.
   * Tipo A (fórmula / expresión evaluada). El evaluador de expresiones lo procesa línea a línea, en orden.
   * **Sintaxis de declaración:**
     ```python
     radio = 50 + (syl.i * 10)
     angulo = (j / maxj) * 360
     pos_x = syl.x + math.cos(math.radians(angulo)) * radio
     pos_y = syl.y + math.sin(math.radians(angulo)) * radio
     color_actual = "&H00FFFF&"
     ```

### 2.3. Salidas
1. **`[1.1] Out`:** Pasa tal cual el dato recibido en `In` (*pass-through*), después de añadir las variables definidas al contexto de ejecución.

#### Efecto en el contexto
Cada variable asignada en `Vars` queda registrada en el contexto con su propio nombre (`radio`, `angulo`, `pos_x`, etc.) y está disponible para:
* Nodos `Variables/Get Var`.
* Nodos `Basics/Dynamic Format` o `Basics/Math`.
* Expresiones entre paréntesis `\tag(variable)` en cadenas de texto y plantillas de tags ASS.

> [!NOTE]
> **Re-evaluación con iteradores de retorno (*Return Iterators*):**
> Cuando un nodo conectado al puerto `Return` de `System/Output` (como `Shape/Slicer`, `Shape/Array`, `Functions/Particles`, `Functions/IMG to pixels`) genera sub-iteraciones (`s_i`, `a_i`, `p_i`, `d_i`, etc.), Pyxis re-evalúa todas las declaraciones activas de `Define Vars` para cada pieza o partícula antes de evaluar las etiquetas conectadas al puerto `Tags`. Así, llamadas como `by.s_i.R(-30, 30)` o expresiones que dependen de `s_i` se resuelven con el valor de la pieza activa y no con el valor estático del bucle exterior. Además, las definiciones están aisladas por cola de salida (*Queue Isolation*), por lo que varios nodos `Output` no interfieren entre sí.

### 2.4. Cómo llegan las variables a otros nodos

```
                    +---------------------------+
                    | Loops/Main Loop (syl)     |
                    +-------------┬-------------+
                                  │
                                  ▼
                    +---------------------------+
                    | Variables/Define Vars     |
                    |   offset_x = syl.i * 12   |
                    |   rot = by.s_i.R(-20, 20) |
                    +-------------┬-------------+
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
      +---------------------------+ +---------------------------+
      | Variables/Get Var         | | Basics/Dynamic Format     |
      |   var_name: rot           | |   \frz(rot)\fscx(110)     |
      +---------------------------+ +---------------------------+
```

### 2.5. Ejemplo

Se coloca cada pieza de `Shape/Slicer` en una órbita circular alrededor de la sílaba y se rota por pieza:

* **Declaraciones en `Define Vars` (`variables`):**
  ```python
  radio = 18 + (syl.i * 4)
  angulo = (s_i / s_n) * 360
  pos_x = syl.x + math.cos(math.radians(angulo)) * radio
  pos_y = syl.y + math.sin(math.radians(angulo)) * radio
  rot = (s_i / s_n) * 180
  ```
* **Tags emitidos por `Basics/Dynamic Format` hacia `Output.Tags`:**
  ```text
  \pos(pos_x, pos_y)\frz(rot)\t(0, syl.dur, \alpha&HFF&)
  ```
* **Línea ASS resultante:**
  ```ass
  Dialogue: 0,0:01:12.40,0:01:15.80,Romaji,,0,0,0,,{\pos(425.2, 672.8)\frz(22.5)\t(0, 320, \alpha&HFF&)}Ka
  ```

---

## 3. Nodo `Variables/Get Var` (Lector de Variables del Contexto)

Emite el valor actual de cualquier variable del contexto, buscada por su nombre. Permite pasar valores por un grafo grande sin cables, y leer contadores de bucle o variables inyectadas dinámicamente.

![Variables/Get Var](img/get_var.jpg)

### 3.1. Coste de la consulta
No necesita puertos de entrada y se resuelve en $\mathcal{O}(1)$ con un acceso directo a la tabla hash del contexto.

### 3.2. Entradas y propiedades
1. **`Name` (`var_name`):** Variable a leer (ej. `"j"`, `"maxj"`, `"module"`, `"custom_val"`, `"offset_x"`). Defecto: `"j"`.
   * Tipo C (texto plano / identificador). No se analiza con `ast.parse`.

### 3.3. Salidas
1. **`[1.1] Data`:** Valor tomado del contexto. Si la variable no está definida en el contexto activo, emite una cadena vacía `""`.

### 3.4. Usos habituales
* **Sub-iteradores:** Leer los contadores secundarios de bucle (`j`, `maxj`, `module`) de `Loops/MaxLoop` para alimentar nodos de interpolación o transformaciones afines.
* **Variables inyectadas:** Leer resultados calculados por `Variables/Define Vars` o por scripts de `System/Script Code`.
* **Enrutado sin cables (*Wireless Routing*):** Evita cables largos que se cruzan en grafos grandes cuando un mismo valor alimenta varias ramas distantes.

### 3.5. Ejemplo

Se lee el iterador `j` de `Loops/MaxLoop` para variar la opacidad y la escala de capas duplicadas:

* **Conexión en el Grafo:**
  ```
  [Loops/MaxLoop (iterations: 4)]
  [Variables/Get Var (var_name: "j")] ──► [In1] ──► [Dynamic Format] ──► Output.Tags
  ```
* **Plantilla en `Dynamic Format`:**
  ```text
  {\pos(syl.x, syl.y)\fscx(%s)\fscy(%s)\alpha(%s)}
  ```
* **Línea ASS resultante (iteración $j = 3$):**
  ```ass
  Dialogue: 0,0:01:12.40,0:01:15.80,Romaji,,0,0,0,,{\pos(412.5, 680.0)\fscx145\fscy145\alpha&H60&}Ka
  ```

---

## 4. Nodo `Variables/Memory` (Memoria Persistente Clave-Valor)

Almacenamiento persistente de variables (*State Retention*) durante toda la sesión de evaluación del grafo. Las variables de contexto ordinarias se reinician en cada sílaba, línea o fotograma, pero `Memory` conserva sus valores entre ciclos. Sirve para movimiento acumulativo, integración numérica de trayectorias, registro de valores extremos ($\min / \max$) y banderas condicionales (*latches*).

![Variables/Memory](img/memory.jpg)

### 4.1. Modos
1. **`remember` (`save` / `SAVE`):** Modo de escritura. Guarda el dato recibido bajo la clave indicada y lo pasa a la salida, de modo que se puede encadenar.
2. **`retrieve` (`load` / `LOAD`):** Modo de lectura. Lee el valor guardado bajo la clave indicada. Si la clave aún no se ha establecido en la sesión, emite el valor de reserva configurado en `Value / Default`.

### 4.2. Entradas y propiedades
1. **`Key` (`key`):** Nombre con el que se guarda el dato (ej. `"prev_x"`, `"accum_rot"`, `"max_width"`).
   * Tipo C (texto plano / identificador). No se analiza con `ast.parse`.
   * *Precedencia:* Cable conectado $\to$ Campo inline de texto $\to$ Defecto `"ref"`.
2. **`Value` (`value` / `default`):**
   * En modo `remember`: Dato a escribir en la memoria.
   * En modo `retrieve`: Valor de reserva (*fallback / default*) emitido si la clave aún no existe.
   * Tipo A / Tipo C (números escalares, coordenadas, cadenas o vectores).
   * *Precedencia:* Cable conectado $\to$ Campo inline de texto $\to$ Cadena vacía `""`.

### 4.3. Salidas
1. **`[1.1] Data`:**
   * En modo `remember`: Emite el valor recién guardado (*pass-through* de escritura).
   * En modo `retrieve`: Emite el valor leído de la memoria, o `default` si la clave no se encontró.

### 4.4. Persistencia y acumulación

El motor mantiene un almacén persistente $\mathcal{M} = \{\text{key} \mapsto \text{value}\}$ durante toda la sesión de renderizado.

#### 4.4.1. Acumulador de posición
Para que cada sílaba $i$ empiece donde terminó la sílaba anterior $i-1$:

$$\text{pos}_x(i) = \text{retrieve}(\text{"last\_x"}, \text{default} = X_0) + \Delta x_i$$
$$\text{remember}(\text{"last\_x"}, \text{pos}_x(i))$$

```
                               Ciclo Sílaba i-1                        Ciclo Sílaba i
                         ┌───────────────────────────┐           ┌───────────────────────────┐
                         │ Memory (remember)         │           │ Memory (retrieve)         │
                         │   key: "pos_x"            │           │   key: "pos_x"            │
                         │   val: 320.5 px           │           │   val => 320.5 px         │
                         └─────────────┬─────────────┘           └─────────────┬─────────────┘
                                       │                                       │
                                       ▼                                       ▼
                         ┌───────────────────────────────────────────────────────────┐
                         │             Almacén Global Persistente (_memory)             │
                         │                   {"pos_x": 320.5}                        │
                         └───────────────────────────────────────────────────────────┘
```

#### 4.4.2. Integrador de velocidad y gravedad
Para simulaciones de partículas y física discreta con sub-bucles `MaxLoop`:

$$v_y(j) = \text{retrieve}(\text{"vel\_y"}, 0.0) + g \cdot \Delta t$$
$$y(j) = \text{retrieve}(\text{"pos\_y"}, Y_0) + v_y(j) \cdot \Delta t$$
$$\text{remember}(\text{"vel\_y"}, v_y(j)) \quad \land \quad \text{remember}(\text{"pos\_y"}, y(j))$$

Aquí $g$ es la aceleración gravitatoria y $\Delta t$ el paso de integración en milisegundos.

### 4.5. Patrones de uso

1. **Reinicio por línea con `Basics/Once`:**
   En acumuladores que recorren una línea, conviene encadenar un nodo `Basics/Once` (`mode: line`) para reiniciar la memoria al comienzo de cada línea, de modo que el estado de líneas anteriores no pase a las siguientes:
   ```
   [Basics/Once (line)] ──► [Variables/Memory (remember: "accum_x" = 0.0)]
   ```

2. **Seguimiento de valores extremos:**
   Para obtener la anchura máxima de glifo en una frase a medida que se procesa:
   ```
   [Math (max: syl.width, Memory.retrieve("max_w", 0))] ──► [Memory (remember: "max_w")]
   ```

3. **Compartir valores entre subgrafos:**
   Un subgrafo tipográfico anterior puede guardar parámetros de escala o color en memoria para que un subgrafo posterior de partículas o resplandor los lea, sin cables a través del lienzo.

### 4.6. Ejemplo

Acumulador horizontal que coloca cada sílaba a continuación de la anterior, para un espaciado fluido a lo largo de la línea:

* **Conexión en el Grafo:**
  ```
  [Basics/Once (line)] ──► [Memory (mode: remember, key: "last_x", value: line.left)]
  [Memory (mode: retrieve, key: "last_x", default: line.left)] ──► [Math (+ syl.width + 10)] ──► [Memory (mode: remember, key: "last_x")]
  ```
* **Línea ASS resultante:**
  ```ass
  Dialogue: 0,0:01:12.40,0:01:15.80,Romaji,,0,0,0,,{\an7\pos(384.0, 680.0)}Ka
  Dialogue: 0,0:01:12.40,0:01:15.80,Romaji,,0,0,0,,{\an7\pos(424.0, 680.0)}ra
  Dialogue: 0,0:01:12.40,0:01:15.80,Romaji,,0,0,0,,{\an7\pos(462.5, 680.0)}o
  ```

---

## 5. Comparación de los Nodos de Variables

| Nodo | Modo Operativo | Ámbito de Vida (*Scope*) | Complejidad | Comportamiento ante Clave Ausente | Tipo de propiedad | Uso principal |
| :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| **`Sys Var`** | Consulta de entorno | Solo lectura (Nativo ASS) | $\mathcal{O}(1)$ | Emite cadena vacía `""` | Tipo C (`var_name`) | Lectura de métricas de sílaba, línea, resolución y tiempos. |
| **`Define Vars`** | Inyección local | Ciclo / Iteración actual | $\mathcal{O}(K)$ | Asigna `val_expr` literal si falla | Tipo A (`variables`) | Variables intermedias y expresiones matemáticas. |
| **`Get Var`** | Lectura dinámica | Contexto activo | $\mathcal{O}(1)$ | Emite cadena vacía `""` | Tipo C (`var_name`) | Lectura de variables y contadores `j` sin cables. |
| **`Memory`** | Escritura / Lectura | Persistente (Toda la sesión) | $\mathcal{O}(1)$ | Emite valor `default` configurado | Tipo C (`key`), Tipo A/C (`value`) | Acumuladores, movimiento iterativo y estado persistente. |

---

## 6. Tipos de Propiedad (A, B y C) y Resolución AST

Toda propiedad de tipo cadena en Pyxis es de uno de tres tipos, que determinan cómo la tratan el motor, el evaluador de cadenas y el validador estático:

### 6.1. Tipo A: fórmulas matemáticas y expresiones AST

* **Runtime:** Se evalúan numéricamente, línea por línea, con el motor de expresiones de Python. Soportan:
  * Operadores aritméticos: `+`, `-`, `*`, `/`, `//`, `%`, `**`.
  * Condicionales ternarios: `valor_a if condicion else valor_b`.
  * Funciones matemáticas: `math.sin()`, `math.cos()`, `math.radians()`, `math.sqrt()`, `abs()`, `min()`, `max()`, `round()`.
  * Funciones aleatorias deterministas ligadas a iteradores: `by.<iter>.R(min, max)`, `by.syl.R(min, max)`, `R()`, `Rm()`.
* **Linter:** Se analizan estáticamente con `ast.parse(mode="eval")`. El validador comprueba que los identificadores sean variables globales conocidas o hayan sido definidos antes en el grafo, y avisa de variables no declaradas y de errores de sintaxis.
* **Ejemplos:**
  * `Variables/Define Vars`: propiedad `variables` (`Vars`).
  * `Basics/Math`: entradas y campos numéricos `A`, `B`.
  * `Functions/Conditioner`: campo `condition`.
  * `Basics/Only`: campo `condition`.
  * `Shape/Filter`: campos `expr_x`, `expr_y`.

### 6.2. Tipo B: plantillas de tags ASS y macros

* **Runtime:** El evaluador de cadenas (`string_evaluator.py`) las procesa en orden:
  * Sustitución de variables entre paréntesis en tags ASS: `\pos(syl.x, syl.y)`, `\frz(rot)`, `\fscxy(escala)`.
  * Atajos temporales de animación: modificadores de tiempo (`2li`, `3lo`, `1m1`) y números de fotograma (`10f`).
  * Expansión de Dark Tags (`~`, `\tagR(...)`).
  * Las subexpresiones aritméticas entre paréntesis, `\tag(subexpr)`, se pasan al evaluador de Tipo A.
* **Linter:** Se revisan con la validación de sintaxis de tags ASS (`_validate_tags`): delimitadores equilibrados (`{`, `}`, `(`, `)`) y número de argumentos esperado para cada tag ASS. Las subexpresiones numéricas se validan con las reglas de Tipo A.
* **Ejemplos:**
  * `Basics/Dynamic Format`: campo `format`.
  * `System/Output`: entradas `Tags` y `Return`.
  * `Basics/MultiTag`: campos de prefijo y sufijo de tags.

### 6.3. Tipo C: texto plano, identificadores y pass-through

* **Runtime:** Se tratan como cadenas literales, sin análisis ni evaluación de expresiones.
* **Linter:** Solo se comprueba que los paréntesis y llaves estén equilibrados, para no romper el formato del subtítulo en Aegisub. **Nunca se pasan a `ast.parse`**, para evitar falsos positivos con cadenas que contengan operadores o texto libre.
* **Ejemplos:**
  * `Variables/Get Var`: campo `var_name`.
  * `Variables/Memory`: campo `key`.
  * `Basics/String`: campo `value`.
  * `Basics/Text`: campo `text`.
  * `Functions/Conditioner`: campos de texto literal `if_true`, `if_false` (cuando no contienen tags ASS con prefijo `\`).

---

## 7. Ámbitos y Colisiones de Nombres

### 7.1. Ámbitos en bucles anidados

Al procesar los subtítulos, Pyxis desciende por una jerarquía de contextos. Cada ámbito hereda las variables de los ámbitos superiores, pero las variables locales inyectadas en un sub-bucle no suben hacia ellos:

$$\text{Línea (Global)} \longrightarrow \text{Unidad Principal (Sílaba / Char / Palabra)} \longrightarrow \text{Sub-Bucle (MaxLoop)} \longrightarrow \text{Retorno Iterativo (Pieza / Partícula)}$$

1. **Nivel Línea:** `line.*`, `l.*`, `line_start_time`, `line_end_time`, `line_dur`, `meta.res_x`, `meta.res_y`.
2. **Nivel Unidad Principal:** `syl.*`, `char.*`, `word.*`, `x`, `y`, `center`, `middle`, `left`, `right`, `top`, `bottom`, `width`, `height`, `i`, `n`, `dur`, `st`, `et`.
3. **Nivel Sub-Bucle:** `j`, `maxj`, `module`, `maxloop`.
4. **Nivel Retorno Iterativo:** `s_i`, `s_n` (Slicer), `a_i`, `a_n` (Array), `p_i`, `p_n` (Particles), `c_i`, `c_n` (Clip Gradient), `d_i`, `d_n` (Union & Divide).

### 7.2. Aislamiento por cola de salida (*Queue Isolation*)

Cuando el grafo tiene varios nodos `System/Output`, cada cola de renderizado procesa su subgrafo de forma aislada. Las variables declaradas con `Variables/Define Vars` en la rama de la Capa 1 no se filtran ni interfieren con las de la Capa 2.

### 7.3. Cómo evitar colisiones de nombres

1. **No sobreescribir identificadores reservados:** Evitar asignar `x`, `y`, `i`, `n`, `dur`, `st` o `et` en `Define Vars`, salvo que se quiera cambiar a propósito el movimiento del glifo mediante la propagación de propiedades del motor (`_apply_fx_setting`).
2. **Usar prefijos descriptivos:** En efectos complejos, prefijar las variables (ej. `orb_rad`, `p_vel_x`, `wave_phase`) para evitar colisiones con las globales y mantener legible el grafo.
3. **No tocar los contadores de bucle al anidar generadores:** Al combinar un bucle `Loops/MaxLoop` (`j`) con un generador de retorno como `Shape/Slicer` (`s_i`), no redefinir `j` dentro de `Define Vars`. Leer `j` con `Variables/Get Var` o referenciarlo directamente en expresiones.

---

## 8. Buenas Prácticas

### 8.1. Reiniciar `Memory` por línea

`Variables/Memory` conserva sus datos durante toda la sesión de renderizado, así que un acumulador que sume desplazamientos entre sílabas sigue creciendo si no se reinicia. Para limitarlo a una línea de diálogo, se reinicia con `Basics/Once`:

```
[Basics/Once (mode: line)] ──► [Variables/Memory (mode: remember, key: "acc_x", value: 0.0)]
```

Al empezar una nueva línea de diálogo, la clave `"acc_x"` vuelve a `0.0`, de modo que no se arrastra estado entre líneas.

### 8.2. Cable directo o `Get Var`

* **Cable directo:** Para dependencias locales e inmediatas dentro del mismo subgrafo visual. El flujo de datos queda visible en el lienzo.
* **Nodo `Get Var`:** Para estos casos:
  * Un valor calculado en un extremo de un lienzo grande debe llegar a ramas distantes, y así se evitan cables largos que se cruzan (*wire clutter*).
  * Se leen iteradores inyectados (`j`, `s_i`, `a_i`) que no tienen puerto de salida en el nodo de bucle.
  * Se alimentan nodos que solo ofrecen campos de texto inline.

### 8.3. Dónde colocar `Define Vars`

`Variables/Define Vars` debe ir **aguas arriba (*upstream*)** de los nodos que usan sus variables, para que estén disponibles en cada iteración. Lo habitual es intercalarlo en la cadena de paso (*pass-through*) que une `Loops/Main Loop` con `System/Output`.

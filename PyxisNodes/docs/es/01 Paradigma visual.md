# Paradigma Visual

Pyxis Effector es un entorno de nodos conectados en un grafo para procesar y generar subtítulos en formato ASS (*Advanced SubStation Alpha*). La iteración, el cálculo numérico, las transformaciones geométricas y la compilación de etiquetas están separados en nodos independientes que se conectan entre sí.

---

## 1. Principios del Grafo

El motor trabaja con un grafo dirigido acíclico (DAG) que tiene dos tipos de enlaces:

```
[Main Loop] ---> [MaxLoop / Sub-iterador] ---> [Script / Transform] ---> [Output]
     │                                                ▲
     │ (Contexto activo)                              │ (Datos evaluados bajo demanda)
     └───────────────────> [Nodos de Datos / Tags] ───┘
```

### 1.1. Enlaces de Flujo (*Flow / Loop Links*)
Los enlaces de flujo fijan el orden y el anidamiento con que se evalúan las ramas del efecto, y cuántas veces se ejecuta cada una (por línea, sílaba, carácter, sub-partícula o fotograma de vídeo). Se conectan mediante los puertos `Loop`, `Loop In` y `Loop Out`. Los nodos de flujo principales son:

* `Main Loop`: itera sobre la unidad base (línea, palabra, sílaba o carácter).
* `MaxLoop`: multiplicador de eventos o bucle sub-fotograma *FBF*.
* `Script Code`: inyecta código Python / Lua.
* `Output`: ensambla el resultado y emite las líneas ASS.

### 1.2. Enlaces de Datos (*Data Links*)
1. **Tipos:** valores numéricos (`float`/`int`), cadenas de texto, pares de coordenadas cartesianas $(x, y)$, colores hexadecimales y ASS (`&HBBGGRR&`), código vectorial ASSdraw (`m ... l ... b ...`) y bloques de etiquetas ASS (`{\pos...\t...\clip}`).
2. **Evaluación bajo demanda (*Lazy Evaluation*):** un nodo de datos solo se calcula cuando el flujo activo pide su valor en la iteración actual. Una rama de datos que no está conectada a un nodo de flujo activo no consume CPU ni memoria.
3. **Ramificación:** una salida puede alimentar varias entradas sin coste adicional, porque los resultados se memorizan dentro de cada ciclo.

---

## 2. Jerarquía de Contextos y Ciclo de Vida de los Datos

Un efecto se procesa en cinco fases:

```
[1. Selección en Aegisub]
           │
           ▼
[2. Dominio Base: Main Loop] (line / syl / word / char)
           │
           ▼
[3. Sub-dominio: MaxLoop] (Clones, Partículas, Cuadros FBF)
           │
           ▼
[4. Transformación de Datos] (Vectores, Tags, Audio, Interpolaciones)
           │
           ▼
[5. Ensamblado Terminal: Output] ───> [Nuevas Líneas ASS en Capas]
```

### Fase 1: Selección y Análisis de Entrada
El motor lee las líneas de diálogo del archivo ASS cargado en Aegisub según el ámbito configurado en `Output` (`apply_to`):
* `Sel. Lines`: solo las líneas seleccionadas en la grilla de Aegisub.
* `Style Lines`: todas las líneas con el mismo estilo que la selección.
* `All Lines`: todas las líneas de diálogo del archivo.

Cada línea se analiza y se descompone en sus métricas tipográficas y sus marcas de tiempo de karaoke (`\k`, `\kf`, `\ko`).

### Fase 2: Iteración Base (`Main Loop`)
`Main Loop` define la unidad base de iteración (`iterator`):
* **`syl`:** una iteración por sílaba, usando las marcas de karaoke. Expone las métricas y los tiempos de la sílaba (`syl.start_time`, `syl.duration`, `syl.text`, etc.).
* **`char`:** una iteración por carácter, de modo que cada glifo puede animarse de forma independiente.
* **`word`:** una iteración por palabra, delimitada por espacios.
* **`line`:** una iteración por línea de diálogo.

La propiedad `blank_mode` (`no_blank` / `with_blanks`) controla si los espacios en blanco se omiten o se procesan como elementos con ancho pero sin glifo visible.

### Fase 3: Sub-bucles (`MaxLoop`) y Anidamiento de Generadores
Para estelas, enjambres de partículas, réplicas con retardo o animaciones fotograma a fotograma *FBF*, el flujo pasa por uno o varios nodos `MaxLoop`. Cada uno multiplica la unidad actual por $N$ sub-iteraciones, expone un contador local (por defecto `j`, de $1 \dots N$) y subdivide el intervalo de tiempo.

Dentro de cada hoja de ejecución de `Main Loop` / `MaxLoop`, el motor recorre además los **nodos generadores de sub-bucles** conectados a `Output` (`Shape/Slicer`, `Shape/Union & Divide`, `Shape/Concentric Borders`, `Shape/Array`, `Shape/Multi`, `Functions/Particles`, `Functions/IMG to pixels`, `Functions/Clip Gradient`, `Functions/Animation`) en **orden topológico post-orden (raíz $\to$ hoja)**:
1. **Canal de geometría (`Output.Return`):** los generadores conectados en serie (ej. `Slicer` $\to$ `Particles`) anidan sus sub-bucles ($s_i = 1 \dots S$ externo $\to$ $p_i = 1 \dots P_k$ interno). Las coordenadas de anclaje (`pos_x`, `pos_y`, `org_x`, `org_y`) pasan de cada pieza padre a sus sub-piezas o partículas hijas.
2. **Canal de etiquetas y recortes (`Output.Tags`):** se ejecuta como sub-bucle interno para cada pieza o partícula emitida por `Output.Return`, en el orden de puertos `In1, In2, ...` de `Concatenate`. Así se puede combinar, por ejemplo, `Slicer` ($s_i$) en `Return` con `Clip Gradient` ($c_i$) y `Animation` ($an_i$) en `Tags` sin que los contadores colisionen.

### Fase 4: Evaluación y Deformación
Los nodos de datos conectados calculan las posiciones `\pos`, las deformaciones de vectores (cortes con `Slicer`, hinchado/escalado con `Transform`, contorno/extrusión con `Stroke`), los degradados de color con `Color Gradient`, la modulación por audio con `Modulator` y las transformaciones temporales aceleradas con `Retime` e `Ipol`.

### Fase 5: Ensamblado y Emisión (`Output`)
`Output` reúne los flujos procesados, combina los bloques de etiquetas del puerto `Tags` con los dibujos/textos del puerto `Return`, resuelve las colisiones entre tags, aplica las capas de renderizado (`Layer`) y escribe las líneas resultantes en el documento de Aegisub.

#### Varios Output y Aislamiento de Contexto
Para generar varias capas simultáneas (por ejemplo, sombra, cuerpo del glifo y partículas), se colocan varios nodos `System/Output` en el mismo lienzo:
* **Ramas independientes:** cada `Output` evalúa su propio árbol hacia atrás (*upstream*).
* **Aislamiento de contexto (`context`):** cada rama e iteración recibe un contexto limpio y privado. Las variables locales, los cálculos temporales y las mutaciones hechas en la rama de un `Output` no pasan a otra, aunque compartan lienzo o acaben en la misma pista de subtítulos.

#### Colas de Salida (`Queue ID` y `Queue Order`)
Las colas solo ordenan y agrupan las líneas una vez generadas. No intervienen en cómo se evalúan los nodos.
1. **`Queue ID` $\to$ campo `Actor` de ASS:**
   * El texto de `Queue ID` se escribe en el campo `Actor` del evento ASS resultante:
     $$\texttt{Dialogue: Layer}, \, t_{\text{start}}, \, t_{\text{end}}, \, \text{Style}, \, \mathbf{Queue\_ID}, \, \text{MarginL}, \, \text{MarginR}, \, \text{MarginV}, \, \text{Effect}, \, \text{Text}$$
   * Así se pueden filtrar y ordenar las capas generadas en la grilla de Aegisub.
2. **`Queue Order`:**
   * Define el orden en que se escriben los bloques de líneas en el documento ASS final.
   * El motor agrupa las líneas por cola y emite primero **todas las colas de menor `Queue Order`, para todas las líneas de diálogo**, y después las de orden superior:
     $$\text{SortKey}(Q) = \left(\min_{l \in Q} (\text{queue\_order}_l), \, \text{qid}\right)$$
   * **Empates y valores por defecto:**
     * *Orden igual u omitido:* las colas sin `Queue Order` explícito, o con el mismo valor entero, se ordenan **alfabéticamente por `Queue ID`**.
     * *Ambos campos vacíos:* las líneas van a la cola `"default"`, en el orden de creación del nodo (su `ID` en el lienzo).
     * *Dentro de una cola:* las líneas se ordenan por el índice de la línea de diálogo (`line_idx`) y luego por el orden interno del evento:
        $$\text{SortKey}(l) = (\text{queue\_order}_l, \, \text{line\_idx}_l)$$

---

## 3. Persistencia de Estados y Variables de Contexto

Tres nodos permiten registrar, pasar y acumular estado entre las fases de evaluación:

1. **`Define Vars` (`Variables`):** añade variables propias al contexto de ejecución (ej. `my_scale = 120`, `custom_color = "#FF00AA"`). Cualquier expresión posterior en la iteración actual puede usarlas de inmediato.
2. **`Get Var` (`Variables`):** lee y emite el valor de cualquier variable del contexto (`i`, `j`, `N`, `syl.duration`, `line.start_time`, `fx.pos_x`, etc.).
3. **`Memory` (`Variables`):** almacén clave-valor persistente con dos modos:
   * `remember`: guarda el valor actual bajo una clave.
   * `retrieve`: devuelve el último valor guardado bajo esa clave en iteraciones anteriores. Sirve para acumuladores de posición, trayectorias continuas o para leer estados previos.

---

## 4. Referencia de Variables del Contexto ASS

Las variables de tiempo parten de orígenes distintos según la unidad:
* **`line` / `l`:** tiempos globales y absolutos del vídeo ($ms$).
* **`syl` / `word`:** relativos al inicio de la línea base ($[0, \text{line.dur}]$).
* **`char`:** relativos al inicio de su sílaba contenedora ($[0, \text{syl.dur}]$).
* **`fx`:** duración de la línea ASS generada ($[0, \text{fx.dur}]$). Para evaluar bloques `\t(...)` en el tiempo del efecto se usa el desfase $\text{ini} = \text{line.start\_time} - \text{fx.start\_time}$.

Las siguientes variables están disponibles en cualquier campo de expresión, condición o script, agrupadas por dominio.

### 4.1. Línea de Origen (`line.` o `l.`)
La línea de diálogo activa leída de Aegisub: marcas de tiempo absolutas, texto, metadatos de la cabecera ASS, coordenadas en pantalla y márgenes.

| Variable | Tipo | Descripción y Unidad | Ejemplo de Uso |
| :--- | :---: | :--- | :--- |
| `line.start_time` / `l.start_time` | `int` | Tiempo de inicio absoluto de la línea en el vídeo ($ms$). | `line.start_time - 500` |
| `line.end_time` / `l.end_time` | `int` | Tiempo de fin absoluto de la línea en el vídeo ($ms$). | `line.end_time + 300` |
| `line.dur` / `line.duration` / `l.dur` | `int` | Duración de la línea ($ms$): $t_{\text{end}} - t_{\text{start}}$. | `line.dur / 2` |
| `line.mid_time` / `l.mid_time` | `float` | Punto medio de la línea: $t_{\text{start}} + \frac{t_{\text{dur}}}{2}$. | `line.mid_time` |
| `line_start_time`, `line_end_time`, `line_dur` | `int` | Alias planos sin prefijo para los tiempos de la línea ($ms$). | `line_start_time` |
| `line.i` / `l.i` | `int` | Índice de la línea activa en el lote procesado ($1 \dots N$). | `line.i == 1` |
| `line.n` / `l.n` | `int` | Cantidad de líneas seleccionadas en el lote. | `line.i / line.n` |
| `line.text` / `l.text` | `string` | Texto sin etiquetas de estilo ni marcas de karaoke. | `len(line.text)` |
| `line.raw_text` / `l.raw_text` | `string` | Texto original, con las etiquetas `{\...}` y las marcas `\k`. | `line.raw_text` |
| `line.style` / `line.style_name` | `string` | Nombre del estilo ASS asignado a la línea en Aegisub. | `line.style == "Default"` |
| `line.actor` / `l.actor` | `string` | Campo de actor de la línea ASS. | `line.actor` |
| `line.effect` / `l.effect` | `string` | Campo de efecto de la línea ASS. | `line.effect` |
| `line.layer` / `l.layer` | `int` | Capa ASS de la línea (profundidad $Z$). | `line.layer + 1` |
| `line.center`, `line.middle` / `l.x`, `l.y` | `float` | Centro horizontal ($X$) y vertical ($Y$) del *bounding box* de la línea (px). | `line.center, line.middle` |
| `line.left`, `line.right` | `float` | Bordes izquierdo y derecho de la línea (px). | `line.right - line.left` |
| `line.top`, `line.bottom` | `float` | Bordes superior e inferior de la línea (px). | `line.bottom` |
| `line.width`, `line.height` | `float` | Anchura y altura del texto de la línea completa (px). | `line.width` |
| `line.descent` (o `l.descend`), `line.extlead` | `float` | Descenso de la fuente e interlineado externo (px). | `line.bottom + line.descent` |
| `line.pos_x`, `line.pos_y` | `float` | Posición absoluta de la línea (`\pos` explícito o calculado). | `line.pos_x, line.pos_y` |
| `line.org_x`, `line.org_y` | `float` | Origen de rotación de la línea (`\org` o centro métrico). | `line.org_x, line.org_y` |
| `line.margin_l`, `line.margin_r`, `line.margin_v` | `int` | Márgenes izquierdo, derecho y vertical definidos en la línea o el estilo (px). | `line.margin_l` |
| `line.margin_t`, `line.margin_b` | `int` | Márgenes superior e inferior (px). | `line.margin_t` |

### 4.2. Estilo de Origen (`line.<style_prop>`)
Propiedades de fuente, color, contorno y alineación tomadas de la cabecera `[V4+ Styles]` del archivo ASS, o sobreescritas en la línea.

| Variable | Tipo | Descripción y Formato | Ejemplo de Uso |
| :--- | :---: | :--- | :--- |
| `line.fontname` | `string` | Familia tipográfica del estilo original (ej. `"Arial"`, `"Montserrat"`). | `line.fontname` |
| `line.fontsize` | `float` | Tamaño de fuente del estilo base ($pt$). | `line.fontsize * 1.5` |
| `line.bold` | `bool` | Negrita definida en el estilo (`True` / `False`). | `line.bold` |
| `line.italic` | `bool` | Cursiva definida en el estilo (`True` / `False`). | `line.italic` |
| `line.underline` | `bool` | Subrayado definido en el estilo (`True` / `False`). | `line.underline` |
| `line.strikeout` | `bool` | Tachado definido en el estilo (`True` / `False`). | `line.strikeout` |
| `line.align` | `int` | Alineación Numpad del estilo ($1 \dots 9$). | `line.align` |
| `line.scale_x`, `line.scale_y` | `float` | Escalas horizontal y vertical del estilo base ($100.0 = 100\%$). | `line.scale_x` |
| `line.spacing` | `float` | Espaciado entre caracteres en píxeles (`\fsp`). | `line.spacing` |
| `line.outline` / `line.bord` | `float` | Grosor del contorno del estilo en píxeles (`\bord`). | `line.outline` |
| `line.shadow` / `line.shad` | `float` | Distancia de la sombra del estilo en píxeles (`\shad`). | `line.shadow` |
| `line.color1` | `string` | Color primario del estilo (`\1c`) en formato ASS `&HBBGGRR&`. | `line.color1` |
| `line.color2` | `string` | Color secundario o de karaoke del estilo (`\2c`) en formato ASS `&HBBGGRR&`. | `line.color2` |
| `line.color3` | `string` | Color del contorno del estilo (`\3c`) en formato ASS `&HBBGGRR&`. | `line.color3` |
| `line.color4` | `string` | Color de la sombra del estilo (`\4c`) en formato ASS `&HBBGGRR&`. | `line.color4` |
| `line.alpha1` .. `line.alpha4` | `string` | Canales alfa (1: primario, 2: karaoke, 3: borde, 4: sombra) en ASS `&HAA&`. | `line.alpha1` |
| `line.angle` / `line.frz` | `float` | Ángulo de rotación $Z$ definido en el estilo, en grados. | `line.frz` |
| `line.frx`, `line.fry` | `float` | Ángulos de rotación 3D de la línea, en grados. | `line.frx` |
| `line.fax`, `line.fay` | `float` | Factores de cizallamiento (*shear*) en $X$ e $Y$. | `line.fax` |

### 4.3. Sílabas (`syl`), Caracteres (`char`) y Palabras (`word`)
Unidades que genera `Main Loop` al iterar en modo `syl`, `char` o `word`. Cada unidad hereda las propiedades de fuente del estilo base (`syl.fontname`, `syl.color1`..`4`, `syl.fontsize`, `char.fontname`, etc.).

| Unidad | Variable | Descripción y Unidad | Ejemplo de Uso |
| :--- | :--- | :--- | :--- |
| **Sílaba (`syl`)** | `syl.start_time`, `syl.end_time` | Tiempos de inicio y fin relativos al comienzo de la línea ($ms$). | `syl.start_time` |
| | `syl.dur` / `syl.duration` | Duración de karaoke de la sílaba ($ms$). | `syl.dur` |
| | `syl.mid_time` | Punto medio de la sílaba, relativo a la línea: $t_{\text{start}} + \frac{t_{\text{dur}}}{2}$. | `syl.mid_time` |
| | `syl.syl_start`, `syl.syl_end`, `syl.syl_mid` | Rango temporal de la sílaba relativo a la línea `fx` generada ($\text{ini} + \text{syl.start\_time}$). | `\t(syl.syl_start, syl.syl_end, \tags)` |
| | `syl.i` / `syl.n` | Índice de la sílaba en la línea ($1 \dots N$) y total de sílabas. | `syl.i / syl.n` |
| | `syl.text`, `syl.text_stripped` | Texto de la sílaba sin etiquetas ni marcas de karaoke. | `syl.text` |
| | `syl.center`, `syl.middle` / `syl.x`, `syl.y` | Centro horizontal ($X$) y vertical ($Y$) del *bounding box* de la sílaba (px). | `syl.center, syl.middle` |
| | `syl.left`, `syl.right`, `syl.top`, `syl.bottom` | Bordes izquierdo, derecho, superior e inferior de la sílaba (px). | `syl.right - syl.left` |
| | `syl.width`, `syl.height` | Anchura y altura de la sílaba (px). | `syl.width` |
| | `syl.descent`, `syl.extlead` | Descenso de la fuente e interlineado de la sílaba (px). | `syl.descent` |
| | `syl.prespace`, `syl.postspace` | Espacios en blanco antes y después de la sílaba. | `syl.prespace` |
| | `syl.pos_x`, `syl.pos_y`, `syl.org_x`, `syl.org_y` | Anclaje de posición y origen de rotación de la sílaba. | `syl.pos_x, syl.pos_y` |
| **Carácter (`char`)** | `char.start_time`, `char.end_time` | Tiempos de inicio y fin relativos al comienzo de su **sílaba contenedora** ($ms$). | `char.start_time` |
| | `char.dur` / `char.duration` | Duración calculada del carácter ($ms$). | `char.dur` |
| | `char.mid_time` | Punto medio del carácter dentro de su sílaba. | `char.mid_time` |
| | `char.char_start`, `char.char_end`, `char.char_mid` | Rango temporal del carácter relativo a la línea `fx` generada ($ms$). | `\t(char.char_start, char.char_end, \tags)` |
| | `char.syl_start`, `char.syl_end`, `char.syl_mid` | Rango temporal de la sílaba contenedora relativo a la línea `fx` generada ($ms$). | `\t(char.syl_start, char.syl_end, \tags)` |
| | `char.i` / `char.n` | Índice del carácter en la línea ($1 \dots N$) y total de caracteres. | `char.i` |
| | `char.syl_i`, `char.word_i` | Posición del carácter dentro de su sílaba y dentro de su palabra. | `char.syl_i` |
| | `char.text` | El propio carácter. | `char.text` |
| | `char.center`, `char.middle` / `char.x`, `char.y` | Centro del carácter en pantalla (px). | `char.center, char.middle` |
| | `char.left`, `char.right`, `char.top`, `char.bottom` | Bordes del *bounding box* del carácter (px). | `char.left` |
| | `char.width`, `char.height` | Anchura y altura del carácter (px). | `char.width` |
| | `char.descent`, `char.extlead` | Descenso de la fuente e interlineado del carácter (px). | `char.descent` |
| **Palabra (`word`)** | `word.start_time`, `word.end_time`, `word.dur`, `word.mid_time` | Inicio, fin, duración y punto medio relativos a la línea ($ms$). | `word.start_time` |
| | `word.word_start`, `word.word_end`, `word.word_mid` | Inicio, fin y punto medio relativos a la línea `fx` generada ($ms$). | `word.word_start` |
| | `word.i` / `word.n` | Índice de la palabra en la línea ($1 \dots N$) y total de palabras. | `word.i` |
| | `word.text` | Texto de la palabra sin etiquetas. | `word.text` |
| | `word.center`, `word.middle` / `word.x`, `word.y` | Centro horizontal ($X$) y vertical ($Y$) de la palabra en pantalla (px). | `word.center, word.middle` |
| | `word.left`, `word.right`, `word.top`, `word.bottom` | Bordes del *bounding box* de la palabra (px). | `word.right` |
| | `word.width`, `word.height` | Anchura y altura de la palabra (px). | `word.width` |
| | `word.descent`, `word.extlead` | Descenso de la fuente e interlineado de la palabra (px). | `word.descent` |

### 4.4. Tinta Real (`ink`) y Unidades Vecinas (`prev` / `next`)

| Categoría | Variable | Descripción | Ejemplo de Uso |
| :--- | :--- | :--- | :--- |
| **Tinta (`ink`)** | `ink.width`, `ink.height` | Anchura y altura del glifo/trazado renderizado, sin el margen de la caja tipográfica. | `ink.width` |
| | `ink.center`, `ink.middle` / `ink.x`, `ink.y` | Centro horizontal ($X$) y vertical ($Y$) calculado sobre los contornos reales de tinta. | `ink.center, ink.middle` |
| | `ink.left`, `ink.right`, `ink.top`, `ink.bottom` | *Bounding box* exacto de los píxeles de tinta en coordenadas de pantalla. | `ink.left` |
| | `ink.l.*`, `ink.syl.*`, `ink.char.*`, `ink.word.*` | Métricas de tinta de la línea, sílaba, carácter o palabra, elegidas explícitamente por ámbito. | `ink.syl.center` |
| **Vecinos (`prev` / `next`)** | `prev.*` / `next.*` | Acceso a la unidad anterior o siguiente (`text`, `dur`, `start_time`, `x`, `y`, `width`, etc.). | `prev.width` |
| | `is_first`, `is_last` | Indican si la unidad es la primera o la última de la secuencia. | `is_first` |
| | `has_prev`, `has_next` | `True` si existe una unidad anterior o siguiente en la cadena. | `has_prev` |

### 4.5. Sub-bucles (`MaxLoop`), Efecto (`fx`) y Entorno Global

| Categoría | Variable | Descripción y Fórmula | Ejemplo de Uso |
| :--- | :--- | :--- | :--- |
| **Sub-bucle (`MaxLoop`)**| `j` | Índice de la sub-iteración activa ($1 \dots N$). | `j` |
| | `maxj` / `maxloop` | Repeticiones configuradas en el sub-bucle. | `maxj` |
| | `module` / `m` / `ratio` | Progreso normalizado del sub-bucle: $\frac{j - 1}{\text{maxj} - 1} \in [0.0, 1.0]$. | `module` |
| **Efecto (`fx`)** | `fx.pos_x`, `fx.pos_y` | Posición de anclaje resuelta del elemento activo en pantalla. | `fx.pos_x, fx.pos_y` |
| | `fx.start_time`, `fx.end_time` | Tiempos absolutos de inicio y fin de la línea ASS generada ($ms$). | `fx.start_time` |
| | `fx.dur` | Duración de la línea ASS generada ($ms$). | `fx.dur` |
| **Entorno Global** | `fps` | Fotogramas por segundo del vídeo activo en Aegisub (ej. `23.976`, `60.0`). | `fps` |
| | `frame_dur` / `fd` | Duración de un fotograma en milisegundos: $\frac{1000}{\text{fps}}$ (ej. $41.708$ ms a $23.976$ fps). | `3 * fd` |
| | `ini` | Desfase temporal: $\text{ini} = \text{line.start\_time} - \text{fx.start\_time}$ ($ms$). | `ini + syl.start_time` |
| | `st`, `et`, `dur` | Inicio, fin y duración del elemento que se está procesando ($ms$). | `st, et` |
| | `maxgap` | Límite máximo para las mediciones entre líneas con `sync()` ($ms$, por defecto `2000.0`). | `maxgap` |

---

## 5. Evaluación de Expresiones y Resolución de Strings

Los campos de texto, los nodos de cadena y los bloques de etiquetas ASS pasan por un evaluador interno (un evaluador numérico y un procesador de plantillas) que calcula expresiones matemáticas, operadores ternarios de Python y variables incrustadas.

### 5.1. Evaluación Numérica y Algebraica en Cajas de Texto
Cualquier campo numérico (en `MultiTag`, `Math`, `Retime`, `Slicers`, `Particles`, etc.) evalúa operaciones matemáticas en tiempo real:
* **Álgebra y funciones:** `syl.center + (i * 15)`, `line.width / 2`, `math.sin(t) * 50`.
* **Atajos de fotogramas y ratios:** `3f` ($3 \times \text{frame\_dur}$), `0.5r` ($50\%$ de la duración).
* **Hexadecimales ASS:** `&HFF&` se evalúa como `255`.

### 5.2. Expresiones Ternarias de Python
Los nodos de variables (`Define Vars`) y los campos condicionales aceptan la sintaxis ternaria de Python:
```python
angle = 1.4 if l.layer == 1 else -1.4
color_fx = "&H00FF00&" if syl.i % 2 == 0 else "&H0000FF&"
```

### 5.3. Evaluación de Strings y Bloques de Tags ASS
Los bloques de etiquetas entre llaves `{\...}` de cualquier nodo que produzca subtítulos (incluyendo `Basics/String`, `Basics/MultiTag`, `System/Output`, transformaciones vectoriales y capas cinemáticas) los procesa el motor de plantillas antes de la exportación final.

> [!IMPORTANT]
> **Aislamiento de trazados ASSdraw:** el evaluador solo actúa dentro de los bloques de etiquetas `{\...}`. El texto plano y los comandos de dibujo vectorial (`m 0 0 l 100 0 ...`) fuera de las llaves nunca se tocan, así que las coordenadas geométricas no se confunden con identificadores ni variables.

El lenguaje de plantillas tiene 4 mecanismos de resolución:

1. **Expresiones algebraicas y variables entre paréntesis de tags ASS (`\tag(...)`):**
   * Rotaciones y escalas: `\frz(rot)`, `\frz(j * 15)`, `\fscxy(120 + i*5)`.
   * Posiciones y pivotes: `\pos(syl.center + 10, syl.middle)`, `\org(fx.pos_x, fx.pos_y - 1000)`.
   * Alfas y colores: `\alpha(255)`, `\1a(128)`, `\1c(line.color1)`, `\1c(ass_color(255, 128, 0))`.
2. **Transformaciones `\t(...)` dinámicas:**
   * Tiempos y tags evaluados: `\t(0, 150, \frz0)\t(fx.dur-150, fx.dur, \frz(rot))`.
3. **Expresiones, variables y ternarios sueltos entre paréntesis `(...)`:**
   * Variables, atributos y cálculos fuera de tags: `(syl.text)`, `(syl.dur)`, `(fx.dur)`, `(j * 15)`, `(line.text)`.
   * Selección condicional de etiquetas o valores dentro del bloque: `(\blur3 if i == 1 else \blur0)`, `(Colores())`.
4. **Conversión automática de alfas decimales a hexadecimal ASS:**
   * Los enteros se convierten a hex ASS: `\4a100` $\to$ `\4a&H64&`, `\alpha255` $\to$ `\alpha&HFF&`, `\1a0` $\to$ `\1a&H00&`.

---

### 5.4. Dark Tags (Tags Compuestos y de Contexto)

Los *Dark Tags* son macros compactas que expanden una sintaxis abreviada a secuencias ASS normales.

#### 5.4.1. Rotaciones con Auto-Origen (`\fr*o`)
Añaden una etiqueta `\org(X, Y)` centrada en el elemento activo del fotograma actual (`fx.pos_x`, `fx.pos_y` o `syl.center`, `syl.middle`):

| Dark Tag | Sintaxis Directa | Sintaxis Evaluada | Expansión ASS Generada |
| :--- | :--- | :--- | :--- |
| `\fro`, `\frzo` | `\fro45`, `\frzo-30` | `\fro(j * 15)` | `\org(X, Y)\frz<val>` |
| `\frxo` | `\frxo30` | `\frxo(syl.i * 5)` | `\org(X, Y)\frx<val>` |
| `\fryo` | `\fryo60` | `\fryo(sin(j) * 45)` | `\org(X, Y)\fry<val>` |
| `\frxyo` | `\frxyo45` | `\frxyo(15)` | `\org(X, Y)\frx<val>\fry<val>` |
| `\frxzo` | `\frxzo30` | `\frxzo(20)` | `\org(X, Y)\frx<val>\frz<val>` |
| `\fryzo` | `\fryzo45` | `\fryzo(25)` | `\org(X, Y)\fry<val>\frz<val>` |
| `\frxyzo` | `\frxyzo30` | `\frxyzo(10)` | `\org(X, Y)\frx<val>\fry<val>\frz<val>` |

#### 5.4.2. Escalas y Tamaño por Ratio de Estilo (`\fsc*r`, `\fsr`)
Multiplican el valor definido en el estilo de Aegisub (`style.scale_x`, `style.scale_y`, `style.fontsize`) por el factor indicado:

| Dark Tag | Sintaxis Directa | Sintaxis Evaluada | Expansión ASS Generada |
| :--- | :--- | :--- | :--- |
| `\fscxr` | `\fscxr1.5` | `\fscxr(1.0 + 0.2*j)` | `\fscx(style.scale_x * ratio)` |
| `\fscyr` | `\fscyr0.8` | `\fscyr(cos(t))` | `\fscy(style.scale_y * ratio)` |
| `\fscxyr` | `\fscxyr2.0` | `\fscxyr(1.5)` | `\fscx(style.scale_x * ratio)\fscy(style.scale_y * ratio)` |
| `\fsr` | `\fsr1.2` | `\fsr(1.0 + syl.i * 0.1)` | `\fs(style.fontsize * ratio)` |

#### 5.4.3. Transformaciones Temporales Contextuales (`\te`, `\ts`, `\tc`, `\tw`)
Atajos de tiempo que se adaptan a la duración total del efecto o a la posición del elemento:

| Dark Tag | Sintaxis de Uso | Expansión ASS Resultante | Descripción |
| :--- | :--- | :--- | :--- |
| `\te` | `\te(t1, t2, \tags)`<br>`\te(t1, t2, accel, \tags)`<br>`\te(t, \tags)` | `\t(fx.dur - t2, fx.dur - t1, \tags)`<br>`\t(fx.dur - t2, fx.dur - t1, accel, \tags)`<br>`\t(fx.dur - t, fx.dur, \tags)` | Animación temporizada hacia atrás desde el final de la línea (`fx.dur`). |
| `\ts` | `\ts(t1, t2, \tags)`<br>`\ts(t1, t2, accel, \tags)`<br>`\ts(t, \tags)` | `\t(syl.start_time + t1, syl.start_time + t2, \tags)`<br>`\t(syl.start_time + t1, syl.start_time + t2, accel, \tags)`<br>`\t(syl.start_time, syl.start_time + t, \tags)` | Animación relativa al inicio de la sílaba. |
| `\tc` | `\tc(t1, t2, \tags)`<br>`\tc(t1, t2, accel, \tags)`<br>`\tc(t, \tags)` | `\t(char.start_time + t1, char.start_time + t2, \tags)`<br>`\t(char.start_time + t1, char.start_time + t2, accel, \tags)`<br>`\t(char.start_time, char.start_time + t, \tags)` | Animación relativa al inicio del carácter. |
| `\tw` | `\tw(t1, t2, \tags)`<br>`\tw(t1, t2, accel, \tags)`<br>`\tw(t, \tags)` | `\t(word.start_time + t1, word.start_time + t2, \tags)`<br>`\t(word.start_time + t1, word.start_time + t2, accel, \tags)`<br>`\t(word.start_time, word.start_time + t, \tags)` | Animación relativa al inicio de la palabra. |

#### 5.4.4. Tags Multicanal y Agrupados
| Dark Tag | Expansión ASS Directa | Ejemplo |
| :--- | :--- | :--- |
| `\fscxy` | `\fscx<val>\fscy<val>` | `\fscxy150` $\to$ `\fscx150\fscy150` |
| `\faxy` | `\fax<val>\fay<val>` | `\faxy0.2` $\to$ `\fax0.2\fay0.2` |
| `\frxyz`, `\frxy`, `\frxz`, `\fryz` | Rotaciones 3D combinadas | `\frxyz45` $\to$ `\frx45\fry45\frz45` |
| `\xybord`, `\xyshad`, `\bs` | Borde y sombra a la vez | `\bs3` $\to$ `\bord3\shad3` |
| `\[1-4]+c` (ej. `\134c`, `\13c`, `\234c`) | Varios colores a la vez | `\134c&H00FFFF&` $\to$ `\1c&H00FFFF&\3c&H00FFFF&\4c&H00FFFF&` |
| `\[1-4]+a` (ej. `\134a`, `\14a`, `\34a`) | Varios alfas a la vez | `\134a&H80&` $\to$ `\1a&H80&\3a&H80&\4a&H80&` |

#### 5.4.5. Restauración de Estilo (`\tag~`) y Valores Aleatorios (`\tagR(...)`)
* **Restauración (`~`):** recupera el valor del estilo original: `\c~` (color primario), `\fscxy~` (escala $X/Y$ base), `\fs~` (tamaño de fuente), `\bs~` (borde y sombra base), `\134c~`, `\134a~`, `\frxyz~`, `\blur~`.
* **Aleatorios (`R`):** generan variaciones aleatorias continuas o discretas: `\frzR(-30, 30)`, `\134cR()`, `\alphaR(0, 128)`, `\froR(-20, 20)`, `\fscxyrR(1.0, 1.5)`.

---

## 6. Sincronización Entre Líneas (`sync`)

`sync` mide el intervalo (*gap*, en milisegundos) entre la línea de diálogo activa y la anterior o la siguiente, ya sea en el orden original del subtítulo o entre las líneas que cumplan un criterio.

### 6.1. La Función `sync()`
Se puede usar en expresiones de tiempo, propiedades de nodos y scripts:

```python
sync(direction="next", mode="order", max_gap=2000)
```

* **`direction` (1º argumento):** `next` o `prev`. Por defecto: `next`.
* **`mode` (2º argumento):** cómo se elige la línea vecina:
  * `1` o `"order"` *(default)*: línea de diálogo siguiente/anterior en el orden del subtítulo (se ignoran las líneas de comentario).
  * `2` o `"style"`: líneas con el mismo estilo ASS (`line.style`).
  * `3` o `"actor"`: líneas con el mismo actor (`line.actor`).
  * `4` o `"effect"`: líneas con el mismo campo de efecto (`line.effect`).
  * `5` o `"layer"`: líneas con la misma capa (`line.layer`).
* **`max_gap` (3º argumento):** límite superior en milisegundos (por defecto `2000.0` ms o el valor definido en `maxgap`).

#### Ejemplos:
```python
# Extiende el final del efecto la mitad del gap a la siguiente línea (máximo 2000ms):
end_time = l.end_time + (sync(next, order) / 2)

# Adelanta el inicio del efecto la mitad del gap a la línea anterior con el mismo estilo (máximo 1500ms):
start_time = l.start_time - (sync(prev, style, 1500) / 2)

# Uso con identificadores numéricos:
start_time = l.start_time - (sync(prev, 2) / 2)
```

### 6.2. El Namespace `sync.*`
En bloques de tags (`\fad`, `\t`), el namespace `sync` expone los mismos valores como propiedades:

| Propiedad | Dirección | Filtro de Modo | Valor de Retorno |
| :--- | :---: | :---: | :--- |
| `sync.next` / `sync.order_next` | `next` | `order` | Gap a la siguiente línea de diálogo (ms). |
| `sync.prev` / `sync.order_prev` | `prev` | `order` | Gap a la línea de diálogo anterior (ms). |
| `sync.style_next` / `sync.style_prev` | `next` / `prev` | `style` | Gap a la línea adyacente con el mismo estilo. |
| `sync.actor_next` / `sync.actor_prev` | `next` / `prev` | `actor` | Gap a la línea adyacente con el mismo actor. |
| `sync.effect_next` / `sync.effect_prev` | `next` / `prev` | `effect` | Gap a la línea adyacente con el mismo efecto. |
| `sync.layer_next` / `sync.layer_prev` | `next` / `prev` | `layer` | Gap a la línea adyacente con la misma capa. |

#### Ejemplos en tags ASS:
```ass
{\fad(sync.order_prev / 2, sync.order_next / 2)}
{\t(0, sync.style_next, \fscxy120)}
{\t(fx.dur - sync.next / 2, fx.dur, \alpha&HFF&)}
```

### 6.3. Cambiar el Límite (`maxgap`)
El límite por defecto de 2000ms se puede cambiar, global o localmente, para todas las evaluaciones de `sync.*` asignando `maxgap` en un nodo `Define Vars` o en un script Python/Lua:
```python
maxgap = 3500
```
Las llamadas posteriores a `sync.order_next` o `sync(next, order)` usarán entonces `3500.0` como límite.

### 6.4. Solapamientos y Límites
* **Líneas solapadas ($\text{gap} < 0$):** si las dos líneas se superponen, `sync` devuelve el valor negativo exacto ($\Delta t < 0$), que es la duración del solapamiento.
* **Sin línea adyacente (primera/última):** si ninguna línea cumple el criterio, `sync` devuelve el límite `maxgap` configurado.

---

## 7. Telemetría de Rendimiento y Estimación Pre-Generación (`Telemetry`)

Cuando una composición combina bucles fotograma a fotograma (`MaxLoop` en modo `fbf`), segmentación poligonal (`Shape/Slicer`), partículas (`Functions/Particles`) o desenfoques (`\blur`), el rendimiento de reproducción depende sobre todo del coste de rasterizar y componer los mapas de bits de cada fotograma en `libass`.

El diagnóstico tiene dos etapas: una **estimación estática antes de generar** y la **telemetría de renderizado por fotograma**.

```
[Topología del Grafo + Selección ASS]
                 │
                 ├──► [1. Estimación Pre-Generación (Hover en Generate Layers)]
                 │      • Concurrencia Sweep-Line (Peak Simultaneous Lines)
                 │      • Factor de Expansión y Peso ASS Estimado (KB / MB)
                 │      • Perfil Vectorial (FBF / Slicer / Particles / Audio / Script)
                 │
                 └──► [2. Telemetría Nativa libass (Refresh en Previewer / Scan en Telemetry)]
                        • Renderizado C nativo paralelo + reloj de hardware QPC (1 µs)
                        • Curva de carga integrada en la barra del Previewer
                        • Panel de diagnóstico (4 métricas superpuestas + navegación 2D)
```

### 7.1. Estimación Estática Antes de Generar
Al situar el cursor sobre el botón **`Generate Layers`**, el motor evalúa la topología del grafo y las líneas de entrada sin compilar el efecto:

1. **Líneas estimadas y factor de expansión:**
   Cantidad de eventos `Dialogue:` que emitirán los nodos `System/Output` conectados ($\hat{N}_{\text{out}}$) y su relación con las líneas originales seleccionadas ($N_{\text{in}}$):
   $$\text{Expansion Ratio} = \frac{\hat{N}_{\text{out}}}{\max(1, N_{\text{in}})}$$
2. **Concurrencia máxima de líneas (*Sweep-Line Peak Simultaneous Lines*):**
   La concurrencia en un instante $t$ es la cantidad de capas que hay a la vez en pantalla. El estimador aplica un barrido de intervalos (*sweep-line*) sobre los rangos $[t_{\text{start}}, t_{\text{end}})$ proyectados de cada rama:
   $$L_{\text{peak}} = \max_{t} \sum_{k=1}^{\hat{N}_{\text{out}}} \mathbf{1}_{[t_{\text{start}, k},\, t_{\text{end}, k})}(t)$$
   Es el número de capas superpuestas en el fotograma más denso del efecto.
3. **Peso ASS estimado (`KB` / `MB`) y perfil de renderizado:**
   Longitud esperada en bytes de las líneas, ponderada según las operaciones presentes en el grafo (trazados vectoriales ASSdraw, recortes `\clip`, transformaciones `\t`), y etiquetas de los subsistemas activos (`FBF`, `Slicer`, `Particles`, `Audio`, `Script`).

### 7.2. Telemetría Nativa Multi-Proceso (`libass` + QPC)
Al ejecutar **`Refresh`** en el nodo `System/Previewer` (o **`Scan`** en el panel `Telemetry`), se mide el rendimiento de renderizado con la biblioteca nativa `libass`:

1. **Solo se mide el efecto:**
   La telemetría renderiza **únicamente las líneas generadas por el efecto**, junto con los estilos y metadatos del script. Las líneas sin modificar se dejan fuera, para que las métricas reflejen el coste del grafo activo.
2. **Procesos paralelos y cronometraje por hardware (`QPC`):**
   El rango de fotogramas del clip previsualizado se reparte en lotes entre varios procesos paralelos (`multiprocessing`). Cada proceso crea una instancia de `libass` a la resolución del proyecto ($\text{PlayResX} \times \text{PlayResY}$) y llama a `ass_render_frame` fotograma a fotograma, midiendo con el contador de rendimiento de hardware ($\text{QPC}$, resolución de $1\,\mu\text{s}$).
3. **Presupuesto de fotograma (*Frame Budget*):**
   Para reproducir a la cadencia del vídeo sin perder cuadros (*frame drops*), el tiempo de renderizado de cada fotograma ($T_{\text{render}}$) debe quedar por debajo de la duración del fotograma que fijan los $\text{FPS}$:
   $$\text{Budget}_{\text{ms}} = \frac{1000}{\text{FPS}}, \qquad \text{Budget \%} = \frac{T_{\text{render}}}{\text{Budget}_{\text{ms}}} \times 100\%$$
   A $23.976\,\text{fps}$ el presupuesto es de $41.71\,\text{ms}$ por fotograma, y a $60\,\text{fps}$ es de $16.67\,\text{ms}$. Todo fotograma que supere $\text{Budget}_{\text{ms}}$ ($\text{Budget \%} > 100\%$) se registra como una posible caída de fotograma.
4. **Memoria de bitmaps y primitivas (`ASS_Image`):**
   En cada fotograma $f$, el motor recorre la lista enlazada de mapas de bits alfa generada por `libass` ($\{I_1, I_2, \dots, I_M\}$) y extrae tres métricas:
   * **`ASS Objects` ($M_f$):** cantidad de primitivas de imagen compuestas en el fotograma.
   * **`Total Bitmap RAM`:** memoria usada por todos los mapas de bits del fotograma:
     $$\text{RAM}_{\text{total}}(f) = \frac{1}{1024} \sum_{m=1}^{M_f} \left( w_m \times h_m \right) \quad [\text{KB}]$$
   * **`Largest Bitmap`:** memoria del mayor mapa de bits individual del fotograma:
     $$\text{RAM}_{\text{max}}(f) = \frac{1}{1024} \max_{1 \le m \le M_f} \left( w_m \times h_m \right) \quad [\text{KB}]$$

### 7.3. Panel Telemetry y Navegación
El panel **`Telemetry`** (se abre desde el tooltip de `Generate Layers` o pulsando sobre la curva de carga en el `Previewer`) tiene tres regiones sincronizadas:

1. **Visor de vídeo y HUD por fotograma (arriba a la izquierda):**
   * El reproductor del nodo `System/Previewer` se acopla al visor y conserva su posición de reproducción, pista de subtítulos y zoom focal.
   * Un control de redimensionamiento mantiene la relación de aspecto original del vídeo.
   * Una barra inferior con HUD muestra el número de fotograma (`F`), el código de tiempo (`MM:SS.mmm`), el tiempo de renderizado (`ms`), la memoria de mapas de bits (`KB`/`MB`) y el conteo de objetos (`obj`).
2. **Tacómetro de presupuesto, tarjetas KPI y puntos críticos (arriba a la derecha):**
   * **Arco de presupuesto (`Frame Budget %`):** tacómetro semicircular que muestra la carga máxima como porcentaje del presupuesto de fotograma disponible.
   * **Tarjetas KPI:** valores de todo el clip: `Peak Render Time` (fotograma y marca temporal), `Average Render` (con percentil `P95`), `Frame Drops` (conteo y porcentaje del clip), `Peak Bitmap RAM` (con `Max Single`) y `Peak ASS Objects`.
   * **Lista de puntos críticos (*Critical Hotspots*):** picos locales de carga, ordenados. Al seleccionar uno, el cabezal de vídeo y el gráfico saltan a ese fotograma.
3. **Gráfico superpuesto y navegación 2D (mitad inferior):**
   * **4 métricas y multiplicadores de escala ($1\times$ – $10\times$):** curvas de `Render Time (ms)`, `Total Bitmap RAM`, `Largest Bitmap` y `ASS Objects`, junto con la línea horizontal del límite de presupuesto (`FPS Budget Limit`). Cada métrica se puede activar o desactivar por separado, y la escala vertical admite multiplicadores (`1x`, `2x`, `5x`, `10x`).
   * **Navegación:**
     * **`Rueda del Ratón`:** zoom horizontal ($X$) centrado en el cursor.
     * **`Ctrl + Rueda` / `Shift + Rueda`:** escala vertical ($Y$).
     * **`Botón Central + Arrastre`:** desplazamiento en $X$ e $Y$.
     * **`Clic Izquierdo + Arrastre`:** desplazamiento temporal (*scrubbing*) sincronizado con el vídeo.
     * **`Tecla R` / `Home`:** restablece la vista al $100\%$ del rango temporal.

> [!NOTE]
> **Estado limpio por sesión:** tanto el gráfico del menú `Telemetry` como el mapa de calor del `Previewer` empiezan vacíos al abrir una sesión nueva o crear un nodo `Previewer`. Solo se rellenan con mediciones reales después de aplicar o refrescar el efecto actual.

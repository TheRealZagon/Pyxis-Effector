# System

La categoría **System** reúne los nodos que escriben los eventos finales en Aegisub, los previsualizan en tiempo real con WebAssembly (JASSUB/libass), ejecutan código Python y Lua y miden el rendimiento de la ejecución.

---

## 1. Nodo `System/Output` (Ensamblador Terminal y Emisor ASS)

Último nodo obligatorio de un grafo. Compila los eventos recibidos, resuelve las precedencias de estilo y escala de fuente, ordena la salida por colas y escribe las líneas resultantes en el archivo ASS activo de Aegisub.

![System/Output](img/output.jpg)

### 1.1. Modos de Cabecera
1. **`[2.1] Apply to` (`apply_to`):** Líneas del documento de Aegisub a las que se aplica el grafo:
   * `Sel. Lines` (*Selected Lines*): Solo las líneas seleccionadas en la grilla de Aegisub.
   * `Style Lines`: Las líneas cuyo estilo coincide con el de la selección activa.
   * `All Lines`: Todas las líneas de diálogo del archivo.

### 1.2. Puertos de Entrada
1. **`Loop / Domain`:** Señal de flujo principal, procedente del último nodo de la rama (`Main Loop`, `MaxLoop`, `Script Code`).
2. **`Layer`:** Capa ASS de la línea generada (ej. `0`, `1`, `5`). Si no está conectado, se mantiene la capa de la línea original.
3. **`Start Time`:** Tiempo de inicio en milisegundos. Si no está conectado, usa el `start_time` calculado en el contexto activo.
4. **`End Time`:** Tiempo de fin en milisegundos. Si no está conectado, usa el `end_time` del contexto activo.
5. **`Tags`:** Bloque consolidado de etiquetas ASS (`{\pos...\1c...\blur...}`), escrito al inicio de la línea de diálogo.
6. **`Return`:** Contenido del evento: diálogo plano o trazados vectoriales ASSdraw (`m ... l ... b ...`).
7. **`Queue ID`:** Identificador alfanumérico opcional que agrupa las líneas generadas en una cola lógica. Se escribe en el campo `Actor` de cada línea `Dialogue:`.
8. **`Queue Order`:** Prioridad entera que determina la posición de la cola en el documento de subtítulos.

### 1.3. Propiedades del Cuerpo
1. **`[2.2] Queue ID` (`queue_id`):** Identificador de cola usado si el puerto de entrada no está conectado (defecto: `""` $\to$ cola `"default"`).
2. **`[2.3] Queue Order` (`queue_order`):** Prioridad de cola usada si el puerto no está conectado (defecto: `""` $\to$ orden `0`).
3. **`origin_align`:** Alineación numérica del origen para el cálculo de anclajes (defecto: `5` / Centro).

### 1.4. Puertos de Salida
1. **`[1.1] Preview`:** Envía los eventos compilados a `System/Previewer`.

### 1.5. Compilación
Para cada línea, el nodo:
1. Valida `start_time` y `end_time`, garantizando $t_{\text{end}} \ge t_{\text{start}}$.
2. Fusiona las etiquetas recibidas en `Tags`, eliminando duplicados sintácticos directos.
3. Resuelve la **precedencia de escala (`\fscx`/`\fscy`)**. Si el estilo ASS tiene una escala distinta del 100%, libass y VSFilter deformarían los trazados vectoriales definidos en coordenadas absolutas. Para evitarlo, el motor aplica cuatro niveles:
   * **Nivel 1 (Texto plano o karaoke):** No se añaden etiquetas de escala. El texto hereda la escala del estilo.
   * **Nivel 2 (Estilo ASS):** Define la escala base.
   * **Nivel 3 (Formas vectoriales):** Si el contenido es un trazado vectorial (`\p1`, ASSdraw `m ...`), el motor inyecta `\fscx100` y `\fscy100` para anular la escala del estilo y conservar las proporciones 1:1 en pantalla.
   * **Nivel 4 (Etiqueta explícita del usuario):** Si el usuario conecta o escribe `\fscx` o `\fscy` en `Tags`, esa etiqueta prevalece sobre el valor neutro.
4. Rastrea el estado de estilo (`ActiveStyleState`):
   * **Camino rápido:** Si la línea no contiene etiquetas de sobreescritura (karaoke simple como `{\k50}`), se omite la máquina de estados.
   * **Máquina de estados por sílaba:** Si la línea contiene etiquetas (`\pos`, `\an`, `\fs`, `\fscx`, `\fscy`, `\fsp`, `\b`, `\i`, `\bord`, `\shad`, `\1c`..`\4c`, `\alpha`, `\1a`..`\4a`, `\frz`, `\r`), las modificaciones se acumulan bloque por bloque.
   * **Medición de texto:** El `width` y el `height` de cada unidad se calculan con el motor tipográfico, según el tamaño y el formato efectivos de la fuente activa.
   * **Posicionamiento:** Un `\pos(x,y)` explícito ancla la línea a esas coordenadas según la alineación efectiva `\an`. Las coordenadas derivadas se proyectan a las sílabas y caracteres hijos.
   * **Herencia:** Las unidades de contexto (`syl`, `char`, `word`, `line`) resuelven las propiedades de estilo en cascada: `Unidad -> Línea -> Estilo -> Valores por defecto`.
   * **Espaciado:** Cuando el estilo define `Spacing > 0` o hay una etiqueta `\fsp`, el espaciado horizontal efectivo es $S_{\text{eff}} = \text{Spacing} \times \frac{\text{ScaleX}}{100} \times \text{FactorX}$. Se aplica de forma uniforme entre sílabas contiguas y entre glifos individuales (`char.left`, `char.center`, `char.right`), igual que libass/VSFilter.
5. Escribe la línea en formato ASS estándar, con `Queue ID` en el campo `Actor`:
   $$\texttt{Dialogue: } \text{Layer}, \, t_{\text{start}}, \, t_{\text{end}}, \, \text{Style}, \, \mathbf{Queue\_ID}, \, \text{MarginL}, \, \text{MarginR}, \, \text{MarginV}, \, \text{Effect}, \, \texttt{\{Tags\}} \text{Return}$$

Las colas se ordenan cuando todas las ramas han terminado:
* **Aislamiento entre ramas:** Cada nodo `Output` evalúa su rama con un contenedor de contexto propio. No comparte variables ni estados cinemáticos con otros nodos terminales.
* **Orden global:** Las líneas se agrupan por `Queue ID` y se insertan en el archivo ASS según la clave:
  $$\text{SortKey}(Q) = \left(\min_{l \in Q}(\text{queue\_order}_l), \, \text{qid}\right)$$
  * **1. Prioridad numérica:** Las colas con menor `Queue Order` se emiten primero.
  * **2. Desempate alfabético:** Si dos o más colas tienen el mismo orden, se ordenan alfabéticamente por `Queue ID`.
  * **3. Cola por omisión:** Si no se especifica cola ni orden, las líneas van a la cola `"default"`.
  * **4. Orden interno:** Dentro de cada cola, las líneas conservan el orden del evento original:
    $$\text{SortKey}(l) = (\text{queue\_order}_l, \, \text{line\_idx}_l)$$

### 1.6. Consejos
* **Composición multicapa:** Usa nodos `Output` independientes para cada capa (ej. Capa 0 para sombras con `Queue Order = 1`, Capa 1 para el texto principal con `Queue Order = 2`).
* **Queue ID como etiqueta:** Identificadores descriptivos como `"FX_Borde"` o `"FX_Relleno"` permiten filtrar, ordenar y revisar las líneas generadas en la grilla de Aegisub.

---

## 2. Nodo `System/Previewer` (Reproductor en Tiempo Real WebAssembly)

Reproduce video y subtítulos en tiempo real con WebAssembly (JASSUB/libass). La reproducción se limita al intervalo temporal del efecto. El vídeo y el audio del usuario se reproducen tal cual, sin transcodificación previa; si no hay medios cargados, el reproductor usa un clip de relleno que FFmpeg genera una vez y guarda en caché.

![System/Previewer](img/previewer.jpg)

### 2.1. Puertos de Entrada
1. **`Output`:** Se conecta al puerto `Preview` de uno o más nodos `Output`. Pueden conectarse varios a la vez para previsualizar varias capas juntas.

### 2.2. Acciones de Cabecera
1. **`[1.1] Selector de Fuente (Source Toggle)`:**
   * **Plantilla Base (icono CD / `preview_base.ass`):** Entorno de prueba aislado con video y plantilla precargados.
   * **Proyecto Activo en Aegisub (icono Aegisub):** Carga el video, audio, estilos y tiempos de la sesión abierta en Aegisub.
2. **`[1.2] Botón Fijar / Desanclar (Pin / Detach)`:**
   * Separa el visor del nodo y lo convierte en una ventana flotante, para mantener la referencia visual mientras te desplazas por el lienzo.
3. **`[1.3] Botón Refrescar (Refresh)`:**
   * Recompila las ramas conectadas a `Output`, actualiza la pista de subtítulos en JASSUB/libass y mide el rendimiento de las líneas generadas.
   * **Coexistencia en escena:** En el visor solo se comentan las líneas originales reemplazadas por el ámbito de `Output` (`Sel. Lines`, `Style Lines`, `All Lines`). El resto de diálogos y carteles siguen visibles.
4. **`[1.4] Botón Renderizar Hardsub (Exportación FFmpeg)`:**
   * Abre el asistente de exportación para incrustar los subtítulos (*hardsub*) en un MP4 con FFmpeg. La exportación solo se ejecuta al accionar este botón. (En el resto de casos FFmpeg solo genera el clip de relleno anterior y optimiza una vez el vídeo de fondo del lienzo cuando se elige.)

### 2.3. Barra de Transporte y Controles de Reproducción
1. **`[2.1] Barra de Desplazamiento Relativa:`** Línea temporal acotada a la duración del efecto ($0 \dots T_{\text{dur}}$), sincronizada por fotograma (`requestAnimationFrame`).
2. **`[2.2] Indicador de Tiempo Relativo:`** Posición actual y duración del efecto en formato `MM:SS`.
3. **`[2.3] Control de Volumen:`** Botón de silencio y control deslizante de ganancia.
4. **`[2.4] Cuadro Anterior (-1 Frame):`** Retrocede un fotograma.
5. **`[2.5] Salto Atrás (-10s):`** Retrocede 10 segundos dentro del rango del efecto.
6. **`[2.6] Play / Pausa`**
7. **`[2.7] Salto Adelante (+10s):`** Avanza 10 segundos dentro del rango del efecto.
8. **`[2.8] Cuadro Siguiente (+1 Frame):`** Avanza un fotograma.
9. **`[2.9] Menú de Ajustes:`** Bucle continuo y velocidad de reproducción ($0.25\times, 0.5\times, 1.0\times, 1.5\times, 2.0\times$).
10. **`[2.10] Pantalla Completa`**
11. **`[2.11] Fondo Gris Neutro:`** Al reproducir pistas de audio sin video, el área de visualización usa un fondo neutro (`#2a2a2a`) para que el texto se lea bien.
12. **`[2.12] Mapa Térmico de Rendimiento (Thermal Heatmap):`**
    * Traza el costo de renderizado fotograma a fotograma de las líneas del efecto con una curva spline, coloreada según el presupuesto temporal ($\text{Budget}_{\text{ms}} = 1000 / \text{FPS}$): cian (carga baja), verde (moderada), naranja (cercana al límite) y rojo (presupuesto superado, $>100\%$).
    * Al pasar el cursor sobre la barra de búsqueda, la curva se expande y muestra la cuadrícula de referencia, la latencia (`MM:SS.mmm · X.X ms`) y el acceso directo **`TELEMETRY ↗`**.

### 2.4. Zoom y Desplazamiento en el Visor
1. **Rueda del ratón:** Acerca o aleja tomando el cursor como punto focal, de $1.0\times$ a $8.0\times$.
2. **Botón central:** Arrastrar con el botón central desplaza el área ampliada.
3. **Tecla `R`:** Sobre el reproductor, devuelve el zoom a $1.0\times$ y centra el encuadre.

### 2.5. Conexión con el Panel `Telemetry`
Al abrir el panel de **`Telemetry`** desde el mapa térmico:
1. **Transferencia del visor:** El reproductor activo pasa al panel de diagnóstico con el mismo fotograma, zoom y estado de reproducción. Al cerrar el panel, vuelve al lienzo.
2. **Sincronización:** Mover el cursor sobre los gráficos o hacer clic en un evento crítico lleva el reproductor a ese fotograma.

### 2.6. Consejos
* Conecta `Preview` para validar sincronía y estética antes de escribir en Aegisub.
* Las crestas del mapa térmico suelen indicar un exceso de desenfoque (`\blur`) o máscaras de recorte complejas (`\clip`).

---

## 3. Nodo `System/Script Code` (Código Python y Lua Embebido)

Ejecuta código Python 3.12 o Lua 5.1/LuaJIT dentro del grafo, con acceso a las variables del contexto ASS y a funciones auxiliares de tags.

![System/Script Code](img/script_code.jpg)

### 3.1. Modos de Cabecera
1. **`[1.1] Language` (`language`):** Motor de ejecución:
   * `Python`: Python 3.12 nativo con los módulos estándar `math`, `random` y `re`.
   * `Lua`: Lua estándar mediante Lupa/LuaJIT, compatible con la sintaxis tradicional de macros de Aegisub.

### 3.2. Puertos
1. **`Loop In`:** Entrada de flujo de ejecución.
2. **`In1`, `In2`, $\dots$, `InN`:** Entradas de datos dinámicas, disponibles en el script como `in1`, `in2`, etc.
3. **`[2.1] Loop Out`:** Pasa el flujo a los nodos siguientes.
4. **`[2.2] Result`:** Emite el valor asignado a `result` (texto, tags ASS o trazados vectoriales).

### 3.3. Propiedades del Cuerpo
1. **`script`:** Código a ejecutar (defecto: `result = 'Hello Pyxis ' + str(in1 if in1 else syl.text)`).
2. **`inputs_count`:** Cantidad de entradas dinámicas (defecto: `2`).

### 3.4. Variables y Funciones Disponibles

Tanto en Python como en Lua, el script tiene acceso a:

| Variable / Objeto | Descripción | Atributos Principales |
| :--- | :--- | :--- |
| `syl` | Sílaba activa del contexto | `x, y, center, middle, left, right, top, bottom, start_time, end_time, dur, text, text_stripped, i, n, prev, next, is_first, is_last, has_prev, has_next, ink` |
| `char` | Carácter activo del contexto | `x, y, center, middle, left, top, start_time, end_time, dur, text, i, n, prev, next, is_first, is_last, has_prev, has_next, ink` |
| `word` | Palabra activa del contexto | `x, y, center, start_time, end_time, dur, text, i, n, prev, next, is_first, is_last, has_prev, has_next, ink` |
| `line` / `l` | Línea de diálogo completa | `text, raw_text, style, layer, start_time, end_time, duration, margin_l, margin_r, margin_v, actor, effect, ink` |
| `prev` / `next` | Unidad vecina anterior y posterior | Métricas y texto de la unidad adyacente (`prev.text`, `prev.dur`, `prev.x`, `next.x`) |
| `is_first` / `is_last` | Banderas de límite | `True` si la unidad es la primera / última de la secuencia |
| `has_prev` / `has_next`| Banderas de vecino | `True` si existe una unidad adyacente anterior / posterior |
| `ink` | Métricas de tinta real | `ink.width`, `ink.height`, `ink.center`, `ink.middle`, `ink.left`, `ink.right`, `ink.top`, `ink.bottom` |
| `fx` | Estructura cinemática | `pos_x, pos_y, org_x, org_y, start_time, end_time, dur, align, i, n` |
| `in1`, `in2`, $\dots$ | Entradas conectadas | Valores recibidos en los puertos `In1`, `In2`, etc. |
| `outputs` / `out` | Salidas múltiples | Asignación por nombre (`outputs["Custom"] = val`) o índice (`out2 = val`). |
| `result` | Salida principal | Contenido emitido por el puerto `Result`. |

#### Funciones auxiliares
* **Constructores ASS:** `pos(x,y)`, `move(x1,y1,x2,y2[,t1,t2])`, `org(x,y)`, `fad(in,out)`, `fade(...)`, `clip(shp)`, `iclip(shp)`, `c1(col)`, `c2(col)`, `c3(col)`, `c4(col)`, `alpha(a)`, `trans(tags)`, `fscx(v)`, `fscy(v)`, `frz(v)`, `blur(v)`, `bord(v)`, `shad(v)`.
* **Interpolación y matemáticas:** `clamp(v,min,max)`, `lerp(a,b,t)`, `map_range(v,in_min,in_max,out_min,out_max)`, `ease_in(t)`, `ease_out(t)`, `ease_in_out(t)`, `cubic_in(t)`, `cubic_out(t)`, `elastic(t)`, `bounce(t)`, `back(t)`.
* **Ondas periódicas:** `sine_wave(t,freq,amp,offset)`, `square_wave(...)`, `triangle_wave(...)`, `sawtooth_wave(...)`.
* **Tiempo y texto:** `time_to_frame(ms,fps)`, `duration(obj)`, `parse_ass_time(str)`, `format_ass_time(ms)`, `strip_tags(txt)`.

---

## 4. Nodo `System/Benchmark Math` (Diagnóstico de Rendimiento)

Ejecuta una carga matemática intensiva (trigonometría, criba de primos o multiplicación de matrices) y devuelve el tiempo transcurrido en milisegundos.

![System/Benchmark Math](img/benchmark_math.jpg)

### 4.1. Puertos de Entrada
1. **`Iterations`:** Cantidad de iteraciones (defecto: `10000`). Si no está conectado, usa la propiedad interna.

### 4.2. Propiedades del Cuerpo
1. **`[2.1] Complexity` (`complexity`):** Algoritmo de prueba:
   * `Heavy Math (Trig + Sqrt)`: Bucles de funciones trigonométricas ($\sin, \cos$) combinadas con raíces cuadradas ($\sqrt{x}$).
   * `Prime Sieve`: Comprobación y criba de números primos.
   * `Matrix Mult`: Multiplicación de matrices $25 \times 25$ en memoria.
2. **`[2.2] Iterations` (`iterations`):** Número de repeticiones (defecto: `10000`).

### 4.3. Puertos de Salida
1. **`[1.1] Out`:** Cadena con el dato de entrada recibido, o el resumen del tiempo transcurrido con formato `[Bench: X.XXms]`.
2. **`[1.2] Time ms`:** Tiempo total de cálculo en milisegundos, medido con `time.perf_counter()`.

### 4.4. Consejos
* Intercala `Benchmark Math` en grafos grandes para comparar los tiempos de ejecución antes y después de optimizaciones como la memorización con `Basics/Once`.

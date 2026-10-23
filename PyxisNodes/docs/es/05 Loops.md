# Loops

La categoría **Loops** contiene los nodos que deciden cómo se divide cada línea de diálogo en unidades (`syl`, `char`, `word`, `line`), ejecutan sub-bucles temporales o fotograma a fotograma (FBF) y calculan factores de progreso normalizados.

---

## 1. Nodo `Loops/Main Loop`

Divide cada línea de diálogo seleccionada de Aegisub en sílabas, caracteres, palabras o la línea completa. Inicia el grafo, emite la señal de flujo y proporciona los contadores de iteración.

![Loops/Main Loop](img/main_loop.jpg)

### 1.1. Modos de Cabecera (*Header Badges*)
1. **Selector de Dominio (`iterator`):** Se cambia con un clic en el badge superior derecho o desde las propiedades:
   * `syl`: Itera sílaba a sílaba, siguiendo las marcas de tiempo de karaoke (`\k`, `\kf`, `\ko`, `\K`).
   * `char`: Itera glifo a glifo, calculando métricas tipográficas para cada carácter.
   * `word`: Itera palabra por palabra, delimitadas por espacios en blanco.
   * `line`: Itera una sola vez para la línea de diálogo completa.
2. **Tratamiento de Espacios (`blank_mode` / `noblank`):** Se cambia con el badge adyacente:
   * `no_blank` (*NO BLANK / Ignorar Espacios*): Omite espacios, tabulaciones y saltos de línea. Los contadores reflejan solo los elementos visibles ($ci$ y $cn$).
   * `with_blanks` (*WITH BLANK / Todos*): Procesa todos los caracteres y asigna índices e intervalos de tiempo también a los espacios ($i$ y $n$).

### 1.2. Puertos de Salida
1. **`[1.1] Loop`:** Señal de flujo que activa los nodos downstream una vez por cada unidad del dominio activo.
2. **`[1.2] Iterator (i)`:** Índice ordinal (base 1) de la unidad actual dentro de la línea ($1 \dots N$). Inyectado en el contexto como `i`, `syl.i`, `char.i` o `word.i`.
3. **`[1.3] Total (N)`:** Cantidad de unidades del dominio activo en la línea. Inyectado como `N`, `syl.n`, `char.n` o `word.n`.

### 1.3. Inyección de Contexto
Para cada línea de diálogo, el nodo construye estos datos de la unidad activa:
* **Indexación:**
  * En modo `no_blank`: $i \leftarrow ci$, $N \leftarrow cn$, de modo que los índices no tienen saltos causados por espacios.
  * En modo `with_blanks`: $i \leftarrow i_{\text{abs}}$, $N \leftarrow n_{\text{abs}}$, conservando el orden absoluto de la línea original.
* **Métricas espaciales** (coordenadas de la unidad en píxeles):
  `center`, `middle`, `left`, `right`, `top`, `bottom`, `width`, `height`, `x`, `y`.
* **Intervalo temporal:**
  Límites $[t_{\text{start}}, t_{\text{end}}]$ y duración $t_{\text{dur}} = t_{\text{end}} - t_{\text{start}}$ de la sílaba o carácter.
* **Variables globales:**
  `i`, `n`, `fx_i`, `fx_n`, junto con el objeto de la unidad actual (`syl`, `char`, `word` o `line`).

### 1.4. Ejemplo
* **Desplazamiento Parabólico Escalonado por Sílaba:**
  Conecte `Loop` al puerto `Loop / Domain` de `System/Output` con `iterator: syl`:
  
  ```
  [Main Loop: syl] ──► Loop ──► [System/Output]
                   ──► Iterator (i)
                   ──► Total (N)
  ```
  
  En un nodo de tags conectado a `Output (Tags)`:
  ```
  {\pos(syl.center, syl.middle - 25 * math.sin(math.pi * (syl.i - 1) / max(1, syl.n - 1)))\k(syl.dur / 10)}
  ```
  
  Para una línea con $N = 5$ sílabas, la tercera sílaba ($i = 3$) alcanza la elevación máxima:
  $$\Delta y = -25 \cdot \sin\left(\pi \cdot \frac{2}{4}\right) = -25 \text{ px}$$

---

## 2. Nodo `Loops/MaxLoop`

Repite el flujo entrante $N$ veces para la unidad actual, como copias concurrentes (`normal`), o divide su intervalo de tiempo en fotogramas regulares de vídeo (`fbf`).

![Loops/MaxLoop](img/maxloop.jpg)

### 2.1. Modos de Cabecera
El modo se selecciona con el botón de la cabecera:
1. **`normal` (*NORMAL*):**
   * Evalúa el sub-grafo downstream $N$ veces.
   * Mantiene los tiempos de inicio y fin originales del elemento base (`start_time`, `end_time`).
   * Puertos de entrada activos: `Loop In`.
   * Propiedades visibles: `iterations` (defecto: `"3"`), `var_name` (defecto: `"j"`).
2. **`fbf` (*Frame by Frame*):**
   * Divide el intervalo $[Start, End]$ en fotogramas uniformes de paso `step_ms`.
   * Puertos de entrada activos: `Loop In`, `Start`, `End`.
   * Propiedades visibles: `step_ms` (defecto: `"41.7"` $\approx 23.976\text{ fps}$), `start_time` (defecto: `"start_time"`), `end_time` (defecto: `"end_time"`), `var_name` (defecto: `"j"`).

### 2.2. Puertos de Entrada
1. **`Loop In`:** Señal de flujo proveniente de `Main Loop` o de otro sub-bucle previo.
2. **`Start` (Modo `fbf`):** Marca de tiempo inicial en milisegundos. Si no está conectado, usa la propiedad `start_time` o el valor `start_time` del contexto.
3. **`End` (Modo `fbf`):** Marca de tiempo final en milisegundos. Si no está conectado, usa la propiedad `end_time` o el valor `end_time` del contexto.

### 2.3. Controles y Propiedades del Cuerpo
1. **`[2.1] Iterations (N)` (`iterations`):** Cantidad de repeticiones en modo `normal`. Admite expresiones.
2. **`[2.2] Step (ms)` (`step_ms`):** Duración de cada fotograma en modo `fbf` (mínimo: $1.0\text{ ms}$).
3. **`[2.3] Inicio (ms)` (`start_time`):** Expresión del tiempo inicial por defecto en modo `fbf`.
4. **`[2.4] Fin (ms)` (`end_time`):** Expresión del tiempo final por defecto en modo `fbf`.
5. **`[2.5] Var Name` (`var_name`):** Nombre de la variable de iteración inyectada en el contexto local (defecto: `"j"`).

### 2.4. Puertos de Salida
1. **`[1.1] Loop Out`:** Señal de flujo enviada a los nodos downstream.
2. **`[1.2] Counter`:** Índice ordinal de la sub-iteración activa ($1 \dots N$).
3. **`[1.3] Total`:** Cantidad total de iteraciones ($N$).

### 2.5. Modelo Matemático
* **Modo Normal:**
  Se ejecuta para cada $j \in [1, N]$. Cada ejecución conserva el intervalo $[t_{\text{start}}, t_{\text{end}}]$ del elemento y define:
  $$\text{var\_name} = j, \quad \text{var\_name\_max} = N, \quad \text{fx\_i} = j, \quad \text{fx\_n} = N$$
* **Modo FBF (Cuadro a Cuadro):**
  A partir de $Start$, $End$ y $\Delta t = step\_ms$, el total de fotogramas es:
  $$N = \left\lceil \frac{End - Start}{\Delta t} \right\rceil$$
  Para cada cuadro $k \in [1, N]$:
  $$t_{\text{start}}^{(k)} = Start + (k - 1) \cdot \Delta t$$
  $$t_{\text{end}}^{(k)} = \min(End, Start + k \cdot \Delta t)$$
  $$t_{\text{dur}}^{(k)} = t_{\text{end}}^{(k)} - t_{\text{start}}^{(k)}$$
  El contexto local recibe las variables de tiempo `st`, `et`, `start_time`, `end_time`, `frame_start_time`, `frame_end_time`, `frame_dur`, `fd`, `fx_start_time`, `fx_end_time`, `fx_dur` y se activa la bandera `in_fbf_loop = True`.

### 2.6. Ejemplos
* **Ejemplo 1 (Modo Normal): Sombras por Capas:**
  Configuración: `mode: normal`, `iterations: 4`, `var_name: j`.
  Genera 4 capas desplazadas con opacidad cada vez menor:
  ```
  {\pos(syl.center + j * 1.5, syl.middle + j * 1.5)\1c&H000000&\1a&H80&\3a&HFF&}
  ```
  Para $j = 1$ el desplazamiento es $(1.5, 1.5)$; para $j = 4$ es $(6.0, 6.0)$, lo que produce una sombra direccional densa.

* **Ejemplo 2 (Modo FBF): Coordenadas por Fotograma sin `\t`:**
  Configuración: `mode: fbf`, `step_ms: 41.7`, `var_name: j`.
  Cada línea emitida cubre un fotograma de vídeo con sus propias coordenadas:
  ```
  {\pos(syl.center + j * 4, syl.middle)\alpha&H00&}
  ```

---

## 3. Nodo `Loops/Module`

Calcula un factor de progreso normalizado en $[0.0, 1.0]$, o un desplazamiento modular, a partir de los contadores de iteración ($i, j$).

![Loops/Module](img/module.jpg)

### 3.1. Puertos de Entrada
1. **`Iterator (i)`:** Índice actual de la iteración. Si no está conectado, usa la propiedad `iter`.
2. **`Total (N)`:** Cantidad total de elementos. Si no está conectado, usa la propiedad `total`.
3. **`Sub-step (m)`:** Desplazamiento o compensación fraccionaria. Si no está conectado, usa la propiedad `sub_m`.

### 3.2. Controles y Propiedades del Cuerpo
1. **`[2.1] Iterator (i)` (`iter`):** Expresión o identificador del índice (defecto: `"i"`).
2. **`[2.2] Total (N)` (`total`):** Expresión o identificador del total (defecto: `"N"`).
3. **`[2.3] Sub-step (m)` (`sub_m`):** Expresión del desplazamiento (defecto: `"0"`).

### 3.3. Puertos de Salida
1. **`[1.1] Data`:** Valor numérico del progreso.

### 3.4. Formulación
El nodo evalúa $i$, $N$ y $m$ en el contexto activo y aplica:

$$\text{Denominador} = N + m - 1.0$$

$$\text{Data} = \begin{cases} \dfrac{i - 1.0 + m}{\text{Denominador}} & \text{si } \text{Denominador} \neq 0 \text{ y } N > 1.0 \\ m & \text{en cualquier otro caso} \end{cases}$$

#### Formato de Salida:
1. El resultado se redondea a 4 decimales: $R = \text{round}(\text{Data}, 4)$.
2. Si $R$ es un entero exacto, se escribe sin punto decimal (ej. `0` o `1`).
3. Si tiene parte fraccionaria, se escribe con un máximo de 4 decimales, sin ceros finales (ej. `0.25`, `0.3333`).

#### Comportamiento con $m = 0$:
Para $i = 1 \dots N$ con $N > 1$:
* Primer elemento ($i = 1$): $\text{Data} = \frac{0}{N - 1} = 0$
* Último elemento ($i = N$): $\text{Data} = \frac{N - 1}{N - 1} = 1$
* El valor emitido divide $[0.0, 1.0]$ en $N - 1$ segmentos iguales.

### 3.5. Ejemplo
* **Modulación de Escala con Curvas Easing:**
  Conecte `Data` a una fórmula cuadrática o al nodo `Basics/Math (Category: easing)` para convertir el orden de los caracteres en una escala no lineal:
  
  ```
  [Main Loop: char] ──► Iterator (i) ──► [Module] ──► Data ──► [Tags]
                    ──► Total (N)    ──►
  ```
  
  Conectando `Data` a la propiedad `Tags`:
  ```
  {\fscx(100 + Data * 50)\fscy(100 + Data * 50)}
  ```
  El primer carácter ($Data = 0.0$) tiene `\fscx100\fscy100`. Con $N = 5$, el carácter central ($Data = 0.5$) tiene `\fscx125\fscy125`, y el último ($Data = 1.0$), `\fscx150\fscy150`.

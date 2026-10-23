# Basics

La categoría **Basics** reúne los nodos para generar, transformar, formatear y enrutar datos primitivos (números, cadenas, colores, expresiones matemáticas y condicionales) al construir efectos en subtítulos ASS.

---

## 1. Nodo `Basics/Number` (Constante Numérica y Expresiones)

Emite un número. El valor puede ser una constante, una variable del contexto ASS o una expresión algebraica, y se evalúa en cada iteración.

![Basics/Number](img/number.jpg)

**Salida**
1. **`[1.1] Number`:** El resultado como cadena de texto. Los enteros exactos se emiten sin decimales (ej. `10`). Si hay decimales, se redondea a un máximo de 4 y se eliminan los ceros finales (ej. `12.5`).

**Propiedades**
1. **`[2.1] Value` (`value`):** Acepta números directos (`100`, `-45.2`), variables del contexto ASS (`syl.x`, `line.width`, `j`, `i`, `char.n`) y expresiones (`syl.width / 2 + 10`, `sin(j * 0.1) * 50`).

Los identificadores registrados en el contexto (`syl`, `line`, `char`, `video_fps`, etc.) se sustituyen por sus valores numéricos antes de calcular. Se aceptan tanto el punto decimal (`12.5`) como la coma decimal (`12,5`).

**Consejos**
* Conecta `Number` a los puertos de `Basics/MultiTag` o a las plantillas de `Basics/Dynamic Format` para controlar etiquetas numéricas como `\fscx<val>`, `\fscy<val>`, `\blur<val>` o una posición como `\pos(syl.center, <val>)`.
* Los puertos de tiempo (`Start Time`, `End Time`) aceptan expresiones relativas al contexto, como `syl.start_time - 150` o `line.duration + 200`.

---

## 2. Nodo `Basics/String` (Cadena de Texto Literal)

Emite una cadena de texto fija, que puede incluir macros de contexto. Sirve para texto de diálogo, nombres de estilo, comandos de dibujo o secuencias de escape ASS.

![Basics/String](img/string.jpg)

**Salida**
1. **`[1.1] String`:** El texto configurado en el cuerpo del nodo.

**Propiedades**
1. **`[2.1] Text` (`value`):** Admite texto plano, secuencias de escape ASS de salto y espacio (`\N`, `\h`), bloques de etiquetas (`{\an5\bord0\shad0}`) y trazados vectoriales (`m 0 0 l 100 0 100 100 0 100`). Dentro de los bloques `{\...}`, el evaluador de cadenas de Pyxis resuelve expresiones y variables de contexto entre los paréntesis de cada tag (ej. `{\pos(syl.center, syl.middle)}` o `\fscx(100 + 20 * i)`) y deja intacto el texto literal que los rodea.

**Consejos**
* Conecta `String` a `Basics/Concatenate` o `Output (Tags)` para anteponer una cabecera fija como `{\an5\bord1\blur1.5}`.
* Guarda el código vectorial en un único nodo `String` conectado a la entrada `Draw Code` de `Shape/Slicer` o `Shape/Transform`, para no duplicar trazados largos en el grafo.

---

## 3. Nodo `Basics/Text` (Manipulación y Procesamiento de Cadenas)

Aplica operaciones de texto a una cadena cualquiera o a la unidad activa del contexto: eliminar etiquetas, cambiar mayúsculas, buscar y reemplazar, transliterar japonés y dividir en sílabas.

![Basics/Text](img/text.jpg)

**Entrada**
1. **`Text`:** La cadena a procesar. Si está desconectado, el nodo toma el texto de la unidad activa del contexto, con este orden de prioridad: `active_unit.text_stripped` $\to$ `syl.text` $\to$ `char.text` $\to$ `line.text`.

**Salida**
1. **`[1.1] Out`:** El resultado de la operación seleccionada.

### Operaciones (`operation`)

| Operación (`operation`) | Descripción | Comportamiento y Parámetros Auxiliares |
| :--- | :--- | :--- |
| `strip_tags` | Eliminar etiquetas ASS | Quita todos los bloques `{\...}`, convierte `\N`, `\n` y `\h` en espacios normales y recorta los espacios de los extremos. |
| `uppercase` | Mayúsculas | Pasa toda la cadena a mayúsculas (`str.upper()`). |
| `lowercase` | Minúsculas | Pasa toda la cadena a minúsculas (`str.lower()`). |
| `clean_spaces` | Colapsar espacios | Sustituye las secuencias de espacios y tabulaciones por un único espacio (`[ \t]+` $\to$ `" "`). |
| `replace` | Reemplazar subcadena | Sustituye todas las apariciones de `Search` por `Replace With`. |
| `substring` | Extraer | Extrae `Length` caracteres a partir del índice `Start` (base 0). |
| `length` | Longitud | Devuelve el número de caracteres como texto. |
| `contains` | Comprobar subcadena | Emite `"1"` si la cadena contiene `Search`, y `"0"` si no. |
| `kana` | Transliteración japonesa | Convierte entre Romaji, Hiragana y Katakana mediante una tabla de equivalencias. Resuelve dígrafos y consonantes geminadas con sokuon (`っ` / `ッ`). |
| `romaji_to_karaoke` | Segmentación silábica automática | Divide las palabras en Romaji en sílabas y genera marcas de karaoke temporizadas (`\k<dur>`, `\kf<dur>`, `\ko<dur>`), repartiendo la duración de la línea a partes iguales entre las sílabas. |

#### `kana`
Los patrones fonéticos se buscan de mayor a menor longitud, de modo que los trígrafos y dígrafos (`kya`, `tsu`, `chi`, `sha`) tienen prioridad sobre las vocales o consonantes sueltas (`ka`, `ta`, `sa`, `a`). Las opciones de `Mode` son:
* `Romaji to Hiragana`: ej. `"sakura"` $\to$ `"さくら"`, `"gakkou"` $\to$ `"がっこう"`.
* `Romaji to Katakana`: ej. `"karaoke"` $\to$ `"カラオケ"`.
* `Hiragana to Katakana`
* `Katakana to Hiragana`
* `Kana to Romaji`: convierte Hiragana o Katakana a Romaji estándar.

#### `romaji_to_karaoke`
Divide la entrada en palabras y después en las sílabas del japonés romanizado. Para una línea de duración total $T$ en centisegundos y $N$ sílabas detectadas:
$$\text{Duración por sílaba } d_i = \left\lfloor \frac{T}{N} \right\rfloor + (1 \text{ si } i < (T \bmod N))$$

Antes de cada sílaba se inserta la etiqueta configurada en `K Mode` (`\k`, `\kf`, `\ko`, `\K`) con su duración en centisegundos (ej. `{\k15}sa{\k20}ku{\k15}ra`).

**Consejos**
* Aplica `strip_tags` antes de la entrada `Text` de `Basics/Text to Shape`, para que el motor vectorial reciba solo glifos y ningún código de control ASS.
* Conecta `contains` a `Basics/Only` para elegir una ruta de estilo según palabras clave del diálogo.

---

## 4. Nodo `Basics/Color Picker` (Selector de Color y Paletas)

Selector de color y gestor de paletas que convierte entre ASS BGR (`&HBBGGRR&`) y hexadecimal web (`#RRGGBB`).

![Basics/Color Picker](img/color_picker.jpg)

**Salidas**
1. **`[1.1] Color List`:** Todos los colores de la paleta activa como una cadena separada por comas, cada uno en el formato de salida de su muestra (ej. `"&H5500FF&, &HFF9900&, #FFFFFF"`).
2. **`[1.2] ASS Color`:** La primera muestra (Slot 0) en sintaxis ASS BGR `&HBBGGRR&`.

**Controles**
* Al pulsar una muestra (*swatch*) se abre el selector, con controles deslizantes, vista previa en tiempo real y selector de formato de salida.
* Se pueden añadir muestras y definir para cada una si exporta en formato `ASS` o `HEX`.

### Conversión de color
Pyxis convierte entre el orden de canales RGB habitual y el orden BGR que usan Aegisub y libass:

$$\text{RGB: } (R, G, B) \implies \text{ASS Color: } \&\text{H}B_{\text{hex}}G_{\text{hex}}R_{\text{hex}}\&$$

* **`ASS`:** intercambia los canales rojo y azul para ajustarse a libass. Por ejemplo:
  * Rojo puro ($R=255, G=0, B=0$) $\implies$ `&H0000FF&`
  * Azul puro ($R=0, G=0, B=255$) $\implies$ `&HFF0000&`
  * Amarillo puro ($R=255, G=255, B=0$) $\implies$ `&H00FFFF&`
* **`HEX`:** conserva el formato web `#RRGGBB`, para usarlo con herramientas externas.

**Consejos**
* Conecta `ASS Color` a las entradas de color primario (`\1c`) o de borde (`\3c`) de `Basics/MultiTag`.
* Conecta `Color List` al puerto del mismo nombre de `Functions/Color Gradient` o `Shape/Concentric Borders` para hacer transiciones de varios colores.

---

## 5. Nodo `Basics/Math` (Motor Matemático y Curvas)

Evalúa aritmética, trigonometría, curvas de easing, ondas periódicas y utilidades de rango, agrupadas en 8 familias.

![Basics/Math](img/math.jpg)

**Selectores de cabecera**
1. **`[2.1] Category` (`category`):** La familia:
   * `basic`: aritmética elemental.
   * `trig`: trigonometría directa e inversa, y conversiones angulares.
   * `rounding`: redondeo al entero más próximo, suelo y techo.
   * `clamping`: acotación de rangos y comparaciones.
   * `easing`: curvas de aceleración y desaceleración normalizadas ($t \in [0.0, 1.0]$).
   * `waves`: osciladores de onda periódica.
   * `random`: números pseudoaleatorios con semilla determinista opcional.
   * `utilities`: mapeo lineal de rangos e interpolación.
2. **`[2.2] Operation` (`operation`):** La función a ejecutar dentro de la familia seleccionada.

**Entradas**
1. **`A`:** Operando principal, factor de progreso $t$, ángulo o valor base. Si está desconectado, toma el valor configurado en la propiedad interna del nodo.
2. **`B`:** Segundo operando, límite superior, frecuencia o valor objetivo.

**Salida**
1. **`[1.1] Out`:** El resultado escalar. Los enteros exactos se emiten sin decimales (ej. `25`); los fraccionarios, con un máximo de 4 decimales (ej. `0.7071`).

### `basic` (aritmética)
* **`add` ($A + B$):** Suma.
* **`sub` ($A - B$):** Resta.
* **`mul` ($A \cdot B$):** Multiplicación.
* **`div` ($A / B$):** División. Devuelve `0.0` si $B = 0$.
* **`mod` ($A \pmod B$):** Resto. Devuelve `0.0` si $B = 0$.
* **`pow` ($A^B$):** Potencia.
* **`abs` ($|A|$):** Valor absoluto.
* **`neg` ($-A$):** Cambio de signo.

### `trig` (trigonometría)
Las funciones directas (`sin`, `cos`, `tan`) esperan el ángulo $A$ en **grados** ($0^\circ \dots 360^\circ$), la misma unidad que las etiquetas de rotación de ASS (`\frz`, `\frx`, `\fry`). Las funciones inversas devuelven grados.

* **`sin`:** $\sin\left(\frac{A \cdot \pi}{180}\right)$
* **`cos`:** $\cos\left(\frac{A \cdot \pi}{180}\right)$
* **`tan`:** $\tan\left(\frac{A \cdot \pi}{180}\right)$
* **`asin` / `arcsin`:** $\arcsin(\text{clamp}(A, -1, 1)) \cdot \frac{180}{\pi} \in [-90^\circ, 90^\circ]$
* **`acos` / `arccos`:** $\arccos(\text{clamp}(A, -1, 1)) \cdot \frac{180}{\pi} \in [0^\circ, 180^\circ]$
* **`atan` / `arctan`:** $\arctan(A) \cdot \frac{180}{\pi} \in (-90^\circ, 90^\circ)$
* **`atan2`:** $\text{atan2}(Y, X) \cdot \frac{180}{\pi}$ con $Y = A$ y $X = B$, en el rango $[-180^\circ, 180^\circ]$
* **`rad` / `radians`:** Grados a radianes: $A \cdot \frac{\pi}{180}$.
* **`deg` / `degrees`:** Radianes a grados: $A \cdot \frac{180}{\pi}$.

### `rounding`
* **`round`:** Redondea $A$ al entero más próximo.
* **`floor`:** Mayor entero menor o igual que $A$ ($\lfloor A \rfloor$).
* **`ceil`:** Menor entero mayor o igual que $A$ ($\lceil A \rceil$).

### `easing` (curvas de progresión)
Recibe un factor de progreso $t = \text{clamp}(A, 0.0, 1.0)$ y devuelve el valor transformado en $[0.0, 1.0]$:

* **`ease_in`:** Aceleración cuadrática: $f(t) = t^2$.
* **`ease_out`:** Desaceleración cuadrática: $f(t) = 1 - (1 - t)^2$.
* **`ease_in_out`:** Aceleración y después desaceleración:
  $$f(t) = \begin{cases} 2t^2 & \text{si } t < 0.5 \\ 1 - \frac{(-2t + 2)^2}{2} & \text{si } t \ge 0.5 \end{cases}$$
* **`cubic_in`:** Aceleración cúbica: $f(t) = t^3$.
* **`cubic_out`:** Desaceleración cúbica: $f(t) = 1 - (1 - t)^3$.
* **`expo`:** Exponencial: $f(t) = 2^{10(t - 1)}$ para $t > 0$.
* **`elastic`:** Oscilación elástica amortiguada.
* **`bounce`:** Rebote en 4 tramos.
* **`back`:** Sobreimpulso: $f(t) = (c_1 + 1)t^3 - c_1 t^2$ con $c_1 = 1.70158$.

### `waves` (osciladores periódicos)
Oscilaciones a partir de $t = A$, frecuencia $f = \text{freq}$, amplitud $A_{\text{amp}} = \text{amp}$ y desplazamiento constante $\text{Offset}$:

* **`sine`:** $y(t) = A_{\text{amp}} \cdot \sin(2\pi \cdot f \cdot t) + \text{Offset}$
* **`square`:** Emite $+A_{\text{amp}} + \text{Offset}$ durante el semiciclo positivo y $-A_{\text{amp}} + \text{Offset}$ durante el negativo.
* **`triangle`:** Para $\phi = (t \cdot f) \pmod 1$, $y(t) = A_{\text{amp}} \cdot (2|2\phi - 1| - 1) + \text{Offset}$.
* **`sawtooth`:** Rampa ascendente que cae de golpe: para $\phi = (t \cdot f) \pmod 1$, $y(t) = A_{\text{amp}} \cdot (2\phi - 1) + \text{Offset}$.

### `utilities`, `clamping` y `random`
* **`clamp`:** Limita $A$ al intervalo $[\text{Min}, \text{Max}]$.
* **`lerp`:** Interpolación lineal entre $A$ y $B$ para $t \in [0.0, 1.0]$: $\text{lerp}(A, B, t) = A + (B - A) \cdot t$.
* **`map_range`:** Reasigna $A$ de forma proporcional desde $[\text{MinIn}, \text{MaxIn}]$ hacia $[\text{MinOut}, \text{MaxOut}]$.
* **`min` / `max`:** El menor o el mayor de $A$ y $B$.
* **`random`:** Número pseudoaleatorio uniforme en $[\text{Min}, \text{Max}]$ con semilla opcional (`Seed`).

**Consejos**
* Conecta una salida `waves/sine` a un campo `\frz` en `Basics/Dynamic Format` para obtener un balanceo (ej. `\frz(%s)` con amplitud de $10^\circ$).
* Conecta el puerto `Out` de una curva `easing/ease_out` a los puertos `\fscx` y `\fscy` de `Basics/MultiTag` para animar una entrada suave de 0% a 100%.

---

## 6. Nodo `Basics/MultiRandom` (Generador Aleatorio Determinista)

Genera valores pseudoaleatorios o listas deterministas, para dispersión espacial, fluctuaciones de tags y secuencias aleatorias. Tiene 15 modos.

![Basics/MultiRandom](img/multirandom.jpg)

**Entradas**
1. **`Min`:** Límite inferior del rango, color inicial o lista de opciones.
2. **`Max`:** Límite superior del rango o color final.
3. **`Step`:** Paso de cuantización entre los valores generados.
4. **`Total (N)`:** Cantidad de valores que emite la salida `Batch / List`.
5. **`Iterator`:** Variable de ámbito que controla la memorización (ej. `s_i`, `j`, `syl`, `char`, `line`). Si está vacío, se calcula un valor nuevo en cada llamada.

**Salidas**
1. **`[1.1] Data`:** Un único valor aleatorio para la iteración actual.
2. **`[1.2] Batch / List`:** Una lista de $N$ valores aleatorios separados por comas (`v1, v2, v3, ...`), para listas de parámetros o matrices de partículas.

### Valores por iterador en expresiones (`by.<iterador>.<R_modo>`)
Para obtener un valor aleatorio que se mantiene fijo por iterador dentro de expresiones ASS o scripts Python:
* **En expresiones ASS:**
  ```text
  \frz(by.syl.Rs(15))
  \fscx(100 + by.char.R(0, 30))
  ```
* **En scripts (`Define Vars` / `Script Code`):**
  ```python
  angle = by.s_i.Rms(0.01, 0.02)          # Mismo valor durante el ciclo del trozo de Slicer
  offset = by.j.Rs(10)                    # Mismo valor durante la repetición de MaxLoop
  color = by.syl.Rcolor("#FFFFFF", "#0088FF") # Mismo color para toda la sílaba
  ```
Dentro de un mismo ciclo del iterador indicado, las llamadas repetidas devuelven el mismo valor almacenado. Cuando el iterador avanza, se calcula y guarda un valor nuevo.

### Modos (`mode`)

| Modo (`mode`) | Nombre | Descripción y Rango | Ejemplo de Salida |
| :--- | :--- | :--- | :--- |
| `R` | Uniforme | Número aleatorio entre `Min` y `Max`, cuantizado a múltiplos de `Step`. Si los extremos y el paso son enteros, devuelve enteros. | `42` |
| `Rs` | Simétrico | Valor uniforme con signo aleatorio ($\pm 1$, igual probabilidad): $\text{res} = R(\text{Min}, \text{Max}) \cdot (\pm 1)$. | `-35` o `35` |
| `Rr` | Relativo a la resolución | Escala el valor según el ancho horizontal del script ($R_x$ relativo a $1280\text{ px}$): $\text{res} = R \cdot \frac{R_x}{1280}$. | `68.5` |
| `Rd` | 1 decimal | Flotante uniforme con 1 decimal ($0.1$). | `14.3` |
| `Rc` | 2 decimales | Flotante uniforme con 2 decimales ($0.01$). | `87.25` |
| `Rm` | 3 decimales | Flotante uniforme con 3 decimales ($0.001$). | `3.142` |
| `Rds` | 1 decimal con signo | `Rd` con signo aleatorio ($\pm$). | `-12.4` |
| `Rcs` | 2 decimales con signo | `Rc` con signo aleatorio ($\pm$). | `-45.82` |
| `Rms` | 3 decimales con signo | `Rm` con signo aleatorio ($\pm$). | `+0.915` |
| `Re` | Elección | Elige al azar un elemento de la lista separada por comas en `Options` (ej. `\blur1, \blur3, \blur6`). | `\blur3` |
| `Rfake` | Hash determinista | Generador congruencial que depende solo del contador de iteración ($i$ o $j$): $\text{Hash}(c) = (c \cdot 9301 + 49297) \pmod{233280}$. | `18` |
| `Rcolor` | Color | Color aleatorio interpolado uniformemente entre `Min` y `Max` en espacio RGB, o elegido de una lista si `Min` contiene comas. | `&H7FA412&` |
| `R2d` | Coordenadas 2D | Un par cartesiano independiente en formato `"X,Y"`. | `120.5,-45.2` |
| `Rbool` | Booleano probabilístico | Devuelve `"True"` o `"False"` usando como umbral el porcentaje $P \in [0, 100]$ indicado en `Min`. | `"True"` |
| `Rstep` | Paso cuantizado | Valores restringidos a múltiplos enteros de `Step` (ej. rotaciones en múltiplos de $45^\circ$). | `180` |

**Consejos**
* Conecta una salida `Data` en modo `Rs` con rango $[2, 8]$ a un desplazamiento posicional $\Delta x$ para añadir una vibración leve sin perder legibilidad.
* Usa `Rcolor` con ámbito `by.syl` conectado a la entrada `\1c` de `Basics/MultiTag` para que cada sílaba tenga su propio color y sus caracteres sigan siendo uniformes.

---

## 7. Nodo `Basics/Concatenate` (Concatenador Extensible y Modo Zip)

Une cualquier cantidad de cadenas de texto, etiquetas ASS o comandos vectoriales en una sola cadena, con un separador o entrelazando listas (modo `zip`).

![Basics/Concatenate](img/concatenate.jpg)

**Entradas**
* **`In1`, `In2`, $\dots$, `InN`:** Puertos de entrada. Al conectar un cable o pulsar `(+)` se añaden más.
* Un puerto sin cable usa el valor escrito en su campo de texto inline.

**Salida**
1. **`[1.1] String`:** La cadena unida.

### Separadores (`separator`)

| Separador (`separator`) | Carácter | Uso |
| :--- | :---: | :--- |
| `nil` / `none` / `""` | *(Ninguno)* | Unión directa (ej. fusionar tags en un bloque `\pos(X,Y)\blur2\1c&HFFFFFF&`). |
| `space` / `" "` | Espacio | Separar palabras o coordenadas en instrucciones ASSdraw (`m 0 0 l 10 10`). |
| `comma` / `","` | Coma `,` | Construir listas para nodos de paleta o arrays de valores. |
| `semicolon` / `";"` | Punto y coma `;` | Agrupar parámetros de datos o secuencias de script. |
| `newline` / `"\n"` | Salto de línea | Subtítulos de varias líneas o bloques de texto apilados. |
| `zip` | *(Entrelazado)* | Combinación elemento a elemento de listas de valores. |

### Modo `zip`
Con `separator` en `zip`, cada entrada se trata como una lista separada por comas y las listas se combinan elemento a elemento:

$$\text{In}_1 = [A_1, A_2, A_3], \quad \text{In}_2 = [B_1, B_2, B_3] \implies \text{Out} = [A_1 B_1, \, A_2 B_2, \, A_3 B_3]$$

1. Cada entrada activa se divide en tokens.
2. Si el campo inline de un puerto contiene un prefijo de tag (ej. `\1c`, `\blur`), se antepone a cada token de esa lista.
3. Los tokens se emparejan por posición hasta la longitud de la lista más corta que tenga más de un elemento. La salida es una lista de keyframes fusionados separados por comas.

**Consejos**
* Usa `separator` en `nil` al combinar salidas de `MultiTag` o cadenas literales, para que no se cuelen espacios en el bloque de tags que puedan alterar el renderizado de libass.
* Usa `zip` para emparejar una lista de colores de `Functions/Color Gradient` con una lista de opacidades en transiciones por fotograma.

---

## 8. Nodo `Basics/Dynamic Format` (Formateador Dinámico de Cadenas)

Construye cadenas a partir de una plantilla con especificadores estilo `printf` (`%s`, `%d`, `%f`, `%.2f`, `%04d`, `%x`). Las listas separadas por comas se procesan automáticamente.

![Basics/Dynamic Format](img/dynamic_format.jpg)

**Entradas**
1. **`In1`, `In2`, $\dots$, `InN`:** Valores escalares o listas, que se insertan en orden en los especificadores `%...` de la plantilla.

**Salida**
1. **`[1.1] String`:** La cadena formateada. Si las entradas son listas, las cadenas formateadas se unen con comas.

### Especificadores en `format`

| Especificador | Tipo Esperado | Conversión | Ejemplo con Entrada `42.68` |
| :--- | :--- | :--- | :--- |
| `%s` | Cualquiera | Se inserta como texto. | `"42.68"` |
| `%d` / `%i` | Entero | Se convierte a entero. | `"42"` |
| `%04d` | Entero con relleno | Entero rellenado con ceros hasta 4 dígitos. | `"0042"` |
| `%f` | Flotante | Representación estándar en punto flotante. | `"42.680000"` |
| `%.2f` | Flotante, 2 decimales | Exactamente 2 decimales. | `"42.68"` |
| `%x` / `%X` | Hexadecimal | Entero en base 16, en minúsculas o mayúsculas. | `"2a"` / `"2A"` |

### Listas
Si alguna entrada recibe una lista separada por comas (ej. `In1 = "10, 20, 30"`, `In2 = "0.5, 1.0, 1.5"`), la plantilla se repite para cada par de elementos:

$$\text{Plantilla: } \texttt{\\blur\%s\\bord\%s} \implies \texttt{"\\blur10\\bord0.5, \\blur20\\bord1.0, \\blur30\\bord1.5"}$$

**Consejos**
* Usa `\pos(%.1f,%.1f)` o `\fscx%d\fscy%d` para controlar la precisión de los valores calculados y evitar decimales largos en el archivo ASS.
* Una plantilla como `\t(%d,%d,\fscx%d\fscy%d)` reúne los cálculos de tiempo y escala en un único nodo antes de la salida final.

---

## 9. Nodo `Basics/MultiTag` (Generador Universal de Etiquetas ASS)

Genera etiquetas ASS (*Advanced SubStation Alpha*): posición, movimiento, transformaciones, colores, alfa y recortes vectoriales.

![Basics/MultiTag](img/multitag.jpg)

**Selectores de cabecera**
1. **`[2.1] Tag Type` (`tag_type`):** Elige la etiqueta ASS y reconfigura los puertos de entrada:

```text
[ \pos ] ───> Inputs: [ X, Y ]
[ \move ] ──> Inputs: [ X1, Y1, X2, Y2, T1, T2 ]
[ \org ] ───> Inputs: [ X, Y ]
[ \t ] ─────> Inputs: [ Tags, T1, T2, Accel ]
[ \clip ] ──> Inputs: [ Shape / Drawing ]
[ \1c..\4c ]> Inputs: [ Color ]
[ \alpha ] ─> Inputs: [ Alpha (0..255) ]
[ Escalar ] > Inputs: [ Value ] (ej. \fscx, \frz, \blur, \bord)
```

2. **Catálogo de tags:** Al pulsar dos veces sobre el cuerpo del nodo o hacer clic en la píldora de modo de la cabecera se abre el catálogo visual de etiquetas ASS. Se puede buscar por nombre, prefijo o categoría (*Posicionamiento, Cinemática, Colorimetría, Alfa, Escalas, Bordes, Tipografía, Karaoke*).

**Salida**
1. **`[1.1] String`:** La etiqueta formateada con sintaxis ASS válida (ej. `\pos(640,360)`, `\t(0,500,2.0,\fscx150\fscy150)`).

### Etiquetas soportadas
* **`pos` $\to$ `\pos(X,Y)`:** Posición en pantalla.
* **`move` $\to$ `\move(X1,Y1,X2,Y2[,T1,T2])`:** Movimiento lineal entre dos puntos.
* **`org` $\to$ `\org(X,Y)`:** Punto de origen para rotaciones (`\frz`) y deformaciones afines.
* **`t` $\to$ `\t([T1,T2,][Accel,]Tags)`:** Anima etiquetas a lo largo del tiempo.
* **`fad` $\to$ `\fad(FadeIn,FadeOut)`:** Fundido simple de entrada y salida, en milisegundos.
* **`fade` $\to$ `\fade(A1,A2,A3,T1,T2,T3,T4)`:** Fundido de opacidad temporizado de 3 niveles.
* **`clip` / `iclip` $\to$ `\clip(Shape)` / `\iclip(Shape)`:** Recorte vectorial normal o invertido.
* **`1c` $\dots$ `4c` $\to$ `\1c&HBBGGRR&` $\dots$ `\4c&HBBGGRR&`:** Colores de relleno, karaoke secundario, borde y sombra.
* **`alpha`, `1a` $\dots$ `4a` $\to$ `\alpha&HAA&` $\dots$ `\4a&HAA&`:** Opacidad global o por canal.
* **Escala y rotación:** `\fscx`, `\fscy`, `\frz`, `\frx`, `\fry`, `\fax`, `\fay`.
* **Borde y sombra:** `\bord`, `\xbord`, `\ybord`, `\shad`, `\xshad`, `\yshad`.
* **Desenfoque:** `\blur`, `\be`.
* **Tipografía y alineación:** `\an`, `\fs`, `\fsp`, `\q`.

**Consejos**
* Conecta salidas numéricas (`Basics/Number` o `Basics/Math`) a `\fscx`, `\fscy` o `\frz` en lugar de concatenar cadenas a mano.
* Conecta las salidas `String` de varios nodos `MultiTag` a `Basics/Concatenate` con separador `nil` para construir el bloque de sobreescritura `{\...}` final antes de la salida.

---

## 10. Nodo `Basics/Only` (Derivación y Filtrado Condicional)

Enruta o filtra datos según una condición evaluada sobre el contexto ASS activo.

![Basics/Only](img/only_a.jpg)

**Selectores de cabecera**
1. **`[2.1] Mode` (`mode`):** Define los puertos del nodo:
   * `select` (*Selector / Ternario 2 $\to$ 1*): dos entradas (`True`, `False`) y una salida (`Out`). Emite el dato de `True` si la condición es verdadera y el de `False` si es falsa.
   * `split` (*Desviador 1 $\to$ 2*): una entrada (`In`) y dos salidas (`True`, `False`). Si la condición es verdadera, envía el dato a `True` y emite la cadena vacía `""` en `False`. Si es falsa, emite `""` en `True` y envía el dato a `False`.

![Basics/Only (Filter Mode)](img/only_b.jpg)

### Puertos según el modo

#### Modo `select` (2 $\to$ 1)
* **Entradas:**
  * `True`: Dato emitido si la condición se cumple.
  * `False`: Dato emitido si la condición no se cumple.
* **Salidas:**
  * `[1.1] Out`: El valor seleccionado.

#### Modo `split` (1 $\to$ 2)
* **Entradas:**
  * `In`: Dato a enrutar.
* **Salidas:**
  * `[1.1] True`: El dato de entrada si la condición es verdadera; `""` en caso contrario.
  * `[1.2] False`: El dato de entrada si la condición es falsa; `""` en caso contrario.

**Propiedades**
1. **`[2.2] Condition` (`condition`):** Expresión lógica evaluada en cada iteración (ej. `char.i == 1`, `syl.duration > 300`, `j % 2 == 0`, `'kanji' in line.tags_str`). Defecto: `"True"`.

### Evaluación

$$\text{Modo select:} \quad \text{Out} = \begin{cases} \text{Input}(\text{True}) & \text{si } \text{eval}(\text{condition}) = \text{True} \\ \text{Input}(\text{False}) & \text{si } \text{eval}(\text{condition}) = \text{False} \end{cases}$$

$$\text{Modo split:} \quad (\text{Out}_{\text{True}}, \text{Out}_{\text{False}}) = \begin{cases} (\text{Input}, \texttt{""}) & \text{si } \text{eval}(\text{condition}) = \text{True} \\ (\texttt{""}, \text{Input}) & \text{si } \text{eval}(\text{condition}) = \text{False} \end{cases}$$

**Consejos**
* Usa `condition: char.i == 1` para aplicar un tamaño de fuente mayor (`\fs40`) o un color distinto solo a la primera letra de cada palabra o línea.
* En modo `select`, conecta dos colores a `True` y `False` con `condition: char.i % 2 == 0` para alternar colores entre caracteres pares e impares.

---

## 11. Nodo `Basics/Once` (Evaluación Única con Caché por Ámbito)

Guarda en caché el valor de su entrada para no recalcularlo dentro de un mismo ámbito (línea, palabra, sílaba, carácter o sub-bucle).

![Basics/Once](img/once.jpg)

**Selectores de cabecera**
1. **`[2.1] Mode` (`mode`):** El ámbito de la caché:
   * `global`: se evalúa una sola vez en toda la ejecución de la macro sobre el script.
   * `line`: una vez al inicio de cada línea de diálogo.
   * `word`: una vez al inicio de cada palabra.
   * `syl`: una vez al inicio de cada sílaba de karaoke.
   * `char`: una vez por carácter.
   * `loop`: una vez por cada ciclo de la variable de sub-bucle indicada en `iterator` (defecto: `j`).

**Entrada**
1. **`In`:** El dato a guardar en caché (ej. trazados vectoriales de `Text to Shape`, `IMG to Shape` o selecciones de color).

**Propiedades**
1. **`[2.2] Iterator` (`iterator`):** Nombre de la variable de iteración que se vigila cuando `mode = "loop"` (defecto: `"j"`).

**Salida**
1. **`[1.1] Out`:** El valor almacenado, sin reevaluar el subgrafo conectado a la entrada.

### Clave de caché
La clave de caché combina el identificador del nodo y la clave de ámbito del modo activo:

$$\text{CacheKey} = \langle \text{NodeID}, \, \text{ScopeKey} \rangle$$

$\text{ScopeKey}$ depende del modo:
* `global` $\to \texttt{"global"}$
* `line` $\to \texttt{"line\_" + LineID}$
* `word` $\to \texttt{"line\_" + LineID + "\_word\_" + WordID}$
* `syl` $\to \texttt{"line\_" + LineID + "\_syl\_" + SylID}$
* `char` $\to \texttt{"line\_" + LineID + "\_char\_" + CharID}$
* `loop` $\to \texttt{"line\_" + LineID + "\_loop\_" + IteratorName + "\_" + IteratorValue}$

Si $\text{CacheKey}$ ya está en memoria, se devuelve el valor guardado en tiempo $\mathcal{O}(1)$ y no se ejecuta el grafo anterior.

**Consejos**
* Coloca un nodo `Once (mode: char)` tras `Text to Shape` al hacer efectos multicapa con `MaxLoop` o `Shape/Array`. Así la geometría del glifo se calcula una vez por carácter en lugar de en cada pasada del bucle.
* Inserta `Once (mode: syl)` después de un generador aleatorio para que todos los fragmentos o partículas de una misma sílaba compartan el mismo valor aleatorio.

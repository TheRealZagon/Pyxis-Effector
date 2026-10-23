# Functions

La categoría **Functions** tiene 16 nodos para manipular etiquetas ASS, generar osciladores, ramificar según condiciones, crear gradientes de color y trabajar con movimiento y geometría vectorial.

* **8.A, modulación de tags, osciladores y condiciones:** [`Tag Manipulator`](#1-nodo-functionstag-manipulator-manipulador-de-tags) (§1), [`Tag Oscillator`](#2-nodo-functionstag-oscillator-oscilador-de-tags) (§2), [`Glitter`](#3-nodo-functionsglitter-generador-estocástico-de-destellos) (§3), [`Conditioner`](#4-nodo-functionsconditioner-condicionador-lógico) (§4), [`Animation`](#8-nodo-functionsanimation-animación-fbf-y-modulación-alfa) (§8).
* **8.B, gradientes de color, muestreo de imágenes y cinemática:** [`Color Gradient`](#5-nodo-functionscolor-gradient-gradiente-de-color-multicapa) (§5), [`Clip Gradient`](#6-nodo-functionsclip-gradient-bandas-y-mallas-de-recorte-para-degradados) (§6), [`IMG to pixels`](#7-nodo-functionsimg-to-pixels-muestreo-ráster-a-partículas) (§7), [`Polar to Cartesian`](#12-nodo-functionspolar-to-cartesian-conversor-polar-a-cartesiano) (§12), [`Interpolator`](#14-nodo-functionsinterpolator-interpolador-paramétrico-polimórfico) (§14).
* **8.C, curvas Bézier, partículas y texto vectorial:** [`Bezier Curve`](#9-nodo-functionsbezier-curve-curvas-y-splines-bézier-2d) (§9), [`Move Tag`](#10-nodo-functionsmove-tag-cinemática-y-trayectorias-de-movimiento-ass) (§10), [`Move Text`](#11-nodo-functionsmove-text-movimiento-cinemático-tipográfico-coordinado) (§11), [`Particles`](#13-nodo-functionsparticles-enjambres-de-partículas-vectoriales) (§13), [`Text on Path`](#15-nodo-functionstext-on-path-texto-adaptado-sobre-curvas) (§15), [`Text to Shape`](#16-nodo-functionstext-to-shape-vectorización-tipográfica-de-glifos) (§16).

---

## 1. Nodo `Functions/Tag Manipulator` (Manipulador de Tags)

Transforma cadenas de etiquetas ASS. Puede invertirlas (colores complementarios, alfas invertidos, rotaciones opuestas, máscaras de recorte inversas), restablecerlas a los valores del estilo activo o extraer el valor de una etiqueta concreta.

![Functions/Tag Manipulator](img/tag_manipulator.jpg)

### Modos
**`Mode` (`mode`)** cambia lo que hace el nodo y reconfigura sus puertos:
* **`invert` (INV):** invierte cada etiqueta ASS de la entrada, incluidas las que están dentro de bloques `\t(...)`.
* **`reset` (RESET):** lee el estilo de subtítulo activo y genera las etiquetas que restauran sus valores base.
* **`extractor` (EXTRACT):** busca la última aparición de la etiqueta indicada en `Target Tag` y extrae su valor limpio, su valor numérico y el bloque original completo.

### Entradas

En los modos `invert` y `reset`:
1. **`Tags In` (`tags`):** las etiquetas ASS a procesar. Acepta etiquetas estáticas (ej. `\frz45\1c&H0000FF&\alpha&H80&`) y transformaciones `\t(...)` (ej. `\t(0,300,\frz-45\fscx150)`). En modo `reset`, `"all"` o vacío regenera todo el estilo base. (Defecto: `""`).

En el modo `extractor`:
1. **`Tags In` (`tags`):** la cadena de etiquetas de la que se extrae la información (ej. `{\pos(320,240)\frz-35.5\1c&H00FF88&}`).
2. **`Target Tag` (`target_tag`):** nombre de la etiqueta a buscar, con o sin barra invertida `\`. Acepta los alias habituales de ASS como `frz` / `fr`, `1c` / `c`, `alpha`, `fscx`, `pos`, `org`, `clip`, `blur`. (Defecto: `"frz"`).

### Salidas

En los modos `invert` y `reset`:
1. **`[1.1] Tags Out`:** las etiquetas invertidas o las de restablecimiento del estilo.

En el modo `extractor`:
1. **`[1.1] String`:** el valor sin prefijo de etiqueta ni paréntesis (ej. `"-35.5"`, `"320,240"`, `"&H00FF88&"`).
2. **`[1.2] Value`:** el valor como `float`. Si son coordenadas compuestas (ej. `320,240`), devuelve el primer componente (`320.0`). Si es un canal de color o alfa hexadecimal de 1 o 2 dígitos, devuelve su entero decimal ($0 \dots 255$).
3. **`[1.3] Raw String`:** el bloque completo de la etiqueta tal como aparece en la entrada (ej. `\frz-35.5`, `\pos(320,240)`).

### Reglas de inversión (`invert`)

| Familia de Tags ASS | Etiquetas Soportadas | Regla de Inversión | Ejemplo Entrada $\to$ Salida |
| :--- | :--- | :--- | :--- |
| **Colores Primario y Secundarios** | `\c`, `\1c`, `\2c`, `\3c`, `\4c` | **Complementario RGB Negativo:**<br>$(R', G', B') = (255 - R, 255 - G, 255 - B)$ | `\1c&H0000FF&` $\to$ `\1c&HFFFF00&` (Azul $\to$ Amarillo) |
| **Canales Alfa** | `\alpha`, `\1a`, `\2a`, `\3a`, `\4a` | **Complemento Hexadecimal:**<br>$\alpha' = 255 - \alpha$ | `\alpha&H00&` $\to$ `\alpha&HFF&` (Opaco $\to$ Transparente) |
| **Rotaciones, Cizallamiento y Sombras** | `\frz`, `\frx`, `\fry`, `\fr`, `\fax`, `\fay`, `\fsp`, `\xshad`, `\yshad` | **Inversión de Signo Aritmético:**<br>$V' = -V$ | `\frz35` $\to$ `\frz-35`<br>`\fax0.5` $\to$ `\fax-0.5` |
| **Bordes, Difuminado y Sombras Escalares** | `\bord`, `\xbord`, `\ybord`, `\blur`, `\be`, `\shad` | **Anulación / Reseteo a Cero:**<br>$V' = 0$ | `\bord4\blur3` $\to$ `\bord0\blur0` |
| **Escalas de Transformación** | `\fscx`, `\fscy` | **Retorno a Escala Base:**<br>$V' = \text{Style.Scale}$ (o $100\%$) | `\fscx200` $\to$ `\fscx100` |
| **Máscaras Vectoriales de Recorte** | `\clip`, `\iclip` | **Conmutación de Máscara Inversa:**<br>`\clip` $\longleftrightarrow$ `\iclip` | `\clip(m 0 0 ...)` $\to$ `\iclip(m 0 0 ...)` |

Dentro de un bloque `\t(t1, t2, [accel,] tags)` solo se invierten las etiquetas internas. El intervalo de tiempo y la aceleración no se tocan:

$$\text{\textbackslash t}(100, 400, 1.5, \text{\textbackslash frz45\textbackslash 1c\&H0000FF\&}) \quad \longrightarrow \quad \text{\textbackslash t}(100, 400, 1.5, \text{\textbackslash frz-45\textbackslash 1c\&HFFFF00\&})$$

### Restablecimiento de estilo (`reset`)
El nodo consulta el `styleref` del contexto activo (`active_unit` o `line`) y toma los valores base del archivo ASS de Aegisub.
* Si `Tags In` está vacío, es `"all"` o `"todo"`, genera la secuencia completa de reseteo:
  $$\text{\textbackslash 1c}\dots\text{\textbackslash 2c}\dots\text{\textbackslash 3c}\dots\text{\textbackslash 4c}\dots\text{\textbackslash 1a}\dots\text{\textbackslash 2a}\dots\text{\textbackslash 3a}\dots\text{\textbackslash 4a}\dots\text{\textbackslash alpha\&H00\&}\text{\textbackslash fscx}\dots\text{\textbackslash fscy}\dots\text{\textbackslash fs}\dots\text{\textbackslash fsp}\dots\text{\textbackslash bord}\dots\text{\textbackslash shad}\dots\text{\textbackslash frz}\dots$$
* Si `Tags In` lista etiquetas concretas (ej. `\1c\fscx`), restablece solo esas.

### Uso
* **Efectos espejo:** en bucles dobles o partículas que rebotan hacia ambos lados, pasa una rama directa y la otra por `Tag Manipulator (INV)` para invertir `\frz`, `\fax` y el desplazamiento relativo de sombra.
* **Extracción de coordenadas:** conecta la salida `String` de un `Tag Manipulator (EXTRACT)` con `Target Tag: pos` a un nodo `Math` para derivar trayectorias relativas a la posición original del glifo.

### Ejemplo: capas en espejo
Dos capas, la segunda obtenida invirtiendo la primera:

```
[Basics/MultiTag: \frz30\fscx120] ──► Tags In ──► [System/Output (Layer 2)]
               │
               └──► Tags In ──► [Functions/Tag Manipulator: mode=invert] ──► Tags Out ──► [System/Output (Layer 1)]
```

* **Capa 2 (directa):** `{\an5\pos(syl.center, syl.middle)\frz30\fscx120}`.
* **Capa 1 (invertida):** `{\an5\pos(syl.center, syl.middle)\frz-30\fscx100}`. La rotación pasa a $-30^\circ$ y la escala vuelve a $100\%$.

---

## 2. Nodo `Functions/Tag Oscillator` (Oscilador de Tags)

Genera modulaciones periódicas, estroboscópicas, rítmicas o en onda sobre cualquier propiedad ASS. Compila la secuencia en bloques `\t(...)` que cubren la vida del elemento activo.

![Functions/Tag Oscillator](img/tag_oscillator.jpg)

### Modos
1. **`Oscillation Mode` (`mode`):** define el perfil de la transición:
   * **`wave` (Onda continua, por defecto):** transición suave y continua entre los estados de la lista de tags ($T_{\text{trans}} = S_i$).
   * **`steps` / `flashes` / `strobe` (Paso / Estroboscópico):** cambios instantáneos sin interpolación ($t_2 = t_1 + 1$).
   * **`pulses` (Pulsos):** la transición ocupa el $50\%$ del paso y el resto queda estático.
   * **`rhythmic` (Rítmico):** pasos no uniformes, leídos en orden desde `Rhythm Pattern`.
   * **`noise` (Ruido):** variación del paso con fluctuaciones pseudoaleatorias.
2. **`Order Mode` (`order_mode`):** cómo se eligen los tags de la lista:
   * **`sequential` (Secuencial, por defecto):** recorre la lista cíclicamente ($0, 1, 2, \dots, N-1, 0, 1, \dots$).
   * **`pingpong` (Rebote):** avanza y retrocede ($0, 1, 2, 1, 0, 1, \dots$).
   * **`random` (Aleatorio):** un tag al azar en cada paso, con semilla determinista.
   * **`shuffle` (Aleatorio sin repetición inmediata):** pseudoaleatorio, sin repetir el mismo tag en pasos consecutivos.

### Entradas
1. **`Start Time` (`start_time`):** inicio en milisegundos relativos a la línea; vacío equivale a `0.0 ms`. (Defecto: `""`).
2. **`End Time` (`end_time`):** fin en ms; vacío toma la duración del elemento activo (`fx.dur`, `syl.duration` o `line.duration`). (Defecto: `""`).
3. **`Step (ms)` (`step_ms`):** duración de cada ciclo o paso en ms. (Defecto: `200.0`).
4. **`Trans (ms)` (`trans_ms`):** duración de la interpolación `\t` hacia el siguiente tag. (Defecto: `50.0`).
5. **`Duty Cycle` (`duty_cycle`):** ciclo de trabajo en el rango $[0.01, 1.0]$. Si se conecta o rellena, sustituye a `Trans (ms)` con $T_{\text{trans}} = S_i \cdot \text{DutyCycle}$.
6. **`Tags` (`tags`):** lista de cadenas de tags separadas por coma o salto de línea (ej. `\frz30\fry20, \frz-20\fry-20` o `\1c&HFF0000&, \1c&H00FF00&, \1c&H0000FF&`).
7. **`Accel` (`accel`):** exponente de aceleración ASS que se escribe en cada bloque `\t(...)`. (Defecto: `1.0`).
8. **`Dilate Step` (`dilat_step_ms`):** cantidad que se suma al paso en cada iteración: $S_i = S_0 + \Delta_{S} \cdot i$. (Defecto: `0.0`).
9. **`Dilate Trans` (`dilat_trans_ms`):** cantidad que se suma a la transición en cada iteración: $T_i = T_0 + \Delta_{T} \cdot i$. (Defecto: `0.0`).
10. **`Seq Offset` (`offset_seq_ms`):** pausa adicional al completar un ciclo entero de la lista de tags. (Defecto: `0.0`).
11. **`Rhythm Pattern` (`rhythm_pattern`):** duraciones separadas por comas (ej. `100, 50, 200, 100`) para el modo `rhythmic`.

### Salidas
1. **`[1.1] Tag Out`:** la cadena de bloques `\t(t1, t2, [accel,] tags)` que cubre todo el intervalo.
2. **`[1.2] Current Val`:** el tag activo en el fotograma o tiempo actual (`frame_time` o `fx_start_time`).
3. **`[1.3] Keyframes`:** lista de todos los fotogramas clave como tuplas `[(t1, t2, tag_str, accel), ...]`.
4. **`[1.4] Values`:** lista con el texto del tag en cada paso.

### Temporización

```
Modo: wave (Transición Continua)
Tags: [ Tag A, Tag B ]
───┬─────────────┬─────────────┬─────────────┬─────────────► Tiempo (ms)
   │ \t(0,200,B) │\t(200,400,A)│\t(400,600,B)│\t(600,800,A)│
   0            200           400           600           800

Modo: steps / strobe (Conmutación Instantánea)
───┬─────────────┬─────────────┬─────────────┬─────────────► Tiempo (ms)
   │ \t(0,1,B)   │ \t(200,201,A) \t(400,401,B)│ \t(600,601,A)
   0            200           400           600           800
```

Para cada paso $i \ge 0$:
1. **Duración del paso ($S_i$):**
   $$S_i = \begin{cases} \text{RhythmPattern}[i \pmod M] & \text{si } \text{rhythm\_pattern} \ne \emptyset \\ \max(5.0, S_{\text{step}} + \Delta_{\text{dilate\_step}} \cdot i) & \text{en otro caso} \end{cases}$$
2. **Ventana de transición ($T_i$):**
   $$T_i = \begin{cases} 0 & \text{si es modo } \text{steps/strobe/flashes} \\ S_i \cdot \text{clamp}(DC, 0.01, 1.0) & \text{si se definió } \text{DutyCycle} \\ \min(S_i, \max(0.0, T_{\text{trans}} + \Delta_{\text{dilate\_trans}} \cdot i)) & \text{en modo estándar} \end{cases}$$
3. **Marcas de tiempo:**
   $$t_1 = \text{round}(T_{\text{start}} + t_{\text{curr}}), \quad t_2 = \begin{cases} t_1 + 1 & \text{si } T_i \le 0 \\ \min(t_{\text{end}}, \text{round}(t_1 + T_i)) & \text{en otro caso} \end{cases}$$

### Uso
* **Vibrato:** `Tags` = `\frz-5, \frz5` con `Step: 60` y `Trans: 30` da un vibrato continuo y sutil en la sílaba cantada.
* **Pulso al ritmo del audio:** usa `Mode: rhythmic` y pon en `Rhythm Pattern` los intervalos en milisegundos medidos en el audio (`125, 250, 125, 375`).

### Ejemplo: vibrato y onda de escala en una nota sostenida
Una onda sobre una sílaba de $300\text{ ms}$:

```
[Functions/Tag Oscillator: mode=wave, step_ms=80, trans_ms=40] ──► Tag Out ──► Tags ──► [System/Output]
   tags: "\frz-4\fscy95, \frz4\fscy105"
```

`Tag Out` contiene:
```ass
\t(0,40,\frz-4\fscy95)\t(80,120,\frz4\fscy105)\t(160,200,\frz-4\fscy95)\t(240,280,\frz4\fscy105)
```
El glifo alterna entre una inclinación de $\mp 4^\circ$ y un estiramiento vertical del $95\%$ al $105\%$.

---

## 3. Nodo `Functions/Glitter` (Generador Estocástico de Destellos)

Emite destellos, pulsos, ondas o ruido aleatorios sobre varias propiedades ASS a la vez, para simular brillo y purpurina sin un patrón repetitivo predecible.

![Functions/Glitter](img/glitter.jpg)

### Modos
**`Mode` (`mode` / `random_profile`)** elige la envolvente temporal:
* **`flashes` (Destello rápido, por defecto):** pausa aleatoria larga $\to$ ataque muy rápido ($1 \dots 3\text{ ms}$) $\to$ sostenimiento corto ($5 \dots 15\text{ ms}$) $\to$ decaimiento largo ($40 \dots 100\text{ ms}$). Pensado para chispas y purpurina.
* **`pulses` (Pulsaciones):** pausa moderada $\to$ subida progresiva ($150 \dots 250\text{ ms}$) $\to$ sostenimiento $\to$ bajada simétrica con aceleración no lineal.
* **`waves` / `oleaje` (Oleaje suave):** subidas y bajadas lentas y continuas ($250 \dots 400\text{ ms}$), sin pausas marcadas.
* **`noise` (Ruido estocástico):** pasos muy cortos ($15 \dots 50\text{ ms}$) con un valor aleatorio por fotograma.

### Entradas
1. **`Start Time` (`start_time`):** inicio del efecto en ms. (Defecto: `"0"`).
2. **`End Time` (`end_time`):** fin en ms o expresión de contexto (ej. `"fx.dur"`). (Defecto: `"fx.dur"`).
3. **`Density` (`density`):** multiplicador de frecuencia. Valores $> 1.0$ acortan las pausas y dan más destellos por segundo; valores $< 1.0$ los espacian. (Defecto: `1.0`).
4. **`Seed` (`seed`):** semilla entera para que el resultado sea reproducible. (Defecto: `0`).
5. **Entradas expandibles de pistas (`In 1`, `In 2`, ...):** cada pista tiene tres campos:
   * **`Tag` (`tag_k`):** la etiqueta ASS a animar (ej. `\fscx`, `\1c`, `\blur`, `\alpha`, `\frz`).
   * **`Min` (`min_k`):** valor de reposo (número, porcentaje, color hexadecimal `#RRGGBB` o `&HBBGGRR&`).
   * **`Max` (`max_k`):** valor en el punto máximo del destello.

`Tag` también acepta estos *dark tags* agrupados:
* `\fscxy`: anima `\fscx` y `\fscy` con el mismo valor.
* `\frxyz`: anima `\frx`, `\fry` y `\frz` a la vez.
* `\134c`: anima juntos los colores primario (`\1c`), borde (`\3c`) y sombra (`\4c`).
* `\xybord`: se expande a `\xbord` y `\ybord`.
* `\bs`: anima juntos el borde `\bord` y la sombra `\shad`.

### Salidas
1. **`[1.1] List`:** todos los bloques `\t(...)` de todas las pistas, sincronizados en los mismos instantes.
2. **`[1.2] TAG 1`:** solo los bloques `\t(...)` de la primera pista.
3. **`[1.3] TAG 2` (expandible):** lo mismo para la segunda pista, y así sucesivamente.

### Cómo funciona

```
Envolvente del Perfil: flashes (Destello)
Valor Max (Cúspide) ─────┐       /───\
                         │      /     \
                         │     /       \
Valor Base (Reposo) ─────┴────/         \──────────────
                         ▲    ▲ ▲     ▲ ▲
                         │    │ │     │ │
                         └──┬─┘ └─┬─┘ └─┬────────┘
                         Pausa   Ataque Decaimiento
                         (dens)  (1-3ms)(40-100ms)
```

1. **Semilla por unidad:** el generador pseudoaleatorio se inicializa por separado para cada sílaba o glifo ($i$):
   $$\text{Seed}_{\text{local}} = \text{Seed} \cdot 1000 + i + 1337$$
2. **Colores:** si `Min` y `Max` son colores, los canales $(R_1, G_1, B_1)$ y $(R_2, G_2, B_2)$ se interpolan en espacio RGB y se escriben como `&HBBGGRR&`:
   $$R_{\text{rand}} = \text{round}(R_1 + (R_2 - R_1) \cdot \text{Factor}), \quad G_{\text{rand}} = \text{round}(G_1 + (G_2 - G_1) \cdot \text{Factor})$$

### Uso
* **Purpurina:** `In 1` = `\fscxy` con rango `(100, 160)`, `In 2` = `\1c` con rango `(#FFFFFF, #FFE460)`. Conecta `List` a `Output` para obtener destellos simultáneos de escala y color dorado.

### Ejemplo: destellos dorados
Ráfagas aleatorias sobre cada carácter durante $400\text{ ms}$:

```
[Functions/Glitter: mode=flashes, density=1.5, start=0, end=400] ──► List ──► Tags ──► [System/Output]
   In 1: tag=\fscxy, min=100, max=140
   In 2: tag=\1c, min=#FFFFFF, max=#FFD700
```

El nodo interpola los canales RGB y descompone `\fscxy`. `List` queda así:
```ass
\t(83,85,\fscx133\fscy133\1c&H00D7FF&)\t(93,173,\fscx105\fscy105\1c&HFFFFFF&)\t(208,211,\fscx133\fscy133\1c&H00D7FF&)...
```
Cada glifo recibe sus destellos en instantes distintos según su índice, así que no parpadean todos a la vez.

---

## 4. Nodo `Functions/Conditioner` (Condicionador Lógico)

Condicional en línea ($A \text{ if } \text{Cond} \text{ else } B$). Elige uno de dos valores (texto, etiquetas ASS, números o listas) según una expresión evaluada sobre el contexto del subtítulo.

![Functions/Conditioner](img/conditioner.jpg)

### Entradas
1. **`Condition` (`condition`):** expresión booleana. Acepta constantes (`True`, `False`, `1`, `0`), comparaciones (`syl.i % 2 == 0`, `char.i > 3`), pertenencia (`line.style == "Romaji"`, `'kanji' in line.tags_str`) o un cable booleano. (Defecto: `"True"`).
2. **`If True` (`if_true`):** valor que se emite cuando la condición es verdadera ($C = \text{True}$). Puede ser una cadena de tags ASS, un número, una lista o un cable. (Defecto: `""`).
3. **`If False` (`if_false`):** valor que se emite cuando la condición es falsa ($C = \text{False}$). (Defecto: `""`).

### Salidas
1. **`[1.1] Out`:** el valor seleccionado. Si es una lista o tupla, sus elementos se unen con `, `.

### Evaluación
La expresión se evalúa en un entorno aislado que expone estas variables de contexto:

| Variable Inyectada | Tipo | Descripción |
| :--- | :---: | :--- |
| `syl.i`, `char.i`, `word.i`, `fx.i`, `j`, `i` | `int` | Índice secuencial del elemento activo ($0$-based o $1$-based). |
| `syl.n`, `char.n`, `word.n`, `line.n` | `int` | Cantidad total de elementos en el grupo de iteración. |
| `line.style`, `line.actor`, `line.effect` | `str` | Metadatos de la línea de diálogo original. |
| `line.duration`, `syl.duration`, `fx.dur` | `float` | Duraciones en milisegundos. |
| `syl.text`, `char.text` | `str` | Contenido del texto o fonema del glifo activo. |

$$\text{Out} = \begin{cases} \text{If True} & \text{si } \text{eval}(\text{Condition}, \text{Context}) = \text{True} \\ \text{If False} & \text{en cualquier otro caso} \end{cases}$$

### Uso
* **Colores alternos:** `Condition` = `syl.i % 2 == 0`, `If True` = `\1c&H00FFFF&` (cian), `If False` = `\1c&HFF00FF&` (magenta).
* **Saltarse espacios:** `Condition: char.text.strip() == ""` permite evitar transformaciones pesadas en caracteres invisibles.

### Ejemplo: caracteres pares e impares
Un color y una escala distintos para los caracteres pares e impares dentro del bucle principal de caracteres:

```
[Loops/Main Loop: char] ──► char.i ───────────────────────────────┐
                                                                  ▼
[Functions/Conditioner: condition="char.i % 2 == 0"] ──► Out ──► Tags ──► [System/Output]
   If True:  "\1c&H00FFFF&\fscxy110"
   If False: "\1c&HFF0088&\fscxy90"
```

* **Caracteres pares ($i \in \{2, 4, 6\}$):** `{\an5\pos(char.center, char.middle)\1c&H00FFFF&\fscx110\fscy110}`.
* **Caracteres impares ($i \in \{1, 3, 5\}$):** `{\an5\pos(char.center, char.middle)\1c&HFF0088&\fscx90\fscy90}`.

Un solo nodo cubre ambos casos, sin duplicar capas ni generar eventos vacíos.

---

## 5. Nodo `Functions/Color Gradient` (Gradiente de Color Multicapa)

Interpola entre varias paradas de color (*multi-stop gradient*) con una curva de aceleración (*easing*). Devuelve el color en una posición $t \in [0.0, 1.0]$, o listas de colores y etiquetas ASS para repartir entre caracteres, sílabas o partículas.

![Functions/Color Gradient](img/color_gradient.jpg)

### Entradas
1. **`Progress (0-1)` (`prog`):** factor de interpolación $t \in [0.0, 1.0]$. Acepta constantes, cables o expresiones de contexto (ej. `char.i / char.n`, `syl.i / syl.n`, `j / maxloop`). (Defecto: `"char.i / char.n"`).
2. **`Color List` (`colors_str`):** paradas de color separadas por comas, espacios o saltos de línea. Acepta códigos hexadecimales (`#RRGGBB`), nombres HTML o códigos ASS (`&HBBGGRR&`). (Defecto: `"#95E648,#3E750C,#ED38CA"`).
3. **`Total (N)` (`total`):** número de muestras para las salidas en lote (`Color List` o `Tags`). Si $N > 1$, genera $N$ muestras repartidas uniformemente entre $t=0.0$ y $t=1.0$. (Defecto: `"1"`).
4. **`Accel` (`accel`):** exponente de aceleración. `1.0` es lineal; valores $> 1.0$ concentran la transición al final (*ease-in*); valores $< 1.0$ la concentran al inicio (*ease-out*). (Defecto: `"1.0"`).
5. **`Tag` (`tag_type`):** etiqueta que se antepone a los códigos de color en la salida `Tags` (`\1c`, `\2c`, `\3c`, `\4c` o `\c`). (Defecto: `"\1c"`).

### Salidas
1. **`[1.1] ASS Color`:** el color `&HBBGGRR&` en el progreso $t$ de `Progress (0-1)`.
2. **`[1.2] Color List`:** códigos de color ASS separados por coma para los $N$ pasos si $N > 1$, o el color único si $N = 1$.
3. **`[1.3] Tags`:** los mismos colores con el prefijo de etiqueta (ej. `\1c&H48E695&` si $N=1$, o `\1c&H48E695&, \1c&H0C753E&, \1c&HCADB38&` si $N > 1$).

### Cómo funciona

```
Paradas:  C1 (#95E648)          C2 (#3E750C)          C3 (#ED38CA)
          ├──────────────────────────┼──────────────────────────┤
Progreso: t = 0.0                  t = 0.5                  t = 1.0
Segmento: └────── Segmento 0 ───────┘└────── Segmento 1 ───────┘
```

**Easing.** Antes de interpolar colores, el progreso $t \in [0.0, 1.0]$ pasa por la función de aceleración:

$$t_{\text{eased}} = \begin{cases} t^{\text{accel}} & \text{si } \text{accel} > 1.0 \\ 1.0 - (1.0 - t)^{1.0 / \text{accel}} & \text{si } 0.0 < \text{accel} < 1.0 \\ t & \text{si } \text{accel} = 1.0 \end{cases}$$

**Segmentos e interpolación RGB.** Con $K$ paradas de color $\{C_0, C_1, \dots, C_{K-1}\}$:
1. Se localiza el segmento (hay $K-1$):
   $$\text{pos} = t_{\text{eased}} \cdot (K - 1), \quad \text{idx} = \min(K - 2, \lfloor \text{pos} \rfloor), \quad t_{\text{local}} = \text{pos} - \text{idx}$$
2. Se toman los canales RGB de las paradas adyacentes $C_{\text{idx}} = (R_1, G_1, B_1)$ y $C_{\text{idx}+1} = (R_2, G_2, B_2)$.
3. Se interpola linealmente cada canal:
   $$R = \text{round}(R_1 + (R_2 - R_1) \cdot t_{\text{local}})$$
   $$G = \text{round}(G_1 + (G_2 - G_1) \cdot t_{\text{local}})$$
   $$B = \text{round}(B_1 + (B_2 - B_1) \cdot t_{\text{local}})$$
4. El resultado se escribe en el formato BGR de ASS: `&HBBGGRR&`.

### Uso
* **Degradado carácter a carácter:** deja `Progress: char.i / char.n` y conecta `Tags` a `System/Output`. Cada letra toma su color.
* **Keyframes de color con `Concatenate (Zip)`:** pon `Total: 5`, conecta `Tags` a la entrada 1 de un `Concatenate (Zip)` y una secuencia de tiempos `\t(0,200,), \t(200,400,), ...` a la entrada 2.

### Ejemplo: degradado de tres colores a lo largo de una línea
Tres paradas (`#FF4500` naranja, `#FFD700` dorado, `#00FFFF` cian) con aceleración ease-in, un color por carácter:

```
[Loops/Main Loop: mode=char] ──► char.i / char.n ─────────────────────┐
                                                                       ▼
[Functions/Color Gradient: accel=1.0] ──► Tags (\1c) ──────────────► Tags In ──► [System/Output]
   colors: "#FF4500, #FFD700, #00FFFF"
```

* **Primer carácter ($t=0.0$):** `{\an5\pos(320, 240)\1c&H0045FF&}` (naranja rojizo).
* **Carácter central ($t \approx 0.5$):** `{\an5\pos(420, 240)\1c&H00D7FF&}` (dorado).
* **Último carácter ($t=1.0$):** `{\an5\pos(520, 240)\1c&HFFFF00&}` (cian).

---

## 6. Nodo `Functions/Clip Gradient` (Bandas y Mallas de Recorte para Degradados)

Divide el área de tinta visible (*glyph ink bounding box*) del elemento activo en franjas o en una malla de $C \times R$ celdas con solapamiento subpíxel. La malla se ajusta al trazado real del glifo y no a los márgenes tipográficos vacíos. Sirve para degradados de color multicapa, barridos angulares y transiciones por celdas en libass sin líneas de costura visibles.

![Functions/Clip Gradient](img/clip_gradient.jpg)

### Modos
**`Mode` (`out_mode`)** define la sintaxis de salida:
* **`\clip` (`clip`, por defecto):** emite `\clip(x1,y1,x2,y2)` para rectángulos, o la forma vectorial `\clip(m x1 y1 l x2 y2 ...)`.
* **`\iclip` (`iclip`):** emite recortes inversos `\iclip(...)`.
* **`Shape` (`shape`):** emite el trazado ASSdraw puro (`m ... l ...`) centrado en el origen local `(0, 0)`, para alimentar nodos de geometría.

### Entradas
1. **`Cols` (`cols`, slot `0`):** número de columnas. (Defecto: `"5"`).
2. **`Rows` (`rows`, slot `1`):** número de filas. `Rows: 1` da franjas verticales, `Cols: 1` da franjas horizontales, y valores mayores en ambos dan una malla 2D ($N = \text{Cols} \times \text{Rows}$). (Defecto: `"1"`).
3. **`Angle` (`angle`, slot `2`):** inclinación de la cuadrícula o las franjas en grados ($0^\circ \dots 360^\circ$). $0^\circ$ da celdas rectangulares; otros ángulos dan cuadriláteros rotados. (Defecto: `"0"`).
4. **Cruceta de relleno (sin puerto de cable, 5 cuadros en línea):** expande el área de recorte más allá de los bordes de la tinta, por dirección o de forma uniforme:
   * **`Pad Top` (`pad_top`):** píxeles extra hacia arriba. (Defecto: `"0"`).
   * **`Pad Left` (`pad_left`):** píxeles extra hacia la izquierda. (Defecto: `"0"`).
   * **`Padding` (`padding`, centro):** píxeles que se suman en las 4 direcciones además de cada valor direccional ($\text{eff}_{\text{dir}} = \text{padding} + \text{pad}_{\text{dir}}$). (Defecto: `"0"`).
   * **`Pad Right` (`pad_right`):** píxeles extra hacia la derecha. (Defecto: `"0"`).
   * **`Pad Bottom` (`pad_bottom`):** píxeles extra hacia abajo. (Defecto: `"0"`).
5. **`Overlap` (`overlap`, slot `3`):** expansión subpíxel en píxeles aplicada a cada celda para ocultar las costuras de anti-aliasing de libass. (Defecto: `"0.5"`).
6. **`Order` (`order`, slot `4`):** ordenamiento 2D (Numpad, radial o aleatorio): `"79"`, `"97"`, `"13"`, `"31"`, `"71"`, `"17"`, `"93"`, `"39"`, `"5"`, `"-5"`, `"cw"`, `"ccw"`, `"rand"`. (Defecto: `"79"`).

### Salidas
1. **`[1.1] Output`:** la etiqueta `\clip(...)` / `\iclip(...)` o el trazado ASSdraw de la celda activa.
2. **`[1.2] Progress (0-1)`:** progreso de la celda actual:
   $$\text{Progress} = \frac{k}{N - 1} \in [0.0, 1.0]$$
3. **`[1.3] Index`:** índice de la celda activa ($1$-based: $1 \dots N$).
4. **`[1.4] Total`:** número total de celdas ($N = \text{Cols} \times \text{Rows}$).
5. **`[1.5] Col`:** columna de la celda activa ($1 \dots \text{Cols}$).
6. **`[1.6] Row`:** fila de la celda activa ($1 \dots \text{Rows}$).

Variables inyectadas en el contexto:
* **`c_i` / `clip_i`:** índice de la celda activa.
* **`c_n` / `clip_n` / `clip_max`:** número total de celdas ($N$).
* **`c_col` / `col`:** columna actual ($1$-based).
* **`c_row` / `row`:** fila actual ($1$-based).

### Geometría

```
Franjas 1D (Cols: 4, Rows: 1)      Malla 2D (Cols: 3, Rows: 2)       Malla Rotada (Ángulo θ)
┌───┬───┬───┬───┐                 ┌─────┬─────┬─────┐                ┌───────/───────┐
│   │   │   │   │                 │ 0,0 │ 1,0 │ 2,0 │               / 0,0   / 1,0   /
│ 0 │ 1 │ 2 │ 3 │                 ├─────┼─────┼─────┤              /───────/───────/
│   │   │   │   │                 │ 0,1 │ 1,1 │ 2,1 │             / 0,1   / 1,1   /
└───┴───┴───┴───┘                 └─────┴─────┴─────┘            └───────/───────┘
```

**Ángulo $0^\circ$.** El nodo genera rectángulos simples alineados a los ejes, `\clip(x1, y1, x2, y2)`, que son los más baratos de rasterizar para libass:
$$W_{\text{cell}} = \frac{B_{\text{width}}}{C}, \quad H_{\text{cell}} = \frac{B_{\text{height}}}{R}$$
$$x_1 = B_{\text{left}} + c \cdot W_{\text{cell}} - \text{ov}, \quad x_2 = B_{\text{left}} + (c + 1) \cdot W_{\text{cell}} + \text{ov}$$
$$y_1 = B_{\text{top}} + r \cdot H_{\text{cell}} - \text{ov}, \quad y_2 = B_{\text{top}} + (r + 1) \cdot H_{\text{cell}} + \text{ov}$$

**Cualquier otro ángulo ($\theta$).** Las dimensiones de la celda se proyectan sobre los ejes rotados $u$ y $v$, y los 4 vértices de la celda se rotan alrededor del centro $(C_x, C_y)$:
$$P_x = C_x + u \cos \theta - v \sin \theta, \quad P_y = C_y + u \sin \theta + v \cos \theta$$
El resultado es un trazado cerrado de 4 puntos: `\clip(m p1_x p1_y l p2_x p2_y l p3_x p3_y l p4_x p4_y)`.

### Medición de tinta y alineación (`\an1` .. `\an9`)
El nodo comprueba qué devuelve el grafo (`Return` del nodo `Output`) y la alineación `\an` activa, para que el recorte caiga sobre la tinta real:
* **Shape** (ASSdraw, biblioteca de formas o piezas de slicer): se detecta por los comandos vectoriales o por nodos generadores de formas (`Shape/Library`, `Shape/Manipulator`, `Shape/Slicer`, etc.). Se calcula directamente la *bounding box* de tinta de los contornos.
* **Texto:** se mide la tinta real (*glyph ink contour*) de la unidad o línea activa. Si se devuelve un texto personalizado, el nodo lo vectoriza con el motor tipográfico para obtener su tinta exacta.
* **Alineación:** se asume `\an5` salvo que otra alineación venga del widget de alineación de `Output`, de tags del contexto o de propiedades.
  * Con `\an7` (la convención habitual para partículas y piezas rotadas sobre su propio eje), la esquina superior izquierda del recorte queda en `\pos(x, y)` (`left = pos_x`, `top = pos_y`), de modo que encaja sin offsets. Con `\an1` se alinea a la esquina inferior izquierda (`top = pos_y - h`), y análogamente para el resto de posiciones del numpad.

### Uso
* **Degradado multicapa en `MaxLoop`:** usa `MaxLoop` con `Total: 10`, `Clip Gradient` con `Rows: 10` (franjas horizontales) y lleva `Progress (0-1)` a un nodo `Color Gradient (Progress)`. Cada capa recibe su franja y el color interpolado que le corresponde.

### Ejemplo: degradado vertical en 5 franjas
El texto se divide en 5 franjas horizontales con `overlap=0.5`, y cada franja recibe un color interpolado entre magenta (`#FF007F`) y violeta (`#7F00FF`):

```
[Loops/MaxLoop: total=5] ──► j ───────────────────────────────┐
                                                               ▼
[Functions/Clip Gradient: cols=1, rows=5] ──► Progress (0-1) ─► Prog ──► [Functions/Color Gradient]
   out_mode: "\clip", overlap: 0.5                             colors: "#FF007F, #7F00FF"
                                  │                                           │
                                  ▼ Output (\clip)                            ▼ Tags (\1c)
                               Tags In ──────────────────────────────────── Tags In ──► [System/Output]
```

* **$j=1$ (franja superior):** `{\clip(300, 199.5, 450, 208.5)\1c&H7F00FF&}`.
* **$j=3$ (franja intermedia):** `{\clip(300, 215.5, 450, 224.5)\1c&HBF00BF&}`.
* **$j=5$ (franja inferior):** `{\clip(300, 231.5, 450, 240.5)\1c&HFF007F&}`.

El solapamiento de $0.5\text{ px}$ absorbe el redondeo subpíxel de libass y evita las costuras.

---

## 7. Nodo `Functions/IMG to pixels` (Muestreo Ráster a Partículas)

Muestrea un archivo de imagen (PNG, JPG, WEBP, GIF animado) y convierte sus píxeles opacos en partículas vectoriales. Cada partícula lleva el color muestreado `\1c`, el alfa `\alpha`, la posición `\pos(x, y)` y un orden Numpad. Usa aceleración por GPU y una caché global.

![Functions/IMG to pixels](img/img_to_pixels.jpg)

### Entradas
1. **`Image Path` (`image_path`):** ruta absoluta a la imagen o al GIF animado.
2. **`Particle` (`particle_shape`):** forma ASSdraw usada para cada píxel. Si está vacío, se usa un micro-cuadrado proporcional al paso: `m 0 0 l s 0 l s s l 0 s`.
3. **`Frame` (`frame_idx` / `frame`):** fotograma a muestrear en GIFs animados ($1$-based). (Defecto: `"1"`).
4. **`Step` (`step`):** paso de muestreo en píxeles. `1` muestrea todos los píxeles; `2` muestrea 1 píxel de cada bloque de $2 \times 2$, lo que reduce mucho el número de líneas ASS y mantiene la silueta. (Defecto: `2`).
5. **`Alpha` (`alpha_threshold`):** umbral de corte del alfa ($0 \dots 255$). Los píxeles con menos opacidad se descartan como fondo. (Defecto: `128`).
6. **`Scale` (`scale`):** multiplicador de las coordenadas y del tamaño de la imagen. (Defecto: `1.0`).
7. **`Anchor` (`anchor`):** punto de referencia (`center`, `topleft`, `topright`, `bottomleft`, `bottomright`). (Defecto: `"center"`).
8. **`Order` (`order`):** código de ordenamiento 2D (`79`, `97`, `13`, `31`, `71`, `17`, `93`, `39`, `5`, `-5`, `cw`, `ccw`, `rand`). (Defecto: `"79"`).

> [!TIP]
> **Doble clic sobre la tarjeta de previsualización** (miniatura central) para abrir el explorador de archivos del sistema y elegir una imagen (`.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`). Actualiza `image_path` y muestra la textura al instante, sin copiar rutas a mano.

### Salidas
1. **`[1.1] Shp Out`:** código ASSdraw de la partícula activa.
2. **`[1.2] Color Arr`:** el color `&HBBGGRR&` muestreado de la imagen.
3. **`[1.3] \pos Tag`:** la etiqueta `\pos(x, y)`, calculada sumando la posición relativa del píxel al centro del elemento activo.
4. **`[1.4] X Arr`:** coordenada $X$ absoluta en píxeles de pantalla.
5. **`[1.5] Y Arr`:** coordenada $Y$ absoluta en píxeles de pantalla.
6. **`[1.6] Total`:** número de partículas muestreadas ($N$).
7. **`[1.7] Pixels Array`:** lista con todos los píxeles muestreados `[(x, y, r, g, b, alpha), ...]`.

Variables inyectadas en el contexto:
* **`ip_i` / `img_p_i`:** índice de la partícula activa ($1 \dots N$).
* **`ip_n` / `img_p_n` / `total_pixels` / `maxloop`:** total de partículas.
* **`fx_pos_x`, `fx_pos_y`, `x`, `y`:** coordenadas absolutas de la partícula.

### Cómo funciona

```
Imagen Ráster (Pillow / NumPy)          Enjambre Vectorial ASS
┌────────────────────────┐              ┌────────────────────────┐
│  Píxeles con α ≥ 128   │  Muestreo    │  Partículas ASSdraw    │
│  (x % step == 0)       │ ───────────► │  \pos(x, y)            │
│  (y % step == 0)       │   Step = 2   │  \1c&HBBGGRR&          │
└────────────────────────┘              └────────────────────────┘
```

1. **Máscara:** la imagen se carga como una matriz NumPy RGBA de dimensiones $(H, W, 4)$ y se filtra con indexación vectorizada:
   $$\text{Mask} = (\text{Alpha} \ge \text{Threshold}) \land (X \pmod{\text{Step}} = 0) \land (Y \pmod{\text{Step}} = 0)$$
2. **Caché:** las matrices ya procesadas se guardan en memoria indexadas por `(ruta, frame, step, threshold, scale, anchor, order)`, así los bucles de render no vuelven a leer la imagen.
3. **GPU (OpenCL/CUDA):** si el gestor de GPU está activo, la traslación, la escala y el ordenamiento Numpad de las coordenadas se ejecutan en paralelo en la GPU.

### Uso
* **Desintegración de logotipos:** conecta `IMG to pixels` a un `MaxLoop (total_pixels)`, lleva `\pos Tag` a un `Move Tag (Trajectory)` o a un `Tag Oscillator` con retardo escalonado por partícula (`ip_i`), y emite a `Output`. Las partículas salen de su posición original y se dispersan por la pantalla.
* **Rendimiento:** con imágenes de alta resolución (ej. $1920 \times 1080$) usa `Step: 4` o `Step: 6` para mantener entre $500 \dots 2000$ partículas y 60 FPS en el visor WebAssembly.

### Ejemplo: emblema como enjambre de partículas de 2x2
Un PNG local muestreado con `step=2`, umbral alfa $128$ y anclaje centrado:

```
[Functions/IMG to pixels: step=2, anchor=center] ──► Total (N) ──► Total ──► [Loops/MaxLoop]
   image_path: "C:/assets/logo_spark.png"                                         │
      │                                                                           │ j (ip_i)
      ├─► Shp Out (m 0 0 l 2 0...) ───────────────► Shape / Text ◄────────────────┘
      ├─► Color Arr (&HBBGGRR&) ──────────────────► Tags In
      └─► \pos Tag (\pos(x, y)) ──────────────────► Tags In ──► [System/Output]
```

* **Partícula 1 ($x=620, y=340$):** `{\an5\pos(620, 340)\1c&H22AAFF&\1a&H00&\p1}m 0 0 l 2 0 l 2 2 l 0 2`.
* **Partícula 250 ($x=640, y=360$):** `{\an5\pos(640, 360)\1c&HFFFFFF&\1a&H00&\p1}m 0 0 l 2 0 l 2 2 l 0 2`.

Cada micro-cuadrado conserva el color muestreado de la textura. La salida son exactamente $N$ eventos, uno por píxel opaco, sin procesar las zonas transparentes.

---

## 8. Nodo `Functions/Animation` (Animación FBF y Modulación Alfa)

Recorre una lista de formas ASSdraw, glifos o cadenas de texto. Puede cambiar de fotograma uno a uno (*FBF*, fotograma a fotograma) con índices sincronizados, o alternar la visibilidad con bloques `\t` sobre el canal alfa (`\alpha` o `\1a..\4a`) compilados en una sola línea de subtítulo.

![Functions/Animation](img/animation.jpg)

### Modos
1. **`FBF` (*Frame-by-Frame*):** cada iteración del bucle principal (`an_i` o `j`) elige la forma activa de la secuencia. `Shape` emite el trazado vectorial con alineación `{\an7}`.
2. **`Alpha`:** compila ciclos `\t` de visibilidad que alternan la opacidad entre visible (`&H00&`) y transparente (`&HFF&`) en los instantes calculados.

### Entradas
1. **`Frames / Text` (`frames`):** la secuencia de formas o de texto. Acepta:
   * Nombres de primitivas de la biblioteca (ej. `"Circle, Star, Heart"`).
   * Arrays JSON (ej. `["m 0 0 l 10 10", "m 0 0 l 20 20"]`).
   * Listas separadas por comas, punto y coma `;` o saltos de línea `\n`.
   * Texto ordinario (se convierte a vectores de fuente).
   * Referencias a variables del contexto (ej. `Shapes1`, `my_frames`).
2. **`Step ms` (`step_ms`):** duración de cada fotograma en ms. `41.7` equivale aproximadamente a 24 FPS; `33.3` a 30 FPS; `16.6` a 60 FPS. (Defecto: `41.7`).
3. **`Start Time` (`start_time`):** inicio en ms relativos al evento activo (`0` o vacío toma el inicio del efecto `fx.st` / `syl.start_time`).
4. **`End Time` (`end_time`):** fin en ms (`fx.dur` o vacío toma la duración total del efecto).
5. **`Alpha Tag` (`alpha_tag`):** [Modo Alpha] etiqueta de transparencia a modular, o un *dark tag* multicanal: `\alpha`, canales individuales `\1a`, `\2a`, `\3a`, `\4a`, pares `\12a`, `\13a`, `\14a`, `\23a`, `\24a`, `\34a`, tríos `\123a`, `\124a`, `\134a`, `\234a` o los cuatro `\1234a`. Permite conmutar solo algunos canales (por ejemplo, `\13a` modula relleno y borde sin afectar a la sombra `\4a`). (Defecto: `"\alpha"`).
6. **`Variable Prefix` (`var_name`):** prefijo de las variables de bucle inyectadas en el contexto. (Defecto: `"an"`).

### Salidas

En modo FBF:
1. **`[1.1] Shape`:** código ASSdraw del fotograma activo con prefijo `{\an7}` si no contiene tags previos.
2. **`[1.2] Frame`:** número del fotograma actual (entero base 1: $1, 2, \dots, N$).
3. **`[1.3] Frames List`:** lista de todos los trazados procesados.

En modo Alpha:
1. **`[1.1] Shape`:** la forma activa envuelta en sus tags de visibilidad `{\an7\alpha&HFF&\t(...)\p1}...`.
2. **`[1.2] Tags`:** solo la cadena de etiquetas (`\an7\alpha&HFF&\t(...)`), sin el código de dibujo.
3. **`[1.3] Frame`:** número del fotograma actual (base 1).
4. **`[1.4] Frames List`:** lista de todos los trazados.

Variables expuestas en el contexto:
* `{var_name}_i` / `an_i`: índice del fotograma actual ($1 \dots K$).
* `{var_name}_n` / `an_n`: número de fotogramas únicos ($K$).
* `an_total_cycles`: número de ciclos completos de animación dentro de la duración total.

### Cómo funciona
Dados $K$ fotogramas $\{F_0, F_1, \dots, F_{K-1}\}$, un tiempo de cuadro $\Delta t_{\text{frame}} = \text{step\_ms}$ y un intervalo $[t_{\text{start}}, t_{\text{end}}]$ con duración $D = t_{\text{end}} - t_{\text{start}}$:

```
Índice de Cuadro:   F0       F1       F2       F0       F1       F2
Tiempo (ms):     ├───Δt───┼───Δt───┼───Δt───┼───Δt───┼───Δt───┼───Δt───┤
Ciclo:           └─────── Ciclo 1 ──────────┘└─────── Ciclo 2 ──────────┘
```

**Modo FBF.** Para la iteración $j \ge 1$:
$$\text{active\_idx} = (j - 1) \pmod K$$
$$\text{Frame} = \text{active\_idx} + 1$$
Cuadros necesarios para cubrir la duración:
$$N_{\text{total}} = \left\lceil \frac{D}{\Delta t_{\text{frame}}} \right\rceil$$

**Modo Alpha.** Para cada ciclo $k \in [0, N_{\text{ciclos}}]$ y cada fotograma con índice local $i$:
$$t_1 = \Delta t_{\text{frame}} \cdot (K \cdot k + i)$$
$$t_2 = t_1 + 1.0$$
$$t_3 = \Delta t_{\text{frame}} \cdot (K \cdot k + i + 1)$$
$$t_4 = \min(D, t_3 + 1.0)$$
Cada fotograma recibe el par de visibilidad:
$$\backslash\text{t}(t_1, t_2, \text{tag}\&H00\&)\backslash\text{t}(t_3, t_4, \text{tag}\&HFF\&)$$

### Uso
* **GIFs y spritesheets:** conecta `Shapes Array` de `Shape/IMG to Shape` a `Frames / Text` para reproducir cuadro a cuadro las animaciones extraídas de un GIF.
* **`Loops/MaxLoop (fbf)`:** configura `MaxLoop` en modo `fbf` y itera exactamente los cuadros que necesita la duración de la línea de karaoke.

### Ejemplo: ciclo de formas vectoriales a 24 FPS
Ciclo de `circle`, `star`, `heart` a 24 FPS ($41.7\text{ ms}$ por cuadro):

```
[Loops/MaxLoop: mode=fbf, step_ms=41.7] ──► j ────────────────────────┐
                                                                       ▼
[Functions/Animation: mode=FBF, step_ms=41.7] ──► Shape ──► Shape / Text ──► [System/Output]
   frames: "circle, star, heart"
```

* **$j=1$:** `{\an7}m 50 0 b 22 0 0 22 0 50 ...` (círculo de la biblioteca).
* **$j=2$:** `{\an7}m 38 36 l 0 36 l 31 59 ...` (estrella).
* **$j=3$:** `{\an7}m 50 25 b 50 10 35 0 20 0 ...` (corazón).
* **$j=4$:** vuelve al fotograma $1$ y sigue repitiéndose mientras dure el subtítulo.

---

## 9. Nodo `Functions/Bezier Curve` (Curvas y Splines Bézier 2D)

Genera, evalúa e interpola curvas de Bézier 2D. Usa el algoritmo de De Casteljau para curvas cuadráticas, cúbicas y de grado $N$. También ofrece velocidad constante mediante integración numérica de la longitud de arco, extracción de tangentes y normales, subdivisión de curvas y trayectorias aleatorias suaves.

![Functions/Bezier Curve](img/bezier_curve.jpg)

### Modos
1. **`Cubic 2D`:** curva Bézier cúbica de 4 puntos de control ($P_0, P_1, P_2, P_3$).
2. **`Quadratic 2D`:** curva Bézier cuadrática de 3 puntos de control ($P_0, P_1, P_2$).
3. **`N-Degree`:** curva de grado $N$ definida por la lista de `Points` ($P_0, P_1, \dots, P_N$).
4. **`Constant Speed`:** mapeo de $t \in [0.0, 1.0]$ corregido por longitud de arco con la regla de Simpson, para velocidad uniforme en píxeles/segundo.
5. **`Shape Contour`:** muestrea paramétricamente un trazado ASSdraw conectado a `Shape`.
6. **`Subdivide`:** divide la curva en el parámetro $t$ en dos splines independientes (`Spline L` y `Spline R`).
7. **`Trajectory`:** genera trayectorias aleatorias suaves con splines cúbicos encadenados (`Free Wander`, `Bounded`, `Closed Loop`).

### Entradas
1. **`Origin` (`origin`):** coordenada $(X_0, Y_0)$ que se suma como desplazamiento a todos los puntos de control. (Defecto: `"0,0"`).
2. **`P0, P1, P2, P3` (`p0`, `p1`, `p2`, `p3`):** coordenadas $(X, Y)$ de los puntos de control. Acepta tuplas separadas por comas o espacios, o cables.
3. **`t` (`t`):** parámetro de evaluación $t \in [0.0, 1.0]$. Acepta variables de contexto como `j / maxloop` o `char.i / char.n`. (Defecto: `"0.5"`).
4. **`Subdivs` (`subdivs`):** número de segmentos para el muestreo de contornos y el cálculo de longitud de arco. (Defecto: `"100"`).
5. **`Shape` (`shape`):** trazado ASSdraw para los modos `Shape Contour` y `Trajectory`.
6. **`Points` (`points`):** puntos de control para el modo `N-Degree` (ej. `"0,0; 50,100; 150,100; 200,0"`).
7. **`Trajectory Mode` (`traj_mode`):** tipo de trayectoria (`"Free Wander"`, `"Bounded"`, `"Closed Loop"`).
8. **`Dist Range` (`dist_range`):** distancia mínima y máxima entre nodos aleatorios (ej. `"50,120"`).
9. **`Seed` (`seed`):** semilla pseudoaleatoria para el modo `Trajectory`. (Defecto: `"1"`).
10. **`Loops` (`loops`):** número de segmentos cúbicos encadenados en la trayectoria. (Defecto: `"8"`).

### Salidas
1. **`[1.1] \pos`:** la etiqueta `\pos(X, Y)` en el punto $t$.
2. **`[1.2] X`:** coordenada horizontal $X(t)$ (entero o float a 2 decimales).
3. **`[1.3] Y`:** coordenada vertical $Y(t)$.
4. **`[1.4] Tan`:** ángulo de la tangente $\theta \in [0^\circ, 360^\circ)$ en grados, útil para `\frz`.
5. **`[1.5] Norm`:** ángulo de la normal perpendicular $(\theta + 90^\circ) \pmod{360^\circ}$.
6. **`[1.6] Spline`:** trazado ASSdraw completo de la curva (ej. `m X0 Y0 b X1 Y1 X2 Y2 X3 Y3`).
7. **`[1.7] Spline L`:** [Modo Subdivide] trazado ASSdraw del segmento izquierdo $[0.0, t]$.
8. **`[1.8] Spline R`:** [Modo Subdivide] trazado ASSdraw del segmento derecho $[t, 1.0]$.

### Matemáticas

```
P1 (50, 100)                     P2 (150, 100)
    ●───────────────────────────────●
   /                                 \
  /           B(t) (X, Y)             \
 /                 ● ───> Tangente     \
●                  │                    ●
P0 (0, 0)          ▼ Normal             P3 (200, 0)
```

**Algoritmo de De Casteljau (grado $N$).** Dados $n+1$ puntos de control $\{P_0, P_1, \dots, P_n\}$ con $P_i \in \mathbb{R}^2$:
$$P_i^{(0)} = P_i \quad \forall i \in \{0, \dots, n\}$$
$$P_i^{(r)} = (1 - t) P_i^{(r-1)} + t P_{i+1}^{(r-1)} \quad \forall r \in \{1, \dots, n\}, \, i \in \{0, \dots, n-r\}$$
El punto de la curva es $B(t) = P_0^{(n)}$.

Para una curva cúbica ($n=3$):
$$B(t) = (1-t)^3 P_0 + 3(1-t)^2 t P_1 + 3(1-t) t^2 P_2 + t^3 P_3$$

**Derivada, tangente y normal.** La primera derivada $B'(t) = (dx/dt, dy/dt)$ de una curva de grado $n$ es una curva Bézier de grado $n-1$:
$$B'(t) = n \sum_{i=0}^{n-1} (P_{i+1} - P_i) \cdot b_{i, n-1}(t)$$
A partir del vector velocidad $(dx, dy)$:
$$\theta_{\text{tan}} = \left( \operatorname{atan2}(dy, dx) \cdot \frac{180}{\pi} + 360^\circ \right) \pmod{360^\circ}$$
$$\theta_{\text{norm}} = (\theta_{\text{tan}} + 90^\circ) \pmod{360^\circ}$$

**Corrección por longitud de arco (velocidad constante).** La longitud acumulada $s(t)$ se calcula integrando la norma de la velocidad con la regla compuesta de Simpson:
$$s(t) = \int_0^t \sqrt{\left(\frac{dx}{du}\right)^2 + \left(\frac{dy}{du}\right)^2} \, du$$
Para evaluar en la distancia objetivo $s_{\text{target}} = t \cdot s(1.0)$, se resuelve $s(t^*) = s_{\text{target}}$ por bisección numérica hasta converger ($\epsilon < 10^{-5}$).

**Subdivisión.** En el parámetro $t$, los puntos intermedios de la pirámide de De Casteljau son los nuevos polígonos de control:
* **Segmento izquierdo ($[0, t]$):** $\{P_0^{(0)}, P_0^{(1)}, P_0^{(2)}, \dots, P_0^{(n)}\}$.
* **Segmento derecho ($[t, 1]$):** $\{P_0^{(n)}, P_1^{(n-1)}, P_2^{(n-2)}, \dots, P_n^{(0)}\}$.

### Uso
* **Partículas orientadas automáticamente:** lleva `\pos` a la posición del objeto y `Tan` a la entrada `Angle` de un `MultiTag` o directamente a `\frz`, para que los elementos giren siguiendo el sentido de avance de la trayectoria.
* **Escritura animada con `Shape/Walker`:** conecta `Spline` a la entrada `Path` de un `Shape/Walker` para trazar la curva en pantalla de forma progresiva.

### Ejemplo: punto y orientación sobre un spline cúbico
Cuatro puntos de control $P_0(100, 300), P_1(200, 100), P_2(400, 100), P_3(500, 300)$ evaluados en $t=0.5$:

```
[Functions/Bezier Curve: mode=cubic_2d, t=0.5] ──► \pos ──────┐
   p0: "100,300", p1: "200,100", p2: "400,100", p3: "500,300" │
                                         └──► Tan ───┐        ▼
                                                     └──► Tags In ──► [System/Output]
                                                                      Return: "m 0 0 l 20 0 l 20 20 l 0 20"
```

* **Punto en $t=0.5$:**
  $$B(0.5) = (1-0.5)^3 P_0 + 3(1-0.5)^2(0.5) P_1 + 3(1-0.5)(0.5)^2 P_2 + 0.5^3 P_3$$
  $$B(0.5) = 0.125(100, 300) + 0.375(200, 100) + 0.375(400, 100) + 0.125(500, 300) = (300.0, 150.0)$$
* **Tangente en el vértice superior:**
  $$B'(0.5) = 3(0.25)(P_1 - P_0) + 6(0.25)(P_2 - P_1) + 3(0.25)(P_3 - P_2) = (450.0, 0.0) \implies \theta = 0^\circ$$
* **Línea ASS resultante:**
  `Dialogue: 0,0:00:01.00,0:00:03.00,Default,,0,0,0,,{\an5\pos(300,150)\frz0\p1}m 0 0 l 20 0 l 20 20 l 0 20{\p0}`

---

## 10. Nodo `Functions/Move Tag` (Cinemática y Trayectorias de Movimiento ASS)

Genera bloques de movimiento ASS (`\pos`, `\fscx`, `\fscy`, `\t`) a partir de trazados vectoriales, waypoints cartesianos o fluctuaciones aleatorias (*jitter*). Re-muestrea la trayectoria con un paso uniforme (`step_px`), aplica una curva de aceleración no lineal y reposiciona el sistema de anclaje.

![Functions/Move Tag](img/move_tag.jpg)

### Modos
1. **`Trajectory` (`SMOVE`):** toma un trazado ASSdraw (`Shape`), calcula su longitud total y la divide en segmentos de longitud máxima `step_px`, para un movimiento continuo y suave.
2. **`Waypoints` (`PMOVE`):** toma puntos cartesianos discretos (`Points` o `Shape`) y genera transiciones lineales o interpoladas entre ellos.
3. **`Jitter` (`RMOVE`):** genera una fluctuación pseudoaleatoria dentro de $(\pm \Delta X, \pm \Delta Y)$ a intervalos regulares (`dur` ms), reproducible con semilla (`seed`).

### Entradas
1. **`Tags` (`tags`):** etiquetas ASS adicionales que se añaden al bloque final (ej. `\1c&HFFFFFF&\blur2`).
2. **`Shape (d)` (`shape`):** trazado ASSdraw que define la ruta (ej. `"m 0 0 b 50 100 150 100 200 0"`).
3. **`Step (px)` (`step_px`):** distancia máxima en píxeles entre dos muestras consecutivas. Valores más pequeños dan más suavidad pero generan más tags `\t`. (Defecto: `7.5`).
4. **`Anchor` (`anchor`):** modo de centrado:
   * `"center"`: centra la trayectoria en el punto medio de su caja delimitadora $(B_{\text{center}} = (0, 0))$.
   * `"origin"` / `"first_point"`: fija el punto inicial del trazado en $(0, 0)$.
5. **`Start Time (t1)` (`t1`):** inicio del movimiento en ms. (Defecto: `0`).
6. **`End Time (t2)` (`t2`):** fin del movimiento en ms. (Defecto: `"fx.dur"`).
7. **`Acceleration` (`accel`):** exponente de aceleración. $1.0 = \text{lineal}$; $> 1.0 = \text{acelerado (ease-in)}$; $< 1.0 = \text{desacelerado (ease-out)}$. (Defecto: `1.0`).

### Salidas
1. **`[1.1] Data`:** la cadena de etiquetas ASS terminada:
   $$\backslash\text{an7}\backslash\text{q2}\backslash\text{pos}(X_0, Y_0)\backslash\text{fscx}P_{x0}\backslash\text{fscy}P_{y0}\backslash\text{t}(t_{s1}, t_{e1}, \backslash\text{fscx}P_{x1}\backslash\text{fscy}P_{y1})\dots\backslash\text{p1}\}m\dots\{\backslash\text{p0}$$

### Cómo funciona

```
Ruta Vectorial:   P0 (0,0) ─────── P1 (7.5px) ─────── P2 (15px) ─────── P3 (22.5px)
Tiempo Mapeado:   t1               st1 ─── et1        st2 ─── et2       t2
Progreso Normal:  0.0              (d1/D)^accel       (d2/D)^accel      1.0
```

Dados $M$ puntos muestreados $\{P_0, P_1, \dots, P_{M-1}\}$ con distancias acumuladas $d_k$ y distancia total $D = d_{M-1}$:
1. Para cada segmento $k \in [1, M-1]$:
   $$\tau_1 = \left(\frac{d_{k-1}}{D}\right)^{\text{accel}}, \quad \tau_2 = \left(\frac{d_k}{D}\right)^{\text{accel}}$$
   $$s_t = \text{round}(t_1 + (t_2 - t_1) \cdot \tau_1)$$
   $$e_t = \text{round}(t_1 + (t_2 - t_1) \cdot \tau_2)$$
2. Se escribe la transición:
   $$\backslash\text{t}(s_t, e_t, \backslash\text{fscx}P_{x,k}\backslash\text{fscy}P_{y,k})$$

### Uso
* **Seguir una curva:** conecta `Spline` de un `Bezier Curve` a `Shape (d)` para mover sílabas o glifos a lo largo de un spline Bézier con control de aceleración.

### Ejemplo: aceleración cuadrática en una ruta de 3 puntos
Una ruta de $300\text{ ms}$ con aceleración cuadrática ($\text{accel}=2.0$) de $(100, 200)$ a $(250, 250)$, muestreada cada $50\text{ px}$:

```
[Functions/Move Tag: mode=trajectory, step_px=50, accel=2.0, t1=0, t2=300]
   shape: "m 100 200 l 170 200 l 250 250" ──► Data ──► Tags In ──► [System/Output]
                                                                   Return: "Texto"
```

* **Muestreo ($\Delta t = 300\text{ ms}$, $D = 164.34\text{ px}$):**
  * Segmento 0 ($d_0 = 0.0$): $\tau_0 = 0.0 \to t = 0\text{ ms}$, posición $(100.0, 200.0)$.
  * Segmento 1 ($d_1 = 70.0$): $\tau_1 = (70.0 / 164.34)^2 \approx 0.181 \to s_{t1} = 54\text{ ms}$, posición $(170.0, 200.0)$.
  * Segmento 2 ($d_2 = 164.34$): $\tau_2 = 1.0 \to s_{t2} = 300\text{ ms}$, posición $(250.0, 250.0)$.
* **Bloque de tags emitido:**
  `{\an7\q2\pos(100.00,200.00)\fscx100.00\fscy100.00\t(0,54,2.00,\fscx170.00\fscy200.00)\t(54,300,2.00,\fscx250.00\fscy250.00)\p1}m 0 0 m 100 100 {\p0}Texto`

---

## 11. Nodo `Functions/Move Text` (Movimiento Cinemático Tipográfico Coordinado)

Mueve texto sin romper el layout del párrafo ni alterar la métrica de la fuente. Compensa en dos ejes: el espaciado de fuente (`\fsp`) para X y la escala vertical (`\fscy`) para Y, con el texto encerrado entre puntos de anclaje invisibles.

![Functions/Move Text](img/move_text.jpg)

### Entradas
1. **`Text` (`text`):** cadena de texto o dibujo ASSdraw. Si está vacío, toma el texto de la sílaba o carácter activo.
2. **`Delta X` (`dx`):** desplazamiento total en el eje X (px).
3. **`Delta Y` (`dy`):** desplazamiento total en el eje Y (px).
4. **`Offset X` (`ox`):** desfase inicial fijo en el eje X (px).
5. **`Offset Y` (`oy`):** desfase inicial fijo en el eje Y (px).
6. **`Shape (d)` (`shape` / `trajectory`):** trazado ASSdraw opcional que sustituye a $\Delta X, \Delta Y$ para trayectorias curvas.
7. **`Points` (`points`):** lista de puntos de control de la ruta.
8. **`Step (px)` (`step_px`):** paso de re-muestreo para trazados vectoriales. (Defecto: `7.5`).
9. **`Start Time (t1)` (`t1`):** inicio del movimiento (ms). (Defecto: `0`).
10. **`End Time (t2)` (`t2`):** fin del movimiento (ms). (Defecto: `"fx.dur"`).
11. **`Acceleration` (`accel`):** exponente de aceleración. (Defecto: `1.0`).

### Salidas
1. **`[1.1] Text`:** la estructura de texto ASS con los bloques de compensación horizontal y vertical:
   $$\text{Block}_{V1} \cdot \text{Block}_{H1} \cdot \{\backslash\text{r}\text{tags}\backslash\text{q2}\}\text{Texto} \cdot \text{Block}_{H2} \cdot \text{Block}_{V2}$$

### Cómo funciona

```
Estructura Generada:
[ Salto \N Compensador Y1 ]
[ Punto '.' Oculto con \fspX1 ] ─── [ TEXTO PRINCIPAL ] ─── [ Punto '.' Oculto con \fspX2 ]
[ Salto \N Compensador Y2 ]
```

El texto se mueve sin afectar a los caracteres vecinos y sin usar `\pos` en coordenadas de pantalla:
1. **Eje horizontal ($X$):** se colocan dos puntos `.` transparentes (`\alpha&HFF&`) a cada lado del texto. Animar `\fsp` con valores duplicados $2 \cdot \Delta X$ desplaza el texto a izquierda o derecha y mantiene constante el ancho de la línea.
2. **Eje vertical ($Y$):** saltos de línea forzados `\N` con micro-dibujos escalados con `\fscy` desplazan la línea activa hacia arriba o abajo sin alterar la línea de base global.

### Uso
* **Entradas suaves:** `Delta Y = -30` y `Accel = 2.0` en la fase `presyl` hacen que cada sílaba baje flotando hasta la línea de base cuando se canta.

### Ejemplo: entrada de sílaba desde arriba
Una caída vertical de $25\text{ px}$ durante los primeros $250\text{ ms}$ de la sílaba:

```
[Variables/Sys Var: var_name=syl.text] ──► Text ─────────────────┐
                                                                 ▼
[Functions/Move Text: dy=-25, t1=0, t2=250, accel=1.5] ──► Text ──► Return ──► [System/Output]
```

El nodo mide el ancho del glifo de anclaje `.` ($w_{\text{dot}} = 7.5\text{ px}$), coloca el texto de la sílaba entre dos caracteres invisibles con `\alpha&HFF&` y compensa el eje vertical con un bloque `\fscy` escalado, precedido de un salto de línea forzado `\N`.

Línea generada:
`Dialogue: 0,0:00:01.00,0:00:03.00,Default,,0,0,0,,{\p0\alpha&HFF&.}{\fscy100\t(0,250,1.5,\fscy0)\p1}m 0 0 l 1 0 l 1 25 l 0 25{\p0}\N{\r\q2}Ka{\p0\alpha&HFF&.}`

---

## 12. Nodo `Functions/Polar to Cartesian` (Conversor Polar a Cartesiano)

Convierte un radio $r$ y un ángulo $\theta$ en coordenadas cartesianas $(X, Y)$ relativas a un origen $(X_0, Y_0)$. Emite una etiqueta `\pos(X, Y)` y los componentes numéricos.

![Functions/Polar to Cartesian](img/polar_to_certesian.jpg)

### Entradas
1. **`Origin X` (`x`):** coordenada $X_0$ del origen. Acepta constantes o expresiones de contexto como `syl.x`, `line.x`, `char.x`. (Defecto: `"0"`).
2. **`Origin Y` (`y`):** coordenada $Y_0$ del origen (ej. `syl.y`, `line.y`). (Defecto: `"0"`).
3. **`Angle (°)` (`angle`):** ángulo $\theta$ en grados ($0^\circ \dots 360^\circ$). $0^\circ$ apunta en la dirección positiva de X (derecha); $90^\circ$ en la positiva de Y (abajo en el sistema ASS). (Defecto: `"0"`).
4. **`Radius` (`radius`):** radio $r$ en píxeles. (Defecto: `"100"`).

### Salidas
1. **`[1.1] \pos Tag`:** la etiqueta `\pos(X, Y)`.
2. **`[1.2] X`:** coordenada absoluta $X = X_0 + \Delta X$.
3. **`[1.3] Y`:** coordenada absoluta $Y = Y_0 + \Delta Y$.
4. **`[1.4] dX`:** desplazamiento horizontal relativo $\Delta X = r \cos(\theta)$.
5. **`[1.5] dY`:** desplazamiento vertical relativo $\Delta Y = r \sin(\theta)$.

### Matemáticas

```
               (X0, Y0)
                  ● ─────────────> Eje X (θ = 0°)
                  │ \
                  │  \  Radio (r)
                  │   \
                  │ θ  \
                  ▼     ● (X, Y)
                Eje Y
```

El ángulo en grados $\theta$ se convierte a radianes:
$$\theta_{\text{rad}} = \theta \cdot \frac{\pi}{180}$$

Desplazamientos y coordenadas absolutas:
$$\Delta X = r \cdot \cos(\theta_{\text{rad}})$$
$$\Delta Y = r \cdot \sin(\theta_{\text{rad}})$$
$$X = X_0 + \Delta X$$
$$Y = Y_0 + \Delta Y$$

Los valores se escriben como enteros si no tienen parte fraccionaria, o redondeados a 2 decimales para no engordar el script ASS.

### Uso
* **Ráfagas radiales:** conecta un iterador como `Basics/MultiRandom`, o la expresión `j * (360 / maxloop)`, a `Angle (°)`, fija `Radius: 80` y lleva `\pos Tag` a `System/Output` para obtener anillos de partículas al instante.
* **Espirales hacia dentro:** modula `Angle (°)` con `Time/Ipol` y reduce `Radius` con el tiempo para obtener trayectorias espirales convergentes hacia el centro del texto.

### Ejemplo: anillo de 8 partículas alrededor de una sílaba
8 elementos separados $45^\circ$ a un radio de $60\text{ px}$ del centro de la sílaba:

```
[Loops/MaxLoop: total=8] ──► j ──► Angle: (j - 1) * 45 ────────┐
                                                               ▼
[Shape/Library: "Star"] ──► Shape ──► Shape / Text ──► [Functions/Polar to Cartesian: radius=60]
                                                          Origin X: syl.x, Origin Y: syl.y
                                                               │
                                                               ▼ \pos Tag (\pos(X, Y))
                                                            Tags In ──► [System/Output]
```

Suponiendo `syl.x = 320, syl.y = 240`:
* **$j=1$ ($\theta = 0^\circ$):** $\Delta X = 60, \Delta Y = 0 \to$ `{\an5\pos(380, 240)\p1}m 0 0 ...` (derecha).
* **$j=3$ ($\theta = 90^\circ$):** $\Delta X = 0, \Delta Y = 60 \to$ `{\an5\pos(320, 300)\p1}m 0 0 ...` (abajo).
* **$j=5$ ($\theta = 180^\circ$):** $\Delta X = -60, \Delta Y = 0 \to$ `{\an5\pos(260, 240)\p1}m 0 0 ...` (izquierda).
* **$j=7$ ($\theta = 270^\circ$):** $\Delta X = 0, \Delta Y = -60 \to$ `{\an5\pos(320, 180)\p1}m 0 0 ...` (arriba).

---

## 13. Nodo `Functions/Particles` (Enjambres de Partículas Vectoriales)

Muestrea los contornos o el interior de texto o formas ASSdraw para generar un enjambre de partículas. Cada punto muestreado puede sustituirse por una forma vectorial propia, ordenarse con notación Numpad y desplazarse aleatoriamente (*jitter*).

![Functions/Particles](img/particles.jpg)

### Modos
1. **`Outline` (`outline_v2` / `border`):** muestrea puntos equidistantes a lo largo del contorno.
2. **`Inner Fill` (`inner_fill` / `relleno`):** genera una cuadrícula regular de puntos dentro de la forma, comprobando la inclusión con ray-casting (paridad impar de cruces).

### Entradas
1. **`Path / Origin` (`shape`):** trazado ASSdraw base (`m ...`) o nombre de primitiva. Si está vacío o se pasa texto plano, Pyxis extrae el contorno del glifo del contexto activo (`syl` o `char`).
2. **`Particle` (`particle_shape`):** forma vectorial de cada partícula (ej. `"Circle"`, `"Star"`, `"Heart"` o ASSdraw directo). Si está vacío, un cuadrado de $2 \times 2$ px (`m 0 0 l 2 0 l 2 2 l 0 2`).
3. **`Density` (`density`):** paso de muestreo en píxeles. En modo `Outline` es la distancia entre partículas a lo largo del trazo; en `Inner Fill` es la separación de la cuadrícula. (Defecto: `5.0`).
4. **`RedrawDist` (`redraw_dist`):** rango de desplazamiento aleatorio uniforme $(\pm \Delta x, \pm \Delta y)$ en píxeles aplicado a cada partícula. (Defecto: `0.0`).
5. **`Seed` (`seed`):** semilla del desplazamiento aleatorio. (Defecto: `1`).
6. **`Scale` (`scale`):** multiplicador de las coordenadas del enjambre. (Defecto: `1.0`).
7. **`Anchor` (`anchor`):** botón cíclico con el mismo perfil *Piece Anchor* que los nodos de fragmentación (`Slicer`, `Array`, `Union & Divide`). Determina cómo se proyectan las coordenadas locales de cada partícula y el centro de rotación `\org` sobre el lienzo del subtítulo:
   * **`pieces` (por defecto):** cada partícula se coloca en sus propias coordenadas `\pos(x, y)` calculadas desde el centroide de su glifo o contorno, con `\org(x, y)` en su propio centro. Así, las transformaciones posteriores (giros `\frz`, escalados `\fscx/\fscy`, deformaciones angulares) rotan cada partícula sobre su propio eje.
   * **`relative`:** conserva las coordenadas relativas al centroide del texto o forma padre, sin sobreescribir `pos_overridden`.
   * **`parent_org`:** coloca la partícula en sus coordenadas absolutas `\pos(x, y)` pero ancla `\org` en el origen del texto o línea padre (`parent_x, parent_y`), para giros orbitales alrededor del elemento de origen.
   * **`pos`:** coloca la partícula en sus coordenadas absolutas `\pos(x, y)` sin forzar un `\org` explícito (`has_org = False`).
   * **`absolute`:** escribe las coordenadas absolutas directamente en los vértices del trazado (`m x y ...`), deja `\pos` en el origen padre y desactiva `pos_overridden`.
8. **`Order` (`order`):** botón cíclico de ordenamiento 2D (*Numpad Order*), que determina el índice `p_i`:
   * `"79"`: Arriba-Izquierda $\to$ Abajo-Derecha (*Top-Left to Bottom-Right*).
   * `"97"`: Arriba-Derecha $\to$ Abajo-Izquierda (*Top-Right to Bottom-Left*).
   * `"13"`: Abajo-Izquierda $\to$ Arriba-Derecha (*Bottom-Left to Top-Right*).
   * `"31"`: Abajo-Derecha $\to$ Arriba-Izquierda (*Bottom-Right to Top-Left*).
   * `"71"`: columna izquierda, de arriba abajo.
   * `"17"`: columna izquierda, de abajo arriba.
   * `"93"`: columna derecha, de arriba abajo.
   * `"39"`: columna derecha, de abajo arriba.
   * `"5"`: del centro hacia fuera (*Inside-Out*).
   * `"-5"`: de fuera hacia el centro (*Outside-In*).
   * `"cw"`: sentido horario (*Clockwise*).
   * `"ccw"`: sentido antihorario (*Counter-Clockwise*).
   * `"rand"`: desorden pseudoaleatorio (*Shuffle*).
   * `"path"`: **a lo largo del contorno.** Conserva el orden de arco en que se calculan los vértices del contorno ($s \in [0, L]$). Funciona como un *Walker* integrado: las cascadas de tags, apariciones y desvanecimientos siguen el trazo caligráfico o la silueta original.
   * `"path_inv"`: **contorno en sentido inverso** ($s \in [L, 0]$).

### Salidas
1. **`[1.1] Shp Out`:** etiqueta de posición y partícula juntas: `{\pos(X, Y)}forma_particula`.
2. **`[1.2] \pos Tag`:** la etiqueta `\pos(X, Y)`.
3. **`[1.3] X Arr`:** coordenada horizontal $X$ de la partícula activa (px).
4. **`[1.4] Y Arr`:** coordenada vertical $Y$ de la partícula activa (px).
5. **`[1.5] Total`:** número total $N$ de partículas del enjambre.

Variables inyectadas en el contexto:
* `p_i` / `tp_i`: índice de la partícula actual ($1 \dots N$).
* `p_n` / `tp_n` / `maxloop`: número total de partículas ($N$).
* `x, y` / `fx_pos_x, fx_pos_y`: coordenadas absolutas de la partícula activa.

### Cómo funciona

```
Modo Outline (Perímetro):            Modo Inner Fill (Ray-Casting):
      ● ─── ● ─── ●                        ●   ●   ●   ●   ● (Fuera)
     /             \                     ┌───────────────────┐
    ●               ●                    │   ●   ●   ●   ●   │ (Dentro: Cruces = 1)
     \             /                     │   ●   ●   ●   ●   │
      ● ─── ● ─── ●                      └───────────────────┘
```

**Outline (longitud de arco).** Para cada contorno cerrado $C = \{V_0, V_1, \dots, V_m, V_0\}$:
1. Se calcula la longitud de cada segmento:
   $$d_k = \|V_{k+1} - V_k\|, \quad D_{\text{total}} = \sum_{k=0}^m d_k$$
2. Se generan objetivos equidistantes $s_j = j \cdot \text{density}$ para $j \in \left[0, \lfloor D_{\text{total}} / \text{density} \rfloor \right]$.
3. Cada objetivo se interpola en su segmento y se perturba aleatoriamente si $\text{RedrawDist} > 0$:
   $$P_j = P_{\text{interp}} + \begin{pmatrix} U(-\text{redraw\_dist}, \text{redraw\_dist}) \\ U(-\text{redraw\_dist}, \text{redraw\_dist}) \end{pmatrix} \cdot \text{scale}$$

**Inner Fill (ray-casting).**
1. Se toma la caja delimitadora $(X_{\min}, Y_{\min}) \to (X_{\max}, Y_{\max})$ de todos los contornos.
2. Se genera una cuadrícula uniforme con paso $\Delta = \text{density}$.
3. Para cada nodo $(g_x, g_y)$, se lanza un rayo hacia $+X$ y se cuentan las intersecciones con los bordes de los polígonos:
   $$\text{inside} = \left(\sum \text{intersecciones}(g_x, g_y, \text{Bordes})\right) \pmod 2 \equiv 1$$
   Si el punto es interior, se añade al enjambre.

### Uso
* **Disolución de texto en partículas:** conecta `Functions/Particles` a un `Loops/MaxLoop` que itere $N$ veces (`p_n`) y anima la dispersión con `Time/Ipol` o `Functions/Polar to Cartesian` hacia direcciones divergentes.
* **Escritura caligráfica (Walker integrado):** con `order="path"` las partículas no se reordenan en bandas cartesianas ni radiales, sino que se indexan a lo largo del contorno ($s = 0 \to L$). Si modulas la aparición con una fórmula en `Tags` (ej. `\alpha!by.p_i.ipol(0, 255, 0, fx.dur)!` o `\t((p_i/p_n)*syl.dur, ((p_i+1)/p_n)*syl.dur, \alpha&H00&)`), cada micro-partícula se ilumina en secuencia siguiendo la silueta del glifo, sin necesitar un nodo `Shape/Walker`.

### Ejemplo: ráfaga de partículas desde el contorno de un glifo
El contorno de un glifo muestreado cada $8\text{ px}$, cada punto sustituido por una micro-estrella y ordenado del centro hacia fuera (orden `"5"`):

```
[Shape/Library: "Star"] ──► Particle ────────────────────────────┐
                                                                 ▼
[Functions/Particles: mode=outline_v2, density=8.0, order="5"] ──► Shp Out ──► Return ──► [System/Output]
   Path / Origin: syl.shape
```

El motor detecta `Particles` en la cadena de `Output.Return`, extrae $N=24$ puntos del perímetro del glifo, inyecta las variables `p_i` ($1 \dots 24$) y `p_n` ($24$), y ordena las coordenadas radialmente según su distancia al centroide del carácter.

Línea de la primera partícula ($p_i=1$, la más cercana al baricentro):
`Dialogue: 0,0:00:01.00,0:00:03.00,Default,,0,0,0,,{\an5\pos(320.50,238.20)\p1}m 0 0 l 2 0 l 2 2 l 0 2{\p0}`

---

## 14. Nodo `Functions/Interpolator` (Interpolador Paramétrico Polimórfico)

Interpola entre dos o más valores ($V_1 \to V_2$) y se adapta al tipo de dato: números, colores (Hex o ASS), alfa, bloques de etiquetas ASS o formas vectoriales completas (*morphing* con re-muestreo).

![Functions/Interpolator](img/interpolador.jpg)

### Entradas
1. **`Iterator` (`iterator`):** índice de iteración o valor de progreso actual. Acepta:
   * Nombres de iteradores de contexto (ej. `"i"`, `"j"`, `"char.i"`, `"syl.i"`, `"a_i"`).
   * Un progreso normalizado $t \in [0.0, 1.0]$.
2. **`Total` (`total`):** número de pasos para normalizar el iterador ($N$). Acepta `"N"`, `"maxloop"`, `"char.n"`, `"syl.n"`. (Defecto: `"N"`).
3. **`Accel` (`accel`):** exponente de aceleración / relajación (*easing*). `1.0` es lineal; $> 1.0$ acelera al final (*ease-in*); $< 1.0$ desacelera (*ease-out*). (Defecto: `"1.0"`).
4. **`V1` (`v1`):** valor en $t=0.0$. Acepta números, colores (`#FF0000`, `&H0000FF&`), tags (`\blur0\fscx100`) o formas ASSdraw (`m 0 0 l 50 0...`).
5. **`V2` (`v2`):** valor en $t=1.0$. También admite cadenas multi-parada separadas por coma o arrays JSON para transiciones de varios tramos ($V_1 \to V_2 \to V_3 \dots$).

### Salidas
1. **`[1.1] Data`:** el valor interpolado para el progreso $t$ actual.
2. **`[1.2] Batch / List`:** lista de los $N$ valores interpolados separados por comas, para asignaciones en lote.

### Cómo funciona

```
Progreso Normalizado:   t = (Iterator - 1) / (Total - 1)   ───>   t_eased = t^Accel
                                                                      │
              ┌───────────────────┬───────────────────┬───────────────┴───────────────┐
              ▼                   ▼                   ▼                               ▼
       [ Escalares ]        [ Colores ]         [ Tags ASS ]                 [ ASSdraw (Morphing) ]
      V1 + (V2-V1)·t       RGB Interpolado    Keyframes Mezclados           Re-muestreo Equidistante
```

**Normalización y easing.** Con el iterador $i$ y el total $N$:
$$t = \begin{cases} i & \text{si } 0.0 \le i \le 1.0 \text{ y } N=1 \\ \frac{i - 1}{N - 1} & \text{si } N > 1 \\ 0.0 & \text{en otro caso} \end{cases}$$
$$t_{\text{eased}} = \begin{cases} t^{\text{accel}} & \text{si } \text{accel} > 1.0 \\ 1.0 - (1.0 - t)^{1.0 / \text{accel}} & \text{si } 0.0 < \text{accel} < 1.0 \\ t & \text{si } \text{accel} = 1.0 \end{cases}$$

**Según el tipo de dato:**
1. **Formas ASSdraw (*morphing*):**
   * Se extraen los contornos de ambas formas con Clipper2.
   * Se re-muestrean a la misma cantidad de vértices $M = \max(|C_1|, |C_2|, 30)$, distribuidos uniformemente por longitud de arco.
   * Cada par de vértices homólogos se interpola linealmente:
     $$P_k(t) = (1 - t_{\text{eased}}) \cdot P_{1,k} + t_{\text{eased}} \cdot P_{2,k}$$
   * Se reconstruye el trazado ASSdraw.
2. **Colores Hex / ASS:** los canales $(R_1, G_1, B_1)$ y $(R_2, G_2, B_2)$ se interpolan linealmente en RGB.
3. **Bloques de etiquetas ASS (*keyframing*):** las etiquetas numéricas (`\fscx`, `\fscy`, `\frz`, `\alpha`, `\blur`, etc.) se leen e interpolan numéricamente.
4. **Números:** $V(t) = V_1 + (V_2 - V_1) \cdot t_{\text{eased}}$, escrito como entero si no tiene decimales.

### Uso
* **Morphing vectorial:** conecta la primitiva `"Circle"` a `V1` y `"Star"` a `V2`, y lleva `Data` a `System/Output` dentro de un `Loops/MaxLoop`.

### Ejemplo: de círculo a estrella en 10 pasos
Dos primitivas re-muestreadas con Clipper2 e interpoladas con `accel=1.5`:

```
[Loops/MaxLoop: total=10] ──► j ──► Iterator ──────────────────┐
                                                               ▼
[Functions/Interpolator: total=10, accel=1.5] ──► Data ──► Shape / Text ──► [System/Output]
   v1: "m 50 0 b 22 0...", v2: "m 50 0 l 61 35..."
```

* **$j=1$ ($t=0.0$):** `{\an5\pos(320, 240)\p1}m 50 0 l 44.8 0.5 ...` (el círculo re-muestreado a 30 nodos).
* **$j=6$ ($t \approx 0.556, t_{\text{eased}} \approx 0.415$):** una forma intermedia con aristas abombadas.
* **$j=10$ ($t=1.0$):** `{\an5\pos(320, 240)\p1}m 50 0 l 61 35 l 98 35 ...` (la estrella completa).

Como los vértices se corresponden 1:1, el trazado no colapsa ni se cruza consigo mismo durante el morphing.

---

## 15. Nodo `Functions/Text on Path` (Texto Adaptado sobre Curvas)

Coloca y reparte texto o glifos sueltos a lo largo de un trazado o curva ASSdraw. En cada punto calcula las coordenadas y la rotación tangencial (`\frz`) para que el texto siga la curvatura.

![Functions/Text on Path](img/text_on_path.jpg)

### Modos
1. **`Center`:** centra todo el texto en el punto medio de la longitud del trazo.
2. **`Left`:** empieza el texto en el comienzo del trazado ($d=0$) más el `Offset`.
3. **`Right`:** termina el texto en el extremo del trazado ($d=L_{\text{total}}$), restando el ancho del texto.
4. **`Justified`:** reparte los caracteres o sílabas uniformemente a lo largo de todo el trazo ($0.0 \to L_{\text{total}}$).
5. **`Animated`:** mapea `Offset` al rango normalizado $0.0 \to 1.0$ para que el texto recorra la curva.

### Entradas
1. **`Path / Shape` (`shape`):** trazado ASSdraw que sirve de guía.
2. **`Offset` (`offset`):** desplazamiento a lo largo del trazo en píxeles (o progreso $0.0 \to 1.0$ en modo `Animated`). (Defecto: `"0"`).
3. **`Extra Angle` (`extra_angle`):** ángulo en grados que se suma al ángulo tangencial calculado. (Defecto: `"0"`).
4. **`Subdivs` (`subdivs`):** número de subdivisiones para el muestreo interno de curvas Bézier. (Defecto: `"30"`).

### Salidas
1. **`[1.1] Tag Out`:** posición y rotación juntas: `\pos(X, Y)\frz(Angle)`.
2. **`[1.2] \pos Tag`:** solo `\pos(X, Y)`.
3. **`[1.3] Angle (\frz)`:** solo `\frz(Angle)`.
4. **`[1.4] X`:** coordenada horizontal $X$ sobre la curva (px).
5. **`[1.5] Y`:** coordenada vertical $Y$ sobre la curva (px).
6. **`[1.6] Length`:** longitud de arco total $L_{\text{total}}$ del trazado en píxeles.

### Cómo funciona

```
                 P_tangente (X, Y)
                        ● ───> Vector Tangente (dx, dy)
                       / \
                      /   \ θ = atan2(dx, dy) - 90°
                     /     \
Ruta Guía: P_inicio ●       ● P_fin (L_total)
```

1. **Posición del carácter en la línea.** Con el ancho total del texto $L_{\text{line}}$ y la posición relativa del carácter $d_{\text{char}} = X_{\text{char}} - X_{\text{inicio}}$:
   $$d_{\text{target}} = \text{lineoffset} + d_{\text{char}}$$
2. **Localización en el trazo.** Se busca el segmento $S_k$ donde cae $d_{\text{target}}$, acotado a $[0, L_{\text{total}}]$, y se obtienen el punto $(X, Y)$ y el vector velocidad $(dx, dy)$.
3. **Orientación.**
   $$\theta_{\text{base}} = \left( \operatorname{atan2}(dx, dy) \cdot \frac{180}{\pi} - 90^\circ \right) + \text{extra\_angle}$$
   El ángulo se normaliza al rango $(-180^\circ, 180^\circ]$ para evitar saltos bruscos de 360 grados en libass.

### Uso
* **Texto sobre un spline dinámico:** lleva `Spline` de `Functions/Bezier Curve` a `Path / Shape` y vincula `Offset` a un oscilador temporal para que el texto ondule como una ola sinusoidal.

### Ejemplo: texto justificado sobre un arco
Los caracteres de una palabra repartidos sobre el trazado `m 100 250 b 200 150 300 150 400 250` en modo `justified`:

```
[Shape/Library: "Arc"] ──► Path / Shape ────────────────────────┐
                                                                ▼
[Functions/Text on Path: mode=justified, subdivs=30] ──► Tag Out ──► Tags In ──► [System/Output]
                                                                                  Return: char.text
```

Para una palabra de 3 caracteres con iterador `char.i` ($1, 2, 3$):
* Carácter 1 ($d=0\text{ px}$, inicio del arco): $P_1(100.0, 250.0)$, tangente ascendente $\theta = 45^\circ \to$ `{\pos(100,250)\frz45}K`.
* Carácter 2 ($d=L/2$, cima del arco): $P_2(250.0, 175.0)$, tangente horizontal $\theta = 0^\circ \to$ `{\pos(250,175)\frz0}a`.
* Carácter 3 ($d=L$, final del arco): $P_3(400.0, 250.0)$, tangente descendente $\theta = -45^\circ \to$ `{\pos(400,250)\frz-45}r`.

---

## 16. Nodo `Functions/Text to Shape` (Vectorización Tipográfica de Glifos)

Convierte glifos TrueType/OpenType en trazados vectoriales ASSdraw (`m ... b ... l ...`). El texto de una sílaba, de una línea o una constante pasa a ser geometría vectorial para operaciones booleanas, segmentadores (*Slicer*), extrusión de bordes o muestreo de partículas.

![Functions/Text to Shape](img/text_to_shape.jpg)

### Entradas
1. **`Text` (`text`):** texto a vectorizar. Si está vacío, toma el texto sin tags de la sílaba o línea activa (`syl.text_stripped` o `line.text_stripped`).
2. **`Font` (`font_name`):** nombre de la familia tipográfica (ej. `"Arial"`, `"Montserrat"`, `"Impact"`). Si está vacío, usa la fuente del estilo ASS activo.
3. **`Size` (`font_size`):** tamaño de fuente en puntos. Si está vacío, usa el tamaño del estilo ASS activo.
4. **`Scale` (`scale`):** multiplicador de escala aplicado a las coordenadas generadas. (Defecto: `"1.0"`).
5. **`Bold` (`bold`):** [Propiedad] negrita (`true` / `false`).
6. **`Italic` (`italic`):** [Propiedad] cursiva (`true` / `false`).

### Salidas
1. **`[1.1] Shape Out`:** trazado ASSdraw cerrado y centrado, con comandos `m`, `l` y curvas Bézier cúbicas `b`.
2. **`[1.2] Width`:** ancho de la caja delimitadora en píxeles ($W$).
3. **`[1.3] Height`:** alto de la caja delimitadora en píxeles ($H$).

### Cómo funciona

```
Fuente TrueType/OpenType ───> FontVectorEngine (Win32 GDI 64x Subpixel) ───> FontVectorMetrics (Sin Pérdida)
                                                                                  │
                ┌─────────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────────────────┐
                ▼                                                                                                                                   ▼
   [ Trazado ASSdraw `m...b...l...` ]                                                                                  [ Ficha Métrica Integral (O(1)) ]
       Para Slicer, Array, Morphs                                                                                   advance_width, cell_height, ascent, descent,
                                                                                                                    lsb, rsb, ink_bbox, delta_x, delta_y
```

1. **Extracción vectorial a resolución subpíxel 64x.** `FontVectorEngine` lee los contornos de la fuente con la API Win32 GDI a resolución subpíxel nativa 64x (`ExtTextOutW` con `BeginPath`) y convierte los splines cuadráticos y cúbicos del glifo en curvas Bézier cúbicas ASSdraw normalizadas (`b cp1x cp1y cp2x cp2y endx endy`).
2. **Métricas (`FontVectorMetrics`).** A diferencia de los conversores habituales, `FontVectorEngine` conserva las métricas de la celda tipográfica:
   * **Márgenes laterales (*Side Bearings*):** $\text{LSB}$ (izquierdo) y $\text{RSB}$ (derecho), que cumplen:
     $$\text{Advance Width} = \text{LSB} + \text{Ink Width} + \text{RSB}$$
   * **Desfase ($\Delta X, \Delta Y$):** desplazamiento entre el centro de avance de la pluma y el baricentro de la tinta:
     $$\Delta X = \frac{\text{LSB} - \text{RSB}}{2}$$
   * **Alturas de celda y línea base:** $\text{ascent}$, $\text{descent}$ y $\text{cell\_height}$, para un registro vertical exacto.
3. **Modos de anclaje (*Anchor Modes*):**
   * **`typographic` (por defecto):** origen en el centro del avance del texto, con calce 1:1 con `\pos(line.center, line.middle)` de libass.
   * **`ink`:** origen en el baricentro físico de la tinta, útil para mallas morfológicas y explosión de partículas.
   * **`baseline` / `origin`:** origen en la línea base tipográfica.

### Uso
* **Fragmentación Voronoi con `Shape/Slicer`:** conecta `Text to Shape` $\to$ `Shape/Slicer (Voronoi)` para romper un texto en trozos poligonales y animar una explosión o desintegración tridimensional.
* **Fusión en una línea con `Shape/Union & Divide (FUSION)`:** conecta `Text to Shape` a `Union & Divide` en modo `FUSION` para emitir subtítulos de una sola línea optimizados, sin sobrecargar libass.

### Ejemplo: vectorizar y extruir un contorno
El texto de la sílaba activa se convierte en geometría ASSdraw y `Shape/Stroke` le aplica un borde vectorial continuo:

```
[Variables/Sys Var: var_name=syl.text] ──► Text ─────────────────┐
                                                                 ▼
[Functions/Text to Shape: font_name="Arial", font_size="50"] ──► Shape Out ──► Shape / Text ──► [Shape/Stroke: width=4.0]
                                                                                                  │
                                                                                                  ▼ Shape Out
                                                                                               Return ──► [System/Output]
```

`FontVectorEngine` vectoriza el glifo a resolución 64x en curvas cúbicas normalizadas `m ... b ...`, mide $W = 42\text{ px}, H = 48\text{ px}$ y conserva el desfase baricéntrico.

Línea emitida:
`Dialogue: 0,0:00:01.00,0:00:03.00,Default,,0,0,0,,{\an5\pos(320,240)\p1}m 0 25 b 0 10 12 0 25 0 b 38 0 50 10 50 25 ...{\p0}`

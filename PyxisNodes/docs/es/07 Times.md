# Times

La categoría **Time** se ocupa de los tiempos de los eventos ASS: desplazar tiempos según la fase de la sílaba o la línea, reescalar transformaciones `\t`, convertir entre milisegundos, marcas ASS y fotogramas, y alargar líneas para cubrir el hueco hasta la siguiente.

* **Fases, retiming y sincronización entre líneas:** `Time/Retime` (§1), `Time/Lead In` (§2), `Time/Lead Out` (§3), `Time/Synced` (§4).
* **Desfases centrales, bucles y duraciones:** `Time/Middle 1` (§5), `Time/Middle 2` (§6), `Time/Loop 1` (§7), `Time/Loop 2` (§8), `Time/Duration` (§14), `Time/Offset` (§15).
* **Conversión, fotogramas e interpolación:** `Time/Parse ASS Time` (§9), `Time/Format ASS Time` (§10), `Time/Time to Frame` (§11), `Time/Frame to Time` (§12), `Time/Ipol` (§13).

---

## 1. `Time/Retime`

Desplaza una ventana temporal según la fase del elemento activo (`syl`, `line`, `presyl`, `postsyl`, etc.) y reescala los bloques `\t(...)` de ASS para ajustarlos a ella. Permite desfases aditivos y aceleración no lineal.

![Time/Retime](img/retime.jpg)

### 1.1. Modo

**`[2.1] Mode` (`phase`):** selecciona el intervalo base. Hay 10 modos:

| Modo (`phase`) | Intervalo Base [$T_1, T_2$] | Descripción |
| :--- | :--- | :--- |
| `syl` | $[T_{\text{syl\_start}}, T_{\text{syl\_end}}]$ | **Sílaba activa (defecto):** ventana en que se canta la sílaba o el carácter. |
| `presyl` | $[T_{\text{syl\_start}}, T_{\text{syl\_start}}]$ | **Pre-sílaba:** instante de inicio de la sílaba, para efectos preparatorios o transiciones de entrada. |
| `postsyl` | $[T_{\text{syl\_end}}, T_{\text{syl\_end}}]$ | **Post-sílaba:** instante de fin de la sílaba, para desvanecimientos o salidas inmediatas. |
| `line` | $[T_{\text{line\_start}}, T_{\text{line\_end}}]$ | **Línea completa:** toda la duración de la línea de diálogo. |
| `preline` | $[T_{\text{line\_start}}, T_{\text{line\_start}}]$ | **Pre-línea:** instante de inicio de la línea. |
| `postline` | $[T_{\text{line\_end}}, T_{\text{line\_end}}]$ | **Post-línea:** instante de fin de la línea. |
| `start2syl` | $[T_{\text{line\_start}}, T_{\text{syl\_start}}]$ | **Entrada a sílaba (*Lead-In*):** desde el inicio de la línea hasta que empieza la sílaba activa. |
| `syl2end` | $[T_{\text{syl\_end}}, T_{\text{line\_end}}]$ | **Sílaba al final (*Lead-Out*):** desde que acaba la sílaba activa hasta que termina la línea. |
| `abs` | $[0, 0]$ | **Absoluto:** no depende de los tiempos de sílaba ni de línea; `Offset In` y `Offset Out` definen la ventana directamente en milisegundos. |
| `sylpct` | $[T_{\text{syl\_start}} + \frac{O_{\text{in}} \cdot D_{\text{syl}}}{100}, T_{\text{syl\_start}} + \frac{O_{\text{out}} \cdot D_{\text{syl}}}{100}]$ | **Porcentaje de sílaba:** `Offset In` y `Offset Out` se interpretan como porcentajes ($0\% \dots 100\%$) de la duración de la sílaba. |

### 1.2. Entradas y Propiedades
1. **`Tags or \t` (`tags`):** etiquetas ASS. Acepta etiquetas estáticas (ej. `\fscx150\fscy150\alpha&HFF&`) o bloques `\t(...)` ya existentes.
2. **`Offset In (ms)` (`offset_in`):** desplazamiento aplicado al punto inicial $T_1$. Positivo retrasa, negativo adelanta; acepta variables y expresiones (defecto: `0`).
3. **`Offset Out (ms)` (`offset_out`):** desplazamiento aplicado al punto final $T_2$ (defecto: `0`).
4. **`Accel` (`accel`):** exponente de aceleración en la etiqueta `\t(t1, t2, accel, \tags)`. `1.0` es lineal; valores $< 1.0$ desaceleran (*ease-out*); valores $> 1.0$ aceleran (*ease-in*) (defecto: `1.0`).

### 1.3. Salidas
1. **`[1.1] \t Out`:** bloque de etiquetas en sintaxis ASS `\t(t1, t2, [accel,] \tags)`. $t_1$ y $t_2$ están en el **tiempo local de la línea** (relativos a `0 ms` al inicio de la línea generada).
2. **`[1.2] Start Time`:** tiempo de inicio absoluto $T_1$ en milisegundos sobre la línea de tiempo del video.
3. **`[1.3] End Time`:** tiempo de fin absoluto $T_2$ en milisegundos sobre la línea de tiempo del video.
4. **`[1.4] Duration`:** $D = \max(0, T_2 - T_1)$, en milisegundos.

### 1.4. Cómo se Mapea `\t`

```
   Inicio Línea                                            Fin Línea
   ├──────────────────────────┬─────────────────┬──────────────────┤
   │        start2syl         │  syl (activa)   │     syl2end      │
   │                          ├────────┬────────┤                  │
   │                          │ presyl │ postsyl│                  │
───┴──────────────────────────┴────────┴────────┴──────────────────┴───► Tiempo
   0 ms                      T_syl_st  T_syl_et  Line_dur
```

Si `Tags or \t` ya contiene bloques `\t(t_a, t_b, ...)`, el nodo recalcula sus tiempos y conserva los sub-intervalos internos:

$$\tilde{t}_1 = T_{\text{local\_1}} + t_a, \quad \tilde{t}_2 = T_{\text{local\_1}} + t_b$$

Si un `\t(...)` no trae tiempos (ej. `\t(\blur10)`), el nodo inserta la ventana completa de la fase:

$$\text{\textbackslash t}(T_{\text{local\_1}}, T_{\text{local\_2}}, [a,] \text{\textbackslash blur10})$$

> [!IMPORTANT]
> * **`\t Out`** es siempre **relativo al inicio de la línea** ($t=0\text{ ms}$), porque la etiqueta `\t` de ASS mide el desfase desde el inicio de la propia línea de subtítulo.
> * **`Start Time` y `End Time`** son **tiempos absolutos de video**, necesarios al crear eventos temporizados independientes en `System/Output`.

### 1.5. Uso
* **Efectos de entrada y salida independientes:** usar dos nodos `Retime`, uno con `Mode: start2syl` para la entrada y otro con `Mode: syl2end` o `postsyl` para la salida.
* **Construir líneas completas:** enviar `\t Out` a `Concatenate` junto con `\pos` y las etiquetas de estilo base para armar la línea en un solo flujo.

### 1.6. Ejemplo
Una entrada donde cada sílaba escala de 0% a 100% y pasa de transparente a opaca antes de cantarse:

```
Tags In: \fscx100\fscy100\alpha&H00& ──► Tags or \t ──► [Time/Retime: start2syl, accel=0.8]
                                                              └──► \t Out ──► Tags ──► [System/Output]
```

Con `Tags` de `System/Output` usando el estilo base `{\an5\pos(syl.center, syl.middle)\fscx0\fscy0\alpha&HFF&}`, el nodo resuelve numéricamente los tiempos en milisegundos y emite:
```
{\an5\pos(320, 240)\fscx0\fscy0\alpha&HFF&\t(0, 180, 0.8, \fscx100\fscy100\alpha&H00&)}
```
La sílaba hace la transición durante el intervalo de entrada (*start2syl*) con una curva *ease-out* (`accel=0.8`).

---

## 2. `Time/Lead In`

Calcula un desfase escalonado a partir del índice $i$ de la unidad activa, de modo que cada sílaba o carácter empiece su animación un poco después del anterior, todo antes de que se cante.

![Time/Lead In](img/lead_in.jpg)

### 2.1. Entradas y Propiedades
1. **`Delay (ms)` (`delay_ms`):** retardo escalonado por unidad, en milisegundos. Acepta constantes, variables y expresiones aritméticas inline (defecto: `40`).

### 2.2. Salidas
1. **`[1.1] Data`:** el desfase en milisegundos.

### 2.3. Modelo
Para el índice de la unidad activa $i \in \{1, \dots, N\}$ (número de sílaba o carácter en el ciclo), el nodo aplica una anticipación fija de $200\text{ ms}$:

$$T_{\text{out}} = T_{\text{base}} + \Delta_{\text{delay}} \cdot (i - 1) - 200$$

* $T_{\text{base}}$ es el tiempo de referencia base (por defecto $0.0\text{ ms}$).
* $\Delta_{\text{delay}}$ es el valor de `Delay (ms)`.
* $i$ es el índice de la sílaba o glifo actual ($1$-based).
* $-200\text{ ms}$ es la constante de anticipación (*lookahead*).

Ejemplo ($N=4\text{ unidades}, \Delta=40\text{ ms}$):
* Unidad $1$ ($i=1$): $40 \cdot (1 - 1) - 200 = -200\text{ ms}$
* Unidad $2$ ($i=2$): $40 \cdot (2 - 1) - 200 = -160\text{ ms}$
* Unidad $3$ ($i=3$): $40 \cdot (3 - 1) - 200 = -120\text{ ms}$
* Unidad $4$ ($i=4$): $40 \cdot (4 - 1) - 200 = -80\text{ ms}$

### 2.4. Ejemplo
Conectar `Data` al puerto `Offset In (ms)` de un nodo `Retime` (en modo `syl` o `start2syl`) para que cada letra empiece a animarse progresivamente antes de cantarse:

```
[Time/Lead In: delay_ms=40] ──► Data ──► Offset In (ms) ──► [Time/Retime: syl, accel=1.0]
                                                                  └──► \t Out ──► Tags ──► [System/Output]
```

Si la entrada `Tags or \t` de `Retime` recibe `\fscx130\fscy130\1c&H00FFFF&`, en una línea de 4 sílabas cada elemento empieza a resaltar $200 - 40 \cdot (i - 1)$ ms antes de cantarse, formando una oleada que anticipa la voz.

---

## 3. `Time/Lead Out`

Calcula un desfase escalonado a partir de la distancia de la unidad activa al final de la línea ($i - n$), para desvanecimientos progresivos y salidas coordinadas después del canto.

![Time/Lead Out](img/lead_out.jpg)

### 3.1. Entradas y Propiedades
1. **`Delay (ms)` (`delay_ms`):** retardo del escalonamiento de salida, en milisegundos (defecto: `40`).

### 3.2. Salidas
1. **`[1.1] Data`:** el desfase en milisegundos.

### 3.3. Modelo
Para la unidad $i$ de un total de $n$:

$$T_{\text{out}} = T_{\text{base}} + \Delta_{\text{delay}} \cdot (i - n - 1) + 200$$

* $n$ es el número total de unidades en la línea (`syl.n`, `char.n`).
* $+200\text{ ms}$ es la constante de sostenimiento posterior.

Ejemplo ($n=4\text{ unidades}, \Delta=40\text{ ms}$):
* Unidad $1$ ($i=1$): $40 \cdot (1 - 4 - 1) + 200 = 40 \cdot (-4) + 200 = +40\text{ ms}$
* Unidad $2$ ($i=2$): $40 \cdot (2 - 4 - 1) + 200 = 40 \cdot (-3) + 200 = +80\text{ ms}$
* Unidad $3$ ($i=3$): $40 \cdot (3 - 4 - 1) + 200 = 40 \cdot (-2) + 200 = +120\text{ ms}$
* Unidad $4$ ($i=4$): $40 \cdot (4 - 4 - 1) + 200 = 40 \cdot (-1) + 200 = +160\text{ ms}$

### 3.4. Ejemplo
Conectar `Data` a `Offset Out (ms)` de un nodo `Retime` en modo `postsyl` (o `syl`), de modo que las primeras sílabas desaparezcan antes y las últimas permanezcan más tiempo en pantalla, siguiendo el sentido de lectura:

```
[Time/Lead Out: delay_ms=50] ──► Data ──► Offset Out (ms) ──► [Time/Retime: postsyl]
                                                                   └──► \t Out ──► Tags ──► [System/Output]
```

Con `Tags or \t: \alpha&HFF&`, la primera sílaba empieza a desvanecerse poco después de cantarse, mientras que las últimas siguen visibles más tiempo, así el texto no desaparece de golpe.

---

## 4. `Time/Synced`

Calcula tiempo extra de permanencia entre líneas de diálogo consecutivas. Rellena las pausas musicales, compensa la distancia en pantalla entre frases y suaviza la transición hacia la siguiente línea.

![Time/Synced](img/synced.jpg)

### 4.1. Entradas y Propiedades
1. **`Mode` (`mode`):** criterio para emparejar la línea actual con la siguiente (`next_line`):
   * `order`: la siguiente línea de la lista, sin filtros.
   * `style`: la siguiente línea con el mismo estilo (`style_name`).
   * `actor`: la siguiente línea con el mismo actor (`actor`).
   * `layer`: la siguiente línea con la misma capa ASS (`layer`).
   * `effect`: la siguiente línea con el mismo campo de efecto ASS (`effect`).
2. **`Constant` (`progression_const`):** multiplicador de progresión según la densidad de caracteres (ms por glifo) (defecto: `0`).
3. **`Fade (ms)` (`fade_dur`):** duración del *fade-out* previsto, en milisegundos (defecto: `300`).
4. **`Max Extra` (`max_added_time`):** límite (*cap*) de tiempo extra, en milisegundos, que se puede añadir a la línea (defecto: `2000`).
5. **`Delay Line` (`delay_ms`):** separación mínima necesaria para considerar que hay una pausa entre líneas (defecto: `250`).
6. **`Threshold` (`max_gap_threshold`):** pausa máxima. Si la pausa entre la línea actual y la siguiente la supera, el algoritmo la trata como una pausa larga independiente y no extiende la línea a través de ella (defecto: `3000`).

### 4.2. Salidas
1. **`[1.1] Extra ms`:** milisegundos extra calculados ($\Delta t_{\text{extra}}$).
2. **`[1.2] Sync End`:** tiempo de fin absoluto sincronizado ($T_{\text{line\_end}} + \Delta t_{\text{extra}}$), listo para usarse como tiempo de fin de la línea ASS.

### 4.3. Algoritmo

```
  Línea Actual                      Pausa / Gap                  Línea Siguiente
├──────────────────────┤◄────────────────────────────────►├──────────────────────┤
0 ms               Curr_End                            Next_Start            Next_End
                       │                                  │
                       └───► [ Sincronización Adaptativa ] ◄──┘
                             • Compensación espacial (Salto X)
                             • Progresión por caracteres
                             • Deducción de Fade-out
```

Para cada línea, el nodo evalúa lo siguiente.

#### 1. Progresión base de la línea actual ($P_{2,\text{curr}}$)
Se calcula a partir del número de elementos $C_{\text{curr}}$:
$$P_{2,\text{curr}} = k_{\text{prog}} \cdot \max(0, C_{\text{curr}} - 1) + \Delta_{\text{delay}}$$

#### 2. Brecha hasta la siguiente línea ($\Delta_{\text{gap}}$)
$$\Delta_{\text{gap}} = T_{\text{next, start}} - T_{\text{curr, end}}$$

* **Caso A (línea aislada, o última línea sin sucesora):**
  $$\Delta t_{\text{extra}} = \min\left(M_{\text{max}}, \max(0, P_{2,\text{curr}})\right)$$

* **Caso B (líneas solapadas o contiguas, $\Delta_{\text{gap}} < \Delta_{\text{delay}}$):**
  $$\Delta t_{\text{extra}} = 0.0\text{ ms}$$

* **Caso C (silencio largo, $\Delta_{\text{gap}} > \text{Threshold}$):**
  La línea recibe su progresión normal, sin puente hacia la siguiente:
  $$\Delta t_{\text{extra}} = \min\left(M_{\text{max}}, \max(0, P_{2,\text{curr}})\right)$$

* **Caso D (puente normal, $\Delta_{\text{delay}} \le \Delta_{\text{gap}} \le \text{Threshold}$):**
  El nodo compara la ocupación 2D de ambas líneas usando los límites de tinta de los glifos o sus cajas tipográficas ($[X_{\text{min}}, X_{\text{max}}], [Y_{\text{min}}, Y_{\text{max}}]$) y sus propiedades de posición (`\pos`, `align`):

  1. **Subcaso D.1 — zonas de pantalla separadas:**
     Las líneas no están en la misma franja vertical (por ejemplo, cabecera en `\an8` y pie en `\an2`, o $|Y_{\text{curr}} - Y_{\text{next}}| > 0.5 \cdot \text{alto}$):
     * Se ignora la progresión por caracteres ($P_2 = 0$).
     * La línea actual se extiende solo para cubrir la brecha hasta que aparece la siguiente, con el *fade-out* ajustado para terminar en ese momento:
       $$T_{\text{ideal\_end}} = T_{\text{next, start}} - \text{Fade}_{\text{dur}}$$

  2. **Subcaso D.2 — mismo espacio, anclaje común:**
     Ambas líneas están en la misma franja vertical y comparten anclaje u origen lateral (por ejemplo, dos líneas consecutivas alineadas a la izquierda `\an4`, a la derecha `\an6`, o centradas reemplazando el mismo renglón, con $X_{\text{next, left}} - X_{\text{curr, right}} \le 0$):
     * El tiempo de transición es el promedio de la progresión de ambas líneas:
       $$T_{\text{trans}} = \frac{P_{2,\text{curr}} + P_{2,\text{next}}}{2}$$
     * No se suma compensación espacial ($\Delta t_{\text{spatial}} = 0.0\text{ ms}$):
       $$T_{\text{ideal\_end}} = T_{\text{next, start}} + T_{\text{trans}} - \text{Fade}_{\text{dur}}$$

  3. **Subcaso D.3 — mismo renglón, siguiente línea más adelante:**
     Ambas líneas están en la misma franja vertical y la siguiente queda más adelante en el sentido de lectura ($X_{\text{next, left}} > X_{\text{curr, right}}$):
     * El salto horizontal es:
       $$\text{Salto} = X_{\text{next, left}} - X_{\text{curr, right}}$$
       $$\Delta t_{\text{spatial}} = \left(\frac{\text{Salto}}{w_{\text{avg}}}\right) \cdot k_{\text{prog}}$$
     * $w_{\text{avg}}$ se toma de las métricas medidas de los glifos (`line.chars` vía `FontEngine`).
     * El tiempo ideal de fin es:
       $$T_{\text{ideal\_end}} = T_{\text{next, start}} + T_{\text{trans}} + \Delta t_{\text{spatial}} - \text{Fade}_{\text{dur}}$$

  Por último, el tiempo extra se limita:
  $$\Delta t_{\text{extra}} = \min\left(M_{\text{max}}, \max(0, T_{\text{ideal\_end}} - T_{\text{curr, end}})\right)$$

### 4.4. Uso
* **Rellenar huecos en karaokes continuos:** conectar `Sync End` al puerto `End Time` de `System/Output`. Los subtítulos siguen visibles durante las pausas cortas y terminan de desvanecerse justo cuando aparece la siguiente línea.
* **Con `Retime`:** enviar `Extra ms` a `Offset Out` de `Time/Retime` (en modo `line` o `postline`) para extender las capas de efectos de fondo (*glow*, bordes concéntricos, partículas) durante el tiempo extra.

### 4.5. Ejemplo
Extender la duración de la línea con `Synced` conectado a `System/Output`:

```
[Time/Synced: mode=style, fade_dur=300, max_extra=2500] ──► Sync End ──► End Time ──► [System/Output]
```

En el bloque de tags:
```
{\pos(line.center, line.bottom - 40)\fad(200, 300)}
```
Si la siguiente línea empieza 1200 ms después, `Synced` extiende el final de la línea actual hasta $T_{\text{next, start}} - 300$, y el `\fad` de 300 ms termina justo cuando aparece la nueva frase.

---

## 5. `Time/Middle 1`

Calcula un desfase simétrico respecto al centro de la línea. Las animaciones de entrada pueden converger desde los extremos hacia el centro o irradiar desde el centro hacia los extremos.

![Time/Middle 1](img/middle_1.jpg)

### 5.1. Entradas y Propiedades
1. **`Delay (ms)` (`delay_ms`):** retardo en milisegundos por cada paso de unidad hacia o desde el centro. Acepta constantes, variables y expresiones (defecto: `30`).

### 5.2. Salidas
1. **`[1.1] Data`:** el desfase en milisegundos, calculado según la mitad en que se encuentra la unidad activa.

### 5.3. Modelo
Las $n$ unidades se dividen en dos mitades a partir del eje central $\frac{n + 1}{2}$. Para el índice activo $i \in \{1, \dots, n\}$:

$$\text{offset} = \begin{cases} 
\Delta_{\text{delay}} \cdot (i - 1) - 200, & \text{si } i \le \frac{n + 1}{2} \\[6pt]
\Delta_{\text{delay}} \cdot (n - i + 0.5) - 200, & \text{si } i > \frac{n + 1}{2}
\end{cases}$$

$$T_{\text{out}} = T_{\text{base}} + \text{offset}$$

* $i$ es el índice activo ($1 \le i \le n$).
* $n$ es el número total de unidades (`syl.n` o `char.n`).
* $\Delta_{\text{delay}}$ es el valor de `Delay (ms)`.
* $-200\text{ ms}$ es la anticipación base (*lookahead*).

Ejemplo ($n=4\text{ unidades}, \Delta=30\text{ ms}$, punto medio $= 2.5$):
* Unidad $1$ ($i=1 \le 2.5$): $30 \cdot (1 - 1) - 200 = -200.0\text{ ms}$
* Unidad $2$ ($i=2 \le 2.5$): $30 \cdot (2 - 1) - 200 = -170.0\text{ ms}$
* Unidad $3$ ($i=3 > 2.5$): $30 \cdot (4 - 3 + 0.5) - 200 = 30 \cdot 1.5 - 200 = -155.0\text{ ms}$
* Unidad $4$ ($i=4 > 2.5$): $30 \cdot (4 - 4 + 0.5) - 200 = 30 \cdot 0.5 - 200 = -185.0\text{ ms}$

### 5.4. Ejemplo
Conectar `Data` a `Offset In (ms)` de `Time/Retime` (en modo `syl` o `start2syl`). Los extremos de la frase se animan primero y convergen hacia el centro (entrada en V o *chevron*):

```
[Time/Middle 1: delay_ms=35] ──► Data ──► Offset In (ms) ──► [Time/Retime: start2syl, accel=0.8]
                                                                  └──► \t Out ──► Tags ──► [System/Output]
```

Con `Tags or \t: \fscx100\fscy100\1c&H00FFFF&` y estilo base `{\an5\fscx0\fscy0\1c&HFFFFFF&}`, en una línea de 6 caracteres el escalado empieza en las letras exteriores ($i=1$ e $i=6$) y avanza hacia dentro hasta llegar a las dos centrales ($i=3, 4$).

---

## 6. `Time/Middle 2`

Calcula un desfase simétrico anclado al final de la línea ($T_{\text{end}}$), para que los desvanecimientos y transiciones de salida actúen de forma simétrica hacia o desde el centro de la frase.

![Time/Middle 2](img/middle_2.jpg)

### 6.1. Entradas y Propiedades
1. **`Delay (ms)` (`delay_ms`):** retardo en milisegundos para el escalonamiento simétrico de salida (defecto: `30`).

### 6.2. Salidas
1. **`[1.1] Data`:** el desfase en milisegundos, relativo al final de la unidad o de la línea.

### 6.3. Modelo
`Middle 2` invierte la orientación para anclarse al final del evento:

$$\text{offset} = \begin{cases} 
\Delta_{\text{delay}} \cdot (i - n - 1) - 200, & \text{si } i \ge \frac{n + 1}{2} \\[6pt]
\Delta_{\text{delay}} \cdot (-i + 0.5) - 200, & \text{si } i < \frac{n + 1}{2}
\end{cases}$$

$$T_{\text{out}} = T_{\text{base}} + \text{offset}$$

Ejemplo ($n=4\text{ unidades}, \Delta=30\text{ ms}$, punto medio $= 2.5$):
* Unidad $1$ ($i=1 < 2.5$): $30 \cdot (-1 + 0.5) - 200 = 30 \cdot (-0.5) - 200 = -215.0\text{ ms}$
* Unidad $2$ ($i=2 < 2.5$): $30 \cdot (-2 + 0.5) - 200 = 30 \cdot (-1.5) - 200 = -245.0\text{ ms}$
* Unidad $3$ ($i=3 \ge 2.5$): $30 \cdot (3 - 4 - 1) - 200 = 30 \cdot (-2) - 200 = -260.0\text{ ms}$
* Unidad $4$ ($i=4 \ge 2.5$): $30 \cdot (4 - 4 - 1) - 200 = 30 \cdot (-1) - 200 = -230.0\text{ ms}$

### 6.4. Ejemplo
Conectar `Data` a `Offset Out (ms)` de un nodo `Time/Retime` en modo `postsyl`, para disoluciones o caídas de partículas en las que los glifos centrales desaparecen antes o después que los laterales (salida en cortina espejada):

```
[Time/Middle 2: delay_ms=40] ──► Data ──► Offset Out (ms) ──► [Time/Retime: postsyl]
                                                                   └──► \t Out ──► Tags ──► [System/Output]
```

Con `Tags or \t: \alpha&HFF&`, los glifos centrales terminan de cantarse y empiezan a desvanecerse enseguida, mientras que los laterales siguen visibles más tiempo, como una cortina que se abre.

---

## 7. `Time/Loop 1`

Genera desfases escalonados o simétricos para las iteraciones de un sub-bucle primario de `Loops/MaxLoop` (modo normal o FBF). Compara el índice de iteración local $j$ (`fx_i`) con el total de repeticiones $\text{maxj}$ (`fx_n`).

![Time/Loop 1](img/loop_1.jpg)

### 7.1. Modo

**`[2.1] Mode` (`mode`):** cómo se reparten los desfases entre las $j$ iteraciones:

| Modo (`mode`) | Ecuación de Desfase ($\text{offset}$) | Comportamiento |
| :--- | :--- | :--- |
| `leadin` (Defecto) | $\Delta \cdot (j - 1) - 200$ | **Cascada:** cada sub-capa $j$ empieza después de la anterior, con anticipación. |
| `leadout` | $\Delta \cdot (j - \text{maxj} - 1) + 200$ | **Salida escalonada:** las sub-capas terminan una tras otra después del final del evento. |
| `middle1` | $\begin{cases} \Delta \cdot (j - 1) - 200, & j \le \frac{\text{maxj}+1}{2} \\ \Delta \cdot (\text{maxj} - j + 0.5) - 200, & j > \frac{\text{maxj}+1}{2} \end{cases}$ | **Entrada simétrica:** las capas convergen desde las iteraciones exteriores hacia el centro. |
| `middle2` | $\begin{cases} \Delta \cdot (j - \text{maxj} - 1) - 200, & j \ge \frac{\text{maxj}+1}{2} \\ \Delta \cdot (-j + 0.5) - 200, & j < \frac{\text{maxj}+1}{2} \end{cases}$ | **Salida simétrica:** salida simétrica centrada en el conjunto de iteraciones. |

### 7.2. Entradas y Propiedades
1. **`Delay (ms)` (`delay_ms`):** desfase en milisegundos entre iteraciones consecutivas del sub-bucle (defecto: `30`).

### 7.3. Salidas
1. **`[1.1] Data`:** el desfase en milisegundos para la iteración actual $j$.

### 7.4. Variables de Contexto
> [!NOTE]
> A diferencia de `Lead In` o `Middle 1`, que leen el índice $i \in [1, n]$ de la sílaba o el carácter en el `Main Loop`, `Time/Loop 1` lee el contexto del sub-bucle:
> * **$j$ (`fx_i`):** índice de la repetición activa ($1, 2, \dots, \text{maxj}$).
> * **$\text{maxj}$ (`fx_n`):** límite de repeticiones configurado en `MaxLoop`.

### 7.5. Ejemplo
Para estelas y ecos (*ghosting*), encadenar `Loops/Main Loop` $\to$ `Loops/MaxLoop (5 iteraciones)` $\to$ `Time/Loop 1 (Mode: leadin, Delay: 40ms)` $\to$ `Time/Retime`. Cada una de las 5 capas se desfasa en el tiempo y produce estelas de movimiento.

Un caso concreto, 3 capas fantasma tras el elemento principal:

```
[Loops/MaxLoop: count=3] ──► j ──► (Contexto local j)
                                         │
[Time/Loop 1: mode=leadin, delay_ms=45] ──► Data ──► Offset In (ms) ──► [Time/Retime: syl]
                                                                            └──► \t Out ──► Tags ──► [System/Output]
```

Combinado con una opacidad por capa `{\1a(120 + j * 40)}`, cada iteración $j \in \{1, 2, 3\}$ se retrasa 45 ms respecto a la anterior y forma una estela sincronizada con el canto (la opacidad se evalúa a `\1a&HA0&`, `\1a&HC8&` y `\1a&HF0&`).

---

## 8. `Time/Loop 2`

Mismas fórmulas que `Time/Loop 1`, pero para **sub-bucles anidados de segundo nivel**: usa la variable de iteración en mayúscula $J$ y el total $\text{maxJ}$.

![Time/Loop 2](img/loop_2.jpg)

### 8.1. Modo
**`[2.1] Mode` (`mode`):** mismas opciones que `Loop 1` (`leadin`, `leadout`, `middle1`, `middle2`).

### 8.2. Entradas y Propiedades
1. **`Delay (ms)` (`delay_ms`):** retardo en milisegundos entre iteraciones $J$ (defecto: `30`).

### 8.3. Salidas
1. **`[1.1] Data`:** el desfase en milisegundos para la sub-iteración anidada actual $J$.

### 8.4. Ámbitos de Iteración

| Nodo de Tiempo | Variable de Índice | Total | Ámbito |
| :--- | :---: | :---: | :--- |
| `Lead In` / `Lead Out` / `Middle 1` / `Middle 2` | $i$ (`syl.i`, `char.i`) | $n$ (`syl.n`, `char.n`) | **Bucle maestro (`Main Loop`):** itera sobre sílabas, caracteres, palabras o líneas. |
| `Loop 1` | $j$ (`fx_i`) | $\text{maxj}$ (`fx_n`) | **Sub-bucle primario (`MaxLoop` nivel 1):** réplicas multicapa o fotogramas FBF. |
| `Loop 2` | $J$ | $\text{maxJ}$ | **Sub-bucle anidado (`MaxLoop` nivel 2):** fractales, enjambres anidados o sub-muestreos complejos. |

### 8.5. Ejemplo
En una rejilla de partículas donde un `MaxLoop (X)` contiene a un `MaxLoop (Y)`, usar `Time/Loop 1` para el desfase por columna ($j$) y `Time/Loop 2` para el desfase por fila ($J$), y sumar ambas salidas en un nodo `Basics/Math (add)` antes de `Time/Retime`:

```
[Loops/MaxLoop X: cols=4] ──► j
     └──► [Loops/MaxLoop Y: rows=3] ──► J
               │
[Time/Loop 1: leadin, delay=30] ──► Data ──► In 1 ──► [Basics/Math: add]
[Time/Loop 2: leadin, delay=60] ──► Data ──► In 2 ─────────┘   │
                                                               └──► Offset In (ms) ──► [Time/Retime: syl]
```

La suma de retardos produce un barrido diagonal ($30 \cdot (j-1) + 60 \cdot (J-1)$ ms) que activa cada celda de la rejilla por turnos.

---

## 9. `Time/Parse ASS Time`

Convierte una marca de tiempo ASS (`H:MM:SS.CS` o `H:MM:SS.MMM`) en un número entero de milisegundos.

![Time/Parse ASS Time](img/parse_ass_time.jpg)

### 9.1. Entradas y Propiedades
1. **`ASS Time` (`ass_time`):** la marca de tiempo a convertir (ej. `"0:01:23.45"` o `"1:12:05.120"`). Si el puerto no está conectado y el campo está en blanco, el nodo usa el tiempo de inicio del elemento activo (`unit.start_str` $\to$ `line.start_str`) (defecto: `"0:00:00.00"`).

### 9.2. Salidas
1. **`[1.1] Time (ms)`:** el total como número entero de milisegundos.

### 9.3. Modelo
Para una marca con horas $H$, minutos $M$, segundos $S$ y centisegundos $CS$:

$$T_{\text{ms}} = (3600 \cdot H + 60 \cdot M + S) \cdot 1000 + CS \cdot 10$$

Ejemplo:
$$\text{"0:01:23.45"} \implies (0 + 60 + 23) \cdot 1000 + 45 \cdot 10 = 83000 + 450 = 83450\text{ ms}$$

### 9.4. Ejemplo
Decodificar marcas literales para operar con `Basics/Math` o `Time/Offset`, y volver a codificarlas con `Time/Format ASS Time` o enviarlas a `System/Output`. Aquí se adelanta 500 ms una marca fija:

```
[Time/Parse ASS Time: ass_time="0:01:15.50"] ──► Time (ms) ──► In 1 ──► [Basics/Math: add, in2=500]
                                                                              └──► In 1 ──► [Time/Format ASS Time]
                                                                                                  └──► ASS Time ──► "0:01:16.00"
```
El valor decodificado (75500 ms) pasa a 76000 ms y se vuelve a codificar en formato ASS sin pérdida de precisión.

---

## 10. `Time/Format ASS Time`

Convierte un número de milisegundos en la cadena de marca de tiempo ASS (`H:MM:SS.CS`).

![Time/Format ASS Time](img/format_ass_time.jpg)

### 10.1. Entradas y Propiedades
1. **`Time (ms)` (`time`):** valor en milisegundos (entero, flotante o expresión evaluable). Si el puerto no está conectado y el campo está vacío, toma el tiempo de inicio de la sílaba o línea (`unit.start_time` $\to$ `line.start_time`) (defecto: `"0"`).

### 10.2. Salidas
1. **`[1.1] ASS Time`:** cadena con ceros de relleno en la sintaxis de Aegisub / libass, `H:MM:SS.CS` (centisegundos de dos dígitos).

### 10.3. Modelo
A partir del total de milisegundos $T_{\text{ms}}$:

$$H = \left\lfloor \frac{T_{\text{ms}}}{3600000} \right\rfloor$$
$$M = \left\lfloor \frac{T_{\text{ms}} \bmod 3600000}{60000} \right\rfloor$$
$$S = \left\lfloor \frac{T_{\text{ms}} \bmod 60000}{1000} \right\rfloor$$
$$CS = \left\lfloor \frac{T_{\text{ms}} \bmod 1000}{10} \right\rfloor$$

$$\text{ASS Time} = H : \text{pad}_2(M) : \text{pad}_2(S) . \text{pad}_2(CS)$$

$\text{pad}_2(x)$ antepone un cero si $x < 10$.

### 10.4. Ejemplo
Conectar `ASS Time` a constructores de eventos en `Script Code` o a generadores de cadenas de diálogo cuando se exportan archivos `.ass` multipista fuera del flujo de salida estándar. Por ejemplo, convertir en marca ASS un tiempo retrasado calculado:

```
[Time/Offset: base=line.start_time, offset_ms=1200] ──► Time (ms) ──► Time (ms) ──► [Time/Format ASS Time]
                                                                                            └──► ASS Time
```
Si `line.start_time` es 10000 ms, `Offset` emite 11200 ms y `Format ASS Time` produce `"0:00:11.20"`.

---

## 11. `Time/Time to Frame`

Convierte un tiempo o duración en milisegundos en un número o cantidad de fotogramas ($f$), según la tasa de cuadros (*FPS*) del proyecto.

![Time/Time to Frame](img/time_to_frame.jpg)

### 11.1. Modos
1. **`[2.1] Mode` (`mode`):** cómo se redondea el número de fotograma:
   * `round` (Defecto): al fotograma más próximo ($\lfloor x + 0.5 \rfloor$).
   * `floor`: hacia abajo ($\lfloor x \rfloor$), adecuado para índices de fotograma en base 0 en la línea de tiempo.
   * `ceil`: hacia arriba ($\lceil x \rceil$), adecuado para la cantidad total de fotogramas que abarca una duración no nula.
2. **`[2.2] Source` (`source`):** de dónde sale el tiempo:
   * `custom` (Defecto): el valor del puerto `Time (ms)` o de la propiedad inline.
   * `start`: tiempo de inicio de la unidad activa (`unit.start_time` $\to$ `line.start_time`).
   * `end`: tiempo de fin (`unit.end_time` $\to$ `line.end_time`).
   * `dur`: duración (`unit.duration` $\to$ `line.duration`).

### 11.2. Entradas y Propiedades
1. **`Time (ms)` (`time`):** tiempo en milisegundos a convertir. Acepta números, marcas ASS `H:MM:SS.CS` y variables de contexto.
2. **`Frame Dur (ms)` (`frame_dur`):** duración de un fotograma en milisegundos. Si está desconectado o vacío, usa el video cargado en Aegisub (por defecto $41.708\text{ ms}$, equivalente a $23.976\text{ fps}$).

### 11.3. Salidas
1. **`[1.1] Frames (f)`:** número entero de fotogramas resultante.

### 11.4. Modelo
Con la duración por cuadro $fd = \frac{1000}{\text{FPS}}$ y el tiempo resuelto $T$:

$$f_{\text{ceil}} = \left\lceil \frac{T}{fd} \right\rceil, \quad f_{\text{floor}} = \left\lfloor \frac{T}{fd} \right\rfloor, \quad f_{\text{round}} = \left\lfloor \frac{T}{fd} + 0.5 \right\rfloor$$

Duración por cuadro según FPS:

| Tasa de Cuadros (FPS) | Duración por Cuadro ($fd$) | Cuadros para $1000\text{ ms}$ (Ceil) |
| :---: | :---: | :---: |
| **$23.976\text{ fps}$** | $\approx 41.7083\text{ ms}$ | $24\text{ frames}$ |
| **$24.000\text{ fps}$** | $\approx 41.6667\text{ ms}$ | $24\text{ frames}$ |
| **$29.970\text{ fps}$** | $\approx 33.3667\text{ ms}$ | $30\text{ frames}$ |
| **$30.000\text{ fps}$** | $\approx 33.3333\text{ ms}$ | $30\text{ frames}$ |
| **$60.000\text{ fps}$** | $\approx 16.6667\text{ ms}$ | $60\text{ frames}$ |

### 11.5. Ejemplo
Conectar `Time to Frame` (con `Source: dur` y `Mode: ceil`) al puerto `Total` o a la propiedad de repeticiones de `Loops/MaxLoop (fbf)`, para que el bucle itere exactamente tantas veces como fotogramas abarca la sílaba. A 23.976 fps:

```
[Time/Time to Frame: source=dur, mode=ceil] ──► Frames (f) ──► Count / Reps ──► [Loops/MaxLoop: fbf]
```
Si la sílaba dura 450 ms y $fd \approx 41.708$ ms:
$$\left\lceil \frac{450}{41.708} \right\rceil = \lceil 10.789 \rceil = 11\text{ frames}$$
`MaxLoop` itera exactamente 11 veces y cubre toda la sílaba sin fotogramas de más ni de menos.

---

## 12. `Time/Frame to Time`

Multiplica un número de fotograma o contador de iteración ($f$, $j$, $J$, $i$) por la duración del fotograma para obtener el tiempo en milisegundos, como marca ASS o en segundos.

![Time/Frame to Time](img/frame_to_time.jpg)

### 12.1. Modos
1. **`[2.1] Format` (`format`):** formato de la salida principal `[1.1] Time`:
   * `ms` (Defecto): milisegundos redondeados a dos decimales (ej. `2000.0`).
   * `hms`: cadena en sintaxis de marca ASS (ej. `"0:00:02.00"`).
   * `sec`: segundos en punto flotante con tres decimales (ej. `2.000`).
2. **`[2.2] Source` (`source`):** de dónde sale el número de fotograma:
   * `custom` (Defecto): el valor del puerto `Frames (f)` o del campo inline `frames`.
   * `iterator`: una variable de iteración propia indicada en `iter_name` (ej. `k`, `step_i`, o expresiones como `k * 2`).
   * `j`: el contador de sub-bucle activo `j` (`fx_i`).
   * `J`: el contador de sub-bucle anidado activo `J`.
   * `i`: el índice secuencial de la unidad `unit.i`.

### 12.2. Entradas y Propiedades
1. **`Frames (f)` (`frames`):** cantidad o índice de fotograma, usado cuando `Source` es `custom` (defecto: `1`).
2. **`Frame Dur (ms)` (`frame_dur`):** duración del fotograma en milisegundos ($fd$). Si se omite, se infiere del video ($41.708\text{ ms}$).

### 12.3. Salidas
1. **`[1.1] Time`:** el tiempo convertido en el formato elegido en `Format` (`ms`, `hms` o `sec`).
2. **`[1.2] ASS Time`:** **siempre** la marca en formato ASS (`0:00:00.00`), sea cual sea el valor de `Format`.

### 12.4. Modelo
Para el número de fotograma $f$ y la duración de cuadro $fd$:

$$T_{\text{ms}} = f \cdot fd$$

* Si `Format` es `ms`: $T_{\text{out}} = \text{round}(T_{\text{ms}}, 2)$
* Si `Format` es `sec`: $T_{\text{out}} = \text{round}\left(\frac{T_{\text{ms}}}{1000}, 3\right)$
* Si `Format` es `hms`: $T_{\text{out}} = \text{format\_time}(T_{\text{ms}})$

### 12.5. Ejemplo
Dentro de un bucle `Loops/MaxLoop (fbf)`, usar `Frame to Time` con `Source: j` para obtener el tiempo transcurrido en cada fotograma. La salida puede alimentar `Base (ms)` de `Time/Offset`, o el factor de interpolación $t$ en curvas Bézier y deformaciones vectoriales:

```
[Loops/MaxLoop: fbf] ──► Contexto j
                              │
[Time/Frame to Time: source=j, format=ms] ──► Time ──► Base (ms) ──► [Time/Offset: offset_ms=syl.start_time]
                                                                           └──► Time (ms) ──► Start Time ──► [System/Output]
```
Cada línea FBF generada recibe su tiempo de inicio absoluto de video ($T = T_{\text{syl\_start}} + j \cdot fd$), así las animaciones quedan ajustadas cuadro a cuadro en Aegisub.

---

## 13. `Time/Ipol`

Divide una duración total ($D_{\text{ms}}$) en una secuencia ordenada de sub-intervalos $[t_0, t_1], [t_1, t_2], \dots$ y aplica una curva de aceleración por potencia (`accel`) sobre una lista de *keyframes* o puntos de control.

![Time/Ipol](img/ipol.jpg)

### 13.1. Entradas y Propiedades
1. **`Duration (ms)` (`dur_ms`):** duración total a subdividir, en milisegundos. Si está vacío o desconectado, usa la duración de la unidad activa (`unit.duration` $\to 1000\text{ ms}$) (defecto: `"syl.duration"`).
2. **`Points / Values` (`points`):** valores escalares separados por comas que definen las etapas o *keyframes* (ej. `"0, 100"` para $1$ segmento; `"0, 50, 100"` para $2$ segmentos; `"0, 20, 80, 100"` para $3$ segmentos) (defecto: `"0, 100"`).
3. **`Acceleration` (`accel`):** exponente de curvatura, cualquier decimal mayor que cero (defecto: `1.0`):
   * $\text{accel} = 1.0$: interpolación lineal (etapas equiespaciadas).
   * $\text{accel} > 1.0$: curva *ease-in* (arranque lento, aceleración hacia el final).
   * $\text{accel} < 1.0$: curva *ease-out* (arranque rápido, desaceleración progresiva).

### 13.2. Salidas
1. **`[1.1] Data`:** cadena con los sub-intervalos calculados entre corchetes y separados por comas (ej. `"[0.0, 500.0], [500.0, 1000.0]"`).

### 13.3. Modelo
Para una lista de $M$ puntos de control $\{p_0, p_1, \dots, p_M\}$, el número de segmentos es $K = M - 1$.

Para cada índice de corte $k \in \{1, \dots, K\}$, la fracción normalizada es:

$$u_k = \frac{k}{K}, \quad u_k \in (0.0, 1.0]$$

El instante final $t_k$ del segmento $k$ usa la potencia de aceleración:

$$t_k = D_{\text{ms}} \cdot (u_k)^{\text{accel}}$$

Los sub-intervalos son:

$$I_k = [t_{k-1}, t_k] \quad \text{con } t_0 = 0.0\text{ ms}$$

```
t=0 ms                                                  t=D ms
├─────────────────────────┼───────────────────────────────────┤
  Intervalo 1: [t_0, t_1]       Intervalo 2: [t_1, t_2]
```

Ejemplos ($D = 1000\text{ ms}$, Puntos $= \text{"0, 50, 100"}$, $K=2$ segmentos):
* **Lineal ($\text{accel} = 1.0$):**
  * $k=1 \implies u_1 = 0.5 \implies t_1 = 1000 \cdot (0.5)^1 = 500.0\text{ ms} \implies [0.0, 500.0]$
  * $k=2 \implies u_2 = 1.0 \implies t_2 = 1000 \cdot (1.0)^1 = 1000.0\text{ ms} \implies [500.0, 1000.0]$
  * **Salida `Data`:** `"[0.0, 500.0], [500.0, 1000.0]"`
* **Ease-in cuadrático ($\text{accel} = 2.0$):**
  * $k=1 \implies u_1 = 0.5 \implies t_1 = 1000 \cdot (0.5)^2 = 250.0\text{ ms} \implies [0.0, 250.0]$
  * $k=2 \implies u_2 = 1.0 \implies t_2 = 1000 \cdot (1.0)^2 = 1000.0\text{ ms} \implies [250.0, 1000.0]$
  * **Salida `Data`:** `"[0.0, 250.0], [250.0, 1000.0]"`

### 13.4. Ejemplo
Enviar `Data` a nodos de animación o a constructores de transformaciones `\t` de varias fases en `Script Code`, para dividir la ventana de canto de una sílaba en etapas, por ejemplo un golpe rápido de escala seguido de un retorno suave. Aquí una sílaba de 600 ms se divide en dos etapas con `points="0, 30, 100"` y `accel=1.5`:

```
[Time/Ipol: dur_ms=600, points="0, 30, 100", accel=1.5] ──► Data
```
El nodo devuelve los sub-intervalos `[0.0, 212.1], [212.1, 600.0]`.
En el bloque ASS:
```
{\t(0, 212, \fscx140\fscy140)\t(212, 600, 0.8, \fscx100\fscy100)}
```
El glifo salta al 140% durante los primeros 212 ms (fase de impacto) y vuelve al 100% en los 388 ms restantes con una curva desacelerada.

---

## 14. `Time/Duration`

Calcula la duración en milisegundos entre dos marcas de tiempo ($T_{\text{start}}$ y $T_{\text{end}}$), o devuelve la duración de la unidad activa si las entradas no están conectadas.

![Time/Duration](img/duration.jpg)

### 14.1. Entradas y Propiedades
1. **`Start Time (ms)` (`start_time`):** tiempo inicial en milisegundos o variable de contexto (ej. `line.start_time`, `syl.start_time`) (defecto: `"line.start_time"`).
2. **`End Time (ms)` (`end_time`):** tiempo final en milisegundos o variable de contexto (ej. `line.end_time`, `syl.end_time`) (defecto: `"line.end_time"`).

### 14.2. Salidas
1. **`[1.1] Duration (ms)`:** la diferencia no negativa entre ambas marcas, como entero.

### 14.3. Modelo
Para los tiempos $T_{\text{start}}$ y $T_{\text{end}}$ evaluados en el contexto:

$$D = \max\left(0, \text{round}(T_{\text{end}} - T_{\text{start}})\right)$$

Si las entradas y los campos inline están vacíos, el nodo recurre a la duración del elemento activo:

$$D = \text{unit.duration} \implies \text{syl.duration} \implies \text{line.duration} \implies 0\text{ ms}$$

### 14.4. Ejemplo
Conectar las salidas `Start Time` y `End Time` de `Time/Retime` a `Time/Duration` para obtener la duración exacta de una fase ya desplazada, offsets incluidos, antes de pasarla a curvas Bézier o escalas proporcionales. Aquí la duración controla una velocidad de rotación:

```
[Time/Retime: syl] ──┬──► Start Time ──► Start Time (ms) ──► [Time/Duration]
                     └──► End Time   ──► End Time (ms)   ───────┘   │
                                                                    └──► Duration (ms) ──► In 1 ──► [Basics/Math: div, in2=100]
                                                                                                           └──► Rot Speed
```

Una sílaba corta de 200 ms da giros rápidos de `\frz`; en una vocal sostenida (1200 ms) el giro se estira por todo el intervalo sin aceleraciones bruscas.

---

## 15. `Time/Offset`

Suma o resta milisegundos a una marca de tiempo base. Los valores positivos retrasan y los negativos adelantan.

![Time/Offset](img/offset.jpg)

### 15.1. Entradas y Propiedades
1. **`Base (ms)` (`time_in` / `base`):** marca de tiempo base en milisegundos. Si no está conectada, usa el tiempo de inicio de la unidad activa (`unit.start_time` $\to$ `line.start_time` $\to 0$).
2. **`Offset (ms)` (`offset_ms` / `offset`):** milisegundos a sumar o restar a la base. Acepta números positivos, negativos y expresiones evaluables (defecto: `"100"`).

### 15.2. Salidas
1. **`[1.1] Time (ms)`:** la marca de tiempo tras aplicar el desfase.

### 15.3. Modelo
$$T_{\text{out}} = \text{round}(T_{\text{base}} + \Delta_{\text{offset}})$$

Ejemplos:
* **Retraso:** $T_{\text{base}} = 1000\text{ ms}, \Delta_{\text{offset}} = 250\text{ ms} \implies T_{\text{out}} = 1250\text{ ms}$
* **Adelanto:** $T_{\text{base}} = 1000\text{ ms}, \Delta_{\text{offset}} = -150\text{ ms} \implies T_{\text{out}} = 850\text{ ms}$

### 15.4. Uso
* **Desplazar una ventana de tiempo:** conectarlo a la salida `End Time` de `Time/Retime` con `Offset: 200` para mantener una línea más tiempo en pantalla antes de enviarla a `System/Output`.
* **Puntos de disparo de animaciones:** generar marcas de tiempo intermedias para sincronizar destellos de `Functions/Glitter` o emisiones de partículas justo antes o después del inicio de una sílaba.

### 15.5. Ejemplo
Mantener visible una sombra o un borde exterior después de que termina la línea:

```
[Time/Retime: line] ──► End Time ──► Base (ms) ──► [Time/Offset: offset_ms=250]
                                                           └──► Time (ms) ──► End Time ──► [System/Output]
```

En el bloque ASS:
```
{\pos(line.center, line.middle)\bord5\3c&H000000&\t(line.duration, line.duration + 250, \alpha&HFF&)}
```
El borde sigue visible 250 ms después de que desaparece el texto principal y luego se desvanece hacia negro.

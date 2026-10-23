# Audio

La categoría **Audio** ofrece análisis espectral FFT, extracción de envolventes de energía (RMS y Peak) y formas de onda vectoriales ASSdraw generadas a partir de la pista de audio del proyecto. Contiene los nodos `Audio/Modulator` y `Audio/Waveform`.

---

## Decodificación y Análisis de Audio

Pyxis Effector guarda el audio en búferes contiguos NumPy float32 normalizados en $[-1.0, 1.0]$:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RESOLUCIÓN DE PISTA DE AUDIO                         │
│  default_audio_source ──► audio_file / video_file ──► Archivo local / WAV   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  DECODIFICACIÓN Y BÚFER PCM (AudioData)                     │
│  Frecuencia de muestreo (Hz), Canales, Normalización float32 [-1.0, 1.0]    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
┌──────────────────────────────────────┐ ┌────────────────────────────────────┐
│        ENERGÍA TEMPORAL O(1)         │ │         ESPECTROMETRÍA FFT         │
│  Prefix Sums (Arreglo acumulado de   │ │  Ventana de Hann precalculada,     │
│  cuadrados _sq_cumsum)               │ │  RFFT 2048 puntos, Caché LRU       │
│  ──► RMS y Peak instantáneos         │ │  ──► 16-64 Bandas Logarítmicas     │
└──────────────────┬───────────────────┘ └─────────────────┬──────────────────┘
                   │                                       │
                   ▼                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MODULACIÓN Y RENDERIZADO                           │
│  • Audio/Modulator ──► Cadenas \t(t1,t2,\tag...) o Valores de Color / Alfa  │
│  • Audio/Waveform  ──► Trazados vectoriales ASSdraw m...l...                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Nodo `Audio/Modulator` (Modulador Espectral de Tags ASS)

Muestrea la energía del audio en una ventana temporal, la filtra por banda de frecuencia y la suaviza con un filtro paso bajo. El resultado controla cualquier etiqueta ASS continua (`\fscy`, `\fscx`, `\blur`, `\alpha`, `\1c`, `\3c`, `\frz`, `\bord`). Genera una cadena de transformaciones `\t(t1, t2, \tag...)` o valores interpolados para sub-bucles `Loops/MaxLoop`.

![Audio/Modulator](img/modulator.jpg)

> [!NOTE]
> En modo `custom`, la interfaz muestra los campos adicionales `[Min Hz]` y `[Max Hz]` para el rango de frecuencias de análisis.

### 1.1. Modos de Cabecera
1. **`rms` (`RMS` / `Volumen General`):** Energía cuadrática media en toda la banda audible. Adecuado para pulsos de escala, resplandor y volumen general.
2. **`peak` (`Peak` / `Amplitud Pico`):** Amplitud máxima absoluta instantánea. Adecuado para transitorios secos de percusión, como redoblantes y golpes de batería.
3. **`bass` (`Bass` / `Graves 20-250 Hz`):** Energía en el rango de subgraves y bombo ($20\text{ Hz} \dots 250\text{ Hz}$).
4. **`mids` (`Mids` / `Medios 250-4000 Hz`):** Voz principal, metales, sintetizadores e instrumentos melódicos ($250\text{ Hz} \dots 4000\text{ Hz}$).
5. **`highs` (`Highs` / `Agudos 4-16 kHz`):** Platillos, charles (*hi-hats*), sibilancias y otros transitorios de alta frecuencia ($4000\text{ Hz} \dots 16000\text{ Hz}$).
6. **`custom` (`Custom` / `Banda Personalizada`):** Habilita los cortes `Min Hz` y `Max Hz` para aislar un rango de frecuencias concreto.

### 1.2. Puertos de Entrada y Propiedades del Cuerpo
Las propiedades son de Tipo A (expresión evaluada) salvo que se indique otro tipo.

1. **`Audio Path` (`audio_path`):** Ruta al archivo de audio o vídeo. Si no está conectado ni especificado, Pyxis usa la pista cargada en el proyecto de Aegisub. Tipo C (texto plano / ruta).
2. **`Tag` (`tag_name`):** Etiqueta ASS a animar (ej. `"fscy"`, `"fscx"`, `"blur"`, `"alpha"`, `"1c"`, `"3c"`, `"frz"`, `"bord"`). (Defecto: `"fscy"`). Tipo C (identificador literal de tag ASS).
3. **`Min Val` (`min_val`):** Valor con energía acústica nula ($0.0$). Tipo A / Tipo C polimórfico.
   * *Escalar:* Valor numérico base (ej. `100.0` para escala, `0.0` para desenfoque).
   * *Alfa:* Código hexadecimal de transparencia base (ej. `&HFF&` o `255`).
   * *Color:* Color inicial en formato Web Hex (`#RRGGBB`), ASS (`&HBBGGRR&`) o paleta de colores separados por coma.
4. **`Max Val` (`max_val`):** Valor con energía acústica máxima ($1.0$). Tipo A / Tipo C polimórfico.
5. **`Gain` (`gain`):** Multiplicador lineal de ganancia ($\ge 0.0$, defecto: `1.0`). Sirve para amplificar pistas de bajo nivel.
6. **`Step ms` (`step_ms`):** Intervalo de muestreo en milisegundos ($\ge 10.0\text{ ms}$, defecto: `41.7\text{ ms}` $\approx 24\text{ FPS}$).
7. **`Smoothing` (`smoothing`):** Factor de suavizado exponencial $\alpha \in [0.0, 0.95]$ que atenúa las fluctuaciones abruptas (Defecto: `0.2`).
8. **`Min Hz` / `Max Hz` (`min_hz`, `max_hz`):** Frecuencias de corte inferior y superior en modo `custom` (Hz). (Defecto: `20.0` y `250.0`).
9. **`Start Time` / `End Time` (`start_time`, `end_time`):** Ventana de análisis en milisegundos. Si se omiten, se usa el intervalo del elemento activo (`fx.start_time`, `fx.end_time`).

### 1.3. Puertos de Salida
1. **`[1.1] Tags Out`:** Cadena de etiquetas ASS con las transformaciones temporales concatenadas:
   $$\text{\textbackslash fscy100\textbackslash t}(0, 42, \text{\textbackslash fscy118})\text{\textbackslash t}(42, 83, \text{\textbackslash fscy152})\dots$$
2. **`[1.2] Current Value`:** Valor escalar, código de color ASS o hexadecimal de alfa en el instante activo (`frame_time` o `fx.start_time`).
3. **`[1.3] Values Array`:** Lista con todos los valores muestreados en la ventana de análisis.
4. **`[1.4] Average RMS`:** Promedio de energía cuadrática media ($0.0 \dots 1.0$) en la ventana.

### 1.4. Algoritmos

#### 1.4.1. Energía RMS en $\mathcal{O}(1)$ (Prefix Sums)
Dado el arreglo de muestras normalizadas $x \in [-1.0, 1.0]$ y el vector de sumas acumuladas de cuadrados $S_k = \sum_{j=0}^{k-1} x_j^2$:

$$\text{RMS}(t_0, t_1) = \sqrt{\frac{S_{\text{end}} - S_{\text{start}}}{\text{end} - \text{start}}} \cdot \text{Gain}$$

Donde $\text{start} = \lfloor t_0 \cdot \frac{f_s}{1000} \rfloor$ y $\text{end} = \lfloor t_1 \cdot \frac{f_s}{1000} \rfloor$, con $f_s$ la tasa de muestreo PCM en Hz.

#### 1.4.2. Suavizado Exponencial (Filtro Paso Bajo)
Para una serie de intensidades brutas $I_0, I_1, \dots, I_N$:

$$S_0 = I_0$$
$$S_k = S_{k-1} + (1 - \alpha) \cdot (I_k - S_{k-1}) \quad \forall k \ge 1$$

Donde $\alpha \in [0.0, 0.95]$ es el parámetro `smoothing`.

#### 1.4.3. Interpolación de Paletas de Color
Si el tag objetivo es de color (`\1c`, `\2c`, `\3c`, `\4c`) y se da una paleta de $M$ colores $[C_0, C_1, \dots, C_{M-1}]$:

$$p = \text{intensity} \cdot (M - 1), \quad \text{idx} = \lfloor p \rfloor, \quad f = p - \text{idx}$$
$$C(t) = C_{\text{idx}} + f \cdot (C_{\text{idx}+1} - C_{\text{idx}})$$

### 1.5. Ejemplo

Escala vertical `\fscy` controlada por los graves y `\blur` controlado por la amplitud de pico:

```
[Audio/Modulator (mode: bass, tag: "fscy", min: 100, max: 155, gain: 1.2)] ──► [In1] ──┐
[Audio/Modulator (mode: peak, tag: "blur", min: 0.5, max: 5.0)]             ──► [In2] ──┼──► [Dynamic Format] ──► Output.Tags
```

* **Plantilla en `Dynamic Format`:**
  ```text
  {\pos(syl.center, syl.middle)%s%s}
  ```
* **Línea ASS compilada resultante:**
  ```ass
  Dialogue: 0,0:01:12.40,0:01:15.80,Romaji,,0,0,0,,{\pos(412.5, 680.0)\fscy100\t(0, 42, \fscy148)\t(42, 83, \fscy112)\blur0.5\t(0, 42, \blur4.2)\t(42, 83, \blur1.1)}Ka
  ```

---

## 2. Nodo `Audio/Waveform` (Osciloscopios y Espectrogramas Vectoriales)

Genera trazados vectoriales ASSdraw (`m ... l ...`) a partir de la señal de audio instantánea. Puede dibujar osciloscopios de cinta continua, ecualizadores de barras espectrales, ondas rellenas hasta la base, visualizadores circulares polares y matrices de partículas reactivas.

![Audio/Waveform](img/waveform.jpg)

### 2.1. Modos de Cabecera

```
1. Oscilloscope (Cinta):             2. FFT Bars (Ecualizador):
    ┌──┐   /\   ┌──┐                     ┌─┐   ┌─┐   ┌─┐
────┘  └──/  \──┘  └────                 │ │ ┌─┤ │ ┌─┤ │ ┌─┐
                                         │ │ │ │ │ │ │ │ │ │
3. Filled Wave (Relleno):            4. Radial (Anillo Polar):
     /\     /\                                 ● ─── ●
    /  \   /  \                               /   ●   \
  ─/────\_/────\────────                     ●    |    ●
  ██████████████████████                      \   ●   /
                                               ● ─── ●
```

1. **`oscilloscope` (`Oscillo` / `Cinta Continua`):** Trazo continuo en cinta de grosor uniforme (`Thickness`) que sigue la forma de onda en el tiempo.
2. **`fftbars` (`Bars` / `Barras de Espectro`):** Gráfico de barras de ecualizador calculado con RFFT en bandas de frecuencia.
3. **`filledwave` (`Filled` / `Onda Rellena`):** Polígono cerrado que une la curva de la onda con la línea de base inferior.
4. **`radial` (`Radial` / `Visualizador Circular`):** Anillo polar donde las frecuencias o amplitudes modulan el radio exterior respecto al centro.
5. **`points` (`Points` / `Nube de Partículas`):** Rectángulos desconectados centrados en cada muestra de la onda.

### 2.2. Puertos de Entrada y Propiedades del Cuerpo
Las propiedades son de Tipo A (expresión evaluada) salvo que se indique otro tipo.

1. **`Audio Path` (`audio_path`):** Ruta a la pista de audio, o resolución automática desde Aegisub. Tipo C (texto plano / ruta).
2. **`Width` (`width`):** Anchura total del cuadro delimitador en píxeles (Defecto: `400.0 px`).
3. **`Height` (`height`):** Altura máxima del área gráfica en píxeles (Defecto: `60.0 px`).
4. **`Samples` (`samples`):** Número de muestras temporales o bandas espectrales ($4 \dots 512$, Defecto: `32`).
5. **`Gain` (`gain`):** Factor de escala de amplitud ($\ge 0.01$, Defecto: `1.0`).
6. **`Thickness` (`thickness`):** Grosor del trazo en píxeles para los modos `oscilloscope` y `points` ($\ge 1.0\text{ px}$, Defecto: `2.0 px`).
7. **`Scale` (`scale`):** Multiplicador de deflexión vertical o expansión radial ($\ge 0.01$, Defecto: `1.0`).
8. **`Min Hz` / `Max Hz` (`min_hz`, `max_hz`):** Rango de frecuencia del análisis FFT en los modos `fftbars` y `radial` ($20\text{ Hz} \dots 16000\text{ Hz}$).
9. **`Start Time` / `End Time` (`start_time`, `end_time`):** Ventana de extracción de muestras en milisegundos.

### 2.3. Puertos de Salida
1. **`[1.1] Shape Out`:** Un único trazado ASSdraw cerrado (`m ... l ...`), listo para `System/Output` o para nodos de la categoría `Shape`.
2. **`[1.2] \pos Tag`:** Etiqueta ASS de posición calculada en el centro geométrico: `\pos(cx, cy)`.
3. **`[1.3] X Array`:** Coordenadas horizontales $X$ de todos los vértices generados.
4. **`[1.4] Y Array`:** Coordenadas verticales $Y$ de todos los vértices generados.
5. **`[1.5] Bands Array`:** Amplitudes o energías espectrales normalizadas ($0.0 \dots 1.0$) de cada banda.

### 2.4. Fórmulas Geométricas

#### 2.4.1. `Oscilloscope` (Cinta Bipolígono)
Para cada muestra temporal $s_i \in [-1.0, 1.0]$ con $i \in [0, N-1]$ y grosor $T$:

$$p_x(i) = \frac{i}{N - 1} \cdot W$$
$$p_y(i) = \frac{H}{2} - s_i \cdot \frac{H}{2} \cdot \text{Scale}$$
$$\text{Top}(i) = \left(p_x(i), p_y(i) - \frac{T}{2}\right), \quad \text{Bottom}(i) = \left(p_x(i), p_y(i) + \frac{T}{2}\right)$$

El trazado recorre todos los puntos $\text{Top}$ de izquierda a derecha y vuelve por los puntos $\text{Bottom}$ en orden inverso:

$$\text{Shape} = \text{m } \text{Top}_0 \text{ l } \text{Top}_1 \dots \text{Top}_{N-1} \text{ l } \text{Bottom}_{N-1} \dots \text{Bottom}_0$$

#### 2.4.2. `Radial` (Proyección Polar)
Para $N$ muestras repartidas uniformemente en la circunferencia:

$$\theta_i = \frac{2\pi i}{N}, \quad R_i = R_{\text{base}} + \text{val}_i \cdot R_{\max} \cdot \text{Scale}$$
$$P_x(i) = c_x + R_i \cos(\theta_i), \quad P_y(i) = c_y + R_i \sin(\theta_i)$$

$$\text{Shape} = \text{m } P_0 \text{ l } P_1 \dots \text{ l } P_{N-1} \text{ l } P_0$$

#### 2.4.3. `FFT Bars` (Ecualizador)
Para $N$ bandas logarítmicas con paso $W_{\text{slot}} = \frac{W}{N}$ y ancho de barra $W_{\text{bar}} = 0.8 \cdot W_{\text{slot}}$:

$$x_0(i) = i \cdot W_{\text{slot}}, \quad x_1(i) = x_0(i) + W_{\text{bar}}$$
$$h_i = \max(1.0, \min(H, \text{val}_i \cdot H \cdot \text{Scale}))$$
$$y_0 = H, \quad y_1(i) = H - h_i$$

Cada barra se escribe como un rectángulo cerrado independiente:

$$\text{Bar}_i = \text{m } x_0(i) \text{ } y_0 \text{ l } x_0(i) \text{ } y_1(i) \text{ l } x_1(i) \text{ } y_1(i) \text{ l } x_1(i) \text{ } y_0$$

### 2.5. Ejemplo

Ecualizador espectral reactivo generado fotograma a fotograma (FBF) con `Loops/MaxLoop`:

* **Conexión en el grafo:**
  ```
  [Loops/Main Loop (line)] ──► [Loops/MaxLoop (mode: fbf)] ──► [Audio/Waveform (mode: fftbars, samples: 16, width: 320, height: 40)] ──► Output.Tags
  ```
* **Línea ASS compilada resultante (fotograma 1):**
  ```ass
  Dialogue: 0,0:01:12.40,0:01:12.44,Romaji,,0,0,0,,{\an5\pos(640, 680)\p1\1c&H00FFFF&}m 0 40 l 0 18.2 l 16 18.2 l 16 40 m 20 40 l 20 8.5 l 36 8.5 l 36 40
  ```

### 2.6. Combinaciones con Otros Nodos

1. **Sub-bucles fotograma a fotograma (*FBF*) con `Loops/MaxLoop`:** Si `Loops/MaxLoop (fbf)` va antes de `Audio/Waveform`, `fx.start_time` y `fx.end_time` se actualizan en cada cuadro del vídeo, lo que da osciloscopios reactivos sin latencia.
2. **Recorte dinámico de texto (`\clip`):** Conectar `Shape Out` al puerto `Clip` de `Basics/MultiTag`, o pasarlo por `Functions/Clip Gradient`, crea máscaras de recorte que descubren el texto del karaoke al ritmo de la música.
3. **Partículas reactivas al audio:** Conectar `Shape Out` a la entrada `Path / Origin` de `Functions/Particles` hace que el enjambre se emita desde las crestas y picos de la onda.

---

## 3. Comparativa de Nodos de Audio

| Parámetro / Característica | `Audio/Modulator` | `Audio/Waveform` |
| :--- | :--- | :--- |
| **Tipo de Salida Principal** | Cadenas de Tags ASS animadas (`\t`) | Trazados vectoriales ASSdraw (`m...l...`) |
| **Dominio de Análisis** | RMS, Peak, Graves, Medios, Agudos, Banda Custom | Dominio temporal (PCM) y Frecuencial (RFFT) |
| **Topologías Disponibles** | Escalar / Color / Alfa / Cadenas `\t` | Oscilloscope, FFT Bars, Filled, Radial, Points |
| **Soporte de Paletas de Color** | Sí (interpolación continua RGB/Hex) | N/A (Geometría vectorial pura) |
| **Compatibilidad FBF** | Sí (vía `Current Value` [Slot 1.2]) | Nativo (Genera una geometría distinta por cuadro) |
| **Tipificación de Entradas** | Tipo A (numéricas/expresiones), Tipo C (tags/rutas) | Tipo A (dimensiones/frecuencias), Tipo C (rutas/modos) |
| **Uso Primario en FX** | Resplandor, rebote, escala y color al ritmo de la música | Ecualizadores visuales, osciloscopios y fondos reactivos |

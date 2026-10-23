# Entorno Base y Personalización

El **Entorno Base** (`preview_base.ass`) es un espacio de trabajo aislado para previsualizar y probar efectos sin usar el archivo de subtítulos cargado en Aegisub.
Esta página cubre el ciclo de vida del archivo en `%APPDATA%`, la ventana temporal del clip, su estructura de estilos y la recarga en caliente.

---

## 1. Arquitectura y Modos de Previsualización

El nodo **`System/Previewer`** tiene un selector de origen con dos modos:

* **Modo Proyecto Activo (Icono Aegisub):** El reproductor usa el vídeo, audio, estilos y líneas de diálogo cargados en la sesión activa de Aegisub.
* **Modo Plantilla Base (Icono Disco CD):** El reproductor se desvincula de Aegisub y proyecta el resultado del grafo sobre `preview_base.ass`, un entorno de pruebas fijo y reproducible.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MODOS DE PREVISUALIZACIÓN                          │
├──────────────────────────────────────┬──────────────────────────────────────┤
│                                      │                                      │
│                 ┌────────────────────┴────────────────────┐                 │
│                 ▼                                         ▼                 │
│  ┌──────────────────────────────┐       ┌────────────────────────────────┐  │
│  │   MODO AEGISUB (Icono Aegi)  │       │   MODO BASE (Icono Disco CD)   │  │
│  │   • Script de trabajo activo │       │   • Sandbox aislado %APPDATA%  │  │
│  │   • Vídeo/Audio del proyecto │       │   • Media de laboratorio fija  │  │
│  │   • Diálogos reales activos  │       │   • Karaoke patrón controlado  │  │
│  └──────────────────────────────┘       └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Ciclo de Vida y Persistencia en `%APPDATA%`

### 2.1. Ubicación en el Sistema
El archivo base está en el directorio de configuración del perfil de usuario de Windows:

```
%APPDATA%\PyxisNodes\preview_base.ass
```

*(Ruta estándar: `C:\Users\<Usuario>\AppData\Roaming\PyxisNodes\preview_base.ass`)*.

### 2.2. Política de No Sobrescritura
Pyxis Effector nunca sobrescribe su copia del archivo:
1. **Primera ejecución:** Si el archivo no existe en `%APPDATA%\PyxisNodes\`, el motor copia la plantilla por defecto incluida en la instalación.
2. **Actualizaciones:** Una vez creado, **Pyxis jamás sobrescribe ni elimina este archivo**. Sus estilos, resoluciones, enlaces de vídeo y textos de prueba son del usuario y persisten entre versiones.

### 2.3. Detección por Hash SHA-256 (Recarga en Caliente)
No hace falta reiniciar la aplicación ni reinstanciar el nodo `System/Previewer` tras editar el entorno base. El backend comprueba el hash del archivo:
* En cada compilación de previsualización, el motor calcula el hash `SHA-256` de `preview_base.ass` en disco.
* Si el usuario edita y guarda `preview_base.ass` en Aegisub o en un editor de texto externo, el cambio de hash invalida la caché en memoria (`_cached_preview_base_info`).
* El visor actualiza de inmediato la resolución, la tasa de fotogramas, la pista sonora y la geometría tipográfica.

---

## 3. Ventana Temporal del Clip

Pyxis no limita la reproducción a la duración de las sílabas del archivo base. Añade un **margen de entrada y salida (*lead-in / lead-out*)** para poder ver completas las transiciones de entrada y salida.

### 3.1. Ecuaciones

Sea $\mathcal{D} = \{d_1, d_2, \dots, d_m\}$ el conjunto de líneas de diálogo de `preview_base.ass`, donde cada línea tiene una marca de inicio $t_{\text{start}}(d_i)$ y de fin $t_{\text{end}}(d_i)$ en milisegundos:

$$t_{\text{min}} = \min_{d \in \mathcal{D}} \big(t_{\text{start}}(d)\big)$$

$$t_{\text{max}} = \max_{d \in \mathcal{D}} \big(t_{\text{end}}(d)\big)$$

A partir de estos extremos, el motor calcula el intervalo del clip en segundos:

$$t_{\text{clip\_start}} = \max\left(0.0, \; \frac{t_{\text{min}} - 2000}{1000.0}\right)$$

$$t_{\text{clip\_end}} = \frac{t_{\text{max}} + 2000}{1000.0}$$

$$T_{\text{clip\_dur}} = \max\left(2.0, \; t_{\text{clip\_end}} - t_{\text{clip\_start}}\right)$$

$$t_{\text{clip\_start\_ms}} = \lfloor t_{\text{clip\_start}} \times 1000 \rfloor$$

### 3.2. Para Qué Sirve el Margen de 2000 ms
* **Nodos `Time/Lead In`:** Las animaciones que empiezan antes de la sílaba (aproximaciones desde fuera de pantalla, aceleraciones exponenciales `accel`, apariciones progresivas) disponen de hasta 2000 ms previos.
* **Nodos `Time/Lead Out`:** Las transiciones posteriores (`\fad`, dispersión de partículas, disolución alfa) disponen de 2000 ms de reproducción adicional antes de que el bucle vuelva a empezar.
* **Scrubber:** La barra de transporte de `Previewer` mapea el tiempo relativo $00:00$ a $t_{\text{clip\_start\_ms}}$, de modo que no hay tiempo muerto al inicio de la línea de tiempo.

---

## 4. Estructura de `preview_base.ass`

`preview_base.ass` es un archivo ASS estándar (*v4.00+*) con cuatro secciones:

```ini
[Script Info]
; Configuración global de lienzo y resolución
Title: Default Aegisub file
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 1000
PlayResY: 260

[Aegisub Project Garbage]
; Vinculación de fuentes multimedia (Vídeo y Audio)
Last Style Storage: Default
Audio File: dummy-audio:silence?sr=44100&bd=16&ch=1&ln=396900000
Video File: ?dummy:23.976000:361:1000:260:150:150:150:c
Video AR Value: 3.846154
Video Zoom Percent: 1.187500
Active Line: 1
Video Position: 120

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,65,&H00FFFFFF,&H000000FF,&H007A3419,&H007A1C42,0,0,0,0,100,100,0,0,1,2,2,2,10,10,100,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,0:00:05.00,0:00:10.00,Default,,0,0,0,,{\k43}Ma{\k65}ry {\k44}te{\k87}nía {\k65}un {\k65}cor{\k44}de{\k43}ri{\k44}to
```

---

## 5. Guía de Personalización

### 5.1. Paso 1: Configurar la Resolución del Lienzo (`PlayResX` / `PlayResY`)
La resolución del encabezado define el plano de coordenadas para los anclajes absolutos y relativos:
* **Full HD (1080p):**
  ```ini
  PlayResX: 1920
  PlayResY: 1080
  ```
* **HD (720p):**
  ```ini
  PlayResX: 1280
  PlayResY: 720
  ```
> [!NOTE]
> El renderizador WebAssembly (`JASSUB`) y el reproductor de vídeo se adaptan automáticamente a la relación de aspecto ($\text{AR} = \text{PlayResX} / \text{PlayResY}$) y escalan los fotogramas sin distorsión anamórfica.

### 5.2. Paso 2: Configurar los Medios de Referencia
En la sección `[Aegisub Project Garbage]` se define el material de prueba:

#### Opción A: Vídeo Virtual Sintético (*Dummy Video* - Recomendado)
Arranca al instante a 23.976 o 60 FPS y no necesita ningún archivo de vídeo en disco:
```ini
Video File: ?dummy:23.976000:40000:1920:1080:26:26:26:
```
* **Sintaxis:** `?dummy:<FPS>:<Fotogramas>:<Ancho>:<Alto>:<R>:<G>:<B>:`
* Los valores `26:26:26:` dan un fondo gris oscuro neutro, con buen contraste para partículas blancas, sombras y contornos de color.

#### Opción B: Archivos Locales de Vídeo y Audio
Para calibrar sincronismo labial, modulación con `Audio/Modulator` o transitorios con `Audio/Waveform`, apunte a un archivo multimedia local:
```ini
Video File: C:\KaraokeResources\test_track_1080p.mp4
Audio File: C:\KaraokeResources\test_track_1080p.mp4
```
> [!TIP]
> Si el vídeo tiene una pista de audio integrada, basta con indicar `Video File`; Pyxis extrae el audio y lo envía automáticamente al motor PCM y al analizador espectral.

### 5.3. Paso 3: Ajustar el Estilo Base (`[V4+ Styles]`)
Pyxis lee `[V4+ Styles]` y usa el **primer estilo definido** como referencia:
* **`Fontname`:** Familia tipográfica instalada en el sistema o ubicada en `%APPDATA%\PyxisNodes\fonts\`.
* **`Fontsize`:** Altura del texto en píxeles de guion (ej. `65` a `80` para 1080p).
* **`PrimaryColour` (`&HAABBGGRR&`):** Color de relleno del glifo.
* **`Outline` y `OutlineColour`:** Grosor y color del contorno inicial.
* **`Alignment`:** Anclaje ASS estándar (`5` para centro de pantalla o `2` para subtítulos inferiores).

### 5.4. Paso 4: Definir la Frase de Prueba en `[Events]`
Use una frase con sílabas de duraciones variadas y distintas formas de glifo:
```ini
Dialogue: 0,0:00:03.00,0:00:09.00,Default,,0,0,0,,{\k45}Kyou{\k40}kai {\k60}no {\k50}Ka{\k55}na{\k70}ta
```
* **Sílabas cortas ($\le 200\text{ ms}$):** Ideales para validar impactos de alta velocidad, transiciones rápidas (*snap eases*) y rebotes elásticos (*Bounce* / *elastic rebounds*).
* **Sílabas largas ($\ge 600\text{ ms}$):** Ideales para observar osciladores continuos (`Tag Oscillator`), gradientes dinámicos o emisiones de partículas sostenidas.
* **Glifos complejos:** Incluya kanjis densos si trabaja con formas vectoriales, o caracteres con islas cerradas (ej. `B`, `P`, `o`, `8`), para verificar las operaciones booleanas de unión y corte en Clipper2, así como la orientación y las reglas de devanado (*winding rules*) de los polígonos.

---

## 6. Plantilla de Referencia Full HD 1080p

Plantilla de `preview_base.ass` para Full HD 1080p a 23.976 FPS con fondo neutro de alto contraste:

```ini
[Script Info]
; Archivo Base Personalizado de Laboratorio - Pyxis Effector
Title: Pyxis Sandbox Environment
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1920
PlayResY: 1080

[Aegisub Project Garbage]
Video File: ?dummy:23.976000:40000:1920:1080:24:28:32:
Audio File: ?dummy:23.976000:40000:1920:1080:24:28:32:

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Cinzel Decorative,76,&H00FFFFFF,&H000000FF,&H00141619,&H80000000,1,0,0,0,100,100,1.5,0,1,3.0,1.5,5,40,40,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:03.00,0:00:08.50,Default,,0,0,0,,{\k45}Py{\k35}xis {\k60}Ef{\k50}fec{\k40}tor {\k75}Nodes
```

---

## 7. Flujos de Trabajo Recomendados

1. **Compartir plantillas:**
   * Al exportar grafos o plantillas para otros usuarios, deje el vídeo en modo `?dummy:...`. Así cualquiera podrá abrir y previsualizar la plantilla sin depender de rutas de vídeo que no existen en su máquina.
2. **Fuentes locales:**
   * Para tipografías experimentales, coloque los archivos `.ttf` o `.otf` en `%APPDATA%\PyxisNodes\fonts\`. Pyxis vectoriza y renderiza estas fuentes localmente mediante FreeType/HarfBuzz y libass, sin necesidad de instalarlas en Windows.
3. **Restablecimiento de fábrica:**
   * Para volver a la configuración original, cierre Pyxis Effector, elimine `%APPDATA%\PyxisNodes\preview_base.ass` y reinicie la aplicación; el motor regenerará una copia limpia.

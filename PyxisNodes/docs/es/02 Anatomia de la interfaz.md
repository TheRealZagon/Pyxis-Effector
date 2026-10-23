# Anatomía de la Interfaz

Pyxis Effector es un espacio de trabajo de grafos de nodos: un lienzo principal de edición rodeado de unos pocos paneles de control.

---

## 1. Distribución General del Espacio de Trabajo

La ventana principal tiene cuatro zonas:

```
+-------------------------------------------------------------------------------+
| [1] BARRA SUPERIOR (TOP BAR)                                                  |
+-------------------------------------------------------------------------------+
|                                                                               |
|                                                                               |
| [2] LIENZO DE TRABAJO (CANVAS WORKSPACE)                                      |
|     (Nodos, puertos de conexión, cables de datos y enlaces de flujo)          |
|                                                                               |
|                                                                               |
|                                                        +----------------------+
| [3] BARRA DE HERRAMIENTAS FLOTANTE                     | [4] NOTIFICACIONES   |
+-------------------------------------------------------------------------------+
```

1. **Barra Superior (*Top Bar*):** Guardar/exportar, biblioteca de plantillas, preferencias globales y generación de capas.
2. **Lienzo de Trabajo (*Canvas Workspace*):** Área bidimensional donde se añaden, organizan y conectan los nodos.
3. **Barra de Herramientas Flotante (*Canvas Toolbar*):** Navegación, zoom, centrado de cámara e historial (*undo/redo*).
4. **Sistema de Notificaciones (*Toast System*):** Alertas no invasivas en la esquina inferior derecha con estado, diagnóstico y tiempos de procesamiento.

---

## 2. Barra Superior (*Top Bar*) y Control de Generación

La barra superior está fija en el margen superior de la ventana:

```
+-------------------------------------------------------------------------------------------------+
| [1] Marca y Versión | [2] Guardar | [3] Guardar Como | [4] Biblioteca | [5] Ajustes | [6] Generar Capas |
+-------------------------------------------------------------------------------------------------+
```

1. **Identificador de Versión:** Nombre del motor y distintivo de versión (`v<versión>`).

2. **Guardar (`Save` / `Ctrl+S`):** Guarda los cambios en la plantilla o el archivo abierto.

3. **Guardar Como (`Save as...`):** Exporta el grafo completo a un archivo `.json` externo, para respaldo o distribución.

4. **Biblioteca de Plantillas (`Library`):** Abre una ventana modal para buscar, etiquetar, categorizar y cargar plantillas predefinidas o propias. Permite filtrar por Favoritos, Recientes y Plantillas de Sistema.

5. **Guardado Rápido (`Quick Save`):** Se activa al editar una plantilla cargada de la biblioteca y la sobrescribe con un solo clic.

6. **Ajustes (`Settings`):** Tema visual del lienzo, fondo (vídeo activo de Aegisub, imagen de referencia o color sólido), idioma y opciones de aceleración gráfica.

7. **Generar Capas (`Generate Layers`):** Compila el grafo y escribe las líneas de diálogo generadas en el script ASS activo de Aegisub. Incluye una barra de progreso.

8. **Tarjeta de Estimación de Carga (*Workload Estimation Card*):** Aparece al situar el cursor sobre **Generate Layers**:
   * **Líneas a generar:** Cantidad estimada de eventos de diálogo ASS que se escribirán en el script.
   * **Líneas de entrada:** Número de líneas de subtítulo seleccionadas en Aegisub para procesar.
   * **Unidades base:** Total de sílabas, palabras o caracteres, según el iterador activo en `Main Loop`.
   * **Alerta de Carga Masiva:** Aviso visual si la complejidad combinada del grafo supera los umbrales de cómputo recomendados.

---

## 3. Lienzo de Trabajo (*Canvas Workspace*)

Espacio bidimensional para editar el grafo, con navegación libre, zoom y selección múltiple.

### 3.1. Arquitectura de Capas Visuales (*Z-Index Stacking*)
1. **Capa de Fondo:** Fondo neutro, imagen estática o vídeo cargado desde Aegisub, como referencia espacial.
2. **Capa Principal de Nodos (`#node_canvas`):** Cajas de nodos, títulos, puertos de conexión, campos de texto y widgets interactivos.
3. **Capa de Conexiones y Selección (`#node_canvas_fg`):** Curvas Bézier de los cables, marcos de selección múltiple y guías de alineación magnética.

### 3.2. Barra de Herramientas Flotante (*Canvas Toolbar*)
Situada en la esquina inferior izquierda:

1. **Deshacer (`Undo` / `Ctrl+Z`):** Revierte la última modificación del lienzo.
2. **Rehacer (`Redo` / `Ctrl+Y`):** Restaura la última acción deshecha.
3. **Centrar Vista (`Home` / `Reset View`):** Mueve la cámara para encuadrar todos los nodos con un zoom óptimo.
4. **Acercar Zoom (`Zoom In` / `+`):** Acerca la vista hacia su centro.
5. **Alejar Zoom (`Zoom Out` / `-`):** Aleja la vista para ver el grafo completo.
6. **Cargar Grafo Predeterminado (`Default Preset`):** Restablece el lienzo al grafo inicial (`Main Loop` $\to$ `Output`).

---

## 4. Anatomía Estructural de un Nodo

Estructura estándar de un nodo en el lienzo:

```
+-------------------------------------------------------------+
| [1] CABECERA: Nombre del Nodo      [4] Selector de Modo [v] |
+-------------------------------------------------------------+
| [2] ENTRADAS Y CAMPOS INLINE          |  [3] PUERTOS SALIDA |
| (o) [ Loop In                   ]     |        Loop Out (o) |
| (o) [ 100.0 (o placeholder)     ]     |          Result (o) |
| (o) [                           ]     |        Data Out (o) |
+-------------------------------------------------------------+
| [5] BORDE DE SELECCIÓN Y ESTADO       [6] BADGE / ITERADOR  |
+-------------------------------------------------------------+
```

1. **Cabecera del Nodo:**
   * Muestra el nombre del nodo con el color de su categoría.
   * Se arrastra para mover el nodo; con doble clic se colapsa o expande el cuerpo.

2. **Puertos de Entrada con Campos Integrados (*Inline Input Fields*):**
   * Cada entrada del lateral izquierdo tiene un conector circular `(o)` y un **campo de texto editable**.
   * **Texto de ayuda (*placeholder*):** Con el campo vacío, muestra en color tenue el nombre del parámetro y su valor predeterminado (ej. `Min`, `Max`, `Delay (ms)`).
   * **Prioridad cable vs. campo:** Si se escribe una constante o expresión en el campo, el nodo evalúa ese valor. Si se conecta un cable al conector `(o)`, **el dato del cable tiene prioridad absoluta** y el campo se ignora.
   * **Excepción (`Output`):** El nodo terminal `Output` no tiene campos inline; muestra etiquetas de asignación directa (`Loop / Domain`, `Layer`, `Start Time`, etc.).

3. **Puertos de Salida (*Outputs*, Lateral Derecho):**
   * Conectores circulares junto al nombre del dato que emiten (`Loop Out`, `Data`, `Result`, `Shape Out`, `\t Out`, etc.).

4. **Selectores de Modo en Cabecera (*Header Mode Combos*):**
   * Menús desplegables en el extremo derecho del título.
   * Cambian el algoritmo o comportamiento del nodo (ej. `syl / char / word / line` en `Main Loop`, `Normal / FBF` en `MaxLoop`, modos en `Manipulator` o `Python / Lua` en `Script Code`) y reconfiguran las entradas del cuerpo.

5. **Borde de Selección y Estado:**
   * Resplandor en el perímetro cuando el nodo está seleccionado o en edición.

6. **Badges e Información al Pie (*Footers / Badges*):**
   * Muestran las variables de iteración expuestas al contexto (`s_i, s_n` en Slicer, `a_i, a_n` en Array, `b_i, b_n` en Concentric Borders, `ish_i, ish_n` en IMG to Shape) o estados especiales del nodo (`Single shape.`, `ALL`, `SELEC.`, `NO BLANK`).

---

## 5. Clasificación de Nodos por Categoría y Código de Color

Pyxis tiene 67 nodos en 8 categorías, cada una con su color:

| Categoría Canónica | Nombre en UI | Rol Funcional | Ejemplos de Nodos | Color |
| :--- | :--- | :--- | :--- | :--- |
| **`Basics`** | `Básicos` | Constantes numéricas, cadenas, operaciones matemáticas, formateo dinámico y control simple. | `Math`, `Number`, `String`, `Text`, `Color Picker`, `MultiRandom`, `Concatenate`, `Once`, `Only` | Azul Celeste (`#4A90E2`) |
| **`Shape`** | `Shape` | Primitivas, cortes booleanos (Clipper2), trazados, transformaciones afines, deformaciones y mallas. | `Library`, `Slicer`, `Manipulator`, `Transform`, `Filter`, `Concentric Borders`, `Stroke`, `Array`, `IMG to Shape` | Verde Esmeralda (`#2ECC71`) |
| **`Time`** | `Tiempo` | Sincronización temporal, re-tiempo acelerado (`\t`), interpolación paramétrica (`Ipol`) y desfases. | `Retime`, `Lead In`, `Lead Out`, `Synced`, `Middle 1/2`, `Loop 1/2`, `Ipol`, `Duration`, `Offset` | Naranja Dorado (`#F39C12`) |
| **`Functions`** | `Funciones` | Moduladores de tags, osciladores de onda, gradientes de color, splines Bézier y partículas. | `Tag Manipulator`, `Tag Oscillator`, `Color Gradient`, `Clip Gradient`, `Bezier Curve`, `Particles`, `Text to Shape` | Púrpura Violeta (`#9B59B6`) |
| **`Variables`** | `Variables` | Variables de contexto ASS, memoria persistente clave-valor y generadores de variables dinámicas. | `Sys Var`, `Define Vars`, `Get Var`, `Memory` | Turquesa (`#1ABC9C`) |
| **`Loops`** | `Bucles` | Descomposición de líneas, multiplicadores de eventos y pasos modulares. | `Main Loop`, `MaxLoop`, `Module` | Rojo Coral (`#E74C3C`) |
| **`Audio`** | `Audio` | Análisis espectral de audio (FFT), extracción de envolventes RMS/Peak y formas de onda vectoriales. | `Modulator`, `Waveform` | Amarillo Ámbar (`#F1C40F`) |
| **`System`** | `Sistema` | Ensamblado final del ASS, previsualización acelerada WASM, scripts de código y pruebas de rendimiento. | `Output`, `Previewer`, `Script Code`, `Benchmark Math` | Gris Acero (`#7F8C8D`) |

---

## 6. Navegación, Gestos y Atajos de Teclado

| Acción | Control de Ratón / Teclado | Resultado |
| :--- | :--- | :--- |
| **Moverse por el lienzo (Paneo)** | Botón central del ratón (pulsar rueda) o Clic derecho y arrastre | Desplaza la cámara en cualquier dirección. |
| **Ajustar Zoom** | Rueda del ratón (*Scroll*) | Acerca o aleja la vista de forma continua. |
| **Seleccionar / Mover Nodo** | Clic izquierdo sobre cabecera y arrastre | Selecciona y mueve nodos individualmente. |
| **Selección Múltiple** | Clic izquierdo sostenido en fondo vacío | Traza un cuadro rectangular de selección. |
| **Crear Conexión (Cable)** | Arrastre desde puerto de salida `(o)` a puerto de entrada `(o)` | Conecta dos nodos compatibles con un cable elástico. |
| **Desconectar Puerto** | Clic sobre un puerto conectado | Desconecta y retira el cable. |
| **Menú Contextual de Creación** | Clic derecho en fondo vacío del lienzo | Abre el catálogo y buscador rápido de nodos. |
| **Eliminar Nodos / Cables** | Tecla `Supr` (*Delete*) o `Retroceso` (*Backspace*) | Elimina los elementos seleccionados. |
| **Duplicar Nodos** | `Ctrl + D` o `Ctrl + C` / `Ctrl + V` | Clona los nodos seleccionados conservando sus parámetros. |
| **Guardar Proyecto / Plantilla** | `Ctrl + S` | Guarda los cambios del grafo activo. |
| **Deshacer / Rehacer** | `Ctrl + Z` / `Ctrl + Y` | Recorre el historial de cambios del lienzo. |
| **Centrar Vista en el Grafo** | Tecla `Home` o botón en barra de herramientas | Encuadra todos los nodos en la ventana. |
| **Consola de Depuración Integrada** | Tecla `F1` (o `Esc` para cerrar) | Abre la consola de logs en tiempo real (operativa incluso durante la inicialización de la ventana). |

---

## 7. Ventanas Modales y Editores Especializados

1. **Editor de Código Script (`Script Code`):**
   * Editor para Python y Lua con resaltado de sintaxis, numeración de líneas y validación de errores en vivo (bloques `end` sin cerrar, dos puntos faltantes, delimitadores desparejados).
   * Gestor de plantillas para guardar y cargar funciones reutilizables.

2. **Selector de Color (`Color Picker`):**
   * Rueda cromática HSV/RGB con canal alfa, paletas de muestras predefinidas y exportación directa a formato ASS (`&HBBGGRR&`) y hexadecimal web (`#RRGGBB`).

3. **Consola de Depuración (`Debug Console` - `F1`):**
   * Visor de logs y diagnósticos del backend en tiempo real, accesible en cualquier momento (incluso durante la inicialización de la ventana).
   * Filtro de búsqueda en vivo, auto-scroll, copiado al portapapeles y limpieza de registros, sin afectar al proceso ni a las dimensiones de la ventana.

4. **Biblioteca de Plantillas (`Library`):**
   * Catálogo con búsqueda por nombre o etiquetas, previsualización de la cantidad de nodos y verificación de integridad del grafo.

5. **Panel de Telemetría y Estimación de Carga (`Telemetry`):**
   * **Tooltip de estimación previa a la generación (`Generate Layers`):** Al situar el cursor sobre el botón de generación, muestra las líneas estimadas, la **Concurrencia de Líneas** (*Sweep-Line Concurrency*), el **Factor de Expansión**, el **Peso ASS Estimado** (`KB`/`MB`), badges de los subsistemas activos (`FBF`, `Slicer`, `Particles`, `Audio`, `Script`), el resumen del último escaneo y un acceso directo a `Telemetry`.
   * **Panel Telemetry (16:9):** Dividido en tres regiones: visor de vídeo con HUD de telemetría por fotograma (arriba-izquierda); tacómetro de presupuesto (`Frame Budget %`), tarjetas KPI y lista de puntos críticos (arriba-derecha); y un gráfico superpuesto con minimapa y navegación 2D (`Rueda` zoom X en cursor, `Ctrl/Shift + Rueda` escala Y, `Botón Central` paneo 2D, `Clic Izquierdo` desplazamiento temporal de vídeo y `R`/`Home` para restablecer vista).

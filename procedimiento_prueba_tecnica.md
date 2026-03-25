# Procedimiento y Paso a Paso - Prueba Técnica Chacutería Foods

Este documento describe la metodología, enfoques y cada una de las actividades realizadas durante el desarrollo de la prueba técnica.

## 1. Entendimiento del Problema

Lo primero que hice fue leer y releer atentamente lo que se me pedía para comprender el problema y crear un plan de seguimiento paso a paso.

## 2. Ingesta y Limpieza de Datos (EDA)

Revisando los documentos pude percatarme de cómo estaban estructurados para tomar las primeras decisiones. El maestro de clientes y el maestro de productos no presentaban irregularidades, por lo que los cargué sin problemas. Lo mismo ocurrió con la tabla de "Inventario cliente inicial", que a primera vista lucía correcta.

En el caso de Presupuesto de ventas, la columna `"cliente"` era la que se utilizaba, pero resulta mucho mejor manejar `"cliente_id"` para garantizar consistencia con el resto de las tablas. Además, la columna `"canal"` ya estaba disponible en la tabla maestra de clientes, por lo que resultaba redundante mantenerla en la tabla de presupuesto.

La tabla de Mercado Nielsen también se veía correcta en su estructura.

Para los archivos de Sell-In noté que cada documento correspondía a un trimestre (aunque en el código se puede confirmar), y que las columnas, a pesar de contener la misma información, no llevaban el mismo nombre entre archivos. Por eso decidí estandarizarlas tomando como referencia la nomenclatura de `Sell_in_2`.

En el caso del Sell-Out ocurría lo mismo: columnas equivalentes con nombres distintos. Elegí también el esquema de `Sell_out_2` como referencia. En este caso los archivos correspondían a datos de cada semestre.

Eliminé duplicados, llené valores faltantes siguiendo la misma lógica de los datos y descarté registros irregulares.

### Limpieza y Transformaciones Necesarias

Una vez cargados y consolidados los datos, apliqué las siguientes transformaciones para dejarlos listos para el análisis:

1. **Homologación de fechas:** Convertí la columna `fecha_factura` al tipo `datetime` en ambos consolidados (Sell-In y Sell-Out), usando el formato `dd/mm/YYYY`. A partir de esta columna derivé una nueva columna `Mes` en formato `Period[M]`, que permite agrupar las transacciones por mes de forma sencilla y eficiente.

2. **Cruce con maestros de clientes y productos:** Realicé un `merge` de cada consolidado con el maestro de clientes (por `cliente_id`) y el maestro de productos (por `sku`). Esto me permitió enriquecer cada transacción con atributos descriptivos como el nombre del cliente, su canal, región y categoría del producto, entre otros, sin duplicar información en las tablas originales.

3. **Estandarización para consolidación:** Para poder unir Sell-In y Sell-Out en una sola tabla de transacciones, agregué una columna `Tipo_Transaccion` a cada tabla con los valores `'Sell-In'` y `'Sell-Out'` respectivamente, y renombré `unidades_vendidas` a `Unidades` como columna común entre ambas.

4. **Consolidación final:** Concatené ambas tablas en un único dataframe llamado `consolidado`, que representa la base principal de análisis. Esta estructura unificada facilita la comparación directa entre las entradas al canal (Sell-In) y las salidas al consumidor (Sell-Out) por cliente, producto y periodo de tiempo.

### Cálculo de Métricas Clave (Kilos, Inventario y DOH)

Con el `consolidado` listo, procedí a calcular las métricas principales que alimentarían el dashboard:

1. **Cálculo de kilos vendidos:** Los archivos originales de Sell-In y Sell-Out no siempre tenían el dato de kilos completo. Para solucionarlo, creé una función que cruza cada SKU con su peso unitario (`peso_kg`) del maestro de productos y lo multiplica por las unidades vendidas. Esto garantiza que todos los registros tengan un valor de kilos consistente, derivado de la misma fuente de verdad (el maestro), evitando depender de datos reportados que podrían ser inconsistentes. Lo mismo apliqué al inventario inicial.

2. **Resumen mensual de inventario:** A partir del `consolidado`, agrupé por mes, cliente y SKU, separando Sell-In de Sell-Out mediante un `unstack`. Esto me permitió tener en cada fila el total de unidades que entraron y salieron por producto y cliente en cada mes.

3. **Cálculo acumulativo del inventario (lógica de arrastre):** Esta es la parte más crítica del modelo. El inventario de cada mes no es independiente: el inventario final de un mes se convierte en el inventario inicial del siguiente. Para implementarlo, recorrí los datos por cada par `(cliente_id, sku)` ordenados cronológicamente, aplicando la fórmula:

   > `Inventario Final (T) = Inventario Anterior (T) + Sell-In (T) - Sell-Out (T)`

   El punto de partida fue la tabla `Inventario_cliente_inicial`, que representa el stock acumulado al 31 de diciembre de 2024. Los kilos finales se calcularon multiplicando las unidades finales por el peso del SKU obtenido del maestro.

4. **Cálculo del DOH (Days on Hand):** A partir del inventario final y el sell-out mensual, calculé los días de inventario disponibles con la fórmula:

   > `DOH = (Inventario Final / Sell-Out mensual) * 30`

   Para los casos donde el Sell-Out es cero pero hay inventario disponible, asigné arbitrariamente `DOH = 999`, indicando riesgo de inventario congelado o sobreabastecimiento sin rotación.

### Exportación del Archivo Final

Una vez calculadas todas las métricas, exporté todos los dataframes procesados al directorio `datos_limpios/` en formato CSV. Esto incluye:

- `consolidado_sell_in.csv` y `consolidado_sell_out.csv` — transacciones limpias y enriquecidas
- `resumen_mensual.csv` — inventario acumulado, variaciones y DOH por cliente, producto y mes
- `maestro_clientes.csv`, `maestro_productos.csv` — tablas de referencia limpias
- `mercado.csv`, `inventario_inicial.csv`, `presupuesto.csv` — fuentes complementarias

Antes de exportar convertí la columna `Mes` (tipo `Period[M]`) a cadena de texto (`str`) para garantizar compatibilidad total con cualquier lector de CSV y evitar errores de serialización con `pyarrow`. Este directorio `datos_limpios/` es la fuente única de datos que consume el dashboard de Streamlit.


## 3. Construcción del Dashboard y KPIs

Buscé que el dashboard tuviera tres secciones: una vista general donde los filtros muestran la información de forma agrupada, otra más específica para ver los productos y clientes de forma detallada, y finalmente la parte del análisis de mercado donde se observa un panorama general de la competencia. En el plan del dashboard está todo detallado.

## 4. Análisis Predictivo de Mercado

Como complemento al análisis descriptivo, construyé en el notebook `analisis.ipynb` un modelo predictivo orientado a entender la tendencia del volumen del mercado y el posicionamiento competitivo de Chacutería Foods.

### Modelo de Regresión Lineal con Lags

El modelo que implementé es una regresión lineal con variables de lag temporal. La idea es simple pero efectiva: en lugar de usar variables externas como predictores, el modelo usa los valores pasados de la propia serie como entradas (`lag_1`, `lag_2`, `lag_3`), es decir, el volumen de ventas del mercado en los 3 meses anteriores explica el volumen del mes actual.

El proceso fue el siguiente:

1. **Carga y preparación de datos:** Leí los archivos `mercado.csv` y `consolidado_sell_out.csv` del directorio `datos_limpios/`. A partir del share histórico de cada actor, calculé el volumen real de ventas de Chacutería Foods y de cada competidor multiplicando el volumen total del mercado por el share correspondiente.

2. **Entrenamiento del modelo:** Agrupé los datos por mes, creé las columnas `lag_1`, `lag_2` y `lag_3` con `shift()`, eliminé las filas con `NaN` resultantes y entrené un `LinearRegression` de scikit-learn con esas variables como features y el volumen del mercado como target.

3. **Pronóstico de 6 meses:** Para predecir hacia adelante implementé un bucle iterativo: en cada iteración el modelo predice el siguiente mes usando los tres últimos valores conocidos (incluidos los ya predichos), y luego desplaza los lags para usarlos en la siguiente predicción. Esto permite proyectar 6 meses sin requerir datos futuros reales.

4. **Desglose por actor:** El pronóstico del mercado total se desglosó para Chacutería Foods y los dos competidores usando el **share promedio histórico** de cada uno. Es decir, asumí que a futuro cada actor manteníría la misma participación relativa que tuvo en el período analizado.

5. **Visualización interactiva:** Construyé un gráfico de líneas con Plotly que muestra el historial y el pronóstico de los cuatro actores (mercado total, Chacutería, Competidor 1 y Competidor 2), diferenciando histórico de predicción con líneas sólidas y punteadas respectivamente. Este mismo gráfico quedó integrado en la pestaña de “Análisis de Negocio” del dashboard.

### Observaciones del Modelo

Al ser un modelo de regresión lineal simple, no captura ciclos estacionales ni cambios bruscos en la tendencia. Sin embargo, permite observar una tendencia general creciente del mercado, probablemente influenciada por el desempeño de los últimos meses del año. Lo más relevante de la gráfica es que, de mantenerse las condiciones actuales, Chacutería Foods estaría mejor posicionada en 2026 que en 2025, aunque aún por detrás de los dos competidores. Esto plantea una ruta de mejora clara: si en los primeros 6 meses de 2026 se implementan medidas que logren superar lo predicho por el modelo, se podrá concluir con evidencia que esas acciones tuvieron impacto real.

### KPIs de Market Share (Top 3 y Bottom 3)

Además del modelo predictivo, calculé los KPIs de participación de mercado de Chacutería Foods por canal y categoría, identificando los 3 segmentos con mayor share y los 3 con menor share.

Se puede observar que en el canal de Grandes Superficies y en las categorías de Quesos, Chacutería Foods tiene un desempeño competitivo que, aunque sigue por detrás de los líderes, rivaliza de forma significativa. Mantener esa presencia es estratégico para seguir siendo un actor relevante en el mercado. En cambio, los segmentos del Bottom 3 representan oportunidades de mejora o puntos donde podría evaluarse si vale la pena seguir compitiendo en función de la rentabilidad.

## Conclusiones Generales

Podemos encontrar en el canal institucional el mayor número de ingresos, repartidos entre las regiones Centro, Antioquia y Occidente. Seguido por Grandes Superficies como el segundo canal en número de ingresos y Hard Discount como el tercero. También se puede observar que los Quesos Análogos son la categoría con mayor porcentaje de ventas, seguida de Quesos Frescos y luego de Carnes Frías, representando entre estas tres más del 67% de las ventas totales.

Podemos observar que en los canales de Exportaciones e Institucional no hay ningún tipo de Sell-Out registrado, por lo cual no es posible hacer un análisis real del desempeño de venta de esos productos, ya que el nivel de ventas al consumidor es cero (probablemente porque no se tienen esos datos disponibles).

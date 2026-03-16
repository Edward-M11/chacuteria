# Procedimiento y Paso a Paso - Prueba Técnica Chacutería Foods

Este documento describe la metodología, enfoques y cada una de las actividades realizadas durante el desarrollo de la prueba técnica.

## 1. Entendimiento del Problema

Lo primero que hice fue leer y releer antentamente lo que se me pedia para comprender el problena y crear un plan se seguimiento paso por paso

## 2. Ingesta y Limpieza de Datos (EDA)

Viendo los documentos puede percatarme de como estaba estructurados para las primeras decisiones, Maesto clientes y maestro productos se en contraban si irregularidades por lo que los cargue sin problemas. Al igual que la tabla de "Inventario cliente inicial" a primera vista todo se veia de forma correcta.

Pero en el caso de Presupuesto ventas "cliente" es que se usa, es muchos mejor utilizar "cliente_id" y ademas "Canal" ya esta en la tabla maestar de clientes por lo que no hace falta en la tabla de presupuesto.

La tabla de Mercado_Nielsen Tambien se veia de forma correcta.

Para el caso de Sell_in puedo notar que cada ducmentos es un un trimestre (aunque en el codigo se puede confirmar) y que las columnas aunque son las misnas no llevan el mismo nombre por lo cual las voy a estandarizar al Sell_in_2.

En el caso del Sell_out ocurre lo mismo, columnas iguales difernetes nombre, escogere el del Sell_out_2, en este caso son datos de cada semestre.

## 3. Modelo de Datos y Relaciones

[Escribe aquí cómo pensaste la relación entre ventas, clientes y catálogo]

## 4. Construcción del Dashboard y KPIs

[Escribe qué métricas creaste y por qué]

## 5. Carga Automatizada en Base de Datos (Supabase)

[Detalla los retos y cómo conectaste Python con la nube]

## Conclusiones Generales

[Escribe alguna nota adicional para el sustentador de la prueba]

# Supuestos y Transformaciones Realizadas

## Consideraciones Generales

Durante el proceso de Limpieza y Estructuración (EDA), nos enfrentamos a múltiples archivos que requerían uniones complejas y validaciones. A continuación se detallan los supuestos clave y las transformaciones implementadas:

### 1. Calidad de Datos (Data Quality) y Nulos

- **Transformación:** Antes de unir, se unificaron los tipos de datos (se aseguró que `ID_Cliente` y `ID_SKU` fueran numéricos `int64` u `Object` estandarizados) en `M_Clientes` y `M_Productos`.
- **Supuesto:** En los casos donde los clientes de sub-canales específicos no tuvieran nombre reportado, se les imputó `"Cliente Genérico - <ID>"`.
- **Transformación de Fechas:** Todas las fechas y periodos presupuestales (tipo *'ene-25'*, *'feb-25'*) que se presentaban en el presupuesto o en *Nielsen* fueron casteadas a un `datetime` equivalente al primer día de ese mes (ej. `2025-01-01`) o transformadas a `Period[M]`.

### 2. Cálculo de Inventario (DOH)

- El inventario reportado por los clientes en la tabla `Inventario_cliente_inicial.csv` pertenece al acumulado total al 31 de Diciembre del año 2024.
- **Supuesto Base de Cálculo de Inventario:** El inventario mensual no es estático; se calcula mediante un modelo de contabilidad de flujo (Flow Control):
  $$
  \text{Inv Final_T} = (\text{Inv Inicial}_{T-1}) + (\text{Sell-In}_T) - (\text{Sell-Out}_T)
  $$
- Se calculó el **DOH (Days on Hand)** de la siguiente manera:
  $$
  \text{DOH} = \frac{\text{Inventario Promedio Mensual}}{\text{Venta Promedio Diaria (Sell-Out Mensual / 30)}}
  $$
- **Supuesto de Sobrestock / Alerta:** Si un producto no tiene venta al consumidor (Sell-Out $= 0$) pero reportó ingreso (Sell-In), la fórmula marcaría error dividiendo entre cero. Se imputó arbitrariamente un DOH de `999` días, siendo éste un indicador de riesgo de inventario congelado.

### 3. Faltante de Sell-Out en Algunos Canales

- **Supuesto:** Tal y como se especifica en las instrucciones originales, *no todo el sell-out fue recopilado de todas las zonas*. Para cálculos de rotación y DOH, **solamente se tuvo en cuenta** la población de clientes (Grandes Superficies principalmente) con datos fidedignos de visibilidad de góndola; de lo contrario el dato daría negativo o generaría falsos positivos de sobrestock.

### 4. Estructuración y Almacenamiento

- La tabla final fue exportada en formato `.parquet` vía Apache Arrow (con `pyarrow`).
- **Supuesto:** Es preferible sacrificar la lectura humana del CSV a cambio de reducir drásticamente el peso (MBs) y optimizar la inserción en base de datos tipo Columnar/Supabase para su explotación masiva posterior en herramientas de Cloud BI.

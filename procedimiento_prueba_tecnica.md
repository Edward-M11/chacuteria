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

# Plan Detallado del Dashboard en Streamlit - Chacutería Foods

El dashboard estará estructurado de forma modular utilizando *Streamlit Multipage*, lo que facilitará su escalabilidad, mantenimiento y facilidad de uso por parte de los equipos gerenciales y analíticos.

## Estructura de Páginas

### 1. Home (`Home.py`)
- **Propósito:** Ser la puerta de entrada corporativa y contextualizar al usuario (Sitio web ficticio de Chacutería Foods).
- **Contenido:**
  - Identidad gráfica (Rojo, Negro, Blanco).
  - Breve descripción, historia, misión.
  - Portafolio y canales de distribución.
  - Botón o enlace de redirección o "Call to Action" -> "Ir al Dashboard de Business Intelligence".

### 2. Overview Gerencial (`pages/1_Overview.py`)
- **Propósito:** Resumen de alto nivel del negocio frente a los objetivos, útil para directores.
- **KPIs Principales (Tarjetas/Scorecards):**
  - Total Sell-In (Valor, Unidades, Toneladas) y % Cumplimiento Presupuesto.
  - Total Sell-Out (Valor, Unidades, Toneladas).
  - Promedio de DOH (Days on Hand).
  - Stock Total Actual en Cliente.
- **Gráficos:**
  - *Bullet chart* o velocímetro comparando Sell-In vs Presupuesto.
  - *Gráfico de dona* para distribución del Sell-In por Regional y Canal.

### 3. Análisis Comercial (Sell-In vs Sell-Out) (`pages/2_Analisis_Comercial.py`)
- **Propósito:** Profundizar sobre el flujo de producto hacia y desde los clientes.
- **Filtros Globales de la Página:** Categoría, SKU, Cliente, Canal, Región, Tipo de Producto, Rango de Fecha.
- **Gráficos:**
  - *Gráfico de Barras Apiladas / Líneas Combinadas:* Sell-in vs Sell-Out a lo largo de los meses (Enero a Diciembre).
  - *Tabla Dinámica / Matriz de Calor:* Sell-out por Categoría vs Cliente. Identifica quién rota mejor el producto.

### 4. Inventarios y Alertas (`pages/3_Inventario_Alertas.py`)
- **Propósito:** Monitorear el estado de stock en PDV, previniendo quiebres y excesos de inventario.
- **Métricas:** 
  - Cálculo de DOH dinámico de acuerdo al sell-out promedio de los últimos X meses.
- **Reglas de Alertas Automáticas:**
  - Riesgo de *Stockout* (Desabastecimiento): DOH < 5 días (Rojo).
  - *Sobreinventario*: DOH > 45 días (Naranja).
  - Saludable: DOH entre 15 y 30 días (Verde).
- **Visualización:**
  - *Scatter plot (Gráfico de dispersión):* Rotación (Sell-Out) vs Nivel de Inventario. Puntos grandes indican mayor riesgo.
  - *Tabla con formato condicional* filtrable únicamente por SKUs críticos.

### 5. Mercado (Nielsen) vs Realidad (`pages/4_Mercado_Nielsen.py`)
- **Propósito:** Contrastar los movimientos propios con las simulaciones de la categoría según datos de mercado.
- **Análisis:**
  - Evolución de la Categoría en Volumen/Valor (Crecimiento de Mercado) versus Crecimiento propio de Sell-Out por Categoría.
  - Market Share (Participación simulada o estimación).
- **Gráficos:**
  - *Line chart cruzado:* Evolución mes a mes Nielsen vs Chacutería.

---

## 🚀 100% Automatizable y Escalable
- **Carga de Datos:** El dashboard conectará directamente con *Supabase* a través de `supabase-py` para leer la tabla `base_consolidada_chacuteria`. 
- **Desacoplamiento:** Al separar la capa de ingesta/EDA (Notebook/Supabase) de la capa visual (Streamlit), el tablero NO se satura procesando CSVs pesados y simplemente carga los _DataFrames_ cacheados.
- **Caché:** Se usará explícitamente `@st.cache_data` para evitar recargas constantes en transiciones entre páginas.
- **Filtros Flexibles:** Filtros cruzados aplicados en cascada para no sobrecargar el renderizado inicial y lograr fluidez.

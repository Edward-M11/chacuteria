# Plan Consolidado del Dashboard - Chacutería Foods

El dashboard ha sido implementado como una solución integral de **Inteligencia de Negocios** utilizando *Streamlit*, estructurado en una página principal de bienvenida y un centro de comando analítico con navegación por pestañas.

## 🧀 Estructura de la Solución

### 1. Home (`Home.py`)
- **Propósito:** Portal corporativo que establece la identidad de marca (Paleta *Inspira*: Naranja, Teal, Carbón).
- **Contenido:**
  - Visión general de la compañía y portafolio.
  - Acceso directo a la documentación técnica y repositorio.
  - Botón de navegación hacia el centro analítico.

### 2. Dashboard Analítico (`pages/1_Dashboard.py`)
Implementado como una aplicación de alto rendimiento con **Filtros en Cascada** y **Carga Híbrida** (Supabase Real-time + Local Fallback).

#### 📊 Tab 1: Vista General (Business Health)
- **KPIs Vitales:** Tarjetas dinámicas con Inventario Actual (Valor/Kg), salud de **DOH (Días de Inventario)**, Sell-In y Sell-Out.
- **Tendencia Inteligente:** Gráfico de líneas con *hover* unificado de 3 métricas (Unidades, Valor, Kg).
- **Cumplimiento vs Presupuesto:** Barras apiladas de cumplimiento en Valor y Kilos, con desglose por categoría/producto y cálculo dinámico de aporte a la meta.
- **Mix de Portafolio:** Composición del negocio por Kilos mediante gráficos de dona interactivos.

#### 🔎 Tab 2: Análisis Detallado (Explorador Profundo)
- **Gestión de Riesgos:** Tarjetas de alerta para productos con *Stockout* (DOH < 1) y sobreinventario (DOH > 7) con tablas expandibles de detalle.
- **Top Ventas:** Comparación horizontal Sell-In vs Sell-Out por SKU con identificación de clientes.
- **Explorador Dinámico:** Tablas de detalle que conmutan automáticamente entre vista **Mensual** y **Diaria** (con cálculo de *carry-over* de inventario día a día).
- **Filtro Cruzado (Click-to-Zoom):** Al hacer clic en un mes de la gráfica de tendencia, todo el dashboard se filtra automáticamente para analizar ese mes al detalle diario.

#### 🤖 Tab 3: Análisis de Negocio & IA (Predictivo)
- **Market Share:** Análisis de participación (Chacutería vs Competidores) mediante KPIs de Top/Bottom categorías y gráficos 100% apilados.
- **Forecasting (Regresión con Lags):** Modelo de Machine Learning (Regresión Lineal con retrasos temporales) para proyectar 6 meses de demanda del mercado y ventas propias.
- **Asistente IA:** Interfaz dedicada para consultas en lenguaje natural (Demo preparada para integración con LLMs como Groq).

---

## 🛠️ Arquitectura Técnica de Vanguardia

- **Ingesta en Tiempo Real:** Conexión nativa con **Supabase** para visualización de datos actualizados al instante, con persistencia en caché de 5 minutos.
- **Motor de Filtrado "Circular":** Los filtros dimensionales se actualizan entre sí para evitar selecciones vacías (Cross-filtering).
- **Diseño Premium:** Interfaz oscura (Glassmorphism) con micro-animaciones y tooltips estilizados.
- **Escalabilidad:** Separación de la lógica de negocio (Helpers de DOH e Inventario) de la capa de visualización para facilitar el mantenimiento.

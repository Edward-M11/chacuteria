import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np
from datetime import timedelta
from sklearn.linear_model import LinearRegression
import asyncio
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
# Configuración inicial de la página
st.set_page_config(page_title="Chacutería - Dashboard", page_icon="🧀", layout="wide")

# CSS personalizado basado en una paleta 
st.markdown("""
    <style>
        :root {
            --primary: #ff6b35; --secondary: #2ec4b6; --dark: #293241;
            --light: #f7f9fc;   --grey: #e0e6ed;     --success: #57cc99;
            --warning: #ffd166; --danger: #ef476f;
        }
        html, body, [class*="css"] {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #e0e6ed;
        }
        .stApp { background-color: #0e1117; }
        [data-testid="stSidebar"] { background-color: #293241; }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label { color: #e0e6ed !important; }
        .stat-card {
            background-color: #293241; border-radius: 12px; padding: 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5); display: flex;
            flex-direction: column; border-bottom: 4px solid #ff6b35; margin-bottom: 20px;
        }
        .stat-card-title {
            font-size: 14px; color: #a9b8d5; margin-bottom: 4px;
            text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px;
        }
        .stat-card-value { font-size: 28px; font-weight: 700; color: #ffffff; margin-bottom: 8px; }
        .stat-card-sub   { font-size: 14px; color: #e0e6ed; margin-bottom: 4px; }
        .trend-up      { color: #57cc99; font-weight: 600; font-size: 13px; }
        .trend-down    { color: #ef476f; font-weight: 600; font-size: 13px; }
        .trend-neutral { color: #ffd166; font-weight: 600; font-size: 13px; }
        [data-testid="stDataFrame"] {
            background-color: #293241; border-radius: 12px;
            padding: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# ── Constantes de estilo para gráficos Plotly ──────────────────────
_BG   = "#1e1e1e"
_GRID = "#374151"

_TOOLTIP = dict(hoverlabel=dict(
    bgcolor="#1e2a3a", bordercolor="#ff6b35",
    font=dict(size=15, color="#ffffff", family="Segoe UI, sans-serif"),
))
_TOOLTIP_DET = dict(hoverlabel=dict(
    bgcolor="#1e2a3a", bordercolor="#2ec4b6",
    font=dict(size=15, color="#ffffff", family="Segoe UI, sans-serif"),
))

def _base_layout(**kwargs):
    base = dict(paper_bgcolor=_BG, plot_bgcolor=_BG,
                font=dict(color="#e0e6ed"), **_TOOLTIP)
    base.update(kwargs)
    return base

# Título del Dashboard
st.markdown("""
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
    <div>
        <h1 style="font-weight:700;font-size:28px;color:#ffffff;margin:0;">Dashboard Comercial</h1>
        <p style="font-size:14px;color:#a9b8d5;margin:4px 0 0 0;">
            Visualizando desempeño general, análisis detallado y modelos predictivos.</p>
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# CARGA DE DATOS
# ==========================================
@st.cache_data
def load_data():
    base_path = 'datos_limpios'
    if not os.path.exists(f'{base_path}/consolidado_sell_in.csv'):
        return None, None, None, None, None, None

    sell_in           = pd.read_csv(f'{base_path}/consolidado_sell_in.csv').drop_duplicates()
    sell_out          = pd.read_csv(f'{base_path}/consolidado_sell_out.csv').drop_duplicates()
    clientes          = pd.read_csv(f'{base_path}/maestro_clientes.csv').drop_duplicates()
    productos         = pd.read_csv(f'{base_path}/maestro_productos.csv').drop_duplicates()
    resumen_mensual   = pd.read_csv(f'{base_path}/resumen_mensual.csv')
    if len(resumen_mensual.columns) >= 7:
        resumen_mensual = resumen_mensual.drop_duplicates(subset=resumen_mensual.columns[:7].tolist())
    else:
        resumen_mensual = resumen_mensual.drop_duplicates()
    presupuesto       = pd.read_csv(f'{base_path}/presupuesto.csv').drop_duplicates()
    mercado           = pd.read_csv(f'{base_path}/mercado.csv').drop_duplicates()
    inventario_inicial = pd.read_csv(f'{base_path}/inventario_inicial.csv').drop_duplicates()

    presupuesto = presupuesto.merge(clientes, on='cliente_id', how='left')
    presupuesto['Mes_Txt']   = presupuesto['mes'].astype(str).str[:7]
    presupuesto['categoria'] = presupuesto['categoria'].str.strip().str.upper()

    sell_in['fecha_factura']  = pd.to_datetime(sell_in['fecha_factura'],  format='%Y-%m-%d', errors='coerce')
    sell_out['fecha_factura'] = pd.to_datetime(sell_out['fecha_factura'], format='%Y-%m-%d', errors='coerce')
    sell_in  = sell_in.dropna(subset=['fecha_factura', 'cliente_id'])
    sell_out = sell_out.dropna(subset=['fecha_factura', 'cliente_id'])

    sell_in['Mes_Txt']  = sell_in['fecha_factura'].dt.strftime('%Y-%m')
    sell_out['Mes_Txt'] = sell_out['fecha_factura'].dt.strftime('%Y-%m')

    sell_in         = sell_in.merge(clientes, on='cliente_id', how='left').merge(productos, on='sku', how='left')
    sell_out        = sell_out.merge(clientes, on='cliente_id', how='left').merge(productos, on='sku', how='left')
    resumen_mensual = resumen_mensual.merge(clientes, on='cliente_id', how='left').merge(productos, on='sku', how='left')
    inventario_inicial = inventario_inicial.merge(clientes, on='cliente_id', how='left').merge(productos, on='sku', how='left')

    for df_tmp in [sell_in, sell_out, resumen_mensual, inventario_inicial]:
        for col in ['canal', 'categoria', 'subcategoria', 'regional', 'tipo_producto', 'marca', 'origen']:
            if col in df_tmp.columns:
                df_tmp[col] = df_tmp[col].fillna(f'Sin {col.capitalize()}')
    sell_in['canal'] = sell_in['canal'].fillna('Sin Canal')

    resumen_mensual['DOH'] = pd.to_numeric(resumen_mensual['DOH'], errors='coerce').fillna(0)
    if 'Mes' in resumen_mensual.columns:
        resumen_mensual['Mes_Txt'] = resumen_mensual['Mes'].astype(str).str[:7]
    elif 'mes' in resumen_mensual.columns:
        resumen_mensual['Mes_Txt'] = resumen_mensual['mes'].astype(str).str[:7]
    elif 'fecha_factura' in resumen_mensual.columns:
        resumen_mensual['fecha_factura'] = pd.to_datetime(resumen_mensual['fecha_factura'], errors='coerce')
        resumen_mensual['Mes_Txt'] = resumen_mensual['fecha_factura'].dt.strftime('%Y-%m')
    else:
        resumen_mensual['Mes_Txt'] = 'Sin Fecha'

    return sell_in, sell_out, resumen_mensual, presupuesto, mercado, inventario_inicial


sell_in, sell_out, resumen, presupuesto, mercado, inventario_inicial = load_data()

if sell_in is None:
    st.error("⚠️ Faltan datos en 'datos_limpios'. Genera los CSV en tu cuaderno EDA primero.")
    st.stop()


# ==========================================
# SIDEBAR – FILTROS
# ==========================================
st.sidebar.markdown("<h2 style='color:#ff6b35;'>🧀 Chacutería Filters</h2>", unsafe_allow_html=True)
st.sidebar.markdown("Segmentación Global Data")
st.sidebar.markdown("<p style='font-size:12px;color:#a9b8d5;'><i>Deja el filtro en blanco para seleccionar TODOS.</i></p>",
                    unsafe_allow_html=True)

df_in   = sell_in.copy()
df_out  = sell_out.copy()
df_res  = resumen.copy()
df_merc = mercado.copy()

for _k, _v in [("mes_fijado", None), ("ignore_chart_clear", False), ("chart_puntos_prev", [])]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

def al_cambiar_slider():        st.session_state.mes_fijado = None
def al_cambiar_otros_filtros(): st.session_state.ignore_chart_clear = True
def quitar_zoom_manualmente():
    st.session_state.mes_fijado = None
    st.session_state.ignore_chart_clear = False

mes_opciones = sorted(df_in['Mes_Txt'].dropna().unique().tolist())

# Cross-filter via chart click
tendencia_estado = st.session_state.get("tendencia_chart", {})
puntos = tendencia_estado.get("selection", {}).get("points", [])
if puntos != st.session_state.chart_puntos_prev:
    if len(puntos) > 0:
        val_crudo = str(puntos[0].get("x"))
        if '-' in val_crudo and len(val_crudo) >= 7:
            mes_det = val_crudo[:7]
            if mes_det in mes_opciones:
                st.session_state.mes_fijado        = mes_det
                st.session_state.ignore_chart_clear = True
    else:
        if st.session_state.ignore_chart_clear:
            st.session_state.ignore_chart_clear = False
        else:
            st.session_state.mes_fijado = None
st.session_state.chart_puntos_prev = puntos

# Inicio fijo en 2025-01 — el usuario solo mueve el mes final
_inicio_fijo = '2025-01' if '2025-01' in mes_opciones else mes_opciones[0]

if len(mes_opciones) >= 1:
    # Mes final seleccionable por el usuario; inicio siempre fijo
    mes_fin_sel = st.sidebar.selectbox(
        "📅 1. Hasta el mes",
        options=mes_opciones,
        index=len(mes_opciones) - 1,
        key="rango_mes_slider",
        on_change=al_cambiar_slider,
    )
    st.sidebar.caption(f"📌 Inicio fijo: **{_inicio_fijo}** → Fin: **{mes_fin_sel}**")

    idx_inicio   = mes_opciones.index(_inicio_fijo)
    idx_fin      = mes_opciones.index(mes_fin_sel)
    meses_filtro = mes_opciones[idx_inicio:idx_fin + 1]

    if st.session_state.mes_fijado:
        meses_filtro = [st.session_state.mes_fijado]
        st.sidebar.warning(
            f"📌 **FILTRO CRUZADO ACTIVO**\n\nAnalizando el detalle diario de **{st.session_state.mes_fijado}**.\n\n"
            "👉 **Cambia el rango de meses** o usa el botón abajo para salir."
        )
        st.sidebar.button("❌ Quitar Zoom de Mes", on_click=quitar_zoom_manualmente)
        mostrar_diario = True
    else:
        mostrar_diario = (len(meses_filtro) == 1)
        if mostrar_diario:
            st.sidebar.info(f"🔎 Viendo detalle diario de **{meses_filtro[0]}**.")

    df_in_mes  = sell_in[sell_in['Mes_Txt'].isin(meses_filtro)].copy()
    df_out_mes = sell_out[sell_out['Mes_Txt'].isin(meses_filtro)].copy()
    df_res_mes = resumen[resumen['Mes_Txt'].isin(meses_filtro)].copy() \
        if 'Mes_Txt' in resumen.columns else resumen.copy()
    mostrar_diario = (len(meses_filtro) == 1)
else:
    df_in_mes = sell_in.copy(); df_out_mes = sell_out.copy(); df_res_mes = resumen.copy()
    mostrar_diario = False; meses_filtro = mes_opciones[:]

# ── Filtros dimensionales ──
_DIMS = {
    'canal': 'canal_sel', 'regional': 'reg_sel', 'categoria': 'cat_sel',
    'subcategoria': 'subc_sel', 'cliente': 'cli_sel', 'descripcion_producto': 'sku_sel',
    'tipo_producto': 'tipo_sel', 'marca': 'marca_sel', 'origen': 'origen_sel',
}

def _opciones_para(col_objetivo):
    if col_objetivo not in df_in_mes.columns: return []
    tmp = df_in_mes.copy()
    for col, key in _DIMS.items():
        if col == col_objetivo or col not in tmp.columns: continue
        sel = st.session_state.get(key, [])
        if sel: tmp = tmp[tmp[col].isin(sel)]
    return sorted(tmp[col_objetivo].dropna().unique().tolist())

canal_sel    = st.sidebar.multiselect("🛒 2. Canal de Venta",      _opciones_para('canal'),                key="canal_sel",  on_change=al_cambiar_otros_filtros)
regional_sel = st.sidebar.multiselect("📍 3. Regional",            _opciones_para('regional'),             key="reg_sel",    on_change=al_cambiar_otros_filtros)
cat_sel      = st.sidebar.multiselect("🧀 4. Categoría",           _opciones_para('categoria'),            key="cat_sel",    on_change=al_cambiar_otros_filtros)
subcat_sel   = st.sidebar.multiselect("🧀 5. Sub-Categoría",       _opciones_para('subcategoria'),         key="subc_sel",   on_change=al_cambiar_otros_filtros)
st.sidebar.markdown("---")
st.sidebar.markdown("<p style='font-size:14px;font-weight:600;color:#ffd166;'>🎯 Filtros Específicos (Explorador)</p>",
                    unsafe_allow_html=True)
cliente_sel  = st.sidebar.multiselect("👤 6. Cliente",             _opciones_para('cliente'),              key="cli_sel",    on_change=al_cambiar_otros_filtros)
sku_sel      = st.sidebar.multiselect("📦 7. SKU / Producto",      _opciones_para('descripcion_producto'), key="sku_sel",    on_change=al_cambiar_otros_filtros)
tipo_sel     = st.sidebar.multiselect("🏷️ 8. Tipo de Producto",  _opciones_para('tipo_producto'),        key="tipo_sel",   on_change=al_cambiar_otros_filtros)
marca_sel    = st.sidebar.multiselect("✨ 9. Marca",                _opciones_para('marca'),                key="marca_sel",  on_change=al_cambiar_otros_filtros)
origen_sel   = st.sidebar.multiselect("🌍 10. Origen",              _opciones_para('origen'),               key="origen_sel", on_change=al_cambiar_otros_filtros)

# ── Aplicar todos los filtros ──
df_in   = df_in_mes.copy()
df_out  = df_out_mes.copy()
df_res  = df_res_mes.copy()
df_merc = mercado.copy()
df_inv  = inventario_inicial.copy()

_activos = {col: st.session_state.get(key, []) for col, key in _DIMS.items()}
for col, sel in _activos.items():
    if sel:
        if col in df_in.columns:   df_in   = df_in  [df_in  [col].isin(sel)]
        if col in df_out.columns:  df_out  = df_out [df_out [col].isin(sel)]
        if col in df_res.columns:  df_res  = df_res [df_res [col].isin(sel)]
        if col in df_merc.columns: df_merc = df_merc[df_merc[col].isin(sel)]
        if col in df_inv.columns:  df_inv  = df_inv [df_inv [col].isin(sel)]

if cliente_sel or sku_sel or tipo_sel or marca_sel or origen_sel:
    st.sidebar.info("🔎 **Análisis Específico Activo.**\nEstos filtros aplican a TODO el dashboard.")

# Rango completo de meses con mismos filtros dimensionales (para inventario estático)
_si_rango = sell_in[sell_in['Mes_Txt'].isin(meses_filtro)].copy()
_so_rango = sell_out[sell_out['Mes_Txt'].isin(meses_filtro)].copy()
for col, sel in _activos.items():
    if sel:
        if col in _si_rango.columns: _si_rango = _si_rango[_si_rango[col].isin(sel)]
        if col in _so_rango.columns: _so_rango = _so_rango[_so_rango[col].isin(sel)]


# ==========================================
# HELPERS
# ==========================================
def calcular_inventario_actual(inv_ini, si, so):
    """
    Stock = inventario_inicial (0 si cliente/sku no figura) + sell_in - sell_out
    Usa outer join para que clientes/skus ausentes del inventario inicial arranquen en 0.
    """
    try:
        # Todos los pares cliente_id×sku que aparecen en si o so
        _pares_si = si[['cliente_id', 'sku']].drop_duplicates() if \
            ('cliente_id' in si.columns and 'sku' in si.columns) else pd.DataFrame(columns=['cliente_id','sku'])
        _pares_so = so[['cliente_id', 'sku']].drop_duplicates() if \
            ('cliente_id' in so.columns and 'sku' in so.columns) else pd.DataFrame(columns=['cliente_id','sku'])
        _pares_inv = inv_ini[['cliente_id', 'sku']].drop_duplicates() if \
            ('cliente_id' in inv_ini.columns and 'sku' in inv_ini.columns) else pd.DataFrame(columns=['cliente_id','sku'])
        todos = pd.concat([_pares_si, _pares_so, _pares_inv]).drop_duplicates().reset_index(drop=True)

        # Stock inicial: 0 para los que no aparecen en inventario
        inv_base = inv_ini.groupby(['cliente_id', 'sku'], as_index=False).agg(
            u_ini=('unidades_inventario', 'sum'),
            kg_ini=('kilos_calculados', 'sum'),
        ) if not inv_ini.empty and 'unidades_inventario' in inv_ini.columns else pd.DataFrame(
            columns=['cliente_id', 'sku', 'u_ini', 'kg_ini'])

        inv = todos.merge(inv_base, on=['cliente_id', 'sku'], how='left').fillna(0)

        # Entradas (sell-in)
        if 'unidades_vendidas' in si.columns and 'sku' in si.columns and 'cliente_id' in si.columns:
            ent = si.groupby(['cliente_id', 'sku'], as_index=False).agg(
                u_in=('unidades_vendidas', 'sum'),
                kg_in=('kilos_vendidos_calculados', 'sum') if 'kilos_vendidos_calculados' in si.columns else ('unidades_vendidas', 'sum'),
            )
            inv = inv.merge(ent, on=['cliente_id', 'sku'], how='left').fillna(0)
        else:
            inv['u_in'] = 0; inv['kg_in'] = 0

        # Salidas (sell-out)
        if 'unidades_vendidas' in so.columns and 'sku' in so.columns and 'cliente_id' in so.columns:
            sal = so.groupby(['cliente_id', 'sku'], as_index=False).agg(
                u_out=('unidades_vendidas', 'sum'),
                kg_out=('kilos_vendidos_calculados', 'sum') if 'kilos_vendidos_calculados' in so.columns else ('unidades_vendidas', 'sum'),
            )
            inv = inv.merge(sal, on=['cliente_id', 'sku'], how='left').fillna(0)
        else:
            inv['u_out'] = 0; inv['kg_out'] = 0

        inv['stock_u']  = (inv['u_ini']  + inv['u_in']  - inv['u_out'] ).clip(lower=0)
        inv['stock_kg'] = (inv['kg_ini'] + inv['kg_in'] - inv['kg_out']).clip(lower=0)
        su  = inv['stock_u'].sum()
        skg = inv['stock_kg'].sum()
        sv  = su * (si['valor_venta'].sum() / si['unidades_vendidas'].sum()) \
              if 'valor_venta' in si.columns and 'unidades_vendidas' in si.columns \
                 and si['unidades_vendidas'].sum() > 0 else 0
        return {'unidades': su, 'valor': sv, 'kilos': skg}
    except Exception:
        u  = inv_ini['unidades_inventario'].sum() if 'unidades_inventario' in inv_ini.columns else 0
        kg = inv_ini['kilos_calculados'].sum()     if 'kilos_calculados'    in inv_ini.columns else 0
        return {'unidades': u, 'valor': 0, 'kilos': kg}


def calcular_doh(inv_ini, si, so, n_dias_periodo=None):
    """
    DOH idéntico al EDA:
      inv_final = max(stock_ini(0 si no existe) + sell_in - sell_out, 0)
      DOH_fila  = (inv_final / sell_out) * 30   si sell_out > 0
               = 999                            si sell_out == 0 e inv_final > 0
               = 0                              si sell_out == 0 e inv_final == 0
    DOH global = promedio ponderado por sell_out (filas con sell_out > 0).
    Si ninguna fila tiene sell_out > 0 pero hay stock → DOH = 999.
    """
    try:
        # Todos los pares sku×cliente_id
        def _pares(df):
            if 'cliente_id' in df.columns and 'sku' in df.columns:
                return df[['cliente_id', 'sku']].drop_duplicates()
            return pd.DataFrame(columns=['cliente_id', 'sku'])

        todos = pd.concat([_pares(si), _pares(so), _pares(inv_ini)]).drop_duplicates().reset_index(drop=True)
        if todos.empty: return 0, 0, 0, 0

        # Stock inicial (0 si no está en inventario)
        inv_base = inv_ini.groupby(['cliente_id', 'sku'], as_index=False).agg(
            u_ini=('unidades_inventario', 'sum')
        ) if not inv_ini.empty and 'unidades_inventario' in inv_ini.columns \
          else pd.DataFrame(columns=['cliente_id', 'sku', 'u_ini'])

        df_g = todos.merge(inv_base, on=['cliente_id', 'sku'], how='left').fillna(0)

        # Sell-In por sku×cliente (0 si no existe)
        if 'unidades_vendidas' in si.columns and 'sku' in si.columns and 'cliente_id' in si.columns:
            ent = si.groupby(['cliente_id', 'sku'], as_index=False).agg(u_in=('unidades_vendidas', 'sum'))
            df_g = df_g.merge(ent, on=['cliente_id', 'sku'], how='left').fillna(0)
        else:
            df_g['u_in'] = 0

        # Sell-Out por sku×cliente (0 si no existe)
        if 'unidades_vendidas' in so.columns and 'sku' in so.columns and 'cliente_id' in so.columns:
            sal = so.groupby(['cliente_id', 'sku'], as_index=False).agg(u_out=('unidades_vendidas', 'sum'))
            df_g = df_g.merge(sal, on=['cliente_id', 'sku'], how='left').fillna(0)
        else:
            df_g['u_out'] = 0

        # Inventario final: 0 + sell_in - sell_out para clientes sin inventario inicial
        df_g['inv_final'] = (df_g['u_ini'] + df_g['u_in'] - df_g['u_out']).clip(lower=0)

        # DOH por fila — igual al EDA
        df_g['doh_row'] = np.where(
            df_g['u_out'] > 0,
            (df_g['inv_final'] / df_g['u_out']) * 30,
            np.where(df_g['inv_final'] > 0, 999.0, 0.0)
        )

        total_so_u = df_g['u_out'].sum()
        stock_total = df_g['inv_final'].sum()

        # DOH global macro (Inventario Total / Venta Promedio Diaria Total)
        prom_diario = total_so_u / 30.0 if total_so_u > 0 else 0.0

        if prom_diario > 0:
            doh_global = stock_total / prom_diario
        elif stock_total > 0:
            # Hay stock pero cero ventas en la selección
            doh_global = 999.0
        else:
            doh_global = 0.0

        # Faltantes: unidades para que el inventario cubra al menos 1 día de venta
        falt_u = max(prom_diario * 1 - stock_total, 0)

        kpu = so['kilos_vendidos_calculados'].sum() / total_so_u if total_so_u > 0 and 'kilos_vendidos_calculados' in so.columns else 0
        vpu = so['valor_venta'].sum()               / total_so_u if total_so_u > 0 and 'valor_venta'               in so.columns else 0

        return doh_global, falt_u, falt_u * vpu, falt_u * kpu
    except Exception:
        return 0, 0, 0, 0


def _estado_abastecimiento(doh):
    if doh < 1:  return "🔴 Falta"
    if doh <= 7: return "🟢 Bien"
    return "🟡 Sobre"


# ==========================================
# TABS
# ==========================================
tab_general, tab_detallado, tab_ia = st.tabs([
    "📊 Vista General",
    "🔎 Análisis Detallado",
    "🤖 Análisis de Negocio",
])


# ─────────────────────────────────────────
# TAB 1: VISTA GENERAL
# ─────────────────────────────────────────
with tab_general:

    # ── Inventario KPI ─────────────────────────────────────────────────────
    # Si hay UN solo mes activo Y existe resumen_mensual con inventario acumulado,
    # usar el inventario final del mes ANTERIOR al filtrado (arrastre real).
    # Si hay múltiples meses, usar el acumulado total del rango.
    _res_full = resumen.copy()  # resumen_mensual completo sin filtro de mes
    _mes_unico = meses_filtro[0] if len(meses_filtro) == 1 else None
    _inv_col_u  = next((c for c in ['Unidades_Inventario_Final'] if c in _res_full.columns), None)
    _inv_col_kg = next((c for c in ['Kilos_Inventario_Final']    if c in _res_full.columns), None)

    if _mes_unico and _inv_col_u and 'Mes_Txt' in _res_full.columns:
        # Tomar el inventario final del mes ANTERIOR al seleccionado
        _todos_meses = sorted(_res_full['Mes_Txt'].dropna().unique().tolist())
        _idx_mes = _todos_meses.index(_mes_unico) if _mes_unico in _todos_meses else -1
        if _idx_mes > 0:
            _mes_anterior = _todos_meses[_idx_mes - 1]
            _res_mes_ant  = _res_full[_res_full['Mes_Txt'] == _mes_anterior]
            # Aplicar filtros del explorador si aplica
            for _col, _sel in _activos.items():
                if _sel and _col in _res_mes_ant.columns:
                    _res_mes_ant = _res_mes_ant[_res_mes_ant[_col].isin(_sel)]
            stock_u  = _res_mes_ant[_inv_col_u].sum()  if _inv_col_u  in _res_mes_ant.columns else 0
            stock_kg = _res_mes_ant[_inv_col_kg].sum() if _inv_col_kg in _res_mes_ant.columns else 0
            stock_v  = stock_u * (_si_rango['valor_venta'].sum() / _si_rango['unidades_vendidas'].sum()) \
                       if 'valor_venta' in _si_rango.columns and _si_rango['unidades_vendidas'].sum() > 0 else 0
        else:
            # Primer mes del historial: usar inventario inicial base
            inv_data = calcular_inventario_actual(df_inv, _si_rango, _so_rango)
            stock_u, stock_v, stock_kg = inv_data['unidades'], inv_data['valor'], inv_data['kilos']
    else:
        inv_data = calcular_inventario_actual(df_inv, _si_rango, _so_rango)
        stock_u, stock_v, stock_kg = inv_data['unidades'], inv_data['valor'], inv_data['kilos']

    # ── DOH KPI ────────────────────────────────────────────────────────────
    # 1 mes: fórmula directa (inv_final / sell_out_mes) * 30
    # Varios meses: inv_final / promedio_mensual_sell_out * 30
    _n_meses = len(meses_filtro)
    if _n_meses == 1:
        doh_val, falt_u, falt_v, falt_kg = calcular_doh(df_inv, _si_rango, df_out)
    else:
        # Calcular sell-out promedio mensual dividiendo por número de meses
        _so_prom = df_out.copy()
        # Crear copia con unidades divididas entre n_meses para simular promedio mensual
        _so_prom_agg = _so_prom.copy()
        if 'unidades_vendidas' in _so_prom_agg.columns:
            _so_prom_agg = _so_prom_agg.copy()
            _so_prom_agg['unidades_vendidas'] = _so_prom_agg['unidades_vendidas'] / _n_meses
            if 'kilos_vendidos_calculados' in _so_prom_agg.columns:
                _so_prom_agg['kilos_vendidos_calculados'] = _so_prom_agg['kilos_vendidos_calculados'] / _n_meses
        doh_val, falt_u, falt_v, falt_kg = calcular_doh(df_inv, _si_rango, _so_prom_agg)

    tot_si_u  = df_in['unidades_vendidas'].sum()          if 'unidades_vendidas'         in df_in.columns  else 0
    tot_si_v  = df_in['valor_venta'].sum()                 if 'valor_venta'               in df_in.columns  else 0
    tot_si_kg = df_in['kilos_vendidos_calculados'].sum()   if 'kilos_vendidos_calculados' in df_in.columns  else 0
    tot_so_u  = df_out['unidades_vendidas'].sum()          if 'unidades_vendidas'         in df_out.columns else 0
    tot_so_v  = df_out['valor_venta'].sum()                 if 'valor_venta'               in df_out.columns else 0
    tot_so_kg = df_out['kilos_vendidos_calculados'].sum()  if 'kilos_vendidos_calculados' in df_out.columns else 0

    # ── KPIs — mismo tamaño y estructura los 4 ──
    col1, col2, col3, col4 = st.columns(4)

    _kpi_h = "font-size:28px;font-weight:800;color:#ffffff;margin:6px 0 4px 0;"
    _kpi_u = "font-size:13px;color:#a9b8d5;font-weight:500;"

    with col1:
        st.markdown(f"""
        <div class="stat-card" style="border-color:#6b7280;">
            <div class="stat-card-title">Inventario Actual</div>
            <div style="{_kpi_h}">{stock_u:,.0f}
                <span style="{_kpi_u}">unidades</span></div>
            <div class="stat-card-sub">💰 Valor: <b>${stock_v:,.0f}</b></div>
            <div class="stat-card-sub">⚖️ Peso: <b>{stock_kg:,.1f} Kg</b></div>
            <div class="stat-card-sub" style="color:#6b7280;">📦 Stock al cierre del período</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        doh_color  = "#ef476f" if doh_val < 1 else ("#57cc99" if doh_val <= 7 else "#ffd166")
        estado_lbl = "🔴 Riesgo Falta" if doh_val < 1 else ("🟢 Saludable" if doh_val <= 7 else "🟡 Sobre Stock")
        st.markdown(f"""
        <div class="stat-card" style="border-color:{doh_color};">
            <div class="stat-card-title">DOH (Días de Inventario)</div>
            <div style="{_kpi_h}">{doh_val:,.1f}
                <span style="{_kpi_u}">días · {estado_lbl}</span></div>
            <div class="stat-card-sub">⚠️ Unidades faltantes: <b>{falt_u:,.0f}</b></div>
            <div class="stat-card-sub">💰 Valor faltante: <b>${falt_v:,.0f}</b></div>
            <div class="stat-card-sub">⚖️ Kg faltantes: <b>{falt_kg:,.1f} Kg</b></div>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card" style="border-color:#ff6b35;">
            <div class="stat-card-title">Sell-In Total</div>
            <div style="{_kpi_h}">{tot_si_u:,.0f}
                <span style="{_kpi_u}">unidades</span></div>
            <div class="stat-card-sub">💰 Valor: <b>${tot_si_v:,.0f}</b></div>
            <div class="stat-card-sub">⚖️ Peso: <b>{tot_si_kg:,.1f} Kg</b></div>
            <div class="stat-card-sub" style="color:#6b7280;">📥 Entradas al canal</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card" style="border-color:#2ec4b6;">
            <div class="stat-card-title">Sell-Out Total</div>
            <div style="{_kpi_h}">{tot_so_u:,.0f}
                <span style="{_kpi_u}">unidades</span></div>
            <div class="stat-card-sub">💰 Valor: <b>${tot_so_v:,.0f}</b></div>
            <div class="stat-card-sub">⚖️ Peso: <b>{tot_so_kg:,.1f} Kg</b></div>
            <div class="stat-card-sub" style="color:#6b7280;">🛒 Ventas al consumidor</div>
        </div>""", unsafe_allow_html=True)

    # ── 1. TENDENCIA — ancho completo ──
    st.markdown("<h3 style='font-size:20px;font-weight:700;text-align:center;margin:10px 0 6px 0;'>Tendencia Sell-In vs Sell-Out</h3>",
                unsafe_allow_html=True)
    eje_tiempo = 'fecha_factura' if mostrar_diario else 'Mes_Txt'

    def _agg_serie(df):
        kw = dict(unidades_vendidas=('unidades_vendidas', 'sum'))
        if 'kilos_vendidos_calculados' in df.columns: kw['kilos'] = ('kilos_vendidos_calculados', 'sum')
        else:                                          kw['kilos'] = ('unidades_vendidas', 'sum')
        if 'valor_venta' in df.columns:               kw['valor'] = ('valor_venta', 'sum')
        else:                                          kw['valor'] = ('unidades_vendidas', 'sum')
        return df.dropna(subset=[eje_tiempo]).groupby(eje_tiempo).agg(**kw).reset_index()

    ev_in_grp  = _agg_serie(df_in);  ev_in_grp['Transacción']  = 'Sell-In'
    ev_out_grp = _agg_serie(df_out); ev_out_grp['Transacción'] = 'Sell-Out'
    tendencia  = pd.concat([ev_in_grp, ev_out_grp]).sort_values(eje_tiempo)

    if not tendencia.empty:
        fig1 = px.line(
            tendencia, x=eje_tiempo, y='unidades_vendidas', color='Transacción',
            markers=True, color_discrete_map={'Sell-In': '#ff6b35', 'Sell-Out': '#2ec4b6'},
            category_orders={'Transacción': ['Sell-In', 'Sell-Out']},
            custom_data=['kilos', 'Transacción', 'valor'],
        )
        fig1.update_traces(
            hovertemplate=(
                "<b>%{customdata[1]}</b> — %{x}<br>"
                "📦 Unidades: <b>%{y:,.0f}</b><br>"
                "💰 Valor: <b>$%{customdata[2]:,.0f}</b><br>"
                "⚖️ Kilos: <b>%{customdata[0]:,.1f} Kg</b><extra></extra>"
            ),
            line=dict(width=3), marker=dict(size=8),
        )
        fig1.update_layout(**_base_layout(
            xaxis_title="Fecha" if mostrar_diario else "Mes",
            yaxis_title="Unidades", legend_title="",
            margin=dict(l=0, r=0, t=10, b=0), height=320,
            xaxis=dict(tickfont=dict(size=13), showgrid=False, color="#a9b8d5"),
            yaxis=dict(tickfont=dict(size=13), gridcolor=_GRID, color="#a9b8d5"),
            legend=dict(font=dict(size=14), orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        ))
        st.plotly_chart(fig1, use_container_width=True, key="tendencia_chart",
                        on_select="rerun", selection_mode="points")

    # ── 2. GAUGES + PIE lado a lado ──
    c_gauge, c_pie = st.columns([4, 6])

    with c_gauge:
        st.markdown("<h3 style='font-size:18px;font-weight:600;text-align:center;margin-top:10px;'>Cumplimiento vs. Presupuesto</h3>",
                    unsafe_allow_html=True)

        tot_si_val_g = df_in['valor_venta'].sum() if 'valor_venta' in df_in.columns else 0
        ppto_f = presupuesto.copy()
        if 'Mes_Txt' in ppto_f.columns:
            try: ppto_f = ppto_f[ppto_f['Mes_Txt'].isin(meses_filtro)]
            except: pass
        for _col, _sel in {'cliente': cliente_sel, 'canal': canal_sel,
                           'regional': regional_sel, 'categoria': cat_sel}.items():
            if _sel and _col in ppto_f.columns:
                _norm = [s.strip().upper() for s in _sel] if _col == 'categoria' else _sel
                ppto_f = ppto_f[ppto_f[_col].isin(_norm)]

        ppto_val   = ppto_f['valor_presupuesto'].sum() if 'valor_presupuesto' in ppto_f.columns and not ppto_f.empty else 1
        ppto_kg    = ppto_f['kilos_presupuesto'].sum()  if 'kilos_presupuesto'  in ppto_f.columns and not ppto_f.empty else 1
        si_kg_g    = df_in['kilos_vendidos_calculados'].sum() if 'kilos_vendidos_calculados' in df_in.columns else 0
        pct_val    = round(tot_si_val_g / ppto_val * 100, 1) if ppto_val > 0 else 0
        pct_kg_g   = round(si_kg_g      / ppto_kg  * 100, 1) if ppto_kg  > 0 else 0

        # ── Dimensión: categorías por defecto, productos si hay categoría filtrada ──
        _dim_ppto = ('descripcion_producto' if cat_sel and 'descripcion_producto' in df_in.columns
                     else ('categoria' if 'categoria' in df_in.columns
                     else ('descripcion_producto' if 'descripcion_producto' in df_in.columns else None)))

        # Presupuesto por categoría (para la sombra)
        ppto_por_cat_val = {}
        ppto_por_cat_kg  = {}
        if 'categoria' in ppto_f.columns:
            _ppto_cat = ppto_f.groupby('categoria').agg(
                p_val=('valor_presupuesto', 'sum') if 'valor_presupuesto' in ppto_f.columns else ('categoria', 'count'),
                p_kg =('kilos_presupuesto',  'sum') if 'kilos_presupuesto'  in ppto_f.columns else ('categoria', 'count'),
            ).reset_index()
            ppto_por_cat_val = dict(zip(_ppto_cat['categoria'].str.upper(), _ppto_cat['p_val']))
            ppto_por_cat_kg  = dict(zip(_ppto_cat['categoria'].str.upper(), _ppto_cat['p_kg']))
        # When drilling to products, map through categoria
        ppto_por_dim_val = ppto_por_cat_val
        ppto_por_dim_kg  = ppto_por_cat_kg
        if _dim_ppto == 'descripcion_producto' and 'categoria' in df_in.columns:
            _prod_cat_map = df_in[['descripcion_producto','categoria']].drop_duplicates() \
                              .set_index('descripcion_producto')['categoria'].str.upper()
            ppto_por_dim_val = {p: ppto_por_cat_val.get(c, 0) for p, c in _prod_cat_map.items()}
            ppto_por_dim_kg  = {p: ppto_por_cat_kg.get(c,  0) for p, c in _prod_cat_map.items()}

        _COLORS_SEQ = ['#57cc99','#2ec4b6','#ff6b35','#ffd166','#a9b8d5','#ef476f','#7b61ff','#f4a261','#e9c46a','#264653']

        def _make_stacked_cumplimiento(df_src, dim, val_col, ppto_total, ppto_por_dim,
                                       label_val, titulo, unidad):
            if dim is None or val_col not in df_src.columns or ppto_total <= 0:
                return None

            grp = df_src.groupby(dim)[val_col].sum().reset_index()
            grp.columns = [dim, 'real']
            grp['pct_meta'] = (grp['real'] / ppto_total * 100).round(2)
            grp['ppto_dim'] = grp[dim].map(ppto_por_dim).fillna(0) if ppto_por_dim else 0.0
            grp['ppto_pct'] = (grp['ppto_dim'] / ppto_total * 100).round(2)
            grp = grp.sort_values('pct_meta', ascending=False)

            total_pct = round(grp['pct_meta'].sum(), 1)
            _pct_label = pct_val if unidad == '$' else pct_kg_g
            _lbl_color = '#57cc99' if _pct_label >= 100 else ('#ffd166' if _pct_label >= 80 else '#ef476f')

            fig = go.Figure()

            for idx, (_, row) in enumerate(grp.iterrows()):
                color = _COLORS_SEQ[idx % len(_COLORS_SEQ)]
                _fmt_r = f"{row['real']:,.0f}" if unidad == '$' else f"{row['real']:,.1f}"
                _fmt_p = f"{row['ppto_dim']:,.0f}" if unidad == '$' else f"{row['ppto_dim']:,.1f}"
                fig.add_trace(go.Bar(
                    name=str(row[dim]),
                    y=['Real'],
                    x=[row['pct_meta']],
                    orientation='h',
                    marker=dict(color=color, opacity=0.88,
                                line=dict(color='rgba(0,0,0,0.25)', width=0.8)),
                    customdata=[[row['real'], row['pct_meta'], row['ppto_dim'], row['ppto_pct']]],
                    hovertemplate=(
                        f"<b>{row[dim]}</b><br>"
                        f"{'💰' if unidad=='$' else '⚖️'} {label_val}: <b>{_fmt_r} {unidad}</b><br>"
                        f"🎯 Aporte a Meta: <b>{row['pct_meta']:.1f}%</b><br>"
                        f"📦 Ppto asignado: <b>{_fmt_p} {unidad} ({row['ppto_pct']:.1f}%)</b>"
                        "<extra></extra>"
                    ),
                    showlegend=True,
                ))

            fig.add_vline(x=100, line_dash='dash', line_color='#ffffff', line_width=1.5,
                          annotation_text='100%',
                          annotation_font=dict(color='#a9b8d5', size=10),
                          annotation_position='top right')

            # ── TAMAÑO DE LOS GRÁFICOS DE CUMPLIMIENTO ──
            # Cambia height para ajustar la altura de cada gráfico (los dos son iguales)
            # Cambia t en margin para el espacio entre el borde superior y la barra
            _HEIGHT_CUMPLIMIENTO = 243   # ← altura de cada gráfico en píxeles
            _MARGIN_TOP          = 30    # ← espacio arriba (título + leyenda)

            fig.update_layout(**_base_layout(
                barmode='stack',
                xaxis_title="% de Meta", yaxis_title="",
                margin=dict(l=0, r=10, t=_MARGIN_TOP, b=10),
                height=_HEIGHT_CUMPLIMIENTO,
                xaxis=dict(tickfont=dict(size=12), color="#a9b8d5",
                           range=[0, max(110, total_pct * 1.08)],
                           ticksuffix='%'),
                yaxis=dict(tickfont=dict(size=12), color="#a9b8d5"),
                legend=dict(
                    font=dict(size=10),
                    orientation='h',
                    yanchor='top', y=1.12,
                    xanchor='left', x=0,
                    tracegroupgap=2,
                ),
                title=dict(
                    text=f"{titulo} — <span style='color:{_lbl_color}'><b>{_pct_label:.1f}%</b></span>",
                    font=dict(size=14, color='#e0e6ed'),
                    x=0.5, xanchor='center',
                    y=0.995, yanchor='top',
                ),
                **_TOOLTIP,
            ))
            return fig

        _fig_val = _make_stacked_cumplimiento(
            df_in, _dim_ppto, 'valor_venta', ppto_val, ppto_por_dim_val,
            "Venta Real", "💰 Cumplimiento Valor", '$',
        )
        _fig_kg = _make_stacked_cumplimiento(
            df_in, _dim_ppto, 'kilos_vendidos_calculados', ppto_kg, ppto_por_dim_kg,
            "Kilos Reales", "⚖️ Cumplimiento Kilos", 'Kg',
        )

        if _fig_val: st.plotly_chart(_fig_val, use_container_width=True)
        if _fig_kg:  st.plotly_chart(_fig_kg,  use_container_width=True)
        if not _fig_val and not _fig_kg:
            st.metric("Cumplimiento Valor", f"{pct_val:.1f}%")
            st.metric("Cumplimiento Kilos", f"{pct_kg_g:.1f}%")

    with c_pie:
        mostrar_subcat = len(cat_sel) > 0
        columna_mix    = 'subcategoria' if mostrar_subcat else 'categoria'
        titulo_mix     = f"Composición de {'Sub-Categorías' if mostrar_subcat else 'Categorías'}"
        st.markdown(f"<h3 style='font-size:18px;font-weight:600;text-align:center;margin-top:10px;'>{titulo_mix}</h3>",
                    unsafe_allow_html=True)

        # Agrupar solo por kilos — sin valor ni unidades en el pie
        _grp_pie = df_in.groupby(columna_mix)
        _pie_series = (_grp_pie['kilos_vendidos_calculados'].sum().rename('kilos')
                       if 'kilos_vendidos_calculados' in df_in.columns
                       else _grp_pie.size().rename('kilos'))
        cat_df = _pie_series.reset_index()

        if not cat_df.empty:
            fig_cat = go.Figure(go.Pie(
                labels=cat_df[columna_mix].astype(str).tolist(),
                values=cat_df['kilos'].tolist(),
                hole=0.45,
                hovertemplate="<b>%{label}</b><br>⚖️ Kilos: <b>%{value:,.1f} Kg</b><br>📊 Mix: <b>%{percent}</b><extra></extra>",
                marker=dict(colors=['#2ec4b6','#ff6b35','#ef476f','#ffd166','#a9b8d5','#57cc99','#7b61ff','#f4a261']),
                textfont=dict(size=13),
                textinfo='label+percent',
            ))
            fig_cat.update_layout(**_base_layout(
                margin=dict(l=0, r=0, t=10, b=0), height=500,
                legend=dict(font=dict(size=13)),
                **_TOOLTIP,
            ))
            st.plotly_chart(fig_cat, use_container_width=True)

    # ── 3. CANAL Y REGIÓN — al fondo ──
    st.markdown("<h3 style='font-size:20px;font-weight:700;text-align:center;margin:24px 0 6px 0;'>Desempeño por Canal y Región</h3>",
                unsafe_allow_html=True)
    if not df_in.empty and 'canal' in df_in.columns and 'regional' in df_in.columns:
        _cr_kw = dict(valor_venta=('valor_venta', 'sum'))
        if 'unidades_vendidas'         in df_in.columns: _cr_kw['unidades'] = ('unidades_vendidas', 'sum')
        if 'kilos_vendidos_calculados' in df_in.columns: _cr_kw['kilos']    = ('kilos_vendidos_calculados', 'sum')
        canal_reg_df = df_in.groupby(['canal', 'regional']).agg(**_cr_kw).reset_index().sort_values('valor_venta', ascending=False)
        if not canal_reg_df.empty:
            _cd = [c for c in ['regional', 'unidades', 'kilos'] if c in canal_reg_df.columns]
            fig_cr = px.bar(
                canal_reg_df, x='canal', y='valor_venta', color='regional', barmode='group',
                color_discrete_sequence=['#ff6b35', '#2ec4b6', '#ffd166', '#57cc99', '#a9b8d5', '#ef476f'],
                custom_data=_cd,
            )
            _ht_cr = ("<b>%{x}</b> · <b>%{customdata[0]}</b><br>"
                      "💰 Valor: <b>$%{y:,.0f}</b><br>"
                      "📦 Unidades: <b>%{customdata[1]:,.0f}</b><br>"
                      "⚖️ Kilos: <b>%{customdata[2]:,.1f} Kg</b><extra></extra>") if len(_cd) == 3 else \
                     "<b>%{x}</b><br>💰 Valor: <b>$%{y:,.0f}</b><extra></extra>"
            fig_cr.update_traces(hovertemplate=_ht_cr)
            fig_cr.update_layout(**_base_layout(
                xaxis_title="", yaxis_title="Ingresos ($)", legend_title="Regional",
                margin=dict(l=0, r=0, t=10, b=0), height=350,
                xaxis=dict(tickfont=dict(size=14), color="#a9b8d5"),
                yaxis=dict(tickfont=dict(size=13), gridcolor=_GRID, color="#a9b8d5", showgrid=True),
                legend=dict(font=dict(size=13)),
            ))
            st.plotly_chart(fig_cr, use_container_width=True)
    else:
        st.info("Sin datos de Canal/Regional disponibles.")


# ─────────────────────────────────────────
# TAB 2: ANÁLISIS DETALLADO
# ─────────────────────────────────────────
with tab_detallado:
    st.markdown("### 🔎 Explorador Dimensional Profundo")
    st.write("Filtra y cruza dinámicamente indicadores específicos usando la barra lateral izquierda.")

    dd_in  = df_in.copy()
    dd_res = df_res.copy()
    dd_out = df_out.copy()

    st.markdown("---")

    # ── KPIs de riesgo — con detalle de productos/clientes ──
    if 'DOH' in dd_res.columns and not dd_res.empty:
        # Columnas de identificación disponibles
        _id_risk = [c for c in ['descripcion_producto', 'cliente'] if c in dd_res.columns]

        risk_under = dd_res[dd_res['DOH'] < 1].copy()
        risk_over  = dd_res[dd_res['DOH'] > 7].copy()

        n_under = risk_under['descripcion_producto'].nunique() if 'descripcion_producto' in risk_under.columns else len(risk_under)
        n_over  = risk_over['descripcion_producto'].nunique()  if 'descripcion_producto' in risk_over.columns  else len(risk_over)

        val_under = risk_under['Unidades_Sell_In'].sum() if 'Unidades_Sell_In' in risk_under.columns else 0
        val_over  = risk_over['Unidades_Sell_In'].sum()  if 'Unidades_Sell_In' in risk_over.columns  else 0
    else:
        n_under = n_over = val_under = val_over = 0
        risk_under = risk_over = pd.DataFrame()
        _id_risk = []

    kpi_r1, kpi_r2 = st.columns(2)

    with kpi_r1:
        st.markdown(f"""
        <div class="stat-card" style="border-color:#ef476f;">
            <div class="stat-card-title">🔴 Riesgo Desabastecimiento (DOH &lt; 1)</div>
            <div class="stat-card-value" style="font-size:22px;">{n_under} Productos</div>
            <div class="stat-card-sub">📦 Unidades Sell-In: <b>{val_under:,.0f}</b></div>
        </div>""", unsafe_allow_html=True)
        if not risk_under.empty and _id_risk:
            with st.expander("👁️ Ver productos en riesgo de desabastecimiento"):
                _date_col_u = next((c for c in ['Mes_Txt', 'mes', 'Mes', 'fecha_factura'] if c in risk_under.columns), None)
                _detail_cols = [c for c in (([_date_col_u] if _date_col_u else []) + _id_risk + [
                    'DOH', 'Unidades_Sell_In', 'Unidades_Sell_Out', 'Unidades_Inventario_Final'
                ]) if c in risk_under.columns]
                _det_u = risk_under[_detail_cols].drop_duplicates().sort_values(
                    [_date_col_u, 'DOH'] if _date_col_u else ['DOH']
                ) if 'DOH' in _detail_cols else risk_under[_detail_cols].drop_duplicates()
                _ren_u = {_date_col_u: 'Mes/Fecha', 'descripcion_producto': 'Producto', 'cliente': 'Cliente',
                          'Unidades_Sell_In': 'Sell-In', 'Unidades_Sell_Out': 'Sell-Out',
                          'Unidades_Inventario_Final': 'Inv. Final'}
                _det_u = _det_u.rename(columns={k: v for k, v in _ren_u.items() if k in _det_u.columns}).reset_index(drop=True)
                _fmt_u = {}
                for _c in ['Sell-In', 'Sell-Out', 'Inv. Final']:
                    if _c in _det_u.columns: _fmt_u[_c] = '{:,.0f}'
                if 'DOH' in _det_u.columns: _fmt_u['DOH'] = '{:,.1f}'
                st.dataframe(_det_u.style.format(_fmt_u), use_container_width=True,
                             height=min(40 * len(_det_u) + 38, 320), hide_index=True)

    with kpi_r2:
        st.markdown(f"""
        <div class="stat-card" style="border-color:#ffd166;">
            <div class="stat-card-title">🟡 Riesgo Sobreabastecimiento (DOH &gt; 7)</div>
            <div class="stat-card-value" style="font-size:22px;">{n_over} Productos</div>
            <div class="stat-card-sub">📦 Unidades Sell-In: <b>{val_over:,.0f}</b></div>
        </div>""", unsafe_allow_html=True)
        if not risk_over.empty and _id_risk:
            with st.expander("👁️ Ver productos en riesgo de sobreabastecimiento"):
                _date_col_o = next((c for c in ['Mes_Txt', 'mes', 'Mes', 'fecha_factura'] if c in risk_over.columns), None)
                _detail_cols_o = [c for c in (([_date_col_o] if _date_col_o else []) + _id_risk + [
                    'DOH', 'Unidades_Sell_In', 'Unidades_Sell_Out', 'Unidades_Inventario_Final'
                ]) if c in risk_over.columns]
                _det_o = risk_over[_detail_cols_o].drop_duplicates().sort_values(
                    [_date_col_o, 'DOH'] if _date_col_o else ['DOH'], ascending=[True, False] if _date_col_o else [False]
                ) if 'DOH' in _detail_cols_o else risk_over[_detail_cols_o].drop_duplicates()
                _ren_o = {_date_col_o: 'Mes/Fecha', 'descripcion_producto': 'Producto', 'cliente': 'Cliente',
                          'Unidades_Sell_In': 'Sell-In', 'Unidades_Sell_Out': 'Sell-Out',
                          'Unidades_Inventario_Final': 'Inv. Final'}
                _det_o = _det_o.rename(columns={k: v for k, v in _ren_o.items() if k in _det_o.columns}).reset_index(drop=True)
                _fmt_o = {}
                for _c in ['Sell-In', 'Sell-Out', 'Inv. Final']:
                    if _c in _det_o.columns: _fmt_o[_c] = '{:,.0f}'
                if 'DOH' in _det_o.columns: _fmt_o['DOH'] = '{:,.1f}'
                st.dataframe(_det_o.style.format(_fmt_o), use_container_width=True,
                             height=min(40 * len(_det_o) + 38, 320), hide_index=True)

    st.markdown("---")
    vc1, vc2 = st.columns([5, 5])

    # ── Gráfico Ventas ──
    with vc1:
        st.markdown("<h3 style='font-size:18px;font-weight:600;text-align:center;'>Ventas (Sell-In vs Sell-Out)</h3>",
                    unsafe_allow_html=True)
        if not dd_in.empty:
            # Agrupar por producto (y acumular clientes como lista para el tooltip)
            def _top_agg_con_cli(src):
                kw = dict(valor_venta=('valor_venta', 'sum'))
                if 'kilos_vendidos_calculados' in src.columns: kw['kilos']    = ('kilos_vendidos_calculados', 'sum')
                if 'unidades_vendidas'         in src.columns: kw['unidades'] = ('unidades_vendidas', 'sum')
                df_agg = src.groupby('descripcion_producto').agg(**kw).reset_index()
                # Clientes que compraron ese producto
                if 'cliente' in src.columns:
                    cli_str = src.groupby('descripcion_producto')['cliente'].apply(
                        lambda x: ', '.join(sorted(x.dropna().unique().tolist()))
                    ).reset_index().rename(columns={'cliente': 'clientes'})
                    df_agg = df_agg.merge(cli_str, on='descripcion_producto', how='left')
                    df_agg['clientes'] = df_agg['clientes'].fillna('—')
                else:
                    df_agg['clientes'] = '—'
                return df_agg

            top_in_v  = _top_agg_con_cli(dd_in);  top_in_v['Tipo']  = 'Sell-In ($)'
            top_out_v = _top_agg_con_cli(dd_out); top_out_v['Tipo'] = 'Sell-Out ($)'
            sku_top   = top_in_v.sort_values('valor_venta', ascending=False).head(7)['descripcion_producto']
            top_comb  = pd.concat([top_in_v, top_out_v])
            top_comb  = top_comb[top_comb['descripcion_producto'].isin(sku_top)].sort_values('valor_venta', ascending=True)

            _cd_bar = [c for c in ['kilos', 'unidades', 'Tipo', 'clientes'] if c in top_comb.columns]
            fig_bar = px.bar(
                top_comb, x="valor_venta", y="descripcion_producto",
                color="Tipo", orientation='h', barmode='group',
                color_discrete_sequence=['#ff6b35', '#2ec4b6'],
                custom_data=_cd_bar,
            )
            # Tooltip con clientes
            if len(_cd_bar) == 4:  # kilos, unidades, Tipo, clientes
                _ht = (
                    "<b>%{y}</b><br>"
                    "👤 Clientes: <b>%{customdata[3]}</b><br>"
                    "💰 Valor: <b>$%{x:,.0f}</b><br>"
                    "📦 Unidades: <b>%{customdata[1]:,.0f}</b><br>"
                    "⚖️ Kilos: <b>%{customdata[0]:,.1f} Kg</b>"
                    "<extra>%{customdata[2]}</extra>"
                )
            elif len(_cd_bar) == 3:  # sin clientes o sin kilos
                _ht = (
                    "<b>%{y}</b><br>💰 Valor: <b>$%{x:,.0f}</b><br>"
                    "📦 Unidades: <b>%{customdata[1]:,.0f}</b><br>"
                    "⚖️ Kilos: <b>%{customdata[0]:,.1f} Kg</b>"
                    "<extra>%{customdata[2]}</extra>"
                )
            else:
                _ht = "<b>%{y}</b><br>💰 Valor: <b>$%{x:,.0f}</b><extra></extra>"
            fig_bar.update_traces(hovertemplate=_ht)
            fig_bar.update_layout(**_base_layout(
                yaxis_title="", legend_title="", margin=dict(t=10, b=10),
                xaxis=dict(tickfont=dict(size=13), color="#a9b8d5"),
                yaxis=dict(tickfont=dict(size=12), color="#a9b8d5"),
                legend=dict(font=dict(size=13)),
                **_TOOLTIP_DET,
            ))
            st.plotly_chart(fig_bar, use_container_width=True)

    # ── Top Clientes / Resumen Productos ──
    with vc2:
        if len(cliente_sel) > 0:
            st.markdown("<h3 style='font-size:18px;font-weight:600;'>📦 Resumen Productos</h3>", unsafe_allow_html=True)
            top_in_c = dd_in.groupby(['cliente', 'descripcion_producto']).agg(
                sell_in_valor=('valor_venta', 'sum'),
                kilos_si=('kilos_vendidos_calculados', 'sum'),
                unidades_si=('unidades_vendidas', 'sum'),
            ).reset_index()
            top_out_c = dd_out.groupby(['cliente', 'descripcion_producto']).agg(
                sell_out_valor=('valor_venta', 'sum'),
                kilos_so=('kilos_vendidos_calculados', 'sum'),
                unidades_so=('unidades_vendidas', 'sum'),
            ).reset_index()
            top_prod_cli = top_in_c.merge(top_out_c, on=['cliente', 'descripcion_producto'], how='left').fillna(0)
            top_prod_cli = top_prod_cli.sort_values('sell_in_valor', ascending=False)
            if 'descripcion_producto' in dd_res.columns and 'DOH' in dd_res.columns:
                doh_prod = dd_res.groupby(['cliente', 'descripcion_producto'])['DOH'].mean().reset_index() \
                    if 'cliente' in dd_res.columns else dd_res.groupby('descripcion_producto')['DOH'].mean().reset_index()
                top_prod_cli = top_prod_cli.merge(
                    doh_prod, on=[c for c in ['cliente', 'descripcion_producto'] if c in doh_prod.columns], how='left')
            top_prod_cli['% Ventas'] = top_prod_cli.apply(
                lambda r: r['unidades_so'] / r['unidades_si'] * 100 if r['unidades_si'] > 0 else 0, axis=1)
            if 'DOH' in top_prod_cli.columns:
                top_prod_cli['Estado'] = top_prod_cli['DOH'].apply(_estado_abastecimiento)
            top_prod_cli = top_prod_cli.rename(columns={
                'cliente': 'Cliente', 'descripcion_producto': 'Producto',
                'sell_in_valor': 'Sell-In ($)', 'sell_out_valor': 'Sell-Out ($)',
                'kilos_si': 'Kilos Sell-In', 'kilos_so': 'Kilos Sell-Out', 'DOH': 'DOH Prom.',
            }).drop(columns=['unidades_si', 'unidades_so'], errors='ignore').reset_index(drop=True)
            fmt_p = {'Sell-In ($)': '${:,.0f}', 'Sell-Out ($)': '${:,.0f}',
                     'Kilos Sell-In': '{:,.1f} Kg', 'Kilos Sell-Out': '{:,.1f} Kg', '% Ventas': '{:.1f}%'}
            if 'DOH Prom.' in top_prod_cli.columns: fmt_p['DOH Prom.'] = '{:,.2f}'
            st.dataframe(top_prod_cli.style.format(fmt_p), use_container_width=True, height=500, hide_index=True)

        else:
            st.markdown("<h3 style='font-size:18px;font-weight:600;'>🏆 Top Clientes (Desempeño Integral)</h3>", unsafe_allow_html=True)
            top_ventas = dd_in.groupby('cliente').agg(
                valor_venta=('valor_venta', 'sum'),
                kilos=('kilos_vendidos_calculados', 'sum'),
                unidades_si=('unidades_vendidas', 'sum'),
            ).reset_index().sort_values('valor_venta', ascending=False)
            if 'cliente' in dd_out.columns:
                top_ventas = top_ventas.merge(
                    dd_out.groupby('cliente').agg(
                        sell_out=('valor_venta', 'sum'),
                        kilos_so=('kilos_vendidos_calculados', 'sum'),
                        unidades_so=('unidades_vendidas', 'sum'),
                    ).reset_index(), on='cliente', how='left').fillna(0)
            if 'cliente' in dd_res.columns and 'DOH' in dd_res.columns:
                top_ventas = top_ventas.merge(
                    dd_res.groupby('cliente')['DOH'].mean().reset_index(), on='cliente', how='left')
            if 'cliente' in dd_res.columns and 'Variacion_Inventario' in dd_res.columns:
                top_ventas = top_ventas.merge(
                    dd_res.groupby('cliente')['Variacion_Inventario'].sum().reset_index(), on='cliente', how='left')
            if 'unidades_so' in top_ventas.columns and 'unidades_si' in top_ventas.columns:
                top_ventas['% Ventas'] = top_ventas.apply(
                    lambda r: r['unidades_so'] / r['unidades_si'] * 100 if r['unidades_si'] > 0 else 0, axis=1)
            top_ventas = top_ventas.rename(columns={
                'cliente': 'Cliente', 'valor_venta': 'Sell-In ($)',
                'kilos': 'Kilos (Sell-In)', 'sell_out': 'Sell-Out ($)',
                'kilos_so': 'Kilos Sell-Out', 'DOH': 'DOH Prom.', 'Variacion_Inventario': 'Var. Inventario',
            }).fillna(0)
            fmt_cli = {'Sell-In ($)': '${:,.0f}', 'Kilos (Sell-In)': '{:,.1f} Kg'}
            for _k, _v in [('Sell-Out ($)','${:,.0f}'), ('Kilos Sell-Out','{:,.1f} Kg'),
                           ('DOH Prom.','{:,.2f}'), ('Var. Inventario','{:,.0f}'), ('% Ventas','{:.1f}%')]:
                if _k in top_ventas.columns: fmt_cli[_k] = _v
            top_ventas = top_ventas.drop(
                columns=[c for c in ['unidades_si', 'unidades_so'] if c in top_ventas.columns],
                errors='ignore').reset_index(drop=True)
            st.dataframe(top_ventas.style.format(fmt_cli), use_container_width=True, height=500, hide_index=True)

    # ══════════════════════════════════════════════════════════
    # TABLA INFERIOR — cambia entre "Mes a Mes" y "Diarios"
    # según si hay 1 mes seleccionado o varios
    # ══════════════════════════════════════════════════════════
    st.markdown("---")

    if mostrar_diario:
        # ── MODO UN MES: Productos Diarios con inventario acumulado día a día ──
        st.markdown("<h3 style='font-size:20px;font-weight:700;margin-top:10px;'>📅 Productos Diarios</h3>",
                    unsafe_allow_html=True)
        if 'fecha_factura' in dd_in.columns and 'descripcion_producto' in dd_in.columns:
            grp_d  = ['fecha_factura', 'descripcion_producto'] + (['cliente'] if 'cliente' in dd_in.columns else [])
            grp_do = [c for c in grp_d if c in dd_out.columns]

            def _dia_agg(src, grp, suffix):
                kw = {f'Sell_{suffix}': ('unidades_vendidas', 'sum')}
                if 'kilos_vendidos_calculados' in src.columns: kw[f'Kilos_{suffix}'] = ('kilos_vendidos_calculados', 'sum')
                if 'valor_venta'               in src.columns: kw[f'Valor_{suffix}'] = ('valor_venta', 'sum')
                return src.groupby(grp).agg(**kw).reset_index()

            dia_in    = _dia_agg(dd_in,  grp_d,  'In')
            dia_out   = _dia_agg(dd_out, grp_do, 'Out')
            tabla_dia = dia_in.merge(dia_out, on=grp_do, how='outer').fillna(0)

            # Inventario acumulado día a día con carry-over, igual al EDA
            if 'descripcion_producto' in tabla_dia.columns and 'fecha_factura' in tabla_dia.columns:
                # Obtener stock inicial por producto (suma sobre todos los clientes del filtro)
                _sku_ini  = (df_inv.groupby('descripcion_producto')['unidades_inventario'].sum()
                    if 'descripcion_producto' in df_inv.columns and 'unidades_inventario' in df_inv.columns
                    else pd.Series(dtype=float))

                tabla_dia = tabla_dia.sort_values(['descripcion_producto'] +
                    (['cliente'] if 'cliente' in tabla_dia.columns else []) + ['fecha_factura'])

                grp_cols_carry = ['descripcion_producto'] + (['cliente'] if 'cliente' in tabla_dia.columns else [])

                tabla_dia['Inv_Anterior']  = 0.0
                tabla_dia['Variacion']     = 0.0
                tabla_dia['Inv_Final_U']   = 0.0
                tabla_dia['DOH_dia']       = 0.0

                for keys, grp in tabla_dia.groupby(grp_cols_carry):
                    prod = keys if isinstance(keys, str) else keys[0]
                    inv_actual = float(_sku_ini.get(prod, 0))
                    for idx in grp.sort_values('fecha_factura').index:
                        si_u  = tabla_dia.at[idx, 'Sell_In']  if 'Sell_In'  in tabla_dia.columns else 0
                        so_u  = tabla_dia.at[idx, 'Sell_Out'] if 'Sell_Out' in tabla_dia.columns else 0
                        var   = si_u - so_u
                        inv_f = max(inv_actual + var, 0)
                        doh_d = (inv_f / so_u * 30) if so_u > 0 else (999 if inv_f > 0 else 0)
                        tabla_dia.at[idx, 'Inv_Anterior'] = inv_actual
                        tabla_dia.at[idx, 'Variacion']    = var
                        tabla_dia.at[idx, 'Inv_Final_U']  = inv_f
                        tabla_dia.at[idx, 'DOH_dia']      = doh_d
                        inv_actual = inv_f

                tabla_dia['Estado'] = tabla_dia['DOH_dia'].apply(_estado_abastecimiento)

            tabla_dia = tabla_dia.rename(columns={
                'fecha_factura': 'Fecha', 'cliente': 'Cliente', 'descripcion_producto': 'Producto',
                'Sell_In': 'Sell-In', 'Sell_Out': 'Sell-Out',
                'Kilos_In': 'Kilos Sell-In', 'Kilos_Out': 'Kilos Sell-Out',
                'Valor_In': 'Valor Sell-In ($)', 'Valor_Out': 'Valor Sell-Out ($)',
                'Inv_Anterior': 'Inv. Anterior', 'Variacion': 'Variación',
                'Inv_Final_U': 'Inv. Final (U)', 'DOH_dia': 'DOH',
            })
            if 'Fecha' in tabla_dia.columns:
                tabla_dia = tabla_dia.sort_values('Fecha').reset_index(drop=True)

            fmt_d = {}
            for c in ['Sell-In', 'Sell-Out', 'Inv. Anterior', 'Variación', 'Inv. Final (U)']:
                if c in tabla_dia.columns: fmt_d[c] = '{:,.0f}'
            for c in ['Kilos Sell-In', 'Kilos Sell-Out']:
                if c in tabla_dia.columns: fmt_d[c] = '{:,.1f} Kg'
            for c in ['Valor Sell-In ($)', 'Valor Sell-Out ($)']:
                if c in tabla_dia.columns: fmt_d[c] = '${:,.0f}'
            if 'DOH' in tabla_dia.columns: fmt_d['DOH'] = '{:,.1f}'

            if not tabla_dia.empty:
                st.dataframe(tabla_dia.style.format(fmt_d), use_container_width=True, height=450, hide_index=True)
            else:
                st.info("Sin datos diarios para esta selección.")
        else:
            st.info("Sin columna de fecha disponible para vista diaria.")

    else:
        # ── MODO VARIOS MESES: Productos Mes a Mes — columnas directas de resumen_mensual ──
        st.markdown("<h3 style='font-size:20px;font-weight:700;margin-top:10px;'>📅 Productos Mes a Mes</h3>",
                    unsafe_allow_html=True)
        if not dd_res.empty:
            mes_col_res = ('Mes_Txt' if 'Mes_Txt' in dd_res.columns
                           else ('mes' if 'mes' in dd_res.columns else None))

            # Columnas de identificación
            id_m = ([mes_col_res] if mes_col_res else []) + \
                   [c for c in ['cliente', 'descripcion_producto'] if c in dd_res.columns]

            # Columnas de ventas
            venta_m = [c for c in ['Unidades_Sell_In', 'Unidades_Sell_Out'] if c in dd_res.columns]

            # Columnas de inventario y DOH — directamente del resumen_mensual
            inv_cols = [c for c in [
                'Inventario_Anterior', 'Variacion_Inventario',
                'Unidades_Inventario_Final', 'Kilos_Inventario_Final',
                'DOH', 'Estado_Abastecimiento'
            ] if c in dd_res.columns]

            cols_sel  = id_m + venta_m + inv_cols
            tabla_mes = dd_res[cols_sel].drop_duplicates().copy()

            # Si Estado_Abastecimiento no viene del resumen, calcularlo desde DOH
            if 'Estado_Abastecimiento' not in tabla_mes.columns and 'DOH' in tabla_mes.columns:
                tabla_mes['Estado_Abastecimiento'] = tabla_mes['DOH'].apply(_estado_abastecimiento)

            ren_m = {
                mes_col_res: 'Mes', 'cliente': 'Cliente', 'descripcion_producto': 'Producto',
                'Unidades_Sell_In': 'Sell-In', 'Unidades_Sell_Out': 'Sell-Out',
                'Inventario_Anterior': 'Inv. Anterior', 'Variacion_Inventario': 'Variación',
                'Unidades_Inventario_Final': 'Inv. Final (U)', 'Kilos_Inventario_Final': 'Inv. Final (Kg)',
                'Estado_Abastecimiento': 'Estado',
            }
            tabla_mes = tabla_mes.rename(columns={k: v for k, v in ren_m.items() if k and k in tabla_mes.columns})

            if 'Mes' in tabla_mes.columns:
                tabla_mes = tabla_mes.sort_values('Mes').reset_index(drop=True)
            else:
                tabla_mes = tabla_mes.reset_index(drop=True)

            fmt_m = {}
            for c in ['Sell-In', 'Sell-Out', 'Inv. Anterior', 'Variación', 'Inv. Final (U)']:
                if c in tabla_mes.columns: fmt_m[c] = '{:,.0f}'
            if 'Inv. Final (Kg)' in tabla_mes.columns: fmt_m['Inv. Final (Kg)'] = '{:,.1f} Kg'
            if 'DOH'             in tabla_mes.columns: fmt_m['DOH']             = '{:,.1f}'

            st.dataframe(tabla_mes.style.format(fmt_m), use_container_width=True, height=450, hide_index=True)
        else:
            st.info("📊 Sin datos de resumen mensual disponibles.")


# ─────────────────────────────────────────
# TAB 3: IA

# ─────────────────────────────────────────

with tab_ia:
    st.markdown("### 🤖 Modelos Predictivos")

    # Dataframes SIN los filtros del Explorador (solo filtros globales)
    # para que esta sección NO se vea afectada por Cliente/SKU/Tipo/Marca/Origen
    _dd_in_ia  = df_in_mes.copy()
    _dd_out_ia = df_out_mes.copy()
    _DIMS_GLOBAL = {'canal':'canal_sel', 'regional':'reg_sel', 'categoria':'cat_sel', 'subcategoria':'subc_sel'}
    for _col, _key in _DIMS_GLOBAL.items():
        _sel = st.session_state.get(_key, [])
        if _sel:
            if _col in _dd_in_ia.columns:  _dd_in_ia  = _dd_in_ia[_dd_in_ia[_col].isin(_sel)]
            if _col in _dd_out_ia.columns: _dd_out_ia = _dd_out_ia[_dd_out_ia[_col].isin(_sel)]



    # ── 1. KPIs DE SHARE (Top 3 y Bottom 3) — PRIMERO como pediste ─────────────────────
    col_kpi1, col_kpi2 = st.columns(2)

    # Cálculo seguro con los filtros aplicados — por mes para saber en qué mes fue el share
    _merc_mes = df_merc.copy()
    if 'mes' in _merc_mes.columns:
        share_por_mes = _merc_mes.groupby(['mes', 'canal', 'categoria'])['share_compania'].mean().reset_index()
        share_por_mes['share_%'] = (share_por_mes['share_compania'] * 100).round(2)
        # Fila con mayor share
        _top_row    = share_por_mes.nlargest(3, 'share_%')
        # Fila con menor share (ascendente: el primero es el peor)
        _bottom_row = share_por_mes.nsmallest(3, 'share_%')
    else:
        share_por_mes = pd.DataFrame()
        _top_row = _bottom_row = pd.DataFrame()

    # También agrupación canal+categoria para los KPI (promedio global para ranking)
    share_group = df_merc.groupby(['canal', 'categoria'])['share_compania'].mean().reset_index()
    share_group = share_group.sort_values('share_compania', ascending=False)

    top3    = _top_row.reset_index(drop=True)    if not _top_row.empty    else share_group.head(3).assign(**{'share_%': lambda d: (d['share_compania']*100).round(2)})
    bottom3 = _bottom_row.reset_index(drop=True) if not _bottom_row.empty else share_group.tail(3).assign(**{'share_%': lambda d: (d['share_compania']*100).round(2)})

    def _mes_label(row):
        return str(row['mes'])[:7] if 'mes' in row.index and pd.notna(row.get('mes')) else ''

    with col_kpi1:
        if top3.empty or len(top3) < 1:
            st.markdown("""
            <div class="stat-card" style="border-color:#ff6b35;">
                <div class="stat-card-title">🔥 TOP 3 CANALES/CATEGORÍAS CON MAYOR SHARE</div>
                <div style="font-size:18px;color:#a9b8d5;padding:30px 20px;text-align:center;">
                    ⚠️ No hay datos de market share<br>con los filtros actuales
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            def _top_item(i):
                if len(top3) <= i: return '—', '—', '—', ''
                r = top3.iloc[i]; mes = _mes_label(r)
                return r.get('canal','—'), r.get('categoria','—'), r['share_%'], mes
            _tc, _tcat, _tpct, _tmes = _top_item(0)
            _2c, _2cat, _2pct, _2mes = _top_item(1)
            _3c, _3cat, _3pct, _3mes = _top_item(2)
            st.markdown(f"""
            <div class="stat-card" style="border-color:#ff6b35;">
                <div class="stat-card-title">🔥 TOP 3 CANALES/CATEGORÍAS CON MAYOR SHARE</div>
                <div style="font-size:22px;font-weight:700;color:#ffffff;margin:12px 0;">
                    {_tc}<br>
                    <span style="font-size:18px;">{_tcat}</span><br>
                    <span style="font-size:34px;color:#57cc99;">{_tpct}%</span>
                    <span style="font-size:13px;color:#a9b8d5;"> · {_tmes}</span>
                </div>
                <div style="color:#a9b8d5;font-size:14px;">
                    2°: {_2cat} ({_2pct}%){f' · {_2mes}' if _2mes else ''}<br>
                    3°: {_3cat} ({_3pct}%){f' · {_3mes}' if _3mes else ''}
                </div>
            </div>""", unsafe_allow_html=True)

    # KPI BOTTOM 3 — ascendente (menor share primero)
    with col_kpi2:
        if bottom3.empty or len(bottom3) < 1:
            st.markdown("""
            <div class="stat-card" style="border-color:#ffd166;">
                <div class="stat-card-title">⚠️ BOTTOM 3 CANALES/CATEGORÍAS CON MENOR SHARE</div>
                <div style="font-size:18px;color:#a9b8d5;padding:30px 20px;text-align:center;">
                    ⚠️ No hay datos de market share<br>con los filtros actuales
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            def _bot_item(i):
                if len(bottom3) <= i: return '—', '—', '—', ''
                r = bottom3.iloc[i]; mes = _mes_label(r)
                return r.get('canal','—'), r.get('categoria','—'), r['share_%'], mes
            _bc,  _bcat,  _bpct,  _bmes  = _bot_item(0)
            _b2c, _b2cat, _b2pct, _b2mes = _bot_item(1)
            _b3c, _b3cat, _b3pct, _b3mes = _bot_item(2)
            st.markdown(f"""
            <div class="stat-card" style="border-color:#ffd166;">
                <div class="stat-card-title">⚠️ BOTTOM 3 CANALES/CATEGORÍAS CON MENOR SHARE</div>
                <div style="font-size:22px;font-weight:700;color:#ffffff;margin:12px 0;">
                    {_bc}<br>
                    <span style="font-size:18px;">{_bcat}</span><br>
                    <span style="font-size:34px;color:#ef476f;">{_bpct}%</span>
                    <span style="font-size:13px;color:#a9b8d5;"> · {_bmes}</span>
                </div>
                <div style="color:#a9b8d5;font-size:14px;">
                    2°: {_b2cat} ({_b2pct}%){f' · {_b2mes}' if _b2mes else ''}<br>
                    3°: {_b3cat} ({_b3pct}%){f' · {_b3mes}' if _b3mes else ''}
                </div>
            </div>""", unsafe_allow_html=True)

    # ── 2. MARKET SHARE 100% STACKED ─────────────────────────────────────
    st.markdown("<h3 style='font-size:20px;font-weight:700;text-align:center;margin:35px 0 6px 0;'>"
                "📊 Market Share por Mes (Chacutería vs Competidores)</h3>", unsafe_allow_html=True)

    if not df_merc.empty:
        df_share = df_merc.copy()
        df_share['Otros'] = (1.0 - (df_share['share_compania'] + df_share['share_competidor_1'] + df_share['share_competidor_2'])).clip(lower=0)

        share_mensual = df_share.groupby('mes').agg({
            'share_compania': 'mean',
            'share_competidor_1': 'mean',
            'share_competidor_2': 'mean',
            'Otros': 'mean'
        }).reset_index()

        # Convertir a porcentaje real (0-100)
        for _sc in ['share_compania', 'share_competidor_1', 'share_competidor_2', 'Otros']:
            share_mensual[_sc] = (share_mensual[_sc] * 100).round(2)

        share_long = share_mensual.melt(
            id_vars=['mes'],
            value_vars=['share_compania', 'share_competidor_1', 'share_competidor_2', 'Otros'],
            var_name='Competidor',
            value_name='Share'
        )

        share_long['Competidor'] = share_long['Competidor'].map({
            'share_compania': 'Chacutería Foods',
            'share_competidor_1': 'Competidor 1',
            'share_competidor_2': 'Competidor 2',
            'Otros': 'Otros / Marcas Blancas'
        })

        fig_share = px.bar(
            share_long, x='mes', y='Share', color='Competidor', barmode='stack',
            color_discrete_map={
                'Chacutería Foods': '#ff6b35',
                'Competidor 1': '#2ec4b6',
                'Competidor 2': '#ffd166',
                'Otros / Marcas Blancas': '#a9b8d5'
            }
        )
        # Nombre del competidor + % real en tooltip
        fig_share.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>Mes: %{x}<br>Share: <b>%{y:.2f}%</b><extra></extra>",
            texttemplate="%{y:.1f}%",
            textposition="inside"
        )
        fig_share.update_layout(**_base_layout(
            xaxis_title="Mes", yaxis_title="Participación de Mercado (%)",
            yaxis=dict(ticksuffix='%', range=[0, 110]),
            legend=dict(title="Participación", orientation="h", yanchor="bottom", y=1.02),
            margin=dict(l=0, r=0, t=10, b=0), height=380
        ))
        st.plotly_chart(fig_share, use_container_width=True, key="market_share_chart")
    else:
        st.info("Sin datos de mercado para esta selección de filtros.")

    # ── 3. GRÁFICO REGRESIÓN CON LAGS ─────────────────────────────────────
    st.markdown("<h3 style='font-size:20px;font-weight:700;text-align:center;margin:35px 0 6px 0;'>"
                "📈 Pronóstico Regresión con Lags - Mercado + Chacutería + Competidores</h3>", unsafe_allow_html=True)

    if not df_merc.empty:
        df_m = df_merc.copy()
        df_m['mes'] = pd.to_datetime(df_m['mes'])
        
        df_m['vol_chacuteria'] = df_m['ventas_mercado_volumen'] * df_m['share_compania']
        df_m['vol_comp1']      = df_m['ventas_mercado_volumen'] * df_m['share_competidor_1']
        df_m['vol_comp2']      = df_m['ventas_mercado_volumen'] * df_m['share_competidor_2']
        
        hist = df_m.groupby('mes').agg({
            'ventas_mercado_volumen': 'sum',
            'vol_chacuteria': 'sum',
            'vol_comp1': 'sum',
            'vol_comp2': 'sum',
            'ventas_mercado_valor': 'sum'
        }).reset_index()

        data_reg = hist[['mes', 'ventas_mercado_volumen']].copy()
        data_reg = data_reg.rename(columns={'mes': 'ds', 'ventas_mercado_volumen': 'y'})
        for lag in [1, 2, 3]:
            data_reg[f'lag_{lag}'] = data_reg['y'].shift(lag)
        data_reg = data_reg.dropna().reset_index(drop=True)

        X = data_reg[['lag_1', 'lag_2', 'lag_3']]
        y = data_reg['y']
        model = LinearRegression().fit(X, y)

        ult_lags = data_reg[['lag_1', 'lag_2', 'lag_3']].iloc[-1:].values.copy()
        pron_market = []
        fechas_fut = pd.date_range(start=hist['mes'].max() + timedelta(days=30), periods=6, freq='M')
        for _ in range(6):
            pred = model.predict(ult_lags)[0]
            pron_market.append(max(0, pred))
            ult_lags = np.roll(ult_lags, 1)
            ult_lags[0][0] = pred

        avg_share_ch = hist['vol_chacuteria'].mean() / hist['ventas_mercado_volumen'].mean()
        avg_share_c1 = hist['vol_comp1'].mean() / hist['ventas_mercado_volumen'].mean()
        avg_share_c2 = hist['vol_comp2'].mean() / hist['ventas_mercado_volumen'].mean()

        pron_chac = np.array(pron_market) * avg_share_ch
        pron_comp1 = np.array(pron_market) * avg_share_c1
        pron_comp2 = np.array(pron_market) * avg_share_c2

        fig_lags = go.Figure()
        fig_lags.add_trace(go.Scatter(x=hist['mes'], y=hist['ventas_mercado_volumen'], name='Mercado Histórico', line=dict(color='#2ec4b6', width=3)))
        fig_lags.add_trace(go.Scatter(x=fechas_fut, y=pron_market, name='Mercado Pronóstico', line=dict(color='#ff6b35', dash='dash', width=4)))
        fig_lags.add_trace(go.Scatter(x=hist['mes'], y=hist['vol_chacuteria'], name='Chacutería Histórico', line=dict(color='#57cc99')))
        fig_lags.add_trace(go.Scatter(x=fechas_fut, y=pron_chac, name='Chacutería Pronóstico', line=dict(color='#57cc99', dash='dash')))
        fig_lags.add_trace(go.Scatter(x=hist['mes'], y=hist['vol_comp1'], name='Competidor 1 Histórico', line=dict(color='#ffd166')))
        fig_lags.add_trace(go.Scatter(x=fechas_fut, y=pron_comp1, name='Competidor 1 Pronóstico', line=dict(color='#ffd166', dash='dash')))
        fig_lags.add_trace(go.Scatter(x=hist['mes'], y=hist['vol_comp2'], name='Competidor 2 Histórico', line=dict(color='#a9b8d5')))
        fig_lags.add_trace(go.Scatter(x=fechas_fut, y=pron_comp2, name='Competidor 2 Pronóstico', line=dict(color='#a9b8d5', dash='dash')))

        fig_lags.update_traces(
            customdata=hist['ventas_mercado_valor'].tolist() + [0]*6,
            hovertemplate="<b>%{fullData.name}</b><br>Mes: %{x}<br>Volumen: %{y:,.0f} unidades<br>Valor Mercado: $%{customdata:,.0f}<extra></extra>"
        )

        fig_lags.update_layout(**_base_layout(
            xaxis_title="Mes", yaxis_title="Unidades de Volumen",
            margin=dict(l=0, r=0, t=10, b=0), height=520,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        ))
        st.plotly_chart(fig_lags, use_container_width=True, key="lags_pronostico_chart")
    else:
        st.info("Sin datos de mercado para esta selección de filtros.")


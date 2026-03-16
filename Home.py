import streamlit as st
import asyncio
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

st.set_page_config(
    page_title="Chacutería Foods S.A.S.",
    page_icon="🧀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilización de la marca (Rojo, Negro, Blanco)
st.markdown("""
    <style>
        .title {
            color: #D32F2F;
            font-size: 50px;
            font-weight: 800;
            text-align: center;
            margin-bottom: 20px;
        }
        .subtitle {
            font-size: 24px;
            font-weight: 600;
            color: #C0C0C0;
            text-align: center;
            margin-bottom: 30px;
        }
        .mission {
            font-size: 18px;
            color: #555555;
            text-align: center;
            font-style: italic;
            margin-bottom: 40px;
        }
        .card {
            background-color: #404040;
            color: white;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #D32F2F;
            margin-bottom: 20px;
        }
        .card h3 {
            color: white;
        }
        .card ul {
            color: white;
        }
        .card li {
            color: white;
        }
        .button-link {
            display: inline-block;
            background-color: #D32F2F;
            color: white;
            padding: 15px 40px;
            font-size: 20px;
            font-weight: bold;
            border-radius: 8px;
            text-align: center;
            text-decoration: none;
            cursor: pointer;
            margin-top: 30px;
        }
        .button-container {
            text-align: center;
        }
        .image-container {
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
        }
    </style>
""", unsafe_allow_html=True)

# Logo y Título
# Placeholder para logo (emoji de queso y embutidos)
st.markdown("<div class='title'>🧀 Chacutería Foods S.A.S. 🍷</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Pasión por el Sabor de Alta Calidad</div>", unsafe_allow_html=True)

# Imagen centrada y más pequeña
st.markdown("""
<div class='image-container'>
    <img src='https://images.unsplash.com/photo-1541592106381-b31e9677c0e5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80' 
    style='width: 600px; height: auto; border-radius: 10px;' />
</div>
""", unsafe_allow_html=True)

# Misión y Descripción
st.markdown("""
<div class='mission'>
"Nuestra misión es llevar la experiencia gourmet a las mesas de todo el país, distribuyendo los mejores quesos madurados, quesos frescos, y carnes curadas, garantizando frescura y sabor a través de una sólida red de canales comerciales."
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class='card'>
    <h3>🧀 Nuestro Portafolio</h3>
    <ul>
        <li><b>Quesos Madurados:</b> Parmesano, Gruyere, Gouda.</li>
        <li><b>Quesos Frescos:</b> Mozzarella, Campesino, Cuajada.</li>
        <li><b>Carnes Curadas:</b> Jamón Serrano, Salami, Prosciutto.</li>
        <li><b>Quesos Análogos:</b> Alternativas de excelente rendimiento para uso institucional.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='card'>
    <h3>🚚 Canales de Distribución</h3>
    <ul>
        <li><b>Grandes Superficies (Retailers):</b> Presencia a nivel nacional.</li>
        <li><b>Discounter:</b> Alianzas estratégicas para marcas propias.</li>
        <li><b>Mayoristas y Distribuidores:</b> Fuerte cobertura regional.</li>
        <li><b>Institucional:</b> Atención a hoteles y restaurantes (HORECA).</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class='button-container'>
<h4>¿Quieres conocer nuestro desempeño en cifras?</h4>
<a class='button-link' href='/Dashboard' target='_self'>📊 Ir al Dashboard Comercial</a>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<p style='text-align:center; color:gray;'>© 2026 Chacutería Foods S.A.S. - Todos los derechos reservados.</p>", unsafe_allow_html=True)

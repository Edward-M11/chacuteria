# Chacutería Foods S.A.S. - Dashboard Comercial

Este repositorio contiene la solución a la **Prueba Técnica de Analista de Planeación e Inteligencia de Negocios** para la empresa ficticia Chacutería Foods S.A.S.

## Módulos y Arquitectura

1. **Jupyter Notebook EDA (`eda_chacuteria.ipynb`):** Encargado de cargar, limpiar y consolidar todos los CSVs.
2. **Script de Ingesta (`upload_to_supabase.py`):** Encargado de enviar automáticamente los archivos una base de datos PostgreSQL hospedada en Supabase, garantizando que el dashboard no tenga que leer CSVs pesados en cada recarga.
3. **App Streamlit (`Home.py` y `pages/1_Dashboard.py`):** El Dashboard comercial modular con la página web corporativa y el análisis de negocio.

## Cómo Ejecutar Localmente

### Prerrequisitos

Tener `Python 3.9` o superior y clonar el repositorio.

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# 3. Instalar requerimientos
pip install -r requirements.txt
```

### Ejecutar EDA y Consolidar Datos

Abre Jupyter o ejecuta el notebook usando VS Code para leer los archivos locales (`paquete_candidato_chacuteria_foods/`) y generar el archivo `consolidado.parquet`.

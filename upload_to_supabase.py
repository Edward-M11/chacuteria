import os
from supabase import create_client
import pandas as pd
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("❌ No se encontraron SUPABASE_URL o SUPABASE_KEY en el archivo .env")

supabase = create_client(url, key)

archivos = {
    "consolidado_sell_in.csv": "sell_in",
    "consolidado_sell_out.csv": "sell_out",
    "maestro_clientes.csv": "clientes",
    "maestro_productos.csv": "productos",
    "resumen_mensual.csv": "resumen_mensual",
    "presupuesto.csv": "presupuesto",
    "mercado.csv": "mercado",
    "inventario_inicial.csv": "inventario_inicial"
}

print("🚀 Subiendo datos a Supabase...\n")

for csv_file, tabla in archivos.items():
    ruta = f"datos_limpios/{csv_file}"
    if os.path.exists(ruta):
        df = pd.read_csv(ruta)
        data = df.to_dict(orient="records")
        response = supabase.table(tabla).upsert(data).execute()
        print(f"✅ {csv_file} → tabla '{tabla}' ({len(data)} filas)")
    else:
        print(f"⚠️ No existe: {ruta}")

print("\n🎉 ¡Todos los datos subidos correctamente a Supabase!")
import os
import pandas as pd
import folium
from folium.plugins import HeatMap
from django.conf import settings

def generar_mapa_calor(csv_path, cie_filtro, geojson_path_custom=None):
    # RUTA SEGÚN TU IMAGEN: mapeo/static/Chiapas_geo.geojson
    geojson_path_default = os.path.join(settings.BASE_DIR, 'mapeo', 'static', 'Chiapas_geo.geojson')
    ruta_final_geo = geojson_path_custom if geojson_path_custom else geojson_path_default

    try:
        df = pd.read_csv(csv_path)
        
        # Limpieza para que Folium no falle con datos nulos
        df = df.dropna(subset=['LAT', 'LON', 'CASOS', 'CIE_10'])
        df['LAT'] = pd.to_numeric(df['LAT'], errors='coerce')
        df['LON'] = pd.to_numeric(df['LON'], errors='coerce')
        df = df.dropna(subset=['LAT', 'LON'])

        # Filtrar por la clave CIE-10
        df_filtrado = df[df['CIE_10'].astype(str).str.contains(cie_filtro, case=False, na=False)]

        # Crear el mapa base
        m = folium.Map(location=[16.5, -92.5], zoom_start=8, tiles='cartodbdark_matter')

        # Cargar el GeoJSON (Chiapas)
        if os.path.exists(ruta_final_geo):
            with open(ruta_final_geo, 'r', encoding='utf-8') as f:
                folium.GeoJson(f.read(), name="Capa Base Chiapas").add_to(m)

        # Añadir el HeatMap si hay resultados
        if not df_filtrado.empty:
            data = df_filtrado[['LAT', 'LON', 'CASOS']].values.tolist()
            HeatMap(data).add_to(m)

        return m
    except Exception as e:
        raise Exception(f"Error al generar el mapa: {e}")
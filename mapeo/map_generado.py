import os
import json
import pandas as pd
import folium
from branca.colormap import LinearColormap
from django.conf import settings

def generar_mapa_calor(csv_path, cie_filtro, geojson_path_custom=None):
    # =====================================================
    # RUTA GEOJSON
    # =====================================================
    geojson_path_default = os.path.join(
        settings.BASE_DIR,
        'mapeo',
        'static',
        'Chiapas_geo.geojson'
    )
    ruta_final_geo = (
        geojson_path_custom
        if geojson_path_custom
        else geojson_path_default
    )
    try:
        # =====================================================
        # LEER CSV
        # =====================================================
        try:
            df = pd.read_csv(csv_path, sep=',', encoding='utf-8')
        except:
            df = pd.read_csv(csv_path, sep=',', encoding='latin1')
        # =====================================================
        # VALIDAR COLUMNAS
        # =====================================================
        columnas_requeridas = ['LAT', 'LON', 'CASOS', 'CIE_10']
        for col in columnas_requeridas:
            if col not in df.columns:
                raise Exception(f"El CSV debe contener la columna: {col}")
        # =====================================================
        # LIMPIAR DATOS
        # =====================================================
        df = df.dropna(subset=['LAT', 'LON', 'CASOS', 'CIE_10'])
        df['LAT'] = pd.to_numeric(df['LAT'], errors='coerce')
        df['LON'] = pd.to_numeric(df['LON'], errors='coerce')
        df['CASOS'] = pd.to_numeric(df['CASOS'], errors='coerce')
        df = df.dropna(subset=['LAT', 'LON', 'CASOS'])
        # =====================================================
        # FILTRAR CIE
        # =====================================================
        df_filtrado = df[
            df['CIE_10']
            .astype(str)
            .str.contains(cie_filtro, case=False, na=False)
        ]
        if df_filtrado.empty:
            raise Exception(f"No se encontraron datos para: {cie_filtro}")
        # =====================================================
        # MAPA BASE
        # =====================================================
        m = folium.Map(location=[16.5, -92.5], zoom_start=7, tiles='CartoDB Positron')
        # =====================================================
        # GEOJSON TRANSPARENTE
        # =====================================================
        if os.path.exists(ruta_final_geo):
            with open(ruta_final_geo, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
                folium.GeoJson(
                    geojson_data,
                    name='GeoJSON',
                    style_function=lambda x: {
                        'fillColor': '#60a5fa',
                        'color': '#ffffff',
                        'weight': 1.5,
                        'fillOpacity': 0.15
                    }
                ).add_to(m)
        # =====================================================
        # MAPA DE COLORES
        # =====================================================
        minimo = df_filtrado['CASOS'].min()
        maximo = df_filtrado['CASOS'].max()
        colormap = LinearColormap(
            colors=['#38bdf8', '#22c55e', '#facc15', '#f97316', '#ef4444'],
            vmin=minimo,
            vmax=maximo
        )
        colormap.caption = f'Incidencia Oncológica ({cie_filtro})'
        colormap.add_to(m)
        # =====================================================
        # CÍRCULOS
        # =====================================================
        for _, row in df_filtrado.iterrows():
            lat, lon, casos = row['LAT'], row['LON'], row['CASOS']
            color = colormap(casos)
            radio = max(5, min(casos * 1.8, 65))
            folium.CircleMarker(
                location=[lat, lon],
                radius=radio,
                popup=f"""
                <div style='font-family:Arial'>
                    <h4 style='margin-bottom:10px'>Información Epidemiológica</h4>
                    <b>CIE-10:</b> {row['CIE_10']}<br>
                    <b>Casos:</b> {casos}<br>
                    <b>Municipio:</b> {row.get('MUNICIPIO', 'Sin dato')}
                </div>
                """,
                color='white',
                weight=2,
                fill=True,
                fill_color=color,
                fill_opacity=0.65,
                opacity=0.9
            ).add_to(m)
        # =====================================================
        # PANEL INFORMATIVO
        # =====================================================
        total_casos = int(df_filtrado['CASOS'].sum())
        panel_html = f"""
        <div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999;
                    background: rgba(255,255,255,0.88); padding: 18px;
                    border-radius: 18px; box-shadow: 0 6px 18px rgba(0,0,0,0.2);
                    font-family: Arial; width: 260px;">
            <h3 style="margin:0; margin-bottom:12px; color:#111827;">Análisis Epidemiológico</h3>
            <p style="margin:0;"><b>CIE-10:</b> {cie_filtro}</p>
            <p style="margin-top:10px;"><b>Total Casos:</b> {total_casos}</p>
        </div>
        """
        m.get_root().html.add_child(folium.Element(panel_html))
        # =====================================================
        # CONTROL DE CAPAS
        # =====================================================
        folium.LayerControl().add_to(m)
        return m
    except Exception as e:
        raise Exception(f"Error al generar el mapa: {e}")
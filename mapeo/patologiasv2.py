import pandas as pd
import folium as fm
import geopandas as gpd
import branca.colormap as cm
import json
import unidecode
from shapely.geometry import shape
from .models import IncidenciaOncologica

def limpiar_nombre(nombre):
    if not nombre:
        return ""
    if isinstance(nombre, list):
        nombre = nombre[0] if len(nombre) > 0 else ""
    return unidecode.unidecode(str(nombre)).strip().upper()

def obtener_datos_oncologicos(cie_id):
    queryset = IncidenciaOncologica.objects.filter(
        id_cie10__startswith=cie_id.upper()
    ).values('estado', 'municipio')
    df = pd.DataFrame(list(queryset))
    if not df.empty:
        df = df.groupby(['estado', 'municipio']).size().reset_index(name='total_casos')
        df['municipio_limpio'] = df['municipio'].apply(limpiar_nombre)
    return df

def generar_mapa_patologias(ruta_geojson, cie_id):
    #obtiene datos encologicos
    df_casos = obtener_datos_oncologicos(cie_id)
    #lee el gjson
    try:
        with open(ruta_geojson, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
    except Exception as e:
        print(f"Error leyendo GeoJSON: {e}")
        return None
   
   #featerus
    registros = []
    for feature in geojson_data['features']:
        props = feature['properties']
        geometry = shape(feature['geometry'])
        mun_name = props.get('mun_name', '')
        if isinstance(mun_name, list):
            mun_name = mun_name[0] if len(mun_name) > 0 else ""
        registros.append({
            'mun_name': mun_name,
            'mun_name_limpio': limpiar_nombre(mun_name),
            'geometry': geometry
        })
  #gdataframe
    gdf = gpd.GeoDataFrame(registros, geometry='geometry', crs="EPSG:4326")
    #combinar datos
    combinado = gdf.merge(df_casos, how='left', left_on='mun_name_limpio', right_on='municipio_limpio')
    #claud
    mapa = fm.Map(location=[16.5, -92.5], zoom_start=8, tiles='CartoDB Voyager')
   #agregar datos
    if not df_casos.empty and not combinado['total_casos'].dropna().empty:
        v_min = combinado['total_casos'].min()
        v_max = combinado['total_casos'].max()
        if v_min == v_max: v_max = v_min + 1
        # MAPA DE COLORES MODERNO
        colormap = cm.LinearColormap(
            colors=['#38bdf8', '#22c55e', '#facc15', '#f97316', '#ef4444'],
            vmin=v_min, vmax=v_max,
            caption=f'Incidencia Oncológica ({cie_id})'
        )
        colormap.add_to(mapa)
        # CREAR BURBUJAS
        for _, row in combinado.iterrows():
            if pd.notnull(row.get('total_casos')):
                centroide = row['geometry'].centroid
                fm.CircleMarker(
                    location=[centroide.y, centroide.x],
                    radius=max((row['total_casos'] ** 0.45) * 1.8, 3),
                    color='white',
                    weight=1.2,
                    fill=True,
                    fill_color=colormap(row['total_casos']),
                    fill_opacity=0.35,
                    popup=f"""
                    <div style="font-family: Arial; font-size: 14px;">
                        <b>{row['mun_name']}</b><br>
                        Casos registrados: <b>{int(row['total_casos'])}</b>
                    </div>
                    """
                ).add_to(mapa)
    else:
        # MOSTRAR MUNICIPIOS SI NO HAY DATOS
        fm.GeoJson(
            gdf,
            style_function=lambda x: {
                'color': '#2563eb',
                'weight': 1,
                'fillOpacity': 0.08
            }
        ).add_to(mapa)
    return mapa
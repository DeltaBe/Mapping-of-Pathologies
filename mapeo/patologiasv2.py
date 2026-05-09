import pandas as pd
import folium as fm
import geopandas as gpd
import branca.colormap as cm
from shapely.geometry import shape
import fiona
import unidecode
from io import BytesIO
from .models import IncidenciaOncologica  # Usamos el modelo de Django

def limpiar_nombre(nombre):
    """Limpia acentos y estandariza nombres para el cruce de datos."""
    if not nombre:
        return ""
    # Eliminamos acentos y pasamos a mayúsculas
    texto = unidecode.unidecode(str(nombre))
    return texto.strip().upper()

def obtener_datos_oncologicos(cie_id):
    """
    Obtiene estadísticas usando el ORM de Django. 
    Más seguro y eficiente que usar psycopg2 directamente.
    """
    queryset = IncidenciaOncologica.objects.filter(
        id_cie10__startswith=cie_id.upper()
    ).values('estado', 'municipio')
    
    df = pd.DataFrame(list(queryset))
    if not df.empty:
        # Agrupar y contar casos
        df = df.groupby(['estado', 'municipio']).size().reset_index(name='total_casos')
        df['municipio_limpio'] = df['municipio'].apply(limpiar_nombre)
    return df

def generar_mapa_patologias(archivo_geojson, cie_id):
    """Genera el mapa interactivo de patologías."""
    
    # 1. Obtener datos de la BD
    df_casos = obtener_datos_oncologicos(cie_id)
    
    # 2. Cargar GeoJSON desde memoria
    geojson_bytes = archivo_geojson.read()
    with fiona.BytesCollection(geojson_bytes) as src:
        gdf = gpd.GeoDataFrame.from_features(src, crs="EPSG:4326")
    
    # Estandarizar nombres en el mapa para el cruce
    gdf['mun_name_limpio'] = gdf['mun_name'].apply(limpiar_nombre)

    # 3. Unir datos (Merge)
    combinado = gdf.merge(
        df_casos, 
        how='left', 
        left_on='mun_name_limpio', 
        right_on='municipio_limpio'
    )

    # 4. Crear Mapa base
    mapa = fm.Map(
        location=[16.5, -94.5], # Centrado aproximado en la zona de interés
        zoom_start=7, 
        tiles='cartodbpositron'
    )

    # 5. Capa de Color y Marcadores
    if not combinado['total_casos'].dropna().empty:
        v_min = combinado['total_casos'].min()
        v_max = combinado['total_casos'].max()
        
        colormap = cm.LinearColormap(
            colors=['blue', 'yellow', 'red'],
            vmin=v_min,
            vmax=v_max,
            caption=f'Casos detectados de {cie_id}'
        ).add_to(mapa)

        for _, row in combinado.iterrows():
            if pd.notnull(row.get('total_casos')) and row['geometry']:
                centroide = row['geometry'].centroid
                fm.CircleMarker(
                    location=[centroide.y, centroide.x],
                    radius=max((row['total_casos'] ** 0.5) * 3, 5),
                    color=colormap(row['total_casos']),
                    fill=True,
                    fill_opacity=0.6,
                    popup=f"<b>{row['mun_name']}</b>: {int(row['total_casos'])} casos",
                    tooltip=row['mun_name']
                ).add_to(mapa)

    return mapa
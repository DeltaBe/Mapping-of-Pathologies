import folium as fm
import geopandas as gpd
import pandas as pd
import os
import branca.colormap as cm
from shapely.geometry import shape
import fiona

from django.conf import settings
from .models import IncidenciaOncologica

def generar_mapa_desde_bd_y_geojson(archivo_geojson, clave_cie):
    # Guardar temporalmente el GeoJSON
    geojson_path = os.path.join(settings.BASE_DIR, 'temp.geojson')
    with open(geojson_path, 'wb') as out:
        for chunk in archivo_geojson.chunks():
            out.write(chunk)

    # Cargar geometrías
    geometries = []
    with fiona.open(geojson_path, encoding='utf-8') as src:
        for feat in src:
            props = feat['properties']
            geom = shape(feat['geometry'])
            props['geometry'] = geom
            geometries.append(props)

    gdf = gpd.GeoDataFrame(geometries)
    gdf.set_crs(epsg=4326, inplace=True)
    gdf['mun_name'] = gdf['mun_name'].str.upper()

    # Cargar datos de base de datos
    datos = IncidenciaOncologica.objects.filter(id_cie10__startswith=clave_cie.upper())
    df = pd.DataFrame(list(datos.values('estado', 'municipio')))
    df = df.groupby(['estado', 'municipio']).size().reset_index(name='total_casos')
    df['municipio'] = df['municipio'].str.upper()

    # Unión
    combinado = gdf.merge(df, how='left', left_on='mun_name', right_on='municipio')

    # Crear mapa
    mapa = fm.Map(location=[23.6, -102.5], zoom_start=5, tiles='cartodbpositron')

    min_casos = combinado['total_casos'].min()
    max_casos = combinado['total_casos'].max()
    colormap = cm.StepColormap(
        ['#ccece6', '#66c2a4', '#238b45'],
        vmin=min_casos or 0,
        vmax=max_casos or 1,
        caption='Total de Casos'
    )
    colormap.add_to(mapa)

    for _, row in combinado.iterrows():
        if pd.notnull(row.get('total_casos')):
            centroide = row['geometry'].centroid
            fm.CircleMarker(
                location=[centroide.y, centroide.x],
                radius=max(row['total_casos'] ** 0.5, 4),
                fill=True,
                fill_color=colormap(row['total_casos']),
                fill_opacity=0.3,
                popup=f"{row['municipio']} - Casos: {row['total_casos']}"
            ).add_to(mapa)

    mapa_path = os.path.join(settings.STATICFILES_DIRS[0], 'mapa_dinamico.html')
    mapa.save(mapa_path)

    # Eliminar geojson
    os.remove(geojson_path)

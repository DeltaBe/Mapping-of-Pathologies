import folium as fm
import geopandas as gpd
import pandas as pd
import io
import branca.colormap as cm
from shapely.geometry import shape
import fiona
from .models import IncidenciaOncologica

def generar_mapa_desde_bd_y_geojson(archivo_geojson, clave_cie):
    """
    Genera un mapa interactivo procesando el GeoJSON en memoria 
    y cruzándolo con datos de la BD.
    """
    try:
        # 1. Procesar GeoJSON directamente en memoria (sin archivos temporales)
        # Esto evita errores de permisos y mejora la velocidad
        geojson_data = archivo_geojson.read()
        with fiona.BytesCollection(geojson_data) as src:
            geometries = []
            for feat in src:
                props = feat['properties']
                # Convertir la geometría de GeoJSON a objeto Shapely
                props['geometry'] = shape(feat['geometry'])
                geometries.append(props)

        gdf = gpd.GeoDataFrame(geometries)
        gdf.set_crs(epsg=4326, inplace=True)
        # Estandarizar a mayúsculas para un cruce de datos preciso
        gdf['mun_name'] = gdf['mun_name'].str.upper().str.strip()

        # 2. Consulta eficiente a la Base de Datos mediante el ORM de Django
        datos = IncidenciaOncologica.objects.filter(
            id_cie10__startswith=clave_cie.upper()
        ).values('estado', 'municipio')

        if not datos.exists():
            # Retornar un mapa base si no hay datos para esa clave CIE
            return fm.Map(location=[23.6, -102.5], zoom_start=5, tiles='cartodbpositron')

        # 3. Transformación de datos con Pandas
        df = pd.DataFrame(list(datos))
        df = df.groupby(['estado', 'municipio']).size().reset_index(name='total_casos')
        df['municipio'] = df['municipio'].str.upper().str.strip()

        # 4. Unión de datos espaciales y tabulares (Merge)
        combinado = gdf.merge(df, how='left', left_on='mun_name', right_on='municipio')

        # 5. Configuración del Mapa
        mapa = fm.Map(location=[23.6, -102.5], zoom_start=5, tiles='cartodbpositron')

        # Configurar escala de colores dinámica
        min_casos = combinado['total_casos'].min()
        max_casos = combinado['total_casos'].max()
        
        # Evitar errores si todos los valores son iguales o nulos
        if pd.isna(min_casos) or min_casos == max_casos:
            min_casos, max_casos = 0, 10

        colormap = cm.LinearColormap(
            colors=['#ccece6', '#66c2a4', '#238b45', '#00441b'],
            vmin=min_casos,
            vmax=max_casos,
            caption=f'Distribución de Casos: {clave_cie}'
        )
        colormap.add_to(mapa)

        # 6. Adición de Marcadores (Círculos Proporcionales)
        for _, row in combinado.iterrows():
            if pd.notnull(row.get('total_casos')) and row['geometry'] is not None:
                # Usar el centroide de la geometría para ubicar el marcador
                centroide = row['geometry'].centroid
                
                # El radio crece con la raíz cuadrada para no saturar el mapa
                radius_size = (row['total_casos'] ** 0.5) * 2

                fm.CircleMarker(
                    location=[centroide.y, centroide.x],
                    radius=max(radius_size, 3),
                    color=colormap(row['total_casos']),
                    fill=True,
                    fill_opacity=0.7,
                    popup=(f"<b>Municipio:</b> {row['mun_name']}<br>"
                           f"<b>Casos:</b> {int(row['total_casos'])}"),
                    tooltip=row['mun_name']
                ).add_to(mapa)

        return mapa

    except Exception as e:
        # En un entorno real, aquí usarías logger.error(e)
        print(f"Error generando el mapa: {e}")
        return None
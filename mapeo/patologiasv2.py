import psycopg2
import pandas as pd
import folium as fm
import geopandas as gpd
import branca.colormap as cm
from shapely.geometry import shape
import fiona as fn
import unidecode
import ast

DB_CONFIG = {
    "host": "localhost",
    "database": "ONCOLOGICA V6",
    "user": "postgres",
    "password": "1234",
    "port": "5433"
}

def limpiar_nombre(nombre):
    try:
        return unidecode.unidecode(ast.literal_eval(nombre)[0]).strip().upper()
    except Exception:
        return unidecode.unidecode(str(nombre)).strip().upper()

def obtener_datos_por_cie(cie_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_client_encoding('UTF8')
        cursor = conn.cursor()

        query = f"""
        SELECT estado, municipio, COUNT(*) AS total_casos
        FROM incidencia_oncologica
        WHERE id_cie10 LIKE '{cie_id}%'
        GROUP BY estado, municipio
        ORDER BY estado, municipio;
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=cols)

        cursor.close()
        conn.close()

        df['municipio'] = df['municipio'].astype(str).str.upper()
        df['municipio'] = df['municipio'].apply(limpiar_nombre)
        return df

    except Exception as e:
        print("❌ Error al obtener datos:", e)
        return pd.DataFrame()

def cargar_datos_geograficos(ruta_geojson, columna_nombre='mun_name'):
    features = []
    with fn.open(ruta_geojson, encoding='utf-8') as src:
        for feat in src:
            props = feat['properties']
            props['geometry'] = shape(feat['geometry'])
            features.append(props)
    gdf = gpd.GeoDataFrame(features)
    gdf.set_crs(epsg=4326, inplace=True)
    gdf[columna_nombre] = gdf[columna_nombre].astype(str).str.upper()
    gdf[columna_nombre] = gdf[columna_nombre].apply(limpiar_nombre)
    gdf = gdf.rename(columns={columna_nombre: 'mun_name'})
    return gdf

def generar_mapa_por_cie(cie_id, ruta_salida, municipio=None):
    # Definir rutas de los GeoJSON
    ruta_geojson_chiapas = 'C:/Users/mende/OneDrive/Documentos/ING. SOFTWARE/SEGUNDO AÑO/Estancia I/Estancia2/Proyecto/Mapping-of-Pathologies/mapeo/static/Chiapas_geo.geojson'
    ruta_geojson_oaxaca = 'C:/Users/mende/OneDrive/Documentos/ING. SOFTWARE/SEGUNDO AÑO/Estancia I/Estancia2/Proyecto/Mapping-of-Pathologies/mapeo/static/datos_geograficos_Oaxaca.geojson'
    # Obtener datos por CIE
    df = obtener_datos_por_cie(cie_id)
    
    # Filtrar por municipio si es proporcionado
    if municipio:
        df = df[df['municipio'] == municipio.upper()]

    # Cargar los datos geográficos de los archivos GeoJSON
    gdf_chiapas = cargar_datos_geograficos(ruta_geojson_chiapas)
    gdf_oaxaca = cargar_datos_geograficos(ruta_geojson_oaxaca)
    gdf = pd.concat([gdf_chiapas, gdf_oaxaca], ignore_index=True)

    # Realizar la unión entre los datos geográficos y los datos de la base de datos
    combinado = gdf.merge(df, how='left', left_on='mun_name', right_on='municipio')

    # Crear el mapa
    mapa = fm.Map(location=[17.0, -95.0], zoom_start=6, tiles='cartodbpositron')

    # Verificar si hay casos y añadir la capa de colores
    if combinado['total_casos'].notna().any():
        min_casos = combinado['total_casos'].min()
        max_casos = combinado['total_casos'].max()
        punto_bajo = min_casos + (max_casos - min_casos) * 0.33
        punto_medio = min_casos + (max_casos - min_casos) * 0.66

        # Crear el colormap para visualizar los casos
        colormap = cm.StepColormap(
            ['blue', 'yellow', 'red'],
            index=[min_casos, punto_bajo, punto_medio, max_casos],
            vmin=min_casos,
            vmax=max_casos,
            caption='Total de casos de cáncer de mama'
        )
        colormap.add_to(mapa)

        # Añadir los marcadores al mapa
        for _, row in combinado.iterrows():
            if pd.notnull(row.get('total_casos')):
                centroide = row['geometry'].centroid
                valor = row['total_casos']
                fm.CircleMarker(
                    location=[centroide.y, centroide.x],
                    radius=max(valor ** 0.5, 4),
                    fill=True,
                    fill_color=colormap(valor),
                    fill_opacity=0.2,
                    popup=f"{row['mun_name']}<br>Casos: {int(valor)}",
                    tooltip=row['mun_name']
                ).add_to(mapa)

    # Guardar el mapa en el archivo de salida
    mapa.save(ruta_salida)
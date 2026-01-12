import psycopg2
import geopandas as gpd
from shapely.geometry import shape
import fiona as fn
import unidecode

DB_CONFIG = {
    "host": "localhost",
    "database": "ONCOLOGICA V6",
    "user": "postgres",
    "password": "1234",
    "port": "5432"
}

def limpiar_nombre(nombre):
    try:
        return unidecode.unidecode(str(nombre)).strip().upper()
    except Exception:
        return ""

def conectar_db():
    return psycopg2.connect(**DB_CONFIG)

def crear_tabla_y_indice(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS municipios_geojson (
                id SERIAL PRIMARY KEY,
                mun_name VARCHAR(255) NOT NULL,
                geometry TEXT NOT NULL
            );
        """)
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS municipios_geojson_mun_name_uidx
            ON municipios_geojson (mun_name);
        """)
    conn.commit()

def cargar_features(ruta_geojson, columna_nombre='mun_name'):
    feats = []
    with fn.open(ruta_geojson, encoding='utf-8') as src:
        for feat in src:
            props = feat.get('properties') or {}
            geom  = shape(feat['geometry']) if feat.get('geometry') else None
            nombre = props.get(columna_nombre) or props.get('NOM_MUN') or props.get('name')
            nombre = limpiar_nombre(nombre)
            feats.append({"mun_name": nombre, "geometry": geom})
    return gpd.GeoDataFrame(feats)

def guardar_geojson_en_db(ruta_geojson, columna_nombre='mun_name'):
    gdf = cargar_features(ruta_geojson, columna_nombre)
    gdf = gdf[(gdf['geometry'].notnull()) & (gdf['mun_name'] != "")]

    conn = conectar_db()
    crear_tabla_y_indice(conn)

    with conn.cursor() as cur:
        for _, row in gdf.iterrows():
            geom_wkt = row['geometry'].wkt
            nombre   = row['mun_name']
            cur.execute("""
                INSERT INTO municipios_geojson (mun_name, geometry)
                VALUES (%s, %s)
                ON CONFLICT (mun_name) DO UPDATE
                SET geometry = EXCLUDED.geometry;
            """, (nombre, geom_wkt))
    conn.commit()
    conn.close()
    print("✅ GeoJSON cargado/actualizado en la base (WKT).")

# Rutas
ruta_geojson_chiapas = r"C:\Users\elver\Documents\ESTANCIA 1\DATA\Chiapas_geo.geojson"
ruta_geojson_oaxaca  = r"C:\Users\elver\Documents\ESTANCIA 1\DATA\datos_geograficos_Oaxaca.geojson"

guardar_geojson_en_db(ruta_geojson_chiapas)
guardar_geojson_en_db(ruta_geojson_oaxaca)

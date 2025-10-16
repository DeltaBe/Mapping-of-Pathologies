import psycopg2
import pandas as pd

def obtener_datos_por_cie(cie_id='C50'):
    host = "localhost"
    database = "ONCOLOGICA V6"
    user = "postgres"
    password = "1234"
    port = "5432"

    try:
        conexion = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )
        conexion.set_client_encoding('UTF8')
        cursor = conexion.cursor()

        consulta = """
            SELECT 
                estado,
                municipio,
                sexo,
                id_cie10,
                COUNT(*) AS total_casos
            FROM 
                incidencia_oncologica
            WHERE 
                id_cie10 LIKE %s
            GROUP BY 
                estado, municipio, sexo, id_cie10
            ORDER BY 
                estado, municipio;
        """

        cursor.execute(consulta, (f"{cie_id}%",))
        filas = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]

        df = pd.DataFrame(filas, columns=columnas)

        cursor.close()
        conexion.close()

        return df

    except Exception as e:
        print("Error al conectar o consultar:", e)
        return pd.DataFrame()

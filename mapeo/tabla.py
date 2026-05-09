import pandas as pd
from django.db.models import Count
from .models import IncidenciaOncologica

def obtener_datos_por_cie(cie_id='C50'):
    """
    Extrae estadísticas de incidencia filtradas por código CIE-10
    utilizando el motor de consultas de Django.
    """
    try:
        # 1. Consulta optimizada directamente desde el modelo
        # Filtramos por el código que empieza con el ID proporcionado
        # Agrupamos por los campos necesarios y contamos registros
        queryset = (
            IncidenciaOncologica.objects
            .filter(id_cie10__startswith=cie_id.upper())
            .values('estado', 'municipio', 'sexo', 'id_cie10')
            .annotate(total_casos=Count('idconsulta'))
            .order_by('estado', 'municipio')
        )

        # 2. Conversión a DataFrame para procesamiento de datos
        # El ORM devuelve un QuerySet de diccionarios, ideal para Pandas
        df = pd.DataFrame(list(queryset))

        # Manejo de caso donde no hay datos
        if df.empty:
            return pd.DataFrame(columns=['estado', 'municipio', 'sexo', 'id_cie10', 'total_casos'])

        return df

    except Exception as e:
        # Aquí podrías usar logging.error(f"Error en tabla.py: {e}")
        print(f"Error al obtener datos para la tabla: {e}")
        return pd.DataFrame()
import csv
import io
from .models import IncidenciaOncologica

def procesar_y_guardar_csv(archivo_csv):
    decoded_file = archivo_csv.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded_file))

    registros = []
    for row in reader:
        registros.append(IncidenciaOncologica(
            idconsulta=row['idconsulta'],
            fecha=row.get('fecha') or None,
            sexo=row.get('sexo'),
            diagnostico=row.get('diagnostico'),
            municipio=row.get('municipio'),
            estado=row.get('estado'),
            expediente=row.get('expediente'),
            paciente=row.get('paciente'),
            iddiagnostico=row.get('iddiagnostico'),
            primera_vez=row.get('primera_vez') or None,
            valor_clasificacion=row.get('valor_clasificacion'),
            diagnostico_cie10=row.get('diagnostico_cie10'),
            id_cie10=row.get('id_cie10'),
        ))

    IncidenciaOncologica.objects.bulk_create(registros)

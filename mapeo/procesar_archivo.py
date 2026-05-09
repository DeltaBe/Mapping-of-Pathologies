import csv
import io
import logging
from django.db import transaction, IntegrityError
from .models import IncidenciaOncologica

# Configuración de logs para rastrear errores sin detener la aplicación
logger = logging.getLogger(__name__)

def procesar_y_guardar_csv(archivo_csv):
    """
    Procesa un archivo CSV de incidencia oncológica de manera eficiente y segura.
    """
    registros_creados = 0
    registros_fallidos = 0
    
    try:
        # 1. Optimización de Memoria: Leemos el archivo por partes (chunks) 
        # en lugar de cargar todo el contenido de golpe con .read()
        decoded_file = (line.decode('utf-8') for line in archivo_csv)
        reader = csv.DictReader(decoded_file)

        registros_para_insertar = []

        # Usamos una transacción atómica para asegurar la integridad de la BD
        with transaction.atomic():
            for numero_linea, row in enumerate(reader, start=1):
                try:
                    # 2. Validación y Limpieza básica de datos
                    # Aseguramos que idconsulta exista y sea un valor válido
                    id_con = row.get('idconsulta')
                    if not id_con:
                        continue

                    # 3. Creación del objeto con limpieza de strings (.strip())
                    obj = IncidenciaOncologica(
                        idconsulta=id_con,
                        fecha=row.get('fecha') if row.get('fecha') else None,
                        sexo=row.get('sexo', '').strip()[:10],
                        diagnostico=row.get('diagnostico', '').strip(),
                        municipio=row.get('municipio', '').strip(),
                        estado=row.get('estado', '').strip(),
                        expediente=row.get('expediente', '').strip(),
                        paciente=row.get('paciente', '').strip(),
                        iddiagnostico=row.get('iddiagnostico', '').strip()[:5],
                        # Validación de entero para 'primera_vez'
                        primera_vez=int(row['primera_vez']) if row.get('primera_vez') and row['primera_vez'].isdigit() else None,
                        valor_clasificacion=row.get('valor_clasificacion', '').strip(),
                        diagnostico_cie10=row.get('diagnostico_cie10', '').strip(),
                        id_cie10=row.get('id_cie10', '').strip()[:10],
                    )
                    
                    registros_para_insertar.append(obj)
                    
                    # 4. Inserción por lotes (Batch processing)
                    # Insertamos cada 1000 registros para no saturar la conexión
                    if len(registros_para_insertar) >= 1000:
                        IncidenciaOncologica.objects.bulk_create(registros_para_insertar, ignore_conflicts=True)
                        registros_creados += len(registros_para_insertar)
                        registros_para_insertar = []

                except (ValueError, TypeError) as e:
                    logger.warning(f"Error de formato en línea {numero_linea}: {e}")
                    registros_fallidos += 1
                    continue

            # Insertar los registros restantes que no llegaron al lote de 1000
            if registros_para_insertar:
                IncidenciaOncologica.objects.bulk_create(registros_para_insertar, ignore_conflicts=True)
                registros_creados += len(registros_para_insertar)

        return {
            "estado": "exito",
            "creados": registros_creados,
            "fallidos": registros_fallidos
        }

    except Exception as e:
        logger.error(f"Error crítico procesando CSV: {e}")
        return {
            "estado": "error",
            "mensaje": str(e)
        }
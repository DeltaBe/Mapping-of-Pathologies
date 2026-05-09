from django.db import models

class Enfermedad(models.Model):
    """
    Catálogo maestro de enfermedades basado en la codificación CIE-10.
    """
    id_cie10 = models.CharField(
        max_length=10, 
        primary_key=True, 
        verbose_name="Código CIE-10"
    )
    diagnostico_cie10 = models.CharField(
        max_length=255, 
        verbose_name="Descripción del Diagnóstico"
    )

    class Meta:
        db_table = 'enfermedades'
        verbose_name = 'Enfermedad'
        verbose_name_plural = 'Catálogo de Enfermedades'
        ordering = ['id_cie10']

    def __str__(self):
        return f"{self.id_cie10} - {self.diagnostico_cie10}"


class IncidenciaOncologica(models.Model):
    """
    Registro detallado de incidencias oncológicas.
    """
    idconsulta = models.BigIntegerField(primary_key=True)
    fecha = models.DateField(null=True, blank=True, db_index=True)
    
    # Datos demográficos
    sexo = models.CharField(max_length=20, null=True, blank=True)
    paciente = models.CharField(max_length=255, null=True, blank=True)
    expediente = models.CharField(max_length=50, null=True, blank=True)
    
    # Datos geográficos (Indexados para optimizar mapas)
    municipio = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    estado = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    
    # Relación con el catálogo de enfermedades
    # Usamos CharField para id_cie10 si los datos del CSV pueden no estar en el catálogo aún,
    # o ForeignKey si queremos integridad total. Aquí lo mantenemos flexible:
    id_cie10 = models.CharField(max_length=10, db_index=True)
    diagnostico_cie10 = models.CharField(max_length=255, null=True, blank=True)
    
    # Otros datos técnicos
    iddiagnostico = models.CharField(max_length=10, null=True, blank=True)
    primera_vez = models.IntegerField(null=True, blank=True)
    valor_clasificacion = models.CharField(max_length=100, null=True, blank=True)
    diagnostico_clinico = models.TextField(null=True, blank=True) # Renombrado para mayor claridad

    class Meta:
        db_table = 'incidencia_oncologica'
        verbose_name = 'Incidencia Oncográfica'
        verbose_name_plural = 'Incidencias Oncográficas'
        # Indexación compuesta para búsquedas frecuentes de mapas
        indexes = [
            models.Index(fields=['id_cie10', 'municipio']),
        ]

    def __str__(self):
        return f"Consulta {self.idconsulta} - {self.id_cie10}"
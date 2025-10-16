from django.db import models

# Create your models here.
#creo la tabla proyecto
# y le pongo un campo name que es un charfield con maximo 100 caracteres y unico
class proyecto(models.Model):
    name = models.CharField(max_length=100, unique=True)
# este metodo me permite devolver el nombre del proyecto cuando se imprima el objeto
    def __str__(self):
        return self.name

class Task(models.Model):
    title = models.CharField(max_length=100)
    descripcion = models.TextField()
    proyect = models.ForeignKey(proyecto, on_delete=models.CASCADE, related_name='tasks')
    done = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title + '-' + self.proyect.name
    
 
 
    
class Enfermedad(models.Model):
    id_cie10 = models.CharField(max_length=10, primary_key=True)
    diagnostico_cie10 = models.CharField(max_length=255)

    class Meta:
        db_table = 'enfermedades'
        verbose_name = 'Enfermedad'
        verbose_name_plural = 'Enfermedades'

    def __str__(self):
        return f"{self.id_cie10} - {self.diagnostico_cie10}"


class IncidenciaOncologica(models.Model):
    idconsulta = models.BigIntegerField(primary_key=True)
    fecha = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=10, null=True, blank=True)
    diagnostico = models.CharField(max_length=255)
    municipio = models.CharField(max_length=255, null=True, blank=True)
    estado = models.CharField(max_length=255, null=True, blank=True)
    expediente = models.CharField(max_length=50, null=True, blank=True)
    paciente = models.CharField(max_length=255, null=True, blank=True)
    iddiagnostico = models.CharField(max_length=5, null=True, blank=True)
    primera_vez = models.IntegerField(null=True, blank=True)
    valor_clasificacion = models.CharField(max_length=60, null=True, blank=True)
    diagnostico_cie10 = models.CharField(max_length=255, null=True, blank=True)
    id_cie10 = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        db_table = 'incidencia_oncologica'
        verbose_name = 'Incidencia Oncológica'
        verbose_name_plural = 'Incidencias Oncológicas'

    def __str__(self):
        return f"{self.idconsulta} - {self.diagnostico}"
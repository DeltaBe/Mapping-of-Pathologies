from django.contrib import admin
from .models import Enfermedad, IncidenciaOncologica

# Registro del catálogo de enfermedades
@admin.register(Enfermedad)
class EnfermedadAdmin(admin.ModelAdmin):
    list_display = ('id_cie10', 'diagnostico_cie10')
    search_fields = ('id_cie10', 'diagnostico_cie10')

# Registro de las incidencias con filtros útiles para tu proyecto
@admin.register(IncidenciaOncologica)
class IncidenciaOncologicaAdmin(admin.ModelAdmin):
    list_display = ('idconsulta', 'id_cie10', 'municipio', 'estado', 'fecha')
    list_filter = ('estado', 'sexo', 'fecha')
    search_fields = ('paciente', 'expediente', 'id_cie10', 'municipio')
    # Esto ayuda a cargar rápido si tienes miles de registros
    list_per_page = 50
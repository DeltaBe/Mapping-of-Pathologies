from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.conf import settings
import os

from mapeo.map_generado import generar_mapa_calor

# 1. IMPORTACIONES CORREGIDAS (Solo modelos que existen)
from .models import IncidenciaOncologica, Enfermedad
from .forms import CIE10Form, ArchivoOncologiaForm
from .tabla import obtener_datos_por_cie
from .procesar_archivo import procesar_y_guardar_csv
from .generar_mapa import generar_mapa_desde_bd_y_geojson
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def index(request):
    title = "Sistema de Mapeo Oncológico"
    # Contamos casos reales para mostrar en el index si lo deseas
    total_casos = IncidenciaOncologica.objects.count()
    return render(request, 'index.html', {
        'title': title,
        'total_casos': total_casos
    })

def about(request):
    """
    Vista para visualizar el mapa generado.
    """
    cie_id = "C50"  # Valor por defecto (Cáncer de mama)
    
    if request.method == "POST":
        cie_id = request.POST.get("cie_id", "C50")
    
    # El archivo mapa.html debe existir en tus estáticos o ser generado
    nombre_archivo = "mapa.html"
    
    return render(request, 'about.html', {
        'mapa_file': nombre_archivo,
        'cie_id': cie_id,
    })

# def proyects(request):
#     """
#     Refactorizado: Muestra un resumen por estados en lugar de 'proyectos'.
#     """
#     resumen_estados = (
#         IncidenciaOncologica.objects.values('estado')
#         .distinct()
#         .order_by('estado')
#     )
#     return render(request, 'proyects.html', {'proyectos': resumen_estados})

def tasks(request):
    """
    Vista informativa sobre las claves CIE-10 y manual de uso.
    """
    return render(request, 'proyects.html')

def create_task(request):
    """
    Vista para buscar datos específicos por CIE-10 y mostrarlos en tabla.
    """
    datos = []
    cie_id = 'C50' 
    form = CIE10Form(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        cie_id = form.cleaned_data['cie_id'] or 'C50'
    
    # Usamos la lógica profesional de tabla.py que refactorizamos
    df = obtener_datos_por_cie(cie_id)
    if not df.empty:
        datos = df.to_dict(orient='records')

    context = {
        'form': form,
        'datos': datos,
        'cie_id': cie_id
    }
    return render(request, 'create_task.html', context)


def tasks_view(request):
    if request.method == 'POST':
        form = ArchivoOncologiaForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_csv = request.FILES.get('archivo_csv')
            archivo_geojson = request.FILES.get('archivo_geojson')
            clave_cie = form.cleaned_data['clave_cie']

            try:
                # 1. Guardado temporal de archivos subidos
                path_csv = default_storage.save('temp/analisis.csv', ContentFile(archivo_csv.read()))
                full_csv = os.path.join(settings.MEDIA_ROOT, path_csv)
                
                full_geo = None
                if archivo_geojson:
                    path_geo = default_storage.save('temp/analisis.json', ContentFile(archivo_geojson.read()))
                    full_geo = os.path.join(settings.MEDIA_ROOT, path_geo)

                # 2. Generar el mapa
                mapa_obj = generar_mapa_calor(full_csv, clave_cie, full_geo)

                # 3. GUARDAR CON UN NOMBRE DIFERENTE PARA NO SOBRESCRIBIR NADA
                # Usamos 'mapa_temporal.html' para la pestaña de carga
                ruta_salida = os.path.join(settings.BASE_DIR, 'mapeo', 'static', 'mapa_temporal.html')
                mapa_obj.save(ruta_salida)

                # 4. Limpiar temporales de la carpeta media
                default_storage.delete(path_csv)
                if full_geo: default_storage.delete(path_geo)

                return redirect('ver_mapa')

            except Exception as e:
                return render(request, 'task.html', {'form': form, 'mensaje': f"Error: {e}"})
    else:
        form = ArchivoOncologiaForm()
    
    return render(request, 'task.html', {'form': form})

def ver_mapa(request):
    # Esta vista ahora solo sirve para mostrar el mapa que acabas de cargar
    return render(request, 'mostrar_mapa.html')
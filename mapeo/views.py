import time
import traceback

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.conf import settings
import os

from mapeo.map_generado import generar_mapa_calor
from mapeo.patologiasv2 import generar_mapa_patologias

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
    cie_id = request.POST.get("cie_id", "C50").strip() if request.method == "POST" else "C50"
    
    ruta_geojson = os.path.join(settings.BASE_DIR, 'mapeo', 'static', 'Chiapas_geo.geojson')
    nombre_archivo = "mapa.html"
    ruta_mapa = os.path.join(settings.BASE_DIR, 'mapeo', 'static', nombre_archivo)

    try:
        # Generar el nuevo objeto mapa
        mapa_obj = generar_mapa_patologias(ruta_geojson, cie_id)
        
        if mapa_obj:
            # ELIMINAR EL ANTERIOR para evitar bloqueos de Windows
            if os.path.exists(ruta_mapa):
                try:
                    os.remove(ruta_mapa)
                except:
                    pass # Si está bloqueado, Folium intentará sobrescribirlo de todos modos
            
            mapa_obj.save(ruta_mapa)
    except Exception as e:
        return HttpResponse(f"Error crítico: {e}")

    return render(request, 'about.html', {
        'mapa_file': nombre_archivo,
        'cie_id': cie_id,
        'timestamp': time.time() # Para forzar la recarga del iframe
    })
    
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
    mensaje = None
    if request.method == 'POST':
        form = ArchivoOncologiaForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_csv = request.FILES.get('archivo_csv')
            archivo_geojson = request.FILES.get('archivo_geojson')
            clave_cie = form.cleaned_data['clave_cie']
            try:
                # =====================================
                # VALIDAR Y GUARDAR CSV TEMPORAL
                # =====================================
                if not archivo_csv:
                    raise Exception("Debes subir un archivo CSV.")
                
                path_csv = default_storage.save('temp/analisis.csv', ContentFile(archivo_csv.read()))
                full_csv = os.path.join(settings.MEDIA_ROOT, path_csv)
                
                # =====================================
                # GUARDAR GEOJSON SI EXISTE
                # =====================================
                full_geo = None
                if archivo_geojson:
                    path_geo = default_storage.save('temp/analisis.geojson', ContentFile(archivo_geojson.read()))
                    full_geo = os.path.join(settings.MEDIA_ROOT, path_geo)
                
                # =====================================
                # GENERAR Y GUARDAR MAPA
                # =====================================
                mapa_obj = generar_mapa_calor(full_csv, clave_cie, full_geo)
                if mapa_obj is None:
                    raise Exception("No se pudo generar el mapa.")
                
                ruta_salida = os.path.join(settings.BASE_DIR, 'mapeo', 'static', 'mapa_temporal.html')
                
                if os.path.exists(ruta_salida):
                    try: os.remove(ruta_salida)
                    except: pass
                
                mapa_obj.save(ruta_salida)
                
                # =====================================
                # LIMPIEZA Y REDIRECCIÓN
                # =====================================
                default_storage.delete(path_csv)
                if full_geo:
                    default_storage.delete(path_geo)
                
                return redirect('ver_mapa')
            except Exception as e:
                print("\n========== ERROR COMPLETO ==========\n")
                print(traceback.format_exc())
                print("\n====================================\n")
                mensaje = f"Error: {e}"
    else:
        form = ArchivoOncologiaForm()
    
    return render(request, 'task.html', {'form': form, 'mensaje': mensaje})

def ver_mapa(request):
    return render(request, 'mostrar_mapa.html', {'timestamp': time.time()})



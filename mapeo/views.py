from django.shortcuts import render, redirect

# Create your views here.
#para poder enviar alggo al cliente por medio de una respuesta http
# el jsonresponse nos permite enviar un objeto json y el HttpResponse nos permite enviar una cadena de texto
from django.http import HttpResponse , JsonResponse
# Register your models here.

#importamos los modelos que hemos creado para poder hacer consultas a la base de datos
from .models import proyecto, Task

from django.shortcuts import get_object_or_404
#funcion que nos permite devolver una respuesta http

from .forms import CreateNewTask
from .forms import CreateNewProyecto

from .forms import CIEForm
from .patologiasv2 import generar_mapa_por_cie  # Asegúrate de tener esta función
from django.contrib import messages
import os
from django.conf import settings
from .tabla import obtener_datos_por_cie
from .forms import CIE10Form

import os
import uuid

from .forms import ArchivoOncologiaForm
from .procesar_archivo import procesar_y_guardar_csv
from .generar_mapa import generar_mapa_desde_bd_y_geojson




def index(request):
    title = "Mi primer proyecto con Django"
    return render(request,'index.html', {'title': title})



def about(request):
    cie_id = "C50"  # Valor por defecto
    municipio = None  # Sin municipio por defecto
    
    # Verificar si el formulario fue enviado con POST
    if request.method == "POST":
        cie_id = request.POST.get("cie_id", "C50")
        municipio = request.POST.get("municipio", None)  # Obtener el municipio desde el formulario
    
    nombre_archivo = f"mapa.html"
    ruta_completa = os.path.join(settings.BASE_DIR, 'mapeo', 'static', nombre_archivo)
    
    # Generar el nuevo mapa con el ID CIE y municipio si se ha seleccionado
    if municipio:
        generar_mapa_por_cie(cie_id, municipio=municipio, ruta_salida=ruta_completa)
    else:
        generar_mapa_por_cie(cie_id, ruta_salida=ruta_completa)
    
    return render(request, 'about.html', {
        'mapa_file': nombre_archivo,
        'cie_id': cie_id,
        'municipio': municipio  # Pasar el municipio a la plantilla
    })
#funcion que nos permite devolver un parametro
def hello(request,username):
    print(username)
    #devolver una respuesta http
    #en este caso una cadena de texto
    return HttpResponse("<h1>Hello World %s</h1>" % username)



def proyec(request):
    return HttpResponse("proyec")

def task(request):
    return HttpResponse("task")




def proyects(request):
    #obtenemos todos los proyectos de la base de datos
    #y los convertimos a un objeto json para que se pueda enviar al cliente
    #usamos el metodo values() para obtener un diccionario con los campos de la tabla
    proyectos = proyecto.objects.all()
    # return JsonResponse(proyectos , safe=False )
    
    
    
    return render(request,'proyects.html', {'proyectos': proyectos})

def tasks(request):
    #obtenemos todas las tareas del proyecto con el id que nos han pasado
    #usamos el metodo get() para obtener un objeto de la base de datos
    task=Task.objects.all()
    
    # usamos get_object_or_404 para obtener el objeto o devolver un error 404 si no existe
    # get_object_or_404 es una funcion que nos permite obtener un objeto de la base de datos o devolver un error 404 si no existe
    # task = get_object_or_404(Task, id=id)
    # return HttpResponse("task %s" % task.title)
    
    return render(request,'task.html', {'task': task})


def create_task(request):
    datos = None
    cie_id = 'C50'  # Valor por defecto
    form = CIE10Form(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        cie_id = form.cleaned_data['cie_id'] or 'C50'
    
    df = obtener_datos_por_cie(cie_id)
    datos = df.to_dict(orient='records') if not df.empty else []

    context = {
        'form': form,
        'datos': datos,
        'cie_id': cie_id
    }
    return render(request, 'create_task.html', context)
    



def tasks_view(request):
    mensaje = ''
    if request.method == 'POST':
        form = ArchivoOncologiaForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_csv = form.cleaned_data['archivo_csv']
            archivo_geojson = form.cleaned_data['archivo_geojson']
            clave_cie = form.cleaned_data['clave_cie']

            try:
                procesar_y_guardar_csv(archivo_csv)
                generar_mapa_desde_bd_y_geojson(archivo_geojson, clave_cie)
                mensaje = '✅ Archivos procesados y mapa generado correctamente.'
                return redirect('tasks')
            except Exception as e:
                mensaje = f'❌ Error: {e}'
    else:
        form = ArchivoOncologiaForm()

    return render(request, 'task.html', {'form': form, 'mensaje': mensaje})


def create_proyect(request):
    if request.method == 'GET':
        return render(request, 'layouts/create_proyect.html', {'forms': CreateNewProyecto()})
    else:
        form = CreateNewProyecto(request.POST)
        if form.is_valid():
            proyecto.objects.create(
                name=form.cleaned_data['name']
            )
            return redirect('proyects')
        return render(request, 'layouts/create_proyect.html', {'forms': form})
    














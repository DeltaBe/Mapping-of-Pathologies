from django.urls import path
from . import views

urlpatterns = [
    # Ruta principal del sitio
    path('', views.index, name='index'),
    
    # Visualización del mapa generado
    path('about/', views.about, name='about'),
    
    # Visualización de la lista de incidencias (reemplaza a la antigua vista de tareas)
    path('tasks/', views.tasks, name='tasks'),
    
    # Carga de archivos CSV/GeoJSON y generación de mapas
    path('tasks_view/', views.tasks_view, name='tasks_view'),
    
    # Consultas por CIE-10 y visualización de tablas de datos
    path('create_task/', views.create_task, name='create_task'),
    
    path('ver-mapa/', views.ver_mapa, name='ver_mapa'),
]
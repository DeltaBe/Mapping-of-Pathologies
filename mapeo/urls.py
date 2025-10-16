from django.urls import path
from . import views



urlpatterns = [
    # añadimos la ruta para la vista hello
    # cuando se acceda a la raiz del sitio web, se llamara a la funcion hello
    path('',views.index,name='index'),
    #cuando se acceda a la ruta /about/ se llamara a la funcion about
    path('about/',views.about,name='about'),
    #cuando se acceda a la ruta /hello/<username> se llamara a la funcion hello
    # y se le pasara el parametro username para acceder a ella es necesario hello\
    path('hello/<str:username>',views.hello ,  name='hello'),
    #cuando se acceda a la ruta /proyec/ se llamara a la funcion proyec
    path('proyects/', views.proyects , name='proyects'),
    path('tasks/', views.tasks_view, name='tasks'),
    path('create_task/', views.create_task, name='create_task'),
    path('create_proyect/', views.create_proyect, name='create_proyect'),
    
]

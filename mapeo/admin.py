
from django.contrib import admin
from .models import proyecto, Task

#anadir en el admin los modelos que hemos creado
admin.site.register(proyecto)
admin.site.register(Task)

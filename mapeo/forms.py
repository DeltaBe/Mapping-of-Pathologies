#aqui creamos nuestro formularios

from django import forms
from .models import proyecto, Task

class CreateNewTask(forms.Form):
    title = forms.CharField(label='Title', max_length=100)
    descripcion = forms.CharField(widget=forms.Textarea , label='descripcion')
    
class CreateNewProyecto(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    
    
    
class CIEForm(forms.Form):
    cie_id = forms.CharField(
        label='Seleccionar enfermedad por ID CIE',
        max_length=10,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej. C50.9',
            'class': 'entrada-cie'
        })
    )
    


class CIE10Form(forms.Form):
    cie_id = forms.CharField(
        label='Clave CIE10',
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej. C50',
            'class': 'input-cie'
        })
    )
    
    


class ArchivoOncologiaForm(forms.Form):
    archivo_csv = forms.FileField(label="Archivo CSV de datos oncológicos")
    archivo_geojson = forms.FileField(label="Archivo GeoJSON del estado")
    clave_cie = forms.CharField(label="Clave CIE-10", max_length=10)
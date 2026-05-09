from django import forms

# Eliminamos la importación de proyecto y Task que causaba el error

class CIE10Form(forms.Form):
    """Formulario para filtrar por código CIE-10 en la tabla de datos."""
    cie_id = forms.CharField(
        label='Clave CIE-10',
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej. C50',
            'class': 'form-control input-cie'
        })
    )

class CIEForm(forms.Form):
    """Formulario secundario para selección de enfermedad."""
    cie_id = forms.CharField(
        label='Seleccionar enfermedad por ID CIE',
        max_length=10,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej. C50.9',
            'class': 'form-control entrada-cie'
        })
    )

class MunicipioFilterForm(forms.Form):
    """Formulario para filtrar mapas por municipio."""
    municipio = forms.CharField(
        label='Seleccionar Municipio', 
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

class ArchivoOncologiaForm(forms.Form):
    """Formulario para la carga masiva de datos y generación de mapas."""
    archivo_csv = forms.FileField(
        label="Archivo CSV de datos oncológicos",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    archivo_geojson = forms.FileField(
        label="Archivo GeoJSON del estado",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        required=False
    )
    clave_cie = forms.CharField(
        label="Clave CIE-10", 
        max_length=10,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej. C50',
            'class': 'form-control'
        })
    )
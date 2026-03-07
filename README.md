#  Mapping of Pathologies - Sistema Epidemiológico

Este proyecto es un sistema de visualización de datos epidemiológicos basado en **Django** y **Folium**. Permite cargar datos de salud, filtrarlos por códigos **CIE (Clasificación Internacional de Enfermedades)** y visualizarlos en un mapa interactivo.

##  Características

- **Mapa Interactivo:** Visualización de patologías utilizando `folium` con capas de `CartoDB Positron`.
- **Filtro Dinámico:** Búsqueda rápida por clave CIE (ej. C50, C18).
- **Diseño Responsivo:** Interfaz adaptada para escritorio y dispositivos móviles.
- **Análisis de Datos:** Procesamiento de datos mediante `Pandas` para segmentación por municipio.

## 🛠️ Tecnologías Utilizadas

* **Backend:** [Django 5.2.1](https://www.djangoproject.com/)
* **Análisis de Datos:** [Pandas](https://pandas.pydata.org/)
* **Mapas:** [Folium](https://python-visualization.github.io/folium/)
* **Frontend:** HTML5, CSS3 (Flexbox/Grid), Django Templates.

## 📦 Instalación y Configuración

Sigue estos pasos para ejecutar el proyecto localmente:

1. **Clona el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/nombre-del-repo.git](https://github.com/tu-usuario/nombre-del-repo.git)
   cd nombre-del-repo

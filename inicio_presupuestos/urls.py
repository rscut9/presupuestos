from django.urls import path
from .views import inicio_presupuestos, crear_material, editar_material, datos

urlpatterns = [
    path("", inicio_presupuestos, name="inicio_presupuestos"),
    path("crear-material/", crear_material, name="crear_material"),
    path("datos/", datos, name="datos"),
    path('editar-material/', editar_material, name='editar_material'),
]

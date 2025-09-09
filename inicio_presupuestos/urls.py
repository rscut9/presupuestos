from django.urls import path
from .views import inicio_presupuestos

urlpatterns = [
    path("", inicio_presupuestos, name="inicio_presupuestos"),
]

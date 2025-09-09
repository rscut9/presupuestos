from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("inicio_presupuestos.urls")),  # raíz -> vista "Hola"
    path("admin/", admin.site.urls),
]

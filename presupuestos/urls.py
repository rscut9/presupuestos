from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("inicio_presupuestos.urls")),  # <--- Aquí se conectan las rutas de tu app
]

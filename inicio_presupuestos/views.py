from django.shortcuts import render
from .forms import PresupuestoForm

def inicio_presupuestos(request):
    form = PresupuestoForm()
    return render(request, "inicio_presupuestos.html", {"form": form})

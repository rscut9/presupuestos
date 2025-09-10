from django.shortcuts import render
from django.forms import formset_factory
from .forms import PresupuestoForm, ItemForm

def inicio_presupuestos(request):
    ItemsFormSet = formset_factory(ItemForm, extra=12)

    if request.method == "POST":
        form = PresupuestoForm(request.POST)
        formset = ItemsFormSet(request.POST, prefix="it")
        if form.is_valid() and formset.is_valid():
            # Cálculo de totales
            bruto = form.cleaned_data.get("precio_bruto") or 0
            iva_pct = form.cleaned_data.get("iva") or 21
            total = bruto * (1 + (iva_pct / 100))
            form.cleaned_data["precio_total"] = round(total, 2)

            ctx = {
                "form": form,
                "formset": formset,
                "calc_total": f"{total:.2f}",
                "submitted": True,
            }
            return render(request, "inicio_presupuestos.html", ctx)

    else:
        form = PresupuestoForm()
        formset = ItemsFormSet(prefix="it")

    ctx = {"form": form, "formset": formset}
    return render(request, "inicio_presupuestos.html", ctx)

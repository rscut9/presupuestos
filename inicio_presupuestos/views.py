from django.shortcuts import render
from django.forms import formset_factory
from .forms import PresupuestoForm, ItemForm
from .mongo import get_db

def inicio_presupuestos(request):
    ItemsFormSet = formset_factory(ItemForm, extra=12)
    if request.method == "POST":
        form = PresupuestoForm(request.POST)
        formset = ItemsFormSet(request.POST, prefix="it")
        if form.is_valid() and formset.is_valid():
            bruto = form.cleaned_data.get("precio_bruto") or 0
            iva_pct = form.cleaned_data.get("iva") or 21
            total = bruto * (1 + (iva_pct / 100))
            form.cleaned_data["precio_total"] = round(total, 2)
            ctx = {"form": form, "formset": formset, "calc_total": f"{total:.2f}", "submitted": True}
            return render(request, "inicio_presupuestos.html", ctx)
    else:
        form = PresupuestoForm()
        formset = ItemsFormSet(prefix="it")
    return render(request, "inicio_presupuestos.html", {"form": form, "formset": formset})

def crear_material(request):
    return render(request, "crear_material.html")

def _stringify_ids(docs):
    out = []
    for d in docs:
        d = dict(d)
        if "_id" in d:
            d["_id"] = str(d["_id"])
        out.append(d)
    return out

def datos(request):
    db = get_db()
    usuarios = _stringify_ids(list(db.usuarios.find({})))

    # columnas dinámicas
    campos = sorted({k for u in usuarios for k in u.keys()})

    # preparamos las filas ya ordenadas por columnas
    filas = [[u.get(c, "") for c in campos] for u in usuarios]

    return render(request, "datos.html", {"campos": campos, "filas": filas})

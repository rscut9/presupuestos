from django.shortcuts import render, redirect
from django.forms import formset_factory
from django.contrib import messages
from .forms import PresupuestoForm, ItemForm, MaterialForm
from .mongo import get_db
from bson.objectid import ObjectId
from datetime import datetime
import json

def inicio_presupuestos(request):
    ItemsFormSet = formset_factory(ItemForm, extra=12)

    # Cargar materiales desde Mongo (solo el campo 'material')
    db = get_db()
    materiales = sorted([
        d["material"] for d in db.materiales.find({}, {"_id": 0, "material": 1})
        if "material" in d
    ])

    if request.method == "POST":
        form = PresupuestoForm(request.POST)
        formset = ItemsFormSet(request.POST, prefix="it")
        if form.is_valid() and formset.is_valid():
            bruto = form.cleaned_data.get("precio_bruto") or 0
            iva_pct = form.cleaned_data.get("iva") or 21
            total = bruto * (1 + (iva_pct / 100))
            form.cleaned_data["precio_total"] = round(total, 2)
            ctx = {
                "form": form,
                "formset": formset,
                "calc_total": f"{total:.2f}",
                "submitted": True,
                "materiales": materiales,
            }
            return render(request, "inicio_presupuestos.html", ctx)
    else:
        form = PresupuestoForm()
        formset = ItemsFormSet(prefix="it")

    return render(
        request,
        "inicio_presupuestos.html",
        {"form": form, "formset": formset, "materiales": materiales},
    )


def crear_material(request):
    return render(request, "crear_material.html")

def _to_serializable(v):
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, datetime):
        return v.isoformat()
    try:
        json.dumps(v)
        return v
    except Exception:
        return str(v)

def _normalize_docs(docs):
    out = []
    for d in docs:
        d2 = {}
        for k, v in dict(d).items():
            if isinstance(v, (list, dict)):
                d2[k] = json.dumps(v, ensure_ascii=False)
            else:
                d2[k] = _to_serializable(v)
        out.append(d2)
    return out

def datos(request):
    db = get_db()
    colecciones = sorted(db.list_collection_names())
    seleccion = request.GET.get("collection") or (colecciones[0] if colecciones else None)

    campos, filas, total = [], [], 0
    if seleccion:
        total = db[seleccion].count_documents({})
        docs = list(db[seleccion].find({}).limit(500))
        docs = _normalize_docs(docs)
        campos = sorted({k for d in docs for k in d.keys()})
        filas = [[d.get(c, "") for c in campos] for d in docs]

    ctx = {
        "colecciones": colecciones,
        "seleccion": seleccion,
        "campos": campos,
        "filas": filas,
        "total": total,
    }
    return render(request, "datos.html", ctx)

def crear_material(request):
    db = get_db()

    if request.method == "POST":
        form = MaterialForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data["material"].strip()

            # id autoincremental
            last = db.materiales.find_one(
                sort=[("id", -1)],
                projection={"id": 1, "_id": 0}
            )
            next_id = (last["id"] + 1) if last else 1

            fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            db.materiales.insert_one({
                "id": next_id,
                "material": nombre,
                "fecha_creación": fecha_str,
            })

            messages.success(request, f"Material guardado con id {next_id}.")
            return redirect("crear_material")
    else:
        form = MaterialForm()

    return render(request, "crear_material.html", {"form": form})
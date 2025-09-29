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

def _to_serializable(v):
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, datetime):
        return v.isoformat()
    try:
        json.dumps(v); return v
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

        # Ocultar _id en todos los casos
        for d in docs:
            d.pop("_id", None)

        if seleccion == "materiales":
            base_order = ["id", "material", "fecha_creación", "fecha_actualización"]
            extras = sorted({k for dd in docs for k in dd.keys()} - set(base_order))
            campos = base_order + extras
        else:
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

def editar_material(request):

    db = get_db()

    # Guardar cambio
    if request.method == "POST":
        try:
            mat_id = int(request.POST.get("id"))
        except (TypeError, ValueError):
            messages.error(request, "ID inválido.")
            return redirect("editar_material")

        nuevo_nombre = (request.POST.get("material") or "").strip()
        if not nuevo_nombre:
            messages.error(request, "El nombre del material no puede estar vacío.")
            return redirect("editar_material")

        fecha_upd = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        db.materiales.update_one(
            {"id": mat_id},
            {"$set": {
                "material": nuevo_nombre,
                "fecha_actualización": fecha_upd
            }}
        )
        messages.success(request, f"Material {mat_id} actualizado.")
        return redirect("editar_material")

    # Modo listado/edición
    try:
        edit_id = int(request.GET.get("edit")) if request.GET.get("edit") else None
    except ValueError:
        edit_id = None

    materiales = list(
        db.materiales.find(
            {},
            {"_id": 0, "id": 1, "material": 1, "fecha_creación": 1, "fecha_actualización": 1}
        ).sort("id", 1)
    )

    return render(request, "editar_material.html", {
        "materiales": materiales,
        "edit_id": edit_id
    })
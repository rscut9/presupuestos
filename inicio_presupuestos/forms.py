from django import forms

class PresupuestoForm(forms.Form):
    # Bloque 1
    cliente = forms.CharField(label="Cliente", max_length=100)
    calle = forms.CharField(label="Calle", max_length=120)
    ciudad = forms.CharField(label="Ciudad", max_length=80)
    codigo_postal = forms.CharField(label="Código Postal", max_length=10)

    # Bloque 2 (tabla materiales se gestiona con formset)
    # ...

    # Bloque 4
    observaciones = forms.CharField(
        label="Observaciones",
        widget=forms.Textarea(attrs={"rows": 3}),
        initial="Garantía de mano de obra 6 meses y materiales 2 años"
    )

    # Totales
    precio_bruto = forms.DecimalField(label="Precio bruto (€)", max_digits=10, decimal_places=2)
    iva = forms.DecimalField(label="IVA (21 %)", max_digits=5, decimal_places=2, initial=21)
    precio_total = forms.DecimalField(label="PRECIO TOTAL (€)", max_digits=10, decimal_places=2, required=False)

class ItemForm(forms.Form):
    material = forms.CharField(label="Material", required=False, max_length=150)
    cantidad = forms.IntegerField(label="Cantidad", required=False, min_value=0)

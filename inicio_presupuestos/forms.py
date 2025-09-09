from django import forms

class PresupuestoForm(forms.Form):
    cliente = forms.CharField(label="Cliente", max_length=100)
    calle = forms.CharField(label="Calle", max_length=150)
    ciudad = forms.CharField(label="Ciudad", max_length=100)
    codigo_postal = forms.CharField(label="Código Postal", max_length=10)
    material = forms.CharField(label="Material", max_length=100)
    cantidad = forms.IntegerField(label="Cantidad", min_value=1)
    precio_bruto = forms.DecimalField(label="Precio bruto", max_digits=10, decimal_places=2)
    iva = forms.DecimalField(label="IVA (21%)", max_digits=5, decimal_places=2, initial=21, disabled=True)
    precio_total = forms.DecimalField(label="Precio total", max_digits=10, decimal_places=2, required=False, disabled=True)

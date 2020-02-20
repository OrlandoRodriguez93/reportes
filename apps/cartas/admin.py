from django.contrib import admin
from apps.cartas.models import Pensionado, Reporte, Credito, Deuda, Plazo

admin.site.register(Pensionado)
admin.site.register(Reporte)
admin.site.register(Credito)
admin.site.register(Deuda)
admin.site.register(Plazo)

# Register your models here.

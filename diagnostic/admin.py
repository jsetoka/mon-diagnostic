from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Vehicule, Diagnostic

admin.site.register(Vehicule)
admin.site.register(Diagnostic)


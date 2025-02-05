from django.contrib import admin
from .models import *

class ClienteAdmin(admin.ModelAdmin):
    list_display = ['id', 'numero', 'nome', 'cnpj', 'empresa', 'valor']
    list_display_links = ['id']

admin.site.register(Empresa)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Account)
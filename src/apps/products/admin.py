from django.contrib import admin
from admin_registrar import AdminRegistrar

from src.apps.products.apps import ProductsConfig

registrar = AdminRegistrar(ProductsConfig)
registrar.register()

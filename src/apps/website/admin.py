from django.contrib import admin
from admin_registrar import AdminRegistrar

from src.apps.website.apps import WebsiteConfig

registrar = AdminRegistrar(WebsiteConfig)

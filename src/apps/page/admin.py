from django.contrib import admin
from admin_registrar import AdminRegistrar

from src.apps.feedback.apps import FeedbackConfig

registrar = AdminRegistrar(FeedbackConfig)
registrar.register()

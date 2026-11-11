from logging import getLogger

from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from src.shared.views import handler404 as handler404

from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    *debug_toolbar_urls(),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

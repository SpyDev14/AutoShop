from django.contrib.sitemaps.views import sitemap
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include

from debug_toolbar.toolbar import debug_toolbar_urls

from src.shared.sitemaps import get_sitemaps_for_paged_models
from src.shared.views import handler404 as handler404


_sitemaps = get_sitemaps_for_paged_models()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, kwargs={"sitemaps": _sitemaps}),
    *debug_toolbar_urls(),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

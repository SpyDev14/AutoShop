from django.contrib.sitemaps.views import sitemap
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path

from src.apps.website import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("favicon.ico", views.FaviconView.as_view()),
    path("robots.txt", views.RobotsView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

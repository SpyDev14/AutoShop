from django.shortcuts import redirect
from django.views import View
from django.http import HttpResponse, HttpResponseNotFound

from src.apps.website.models import SiteSettings


class FaviconView(View):
    def get(self, request):
        try:
            favicon_url = SiteSettings.get_solo().favicon.url
        except ValueError:
            return HttpResponseNotFound()

        return redirect(favicon_url)


class RobotsView(View):
    def get(self, request):
        return HttpResponse(SiteSettings.get_solo().robots_txt_content, content_type="text/plain")

from logging import getLogger

from django.template.exceptions import TemplateDoesNotExist
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

_logger = getLogger(__name__)


def handler404(request: HttpRequest, exception: Exception):
    try:
        return render(request, "404.html", {"exception": exception}, status=404)
    except TemplateDoesNotExist as ex:
        _logger.error(ex)
        return HttpResponse("Страница не найдена", status=404)

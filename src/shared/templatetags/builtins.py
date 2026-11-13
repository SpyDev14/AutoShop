from typing import Any
import json

from django.db.models import Model
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.template import Template, RequestContext, Library


register = Library()

@register.filter("getattr")
def _getattr(obj, attr_name: str, default = None):
    print(getattr(obj, attr_name, default))
    return getattr(obj, attr_name, default)

@register.filter
def eq(obj1, obj2):
    return obj1 == obj2

@register.filter("or")
def _or(obj1, obj2):
    return obj1 or obj2

@register.filter
def get_admin_url(model: Model):
    return f"/{reverse("admin")}/{model._meta.app_label}/{model._meta.model_name}/{model.pk}/change/"

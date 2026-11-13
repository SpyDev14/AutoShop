from typing import TYPE_CHECKING

from django.db import models

class AnnotatePkMixin:
    if TYPE_CHECKING:
        def __init__(self, *args, **kwargs):
            self.pk: int | None

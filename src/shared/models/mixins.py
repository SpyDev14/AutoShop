from django.db import models


class CreatedAtMixin:
    created_at = models.DateTimeField("Дата создания", auto_now_add=True, editable=False)

from datetime import time

from django.db import models

from phonenumber_field.modelfields import PhoneNumberField
from solo.models import SingletonModel


class CompanyInfo(SingletonModel):
    phone = PhoneNumberField("Основной телефон для связи", default="+70000000000")
    email = models.EmailField("Основная почта для связи", default="kds@granfort.ru")
    work_time_starts = models.TimeField("Время начала работы", default=time(hour=9))
    work_time_ends = models.TimeField("Время начала работы", default=time(hour=18))

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        verbose_name = "📑 | Информация о компании"

    def __str__(self):
        return "Основная информация"

from django.db import models

from phonenumber_field.modelfields import PhoneNumberField

from src.apps.products.models import Car, ProductKind, Material
from src.apps.users import User


class FeedbackRequest(models.Model):
    phone_number = PhoneNumberField("Номер телефона")
    requestener_name = models.CharField("Имя", max_length=24, help_text="Как к вам обращатся")
    city = models.CharField("Город", help_text="Например, Тула")

    interest_car = models.ForeignKey(Car, models.SET_NULL, null=True, default=None, verbose_name="Машина")
    interest_product_kind = models.IntegerField("Что нужно", choices=ProductKind.choices, default=ProductKind.BOTH)
    interest_material = models.ForeignKey(Material, models.SET_NULL, null=True, verbose_name="Материал")
    interest_turnkey_installation = models.BooleanField("Установка под ключ", default=True)

    client_is_served = models.BooleanField(
        "Клиент обслужен",
        default=False,
        help_text="Поставьте галочку, когда клиент был обслужен, т.е заявка был обработана.",
    )
    served_at = models.DateTimeField("Дата закрытия заявки", help_text="Когда было обслужено")
    served_by = models.ForeignKey(User, models.SET_NULL, null=True, verbose_name="Закрыл")
    created_at = models.DateTimeField("Дата заполнения заявки", auto_now_add=True, editable=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заявка на обратную связь"
        verbose_name_plural = "Заявки на обратную связь"

    def __str__(self):
        return f"Заявка от {self.requestener_name}, тел.: {self.phone_number}"


class EmailRecipient(models.Model):
    email = models.EmailField("Эл. адрес", unique=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True, editable=False)


class EmailLog(models.Model):
    recipient = models.ForeignKey(EmailRecipient, models.SET_NULL, verbose_name="Получатель", null=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True, editable=False)

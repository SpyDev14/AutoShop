from django.db import models

from phonenumber_field.modelfields import PhoneNumberField


class FeedbackRequest(models.Model):
    phone_number = PhoneNumberField("Номер телефона")
    requestener_name = models.CharField("Имя", max_length=24, help_text="Как к вам обращатся")
    # Машина
    # Что нужно
    # Материал
    city = models.CharField("Город", help_text="Например, Тула")
    turnkey_installation = models.BooleanField("Установка под ключ", default=True)

    # seen = models.BooleanField(
    #     "Увидено персоналом",
    #     default=False,
    #     help_text=(
    #         "Если уведомление о создании новой заявки успешно ушло "
    #         'в телеграм — автоматически считается "Увиденным". '
    #         "Иначе, считается что заявку не увидели и нужно вручную "
    #         "поставить эту галочку админке, когда её увидят."
    #     ),
    # )
    created_at = models.DateTimeField("Дата заполнения заявки", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заявка на обратную связь"
        verbose_name_plural = "Заявки на обратную связь"

    def __str__(self):
        return f"Заявка от {self.requestener_name} {self.phone_number}"


class EmailRecipient(models.Model):
    email = models.EmailField("Эл. адрес", unique=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True, editable=False)


class EmailLog(models.Model):
    recipient = models.ForeignKey(EmailRecipient, models.SET_NULL, verbose_name="Получатель", null=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True, editable=False)

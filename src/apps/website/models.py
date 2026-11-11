from django.db import models
from solo.models import SingletonModel


class SiteSettings(SingletonModel):
    site_name = models.CharField(
        "Название сайта", max_length=128, default="JBrony Site", help_text="В основном используется в base.html"
    )
    favicon = models.ImageField(blank=True, upload_to="favicon")
    robots_txt_content = models.TextField("Содержимое Robots.txt", blank=True)
    head_addition = models.TextField(
        "Дополнительный контент <head>",
        blank=True,
        help_text="Этот текст будет вставлен в конце &lthead&gt на каждой html-странице сайта",
    )

    class Meta:
        verbose_name = "⚙ | Настройки сайта"

    def __str__(self):
        return "⚙ | Настройки сайта"

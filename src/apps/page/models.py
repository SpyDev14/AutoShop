from functools import cached_property
from typing import Optional
import logging

from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.urls import reverse, NoReverseMatch
from django.db import models

from tinymce.models import HTMLField

from src.shared.models.bases import PagedModel, OrderedModel

from src.shared.constants import RENDERING_SUPPORTS_TEXT
from src.apps.page.constants import GENERIC_TEMPLATE

# CI
# from core.views.bases import GenericPageView

_logger = logging.getLogger(__name__)


class DynamicPageManager(models.Manager):
    def get_by_slug(self, slug: str) -> Optional["DynamicPage"]:
        """
        Попытается вернуть объект Page с указанным slug.
        Если Page с таким slug нет - вернёт None и оставит запись в логах.
        """
        page = self.filter(slug=slug).first()
        if not page:
            _logger.warning(f"Page со slug = {slug} не существует, ")
        return page


class DynamicPage(OrderedModel, PagedModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra_context_manager: models.Manager["ExtraContext"]
        self.children_pages: models.Manager["DynamicPage"]

    add_to_header = models.BooleanField(
        "Отображать в главном header?",
        default=True,
        help_text="Страницы без этой галочки не будут отображаться в главном хедере сайта.",
    )

    content = HTMLField("Контент", blank=True, help_text=RENDERING_SUPPORTS_TEXT)
    is_generic_page = models.BooleanField(
        "Это динамически-добавляемая страница?",
        default=False,
        help_text=mark_safe(
            '✅: Будет автоматически доступно по url <code>"/&ltslug&gt/"</code>, требует заданного '
            "<code>Template name</code>. Используйте для простых страниц, которым не нужен свой View.<br>"
            "❌: Выбирайте, когда для обработки страницы нужно использовать кастомный View.<br>"
            "<br>"
            "Влияет на логику работы полей <code>URL Pathname</code> и <code>Template name</code>."
        ),
    )

    url_name = models.CharField(
        "URL Name",
        max_length=64,
        blank=True,
        help_text=mark_safe(
            "<code>is_generic_page:</code>✅ - Игнорируется, потому <b>должно быть</b> пустым."
            "<br>"
            "<code>is_generic_page:</code>❌ - <code>name</code> того url, который обрабатывает эту страницу."
            '<details style="padding-left: 1rem;">'
            'Например, в ваших <code>urlpatterns</code> есть <code>path("fun-path/", some_view, '
            'name="your-name")</code>, тут указываете <code>"your-name"</code>.<br>'
            "Вы всё корретно указали, метод <code>get_absolute_url()</code> вернёт ссылку на этот "
            'path, т.е <code>"/fun-path/"</code>.<br>'
            "<br>"
            'Для index страницы по полному пути "/", а также для generic страниц с кастомным '
            "URL в принципе, увы, но вы вынуждены создавать свои собственные url и view, даже если вам не "
            "нужна дополнительная логика."  # В прочем, как-будто бы кому-то не пофиг, раньше
            # все всегда делали View-ы под каждую страницу
            "</details>"
        ),
    )

    template_name = models.CharField(
        "Название django-темплейта",
        blank=True,
        # Ps: DetailView имеет функционал для получения темплейта из поля модели, но я не хочу,
        # чтобы было 2 разных способа задать темплейт - через модель и в классе View,
        # это усложнит понимание работы этого поля, поэтому всегда через View.
        help_text=mark_safe(
            "<code>is_generic_page:</code>✅ - Путь к файлу, включая расширение. "
            f"По умолчанию используется <code>{GENERIC_TEMPLATE.PAGE}</code><br>"
            "<code>is_generic_page:</code>❌ - Игнорируется, потому <b>должно быть</b> пустым."
        ),
    )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        verbose_name = "страница"
        verbose_name_plural = "страницы"
        ordering = ["order"]

    def clean(self):
        # Проверка template_name
        if not self.is_generic_page and self.template_name:
            raise ValidationError(
                {
                    "template_name": "Должно быть пустым при is_generic_page:❌, так как "
                    "игнорируется (строгое обеспечение явности)."
                }
            )

        # Проверка url_source
        if self.is_generic_page and self.url_name:
            raise ValidationError(
                {
                    "url_name": "Должно быть пустым при is_generic_page:❌, так как "
                    "игнорируется (строгое обеспечение явности)."
                }
            )

        if not self.is_generic_page:
            try:
                self.get_absolute_url()
            except NoReverseMatch:
                raise ValidationError({"url_name": "path с таким name не существует!"})

    def get_absolute_url(self):
        if self.is_generic_page:
            # Этот формат должен оставаться неизменным
            return f"/{self.slug}/"

        return reverse(self.url_name)

    # В контексте объект Page живёт только 1 запрос,
    # но внутри могут много раз обращаться к этому св-ву
    # Поэтому cached_property
    @cached_property
    def extra_context(self) -> dict:
        """Для темплейтов"""
        return {ctx.key: ctx.value for ctx in self.extra_context_manager.all()}

    def get_breadcrumbs(self):
        return [self] if self.slug != "index" else []


class ExtraContext(models.Model):
    key = models.CharField("Ключ", max_length=64)
    value = models.CharField("Значение")
    page = models.ForeignKey(
        DynamicPage,
        models.CASCADE,
        blank=True,
        null=True,
        related_name="extra_context_manager",
        verbose_name="Привязать к странице",
        help_text=mark_safe(
            "Если указать здесь страницу - ключ будет доступен через объект страницы "
            "и будет исключён из глобального контекста (<code>global.extra_context</code>).<br>"
            "Тем не менее, он всё также будет доступен глобально, но уже через <code>global.pages</code>"
        ),
    )

    class Meta:
        verbose_name = "Дополнительный контекст"
        verbose_name_plural = "Дополнительный контекст"

    def __str__(self):
        if self.page is None:
            return f"global {self.key}"
        else:
            return f'{self.key} for page "{self.page}"'

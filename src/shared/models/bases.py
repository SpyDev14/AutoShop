from typing import Any, Self, Sequence
import json, logging

from django.core.exceptions import ImproperlyConfigured, FieldDoesNotExist
from django.urls import reverse, NoReverseMatch
from django.db import models

from src.shared.reflection import typename
from src.shared.seo.og import OgType
from src.apps.website.models import SiteSettings


_logger = logging.getLogger(__name__)


class OrderedModel(models.Model):
    pk: int
    order = models.PositiveSmallIntegerField(default=0, db_index=True)

    class Meta:
        abstract = True
        ordering = ["order"]


class UniqueNamedModel(models.Model):
    pk: int
    name = models.CharField("Название", max_length=80, unique=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name


class PagedModel(models.Model):
    """Базовая модель для всех моделей со своей detail-страницой"""

    pk: int

    # см. get_absolute_url()
    # Под редкое переопределение в подклассах
    _url_path_name: str | None = None
    _url_kwarg_name: str = "slug"

    name = models.CharField(
        "Название",
        max_length=128,
        help_text="Указывайте человеко-читаемый текст. По умолчанию также используется для HTML Title и H1.",
    )
    slug = models.SlugField(max_length=128, unique=True)
    _h1 = models.CharField(  # Названо с _ чтобы не было путаницы с get_h1 (не использовали h1 напрямую)
        "H1 Заголовок", max_length=128, blank=True, help_text="По умолчанию для H1 используется Name.", name="h1"
    )
    _html_title = models.CharField(  # Названо с _ чтобы не было путаницы
        "HTML Title",
        max_length=128,
        blank=True,
        help_text="По умолчанию для HTML Title используется Name.",
        name="html_title",
    )
    add_site_name_to_html_title = models.BooleanField("Добавить название сайта к HTML Title?", default=True)
    _html_description = models.TextField("HTML Description", blank=True, name="html_description")
    last_modified_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def get_h1(self) -> str:
        return self._h1 or self.name

    def get_html_title(self) -> str:
        site_name = SiteSettings.get_solo().site_name
        return (self._html_title or self.name) + (f" | {site_name}" if self.add_site_name_to_html_title else "")

    def get_html_description(self) -> str:
        return self._html_description

    def get_image_url(self) -> str | None:
        """
        Если у модели есть изображение - переопределите этот метод
        и возвращайте url ссылку на него.

        По умолчанию пробует взять из `image`.
        """
        FIELD_NAME = "image"
        try:
            field = self._meta.get_field(FIELD_NAME)
        except FieldDoesNotExist:
            return None

        if not isinstance(field, models.ImageField):
            _logger.debug(
                f"У {typename(self)} есть поле {FIELD_NAME}, но оно не является "
                f"{typename(models.ImageField)}, get_image_url возвращает None."
            )
            return None

        return getattr(self, FIELD_NAME).url

    # Переопределение DefaultAltTextMixin
    def get_default_alt_text(self) -> str:
        return self.name

    # Необходимо указать в дочернем классе, но можно оставить по умолчанию
    _OG_TYPE: OgType = OgType.WEBSITE

    # Возможно тоже стоит сделать методами с get
    @property
    def og_type(self):
        return self._OG_TYPE

    @property
    def og_title(self):
        return self.get_html_title()

    @property
    def og_description(self):
        return self.get_html_description()

    @property
    def og_image_url(self):
        return self.get_image_url()

    # Под переопределение
    def _get_parent_object(self) -> Self | None:
        """
        Возвращает объект, считающийся родительским для этого объекта.
        Используется в генерации breadcrumbs.
        """
        return None

    def get_breadcrumbs(self) -> Sequence[Self]:
        """Возвращает "хлебные крошки" для этого объекта, включая сам объект."""
        CACHE_KEY = "_cache_get_breadcrumbs"
        if cache := getattr(self, CACHE_KEY, None):
            return cache

        breadcrumbs: list[Self] = []
        seen: set[tuple[type[models.Model], int]] = set()

        current: Self | None = self
        while current is not None:
            if (item := (type(current), current.pk)) in seen:
                model, pk = item
                raise ValueError(f"Циклическая последовательность parent объектов (model: {typename(model)}, pk: {pk})")

            seen.add(item)
            breadcrumbs.append(current)
            current = current._get_parent_object()

        breadcrumbs.reverse()

        setattr(self, CACHE_KEY, breadcrumbs)
        return breadcrumbs

    def _get_specific_microdata(self) -> dict[str, Any]:
        """Под переопределение, возвращайте здесь нужный словарь с данными"""
        return {}

    def _get_base_microdata(self) -> dict[str, Any]:
        microdata = {
            "@context": "https://schema.org",
            "@type": "CreativeWork",  # Самый общий тип для контента
            "name": self.name,
            "url": self.get_absolute_url(),
            "dateModified": self.last_modified_time.isoformat(),
            "mainEntityOfPage": {"@type": "WebPage", "@id": self.get_absolute_url()},
        }
        if desc := self.get_html_description():
            microdata["description"] = desc
        if img_url := self.get_image_url():
            microdata["image"] = img_url
        return microdata

    def get_microdata_html_block(self) -> str:
        """
        Возвращает HTML структуру с мирокроразметочными элементами.
        """
        from src.apps.page.models import DynamicPage

        microdates: list[dict] = []

        microdates.append({**self._get_base_microdata(), **self._get_specific_microdata()})

        microdates.append(
            {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": i,
                        "name": item.name,
                        **({"item": item.get_absolute_url()} if item != self else {}),
                    }
                    for i, item in enumerate(
                        tuple(DynamicPage.objects.filter(slug="index")) + tuple(self.get_breadcrumbs())
                    )
                ],
            }
        )

        return "".join(
            '<script type="application/ld+json">\n'
            + f"{json.dumps(microdata, indent=4, ensure_ascii=False)}\n"
            + "</script>\n"
            for microdata in microdates
        )

    def get_absolute_url(self) -> str:
        default_url_name = f"{self._meta.model_name}-detail"
        url_name = self._url_path_name or default_url_name

        try:
            return reverse(url_name, kwargs={self._url_kwarg_name: self.slug})
        except NoReverseMatch:
            raise ImproperlyConfigured(
                "Вы не настроили get_absolute_url()! Настройте, либо переопределите базовый метод."
            )

    def get_admin_url(self):
        return f"/admin/{self._meta.app_label}/{self._meta.model_name}/{self.pk}/change/"

    @classmethod
    def get_sitemap_queryset(cls):
        return cls.objects.all()

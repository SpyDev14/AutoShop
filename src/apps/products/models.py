from django.db import models

from src.shared.models.storages import get_upload_path
from src.shared.models.mixins import AnnotatePkMixin
from src.shared.models.bases import UniqueNamedModel, PagedModel
from src.shared.enums.flags import FlagsMixin


class Car(UniqueNamedModel):
    class Meta:  # type: ignore
        verbose_name = "Модель автомобиля"
        verbose_name_plural = "Модели автомобилей"


class Material(UniqueNamedModel):
    image = models.ImageField("Изображение", upload_to=get_upload_path("material/images"))

    class Meta:  # type: ignore
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"


class ProductKind(FlagsMixin, models.IntegerChoices):
    FRONT = (1 << 0, "Перед")
    BACK = (1 << 1, "Зад")
    BOTH = (FRONT[0] | BACK[0], "Оба")


class Product(UniqueNamedModel):
    price = models.DecimalField("Цена", decimal_places=5)

    class Meta:  # type: ignore
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"


class ProductBundle(AnnotatePkMixin, models.Model):
    name = models.CharField("Название", max_length=80)
    car = models.ForeignKey(Car, models.CASCADE, verbose_name="Машина")
    # kind = models.IntegerField("Вид", choices=Kind.choices)
    products = models.ManyToManyField(Product, verbose_name="Продукты в пакете")
    image_for_list = models.ImageField("Изображение для карточки в списке", upload_to=get_upload_path("bundle/images"))
    image_for_main = models.ImageField("Изображение на главной странице", upload_to=get_upload_path("bundle/images"))

    class Meta:
        verbose_name = "Торговое предложение"
        verbose_name_plural = "Торговые предложения"

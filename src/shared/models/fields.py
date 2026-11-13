from django.utils.safestring import mark_safe
from django.core.checks import Error, Info
from django.db.models import CharField, Model

_NOT_RECOMMENDED_FIELD_NAME_MSG_ID = "src.shared.models.fields.W001"


# Это поле пережило несколько серьёзных изменений структуры, раньше здесь было св-во вместо метода,
# строгая форма названия поля (ImageAltTextField), параметр для названия св-ва, куча проверок 💀💀💀
class ImageAltTextField(CharField):
    """
    ## Существует проблема миграций! Смотрите ниже!
    <hr>

    Поле для текста атрибута `alt` в теге `<img>` связанного изображения.
    Динамически добавляет метод `get_{image_field_name}_alt_text(self) -> str` возвращающий
    либо текст указанный в этом поле, либо значение из `default_source_name` (через `getattr()`).
    `default_source_name` также может быть вызываемым объектом без обязательных аргументов.
    <hr>

    ## Параметры
    - **`image_field_name: str`**<br>
        Название поля с изображением, к которому будет привязан alt text, **обязательный параметр**,
        должно действительно существовать у модели. Также используется для генерации `verbose_name`
        и `help_text` по умолчанию.
    - **`default_source_name: str | None`** (по умолчанию `None`)<br>
        Название поля или метода без обязательных аргументов, из которого следует брать значение по
        умолчанию. Можно не указывать, Должно действительно существовать у модели.
        <br>Если не было задано - этот Field будет работать *почти* как обычный `CharField`
        с предустановленными параметрами (всегда добавляет метод). Также влияет на `help_text`
        по умолчанию (даже если не задано).
        <br>Сделано необязательным специально, чтобы вы **всегда** использовали это поле, когда вам
        нужен alt text для изображения, для которого не от куда брать значение по умолчанию
        (для консистентности в проекте).

    ## Проблема миграций
    Из-за того, что при переименовании поля с изображением, при работе с этим полем, вам
    нужно изменить строку с названием той переменной, а также (рекомендуется) и название
    самого поля (`photo_alt_text` -> `image_alt_text`), `makemigrations` такое изменение
    расценят не как переименование, а как удаление + добавление нового поля.<br>
    **Как же тогда мигрировать при переименовании поля с картинкой?** Нужно мигрировать в 2
    этапа:
    1. Переименуйте поле с изображением, обновите строковое значение `image_field_name`,
    выполните `makemigrations`. Подтвердите, что действительно переименовали поле с изображением.
    2. Переименуйте поле с alt text под новое название поля с изображением (например,
    `photo_alt_text` -> `image_alt_text`).

    ## Примеры
    ### Модели
    - **Неправильные примеры**
    ```
    class WrongModel(Model):
        image = ImageField()
        # Ошибка: myimage не существует
        image_alt_text = ImageAltTextField('myimage')

    class WrongModel2(Model):
        image = ImageField()
        # Ошибка: default_source_name 'some_name' не существует
        image_alt_text = ImageAltTextField('image', 'some_name')
    ```

    - **Правильные примеры**
    ```
    class RightModel(Model):
        image = ImageField()
        # Без default_source_name - поле работает почти как обычный CharField
        image_alt_text = ImageAltTextField('image')

    class RightModelWithDefault(Model):
        name = CharField()
        image = ImageField()
        # С default_source_name - поле берёт значение по умолчанию из 'name'
        image_alt_text = ImageAltTextField('image', 'name')
        # Аннотация для IDE (опционально)
        get_image_alt_text: Callable[[], str]

    class RightModelWithProperty(Model):
        title = CharField()
        image = ImageField()

        @property
        def alt_source(self):
            return f"Alt for {self.title}"

        # default_source_name может быть property
        image_alt_text = ImageAltTextField('image', 'alt_source')

    class RightModelWithMethod(Model):
        image = ImageField()

        def generate_alt(self):
            return "Generated alt text"

        # default_source_name может быть методом без аргументов
        image_alt_text = ImageAltTextField('image', 'generate_alt')

    class RightModelComplex(Model):
        main_image = ImageField()
        title = CharField()

        def get_default_alt(self):
            return f"{self.title} - main image"

        # Название поля может быть произвольным, но всё же рекомендуется стандартный формат
        # (<image_field_name>_alt_text)
        skibidi_slon = ImageAltTextField('main_image', 'get_default_alt')
        # Аннотация для IDE
        get_main_image_alt_text: Callable[[], str]
    ```
    ### В Python коде
    ```
    item = RightModelWithDefault(
        name="Продукт XYZ",
        image="product.jpg"
    )
    # Получение alt текста через динамический метод
    print(item.get_image_alt_text()) # -> "Продукт XYZ"

    item.image_alt_text = "Альтернативный текст вручную"

    # Получение alt текста через динамический метод
    print(item.get_image_alt_text())
    # Если задано image_alt_text: "Альтернативный текст вручную"
    # Если не задано: "Продукт XYZ" (из поля name)

    # Модель без default
    item2 = RightModel(
        image="product.jpg"
    )
    print(item2.get_image_alt_text()) # -> ""

    item2.image_alt_text = "Alt text"
    print(item2.get_image_alt_text()) # -> "Alt text"
    ```
    ### В Django HTML темплейтах
    ```
    <img src="{{ item.image.url }}" alt="{{ item.get_image_alt_text }}">
    ```
    """

    DEFAULT_MAX_LENGTH = 255

    def __init__(self, image_field_name: str, default_source_name: str | None = None, **kwargs):
        self.image_field_name = image_field_name
        self.default_source_name = default_source_name

        # Должно быть убрано в deconstruct()!!! Иначе миграции будут сломаны!
        # (стандартное django поведение)
        kwargs.setdefault("max_length", self.DEFAULT_MAX_LENGTH)
        kwargs.setdefault("blank", True)
        kwargs.setdefault("verbose_name", self.get_default_verbose_name())
        kwargs.setdefault("help_text", mark_safe(self.get_default_help_text()))

        # Будет задано в _save_contribute_info_in_self_attrs()
        self._this_field_name: str | None = None
        self._owner_class: type[Model] | None = None

        super().__init__(**kwargs)

    def _get_this_field_recommended_name(self):
        return f"{self.image_field_name}_alt_text"

    def _get_method_name(self):
        return f"get_{self.image_field_name}_alt_text"

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs: dict

        kwargs["image_field_name"] = self.image_field_name

        if self.default_source_name is not None:
            kwargs["default_source_name"] = self.default_source_name

        if kwargs.get("max_length") == self.DEFAULT_MAX_LENGTH:
            del kwargs["max_length"]
        if kwargs.get("blank") is True:
            del kwargs["blank"]
        if kwargs["verbose_name"] == self.get_default_verbose_name():
            del kwargs["verbose_name"]
        if kwargs["help_text"] == self.get_default_help_text():
            del kwargs["help_text"]

        return name, path, args, kwargs

    def get_default_verbose_name(self):
        return f"Alt текст для {self.image_field_name}"

    def get_default_help_text(self):
        return "Будет подставлено в атрибут alt тега &lt;img&gt;, если задано.<br>" + (
            f'По умолчанию используется значение из поля (или метода) <code>"{self.default_source_name}"</code>.'
            if self.default_source_name
            else "Значения по умолчанию либо не предусмотрено, либо оно "
            "подставляется напрямую в разметке, смотрите в итоговом HTML документе."
        )

    def check(self, **kwargs):
        # check() будет вызвано после contribute_to_class()
        # assert для явности + аннотация (Any | None => Any)
        assert self._this_field_name is not None
        assert self._owner_class is not None

        messages = super().check(**kwargs)
        owner_class_name = self._owner_class.__name__

        # image_field_name существует
        if not (image_field_exsists := hasattr(self._owner_class, self.image_field_name)):
            messages.append(
                Error(
                    f'Указанного поля с изображением "{self.image_field_name}" для {self._this_field_name} '
                    f"({type(self).__name__}) не существует (в модели {owner_class_name}).",
                    obj=self,
                )
            )

        # Название соответствует формату (но только если правильно указано)
        if image_field_exsists and (self._this_field_name != self._get_this_field_recommended_name()):
            messages.append(
                Info(
                    f'Вы используете не рекомендуемое имя поля. Вместо "{self._this_field_name}" рассмотрите '
                    f'использование "{self._get_this_field_recommended_name()}" для консистентности в проекте.',
                    obj=self,
                    id=_NOT_RECOMMENDED_FIELD_NAME_MSG_ID,
                )
            )

        if self.default_source_name:
            # default_source_name существует
            if not hasattr(self._owner_class, self.default_source_name):
                messages.append(
                    Error(
                        f'Атрибута с названием "{self.default_source_name}" (default_source_name) не '
                        f'существует в "{owner_class_name}"',
                        obj=self,
                    )
                )

        return messages

    def _save_contribute_info_in_self_attrs(self, this_field_name: str, owner_class: type):
        self._this_field_name = this_field_name
        self._owner_class = owner_class

    # Гарантированно вызывается ДО check()
    def contribute_to_class(self, cls: type[Model], name: str, private_only=False, **kwargs):
        self._save_contribute_info_in_self_attrs(name, cls)
        super().contribute_to_class(cls, name, private_only, **kwargs)

        def _get_alt_text(instance: object):
            value: str = getattr(instance, name)
            if value:
                return value

            default_value = getattr(instance, self.default_source_name) if self.default_source_name else ""

            if callable(default_value):
                default_value = default_value()

            # default_value может не быть строкой, но может быть None
            return str(default_value) if default_value is not None else ""

        # _get_alt_text станет методом класса получающим self
        # (так python работает)
        setattr(cls, self._get_method_name(), _get_alt_text)

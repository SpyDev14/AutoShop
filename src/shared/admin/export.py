from collections.abc import Set
from datetime import date
from typing import Iterable, Mapping, Protocol, Sequence, Callable, Any
from io import BytesIO

from django.contrib.admin import action
from django.db.models import QuerySet, Model
from django.utils import timezone
from django.http import FileResponse

from openpyxl.worksheet.worksheet import Worksheet
from phonenumbers import format_number, PhoneNumberFormat, PhoneNumber
from pandas import DataFrame, ExcelWriter

'''
class Formatter(Protocol):
    def __call__(self, value: Any, /) -> Any: ...

class TypeFormatter:
    def __init__(self, target_types: Iterable[type], formatter: Formatter):
        self.target_types: Set[type] = set(target_types)
        self._formatter = formatter

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self._formatter(*args, **kwds)

class ExcelExporter:
    def __init__(
        self,
        *,
        exported_sheet_name: str = "Данные",
        cells_to_calc_max_width: slice = slice(0, 20), # только первые 20; slice read-only
        max_cell_width: int = 60,
        type_formatters: Iterable[TypeFormatter] = (),
        # словарь в параметрах по умолчанию не проблема, так как он под иммутабельной аннотацией
        field_formatters: Mapping[str, Formatter] = {},
        verbose_name_overrides: Mapping[str, str] = {},
        dates_format: str = "%d.%m.%Y %H:%M"
    ) -> None:
        """
        Params:
            verbose_name_overrides: Название поля -> имя
        """
        pass
'''


# TODO: Переписать через класс
# (Дальше бога нет)
def _export_to_excel(
    queryset: QuerySet,
    filename: str,
    *,
    sheet_name: str | None = "Данные",
    max_cells_check: int = 20,
    max_cells_width: int = 64,
    fields: Sequence[str] | None = None,
    verbose_names: Sequence[str | None] | None = None,
    date_format: str = "%d.%m.%Y %H:%M",
    formatters: dict[str, Callable[[Any], Any]] | None = None,
) -> FileResponse:
    """
    Экспорт QuerySet в Excel. Возвращает HTTP FileResponse с файлом для скачивания.
    Не будет экспортировать поля один ко многим.

    Params:
        queryset: QuerySet для экспорта.
        filename: Имя файла для экспорта.
        sheet_name: Название листа в Excel.
        max_cells_check:
            Максимальное количество первых клеток для подсчёта
            ширины столбца, минимум 1.
        max_cells_width:
            Максимальная ширина ячейки.
        fields: Список полей модели (если None — все поля).
        verbose_names:
            Читаемые названия колонок (соответствуют fields).
            Если не задано - будут использованы verbose_names из данных модели.
            При указании None в качестве эелемента - для поля по этому индексу
            будет выбрано значение по умолчанию.
            Здесь можно было использовать dict, но я до этого догадался уже когда всё сделал.
        date_format: Формат дат (по умолчанию 'дд.мм.гггг чч:мм').
        formatters: Словарь {поле: функция_форматирования(значение поля) ->
            форматированое значение поля (предпочтительно строка)}.

    Returns:
        HttpResponse с файлом Excel.

    Raises:
        ValueError:
            - max_cells_check < 1
            - fields содержит несуществующие поля.
            - Длина fields & verbose_names (если последние указанны) не совпадают.
    """
    # MARK: ВАЛИДАЦИЯ
    if max_cells_check < 1:
        raise ValueError("Max cells check cannot be less 1")

    if verbose_names and len(verbose_names) != len(fields):
        raise ValueError("verbose_names length must match fields")

    # MARK: ИНИЦИАЛИЗАЦИЯ
    model_class: Model = queryset.model  # для аннотации
    model_meta = model_class._meta
    del model_class

    if fields is not None:
        for field_name in fields:
            if not model_meta.get_field(field_name):
                raise ValueError(f"Field {field_name} does not exist")

    # Поля для экспорта
    else:
        fields = tuple(field.name for field in model_meta.fields)

    # Кастомные форматтировщики
    formatters = formatters or {}

    # Названия колонок
    if verbose_names is None:
        verbose_names = [model_meta.get_field(field_name).verbose_name for field_name in fields]
    else:
        for i, (field_name, verbose_name) in enumerate(zip(fields, verbose_names)):
            if verbose_name is None:
                verbose_names[i] = model_meta.get_field(field_name).verbose_name

    # MARK: ФОРМИРОВАНИЕ ДАННЫХ
    data: list[dict[str, Any]] = []
    for instance in queryset:
        row: dict[str, Any] = {}

        for field_name, verbose_name in zip(fields, verbose_names):
            value = getattr(instance, field_name)

            # Раньше обработка была сложнее, но я упростил
            if field_name in formatters:
                value = formatters[field_name](value)
            elif isinstance(value, date):
                value = value.strftime(date_format)
            elif isinstance(value, bool):
                value = "Да" if value else "Нет"
            elif isinstance(value, Model):
                value = str(value)
            elif isinstance(value, PhoneNumber):
                value = format_number(value, PhoneNumberFormat.INTERNATIONAL)

            # Может не пройти никакой обработки
            row[verbose_name] = value or ""

        data.append(row)

    # MARK: ГЕНЕРАЦИЯ ФАЙЛА
    data_frame = DataFrame(data)
    buffer = BytesIO()  # В памяти
    # Также можно сразу писать в HttpResponse, но так удобне

    with ExcelWriter(buffer, engine="openpyxl") as writer:
        data_frame.to_excel(writer, index=False, sheet_name=sheet_name)

        worksheet: Worksheet = writer.sheets[sheet_name]

        for column in worksheet.columns:
            # column_letter - колонка в Excel: A, B, C, D...
            column_letter = column[0].column_letter

            max_cell_width = max(len(str(cell.value)) if cell.value else 0 for cell in column[:max_cells_check])

            # К сожалению, по умолчанию стиль расположения текста в
            # ячейках - слева снизу, и исправить это можно только перебором
            # ВСЕХ ячеек в таблице, что будет очень неэффективно, поэтому
            # придётся проигнорировать страшный вид :^(
            # PS: Но это касательно
            worksheet.column_dimensions[column_letter].width = min(
                max_cell_width + 2,  # (С запасом)
                max_cells_width,  # Из параметров
            )

    # Подготавливаем буффер для чтения: устанавливаем курсор в начало
    buffer.seek(0)

    return FileResponse(
        buffer,
        filename=f"{filename}.xlsx",
        as_attachment=True,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def make_export_to_excel_action(
    name: str, *, add_date_to_name: bool = False, filename_date_format: str = "%d.%m.%Y", **kwargs
):
    """Возвращает admin-action функцию, экспортирующую
    и отправляющую обратно записи в excel формате.

    Params:
        name:
            Название выходного файла.
        add_date_to_name:
            Добавить ли текущую дату к названию файла (вынесено сюда
            из-за частой необходимости)
        filename_date_format:
            Используется вместе с `add_date_to_name`, формат `strftime`.
            **НЕ ИСПОЛЬЗУЙТЕ** символы, недопустимые для имени файла.
        kwargs:
            Будет передано в развёрнутом виде в функцию `export_to_excel`,
            подробнее смотрите там.
    """
    if add_date_to_name:
        name = f"{name} {timezone.now().strftime(filename_date_format)}"

    @action(description="Экспортировать в Excel")
    def admin_action(modeladmin, request, queryset: QuerySet):
        return _export_to_excel(queryset, name, **kwargs)

    return admin_action

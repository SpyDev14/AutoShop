from django.utils.safestring import mark_safe
from src.apps.page.constants import GENERIC_TEMPLATE


RENDERING_SUPPORTS_TEXT = mark_safe(
    "Поддерживается django template рендеринг!"
    '<details style="width: 70%; padding-left: 1rem;">'
    '<summary style="margin-left: -1rem;">Подробнее</summary>'
    """
        Если активирован рендеринг, текст из этого поля будет обработан через django template рендеринг.<br>
        Это означает, что вы можете использовать здесь темплейт инструменты, такие как:
        <li>Теги <code>{% if %}</code>, <code>{% for %}</code> и другие.</li>
        <li>
            Переменные, например: <code>{{ page.extra_context }},
            {{ global.pages.index }}, {{ global.extra_context }}</code> и т.д.
        </li>
        <li>
            А также теги обработки, например: <code>...|default:"..."</code>,
             <code>...|truncatechars:40</code> и многие другие.
        </li>
        Контекст будет такой же, как и на странице, на которой будет выводится этот текст.<br>

        Важно: функционал рендеринга реализуется в каждом темплейте отдельно, через специальный template-тег.
        Это означает, что <b>нет гарантии</b>, что фронтендер добавил эту обработу <i>там</i>.
        Согласуйте это вместе с фронтендером.<br>"""
    f"Если же вы используете стандартный темплейт <code>{GENERIC_TEMPLATE.PAGE}</code>, "
    "то рендеринг гарантирован."
    "</details>"
)

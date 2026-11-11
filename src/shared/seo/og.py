from enum import StrEnum


class OgType(StrEnum):  #  Предназначения:
    ARTICLE = "article"  # - Статьи, блог-посты, новости
    PRODUCT = "product"  # - Товары в интернет-магазине
    PROFILE = "profile"  # - Профили пользователей
    WEBSITE = "website"  # - Главная страница, лендинги
    PLACE = "place"  #     - Места, локации
    BOOK = "book"  #       - Книги, литературные произведения

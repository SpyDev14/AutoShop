def typename(obj: object | type) -> str:
    if isinstance(obj, type):
        return obj.__name__
    return type(obj).__name__


def get_subclasses[T: type](cls: T) -> set[T]:
    """Рекурсивно возвращает все подклассы переданного класса"""
    subclasses: set[T] = set(cls.__subclasses__())

    for subclass in cls.__subclasses__():
        subclasses.update(get_subclasses(subclass))

    return subclasses

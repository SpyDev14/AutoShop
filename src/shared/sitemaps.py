from django.contrib.sitemaps import GenericSitemap

from src.shared.models.bases import PagedModel
from src.shared.reflection import get_subclasses


# Если какая-то запись будет не нужна в Sitemap - её исключат в
# robots.txt через disallow
def get_sitemaps_for_paged_models() -> dict[str, GenericSitemap[PagedModel]]:
    def proc_name[T](value: T | None) -> T:
        if value is None:
            raise ValueError("model._meta.model_name is None")
        return value

    return {
        proc_name(model._meta.model_name): GenericSitemap(
            {"queryset": model.objects.order_by("-last_modified_time"), "date_field": "last_modified_time"}
        )
        for model in get_subclasses(PagedModel)
        if not model._meta.abstract
    }

from pathlib import Path
import sys, logging

from django.conf import settings
from django.apps import AppConfig, apps

from src.shared.reflection import typename


_logger = logging.getLogger(__name__)


def get_upload_path(local_name: str | Path, module_or_app_cfg: str | type[AppConfig] | None = None) -> str:
    local_name = Path(local_name)
    app: AppConfig | None = apps.get_app_config(module_or_app_cfg.name) if isinstance(module_or_app_cfg, type) else None

    if app is None:
        module: str
        if isinstance(module_or_app_cfg, str):
            module = module_or_app_cfg
        else:
            f_back = sys._getframe().f_back
            assert f_back is not None
            module = f_back.f_globals["__name__"]
            assert module is not None
            _logger.debug(f"Get module by sys._getframe: {module}")

        app = apps.get_containing_app_config(module)

        if app is None:
            raise RuntimeError(f"Module {module} not in any app.")

    media_dir = settings.MEDIA_ROOT
    if not isinstance(media_dir, Path):
        raise TypeError(f"MEDIA_DIR should be a Path, got: {typename(media_dir)}")

    return str(media_dir / app.name / local_name)

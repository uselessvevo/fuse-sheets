import inspect
import importlib
import importlib.util

from os import sep
from pathlib import Path
from typing import Tuple
from logging import getLogger


logger = getLogger(__name__)


def register_fuse_views_routes(
    app: "aiohttp.web.Application",
    prefix: str,
    pkg_path: str,
    object_type,
    exclude_modules: Tuple[str] = None
) -> None:
    """
    Collect and register all needed `FuseViews`
    """
    exclude_modules = exclude_modules or ()
    current_path = Path(pkg_path).resolve()
    modules = tuple(
        i for i in current_path.glob('*.py')
        if '__init__.py' not in i.name if i.name not in exclude_modules
    )

    for obj_module in modules:
        specs = importlib.util.spec_from_file_location(
            name=f'{pkg_path.replace(sep, ".")}.{obj_module.stem}',
            location=obj_module.as_posix()
        )
        module = importlib.util.module_from_spec(specs)
        specs.loader.exec_module(module)

        for name, fuse_view in inspect.getmembers(module):
            if (
                inspect.isclass(fuse_view)
                and issubclass(fuse_view, (object_type,))
                and fuse_view not in (object_type,)
            ):
                url = f'{prefix}v{fuse_view.version}/{fuse_view.urlpattern}'
                app.router.add_view(url, fuse_view)

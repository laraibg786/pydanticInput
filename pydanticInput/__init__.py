from importlib.metadata import PackageNotFoundError, version

from pydanticInput.dispatch import type_dispatch
from pydanticInput.main import Input


try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = "0.0.0"

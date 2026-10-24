__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

from importlib.metadata import PackageNotFoundError, version


__all__ = ["account", "anime", "manga", "seasons"]


try:
    __version__ = version("pymal-ng")
except PackageNotFoundError:  # running from a source tree that isn't installed
    __version__ = "unknown"

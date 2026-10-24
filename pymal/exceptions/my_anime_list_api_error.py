__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

__all__ = [
    "MyAnimeListApiError",
    "MyAnimeListApiUpdateError",
    "MyAnimeListApiDeleteError",
    "MyAnimeListApiAddError",
]


class MyAnimeListApiError(RuntimeError):
    """MyAnimeList's API answered with an error; ``status_code`` is the HTTP status."""

    def __init__(self, message: str = "", status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class MyAnimeListApiUpdateError(MyAnimeListApiError):
    pass


class MyAnimeListApiDeleteError(MyAnimeListApiError):
    pass


class MyAnimeListApiAddError(MyAnimeListApiError):
    pass

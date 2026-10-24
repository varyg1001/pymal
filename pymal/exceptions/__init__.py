__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

from pymal.exceptions.failed_to_parse_error import *  # noqa: F401, F403, E402
from pymal.exceptions.my_anime_list_api_error import *  # noqa: F401, F403, E402


__all__ = [
    "UnauthenticatedAccountError",
    "NotASeasonError",
    "GotRobotError",
    "SiteUnavailableError",
]


class UnauthenticatedAccountError(ValueError):
    pass


class NotASeasonError(ValueError):
    def __init__(self, tried_season_name):
        super().__init__(
            f"The wanted season '{tried_season_name:s}' is not: 'Winter', 'Spring', 'Summer' or 'Fall'."
        )


class GotRobotError(RuntimeError):
    pass


class SiteUnavailableError(RuntimeError):
    """MyAnimeList could not be reached, timed out, or kept answering with a server error."""

    def __init__(self, url: str, reason: str):
        super().__init__(f"MyAnimeList is unavailable ({reason}): {url}")
        self.url = url
        self.reason = reason

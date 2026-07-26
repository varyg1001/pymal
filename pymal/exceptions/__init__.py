__authors__ = ""
__copyright__ = "(c) 2014, pymal"
__license__ = "BSD License"
__contact__ = "Name Of Current Guardian of this file <email@address>"

from pymal.exceptions.failed_to_parse_error import *  # noqa: F401, F403, E402
from pymal.exceptions.my_anime_list_api_error import *  # noqa: F401, F403, E402


__all__ = [
    "UnauthenticatedAccountError",
    "NotASeasonError",
    "GotRobotError",
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

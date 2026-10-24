import os
from pathlib import Path

from pymal import account, mal_api


# The live account tests (tests/account_objects) need API access to a real account:
#   MAL_USERNAME      the account name
#   MAL_CLIENT_ID     the client id of your API app (https://myanimelist.net/apiconfig)
#   MAL_ACCESS_TOKEN  an OAuth access token (optional if you ran Account.authorize()
#                     before: the saved token file is used then)
#   MAL_SESSIONID     instead of the API: the MALSESSIONID cookie of a logged in browser, or
#                     the path of a cookies.txt export of it.
#                     Experimental, only status/score/progress work.
#   MAL_USER_AGENT    the User-Agent of that browser, if MAL needs it
#   MAL_REFRESH_TOKEN, MAL_CLIENT_SECRET   optional
#   MAL_TEST_WRITE=1  also run the tests that add/change/delete entries of that account
# Without them, all account_objects tests are automatically skipped.
ACCOUNT_TEST_USERNAME = os.environ.get("MAL_USERNAME")
ACCOUNT_TEST_CLIENT_ID = os.environ.get("MAL_CLIENT_ID")
ACCOUNT_TEST_ACCESS_TOKEN = os.environ.get("MAL_ACCESS_TOKEN")
ACCOUNT_TEST_WRITE = os.environ.get("MAL_TEST_WRITE") == "1"

ANIME_ID = 1887
MANGA_ID = 587

ADD_ANIME_ID = 20707
ADD_MANGA_ID = 11

SOURCES_DIRECTORY = Path(__file__).parent / "sources"


def has_account_credentials() -> bool:
    if not ACCOUNT_TEST_USERNAME:
        return False
    if os.environ.get("MAL_SESSIONID") or (
        ACCOUNT_TEST_CLIENT_ID and ACCOUNT_TEST_ACCESS_TOKEN
    ):
        return True
    return mal_api.default_token_file(ACCOUNT_TEST_USERNAME).exists()


def make_account() -> account.Account:
    acc = account.Account(ACCOUNT_TEST_USERNAME)
    if ACCOUNT_TEST_CLIENT_ID and ACCOUNT_TEST_ACCESS_TOKEN:
        acc.login(
            ACCOUNT_TEST_CLIENT_ID,
            ACCOUNT_TEST_ACCESS_TOKEN,
            os.environ.get("MAL_REFRESH_TOKEN", ""),
            os.environ.get("MAL_CLIENT_SECRET", ""),
        )
    if os.environ.get("MAL_SESSIONID") and not ACCOUNT_TEST_CLIENT_ID:
        acc.login_with_cookie(
            os.environ["MAL_SESSIONID"], user_agent=os.environ.get("MAL_USER_AGENT", "")
        )
    return acc

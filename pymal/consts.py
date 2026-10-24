__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

USER_AGENT = "api-indiv-0829BA2B33942A4A5E6338FE05EFB8A1"
# For the website session (Account.login_with_cookie): a session made in a browser
# is used with a browser-like agent unless you pass the exact one of that browser.
BROWSER_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/155.0.0.0 Safari/537.36"
)

HOST_NAME = "https://myanimelist.net"

DEBUG = False
RETRY_NUMBER = 4
RETRY_SLEEP = 1
REQUEST_TIMEOUT = 15
UNAVAILABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})

SHORT_SITE_FORMAT_TIME = "%b %Y"
LONG_SITE_FORMAT_TIME = "%b %d, %Y"
MALAPPINFO_FORMAT_TIME = "%Y-%m-%d"
MALAPPINFO_NONE_TIME = "0000-00-00"
MALAPI_FORMAT_TIME = "%Y%m%d"
MALAPI_NONE_TIME = "00000000"

# Testing

## Running the tests

The suites in `tests/` (`test_fixes.py`, `test_connection.py`, `test_api.py`) are fully
offline — no MAL connection required. The live account tests in `tests/account_objects/`
are skipped automatically unless API access to a real account is configured:

| Variable | |
|----------|---|
| `MAL_USERNAME` | the account name |
| `MAL_CLIENT_ID` | client ID of your API app ([apiconfig](https://myanimelist.net/apiconfig)) |
| `MAL_ACCESS_TOKEN` | an OAuth access token — optional if you ran `Account.authorize()` before (the saved token file is used) |
| `MAL_SESSIONID` | the `MALSESSIONID` cookie, instead of the API variables (experimental; only status, score and progress are tested) |
| `MAL_TEST_WRITE=1` | also run the tests that add, change and delete entries (`ADD_ANIME_ID` / `ADD_MANGA_ID` in `tests/constants_for_testing.py` must not be in the list) |

```bash
# Run all tests
uv run pytest

# Verbose output
uv run pytest -v

# Specific file
uv run pytest tests/test_fixes.py -v
```

## Structure

```
tests/
├── test_fixes.py              # Parsing, guards, imports, object behaviour
├── test_connection.py         # Retries and "site unavailable" handling, helpers
├── test_api.py                # OAuth, API client, account lists, MyAnime/MyManga (mocked API)
├── constants_for_testing.py   # Shared test constants and live-test credentials
└── account_objects/           # Live account tests (skipped without credentials)
    ├── test_live_account.py
    └── test_account_friends.py
```

## Guidelines

**New tests should be offline** (except the ones in `account_objects/`). Use `unittest.mock.patch` and inline HTML fixtures
instead of real HTTP calls or saved HTML snapshots.

```python
from unittest.mock import patch, MagicMock

def make_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    return mock

with patch("pymal.global_functions.session") as mock_session:
    mock_session.get.return_value = make_response("<html>...</html>")
    anime.reload()
```

**Keep assertions informative** — use the `msg=` parameter or structure your
assertions so failures clearly identify what broke.

**Shared constants** go in `tests/constants_for_testing.py`.
Test-local constants go inside the `TestCase` class.

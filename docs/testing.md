# Testing

## Running the tests

The test suite is fully offline — no MAL connection required.

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
├── test_fixes.py              # Main offline suite (40 tests)
│                              # covers parsing, guards, imports, object behaviour
├── constants_for_testing.py   # Shared test constants
└── account_objects/           # Account-level test cases
    ├── test_account_animes.py
    ├── test_account_mangas.py
    ├── test_my_anime.py
    └── test_my_manga.py
```

## Guidelines

**All tests must be offline.** Use `unittest.mock.patch` and inline HTML fixtures
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

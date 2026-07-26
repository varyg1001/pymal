# Changelog

## 1.0.0 — 2026-07

### Breaking changes
- Dropped Python 2 support entirely (was already broken)
- Removed `six` dependency
- Removed `html5lib` dependency

### Fixes
- **HTML parser**: switched from `html5lib` to `lxml` — resolves dependency conflicts and speeds up parsing
- **HTTP client**: replaced `requests` with `niquests` (drop-in replacement with modern TLS/HTTP2 support)
- **Sidebar parsing** (`anime.py`): rewrote from brittle index-based access to label-based lookup via `span.dark_text` — fixes all fields broken by MAL's layout update
- **Title extraction** (`anime.py`): fixed `IndexError` caused by MAL wrapping the title in a `<strong>` tag inside `<h1>`
- **Table parsing** (`anime.py`): fixed `AttributeError` caused by MAL removing `<tbody>` from tables
- **Search provider** (`searches/search_provider.py`): added `None` guard on `#content` div — fixes `AttributeError` when MAL redirects unauthenticated requests
- **`ReloadedSet`**: fixed `collections.Set` → `collections.abc.Set` (removed in Python 3.10)
- **`HOST_NAME`**: updated `http://` → `https://` (MAL enforces HTTPS)

### Infrastructure
- Migrated build system from `setup.py` to `uv_build` (`pyproject.toml`)
- Replaced `nosetests` with `pytest`
- Added offline test suite (`tests/test_fixes.py`, 40 tests)
- Docs migrated from Sphinx/RST to MkDocs Material
- Deleted obsolete files: `upload_new_version.bat`, `.travis.yml`, `MANIFEST.in`, legacy HTML fixtures

---

## 0.5b4 — 2014

Initial public release.

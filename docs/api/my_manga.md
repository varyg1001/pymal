# MyManga

```python
from pymal.account_objects.my_manga import MyManga
```

Extends [`Manga`](manga.md) with per-account tracking data.
You get a `MyManga` back when you call `manga.add(account)` or
when iterating `account.mangas`.

## Additional attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `my_id` | `int` | Entry ID in your list |
| `my_status` | `int` | Read status (1=Reading, 2=Completed, 3=On-Hold, 4=Dropped, 6=Plan to Read) |
| `my_score` | `int` | Your score (0–10) |
| `my_read_chapters` | `int` | Chapters read |
| `my_read_volumes` | `int` | Volumes read |
| `my_is_rereading` | `bool` | Whether you're rereading |
| `my_tags` | `frozenset` | Your tags |
| `my_comments` | `str` | Your comments |
| `my_priority` | `int` | Priority |
| `my_start_date` | `str` | Your read start date |
| `my_end_date` | `str` | Your read finish date |
| `my_times_reread` | `int` | Times reread |
| `my_reread_value` | `int` | Reread value |
| `my_retail_volumes` | `int` | Physical volumes owned |

## Methods

### `my_reload()`
Fetch personal tracking data from MAL.

### `update()`
Push local changes back to MAL.

### `delete()`
Remove this entry from your list.

### `to_xml() -> str`
Serialize entry to MAL API XML format.

## Example

```python
from pymal.account import Account

account = Account("your-username", "your-password")
entry = list(account.mangas)[0]

entry.my_reload()
print(entry.title)             # inherited from Manga
print(entry.my_read_chapters)
print(entry.my_score)

entry.my_score = 9
entry.update()
```

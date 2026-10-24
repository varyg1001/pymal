# Account

```python
from pymal.account import Account
```

## Logging in

MyAnimeList's website login has a captcha, so pymal can't log in with a password.
There are two ways to act as your account; pick one:

| | Official API (OAuth) | Browser cookies (experimental) |
|---|---|---|
| Setup | An API app, once | A cookie export of your browser |
| Lasts | Tokens refresh themselves | Until the session expires |
| Works | Everything below | Status, score and progress only |
| Verified | Written from MAL's API documentation and tested against mocked answers | Run against a real account (read, add, edit, delete) |

If both are set, the API is used.

### The official API

pymal uses MAL's [API v2](https://myanimelist.net/apimain) here.

**1. Create an API app (once).** Open <https://myanimelist.net/apiconfig> and create an app:

| Field | What to enter |
|---|---|
| App Type | **other** gives a client ID only (simplest). **web** also gives a client secret; pass it as `client_secret=`. |
| App Description | 50–500 characters, no special characters |
| App Redirect URL | `http://localhost/callback` (nothing has to listen there) |
| Commercial / Non-Commercial | non-commercial, for personal use |
| Homepage URL, logo, policy URLs | optional |

Creating an app means accepting MAL's [API License and Developer Agreement](https://myanimelist.net/apiconfig),
so read it first. It applies only to people who register an app (the OAuth route); reading titles,
searching, seasons and public lists, and the cookie route, don't involve it. The app gives you a **client ID** (and a secret for the *web* type); keep them private,
and don't share one client ID between people.

**2. Log in (once).**

```python
account = Account("your-username")
account.authorize("your-client-id")            # add client_secret="…" for a web app
```

`authorize` shows a link (and opens it). MAL always asks you to log in on that page: log in
as the account you named, allow the app, and your browser is sent to the redirect URL
(it shows "can't connect"; that is expected). Copy the whole address from the address bar and paste
it into the terminal. pymal checks that you logged in as the account you named, and refuses
(saving nothing) if it was somebody else.

The tokens are saved to `~/.config/pymal/<username>.json` (readable only by you, or
`$XDG_CONFIG_HOME/pymal/`; change it with `Account(name, token_file=…)`). They are loaded
automatically next time and refreshed when they expire, so you only do this once.
If a refresh is refused (`MyAnimeListApiError`, for example the app was deleted or the refresh token was revoked), log in again with `authorize`.

**Other ways to provide tokens**
- Already have tokens: `account.login(client_id, access_token, refresh_token, save=True)`.
- A server or other machine with no browser: run `authorize` on your own machine and copy the token
  file to the same path on the server (`authorize` needs a terminal to paste into).
- Only a client ID, no login: `account.login(client_id)` reads public data of any account.

Without any login, the **public** anime/manga list of any account can still be read (as bare
entries), but changing a list or reading your private data needs one of the two routes.

**Security.** The token file lets anyone who has it edit your list. Don't commit or share it. To
cut off access, delete the file and delete the app on the apiconfig page.

### Experimental: without the API, with a browser cookie

If you can't or won't create an API app, log in to MyAnimeList in your **browser**
(you solve the captcha there) and give pymal the login cookies of that browser.

```python
account = Account("your-username")
account.login_with_cookie("/path/to/cookies.txt", save=True)   # save=True keeps it in the token file
```

What to pass as the first argument:
- the **path of a cookie export** of your browser (`cookies.txt`, Netscape format, made by an
  extension such as "Get cookies.txt"). Only the login cookies of myanimelist.net are read from it;
- or just the value of the `MALSESSIONID` cookie (developer tools → Application/Storage → Cookies);
- or a dict of cookies, or the whole `Cookie` header string of a request your browser sends to
  myanimelist.net (Network tab → any request → Request Headers → `Cookie`).

MAL only treats a request as logged in if the `is_logged_in=1` flag cookie is sent as well; pymal
adds it automatically. If MAL still doesn't see you as logged in, pass your browser's exact
`User-Agent` with `user_agent="Mozilla/5.0 …"` (a recent Chrome one is the default).

This reads your lists, including a private one, and can add, change and delete entries, but
**only the status, score and progress** (episodes, or chapters and volumes) work; tags, comments,
dates, priority and rewatch/reread values need the API. Every change is read back from your list,
and pymal raises an error if it didn't happen.

The session expires: when pymal says MAL refused the session, log in in the browser again and pass
the new cookies. This route uses MAL's website endpoints, which are not documented, can change
without notice, and fall under MAL's website Terms of Use rather than the API agreement. If a
client ID is set as well, the API is used. Treat the cookies like a password: anyone who has them
is logged in as you.

### Troubleshooting

| Message | Meaning |
|---|---|
| `You logged in as 'x', not 'y'` | The browser logged in as another account. Log in as the named one on MAL's page. |
| `The state doesn't match` | The pasted address is from another attempt. Run `authorize` again and paste the new one. |
| `MAL refused the token request (HTTP 4xx)` | Wrong client ID/secret, a used or expired code, a redirect URL that doesn't match the app, or a refresh token that no longer works. Log in again with `authorize`. |
| `UnauthenticatedAccountError` | No credentials at all (or no access token for something that needs one): log in first. |
| `MAL doesn't see the MALSESSIONID cookie as logged in` | The cookie is wrong or expired. Export it again from a logged in browser. |
| `MyAnimeListApiError` (`.status_code`) | MAL refused the request; the message includes MAL's answer. |
| `SiteUnavailableError` | MAL can't be reached, or keeps answering with a server error. |

## Constructor

```python
Account(username: str, *, token_file: str | None = None)
```

Returns a singleton keyed by username. `token_file` changes where the tokens are
saved and loaded from.

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `username` | `str` | MAL username |
| `animes` | `AccountAnimes` | The anime list (lazy-loaded set) |
| `mangas` | `AccountMangas` | The manga list (lazy-loaded set) |
| `friends` | `AccountFriends` | The friends list (lazy-loaded set, first 100) |
| `user_id` | `int` | MAL user id (loaded on first access) |
| `is_auth` | `bool` | Whether there is an access token (list editing possible) |
| `has_api_access` | `bool` | Whether there is at least a client ID |
| `has_session` | `bool` | Whether there is a website session cookie |
| `web` | `WebSession` or `None` | The website session of the cookie login (`pymal.web_session`) |

## Methods

- `authorize(client_id, client_secret=None, redirect_uri=None, open_browser=True)` — the one-time login described above.
- `login_with_cookie(session_id, save=False, user_agent="")` — experimental login with browser cookies (a cookie export path, the `MALSESSIONID` value, a dict or a `Cookie` header), see above.
- `login(client_id, access_token="", refresh_token="", client_secret="", save=False)` — use tokens you already have.
- `api_pages(path, params=None)` — like `api` for a paged answer (`{"data": [...], "paging": ...}`): iterates over all the items, following the pages.
- `api(method, path, params=None, data=None)` — call any [API v2](https://myanimelist.net/apiconfig/references/api/v2) endpoint, e.g. `account.api("GET", "/users/@me")`; returns the decoded JSON.
- `me(fields="anime_statistics") -> dict` — your profile and list statistics (needs a token).
- `suggestions(limit=100)` — animes MAL suggests to you, as `Anime` objects (needs a token).
- `anime_ranking(ranking_type="all", limit=100)` — the top animes (`all`, `airing`, `upcoming`, `tv`, `ova`, `movie`, `special`, `bypopularity`, `favorite`) as `Anime` objects.
- `search(search_line, is_anime=True)` — search anime (or manga); results already in your list are your `MyAnime`/`MyManga`.
- `get_image()` — download the avatar as a `PIL.Image.Image`.
- `reload()` — re-fetch account data.

Errors: `UnauthenticatedAccountError` when there are no credentials,
`MyAnimeListApiError` (with `.status_code`) when the API refuses a request, and
`SiteUnavailableError` when MAL can't be reached.

## List objects

`account.animes` and `account.mangas` are set-like objects. Their entries are
[`MyAnime`](my_anime.md) / [`MyManga`](my_manga.md) objects, already filled with your data.

```python
len(account.animes)              # number of entries
anime in account.animes          # membership test (Anime, MyAnime or ID)
account.animes.reload()          # re-fetch from MAL
account.animes.watching          # also completed, on_hold, dropped, plan_to_watch
account.mangas.reading           # also completed, on_hold, dropped, plan_to_read

# Set operations
account.animes | friend.animes   # union
account.animes & friend.animes   # intersection
account.animes - friend.animes   # difference
account.animes ^ friend.animes   # symmetric difference
```

## Example

```python
from pymal.account import Account
from pymal.anime import Anime

account = Account("your-username")
account.authorize("your-client-id")      # only the first time

for entry in account.animes:
    print(entry.title, entry.my_score)

print(Anime(1) in account.animes)        # True / False
```

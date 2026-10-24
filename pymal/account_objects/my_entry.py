__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

from pymal import exceptions


__all__ = ["MyEntry"]


class _Field:
    """
    A ``my_*`` value of a list entry. It is read from the API's list status the first
    time it is used, can be changed, and is sent back by :meth:`MyEntry.update`.

    :param key: the key in the API's list status.
    :param default: the value of an entry that isn't in the list.
    :param update_key: the name of the parameter when updating, if it isn't ``key``.
    :param convert: API value -> python value.
    :param to_api: python value -> API value.
    :param valid: the python values this field accepts.
    """

    def __init__(
        self, key, default, update_key=None, convert=None, to_api=None, valid=None
    ):
        self.key = key
        self.default = default
        self.update_key = update_key or key
        self.convert = convert or (lambda value: value)
        self.to_api = to_api or (lambda value: value)
        self.valid = valid
        self.name = ""

    def __set_name__(self, _owner, name):
        self.name = name

    def __get__(self, obj, _owner=None):
        if obj is None:
            return self
        if not obj._is_my_loaded:
            obj.my_reload()
        return obj._my_values[self.name]

    def __set__(self, obj, value):
        if self.valid is not None and not self.valid(value):
            raise ValueError(f"invalid value for {self.name}: {value!r}")
        if not obj._is_my_loaded:
            obj.my_reload()
        obj._my_values[self.name] = value


def int_between(low, high):
    return lambda value: isinstance(value, int) and low <= value <= high


def at_least_zero(value):
    return isinstance(value, int) and value >= 0


def status_field(names: dict) -> _Field:
    """
    :param names: ``{number: api name}``, for example ``{1: "watching", ...}``.
    """
    numbers = {name: number for number, name in names.items()}
    return _Field(
        "status",
        0,
        convert=lambda name: numbers.get(name, 0),
        to_api=lambda number: names[number],
        valid=lambda value: value in names,
    )


def _date_from_api(value) -> str:
    """``2024-03-05`` (or ``2024-03`` / ``2024``) -> ``20240305`` (``00`` for unknown parts)."""
    parts = (value or "").split("-")
    parts += ["00"] * (3 - len(parts))
    return "".join(
        part.zfill(width) for part, width in zip(parts, (4, 2, 2), strict=True)
    )


def _date_to_api(value: str) -> str | None:
    year, month, day = value[:4], value[4:6], value[6:8]
    if year == "0000":
        return None
    if month == "00":
        return year
    return f"{year}-{month}" if day == "00" else f"{year}-{month}-{day}"


def _valid_date(value) -> bool:
    return isinstance(value, str) and len(value) == 8 and value.isdigit()


def date_field(key: str) -> _Field:
    return _Field(
        key, "00000000", convert=_date_from_api, to_api=_date_to_api, valid=_valid_date
    )


def tags_field() -> _Field:
    return _Field(
        "tags",
        frozenset(),
        convert=lambda tags: frozenset(tags or ()),
        to_api=lambda tags: ",".join(sorted(tags)),
        valid=lambda value: isinstance(value, (set, frozenset, list, tuple)),
    )


class MyEntry:
    """
    Base of :class:`my_anime.MyAnime` and :class:`my_manga.MyManga`: the data of an
    account about an anime/manga (status, score, progress, ...), kept on MAL.

    Everything that isn't here is taken from the wrapped :class:`anime.Anime` or
    :class:`manga.Manga` (``self.obj``).
    """

    _KIND = ""  # "anime" or "manga"
    # What the website session (experimental) can read and change:
    # {field name: (key in the website's list, key when changing)}
    _WEB_FIELDS = {}
    _FIELDS = ()  # the _Field attributes of the class, in order

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._FIELDS = tuple(v for v in vars(cls).values() if isinstance(v, _Field))

    def __init__(self, obj, account):
        self.obj = obj
        self._account = account
        self._is_my_loaded = False
        self._in_list = False
        self._my_values = {}
        self._set_defaults()

    def _set_defaults(self):
        self._my_values = {field.name: field.default for field in self._FIELDS}

    # -- loading ----------------------------------------------------------------

    @property
    def in_list(self) -> bool:
        """
        :return: True if the account has this in its list.
        :rtype: bool
        """
        if not self._is_my_loaded:
            self.my_reload()
        return self._in_list

    def my_reload(self):
        """
        Reloading the account's data about this from MAL.
        """
        if not self._account.has_api_access:
            self._web_reload()
            return
        fields = ",".join(field.key for field in self._FIELDS)
        data = self._account.api(
            "GET",
            f"/{self._KIND}/{self.obj.id}",
            {"fields": f"my_list_status{{{fields}}}"},
        )
        self._load_status((data or {}).get("my_list_status"))

    def _load_status(self, status: dict | None):
        """Fill from an API list status; ``None`` means it isn't in the list."""
        self._set_defaults()
        self._in_list = bool(status)
        for field in self._FIELDS:
            if status and field.key in status:
                self._my_values[field.name] = field.convert(status[field.key])
        self._is_my_loaded = True

    def _web_to_status(self, item: dict) -> dict:
        """A website list entry -> an API list status."""
        status = {"status": self._STATUS_NAMES.get(item.get("status"))}
        for name, (read_key, _write_key) in self._WEB_FIELDS.items():
            if name != "my_status" and read_key in item:
                status[getattr(type(self), name).key] = item[read_key]
        return status

    def _web_session(self):
        web = self._account.web
        if web is None:
            from pymal import exceptions

            raise exceptions.UnauthenticatedAccountError(self._account.username)
        return web

    def _web_reload(self):
        web = self._web_session()
        wanted = self.obj.id
        for item in web.list_items(self._KIND, self._account.username):
            if item.get(f"{self._KIND}_id") == wanted:
                self._load_status(self._web_to_status(item))
                return
        self._load_status(None)

    def _web_update(self):
        self._form()  # fills in the default status
        payload = {f"{self._KIND}_id": self.obj.id}
        for name, (_read_key, write_key) in self._WEB_FIELDS.items():
            payload[write_key] = self._my_values[name]
        action = "edit" if self._in_list else "add"
        self._web_session().post_json(f"/ownlist/{self._KIND}/{action}.json", payload)
        # Trust the website, not the answer: read the entry back.
        self._web_reload()
        if not self._in_list:
            raise exceptions.MyAnimeListApiError(
                f"The website accepted the {action} of {self._KIND} {self.obj.id} "
                "but it is not in the list."
            )

    def _web_delete(self):
        self._web_session().post_form(f"/ownlist/{self._KIND}/{self.obj.id}/delete")
        self._web_reload()
        if self._in_list:
            raise exceptions.MyAnimeListApiError(
                f"The website accepted the delete of {self._KIND} {self.obj.id} "
                "but it is still in the list."
            )

    # -- changing ---------------------------------------------------------------

    def _form(self) -> dict:
        # An entry that isn't in the list yet has no status; start as "plan to".
        if not self._my_values["my_status"]:
            self._my_values["my_status"] = 6
        form = {}
        for field in self._FIELDS:
            value = field.to_api(self._my_values[field.name])
            if value is None:  # an unset date can't be sent
                continue
            form[field.update_key] = (
                str(value).lower() if isinstance(value, bool) else value
            )
        return form

    def update(self):
        """
        Sending the data to MAL; adds the entry to the list if it isn't there.
        """
        if not self._is_my_loaded:
            self.my_reload()
        try:
            if not self._account.has_api_access:
                self._web_update()
                return
            status = self._account.api(
                "PUT", f"/{self._KIND}/{self.obj.id}/my_list_status", data=self._form()
            )
        except exceptions.MyAnimeListApiError as err:
            raise exceptions.MyAnimeListApiUpdateError(str(err), err.status_code) from err
        self._load_status(status)

    def delete(self):
        """
        Deleting from the list.
        """
        try:
            if not self._account.has_api_access:
                self._web_delete()
                return
            self._account.api("DELETE", f"/{self._KIND}/{self.obj.id}/my_list_status")
        except exceptions.MyAnimeListApiError as err:
            raise exceptions.MyAnimeListApiDeleteError(str(err), err.status_code) from err
        self._load_status(None)

    def add(self, account):
        """
        Adding to the list of an account.
        If its the same account as this owner returning this.

        :param account: account to connect to.
        :type account: :class:`account.Account`
        :return: the entry of the account
        """
        if account != self._account:
            return self.obj.add(account)
        if not self.in_list:
            try:
                self.update()
            except exceptions.MyAnimeListApiUpdateError as err:
                raise exceptions.MyAnimeListApiAddError(
                    str(err), err.status_code
                ) from err
        return self

    # -- python protocol ----------------------------------------------------------

    def __getattr__(self, name):
        if name.startswith("_") or name == "obj":
            raise AttributeError(name)
        return getattr(self.obj, name)

    def __dir__(self):
        return list(set(dir(type(self)) + list(self.__dict__.keys()) + dir(self.obj)))

    def __eq__(self, other):
        return self.obj == other

    def __hash__(self):
        import hashlib

        hash_md5 = hashlib.md5()
        hash_md5.update(self._account.username.encode())
        hash_md5.update(self._KIND.encode())
        hash_md5.update(str(self.obj.id).encode())
        return int(hash_md5.hexdigest(), 16)

    def __repr__(self):
        title = f" '{self.title:s}'" if self.obj._is_loaded else ""
        return (
            f"<{self.__class__.__name__:s}{title:s} of account "
            f"'{self._account.username:s}' id={self.obj.id:d}>"
        )

    def __format__(self, format_spec):
        return str(self).__format__(format_spec)

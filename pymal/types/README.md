Usage
=====
All kinds of generic objects and types are placed here.

Objects
-------

### ReloadedSet
A base class for all `set` object in pymal.
Because MAL using a db, there shouldn't be anything twice, so we always use set.
Because we want people to be able to do set-like function on the `set` object we use set.
Because we don't want people to thing they can change the set we use `frozenset`.
But we can't reload and using `frozenset` so we created our own object!

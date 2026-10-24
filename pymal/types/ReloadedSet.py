__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

import collections.abc

import singleton_factory


class ReloadedSet(collections.abc.Set):
    """
    A reloaded set - like frozenset but can fetch new data in the function reload.
    To inheritance you need to make:
     - _values
     - reload
    """

    @property
    def _values(self):
        raise NotImplementedError()

    def reload(self):
        raise NotImplementedError()

    def __contains__(self, item):
        return item in list(self._values)

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)

    def issubset(self, other) -> frozenset:
        return self <= frozenset(other)

    def issuperset(self, other) -> frozenset:
        return self >= frozenset(other)

    def union(self, *others) -> frozenset:
        res = set(self)
        for other in others:
            res |= frozenset(other)
        return frozenset(res)

    def __or__(self, other) -> frozenset:
        return self.union(other)

    def intersection(self, *others) -> frozenset:
        other_lists = [list(other) for other in others]
        return frozenset(x for x in self if all(x in lst for lst in other_lists))

    def __and__(self, other) -> frozenset:
        return self.intersection(other)

    def difference(self, *others) -> frozenset:
        other_lists = [list(other) for other in others]
        return frozenset(x for x in self if not any(x in lst for lst in other_lists))

    def __sub__(self, other) -> frozenset:
        return self.difference(other)

    def symmetric_difference(self, other) -> frozenset:
        self_list = list(self)
        other_not_in_self = frozenset(filter(lambda x: x not in self_list, other))

        other = list(other)
        self_not_in_other = frozenset(filter(lambda x: x not in other, self))

        return other_not_in_self | self_not_in_other

    def __xor__(self, other) -> frozenset:
        return self.symmetric_difference(other)


class ReloadedSetSingletonFactoryType(
    type(ReloadedSet), singleton_factory.SingletonFactory
):
    """
    A singleton factory ReloadedSet type.
    """

    pass


class ReloadedSetSingletonFactory(ReloadedSet, metaclass=ReloadedSetSingletonFactoryType):
    """
    A singleton factory ReloadedSet.
    """

    pass

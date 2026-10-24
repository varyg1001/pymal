__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

import functools


def load(function):
    """
    This decorator checking of the class was loaded and load it if needed.
    For lazy.
    Needs attribute _is_loaded and a function reload().
    """

    @functools.wraps(function)
    def _load_wrapper(self, *args):
        if not self._is_loaded:
            self.reload()
        return function(self, *args)

    return _load_wrapper

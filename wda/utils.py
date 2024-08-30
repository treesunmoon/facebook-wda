# coding: utf-8

import functools
import typing
import inspect


def inject_call(fn, *args, **kwargs):
    """
    Call function without known all the arguments

    Args:
        fn: function
        args: arguments
        kwargs: key-values
    
    Returns:
        as the fn returns
    """
    assert callable(fn), "first argument must be callable"

    st = inspect.signature(fn)
    fn_kwargs = {
        key: kwargs[key]
        for key in st.parameters.keys() if key in kwargs
    }
    ba = st.bind(*args, **fn_kwargs)
    ba.apply_defaults()
    return fn(*ba.args, **ba.kwargs)


def limit_call_depth(n: int):
    """
    n = 0 means not allowed recursive call
    """

    def wrapper(fn: typing.Callable):

        @functools.wraps(fn)
        def _inner(*args, **kwargs):
            ismethod = len(args) > 0 and not isinstance(args[0], type) and hasattr(args[0].__class__, fn.__name__)
            if not ismethod and not hasattr(fn, '__call_depth'):
                fn.__call_depth = 0
            if ismethod and not hasattr(args[0], '__call_depth'):
                args[0].__call_depth = 0
            if (not ismethod and fn.__call_depth > n) or (ismethod and args[0].__call_depth > n):
                raise RuntimeError("call depth exceed %d" % n)
            if ismethod:
                args[0].__call_depth += 1
            else:
                fn.__call_depth += 1
            try:
                return fn(*args, **kwargs)
            finally:
                if ismethod:
                    args[0].__call_depth -= 1
                else:
                    fn.__call_depth -= 1

        return _inner

    return wrapper


class AttrDict(dict):
    def __getattr__(self, key):
        if isinstance(key, str) and key in self:
            return self[key]
        raise AttributeError("Attribute key not found", key)


def convert(dictionary):
    """
    Convert dict to namedtuple
    """
    return AttrDict(dictionary)

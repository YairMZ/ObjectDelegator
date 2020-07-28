import inspect


# taken from https://www.fast.ai/2019/08/06/delegation/
## not yet tested ##
def delegates(to=None, keep=False):
    """Decorator: replace `**kwargs` in signature with params from `to`"""
    def _f(f):
        if to is None:
            to_f, from_f = f.__base__.__init__, f.__init__
        else:
            to_f, from_f = to, f
        sig = inspect.signature(from_f)
        sigd = dict(sig.parameters)
        k = sigd.pop('kwargs')
        s2 = {k: v for k, v in inspect.signature(to_f).parameters.items()
              if v.default != inspect.Parameter.empty and k not in sigd}
        sigd.update(s2)
        if keep:
            sigd['kwargs'] = k
        from_f.__signature__ = sig.replace(parameters=sigd.values())
        return f
    return _f


# taken from https://www.fast.ai/2019/08/06/delegation/
def custom_dir(c, add): return dir(type(c)) + list(c.__dict__.keys()) + add

# based on https://www.fast.ai/2019/08/06/delegation/
# noinspection SpellCheckingInspection
class Delegator:
    """
    Base class for attr accesses in `self._xtra` passed down to `self.default`
    """
    xtra = []

    @property
    def xtra(self):
        return self._xtra

    @xtra.setter
    def xtra(self, val):
        if self.default is not None:
            self._xtra = val
        else:
            self._xtra = []

    def set_delegated_methods(self, methods_list=None):
        if methods_list is None:
            self.xtra = self.get_possible_methods_to_delegate()
        else:
            self.xtra = methods_list

    def get_possible_methods_to_delegate(self):
        if self.default is None:
            return []
        else:
            return [o for o in dir(self.default) if not o.startswith('_')]


    def __getattr__(self, k):
        if k in self.xtra:
            return getattr(self.default, k)
        raise AttributeError(k)

    def __dir__(self):
        return custom_dir(self, self.xtra)


if __name__ == '__main__':
    class Foo:
        def foo(self):
            return 'foo'

    class Bar(Delegator):
        def __init__(self):
            tmp = Foo()
            self.bar = tmp
            self.default = tmp
            self.set_delegated_methods()

    b = Bar()
    print(b.foo())
    print(b.get_possible_methods_to_delegate())
    pass

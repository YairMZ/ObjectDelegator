from abc import ABC


# taken from https://www.fast.ai/2019/08/06/delegation/
def custom_dir(c, add): return dir(type(c)) + list(c.__dict__.keys()) + add


# based on https://www.fast.ai/2019/08/06/delegation/
# noinspection SpellCheckingInspection
class Delegator(ABC):
    """
    Base class for attr accesses in `self._xtra` passed down to `self.default`
    """
    _delegated_methods = []

    def get_delegated_methods(self):
        return self._delegated_methods

    def set_delegated_methods(self, methods_list=None):
        if self.default is not None:
            if methods_list is None:
                self._delegated_methods = self.get_possible_methods_to_delegate()
            else:
                self._delegated_methods = methods_list
        else:
            self._delegated_methods = []

    def get_possible_methods_to_delegate(self):
        if self.default is None:
            return []
        else:
            return list(filter(lambda x: x[0] != '_' and callable(getattr(self.default, x)), dir(self.default)))
            # [o for o in dir(self.default) if not o.startswith('_')]

    def get_possible_objects_to_delegate_to(self):
        """This method is only relevant if called within a child class (when self is a subclassed object).
        Most probably won't raise any exceptions otherwise, but results will be confusing and misleading.
        """
        return [obj for obj in dir(self) if not (obj.startswith('_') or callable(getattr(self, obj)))]

    def __getattr__(self, k):
        if k in self._delegated_methods:
            return getattr(self.default, k)
        raise AttributeError(k)

    def __dir__(self):
        return custom_dir(self, self._delegated_methods)



if __name__ == '__main__':
    class Foo:
        def foo(self):
            return 'foo'

    class Bar(Delegator):
        def __init__(self):
            tmp = Foo()
            self.bar = tmp
            self.test = 1
            self.default = tmp
            self.set_delegated_methods()


    b = Bar()
    print(b.foo())
    test1 = [o for o in dir(b) if not o.startswith('_')]
    test2 = [o for o in test1 if not callable(getattr(b,o))]
    test = [o for o in dir(b) if not (o.startswith('_') or callable(getattr(b,o))) ]
    print(b.get_possible_objects_to_delegate_to())
    print(b.get_possible_methods_to_delegate())
    pass

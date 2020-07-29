from abc import ABC
from typing import Union, Any, List


# taken from https://www.fast.ai/2019/08/06/delegation/
def _custom_dir(c: Any, add: List[str]) -> list:
    """Used to add list of custom strings to the dir() of a delegator"""
    return dir(type(c)) + list(c.__dict__.keys()) + add


# based on https://www.fast.ai/2019/08/06/delegation/
# noinspection SpellCheckingInspection
class Delegator(ABC):
    """
    Abstract class to enable delegation of methods.
    To use inherit it and use the API to delegate specific methods of chosen members.
    """
    _delegated_methods: dict = {}

    def get_delegated_methods(self) -> dict:
        """
        return all delegated methods

        :rtype: dict
        :return: returns a dictionary with keys as memebers which own delegated methods, values as list of string names of delegated methds per member.
        """
        return self._delegated_methods

    def set_delegated_methods(self, delegation_dict: dict) -> None:
        """sets the delegated methods

        delegation dict should be a dictionary of members names as keys, and methods names as list of strings.
        Example:

        {'foo_obj': ['foo_method1], 'bar_obj': ['bar_method1', 'bar_method2']}

        :raises AttributeError: The function raises an AttributeError if a certian member doesn't have the required method
        :raises ValueError: The function raises a ValueError if the same method name appears twice.
        """
        method_names = []
        [method_names.extend(x) for x in delegation_dict.values()]  # get all method names
        if len(set(method_names)) < len(method_names):  # check for recurring names
            raise ValueError("cannot delegate two methods with the same name.")
        for member in delegation_dict.keys():
            for method_name in delegation_dict[member]:
                if not callable(getattr(getattr(self, member), method_name)):
                    raise AttributeError("'%s' object has no callable '%s'" % (member, method_name))
        self._delegated_methods = delegation_dict

    def get_possible_methods_to_delegate(self, required_object: Union[None, str] = None) -> dict:
        """Obtain a dict of methods which can be delegated for a single or all members.

        :param required_object: if required_object is None possible methods are returned for all object members otherwise methods are returned for selected member.
        :rtype: dict
        :returns: a dict of keys as objects, and values as strings of method names whic hcan be delegated.
        """
        if required_object is None:
            possible_members = self.get_possible_objects_to_delegate_to()
            result = {}
            for member in possible_members:
                result[member] = list(
                    filter(lambda x: x[0] != '_' and callable(getattr(getattr(self, member), x)),
                           dir(getattr(self, member))))
            return result
        else:
            return {required_object: list(
                filter(lambda x: x[0] != '_' and callable(getattr(getattr(self, required_object), x)),
                       dir(getattr(self, required_object))))}

    def get_possible_objects_to_delegate_to(self):
        """This method is only relevant if called within a child class (when self is a subclassed object).
        Most probably won't raise any exceptions otherwise, but results will be confusing and misleading.
        """
        return [obj for obj in dir(self) if not (obj.startswith('_') or callable(getattr(self, obj)))]

    @property
    def _list_all_delegated_methods(self):
        """returns a flat list of all delegated methods. For internal use."""
        if self._delegated_methods:
            method_names = []
            [method_names.extend(x) for x in self._delegated_methods.values()]  # get all method names
            return method_names
        else:
            return []

    def __getattr__(self, _attribute):
        for member in self._delegated_methods.keys():
            if _attribute in self._delegated_methods[member]:
                return getattr(getattr(self, member), _attribute)
        raise AttributeError(_attribute)

    def __dir__(self):
        return _custom_dir(self, self._list_all_delegated_methods)


if __name__ == '__main__':
    class Foo:
        # noinspection PyMethodMayBeStatic
        def foo(self):
            """dummy method"""
            return 'foo'


    class Bar(Delegator):
        def __init__(self):
            tmp = Foo()
            self.bar = tmp
            self.test = 1
            self.set_delegated_methods({'bar': ['foo']})


    b = Bar()
    print(b.foo())
    test = dir(b)
    print(b.get_possible_objects_to_delegate_to())
    print(b.get_possible_methods_to_delegate())
    pass

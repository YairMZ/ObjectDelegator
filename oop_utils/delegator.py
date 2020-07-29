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
    Abstract class to enable delegation of members, properties, and methods.
    To use, inherit it and use the API to delegate chosen members.
    """
    _delegated_members: dict = {}

    def get_delegated_members(self) -> dict:
        """
        return all delegated members

        :rtype: dict
        :return: returns a dictionary with keys as memebers which own delegated members, values as list of string names of delegated members.
        """
        return self._delegated_members

    def set_delegated_members(self, delegation_dict: dict) -> None:
        """sets the delegated members

        delegation dict should be a dictionary of members names as keys, and delegated members names as list of strings.
        Example:

        {'foo_obj': ['foo_method1], 'bar_obj': ['bar_method1', 'bar_method2']}

        :raises AttributeError: The function raises an AttributeError if a certian member doesn't have the required attribute
        :raises ValueError: The function raises a ValueError if the same member name appears twice.
        """
        member_names = []
        [member_names.extend(x) for x in delegation_dict.values()]  # get all member names
        if len(set(member_names)) < len(member_names):  # check for recurring names
            raise ValueError("cannot delegate two members with the same name.")
        for member in delegation_dict.keys():
            for member_name in delegation_dict[member]:
                if not getattr(getattr(self, member), member_name, None):
                    raise AttributeError("'%s' object has no attribute '%s'" % (member, member_name))
        self._delegated_members = delegation_dict

    def get_possible_members_to_delegate(self, required_object: Union[None, str] = None) -> dict:
        """Obtain a dict of members which can be delegated.

        :param required_object: if required_object is None possible members are returned for all members of self. otherwise  possible members are returned for required_object.
        :rtype: dict
        :returns: a dict of object names as keys, and values as strings of member names which hcan be delegated.
        """
        if required_object is None:
            possible_members = self.get_possible_objects_to_delegate_to()
            result = {}
            for member in possible_members:
                result[member] = list(
                    filter(lambda x: x[0] != '_' and getattr(getattr(self, member), x, None),
                           dir(getattr(self, member))))
            return result
        else:
            return {required_object: list(
                filter(lambda x: x[0] != '_' and getattr(getattr(self, required_object), x, None),
                       dir(getattr(self, required_object))))}

    def get_possible_objects_to_delegate_to(self):
        """This method is only relevant if called within a child class (when self is a subclassed object).
        Most probably won't raise any exceptions otherwise, but results will be confusing and misleading.
        """
        delegation_dict = self._delegated_members
        self._delegated_members = {}
        res = [obj for obj in dir(self) if not (obj.startswith('_') or callable(getattr(self, obj)))]
        self.set_delegated_members(delegation_dict)
        return res

    @property
    def _list_all_delegated_members(self):
        """returns a flat list of all delegated members. For internal use."""
        if self._delegated_members:
            member_names = []
            [member_names.extend(x) for x in self._delegated_members.values()]  # get all member names
            return member_names
        else:
            return []

    def __getattr__(self, _attribute):
        for member in self._delegated_members.keys():
            if _attribute in self._delegated_members[member]:
                return getattr(getattr(self, member), _attribute)
        raise AttributeError(_attribute)

    def __dir__(self):
        return _custom_dir(self, self._list_all_delegated_members)


if __name__ == '__main__':
    class Foo:
        foo_property = 'hi'

        # noinspection PyMethodMayBeStatic
        def foo(self):
            """dummy method"""
            return 'foo'


    class Bar(Delegator):
        def __init__(self):
            tmp = Foo()
            self.bar = tmp
            self.test = 1
            self.set_delegated_members({'bar': ['foo', 'foo_property']})


    b = Bar()
    print(b.foo())
    test = dir(b)
    print(b.get_possible_objects_to_delegate_to())
    print(b.get_possible_members_to_delegate())
    print(b.foo_property)
    pass

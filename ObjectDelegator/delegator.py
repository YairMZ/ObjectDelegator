from abc import ABC
from typing import Union
import inspect
from types import MethodType


# based on https://www.fast.ai/2019/08/06/delegation/
class Delegator(ABC):
    """
    Abstract class to enable delegation of members, properties, and methods.
    To use, inherit it and use the API to delegate chosen members.
    """
    _delegated_members: dict = {}
    _originating_object_delegatable_members = []

    def get_delegated_members(self) -> dict:
        """
        return all delegated members

        :rtype: dict
        :return: returns a dictionary with keys as members which own delegated members, values as list of string names of delegated members.
        """
        return self._delegated_members

    def set_delegated_members(self, delegation_dict: dict) -> None:
        """sets the delegated members

        delegation dict should be a dictionary of members names as keys, and delegated members names as list of strings.
        Example:

        {'foo_obj': ['foo_method1], 'bar_obj': ['bar_method1', 'bar_method2']}

        :raises AttributeError: The function raises an AttributeError if a certain member doesn't have the required attribute
        :raises ValueError: The function raises a ValueError if the same member name appears twice.
        """
        if not self._delegated_members:  # if no delegations were yet made, list originating members
            self._originating_object_delegatable_members = [obj for obj in dir(self) if
                                                            not (obj.startswith('_') or callable(getattr(self, obj)))]
        member_names = []
        [member_names.extend(x) for x in delegation_dict.values()]  # get all member names
        if len(set(member_names)) < len(member_names):  # check for recurring names
            raise ValueError("cannot delegate two members with the same name.")

        previous_delegations = self._list_all_delegated_members  # look for new conflicting delegations
        for new_member in member_names:
            if new_member in previous_delegations:
                raise ValueError("cannot delegate two members with the same name.")

        for obj in delegation_dict:  # verify suggested object names and members are valid attributes
            for member_name in delegation_dict[obj]:
                if not getattr(getattr(self, obj), member_name, None):
                    raise AttributeError("'%s' object has no attribute '%s'" % (obj, member_name))

        # now delegate
        if not self._delegated_members:
            self._delegated_members = delegation_dict
        else:
            for obj in delegation_dict:  # for each object needing delegation
                if obj not in self._delegated_members.keys():  # if this object didn't have delegation before
                    self._delegated_members[obj] = delegation_dict[obj]
                else:  # if it had delegations append the new ones
                    self._delegated_members[obj] += delegation_dict[obj]

    def get_possible_members_to_delegate(self, required_object: Union[None, str] = None) -> dict:
        """Obtain a dict of members which can be delegated.

        :param required_object: if required_object is None possible members are returned for all members of self. otherwise  possible members are returned for required_object.
        :rtype: dict
        :returns: a dict of object names as keys, and values as strings of member names which can be delegated.
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
        already_delegated = self._list_all_delegated_members  # list members already delegated as I may delegate to them recursively
        return self._originating_object_delegatable_members + already_delegated

    def clear_all_delegations(self):
        self._delegated_members = {}

    def remove_delegations_for_object(self, obj_name: str):
        """The function removes all delegations made for members obj_name,
        as well dependent recursive delegations, i.e. if one of obj_name did his own delegations they are rmoved too"""
        # check if i need to remove dependent recursive delegations
        for delegate in self._delegated_members.get(obj_name, None):
            if delegate in self._delegated_members:
                self.remove_delegations_for_object(delegate)
        self._delegated_members.pop(obj_name, None)

    @property
    def _list_all_delegated_members(self):
        """returns a flat list of all delegated members. For internal use."""
        if self._delegated_members:
            member_names = []
            [member_names.extend(x) for x in self._delegated_members.values()]  # get all member names
            return member_names
        else:
            return []

    def _compose_a_method(self, obj, delegate):
        """ not currently used """

        def new_method(self, *args, **kwargs):
            return getattr(getattr(self, obj), delegate)(*args, **kwargs)

        if inspect.isfunction(getattr(getattr(self, obj), delegate)):
            new_method.__defaults__ = getattr(getattr(self, obj), delegate).__defaults__
            new_method.__kwdefaults__ = getattr(getattr(self, obj), delegate).__kwdefaults__
            new_method.__annotations__ = getattr(getattr(self, obj), delegate).__annotations__

        new_method.__name__ = delegate
        new_method.__doc__ = getattr(getattr(self, obj), delegate).__doc__
        new_method.__qualname__ = self.__class__.__name__ + '.' + delegate
        new_method.__signature__ = inspect.signature(getattr(getattr(self, obj), delegate))

        self.__setattr__(delegate, MethodType(new_method, self))

    def __getattr__(self, _attribute):
        for member in self._delegated_members.keys():
            if _attribute in self._delegated_members[member]:
                return getattr(getattr(self, member), _attribute)
        raise AttributeError(_attribute)

    def __dir__(self):
        return list(set(dir(type(self)) + list(self.__dict__.keys()) + self._list_all_delegated_members))


if __name__ == '__main__':
    class RabbitHole:
        def __init__(self, txt):
            self.down_we_go = txt


    class Foo:
        foo_property = 'hi'
        not_delegated_property = 'bye'
        rabbit = RabbitHole('first rabbit')

        # noinspection PyMethodMayBeStatic
        def foo(self, txt: str) -> str:
            """dummy method"""
            return txt


    class Bar:
        rabbit_too = RabbitHole('second rabbit')
        boring = 2

        def bar_meth(self, text: str) -> str:
            return text + text


    class Master(Delegator):
        def __init__(self):
            self.foo_obj = Foo()
            self.bar_obj = Bar()
            self.test = 1

        def master_method(self):
            print("I'm the master")

    master = Master()  # instantiate a master

    # Do some delegations
    master.set_delegated_members({'foo_obj': ['foo', 'foo_property', 'rabbit'], 'bar_obj': ['rabbit_too']})
    print(master.foo.__doc__)  # can delegate methods
    sig = inspect.signature(master.foo)

    print(master.foo('hi there'))
    print(inspect.getmembers(master, inspect.ismethod))
    print(master.foo_property)  # can delegate properties

    print(master.rabbit.down_we_go)  # or even other objects
    print(master.rabbit_too.down_we_go)  # and another rabbit hole instance
    # find more objects I can delegate too
    print(master.get_possible_objects_to_delegate_to())

    # find more members I can delegate to master
    print(master.get_possible_members_to_delegate())

    # list delegated members
    print(master.get_delegated_members())

    # delegate the first rabbit too to preserve encapsulation
    master.set_delegated_members({'rabbit': ['down_we_go']})
    print(master.down_we_go)

    # if we try to delegate the second rabbit we get a ValueError as we can't have two members with the same name
    # master.set_delegated_members({'rabbit_too': ['down_we_go']})

    # let us then remove the delegation for the first rabbit
    print('before removal: ', master.get_delegated_members())
    master.remove_delegations_for_object('foo_obj')
    print('after recursive removal: ', master.get_delegated_members())

    # and delegate the second
    master.set_delegated_members({'rabbit_too': ['down_we_go']})
    print(master.down_we_go)

    # clear all the mess
    master.clear_all_delegations()

    master.set_delegated_members({'foo_obj': ['foo', 'foo_property', 'rabbit'], 'bar_obj': ['rabbit_too', 'bar_meth']})

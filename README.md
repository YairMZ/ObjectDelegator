# Delegate objects powerfully
This minimal yet powerful library allows delegating an object's: methods, properties, and his own member objects, to its owner. Recursive delegation is also supported.

Use the simple API to handle delegations.

From wikipedia, what is delegation:
> In object-oriented programming, delegation refers to evaluating a member
> (property or method) of one object (the receiver) in the context of another
> original object (the sender). Delegation can be done explicitly, by passing
> the sending object to the receiving object, which can be done in any
> object-oriented language; or implicitly, by the member lookup rules of the
> language, which requires language support for the feature.


# Installation

This is python3 only with no dependencies, simply:

    pip install ObjectDelegator

# Examples
ObjectDelegator is used by inheriting from `Delegeator` class. Delegation is then handled via the API, and delegated 
objects can simply be referred to as if they members of the original class subclassing `Delegeator`.

Define some dummy classes for the sake of example:

```
class RabbitHole:
    def __init__(self, txt):
        self.down_we_go = txt

class Foo:
    foo_property = 'hi'
    not_delegated_property = 'bye'
    rabbit = RabbitHole('first rabbit')

    # noinspection PyMethodMayBeStatic
    def foo(self):
        """dummy method"""
        return 'foo'

class Bar:
    rabbit_too = RabbitHole('second rabbit')
    boring = 2
```

Now define a class which inherits from `Delegeator`:

```
class Master(Delegator):
    def __init__(self):
        self.foo_obj = Foo()
        self.bar_obj = Bar()
        self.test = 1

# instantiate a master
master = Master()
```

Delegate using the `set_delegated_members` method of the `Delegeator`:

```
# use a diciotionary with keys as objects delegating members, and values as their members 
master.set_delegated_members({'foo_obj': ['foo', 'foo_property', 'rabbit'], 'bar_obj': ['rabbit_too']})
```

Delegation is versatile:

```
# can delegate methods
master.foo() # => 'foo'
# can delegate properties
master.foo_property # => 'hi'
# or even other objects
master.rabbit.down_we_go # => 'first rabbit'
# and another rabbit hole instance
master.rabbit_too.down_we_go # => 'second rabbit'
```

## API
The API allows to:

 - Delegate objects (see above).
 - Find potential objects which can delegate their members to the master:
 
```
master.get_possible_objects_to_delegate_to()  # => ['bar_obj', 'foo_obj', 'test', 'foo', 'foo_property', 'rabbit', 'rabbit_too']
```
 
 - Find potential members which can be delegated to the master:

```
master.get_possible_members_to_delegate()  # => {'bar_obj': ['boring', 'rabbit_too'], 'foo_obj': ['foo', 'foo_property', 'not_delegated_property', 'rabbit'], 'test': ['as_integer_ratio', 'bit_length', 'conjugate', 'denominator', 'from_bytes', 'numerator', 'real', 'to_bytes'], 'foo': [], ...}
```

 - List currently delegated members:

```
master.get_delegated_members()  # => {'foo_obj': ['foo', 'foo_property', 'rabbit'], 'bar_obj': ['rabbit_too']}
```

 - Add further _recursive_ delegation:

```
# Note that rabbit itself was delegated before
master.set_delegated_members({'rabbit': ['down_we_go']})
master.down_we_go   # => first rabbit
```

 - Raise a ValueError if we try to delegate to objects of the sae name

```
# if we try to delegate the second rabbit we get a ValueError as we can't have two members with the same name (down_we_go)
master.set_delegated_members({'rabbit_too': ['down_we_go']})
```

 - Remove delegations for a specific object:

```
master.remove_delegations_for_object('rabbit')
# Now we may delegate the other rabbit
master.set_delegated_members({'rabbit_too': ['down_we_go']})
master.down_we_go  # => second rabbit
```

 - clear all delegations:

```
master.clear_all_delegations()
```
from __future__ import unicode_literals
import tempfile
from nose.tools import raises

from h5it import save, load
from h5it.base import instance_is_hdf5able



path = tempfile.mkstemp()[1]


class Foo(object):

    def __init__(self):
        self.a = 1
        self.b = 'a'
        self.c = {'x': None}
        self.d = None
        self.e = False
        self.f = (1, 5, 1)
        self.g = ['h', 142+32j, -159081.1340]

    def __eq__(self, other):
        return (self.a == other.a and
                self.b == other.b and
                self.c == other.c and
                self.d == other.d and
                self.e == other.e and
                self.f == other.f and
                self.g == other.g)


class FooCustom(Foo):

    def __getstate__(self):
        state = self.__dict__.copy()
        state['f'] = list(state['f'])
        state['e_another_name'] = not state.pop('e')
        return state

    def __setstate__(self, state):
        state['f'] = tuple(state['f'])
        state['e'] = not state.pop('e_another_name')
        self.__dict__.update(state)


def test_save_instance():
    save(path, Foo())


def test_load_instance():
    x = Foo()
    save(path, x)
    y = load(path)
    assert y == x
    assert type(y) == Foo


def test_load_custom_instance():
    x = FooCustom()
    save(path, x)
    y = load(path)
    assert y == x
    print(type(y))
    assert type(y) == FooCustom


# We currently don't support more advanced uses of the Pickle protocol - ensure
# we are correctly identifying these cases

class NotAllowedReduce(object):

    def __reduce__(self):
        pass


def test_not_allowed_reduce():
    assert not instance_is_hdf5able(NotAllowedReduce())


class NotAllowedReduceEx(object):

    def __reduce_ex__(self):
        pass


def test_not_allowed_reduce_ex():
    assert not instance_is_hdf5able(NotAllowedReduceEx())


class NotAllowedGetInitArgs(object):

    def __getinitargs__(self):
        pass


def test_not_allowed_getinitargs():
    assert not instance_is_hdf5able(NotAllowedGetInitArgs())


class NotAllowedGetNewArgs(object):

    def __getnewargs__(self):
        pass


def test_not_allowed_getnewargs():
    assert not instance_is_hdf5able(NotAllowedGetNewArgs())


class NotAllowedGetNewArgsEx(object):

    def __getnewargs_ex__(self):
        pass


def test_not_allowed_getnewargs_ex():
    assert not instance_is_hdf5able(NotAllowedGetNewArgsEx())


class NotAllowedSlotsWithoutGetState(object):

    __slots__ = 'y'


def test_not_allowed_slots_without_get_state():
    assert not instance_is_hdf5able(NotAllowedSlotsWithoutGetState())


class IsAllowedSlotsWithGetState(object):

    __slots__ = 'y'

    def __getstate__(self):
        pass


def test_is_allowed_slots_with_get_state():
    assert instance_is_hdf5able(IsAllowedSlotsWithGetState())


@raises(ValueError)
def ensure_non_hdf5able_instance_raises_value_error():
    save(path, NotAllowedReduce())
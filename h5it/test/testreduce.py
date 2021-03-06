from __future__ import unicode_literals
import tempfile

from h5it import dump, load


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
    dump(Foo(), path)


def test_load_instance():
    x = Foo()
    dump(x, path)
    y = load(path)
    assert y == x
    assert type(y) == Foo


def test_load_custom_instance():
    x = FooCustom()
    dump(x, path)
    y = load(path)
    assert y == x
    print(type(y))
    assert type(y) == FooCustom


def test_save_set():
    dump({'b', True, 'd', 1, None, ('key', 2.5012343)}, path)


def test_load_set():
    x = {'b', True, 'd', 1, None, ('key', 2.5012343)}
    dump(x, path)
    y = load(path)
    assert y == x
    assert type(y) == set

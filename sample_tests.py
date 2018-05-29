"""

StateDescriptor: State | str

@state(str)
def f(cur, prev): -> boolean
    pass

@trans(oldstate: StateDescriptor, newstate: StateDescriptor)
def f(old) -> new
    # old must be immutable!
    return old[:]

"""

from transition import Tester

import random


class Class(object):
    def __init__(self, prev=None):
        if prev:
            self.items = prev.items[:]
        else:
            self.items = []


with Tester(Class) as test:
    @test.state('initial state S1')
    def s1(cur):
        test.assertEqual(len(cur.items), 0)

    @test.state('item added')
    def s_item_added(cur, prev):
        test.assertEqual(len(prev.items) + 1, len(cur.items))
        test.assertTrue(all(x == y))

    @test.trans(s1, s_item_added)
    def additem(prev):
        cur = Class(prev)
        cur.items.append(random.randint(0, 100))
        return cur

    @test.trans(s_item_added, s1)
    def clearitem(prev):
        cur = Class(prev)
        cur.items = []
        return cur

    @test.entry(s1)
    def entry_to_s1():
        return Class()  # or t.cls()

    test.run()

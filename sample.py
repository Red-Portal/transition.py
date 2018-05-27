import unittest

class test_runner:
    def __init__(self, states, transitions):
        self.states = {}
        for i in states:
            states[i.name] = i
            
        self.transitions = {}
        for i in transitions:
            states[i.name] = i

        # construct graph here

    def run():
        # walk through graph invoking the 'transition tests'
        return

class state:
    def __init__(self, name, state_def, prev_state=None):
        self.name = name
        self.state_definition = state_def
        self.prev_state = prev_state # this means this is an induction test. state is "N+1" regarding state "N"
        return

    def __call__(self, obj, prev_test):
        self.state_definition(obj)
        return

class trans:
    def __init__(self, name, trans_routine, before_state, after_state):
        self.name = name
        self.trans = trans_routine
        self.before = before_state
        self.after = after_state
        return

    def __call__(self, before):
        return self.trans(before)


# actual use case
import random

def s1_check(obj):
    assert len(obj) == 0 
    # etc... various assertions
    return

def s2_check(obj, prev): # this is an induction test
    assert len(obj) == len(prev) + 1
    assert prev[-1] == obj[-2]
    # etc... various assertions dependent on 'prev' state
    return

def t1_routine(obj):
    obj.append(random.random())
    return obj

s1 = state("initial state", s1_check)
s2 = state("state after append", s2_check, s1)
t1 = trans("append transition", t1_routine, s1, s2)

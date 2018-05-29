import inspect, networkx as nx

MAX_VISIT_PER_STATE = int(10)


class State(object):
    def __init__(self, tester, checker, description):
        self.tester = tester
        self.checker = checker
        self.description = description

        # Some python-internal-stuffs
        spec = inspect.getargspec(checker)
        argcount = len(spec.args)
        assert argcount in (1, 2)

        # TODO: add better way to get id (maybe description will work?)
        self.id = checker.__name__
        self.is_induction = argcount == 2
        self.outtrans = []

    def __call__(self, cur, prev=None):
        if self.is_induction:
            return self.checker(cur, prev)
        else:
            return self.checker(cur)

    def add_out(self, trans):
        self.outtrans.append(trans)

    def __repr__(self):
        return '<State %s (%r)>' % (self.id, self.description)


class Transition(object):
    def __init__(self, tester, transit, oldstate, newstate, arg_gen):
        self.tester = tester
        self.transit = transit
        self.oldstate = oldstate
        self.newstate = newstate
        self.arg_generator = arg_gen

        oldstate.add_out(self)
        # newstate.add_in(self)

    def __call__(self, old):
        if self.arg_generator != None:
            return self.transit(old, self.arg_generator())
        else:
            return self.transit(old)


class InitialState(object):
    def __init__(self, initializer, initial_state):
        self.initializer = initializer
        self.state = initial_state

    def __call__(self):
        return self.initializer()

class Tester(object):
    def __init__(self, cls):
        self.cls = cls
        self.results = self.succeeded = None
        self.entries = []

    def state(self, description):
        def handler(f):
            return State(tester=self, checker=f, description=description)
        return handler

    def trans(self, oldstate, newstate, arg_gen=None):
        def handler(f):
            return Transition(tester=self,
                              transit=f,
                              oldstate=oldstate,
                              newstate=newstate,
                              arg_gen=arg_gen)
        return handler

    def __clear_results(self):
        self.results = []
        self.succeeded = True

    # Some assert-related functions from 'unittest' module

    def assertEqual(self, a, b):
        self.__add_result(a == b)

    def assertTrue(self, a):
        self.__add_result(not not a)

    def assertFalse(self, a):
        self.__add_result(not a)

    def __add_result(self, result):
        # frame stuffs like line, ...
        frame = None
        # result stuffs
        self.results.append((frame, result))
        if not result:
            self.succeeded = False

    # Graph traverse using BFS
    # TODO: maybe DFS is more user-friendly?
    def run(self):
        # queue: List<Tuple<Class, State, Map<State, int>>>
        queue = []
        for entry in self.entries:
            queue.append((entry(), entry.state, dict()))
        while queue:
            obj, oldstate, visitCounts = queue.pop()
            curVisitCount = visitCounts.get(oldstate, 0)
            print('Running', oldstate)
            if curVisitCount >= MAX_VISIT_PER_STATE:
                print('Recursion limit exceeded: ...')
            else:
                for trans in oldstate.outtrans:
                    self.__clear_results()
                    newobj = trans(obj)
                    newVisitCounts = dict(visitCounts)
                    newVisitCounts[oldstate] = visitCounts.get(oldstate, 0) + 1
                    if self.succeeded:
                        queue.append((newobj, trans.newstate, newVisitCounts))
                    else:
                        print('Test failed: ...')

    def graph(self):
        G = nx.DiGraph()

        queue = []
        visited = set()
        for entry in self.entries:
            queue.append(entry.state)

        while queue:
            oldstate = queue.pop()
            if oldstate in visited:
                continue
            G.add_node(oldstate.id, oldstate.description)
            for trans in oldstate.outtrans:
                # trans.oldstate is oldstate
                G.add_edge(oldstate.id, trans.newstate)
                queue.append(trans.newstate)

        return G

    def entry(self, initial_state):
        def handler(f):
            self.entries.append(
                InitialState(initializer=f,
                             initial_state=initial_state))

        return handler

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        pass

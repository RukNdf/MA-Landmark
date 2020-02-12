from copy import deepcopy
from itertools import chain, combinations
from .action import Action
from .state import applicable, apply

def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


class Problem():
    def __init__(self, initial_state, goal_state):
        self.initial_state = initial_state
        self.goal_state = goal_state


class Domain():

    def __init__(self,actions):
        self.ss = None
        self.actions = {}
        for action in actions:
            self.actions[action.name] = action

    @property
    def all_facts(self):
        all_facts = set([fact for op in self.actions.values() for fact in op.all_facts()])
        return all_facts

    @property
    def state_space(self):
        if self.ss is None:
            self.ss = [s for s in self.generate_state_space()]
        return self.ss

    def generate_state_space(self):
        return powerset(self.all_facts)

    def groundify(self):
        return Domain([action.groundify() for action in self.actions.values()])

    def __iter__(self):
        return iter(self.actions.values())

    def __getitem__(self, item):
        return self.actions[item]

    def __setitem__(self, key, value):
        self.actions[key] = value
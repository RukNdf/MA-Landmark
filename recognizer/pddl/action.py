#!/usr/bin/env python
# Four spaces as indentation [no tabs]

import itertools

from .state import applicable, apply

class Action:

    def __init__(self, name, parameters, positive_preconditions, negative_preconditions, add_effects, del_effects, cost = 0):
        self.name = name
        self.parameters = parameters
        self.positive_preconditions = frozenset(positive_preconditions)
        self.negative_preconditions = frozenset(negative_preconditions)
        self.add_effects = frozenset(add_effects)
        self.del_effects = frozenset(del_effects)
        self.cost = cost

    def __repr__(self):
        return "<" + self.name + "," + str(self.parameters) + "," + str(self.positive_preconditions) + "," + str(
            self.negative_preconditions) + \
               "," + str(self.add_effects) + "," + str(self.del_effects) + "," + str(self.cost) + ">"

    def __str__(self):
        return 'action: ' + self.name + \
            '\n  parameters: ' + str(self.parameters) + \
            '\n  positive_preconditions: ' + str(list(self.positive_preconditions)) + \
            '\n  negative_preconditions: ' + str(list(self.negative_preconditions)) + \
            '\n  add_effects: ' + str(list(self.add_effects)) + \
            '\n  del_effects: ' + str(list(self.del_effects)) + '\n'

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def all_facts(self):
        facts = []
        # TODO we need to change this to separate ground from lifted operators, now I'm assuming it's propositional
        # facts += [str(prop) for prop in self.positive_preconditions]
        # facts += [str(prop) for prop in self.negative_preconditions]
        # facts += [str(prop) for prop in self.add_effects]
        # facts += [str(prop) for prop in self.del_effects]
        facts += self.positive_preconditions
        facts += self.negative_preconditions
        facts += self.add_effects
        facts += self.del_effects
        return set(facts)

    def applicable(self, state):
        return applicable(state, self.positive_preconditions, self.negative_preconditions)

    def groundify(self, objects):
        if not self.parameters:
            yield self
            return
        type_map = []
        variables = []
        for var, type in self.parameters:
            type_map.append(objects[type])
            variables.append(var)
        for assignment in itertools.product(*type_map):
            positive_preconditions = self.replace(self.positive_preconditions, variables, assignment)
            negative_preconditions = self.replace(self.negative_preconditions, variables, assignment)
            add_effects = self.replace(self.add_effects, variables, assignment)
            del_effects = self.replace(self.del_effects, variables, assignment)
            yield Action(self.name, assignment, positive_preconditions, negative_preconditions, add_effects, del_effects)

    def replace(self, group, variables, assignment):
        g = []
        for pred in group:
            a = pred
            iv = 0
            for v in variables:
                while v in a:
                    i = a.index(v)
                    a = a[:i] + tuple([assignment[iv]]) + a[i+1:]
                iv += 1
            g.append(a)
        return frozenset(g)

if __name__ == '__main__':
    a = Action('move', [['?ag', 'agent'], ['?from', 'pos'], ['?to', 'pos']],
        frozenset([tuple(['at', '?ag', '?from']), tuple(['adjacent', '?from', '?to'])]),
        frozenset([tuple(['at', '?ag', '?to'])]),
        frozenset([tuple(['at', '?ag', '?to'])]),
        frozenset([tuple(['at', '?ag', '?from'])])
    )
    print(a)

    objects = {
        'agent': ['ana','bob'],
        'pos': ['p1','p2']
    }
    for act in a.groundify(objects):
        print(act)
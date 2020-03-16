#!/usr/bin/env python
# Four spaces as indentation [no tabs]
#
#  pddl_parser.py
#  ma-goal-recognition
#
#  Created by Felipe Meneguzzi on 2020-03-12.
#  Copyright 2020 Felipe Meneguzzi. All rights reserved.
#


import re
from recognizer.pddl.action import Action


def string_to_fluent(sfluent):
    """Converts a string sfluent into a tuple """
    return tuple(tok.strip() for tok in sfluent.split(' '))


class PDDL_Parser:

    SUPPORTED_REQUIREMENTS = [':strips', ':negative-preconditions', ':typing', ':equality']

    # ------------------------------------------
    # Tokens
    # ------------------------------------------

    def __init__(self):
        self.domain_name = None
        self.actions = []
        self.types = dict()  # Types are a dictionary indicating parent type
        self.objects = dict()
        self.state = frozenset()
        self.positive_goals = frozenset()
        self.negative_goals = frozenset()
        self.predicates = dict()  # We store predicates with their names and arities

    def scan_tokens(self, filename):
        with open(filename,'r') as f:
            # Remove single line comments
            str = re.sub(r';.*$', '', f.read(), flags=re.MULTILINE).lower()
        # Tokenize
        stack = []
        tokens = []
        for t in re.findall(r'[()]|[^\s()]+', str):
            if t == '(':
                stack.append(tokens)
                tokens = []
            elif t == ')':
                if stack:
                    l = tokens
                    tokens = stack.pop()
                    tokens.append(l)
                else:
                    raise Exception('Missing open parentheses')
            else:
                tokens.append(t)
        if stack:
            raise Exception('Missing close parentheses')
        if len(tokens) != 1:
            raise Exception('Malformed expression')
        return tokens[0]

    #-----------------------------------------------
    # Parse domain
    #-----------------------------------------------

    def parse_domain(self, domain_filename):
        tokens = self.scan_tokens(domain_filename)
        if type(tokens) is list and tokens.pop(0) == 'define':
            self.domain_name = 'unknown'
            self.actions = []
            while tokens:
                group = tokens.pop(0)
                t = group.pop(0)
                if   t == 'domain':
                    self.domain_name = group[0]
                elif t == ':requirements':
                    for req in group:
                        if not req in self.SUPPORTED_REQUIREMENTS:
                            raise Exception('Requirement ' + req + ' not supported')
                    self.requirements = group
                elif t == ':predicates':
                    self.parse_predicates(group)
                elif t == ':types':
                    self.types = group
                elif t == ':action':
                    self.parse_action(group)
                else: print(str(t) + ' is not recognized in domain')
        else:
            raise Exception('File ' + domain_filename + ' does not match domain pattern')

    #-----------------------------------------------
    # Parse predicates
    #-----------------------------------------------

    def parse_predicates(self, group):
        for pred in group:
            predicate_name = pred.pop(0)
            if predicate_name in self.predicates:
                raise Exception('Predicate ' + predicate_name + ' redefined')
            arguments = {}
            untyped_variables = []
            while pred:
                t = pred.pop(0)
                if t == '-':
                    if not untyped_variables:
                        raise Exception('Unexpected hyphen in predicates')
                    type = pred.pop(0)
                    while untyped_variables:
                        arguments[untyped_variables.pop(0)] = type
                else:
                    untyped_variables.append(t)
            while untyped_variables:
                arguments[untyped_variables.pop(0)] = 'object'
            self.predicates[predicate_name] = arguments

    #-----------------------------------------------
    # Parse action
    #-----------------------------------------------

    def parse_action(self, group):
        name = group.pop(0)
        if not type(name) is str:
            raise Exception('Action without name definition')
        for act in self.actions:
            if act.name == name:
                raise Exception('Action ' + name + ' redefined')
        parameters = []
        positive_preconditions = []
        negative_preconditions = []
        add_effects = []
        del_effects = []
        while group:
            t = group.pop(0)
            if t == ':parameters':
                if not type(group) is list:
                    raise Exception('Error with ' + name + ' parameters')
                parameters = []
                untyped_parameters = []
                p = group.pop(0)
                while p:
                    t = p.pop(0)
                    if t == '-':
                        if not untyped_parameters:
                            raise Exception('Unexpected hyphen in ' + name + ' parameters')
                        ptype = p.pop(0)
                        while untyped_parameters:
                            parameters.append([untyped_parameters.pop(0), ptype])
                    else:
                        untyped_parameters.append(t)
                while untyped_parameters:
                    parameters.append([untyped_parameters.pop(0), 'object'])
            elif t == ':precondition':
                self.split_predicates(group.pop(0), positive_preconditions, negative_preconditions, name, ' preconditions')
            elif t == ':effect':
                self.split_predicates(group.pop(0), add_effects, del_effects, name, ' effects')
            else: print(str(t) + ' is not recognized in action')
        self.actions.append(Action(name, parameters, frozenset(positive_preconditions), frozenset(negative_preconditions), frozenset(add_effects), frozenset(del_effects)))

    # -----------------------------------------------
    # Parse problem
    # -----------------------------------------------

    def parse_problem(self, problem_filename):
        tokens = self.scan_tokens(problem_filename)
        if type(tokens) is list and tokens.pop(0) == 'define':
            self.problem_name = 'unknown'
            self.objects = dict()
            self.state = frozenset()
            self.positive_goals = frozenset()
            self.negative_goals = frozenset()
            while tokens:
                group = tokens.pop(0)
                t = group[0]
                if   t == 'problem':
                    self.problem_name = group[-1]
                elif t == ':domain':
                    if self.domain_name != group[-1]:
                        raise Exception('Different domain specified in problem file')
                elif t == ':requirements':
                    pass # TODO
                elif t == ':objects':
                    group.pop(0)
                    object_list = []
                    while group:
                        if group[0] == '-':
                            group.pop(0)
                            self.objects[group.pop(0)] = object_list
                            object_list = []
                        else:
                            object_list.append(group.pop(0))
                    if object_list:
                        if 'object' not in self.objects:
                            self.objects['object'] = []
                        self.objects['object'] += object_list
                elif t == ':init':
                    group.pop(0)
                    self.state = self.state_to_tuple(group)
                elif t == ':goal':
                    pos = []
                    neg = []
                    self.split_predicates(group[1], pos, neg, '', 'goals')
                    self.positive_goals = frozenset(pos)
                    self.negative_goals = frozenset(neg)
                else: print(str(t) + ' is not recognized in problem')
        else:
            raise Exception('File ' + problem_filename + ' does not match problem pattern')

    # -----------------------------------------------
    # State to tuple
    # -----------------------------------------------

    def state_to_tuple(self, state):
        return frozenset(tuple(fact) for fact in state)

    def string_to_predicates(self, pred_string):
        pred_string = pred_string.strip()
        pred_string = pred_string[1:-1]

        return tuple(pred_string.split(' '))

    # -----------------------------------------------
    # Split propositions
    # -----------------------------------------------

    def split_predicates(self, group, pos, neg, name, part):
        if not type(group) is list:
            raise Exception('Error with ' + name + part)
        if group[0] == 'and':
            group.pop(0)
        else:
            group = [group]
        for predicate in group:
            if predicate[0] == 'not':
                if len(predicate) != 2:
                    raise Exception('Unexpected not in ' + name + part)
                neg.append(tuple(predicate[-1]))
            else:
                pos.append(tuple(predicate))

# ==========================================
# Main
# ==========================================


if __name__ == '__main__':
    import sys
    import pprint
    domain = sys.argv[1]
    problem = sys.argv[2]
    parser = PDDL_Parser()
    print('----------------------------')
    pprint.pprint(parser.scan_tokens(domain))
    print('----------------------------')
    pprint.pprint(parser.scan_tokens(problem))
    print('----------------------------')
    parser.parse_domain(domain)
    parser.parse_problem(problem)
    print('Domain name: ' + parser.domain_name)
    for act in parser.actions:
        print(act)
    print('----------------------------')
    print('Problem name: ' + parser.problem_name)
    print('Objects: ' + str(parser.objects))
    print('State: ' + str(parser.state))
    print('Positive goals: ' + str(parser.positive_goals))
    print('Negative goals: ' + str(parser.negative_goals))
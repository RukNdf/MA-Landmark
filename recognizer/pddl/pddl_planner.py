#!/usr/bin/env python
#
#  pddl_planner.py
#  ma-goal-recognition
#
#  Created by Felipe Meneguzzi on 2020-03-12.
#  Copyright 2020 Felipe Meneguzzi. All rights reserved.
#


from recognizer.pddl.pddl_parser import PDDL_Parser
from recognizer.pddl.state import applicable, apply
import time


class PDDL_Planner:

    def __init__(self, verbose=False):
        self.verbose = verbose

    def applicable(self, state, positive, negative):
        return applicable(state, positive, negative)

    def apply(self, state, positive, negative):
        return apply(state, positive, negative)

    def solvable(self, domain, initial_state, goal_state):
        """"Computes whether the problem posed by initial_state, goal_state is solvable by reachability analysis"""
        last_state = set([])
        reachable_literals = set(initial_state)
        positive_goals = set(goal_state[0])
        actions = domain

        positive_effects = set([])
        negative_effects = set([])
        for a in actions:
            positive_effects = positive_effects.union(set(a.add_effects))
            negative_effects = negative_effects.union(set(a.del_effects))
        # First check the obvious stuff
        for p in goal_state[0]:
            if p not in reachable_literals and p not in positive_effects:
                return False
        for p in goal_state[1]:
            if p in reachable_literals and p not in negative_effects:
                return False

        while last_state != reachable_literals:
            last_state = reachable_literals.copy()
            if positive_goals.issubset(reachable_literals):
                return True
            for a in actions:
                if a.applicable(reachable_literals):
                    reachable_literals = reachable_literals.union(a.add_effects)

        return False

    #-----------------------------------------------
    # Solve
    #-----------------------------------------------

    def solve_file(self, domainfile, problemfile, verbose=False):
        # Parser
        start_time = time.time()
        parser = self.parse(domainfile,problemfile)
        # Test if first state is not the goal
        if applicable(parser.state, parser.positive_goals, parser.negative_goals):
            return [], 0
        # Grounding process
        ground_actions = self.grounding(parser)
        plan = self.solve(ground_actions, parser.state, (parser.positive_goals, parser.negative_goals))
        final_time = time.time() - start_time
        if verbose:
            print('Time: ' + str(final_time) + 's')
            if plan:
                print('plan:')
                for act in plan:
                    print('(' + act.name + ''.join(' ' + p for p in act.parameters) + ')')
            else:
                print('No plan was found')
        return plan, final_time

    def parse(self, domainfile, problemfile):
        if self.verbose: print("Parsing %s and %s" % (domainfile,problemfile))
        parser = PDDL_Parser()
        parser.parse_domain(domainfile)
        parser.parse_problem(problemfile)
        return parser

    def grounding(self, parser):
        ground_actions = []
        start_time = time.time()
        for action in parser.actions:
            for act in action.groundify(parser.objects):
                ground_actions.append(act)

        final_time = time.time() - start_time
        if self.verbose:
            print("Grounding time: %d s" % final_time)
            print("Number of actions: %d" % len(ground_actions))
        return ground_actions

    def solve(self, domain, initial_state, goals):
        raise NotImplementedError("PDDL Planners need to implement solve")
#!/usr/bin/env python
# Four spaces as indentation [no tabs]
#
#  sat_planner.py
#  ma-goal-recognition
#
#  Created by Felipe Meneguzzi on 2020-03-12.
#  Copyright 2020 Felipe Meneguzzi. All rights reserved.
#


from itertools import combinations

# from z3 import *
from z3 import Solver, And, Or, Not, Implies, sat, Bool, simplify, With, Tactic, Then

from recognizer.pddl.domain import Domain
from recognizer.pddl.pddl_planner import PDDL_Planner


class SATPlanner(PDDL_Planner):

    def __init__(self, allow_parallel_actions=False, verbose=False, simplify=False):
        super().__init__(verbose)
        self.props = dict()
        self.action_map = dict()
        self.max_length = 20
        self.verbose = verbose
        self.allow_parallel_actions = allow_parallel_actions
        self.action_mutexes = dict()
        self.simplify = simplify

    def solve(self, actions, initial_state, goal_state):
        """Solves the planning problem given the elements of the problem
        """
        # encode the problem
        for length in range(0, self.max_length):
            if self.simplify:
                # s = Then('sat-preprocess', 'psmt').solver()
                # s = With('psmt').solver()
                # s = Then('aig', 'elim-and','psmt').solver()
                # s = Then('aig', 'psmt').solver()
                # s = Then('simplify', 'propagate-values', 'ctx-simplify').solver()
                s = Then('simplify', 'propagate-values', 'psmt').solver()
            else:
                s = Solver()
            self.props.clear()
            self.action_map.clear()
            print("Encoding domain with length {0}".format(length))
            self.encode_formula(s, actions, initial_state, goal_state, length)
            if self.verbose: print(s.to_smt2())
            # print(s)
            if s.check() == sat:
                if self.verbose: print("Model found with length {0}".format(length))
                # print(s.model())
                return self.extract_plan(s.model(), length)
            else:
                if self.verbose: print("No model found with length {0}".format(length))
        return None

    def extract_plan(self, model, length):
        extracted_plan = []
        for prop in model:
            if prop.name() in self.action_map.keys() and model[prop]:
                # print("Adding "+prop.name())
                (action, index) = self.action_map[prop.name()]
                extracted_plan.append(action)
        return extracted_plan

    def encode_formula(self, s, actions, initial_state, goal_state, plan_length):
        # Parsed data
        domain = Domain(actions)
        preds = domain.all_facts
        goal_pos = goal_state[0]
        goal_not = goal_state[1]
        # Compute Mutexes
        if self.allow_parallel_actions: self.compute_action_mutexes(actions)

        # Encode initial state
        s0_formula = []
        # for pred in initial_state:
        #     s0_formula.append(self.prop_at(pred,0))
        for pred in preds:
            if pred in initial_state:
                s0_formula.append(self.prop_at(pred, 0))
            else:
                s0_formula.append(Not(self.prop_at(pred, 0)))
        s0_formula = And(*s0_formula)

        # Encode goal state
        goal_formula = []
        for pred in goal_pos:
            goal_formula.append(self.prop_at(pred, plan_length))

        for pred in goal_not:
            goal_formula.append(Not(self.prop_at(pred, plan_length)))

        if goal_formula:
            goal_formula = And(*goal_formula)
        else:
            if self.verbose: print("Warning: empty goal formula")

        action_formula = []
        exclusion_axiom = []
        frame_axioms = []

        for i in range(0, plan_length+1):
            for p in preds:
                self.prop_at(p, i)

        for i in range(0, plan_length):
            for a in actions:
                self.action_prop_at(a, i)

        full_frame_axioms = []  # This is to ensure at least one action is present at every time
        #  encode stuff over the length of the plan
        for i in range(0, plan_length):
            action_names = []
            action_propositions = dict()
            # Encode actions
            for action in actions:
                action_prop = self.action_prop_at(action, i)
                action_names.append(action_prop)
                action_propositions[action_prop] = action
                action_formula.append(self.action(action, i))

            # Encode full frame axiom
            full_frame_axioms.append(Or(*action_names))

            # Encode exclusion axioms
            for (a1, a2) in combinations(action_names, 2):
                if self.allow_parallel_actions:
                    if action_propositions[a2] in self.action_mutexes[action_propositions[a1]]:
                        exclusion_axiom.append(Or(Not(a1), Not(a2)))
                else:
                    exclusion_axiom.append(Or(Not(a1), Not(a2)))

            # Encode frame axioms (explanatory frame actions)
            for p in preds:
                add_eff_actions = []
                del_eff_actions = []
                for a in actions:
                    if p in a.add_effects:
                        add_eff_actions.append(a)
                    if p in a.del_effects:
                        del_eff_actions.append(a)

                ant = And(Not(self.prop_at(p, i)), self.prop_at(p, i+1))
                cons = []
                for a in add_eff_actions:
                    cons.append(self.action_prop_at(a, i))
                cons = Or(*cons)
                frame_axioms.append(Implies(ant, cons))

                ant = And(self.prop_at(p, i), Not(self.prop_at(p, i+1)))
                cons = []
                for a in del_eff_actions:
                    cons.append(self.action_prop_at(a, i))
                if cons:
                    cons = Or(*cons)
                    frame_axioms.append(Implies(ant, cons))

        if not exclusion_axiom and self.verbose: print('Warning: empty exclusion axiom')
        if not frame_axioms and self.verbose: print('Warning: empty frame axiom')

        s.add(s0_formula)
        s.add(goal_formula)
        s.add(And(*action_formula))
        s.add(And(*full_frame_axioms))
        s.add(And(*exclusion_axiom))
        s.add(And(*frame_axioms))

    def action(self, action, t):

        ant = self.action_prop_at(action, t)
        precond = []
        for pred in action.positive_preconditions:
            precond.append(self.prop_at(pred, t))
        for pred in action.negative_preconditions:
            precond.append(Not(self.prop_at(pred, t)))

        effect = []
        for pred in action.add_effects:
            effect.append(self.prop_at(pred, t+1))
        for pred in action.del_effects:
            effect.append(Not(self.prop_at(pred, t+1)))

        cons = And(And(*precond), And(*effect))

        st = Implies(ant, cons)
        return st

    def action_prop_at(self, action, t):
        prop = self.prop_at((action.name, action.parameters), t)
        self.action_map[prop.decl().name()] = (action, t)
        return prop

    def prop_at(self, prop, t):
        st = ""
        for term in prop:
            st += str(term)+"_"
        key = st+str(t)
        if key not in self.props:
            p = Bool(key)
            self.props[key] = p

        return self.props[key]

    def compute_action_mutexes(self, actions):
        self.action_mutexes = dict()
        for action in actions:
            self.action_mutexes[action] = set([])
        for (a1, a2) in combinations(actions, 2):
            if a1.is_mutex(a2):
                self.action_mutexes[a1].add(a2)

# ==========================================
# Main
# ==========================================


if __name__ == '__main__':
    import sys
    domain = sys.argv[1]
    problem = sys.argv[2]
    planner = SATPlanner(allow_parallel_actions=True, verbose=False)
    plan = planner.solve_file(domain, problem)
    if plan:
        print('plan:')
        for act in plan:
            # print('(' + act.name + ''.join(' ' + p for p in act.parameters) + ')')
            print(act)
    else:
        print('No plan was found')

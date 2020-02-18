from recognizer import problem
from recognizer.pddl.sat_planner import SATPlanner
import sys, os, csv, time, math


class PlannerInterface:

    def __init__(self, domain, problem, max_time=120, max_mem=2048):
        self.domain = domain
        self.problem = problem
        self.noext_problem = os.path.basename(self.problem).replace('.pddl', '')
        self.max_time = max_time
        self.max_mem = max_mem

    def execute(self, observations):
        raise NotImplementedError("PlannerInterface implementations need to implement execute")

from z3 import Solver, And, Or, Not, Implies, sat, Bool

class SATPlannerInterface(PlannerInterface):

    def __init__(self, domain, problem, max_time=120, max_mem=2048, max_length=50, verbose=False):
        super().__init__(domain, problem, max_time, max_mem)
        self.verbose = verbose
        self.sat_planner = SATPlanner(allow_parallel_actions=True, verbose=verbose)
        self.max_length = max_length

    def execute(self, observations=None):
        parser = self.sat_planner.parse(self.domain,self.problem)
        ground_actions = self.sat_planner.grounding(parser)

        for length in range(0, self.max_length):
            s3solver = Solver()
            print("Encoding domain with length {0}".format(length))
            self.sat_planner.encode_formula(s3solver, ground_actions, parser.state,
                                            (parser.positive_goals, parser.negative_goals),
                                            length)
            if observations is not None:  # Add formulas for observations
                if self.verbose: print("Encoding axioms for observations %s"%observations)
                observation_atoms = [parser.string_to_predicates(obs) for obs in observations]
                # FIXME Figure out how to encode this

            if s3solver.check() == sat:
                plan = self.sat_planner.extract_plan(s3solver.model(), length)
                return plan

        return None

from recognizer.plan_recognizer import PlanRecognizer
from recognizer.pddl.pddl_parser import PDDL_Parser
from recognizer.pddl.pddl_planner import applicable
from recognizer.pddl.sat_planner import SATPlanner
from z3 import Solver, And, Or, Not, Implies, sat, Bool, Sort, Const, Function, IntSort, BoolSort, ForAll, Var, Int, DeclareSort


class SATPlanRecognizer(PlanRecognizer):

    name = "sat"

    def __init__(self, options=None):#TODO Refactor Options part of the program to make it simpler
        PlanRecognizer.__init__(self,options)

    def accept_hypothesis(self, h):
        return not h.test_failed and h.cost == self.unique_goal.cost

    def add_observation_constraints(self, s, planner, ground_actions, length, observations):
        obsSort = DeclareSort('Obs')
        orderObs = Function('orderObs', obsSort, IntSort())
        orderExec = Function('orderExec', obsSort, IntSort())
        obsConsts = []
        for i in range(0, len(observations)):
            o = Const(str(observations[i]), obsSort)
            obsConsts.append(o)
            s.add(orderObs(o) == i)

        for t in range(0, length):
            # forced_obs = []
            for action in ground_actions:
                index = observations.index_of(action.signature())
                if index > -1:
                    obsC = obsConsts[index]
                    # forced_obs.append(planner.action_prop_at(action, t))
                    s.add(Implies(planner.action_prop_at(action, t), orderExec(obsC) == t))
            # s.add(Or(*forced_obs))

        x = Const('x', obsSort)
        y = Const('y', obsSort)
        # orderSync = Function('order-sync', BoolSort())
        s.add(ForAll([x, y], Implies(orderObs(x) < orderObs(y), orderExec(x) < orderExec(y))))
        s.add(ForAll([x, y], Implies(orderObs(x) == orderObs(y), orderExec(x) == orderExec(y))))
        s.add(ForAll([x, y], Implies(orderObs(x) > orderObs(y), orderExec(x) > orderExec(y))))

    def evaluate_hypothesis(self, index, hypothesis, observations):
        hyp_problem = self.options.work_dir + 'hyp_%d_problem.pddl' % index
        domain_file = self.options.work_dir+self.options.domain_name+'.pddl'
        # domain_file = 'examples/blocksworld/blocksworld.pddl'
        hypothesis.generate_pddl_for_hyp_plan(hyp_problem)
        planner = SATPlanner(allow_parallel_actions=True, verbose=True)
        planner.max_length = 15

        parser = planner.parse(domain_file, hyp_problem)
        if applicable(parser.state, parser.positive_goals, parser.negative_goals):
            hypothesis.cost = 0
        # Grounding process
        ground_actions = planner.grounding(parser)
        for length in range(0, planner.max_length):
            s = Solver()
            planner.props.clear()
            planner.action_map.clear()
            # if self.options.verbose: print("Encoding domain with length {0}".format(length))
            planner.encode_formula(s, ground_actions, parser.state, (parser.positive_goals, parser.negative_goals), length)
            # Add the constraints for the observations
            self.add_observation_constraints(s, planner, ground_actions, length, observations)

            # if self.options.verbose: print(s.to_smt2())
            if s.check() == sat:
                if self.options.verbose: print("Model found with length {0}".format(length))
                plan = planner.extract_plan(s.model(),length)
                if self.options.verbose: print("Plan %d is %s"%(len(plan),plan))
                hypothesis.cost = len(plan)
                return plan
            else:
                if self.options.verbose: print("No model found with length {0}".format(length))

    def run_recognizer(self):
        for i in range(0, len(self.hyps)):
            if self.options.verbose: print("Evaluating hypothesis %d: %s"%(i,str(self.hyps[i])))
            self.evaluate_hypothesis(i, self.hyps[i], self.observations)

        for h in self.hyps:
            if not h.test_failed:
                if not self.unique_goal or h.cost < self.unique_goal.cost:
                    self.unique_goal = h

        # Select unique goal (choose the goal with the minimal score)
        for h in self.hyps:
            if self.accept_hypothesis(h):
                self.accepted_hypotheses.append(h)

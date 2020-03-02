from recognizer.plan_recognizer import PlanRecognizer
from recognizer.pddl.sat_planner import SATPlanner
from recognizer.pddl.pddl_parser import PDDL_Parser


class SATPlanRecognizer(PlanRecognizer):

    name = "sat"

    def __init__(self, options=None):#TODO Refactor Options part of the program to make it simpler
        PlanRecognizer.__init__(self,options)

    def accept_hypothesis(self, h):
        if not h.test_failed:
            return h # Still needs to work on this
        return False

    def run_recognizer(self):
        # FIXME Just forced some agents in the hypothesis to get it to test
        for i in range(0, len(self.hyps)):
            self.hyps[i].team = frozenset(['ag1'])
            # FIXME - Refactor this thoroughly
            # self.hyps[i].evaluate(i, self.observations)
            hyp_problem = self.options.work_dir + 'hyp_%d_problem.pddl' % i
            self.hyps[i].generate_pddl_for_hyp_plan(hyp_problem)
            planner = SATPlanner(allow_parallel_actions=True,verbose=True)
            planner.solve_file('examples/blocksworld/ma-blocksworld.pddl',hyp_problem)

        for h in self.hyps:
            if not h.test_failed:
                if not self.unique_goal or h.score < self.unique_goal.score:
                    self.unique_goal = h

        # Select unique goal (choose the goal with the minimal score)
        for h in self.hyps:
            if self.accept_hypothesis(h):
                self.accepted_hypotheses.append(h)



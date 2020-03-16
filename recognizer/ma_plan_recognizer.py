from recognizer.plan_recognizer import PlanRecognizer, TeamPlanRecognizer
from recognizer.pddl.sat_planner import SATPlanner
from recognizer.sat_plan_recognizer import SATPlanRecognizer
from recognizer.pddl.pddl_parser import PDDL_Parser
from itertools import chain, combinations

def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


class SATTeamPlanRecognizer(TeamPlanRecognizer):

    name = "team-sat"

    def __init__(self, options=None):#TODO Refactor Options part of the program to make it simpler
        PlanRecognizer.__init__(self,options)
        self.recognizer = SATPlanRecognizer(options)

    def accept_hypothesis(self, h):
        return not h.test_failed and h.cost == self.unique_goal.cost

    def run_recognizer(self):
        # FIXME Just forced some agents in the hypothesis to get it to test
        agents = ['ag1', 'ag2', 'ag3']
        for i in range(0, len(self.hyps)):
            # self.hyps[i].team = frozenset(['ag1'])
            for team in powerset(agents):
                if len(team) == 0: continue
                self.hyps[i].team = frozenset(team)
                if self.options.verbose: print("Testing hypothesis %s" % self.hyps[i])
                self.recognizer.evaluate_hypothesis(i, self.hyps[i], self.observations)

        for h in self.hyps:
            if not h.test_failed:
                if not self.unique_goal or h.cost < self.unique_goal.cost:
                    self.unique_goal = h

        # Select unique goal (choose the goal with the minimal cost)
        for h in self.hyps:
            if self.accept_hypothesis(h):
                self.accepted_hypotheses.append(h)



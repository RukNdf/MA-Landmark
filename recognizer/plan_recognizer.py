#!/usr/bin/env python3
#
#  plan_recognizer.py
#  ma-goal-recognition
#
#  Created by Felipe Meneguzzi on 2020-03-12.
#  Copyright 2020 Felipe Meneguzzi. All rights reserved.
#


from recognizer.planner_interface import PlannerInterface
from recognizer.problem import Observations, Hypothesis, TeamHypothesis


class PlanRecognizer:
    name = None

    def __init__(self, options):
        self.options = options
        self.observations = Observations(options.work_dir+'ma-obs.dat')
        self.hyps = self.load_hypotheses('hyps.dat')
        self.unique_goal = None
        self.accepted_hypotheses = []

    def load_hypotheses(self, hyp_files = 'hyps.dat'):
        return Hypothesis.load_hypotheses(hyp_files, work_dir=self.options.work_dir)

    def get_real_hypothesis(self):
        for h in self.hyps:
            if h.is_true:
                realHyp = h
                return realHyp

    def write_report(self, experiment, hyps):
        outstream = open('report.txt', 'w')

        # print(s,end="", file=outstream)
        print("Experiment=%s" % experiment, file=outstream)
        print("Num_Hyp=%d" % len(hyps), file=outstream)
        for hyp in hyps:
            print("Hyp_Atoms=%s" % ",".join(hyp.atoms), file=outstream)
            if hyp.test_failed:
                print("Hyp_Score=unknown", file=outstream)
                print("Hyp_Plan_Len=unknown", file=outstream)
            else:
                print("Hyp_Score=%f" % hyp.score, file=outstream)
                print("Hyp_Plan_Len=%d" % len(hyp.plan), file=outstream)
            print("Hyp_Trans_Time=%f" % hyp.trans_time, file=outstream)
            print("Hyp_Plan_Time=%f" % hyp.plan_time, file=outstream)
            print("Hyp_Test_Time=%f" % hyp.total_time, file=outstream)
            print("Hyp_Is_True=%s" % hyp.is_true, file=outstream)

        outstream.close()
        print((max(hyps)))

    def run_recognizer(self):
        # return None
        raise NotImplementedError("You need to implement your method to run the recognizer")

    def accept_hypothesis(self, h):
        """ Tests whether or not to accept hypothesis h as a likely one, under an unc uncertainty in the range [1,2]"""
        # TODO I still need to refactor this function to something more elegant in terms of how we access it
        # return None
        raise NotImplementedError("You need to implement your method to run the recognizer")


class TeamPlanRecognizer(PlanRecognizer):

    def __init__(self,options):
        PlanRecognizer.__init__(self, options)

    def load_hypotheses(self, hyp_files = 'hyps.dat'):
        return TeamHypothesis.load_hypotheses(hyp_files, work_dir=self.options.work_dir)
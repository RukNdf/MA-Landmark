#!/usr/bin/env python
#
#  benchmark.py
#  ma-goal-recognition
#
#  Created by Felipe Meneguzzi on 2020-03-12.
#  Copyright 2020 Felipe Meneguzzi. All rights reserved.
#
from recognizer.ma_plan_recognizer import SATTeamPlanRecognizer
from recognizer.sat_plan_recognizer import SATPlanRecognizer
from recognizer.plan_recognizer_factory import PlanRecognizerFactory

from recognizer.options import ProgramOptions

import sys
import time


class Experiment:
    def __init__(self, recognizer_name):
        self.unique_correct = 0
        self.multi_correct = 0
        self.multi_spread  = 0
        self.candidate_goals = 0
        self.recognizer_name = recognizer_name
        self.totalTime = 0

    def reset(self):
        self.unique_correct = 0
        self.multi_correct = 0
        self.multi_spread  = 0
        self.candidate_goals = 0
        self.totalTime = 0

    def run_experiment(self, options):
        # print(self.recognizer_name)
        recognizer = PlanRecognizerFactory(options).get_recognizer(self.recognizer_name, options)

        startTime = time.time()
        recognizer.run_recognizer()
        experimentTime = time.time() - startTime
        self.totalTime += experimentTime

        if recognizer.unique_goal is not None and recognizer.get_real_hypothesis() == recognizer.unique_goal:
            self.unique_correct = self.unique_correct + 1
        if recognizer.get_real_hypothesis() in recognizer.accepted_hypotheses:
            self.multi_correct = self.multi_correct + 1
        self.multi_spread = self.multi_spread  + len(recognizer.accepted_hypotheses)
        self.candidate_goals = self.candidate_goals + len(recognizer.hyps)
        return recognizer.unique_goal is not None

    def __repr__(self):
        return "UC=%d MC=%d MS=%d CG=%d"%(self.unique_correct,self.multi_correct,self.multi_spread,self.candidate_goals)


class RecognizerBenchmark:

    def __init__(self, options):
        self.failed_experiments = []
        self.experiment_names = []
        self.experiments = {}

    def run_benchmark(self):
        pass

    def compute_states(self):
        pass


if __name__ == '__main__':
    print(sys.argv)
    options = ProgramOptions(sys.argv[1:])
    benchmark = RecognizerBenchmark(options)
    benchmark.run_benchmark()

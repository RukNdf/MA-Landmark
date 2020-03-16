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

from recognizer.options import ProgramOptions, Options

import sys
import time
import os


def progress(count, total, status=''):
    bar_len = 30
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

## Or
# def update_progress(progress):
#     print('\r[{0}] {1}%'.format('#'*(progress/10), progress))


class Experiment:
    """ A single experiment for one recognizer"""
    def __init__(self, recognizer_name):
        self.observability = None
        self.unique_correct = 0
        self.multi_correct = 0
        self.multi_spread  = 0
        self.candidate_goals = 0
        self.recognizer_name = recognizer_name
        self.problems = 0
        self.totalTime = 0

    def reset(self):
        self.observability = None
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

    def compute_stats(self):
        # TODO change this to pandas
        truePositives = float(self.multi_correct)
        trueNegatives = float(self.candidate_goals - self.multi_spread)
        falsePositives = float(self.multi_spread - self.multi_correct)
        falseNegatives = float(self.candidate_goals - self.multi_correct)
        print("TP=%2.4f TN=%2.4f FP=%2.4f FN=%2.4f MSpread=%2.4f"%(truePositives,trueNegatives,falsePositives,falseNegatives,self.multi_spread))

        accuracy = float(self.multi_correct)/float(self.problems)
        precision = truePositives / float(self.multi_spread) if self.multi_spread != 0 else 0
        recall = truePositives/float(self.problems)
        if precision + recall == 0:
            f1score = 0
        else:
            f1score = 2 * ((precision * recall) / (precision + recall))

        fallout = falsePositives / (trueNegatives + falsePositives)
        missrate = falseNegatives / (falseNegatives + truePositives)
        avgGoals = self.multi_spread/self.problems
        avgTime = self.totalTime/self.problems

        return accuracy, precision, recall, f1score, fallout, missrate, avgGoals, avgTime

    def __repr__(self):
        return "UC=%d MC=%d MS=%d CG=%d"%(self.unique_correct,self.multi_correct,self.multi_spread,self.candidate_goals)


class RecognizerBenchmark:

    def __init__(self, options):
        self.failed_experiments = []
        self.experiment_names = []
        self.experiments = {}
        self.options = options
        # self.observability = ['25', '50', '75', '100'] # FIXME parameterize this
        self.observability = ['10', '30', '50', '70', '100']

    def run_benchmark(self):
        benchmark_time = time.time()
        total_problems = 0
        for recognizer_name in self.options.recognizer:
            self.experiment_names.append(recognizer_name)
            self.experiments[recognizer_name] = Experiment(recognizer_name)

        for obs in self.observability:
            problems = 0
            problems_path = self.options.work_dir+'/'+self.options.domain_name+'/'+obs+'/'
            folder_problems = len(os.listdir(problems_path))

            for problem_file in os.listdir(problems_path):
                if problem_file.endswith(".tar.bz2"):
                    cmd_clean = 'rm -rf %s/*.pddl %s/*.dat %s/*.log'%(self.options.work_dir,self.options.work_dir,self.options.work_dir)
                    os.system(cmd_clean)

                    cmd_untar = 'tar xvjf ' + problems_path + problem_file + ' -C '+self.options.work_dir

                    os.system(cmd_untar)

                    problems += 1

                    exp_options = Options(self.options.work_dir)
                    exp_options.verbose = False
                    exp_options.exp_file = problems_path+problem_file
                    exp_options.domain_name='domain'
                    for e in self.experiment_names:
                        self.experiments[e].observability = obs
                        success = self.experiments[e].run_experiment(exp_options)
                        if not success:
                            self.failed_experiments.append(problems_path+problem_file)
                            progress(problems, folder_problems, e+":"+self.options.domain_name+":"+str(obs)+"%")

            total_problems += problems

            for e in self.experiments:
                print(e.compute_stats())

    def compute_stats(self):
        print('Not implemented ')


if __name__ == '__main__':
    print(sys.argv)
    options = ProgramOptions(sys.argv[1:])
    benchmark = RecognizerBenchmark(options)
    benchmark.run_benchmark()

#!/usr/bin/env python
#
#  main.py
#  ma-goal-recognition
#
#  Created by Felipe Meneguzzi on 2020-03-12.
#  Copyright 2020 Felipe Meneguzzi. All rights reserved.
#

from recognizer.pddl.propositional_planner import Propositional_Planner
from recognizer.pddl.sat_planner import SATPlanner
from recognizer.pddl.heuristic_planner import Heuristic_Planner

from recognizer.ma_plan_recognizer import SATTeamPlanRecognizer
from recognizer.plan_recognizer_factory import PlanRecognizerFactory

import sys

from recognizer.options import ProgramOptions


def run_recognizer(recognizer):
    recognizer.run_recognizer()
    realHyp = recognizer.get_real_hypothesis()
    print("Real Goal is: %s\n\nRecognized: %s"%(str(realHyp),str(recognizer.unique_goal)))
    if recognizer.unique_goal is not None and realHyp == recognizer.unique_goal:
        print('True!')
    else:
        print('False!')
    print(recognizer.name)


def main():
    # cmdClean = 'rm -rf *.pddl *.dat *.log *.soln *.csv report.txt h_result.txt results.tar.bz2'
    # os.system(cmdClean)

    print(sys.argv)
    options = ProgramOptions(sys.argv[1:])
    options.untar_experiment()

    recognizer = None
    if options.recognizer == 'sat':
        # factory = PlanRecognizerFactory()
        # recognizer = factory.get_recognizer('sat')#factory.get_recognizer('SATTeamPlanRecognizer')
        recognizer = SATTeamPlanRecognizer(options)

    if recognizer is not None:
        run_recognizer(recognizer)


if __name__ == '__main__':
    main()
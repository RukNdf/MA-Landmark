#!/usr/bin/env python
#
#  plan_recognizer_test.py
#  ma-goal-recognition
#
#  Created by Felipe Meneguzzi on 2020-03-12.
#  Copyright 2020 Felipe Meneguzzi. All rights reserved.
#


import unittest

from recognizer.plan_recognizer_factory import PlanRecognizerFactory
from recognizer.ma_plan_recognizer import SATTeamPlanRecognizer
from recognizer.sat_plan_recognizer import SATPlanRecognizer
from recognizer.options import Options
from recognizer.problem import Hypothesis, TeamHypothesis
import sys


class PlanRecognizerTest(unittest.TestCase):

    @unittest.skip("Factory still not working")
    def test_factory(self):
        factory = PlanRecognizerFactory()
        recognizer = factory.get_recognizer('SATTeamPlanRecognizer')
        self.assertIsInstance(recognizer, SATTeamPlanRecognizer)

    # @unittest.skipUnless(sys.platform.startswith("linux"), "Only test in Travis")
    def test_sat_recognizer(self):
        options = Options('examples/blocksworld/')
        options.domain_name = 'blocksworld'
        options.verbose = True
        recognizer = SATPlanRecognizer(options)
        recognizer.run_recognizer()
        real_hypothesis = Hypothesis.load_real_hypothesis('examples/blocksworld/real_hyp.dat')
        print("Unique goal: %s"%recognizer.unique_goal)
        self.assertIn(real_hypothesis, recognizer.accepted_hypotheses)

    # @unittest.skipUnless(sys.platform.startswith("linux"), "Only test in Travis")
    def test_sat_ma_recognizer(self):
        options = Options('examples/blocksworld/')
        options.domain_name = 'ma-blocksworld'
        options.verbose = True
        recognizer = SATTeamPlanRecognizer(options)
        recognizer.run_recognizer()
        real_hypotheses = TeamHypothesis.load_real_hypothesis('examples/blocksworld/realTeamHyp.dat')
        print("Unique goal: %s" % recognizer.unique_goal)
        self.assertIn(real_hypotheses[0], recognizer.accepted_hypotheses)
        self.assertIn(real_hypotheses[1], recognizer.accepted_hypotheses)

if __name__ == '__main__':
    unittest.main()

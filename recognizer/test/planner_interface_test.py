#!/usr/bin/env python
#
#  planner_interface_test.py
#  ma-goal-recognition
#
#  Created by Felipe Meneguzzi on 2020-03-12.
#  Copyright 2020 Felipe Meneguzzi. All rights reserved.
#


import unittest
from recognizer.planner_interface import SATPlannerInterface
from recognizer.problem import Observations, Hypothesis, TeamHypothesis
import sys


class PlannerInterfaceTest(unittest.TestCase):

    def test_observations(self):
        observations = Observations('examples/blocksworld/ma-obs.dat')
        self.assertEqual('(pickup ag1 a)', observations[0])

        observations = Observations('examples/blocksworld/obs.dat')
        self.assertEqual('(pickup a)', observations[0])

    def test_hypothesis(self):
        hypotheses = Hypothesis.load_hypotheses('hyps.dat',work_dir="examples/blocksworld/")
        self.assertIn('(on a b)', hypotheses[0].atoms)
        actual_hypotheses = Hypothesis.load_real_hypothesis('realHyp.dat', work_dir='examples/blocksworld/')
        hypotheses[0].check_if_actual(actual_hypotheses)
        self.assertTrue(hypotheses[0].is_true)
        self.assertFalse(hypotheses[2].is_true)

    def test_team_hypothesis(self):
        hypotheses = TeamHypothesis.load_hypotheses('hyps.dat',work_dir="examples/blocksworld/")
        self.assertIn('(on a b)',hypotheses[0].atoms)
        actual_hypotheses = TeamHypothesis.load_real_hypothesis('realTeamHyp.dat', work_dir='examples/blocksworld/')
        hypotheses[0].team = frozenset(['ag1','ag2'])
        hypotheses[0].check_if_actual(actual_hypotheses)
        self.assertTrue(hypotheses[0].is_true)
        hypotheses[1].team = frozenset(['ag3'])
        hypotheses[1].check_if_actual(actual_hypotheses)
        self.assertTrue(hypotheses[1].is_true)
        hypotheses[2].team = frozenset(['ag1'])
        hypotheses[2].check_if_actual(actual_hypotheses)
        self.assertFalse(hypotheses[2].is_true)

    # @unittest.skip("Skipping because it takes too long")
    @unittest.skipUnless(sys.platform.startswith("linux"), "Only test in Travis")
    def test_execute(self):
        planner_interface = SATPlannerInterface('examples/blocksworld/ma-blocksworld.pddl','examples/blocksworld/m-pb5b.pddl',verbose=True)
        plan = planner_interface.execute()
        self.assertIsNotNone(plan)
        self.assertEqual(6,len(plan))

        observations = Observations('examples/blocksworld/ma-obs.dat')
        plan_constrained = planner_interface.execute(observations)


if __name__ == '__main__':
    unittest.main()

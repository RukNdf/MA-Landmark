#!/usr/bin/env python
#
#  GR_Test.py
#  ma-goal-recognition
#
#  Created by Felipe Meneguzzi on 2020-03-12.
#  Copyright 2020 Felipe Meneguzzi. All rights reserved.
#


import unittest

from recognizer.problem import Hypothesis, Observations

class GRTest(unittest.TestCase):

    def test_load_hypotheses(self):
        hyps = Hypothesis.load_hypotheses('examples/blocksworld/hyps.dat')
        self.assertEqual('(on a b)', hyps[0].atoms[0])

    def test_load_observations(self):
        obsAll = Observations('examples/blocksworld/ma-obs.dat')
        self.assertEqual(6,len(obsAll))
        self.assertEqual('(pickup ag1 a)',obsAll.observations[0])

        obsAg1 = Observations('examples/blocksworld/ma-obs.dat',agent='ag1')
        self.assertEqual(2, len(obsAg1))

    def test_load_real_hypotheses(self):
        hyps = Hypothesis.load_real_hypothesis('examples/blocksworld/realTeamHyp.dat')
        self.assertEqual(2,len(hyps))
        self.assertIn('ag1', hyps[0].team)
        self.assertIn('ag3',hyps[1].team)
        self.assertIn('(on a b)',hyps[0].atoms)
        self.assertIn('(on c d)', hyps[0].atoms)
        self.assertIn('(on e f)', hyps[1].atoms)


if __name__ == '__main__':
    unittest.main()

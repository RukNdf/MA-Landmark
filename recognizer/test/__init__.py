#
#  __init__.py
#  ma-goal-recognition
#
#  Created by Felipe Meneguzzi on 2020-03-12.
#  Copyright 2020 Felipe Meneguzzi. All rights reserved.
#

import unittest
from .PDDL_test import PDDL_Test
from .propositional_planner_test import Propositional_Planner_Test
from .planner_interface_test import PlannerInterfaceTest
from recognizer.test.plan_recognizer_test import PlanRecognizerTest


def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(PDDL_Test))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Propositional_Planner_Test))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(PlannerInterfaceTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(PlanRecognizerTest))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)


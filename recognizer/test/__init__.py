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


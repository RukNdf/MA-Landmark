import unittest
from recognizer.planner_interface import SATPlannerInterface
from recognizer.problem import Observations


class PlannerInterfaceTest(unittest.TestCase):
    def test_execute(self):
        planner_interface = SATPlannerInterface('examples/blocksworld/ma-blocksworld.pddl','examples/blocksworld/m-pb5b.pddl',verbose=True)
        plan = planner_interface.execute()
        self.assertIsNotNone(plan)
        self.assertEqual(6,len(plan))

        observations = Observations('examples/blocksworld/obs.dat')
        plan_constrained = planner_interface.execute(observations)



if __name__ == '__main__':
    unittest.main()

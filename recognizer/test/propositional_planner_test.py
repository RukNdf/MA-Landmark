#!/usr/bin/env python
# Four spaces as indentation [no tabs]

import unittest
from recognizer.pddl.action import Action
from recognizer.pddl.propositional_planner import Propositional_Planner
from recognizer.pddl.sat_planner import SATPlanner
from recognizer.pddl.heuristic_planner import Heuristic_Planner
import time, sys, math

# ==========================================
# Test Propositional_Planner
# ==========================================


class Propositional_Planner_Test(unittest.TestCase):

    # ------------------------------------------
    # Test solve
    # ------------------------------------------

    def test_solve_dinner(self):
        planner = Propositional_Planner()
        self.assertEqual([
                Action('cook', [], [('clean',)], [], [('dinner',)], []),
                Action('wrap', [], [('quiet',)], [], [('present',)], []),
                Action('carry', [], [('garbage',)], [], [], [('garbage',), ('clean',)])
            ], planner.solve_file('examples/dinner/dinner.pddl', 'examples/dinner/pb1.pddl')[0])

    # @unittest.skipUnless(sys.platform.startswith("osx"), "Skip, as travis will timeout")
    # @unittest.skip("Skip, to avoid timeout")
    @unittest.skipUnless(sys.platform.startswith("linux"), "Only test in Travis")
    def test_solve_psr(self):
        domain_template = 'examples/psr-small/domain{0}.pddl'
        problem_template = 'examples/psr-small/task{0}.pddl'
        planner = Propositional_Planner(time_limit=0.1)
        last_domain = 50
        # last_domain = 14
        for i in range(1, last_domain+1):
            domain_filename = domain_template.format("%02d" % i)
            problem_filename = problem_template.format("%02d" % i)
            print("Processing ", domain_filename, " and ", problem_filename)
            start = time.time()
            plan = planner.solve_file(domain_filename,problem_filename)
            end = time.time()
            print("Planning took {0}s for {1} using {2}".format(end - start, problem_filename, planner.__class__.__name__))
            print("Plan length ",len(plan)) if plan is not None else 0

    def test_solve_heuristic(self):
        planner = Heuristic_Planner()
        plan = planner.solve_file('examples/dinner/dinner.pddl', 'examples/dinner/pb1.pddl')[0]
        self.assertIsNotNone(plan)
        self.assertEqual(3, len(plan))
        # print("Plan: ", plan)
        self.assertEqual(plan,
                         [
                             Action('cook', [], [('clean',)], [], [('dinner',)], []),
                             Action('carry', [], [('garbage',)], [], [], [('garbage',), ('clean',)]),
                             Action('wrap', [], [('quiet',)], [], [('present',)], [])
                         ]
                         )

    #@unittest.skipUnless(sys.platform.startswith("osx"), "Skip, since travis does not like z3")
    def test_solve_sat(self):
        planner = SATPlanner()
        plan = planner.solve_file('examples/dinner/dinner.pddl', 'examples/dinner/pb1.pddl')[0]
        self.assertIsNotNone(plan)
        self.assertEqual(3,len(plan))
        # print plan
        self.assertIn(plan, [[Action('wrap', [], [('quiet',)],[],[('present',)],[]),
                Action('cook', [], [('clean',)],[],[('dinner',)],[]),
                Action('dolly', [], [('garbage',)], [], [], [('garbage',), ('quiet',)])],
                             [Action('cook', [], [('clean',)], [], [('dinner',)], []),
                              Action('wrap', [], [('quiet',)], [], [('present',)], []),
                              Action('dolly', [], [('garbage',)], [], [], [('garbage',), ('quiet',)])]
                             ])
        # self.assertEqual(
        #     [Action('wrap', [], [('quiet',)],[],[('present',)],[]),
        #         Action('cook', [], [('clean',)],[],[('dinner',)],[]),
        #         Action('dolly', [], [('garbage',)], [], [], [('garbage',), ('quiet',)])],
        #     plan
        # )

        blk = "examples/blocksworld/blocksworld.pddl"
        b_pb1 = "examples/blocksworld/pb1.pddl"
        b_pb2 = "examples/blocksworld/pb2.pddl"
        b_pb3 = "examples/blocksworld/pb3.pddl"
        b_pb4 = "examples/blocksworld/pb4.pddl"
        b_pb5 = "examples/blocksworld/pb5.pddl"
        b_pb6 = "examples/blocksworld/pb6.pddl"

        bpd_list = [b_pb1, b_pb2, b_pb3, b_pb4, b_pb5, b_pb6]
        results = [2, 6, 4, 8, 8, 10]

        times = []
        for b, r in zip(bpd_list, results):
            plan, time = planner.solve_file(blk, b, False)
            times.append(time)
            self.assertEqual(r, len(plan), "Failed on BW prob %s"%b )

        times_simp = []
        planner = SATPlanner(simplify=True)
        for b, r in zip(bpd_list, results):
            plan, time = planner.solve_file(blk, b, False)
            times_simp.append(time)
            self.assertEqual(r, len(plan), "Failed on BW prob %s"%b )

        avg_time = sum(times) / len(times)
        avg_time_simp = sum(times_simp) / len(times_simp)
        print("Unsimplified time: %f | Simplified time: %f "%(avg_time, avg_time_simp))
        self.assertGreaterEqual(avg_time,avg_time_simp,"Simplification did not work")

    def test_benchmark_planners(self):
        pass

if __name__ == '__main__':
    unittest.main()
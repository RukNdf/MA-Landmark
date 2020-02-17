#!/usr/bin/env python
# Four spaces as indentation [no tabs]

import unittest
from recognizer.pddl.pddl_parser import PDDL_Parser
from recognizer.pddl.pddl_planner import PDDL_Planner
from recognizer.pddl.action import Action

# ==========================================
# Test PDDL
# ==========================================


class PDDL_Test(unittest.TestCase):

    # ------------------------------------------
    # Test scan_tokens
    # ------------------------------------------

    def test_scan_tokens_domain(self):
        parser = PDDL_Parser()
        self.assertEqual(parser.scan_tokens('examples/dinner/dinner.pddl'),
            ['define', ['domain', 'dinner'],
            [':requirements', ':strips'],
            [':predicates', ['clean'], ['dinner'], ['quiet'], ['present'], ['garbage']],
            [':action', 'cook',
                ':parameters', [],
                ':precondition', ['and', ['clean']],
                ':effect', ['and', ['dinner']]],
            [':action', 'wrap',
                ':parameters', [],
                ':precondition', ['and', ['quiet']],
                ':effect', ['and', ['present']]],
            [':action', 'carry',
                ':parameters', [],
                ':precondition', ['and', ['garbage']],
                ':effect', ['and', ['not', ['garbage']], ['not', ['clean']]]],
            [':action', 'dolly',
                ':parameters', [],
                ':precondition', ['and', ['garbage']],
                ':effect', ['and', ['not', ['garbage']], ['not', ['quiet']]]]]
        )

    def test_scan_tokens_problem(self):
        parser = PDDL_Parser()
        self.assertEqual(parser.scan_tokens('examples/dinner/pb1.pddl'),
            ['define', ['problem', 'pb1'],
            [':domain', 'dinner'],
            [':init', ['garbage'], ['clean'], ['quiet']],
            [':goal', ['and', ['dinner'], ['present'], ['not', ['garbage']]]]]
        )

    # ------------------------------------------
    # Test parse domain
    # ------------------------------------------

    def test_parse_domain(self):
        parser = PDDL_Parser()
        parser.parse_domain('examples/dinner/dinner.pddl')
        print(parser.actions)
        self.assertEqual(parser.domain_name, 'dinner')
        self.assertEqual(parser.actions,
            [
                Action('cook', [], [('clean',)], [], [('dinner',)], []),
                Action('wrap', [], [('quiet',)], [], [('present',)], []),
                Action('carry', [], [('garbage',)], [], [], [('garbage',), ('clean',)]),
                Action('dolly', [], [('garbage',)], [], [], [('garbage',), ('quiet',)])
            ]
        )

    # ------------------------------------------
    # Test parse problem
    # ------------------------------------------

    def test_parse_problem(self):
        parser = PDDL_Parser()
        parser.parse_domain('examples/dinner/dinner.pddl')
        parser.parse_problem('examples/dinner/pb1.pddl')
        self.assertEqual('pb1', parser.problem_name)
        self.assertEqual({}, parser.objects)
        self.assertEqual(frozenset([('garbage',),('clean',),('quiet',)]), parser.state)
        self.assertEqual(frozenset([('dinner',), ('present',)]), parser.positive_goals)
        self.assertEqual(frozenset([('garbage',)]), parser.negative_goals)

    # -------------------------------------------
    # Split propositions
    # -------------------------------------------

    def test_parse_first_order(self):
        parser = PDDL_Parser()
        parser.parse_domain('examples/dwr/dwr.pddl')
        parser.parse_problem('examples/dwr/pb1.pddl')
        self.assertEqual(parser.problem_name, 'pb1')
        print(parser.objects.values())
        self.assertEqual(set(['r1','l1','l2','k1','k2','p1','q1','p2','q2','ca','cb','cc','cd','ce','cf', 'pallet']),
                         {object for obj_types in parser.objects.values() for object in obj_types})
        # print(parser.actions)

    def test_parse_types(self):
        parser = PDDL_Parser()
        parser.parse_domain('examples/dwr/dwr.pddl')
        parser.parse_problem('examples/dwr/pb1.pddl')
        self.assertEqual(parser.problem_name, 'pb1')
        print(parser.types)

    def test_mutex(self):
        parser = PDDL_Parser()
        cook = Action('cook', [], [('clean',)], [], [('dinner',)], [])
        wrap = Action('wrap', [], [('quiet',)], [], [('present',)], [])
        carry = Action('carry', [], [('garbage',)], [], [], [('garbage',), ('clean',)])
        dolly = Action('dolly', [], [('garbage',)], [], [], [('garbage',), ('quiet',)])
        self.assertTrue(cook.is_mutex(carry))
        self.assertTrue(carry.is_mutex(cook))
        self.assertTrue(wrap.is_mutex(dolly))
        self.assertTrue(dolly.is_mutex(wrap))
        self.assertFalse(cook.is_mutex(wrap))


    def test_reachability_analysis(self):
        parser = PDDL_Parser()
        parser.parse_domain('examples/dinner/dinner.pddl')
        parser.parse_problem('examples/dinner/pb1.pddl')
        planner = PDDL_Planner()
        self.assertTrue(planner.solvable(parser.actions,parser.state,(parser.positive_goals, parser.negative_goals)))
        initial_state = [p for p in parser.state]
        initial_state.remove(("clean",))
        self.assertFalse(planner.solvable(parser.actions,initial_state,(parser.positive_goals,parser.negative_goals)))
        domain = [a for a in parser.actions]
        domain.pop(0)
        self.assertFalse(planner.solvable(domain, initial_state, (parser.positive_goals,parser.negative_goals)))

if __name__ == '__main__':
    unittest.main()
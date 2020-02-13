from recognizer.pddl.pddl_parser import PDDL_Parser
from recognizer.pddl.state import applicable, apply


class PDDL_Planner:

    def applicable(self, state, positive, negative):
        return applicable(state, positive, negative)

    def apply(self, state, positive, negative):
        return apply(state, positive, negative)

    def solvable(self, domain, initial_state, goal_state):
        """"Computes whether the problem posed by initial_state, goal_state is solvable by reachability analysis"""
        last_state = set([])
        reachable_literals = set(initial_state)
        positive_goals = set(goal_state[0])
        actions = domain

        positive_effects = set([])
        negative_effects = set([])
        for a in actions:
            positive_effects = positive_effects.union(set(a.add_effects))
            negative_effects = negative_effects.union(set(a.del_effects))
        # First check the obvious stuff
        for p in goal_state[0]:
            if p not in reachable_literals and p not in positive_effects:
                return False
        for p in goal_state[1]:
            if p in reachable_literals and p not in negative_effects:
                return False

        while last_state != reachable_literals:
            last_state = reachable_literals.copy()
            if positive_goals.issubset(reachable_literals):
                return True
            for a in actions:
                if a.applicable(reachable_literals):
                    reachable_literals = reachable_literals.union(a.add_effects)

        return False

    #-----------------------------------------------
    # Solve
    #-----------------------------------------------

    def solve_file(self, domainfile, problemfile, verbose=True):
        # Parser
        import time
        start_time = time.time()
        parser = PDDL_Parser()
        parser.parse_domain(domainfile)
        parser.parse_problem(problemfile)
        # Test if first state is not the goal
        if applicable(parser.state, parser.positive_goals, parser.negative_goals):
            return [], 0
        # Grounding process
        ground_actions = []
        for action in parser.actions:
            for act in action.groundify(parser.objects):
                ground_actions.append(act)
        plan = self.solve(ground_actions, parser.state, (parser.positive_goals, parser.negative_goals))
        final_time = time.time() - start_time
        if verbose:
            print('Time: ' + str(final_time) + 's')
            if plan:
                print('plan:')
                for act in plan:
                    print('(' + act.name + ''.join(' ' + p for p in act.parameters) + ')')
            else:
                print('No plan was found')
        return plan, final_time

    def solve(self, domain, initial_state, goals):
        raise NotImplementedError("PDDL Planners need to implement solve")
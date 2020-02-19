#!/usr/bin/env python3

from recognizer.pddl.pddl_parser import string_to_fluent

def custom_partition(s, sep):
    i = 0
    while i < len(s):
        if s[i] == sep: break
        i = i + 1
    if i == len(s): return (None, None, None)
    if i == 0: return (None, s[i], s[i + 1:])
    return (s[:i], s[i], s[i + 1:])


class Hypothesis:

    def __init__(self, atoms=[], team = None):
        self.atoms = atoms
        self.is_true = True

        self.team = team

    def evaluate(self, index, observations):
        hyp_problem = 'hyp_%d_problem.pddl' % index
        self.generate_pddl_for_hyp_plan(hyp_problem)

    def generate_pddl_for_hyp_plan(self, out_name):
        instream = open('template.pddl')
        outstream = open(out_name, 'w')

        for line in instream:
            line = line.strip()
            if '<HYPOTHESIS>' in line:
                for atom in self.atoms:
                    outstream.write(atom)
            elif '<TEAM-OBJS>' in line:
                for agent in self.team:
                    outstream.write(agent)
            elif '<TEAM-ATOMS>' in line:
                for agent in self.team:
                    outstream.write('(agent %s)'%agent)
            else:
                outstream.write(line)

        outstream.close()
        instream.close()

    @staticmethod
    def load_hypotheses(hyp_file = "hyps.dat"):
        hyps = []
        instream = open(hyp_file)
        for line in instream:
            line = line.strip()
            atoms = [tok.strip() for tok in line.split(',')]
            # TODO - check if I need to implement something analogous to check_if_actual from Ramirez
            hyps.append(Hypothesis(atoms))
        instream.close()
        return hyps

    @staticmethod
    def load_real_hypothesis(hyp_file = 'realHyp.dat'):
        hyps = []
        instream = open(hyp_file)
        for line in instream:
            line = line.strip()
            agents, _, atoms = custom_partition(line, ':')
            atoms = [tok.strip() for tok in atoms.split(',')]
            agents = [tok.strip() for tok in agents.split(',')]
            hyps.append(Hypothesis(atoms,agents))

        instream.close()
        return hyps


class Observations:
    """ A set of observations for a specific agent. We assume
        the first parameter of the actions are always the agent"""
    
    def __init__(self, obs_file="obs.dat", agent = None):
        self.observations = []
        instream = open(obs_file)
        for line in instream:
            obs = line.strip().lower()
            obs_fluent = string_to_fluent(obs)
            if agent is None or obs_fluent[1] == agent:
                self.observations.append(obs)
        instream.close()

    @property
    def __len__(self):
        return len(self.observations)

    def __iter__(self):
        return self.observations.__iter__()

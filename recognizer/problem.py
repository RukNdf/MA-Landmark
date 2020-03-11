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


# noinspection SpellCheckingInspection
class Hypothesis:
    """ A Single agent hypothesis"""
    def __init__(self, atoms=[], work_dir="."):
        self.atoms = frozenset(atoms)
        self.is_true = False
        self.work_dir = work_dir
        self.test_failed = False
        self.cost = 0

    def evaluate(self, index, observations):
        hyp_problem = self.work_dir+'hyp_%d_problem.pddl' % index
        self.generate_pddl_for_hyp_plan(hyp_problem)

    def generate_pddl_for_hyp_plan(self, out_name):
        instream = open(self.work_dir+'/template.pddl')
        outstream = open(out_name, 'w')

        for line in instream:
            line = line.strip()
            if '<HYPOTHESIS>' in line:
                for atom in self.atoms:
                    outstream.write(atom)
            else:
                outstream.write(line)

        outstream.close()
        instream.close()

    def check_if_actual(self, actual_hyps):
        self.is_true = self.atoms == actual_hyps.atoms

    @staticmethod
    def load_hypotheses(hyp_file='hyps.dat', work_dir='.'):
        actual_hyps = Hypothesis.load_real_hypothesis(work_dir=work_dir)
        hyps = []
        instream = open(work_dir+ '/' + hyp_file)
        for line in instream:
            line = line.strip()
            atoms = [tok.strip() for tok in line.split(',')]
            h = Hypothesis(atoms, work_dir=work_dir)
            h.check_if_actual(actual_hyps)
            hyps.append(h)
        instream.close()
        return hyps

    @staticmethod
    def load_real_hypothesis(hyp_file='realHyp.dat', work_dir='.'):
        real_hyp_atoms = []
        instream = open(work_dir + '/' + hyp_file)
        for line in instream:
            real_hyp_atoms = [tok.strip() for tok in line.split(',')]
        instream.close()
        return Hypothesis(real_hyp_atoms)

    def __iter__(self):
        return iter(self.atoms)

    def __str__(self):
        res = ""
        for a in self.atoms:
            res += a
        return res

    def __repr__(self):
        return str(self)


class TeamHypothesis(Hypothesis):
    """ A Team hypothesis"""

    def __init__(self, atoms=[], team = None, work_dir=""):
        Hypothesis.__init__(self,atoms,work_dir)
        self.team = frozenset(team) if team is not None else None

    def generate_pddl_for_hyp_plan(self, out_name):
        instream = open(self.work_dir+'template.pddl')
        outstream = open(out_name, 'w')

        for line in instream:
            line = line.strip()
            if '<HYPOTHESIS>' in line:
                for atom in self.atoms:
                    outstream.write(atom)
            elif '<TEAM-OBJS>' in line:
                outstream.write(' ')
                for agent in self.team:
                    outstream.write(agent)
            elif '<TEAM-ATOMS>' in line:
                outstream.write(' ')
                for agent in self.team:
                    outstream.write('(agent %s)'%agent)
            else:
                outstream.write(line)

        outstream.close()
        instream.close()

    def check_if_actual(self, actual_hyps):
        self.is_true = False
        for actual in actual_hyps:
            if actual.atoms == self.atoms and actual.team == self.team:
                self.is_true = True
                return True

        return self.is_true

    @staticmethod
    def load_hypotheses(hyp_file='hyps.dat', work_dir='.'): # TODO There might be a bit of code replication here
        actual_hyps = TeamHypothesis.load_real_hypothesis(work_dir=work_dir)
        hyps = []
        instream = open(work_dir + '/' + hyp_file)
        for line in instream:
            line = line.strip()
            atoms = [tok.strip() for tok in line.split(',')]
            h = TeamHypothesis(atoms, work_dir=work_dir)
            h.check_if_actual(actual_hyps)  # Check if actual is pointless, since what we read from file has no teams
            hyps.append(h)
        instream.close()
        return hyps

    @staticmethod
    def load_real_hypothesis(hyp_file = 'realTeamHyp.dat', work_dir='.'):
        hyps = []
        instream = open(work_dir+'/'+hyp_file)
        for line in instream:
            line = line.strip()
            agents, _, atoms = custom_partition(line, ':')
            atoms = [tok.strip() for tok in atoms.split(',')]
            agents = [tok.strip() for tok in agents.split(',')]
            hyps.append(TeamHypothesis(atoms,agents))

        instream.close()
        return hyps

    def __str__(self):
        res = "" if self.team is None else str(self.team)+": "
        for a in self.atoms:
            res += a
        return res

    def __repr__(self):
        return str(self)


class Observations:
    """ A set of observations for a specific agent. We assume
        the first parameter of the actions are always the agent
        TODO This may need refactoring later
    """
    
    def __init__(self, obs_file="ma-obs.dat", agent = None):
        self.observations = []
        instream = open(obs_file)
        for line in instream:
            obs = line.strip().lower()
            obs_fluent = string_to_fluent(obs)
            if agent is None or obs_fluent[1] == agent:
                self.observations.append(obs)
        instream.close()

    def index_of(self, action_signature):
        for i in range(0,len(self.observations)):
            if action_signature == self.observations[i]:
                return i
        return -1

    def __len__(self):
        return len(self.observations)

    def __iter__(self):
        return self.observations.__iter__()

    def __getitem__(self, item):
        return self.observations[item]

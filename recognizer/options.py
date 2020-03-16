#!/usr/bin/env python
#
#  options.py
#  ma-goal-recognition
#
#  Created by Felipe Meneguzzi on 2020-03-12.
#  Copyright 2020 Felipe Meneguzzi. All rights reserved.
#


import getopt, os, sys


def usage():
    print("Parameters:", file=sys.stderr)
    print("-b  --batch                      Run a batch of experiments", file=sys.stderr)
    print("-e  --experiment <file/folder>   Plan Recognition experiment files (tar'ed) or folder (in batch mode)", file=sys.stderr)
    print("-h  --help                       Get Help", file=sys.stderr)
    print("-t  --max-time <time>            Maximum allowed execution time (defaults to 1800 secs)", file=sys.stderr)
    print("-m  --max-memory <time>          Maximum allowed memory consumption (defaults to 1Gb)", file=sys.stderr)
    print("-w  --work-dir <dir>             Working directory (defaults to ./)", file=sys.stderr)
    print("-r  --recognizer <name>          Name of the recognizer (defaults to sat)", file=sys.stderr)


class Options:

    def __init__(self, work_dir="./"):
        self.batch = False
        self.exp_file = None
        self.domain_name = None
        self.instance_names = []
        self.goal_file = None
        self.max_time = 1800
        self.max_memory = 1024
        self.recognizer = 'sat'
        self.work_dir = work_dir
        self.verbose = False
        self.observation_file = 'obs.dat'
        self.real_hypothesis_file = 'real_hyp.dat'
        self.template_file = 'template.pddl'


class ProgramOptions(Options):

    def __init__(self, args):
        Options.__init__(self)

        try:
            opts, args = getopt.getopt(args,
                                       "be:ht:m:r:w:v",
                                       ["batch",
                                        "experiment=",
                                        "help",
                                        "max-time=",
                                        "max-memory=",
                                        "recognizer=",
                                        "work-dir=",
                                        "verbose"])
        except getopt.GetoptError:
            print("Missing or incorrect parameters specified!", file=sys.stderr)
            # print("Missing or incorrect parameters specified!", file=sys.stderr)
            usage()
            sys.exit(1)

        for opcode, oparg in opts:
            if opcode in ('-b', '--batch'):
                print("Running batch experiments!", file=sys.stderr)
                self.batch = True
            if opcode in ('-h', '--help'):
                print("Help invoked!", file=sys.stderr)
                usage()
                sys.exit(0)
            if opcode in ('-e', '--experiment'):
                self.exp_file = oparg
            if opcode in ('-t', '--max-time'):
                try:
                    self.max_time = int(oparg)
                    if self.max_time <= 0:
                        print("Maximum time must be greater than zero", file=sys.stderr)
                        sys.exit(1)
                except ValueError:
                    print("Time must be an integer", file=sys.stderr)
                    sys.exit(1)
            if opcode in ('-m', '--max-memory'):
                try:
                    self.max_memory = int(oparg)
                    if self.max_memory <= 0:
                        print("Maximum memory must be greater than zero", file=sys.stderr)
                        sys.exit(1)
                except ValueError:
                    print("Memory amount must be an integer", file=sys.stderr)
                    sys.exit(1)
            if opcode in ('-r', '--recognizer'):
                self.recognizer = oparg
                if self.recognizer not in {'sat','lp'}: # TODO Use the actual recognizer names in future
                    print("recognizer parameter requires a valid recognizer name", file=sys.stderr)
                    sys.exit(1)
            if opcode in ('-w','--work-dir'):
                self.work_dir = oparg
                if not os.path.exists(self.work_dir):
                    print("Working directory %s does not exist!"%self.work_dir, file=sys.stderr)
                    usage()
                    sys.exit(1)
            if opcode in ('v', '--verbose'):
                self.verbose = True

        if self.batch:
            # print("Not checking other files", file=sys.stderr)
            if not os.path.exists(self.work_dir+'/'+self.exp_file):
                print("Folder %s does not exist for batch experiments"%self.work_dir+'/'+self.exp_file, file=sys.stderr)
                sys.exit(1)
            else:
                self.domain_name = self.exp_file

            if isinstance(self.recognizer,str):
                self.recognizer = [self.recognizer]

        if self.exp_file is None:
            print("No experiment file was specified!!", file=sys.stderr)
            usage()
            sys.exit(1)

        if not os.path.exists(self.work_dir+'/'+self.exp_file):
            print("File", self.work_dir+'/'+self.exp_file, "does not exist", file=sys.stderr)
            print("Aborting", file=sys.stderr)
            sys.exit(1)

    def untar_experiment(self):
        os.system('tar jxvf %s' % self.exp_file)
        if not os.path.exists(self.work_dir + '/domain.pddl'):
            os.system('tar -jxvf %s' % self.exp_file + ' --strip-components 1')
            if not os.path.exists(self.work_dir + 'domain.pddl'):
                print("No 'domain.pddl' file found in experiment file!", file=sys.stderr)
                usage()
                sys.exit(1)
        if not os.path.exists(self.work_dir + 'template.pddl'):
            print("No 'template.pddl' file found in experiment file!", file=sys.stderr)
            usage()
            sys.exit(1)
        if not os.path.exists(self.work_dir + 'hyps.dat'):
            print("No 'hyps.dat' file found in experiment file!", file=sys.stderr)
            usage()
            sys.exit(1)
        if not os.path.exists(self.work_dir + 'ma-obs.dat'):
            print("No 'ma-obs.dat' file found in experiment file!", file=sys.stderr)
            usage()
            sys.exit(1)
        if not os.path.exists(self.work_dir + 'real_hyp.dat'):
            print("No 'real_hyp.dat' file found in experiment file!", file=sys.stderr)
            usage()
            sys.exit(1)

    def print_options(self):
        def print_yes(): 
            print("Yes", file=sys.stdout)

        def print_no():
            print("No", file=sys.stdout)

        print("Options set", file=sys.stdout)
        print("===========", file=sys.stdout)
        print("Experiment File:", self.exp_file, file=sys.stdout)
        print("Max. Time Allowed", self.max_time, file=sys.stdout)
        print("Max. Memory Allowed", self.max_memory, file=sys.stdout)

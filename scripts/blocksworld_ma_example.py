from recognizer.problem import Hypothesis
from recognizer.sat_plan_recognizer import SATPlanRecognizer


def main():
    options = Options('examples/blocksworld/')
    options.domain_name = 'blocksworld'
    options.verbose = True
    recognizer = SATPlanRecognizer(options)
    recognizer.run_recognizer()
    real_hypothesis = Hypothesis.load_real_hypothesis('examples/blocksworld/real_hyp.dat')
    print("Unique goal: %s" % recognizer.unique_goal)

if __name__ == '__main__':
    main()
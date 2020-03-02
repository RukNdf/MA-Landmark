import unittest

from recognizer.plan_recognizer_factory import PlanRecognizerFactory
from recognizer.ma_plan_recognizer import SATPlanRecognizer
from recognizer.options import Options
from recognizer.problem import Hypothesis
import sys


class PlanRecognizerTest(unittest.TestCase):

    @unittest.skip("Factory still not working")
    def test_factory(self):
        factory = PlanRecognizerFactory()
        recognizer = factory.get_recognizer('SATPlanRecognizer')
        self.assertIsInstance(recognizer,SATPlanRecognizer)

    @unittest.skipUnless(sys.platform.startswith("linux"), "Only test in Travis")
    def test_sat_ma_recognizer(self):
        options = Options('examples/blocksworld/')
        recognizer = SATPlanRecognizer(options)
        recognizer.run_recognizer()
        real_hypotheses = Hypothesis.load_real_hypothesis('examples/blocksworld/realHyp.dat')
        self.assertIn(real_hypotheses[0], recognizer.accepted_hypotheses)
        self.assertIn(real_hypotheses[1], recognizer.accepted_hypotheses)

if __name__ == '__main__':
    unittest.main()

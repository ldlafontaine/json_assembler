import os
import sys
import unittest

import maya.cmds as cmds

from MayaTestSettings import MayaTestSettings
from MayaTestResult import MayaTestResult

MODELS_DIRECTORY = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                 "..", "src", "json_assembler", "models"))


def run_tests():
    import maya.standalone
    maya.standalone.initialize()

    if MODELS_DIRECTORY not in sys.path:
        sys.path.append(MODELS_DIRECTORY)

    test_suite = unittest.TestSuite()
    directory = os.path.dirname(os.path.realpath(__file__))
    discovered_suite = unittest.TestLoader().discover(directory)
    if discovered_suite.countTestCases():
        test_suite.addTests(discovered_suite)

    runner = unittest.TextTestRunner(verbosity=2, resultclass=MayaTestResult)
    runner.failfast = False
    runner.buffer = MayaTestSettings.buffer_output
    runner.run(test_suite)

    if float(cmds.about(v=True)) >= 2016.0:
        maya.standalone.uninitialize()


if __name__ == "__main__":
    run_tests()

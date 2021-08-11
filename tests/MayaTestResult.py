import logging
import os
import shutil
import unittest

import maya.cmds as cmds

from MayaTestSettings import MayaTestSettings


class MayaTestResult(unittest.TextTestResult):
    """Customize the test result so we can do things like do a file new between each test and suppress script
    editor output.
    """

    # Used to restore logging states in the script editor
    suppress_results = None
    suppress_errors = None
    suppress_warnings = None
    suppress_info = None

    def startTestRun(self):
        """Called before any tests are run."""
        super(MayaTestResult, self).startTestRun()
        self.suppress_output()
        if MayaTestSettings.buffer_output:
            # Disable any logging while running tests. By disabling critical, we are disabling logging
            # at all levels below critical as well
            logging.disable(logging.CRITICAL)

    def stopTestRun(self):
        """Called after all tests are run."""
        if MayaTestSettings.buffer_output:
            # Restore logging state
            logging.disable(logging.NOTSET)
        self.restore_output()
        if MayaTestSettings.delete_files and os.path.exists(MayaTestSettings.temp_dir):
            shutil.rmtree(MayaTestSettings.temp_dir)

        super(MayaTestResult, self).stopTestRun()

    def stopTest(self, test):
        """Called after an individual test is run.

        @param test: TestCase that just ran."""
        super(MayaTestResult, self).stopTest(test)
        if MayaTestSettings.file_new:
            cmds.file(f=True, new=True)

    @classmethod
    def suppress_output(cls):
        """Hides all script editor output."""
        if MayaTestSettings.buffer_output:
            cls.suppress_results = cmds.scriptEditorInfo(q=True, suppressResults=True)
            cls.suppress_errors = cmds.scriptEditorInfo(q=True, suppressErrors=True)
            cls.suppress_warnings = cmds.scriptEditorInfo(q=True, suppressWarnings=True)
            cls.suppress_info = cmds.scriptEditorInfo(q=True, suppressInfo=True)
            cmds.scriptEditorInfo(
                e=True,
                suppressResults=True,
                suppressInfo=True,
                suppressWarnings=True,
                suppressErrors=True,
            )

    @classmethod
    def restore_output(cls):
        """Restores the script editor output settings to their original values."""
        if None not in {
            cls.suppress_results,
            cls.suppress_errors,
            cls.suppress_warnings,
            cls.suppress_info,
        }:
            cmds.scriptEditorInfo(
                e=True,
                suppressResults=cls.suppress_results,
                suppressInfo=cls.suppress_info,
                suppressWarnings=cls.suppress_warnings,
                suppressErrors=cls.suppress_errors,
            )

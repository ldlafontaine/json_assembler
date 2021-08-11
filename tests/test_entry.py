import maya.cmds as cmds

from Entry import Entry
import maya_utilities

from MayaTestCase import MayaTestCase


class EntryTests(MayaTestCase):

    def test_entry_is_string(self):
        entry = Entry()
        entry.value = "string"
        self.assertTrue(entry.is_string())

    def test_entry_is_number(self):
        float_entry = Entry()
        float_entry.value = 6.45
        int_entry = Entry()
        int_entry.value = 3
        result = float_entry.is_number() and int_entry.is_number()
        self.assertTrue(result)

    def test_entry_is_object(self):
        entry = Entry()
        entry.value = {}
        self.assertTrue(entry.is_object())

    def test_entry_is_array(self):
        entry = Entry()
        entry.value = []
        self.assertTrue(entry.is_array())

    def test_entry_is_bool(self):
        entry = Entry()
        entry.value = False
        self.assertTrue(entry.is_bool())

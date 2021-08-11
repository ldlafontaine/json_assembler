import maya.cmds as cmds

from NodeEntry import NodeEntry
import maya_utilities

from MayaTestCase import MayaTestCase


class EntryTests(MayaTestCase):

    def test_node_entry_title(self):
        cmds.select("front", replace=True)
        entry = maya_utilities.get_entries_from_selection()[0]
        self.assertEqual(entry.title, "front")

    def test_node_entry_hashable(self):
        cmds.select("front", replace=True)
        entries = set()
        entry_a = maya_utilities.get_entries_from_selection()[0]
        entries.add(entry_a)
        entry_b = maya_utilities.get_entries_from_selection()[0]
        self.assertTrue(entry_b in entries)

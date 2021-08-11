import maya.cmds as cmds
import maya.OpenMaya as om

from AttributeEntry import AttributeEntry
import maya_utilities

from MayaTestCase import MayaTestCase


class EntryTests(MayaTestCase):

    def attribute_entry_from_name(self, node_name, attribute_name):
        cmds.select(node_name, replace=True)
        node = maya_utilities.get_nodes_from_selection()[0]
        dg_node_fn = om.MFnDependencyNode(node)
        plug = dg_node_fn.findPlug(attribute_name, True)
        attribute = plug.attribute()
        return AttributeEntry(plug, attribute)

    def test_attribute_entry_title(self):
        node_name = "front"
        attribute_name = "visibility"
        entry = self.attribute_entry_from_name(node_name, attribute_name)
        self.assertEqual(entry.title, attribute_name)

    def test_attribute_entry_hashable(self):
        node_name = "front"
        attribute_name = "nodeState"
        cmds.select("front", replace=True)
        entries = set()
        entry_a = self.attribute_entry_from_name(node_name, attribute_name)
        entries.add(entry_a)
        entry_b = self.attribute_entry_from_name(node_name, attribute_name)
        self.assertTrue(entry_b in entries)

    def test_attribute_entry_value(self):
        node_name = "side"
        attribute_name = "translateX"
        attribute_value = 30
        cmds.setAttr("%s.%s" % (node_name, attribute_name), attribute_value)
        entry = self.attribute_entry_from_name(node_name, attribute_name)
        self.assertEqual(entry.value, attribute_value)

    def test_attribute_entry_compound_value(self):
        node_name = "persp"
        attribute_name = "translate"
        entry = self.attribute_entry_from_name(node_name, attribute_name)
        self.assertEqual(len(entry.value), 3)

    def test_attribute_entry_numeric_value(self):
        node_name = "side"
        attribute_name = "caching"
        attribute_value = 1
        cmds.setAttr("%s.%s" % (node_name, attribute_name), attribute_value)
        entry = self.attribute_entry_from_name(node_name, attribute_name)
        self.assertEqual(entry.value, attribute_value)

    def test_attribute_entry_typed_value(self):
        node_name = "front"
        attribute_name = "creator"
        attribute_value = "string"
        cmds.setAttr("%s.%s" % (node_name, attribute_name), attribute_value, type="string")
        entry = self.attribute_entry_from_name(node_name, attribute_name)
        self.assertEqual(entry.value, attribute_value)

    def test_attribute_entry_unit_value(self):
        node_name = "persp"
        attribute_name = "ghostRangeStart"
        attribute_value = 4
        cmds.setAttr("%s.%s" % (node_name, attribute_name), attribute_value)
        entry = self.attribute_entry_from_name(node_name, attribute_name)
        self.assertEqual(entry.value, attribute_value)

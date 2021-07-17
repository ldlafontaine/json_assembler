import maya.OpenMaya as om

from Attribute import Attribute


class Node:

    def __init__(self, maya_object):
        if type(maya_object) != om.MObject:
            raise TypeError
        self.object = maya_object
        self.name = self.get_node_name(self.object)
        self.attributes = set()

    @staticmethod
    def get_node_name(node):
        if type(node) != om.MObject:
            raise TypeError
        dg_node_fn = om.MFnDependencyNode(node)
        return dg_node_fn.name()

    def get_all_attributes(self):
        depend_fn = om.MFnDependencyNode(self.object)
        attribute_count = depend_fn.attributeCount()
        attributes = []
        for attribute_index in range(attribute_count):
            attribute_object = depend_fn.attribute(attribute_index)
            attribute_plug = depend_fn.findPlug(attribute_object, True)
            attributes.append(Attribute(attribute_plug, attribute_object))
        return attributes

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.object == other.object
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.object)

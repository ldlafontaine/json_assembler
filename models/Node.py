import maya.OpenMaya as om

from Attribute import Attribute


class Node:

    def __init__(self, maya_object):
        if type(maya_object) != om.MObject:
            raise TypeError
        self.object = maya_object
        self.name = self.get_node_name(self.object)

    def get_icon_path(self):
        dg_node_fn = om.MFnDependencyNode(self.object)
        if self.object.hasFn(om.MFn.kMesh):
            return ":mesh.svg"
        elif self.object.hasFn(om.MFn.kCamera):
            return ":camera.svg"
        elif self.object.hasFn(om.MFn.kNurbsCurve):
            return ":nurbsCurve.svg"
        elif self.object.hasFn(om.MFn.kNurbsSurface):
            return ":nurbsSurface.svg"
        elif self.object.hasFn(om.MFn.kJoint):
            return ":joint.svg"
        elif self.object.hasFn(om.MFn.kLocator):
            return ":locator.svg"
        elif self.object.hasFn(om.MFn.kSet):
            return ":objectSet.svg"
        elif self.object.hasFn(om.MFn.kTransform):
            return ":transform.svg"
        else:
            return ":dagNode.svg"

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

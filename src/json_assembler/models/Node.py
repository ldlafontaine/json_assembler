import maya.OpenMaya as om

from Attribute import Attribute
from Entry import Entry


class Node(Entry):

    def __init__(self, maya_object):
        self.maya_object = maya_object
        self.node_name = self.get_node_name(self.maya_object)
        self.uuid = self.get_uuid()
        super(Node, self).__init__(self.node_name)
        self.value = {}

    def get_icon_path(self):
        if self.maya_object.hasFn(om.MFn.kMesh):
            return ":mesh.svg"
        elif self.maya_object.hasFn(om.MFn.kLocator):
            return ":locator.svg"
        elif self.maya_object.hasFn(om.MFn.kNurbsCurve):
            return ":nurbsCurve.svg"
        elif self.maya_object.hasFn(om.MFn.kNurbsSurface):
            return ":nurbsSurface.svg"
        elif self.maya_object.hasFn(om.MFn.kJoint):
            return ":joint.svg"
        elif self.maya_object.hasFn(om.MFn.kLight):
            return ":pointLight.svg"
        elif self.maya_object.hasFn(om.MFn.kLambert):
            return ":lambert.svg"
        elif self.maya_object.hasFn(om.MFn.kCamera):
            return ":camera.svg"
        elif self.maya_object.hasFn(om.MFn.kSet):
            return ":objectSet.svg"
        elif self.maya_object.hasFn(om.MFn.kTransform):
            return ":transform.svg"
        else:
            return ":default.svg"

    @staticmethod
    def get_node_name(node):
        dg_node_fn = om.MFnDependencyNode(node)
        return dg_node_fn.name()

    def get_uuid(self):
        dg_node_fn = om.MFnDependencyNode(self.maya_object)
        return dg_node_fn.uuid().asString()

    def get_all_attributes(self):
        depend_fn = om.MFnDependencyNode(self.maya_object)
        attribute_count = depend_fn.attributeCount()
        attributes = []
        for attribute_index in range(attribute_count):
            attribute_object = depend_fn.attribute(attribute_index)
            attribute_plug = depend_fn.findPlug(attribute_object, True)
            try:
                attributes.append(Attribute(attribute_plug, attribute_object))
            except AttributeError:
                continue
        return attributes

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.maya_object == other.maya_object
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.uuid)

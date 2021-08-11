import maya.OpenMaya as om

from AttributeEntry import AttributeEntry
from Entry import Entry


class NodeEntry(Entry):

    def __init__(self, node):
        self.node = node
        self.node_name = self.get_node_name(self.node)
        self.uuid = self.get_uuid()
        super(NodeEntry, self).__init__(self.node_name)
        self.value = {}

    def get_icon_path(self):
        if self.node.hasFn(om.MFn.kMesh):
            return ":mesh.svg"
        elif self.node.hasFn(om.MFn.kLocator):
            return ":locator.svg"
        elif self.node.hasFn(om.MFn.kNurbsCurve):
            return ":nurbsCurve.svg"
        elif self.node.hasFn(om.MFn.kNurbsSurface):
            return ":nurbsSurface.svg"
        elif self.node.hasFn(om.MFn.kJoint):
            return ":joint.svg"
        elif self.node.hasFn(om.MFn.kLight):
            return ":pointLight.svg"
        elif self.node.hasFn(om.MFn.kLambert):
            return ":lambert.svg"
        elif self.node.hasFn(om.MFn.kCamera):
            return ":camera.svg"
        elif self.node.hasFn(om.MFn.kSet):
            return ":objectSet.svg"
        elif self.node.hasFn(om.MFn.kTransform):
            return ":transform.svg"
        else:
            return ":default.svg"

    @staticmethod
    def get_node_name(node):
        dg_node_fn = om.MFnDependencyNode(node)
        return dg_node_fn.name()

    def get_uuid(self):
        dg_node_fn = om.MFnDependencyNode(self.node)
        return dg_node_fn.uuid().asString()

    def get_attribute_entries(self):
        depend_fn = om.MFnDependencyNode(self.node)
        attribute_count = depend_fn.attributeCount()
        attributes = []
        for attribute_index in range(attribute_count):
            attribute_object = depend_fn.attribute(attribute_index)
            attribute_plug = depend_fn.findPlug(attribute_object, True)
            try:
                attributes.append(AttributeEntry(attribute_plug, attribute_object))
            except AttributeError:
                continue
        return attributes

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.node == other.node
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.uuid)

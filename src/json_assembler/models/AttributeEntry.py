import maya.OpenMaya as om
import sys

from Entry import Entry


class AttributeEntry(Entry):

    def __init__(self, plug, attribute):
        self.plug = plug
        self.attribute_name = self.get_attribute_name()
        self.attribute = attribute
        self.node = plug.node()
        self.node_uuid = self.get_node_uuid()
        super(AttributeEntry, self).__init__(self.attribute_name)

        try:
            self.value = self.get_value()
        except:
            raise AttributeError
            #self.value = str(sys.exc_info())

    def get_icon_path(self):
        return ":default.svg"

    def get_attribute_name(self):
        return self.plug.partialName(False, False, False, False, False, True)

    def get_attribute_long_name(self):
        return self.plug.name()

    def get_node_uuid(self):
        dg_node_fn = om.MFnDependencyNode(self.node)
        return dg_node_fn.uuid().asString()

    def is_non_keyable(self):
        return not self.plug.isKeyable()

    def is_connected(self):
        return self.plug.isConnected()

    def is_hidden(self):
        attribute_fn = om.MFnAttribute(self.attribute)
        return attribute_fn.isHidden()

    def get_value(self):
        return self.get_attribute_value(self.plug, self.attribute)

    @staticmethod
    def get_attribute_value(plug, attribute):
        plug_type = attribute.apiTypeStr()

        # attribute_fn = om.MFnAttribute(attribute)
        # print(attribute_fn.name() + " has a plug type of " + plug_type + ".")

        if attribute.hasFn(om.MFn.kCompoundAttribute) or plug.isCompound():
            return AttributeEntry.get_compound_attribute_value(plug, attribute)
        elif attribute.hasFn(om.MFn.kUnitAttribute):
            return AttributeEntry.get_unit_attribute_value(plug, attribute)
        elif plug_type == "kNumericAttribute":
            return AttributeEntry.get_numeric_attribute_value(plug, attribute)
        elif plug_type == "kDoubleLinearAttribute":
            return plug.asDouble()
        elif plug_type == "kEnumAttribute":
            return plug.asInt()
        elif plug_type == "kTypedAttribute":
            return AttributeEntry.get_typed_attribute_value(plug, attribute)
        elif plug_type == "kGenericAttribute":
            raise NotImplementedError
        else:
            raise NotImplementedError

    @staticmethod
    def get_numeric_attribute_value(plug, attribute):
        numeric_fn = om.MFnNumericAttribute(attribute)
        unit_type = numeric_fn.unitType()
        # print(numeric_fn.name() + "\'s numeric attribute has found a unit type of " + str(unit_type) + ".")

        if unit_type == om.MFnNumericData.kBoolean:
            return plug.asBool()
        elif unit_type == om.MFnNumericData.kByte:
            return plug.asInt()
        elif unit_type == om.MFnNumericData.kChar:
            return plug.asChar()
        elif unit_type == om.MFnNumericData.kShort:
            return plug.asShort()  # Produces an error.
        elif unit_type == om.MFnNumericData.kLong:
            return plug.asDouble()
        elif unit_type == om.MFnNumericData.kInt:
            return plug.asInt()
        elif unit_type == om.MFnNumericData.kInt64:
            return plug.asInt64()
        elif unit_type == om.MFnNumericData.kFloat:
            return plug.asFloat()
        elif unit_type == om.MFnNumericData.kDouble:
            return plug.asDouble()

    @staticmethod
    def get_compound_attribute_value(plug, attribute):
        compound_fn = om.MFnCompoundAttribute(attribute)
        value = {}
        for child_index in range(compound_fn.numChildren()):
            child_attribute = compound_fn.child(child_index)
            child_node = plug.node()
            child_plug = om.MPlug(child_node, child_attribute)
            child_attribute = AttributeEntry(child_plug, child_attribute)
            child_attribute_name = child_attribute.attribute_name
            child_attribute_value = child_attribute.get_value()
            value[child_attribute_name] = child_attribute_value
        return value

    @staticmethod
    def get_typed_attribute_value(plug, attribute):
        typed_fn = om.MFnTypedAttribute(attribute)
        attribute_type = typed_fn.attrType()
        # print(typed_fn.name() + "\'s typed attribute has found a type of " + str(attribute_type) + ".")

        if attribute_type == om.MFnData.kNumeric:
            return AttributeEntry.get_numeric_attribute_value(plug, attribute)
        elif attribute_type == om.MFnData.kMatrix:
            matrix = om.MFnMatrixData(plug.asMObject()).matrix()
            matrix_multi_array = [[[] for i in range(4)] for i in range(4)]
            for x in range(4):
                for y in range(4):
                    matrix_multi_array[x][y] = matrix(x, y)
            return matrix_multi_array
        elif attribute_type == om.MFnData.kString:
            return plug.asString()
        elif attribute_type == om.MFnData.kStringArray:
            return om.MFnStringArrayData(plug.asMObject()).array()
        elif attribute_type == om.MFnData.kDoubleArray:
            return om.MFnDoubleArrayData(plug.asMObject()).array()
        elif attribute_type == om.MFnData.kFloatArray:
            return om.MFnFloatArrayData(plug.asMObject()).array()
        elif attribute_type == om.MFnData.kIntArray:
            return om.MFnIntArrayData(plug.asMObject()).array()
        elif attribute_type == om.MFnData.kPointArray:
            return om.MFnPointArrayData(plug.asMObject()).array()
        elif attribute_type == om.MFnData.kVectorArray:
            return om.MFnVectorArrayData(plug.asMObject()).array()
        elif attribute_type == om.MFnData.kMatrixArray:
            matrix_array = om.MFnMatrixArrayData(plug.asMObject()).array()
            return [AttributeEntry.get_typed_attribute_value(plug, attribute) for m in matrix_array]
        elif attribute_type == om.MFnData.kComponentList:
            raise NotImplementedError
        elif attribute_type == om.MFnData.kMesh:
            mesh = om.MFnMeshData(plug.asMObject()).create()
            return om.MFnDependencyNode(mesh).name()
        elif attribute_type == om.MFnData.kLattice:
            raise NotImplementedError
        else:
            raise NotImplementedError

    @staticmethod
    def get_unit_attribute_value(plug, attribute):
        unit_fn = om.MFnUnitAttribute(attribute)
        unit_type = unit_fn.unitType()
        # print(unit_fn.name() + "\'s unit attribute has found a type of " + str(unit_type) + ".")

        if unit_type == om.MFnUnitAttribute.kAngle:
            return plug.asMAngle().value()
        elif unit_type == om.MFnUnitAttribute.kDistance:
            return plug.asMDistance().value()
        elif unit_type == om.MFnUnitAttribute.kTime:
            return plug.asMTime().value()
        else:
            raise NotImplementedError

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.attribute == other.attribute
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.node_uuid) + hash(self.attribute_name)

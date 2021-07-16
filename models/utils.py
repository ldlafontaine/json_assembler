import maya.OpenMaya as om


def get_active_selection():
    active_selection = om.MSelectionList()
    om.MGlobal_getActiveSelectionList(active_selection)
    selection_iter = om.MItSelectionList(active_selection)
    selected_nodes = []
    while not selection_iter.isDone():
        dg_node = om.MObject()
        selection_iter.getDependNode(dg_node)
        selected_nodes.append(dg_node)
        selection_iter.next()
    return selected_nodes


def get_attributes(node):
    if type(node) != om.MObject:
        raise TypeError
    depend_fn = om.MFnDependencyNode(node)
    attribute_count = depend_fn.attributeCount()
    attributes = []
    for attribute_index in range(attribute_count):
        attribute = depend_fn.attribute(attribute_index)
        attribute_plug = depend_fn.findPlug(attribute, True)
        attributes.append(attribute_plug)
    return attributes


def get_node_name(node):
    if type(node) != om.MObject:
        raise TypeError
    dg_node_fn = om.MFnDependencyNode(node)
    return dg_node_fn.name()


def get_attribute_name(plug):
    if type(plug) != om.MPlug:
        raise TypeError
    return plug.partialName(False, False, False, False, False, True)


def get_attribute_long_name(plug):
    if type(plug) != om.MPlug:
        raise TypeError
    return plug.name()


def get_attribute_value(plug):
    if type(plug) != om.MPlug:
        raise TypeError

    attribute = plug.attribute()
    plug_type = attribute.apiTypeStr()

    results = []
    om.MGlobal_getFunctionSetList(attribute, results)
    attribute_fn = om.MFnAttribute(attribute)
    print(attribute_fn.name() + " has a plug type of " + plug_type + " and the following function sets:" + str(results) + ".")

    if attribute.hasFn(om.MFn.kCompoundAttribute):
        return get_compound_attribute_value(plug, attribute)
    elif attribute.hasFn(om.MFn.kUnitAttribute):
        return get_unit_attribute_value(plug, attribute)
    elif plug_type == "kNumericAttribute":
        return get_numeric_attribute_value(plug, attribute)
    elif plug_type == "kDoubleLinearAttribute":
        return plug.asDouble()
    elif plug_type == "kEnumAttribute":
        return plug.asInt()
    elif plug_type == "kTypedAttribute":
        return get_typed_attribute_value(plug, attribute)
    elif plug_type == "kGenericAttribute":
        print plug.info()
        return plug.asMObject()
    else:
        raise NotImplementedError


def get_numeric_attribute_value(plug, attribute):
    if type(plug) != om.MPlug or type(attribute) != om.MObject:
        raise TypeError

    numeric_fn = om.MFnNumericAttribute(attribute)
    unit_type = numeric_fn.unitType()

    print(numeric_fn.name() + " has a unit type of " + str(unit_type) + ".")

    if unit_type == om.MFnNumericData.kBoolean:
        return plug.asBool()
    elif unit_type == om.MFnNumericData.kByte:
        raise NotImplementedError
    elif unit_type == om.MFnNumericData.kChar:
        return plug.asChar()
    elif unit_type == om.MFnNumericData.kShort:
        return plug.asShort()
    elif unit_type == om.MFnNumericData.k2Short:
        raise NotImplementedError
    elif unit_type == om.MFnNumericData.k3Short:
        raise NotImplementedError
    elif unit_type == om.MFnNumericData.kLong:
        return plug.asDouble()
    elif unit_type == om.MFnNumericData.kInt:
        return plug.asInt()
    elif unit_type == om.MFnNumericData.k2Long:
        raise NotImplementedError
    elif unit_type == om.MFnNumericData.k2Int:
        raise NotImplementedError
    elif unit_type == om.MFnNumericData.k3Int:
        raise NotImplementedError
    elif unit_type == om.MFnNumericData.kInt64:
        return plug.asInt64()
    elif unit_type == om.MFnNumericData.kFloat:
        return plug.asFloat()
    elif unit_type == om.MFnNumericData.k2Float:
        raise NotImplementedError
    elif unit_type == om.MFnNumericData.k3Float:
        raise NotImplementedError
    elif unit_type == om.MFnNumericData.kDouble:
        return plug.asDouble()
    elif unit_type == om.MFnNumericData.k2Double:
        raise NotImplementedError
    elif unit_type == om.MFnNumericData.k3Double:
        raise NotImplementedError
    elif unit_type == om.MFnNumericData.k4Double:
        raise NotImplementedError
    elif unit_type == om.MFnNumericData.kAddr:
        raise NotImplementedError
    elif unit_type == om.MFnNumericData.kLast:
        raise NotImplementedError


def get_compound_attribute_value(plug, attribute):
    if type(plug) != om.MPlug or type(attribute) != om.MObject:
        raise TypeError

    compound_fn = om.MFnCompoundAttribute(attribute)
    value = {}
    for child_index in range(compound_fn.numChildren()):
        child_attribute = compound_fn.child(child_index)
        child_node = plug.node()
        child_plug = om.MPlug(child_node, child_attribute)
        child_attribute_value = get_attribute_value(child_plug)
        child_attribute_name = get_attribute_name(child_plug)
        value[child_attribute_name] = child_attribute_value
    return value


def get_typed_attribute_value(plug, attribute):
    if type(plug) != om.MPlug or type(attribute) != om.MObject:
        raise TypeError

    numeric_fn = om.MFnTypedAttribute(attribute)
    attribute_type = numeric_fn.type()

    if attribute_type == om.MFnNumericData.kInvalid:
        return "TYPED ATTRIBUTE"
    else:
        return "TYPED ATTRIBUTE"


def get_unit_attribute_value(plug, attribute):
    if type(plug) != om.MPlug or type(attribute) != om.MObject:
        raise TypeError

    unit_fn = om.MFnUnitAttribute(attribute)
    unit_type = unit_fn.unitType()

    if unit_type == om.MFnUnitAttribute.kInvalid:
        raise NotImplementedError
    elif unit_type == om.MFnUnitAttribute.kAngle:
        return plug.asMAngle().value()
    elif unit_type == om.MFnUnitAttribute.kDistance:
        return plug.asMDistance().value()
    elif unit_type == om.MFnUnitAttribute.kTime:
        return plug.asMTime().value()
    elif unit_type == om.MFnUnitAttribute.kLast:
        raise NotImplementedError


def register_selection_changed_callback(callback):
    event_message = om.MEventMessage()
    callback_id = event_message.addEventCallback("SelectionChanged", lambda *args: callback())
    return callback_id


def deregister_callbacks(callback_ids):
    message = om.MMessage()
    for callback_id in callback_ids:
        message.removeCallback(callback_id)

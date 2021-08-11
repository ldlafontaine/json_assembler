import maya.OpenMaya as om

from NodeEntry import NodeEntry


def get_nodes_from_selection():
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


def get_entries_from_nodes(nodes):
    return [NodeEntry(node) for node in nodes]


def get_entries_from_selection():
    nodes = get_nodes_from_selection()
    return get_entries_from_nodes(nodes)


def register_selection_changed_callback(callback):
    event_message = om.MEventMessage()
    callback_id = event_message.addEventCallback("SelectionChanged", lambda *args: callback())
    return callback_id


def deregister_callbacks(callback_ids):
    message = om.MMessage()
    for callback_id in callback_ids:
        message.removeCallback(callback_id)


def display_error(message):
    om.MGlobal_displayError(message)


def display_warning(message):
    om.MGlobal_displayWarning(message)

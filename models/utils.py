import maya.OpenMaya as om

from Attribute import Attribute
from Node import Node


def get_active_selection():
    active_selection = om.MSelectionList()
    om.MGlobal_getActiveSelectionList(active_selection)
    selection_iter = om.MItSelectionList(active_selection)
    selected_nodes = []
    while not selection_iter.isDone():
        dg_node = om.MObject()
        selection_iter.getDependNode(dg_node)
        node = Node(dg_node)
        selected_nodes.append(node)
        selection_iter.next()
    return selected_nodes


def register_selection_changed_callback(callback):
    event_message = om.MEventMessage()
    callback_id = event_message.addEventCallback("SelectionChanged", lambda *args: callback())
    return callback_id


def deregister_callbacks(callback_ids):
    message = om.MMessage()
    for callback_id in callback_ids:
        message.removeCallback(callback_id)

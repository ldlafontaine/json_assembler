import maya.OpenMaya as om
import json
import io
import sys

import utils


class File:

    def __init__(self):
        self.elements = {}

    def add_element(self, data):
        if type(data) == om.MPlug:
            node = data.node()
            node_name = utils.get_node_name(node)
            attribute_name = utils.get_attribute_name(data)
            try:
                attribute_value = utils.get_attribute_value(data)
            except:
                print("Error:", sys.exc_info()[0])
                return
            if node_name not in self.elements:
                self.elements[node_name] = {}
            self.elements[node_name][attribute_name] = attribute_value

    def remove_element(self, data):
        if type(data) == om.MPlug:
            node = data.node()
            node_name = utils.get_node_name(node)
            attribute_name = utils.get_attribute_name(data)
            if node_name in self.elements:
                self.elements[node_name].pop(attribute_name, None)
                if not len(self.elements[node_name].keys()) > 0:
                    self.elements.pop(node_name, None)

    def clear_elements(self):
        self.elements = {}

    def get_formatted_text(self):
        if len(self.elements.keys()) > 0:
            return json.dumps(self.elements, indent=4)
        else:
            return ""

    def save_to_file(self, path, include_indentation):
        with io.open(path, 'w', encoding='utf-8') as f:
            if include_indentation:
                f.write(json.dumps(self.elements, ensure_ascii=False, indent=4))
            else:
                f.write(json.dumps(self.elements, ensure_ascii=False))

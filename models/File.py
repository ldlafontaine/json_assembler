import maya.OpenMaya as om
import json
import io
import sys

from Attribute import Attribute
from Node import Node


class File:

    def __init__(self):
        self.data = {}

    def add_data(self, new_data):
        self.merge_dictionaries(self.data, new_data)

    def remove_data(self, subtraction_data):
        self.data = {key: value for key, value in self.subtraction(self.data, subtraction_data)}

    def clear_data(self):
        self.data = {}

    @staticmethod
    def merge_dictionaries(a, b):
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    File.merge_dictionaries(a[key], b[key])
                elif isinstance(a[key], set) and isinstance(b[key], set):
                    a[key].update(b[key])
            else:
                a[key] = b[key]

    @staticmethod
    def subtraction(data, subtraction_data):
        for key, value in data.items():
            if key not in subtraction_data:
                if isinstance(value, dict):
                    value = {child_key: child_value for child_key,
                             child_value in File.subtraction(value, subtraction_data)}
                yield [key, value]

    def encode_data(self, data):
        if isinstance(data, dict):
            return self.encode_dict(data)
        elif isinstance(data, Node):
            return data.name
        elif isinstance(data, Attribute):
            return data.name
        else:
            return data

    def encode_dict(self, data):
        encoded_dict = {}
        for key, value in data.items():
            encoded_key = self.encode_data(key)
            encoded_value = self.encode_data(value)
            encoded_dict[encoded_key] = encoded_value
        return encoded_dict

    def get_formatted_text(self):
        encoded_data = self.encode_data(self.data)
        if len(self.data.keys()) > 0:
            return json.dumps(encoded_data, indent=4)
        else:
            return ""

    def save_to_file(self, path, include_indentation):
        encoded_data = self.encode_data(self.data)
        with io.open(path, 'w', encoding='utf-8') as f:
            if include_indentation:
                f.write(json.dumps(encoded_data, ensure_ascii=False, indent=4))
            else:
                f.write(json.dumps(encoded_data, ensure_ascii=False))

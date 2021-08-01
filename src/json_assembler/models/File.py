import json
import io
from collections import OrderedDict


class File:

    def __init__(self):
        self.entries = set()

    def add_entry(self, entry):
        self.entries.add(entry)

    def remove_entry(self, entry):
        self.entries.remove(entry)

    def add_entries(self, addition_data):
        self.entries.update(addition_data)

    def remove_entries(self, subtraction_data):
        self.entries = self.entries.difference(subtraction_data)

    def clear_entries(self):
        self.entries = set()

    def encode_data(self):
        entry_groups = OrderedDict()
        for item in sorted(self.entries, key=lambda x: x.position):
            if item.parent not in entry_groups:
                entry_groups[item.parent] = OrderedDict()
            entry_groups[item.parent][item] = item.value

        if None in entry_groups:
            return self.encode_data_level(entry_groups[None], entry_groups)
        else:
            return {}

    def encode_data_level(self, level, groups):
        encoded_data = OrderedDict()
        for key, value in level.items():
            encoded_key = key.title
            if key in groups:
                # Add as parent.
                encoded_data[encoded_key] = self.encode_data_level(groups[key], groups)
            else:
                # Add as value.
                encoded_data[encoded_key] = value
        return encoded_data

    def get_formatted_text(self, include_indentation, indentation_size):
        encoded_data = self.encode_data()
        if len(encoded_data) > 0:
            if include_indentation:
                return json.dumps(encoded_data, indent=indentation_size)
            else:
                return json.dumps(encoded_data)
        else:
            return ""

    def save_to_file(self, path, include_indentation, indentation_size):
        encoded_data = self.encode_data()
        with io.open(path, 'w', encoding='utf-8') as f:
            if include_indentation:
                f.write(json.dumps(encoded_data, ensure_ascii=False, indent=indentation_size))
            else:
                f.write(json.dumps(encoded_data, ensure_ascii=False))

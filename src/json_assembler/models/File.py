import json
import io

from EntryEncoder import EntryEncoder
from EntryPreprocessor import EntryPreprocessor


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

    def get_children(self, entry):
        children = []
        for child_entry in [x for x in self.entries if x.parent == entry]:
            children.append(child_entry)
            children.extend(self.get_children(child_entry))
        return children

    def encode(self, include_indentation, indentation_size):
        preprocessed_entries = EntryPreprocessor.preprocess(self.entries)
        if len(preprocessed_entries) > 0:
            if include_indentation:
                return json.dumps(preprocessed_entries, ensure_ascii=False, cls=EntryEncoder, indent=indentation_size)
            else:
                return json.dumps(preprocessed_entries, ensure_ascii=False, cls=EntryEncoder)
        else:
            return ""

    def save_to_file(self, path, include_indentation, indentation_size):
        with io.open(path, 'w', encoding='utf-8') as f:
            f.write(self.encode(include_indentation, indentation_size))

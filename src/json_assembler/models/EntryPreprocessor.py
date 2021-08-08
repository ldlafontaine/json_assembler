from collections import OrderedDict


class EntryPreprocessor:

    def __init__(self, entries):
        self.entries_by_parent = OrderedDict()

    @classmethod
    def preprocess(cls, entries):
        preprocessor = cls(entries)

        # Group entries by parent.
        for item in sorted(entries, key=lambda x: x.position):
            if item.parent not in preprocessor.entries_by_parent:
                preprocessor.entries_by_parent[item.parent] = []
            preprocessor.entries_by_parent[item.parent].append(item)

        # Recursively preprocess the entries, starting from those at the root level.
        root = None
        if root in preprocessor.entries_by_parent:
            preprocessed_root = OrderedDict()
            for entry in preprocessor.entries_by_parent[root]:
                key, value = preprocessor.preprocess_entry(entry)
                preprocessed_root[key] = value
            return preprocessed_root
        else:
            return {}

    def preprocess_entry(self, entry):
        if entry in self.entries_by_parent:
            if isinstance(entry.value, list):
                value = self.preprocess_list(self.entries_by_parent[entry])
            else:
                value = self.preprocess_dictionary(self.entries_by_parent[entry])
        else:
            value = entry.value
        return entry, value

    def preprocess_list(self, entries):
        preprocessed_entries = [self.preprocess_entry(x) for x in entries]
        return [{key: value} for key, value in preprocessed_entries]

    def preprocess_dictionary(self, entries):
        preprocessed_dictionary = OrderedDict()
        for entry in entries:
            key, value = self.preprocess_entry(entry)
            preprocessed_dictionary[key] = value
        return preprocessed_dictionary

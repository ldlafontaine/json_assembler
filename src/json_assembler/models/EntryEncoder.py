import json

from Entry import Entry


class EntryEncoder(json.JSONEncoder):

    def get_count(self, o):
        if isinstance(o, list):
            return sum([self.get_count(item) for item in o])
        elif isinstance(o, dict):
            return sum([self.get_count(item) for item in o.values()])
        else:
            return 1

    def get_indent_size(self, o):
        count = self.get_count(o)
        if count > 1:
            return self.indent
        else:
            return 0

    def add_indentation(self, string, size, depth):
        if size:
            return string + "\n" + ((depth * size) * " ")
        else:
            return string

    def encode_dict(self, o, depth=0):
        string = "{"
        indent_size = self.get_indent_size(o)
        for count, (key, value) in enumerate(o.items()):
            inner_depth = depth + 1
            string = self.add_indentation(string, indent_size, inner_depth)
            encoded_key = super(EntryEncoder, self).encode(key)
            encoded_value = self.encode(value, inner_depth)
            string = string + "%s: %s" % (encoded_key, encoded_value)
            if count < len(o) - 1:
                string = string + ", "
        string = self.add_indentation(string, indent_size, depth)
        string = string + "}"
        return string

    def encode_list(self, o, depth=0):
        string = "["
        indent_size = self.get_indent_size(o)
        for count, item in enumerate(o):
            inner_depth = depth + 1
            string = self.add_indentation(string, indent_size, inner_depth)
            string = string + self.encode(item, inner_depth)
            if count < len(o) - 1:
                string = string + ", "
        string = self.add_indentation(string, indent_size, depth)
        string = string + "]"
        return string

    def encode(self, o, depth=0):
        if isinstance(o, dict):
            return self.encode_dict(o, depth)
        elif isinstance(o, list):
            return self.encode_list(o, depth)
        else:
            return super(EntryEncoder, self).encode(o)

    def default(self, o):
        if isinstance(o, Entry):
            return o.title
        else:
            return super(EntryEncoder, self).default(o)

from datetime import datetime


class Entry(object):

    def __init__(self, title="New Entry"):
        self.title = title
        self.parent = None
        self.position = 0
        self.value = None
        self.created_at = datetime.now()

    def get_icon_path(self):
        return ":fileNew.png"

    def is_string(self):
        if isinstance(self.value, str):
            return True
        return False

    def is_number(self):
        number_types = [int, float, complex]
        for number_type in number_types:
            if isinstance(self.value, number_type):
                return True
        return False

    def is_object(self):
        if isinstance(self.value, dict):
            return True
        return False

    def is_array(self):
        if isinstance(self.value, list):
            return True
        return False

    def is_bool(self):
        if isinstance(self.value, bool):
            return True
        return False

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.created_at == self.created_at
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.created_at)

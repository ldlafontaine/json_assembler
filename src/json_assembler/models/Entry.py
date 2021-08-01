class Entry(object):

    def __init__(self, title):
        self.title = title
        self.parent = None
        self.position = 0
        self.value = None

    def get_icon_path(self):
        return ":fileNew.png"

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.title == self.title
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.title)

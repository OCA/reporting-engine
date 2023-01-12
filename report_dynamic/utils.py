class Header:
    def __init__(self, child=False, parent=False):
        self.value = 0
        self.base_value = 0
        self.child = child
        if parent:
            parent.child = self

    @property
    def next(self):
        self.value += 1
        if self.child:
            self.child.reset()
        return self.value

    @property
    def previous(self):
        if self.value:
            self.value -= 1
        return self.value

    def reset(self):
        self.value = self.base_value
        if self.child:
            self.child.reset()
        return self.value

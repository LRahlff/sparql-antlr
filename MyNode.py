class MyNode:
    def __init__(self, type, name):
        self.type = type
        self.name = name

    def __eq__(self, other):
        return self.type == other.type and self.name == other.name

    def __hash__(self):
        return (self.type).__hash__() + (self.name).__hash__()

    def __str__(self):
        return self.type + '_' + self.name

    def is_var(self):
        return self.type == 'var'

    def is_same(self):
        return self.type == 'nothing' and (self.name == 'IN' or self.name == '=')

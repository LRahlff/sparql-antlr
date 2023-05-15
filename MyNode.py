class MyNode:
    def __init__(self, type, name, new):
        self.type = type
        self.name = name
        self.new = new

    def __eq__(self, other):
        # if self.type == 'konzept' and (self.name == 'Parameter' or self.name == 'Material'):
        #     return self.type == other.type and self.name == other.name and self.new == other.new
        return self.type == other.type and self.name == other.name

    def __hash__(self):
        return (self.type).__hash__() + (self.name).__hash__()

    def __str__(self):
        return self.type + '_' + self.name

    def is_var(self):
        return self.type == 'var'

    def is_same(self):
        return self.type == 'nothing' and (self.name == 'IN' or self.name == '=')


from enum import Enum
class Relation(Enum):
    LESS = 1
    EQUAL = 2
    GREATER = 3

class MyNode:

    def __init__(self, nodetype, name, new):
        self.type = nodetype
        self.name = name
        self.new = new
        self.rel = Relation.EQUAL
        self.nr_of_interval = 10

    def __eq__(self, other):
        return self.type == other.type and self.name == other.name

    def __hash__(self):
        return self.type.__hash__() + self.name.__hash__()

    def __str__(self):
        return self.type + '_' + self.name

    def is_var(self):
        return self.type == 'var'

    def is_same(self):
        return self.type == 'nothing' and (self.name == 'IN' or self.name == '=')

    def is_less(self):
        return self.type == 'nothing' and (self.name == '<=' or self.name == '<')

    def is_greater(self):
        return self.type == 'nothing' and (self.name == '>=' or self.name == '>')

    def setLess(self, interval):
        self.rel = Relation.LESS
        self.nr_of_interval = interval
    def setGreater(self, interval):
        self.rel = Relation.GREATER
        self.nr_of_interval = interval

    def setNrInInterval(self, nr):
        self.nr_of_interval = nr
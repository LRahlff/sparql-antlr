from antlr4 import ParseTreeListener

from MyNode import MyNode
from gen.SparqlLexer import SparqlLexer
from gen.SparqlParser import SparqlParser

# from colorama import Fore, Style

class MyWalkListener(ParseTreeListener):

    def __init__(self, tree):
        self.tree = tree
        self.depth = 0
        self.error = False
        self.subject = []
        self.predicate = [None]
        self.object = [None]
        self.searching_for = []
        self.lastListNode = []
        self.update_mode_is_set = False

    def exitEveryRule(self, ctx):
        self.depth -= 1

    def enterEveryRule(self, ctx):
        self.depth += 1
        pre = ''
        i = 0
        while (i < self.depth):
            pre = pre + '  '
            i = i + 1
        print(pre + str(type(ctx)) + " " + ctx.getText())

    def visitErrorNode(self, node):
        print('visitErrorNode ' + str(self.depth) + '---------------------------------' )

    def visitTerminal(self, node):
        print('TerminalNode   ' + str(self.depth) + ' ' + str(type(node)) + '  ' + node.getText())

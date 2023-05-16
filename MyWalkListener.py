from antlr4 import ParseTreeListener

from MyNode import MyNode
from gen.SparqlLexer import SparqlLexer
from gen.SparqlParser import SparqlParser

# import colorama
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
        if isinstance(ctx, SparqlParser.TriplesSameSubjectContext):
            self.object.pop()
            self.object.append(None)
            self.predicate.pop()
            self.predicate.append(None)
            self.subject.pop()
            return
        # if isinstance(ctx, SparqlParser.VerbContext):
        #     self.predicate.pop()
        #     return
        # if isinstance(ctx, SparqlParser.Object_Context):
        #     self.object.pop()
        #     return
        if isinstance(ctx, SparqlParser.Filter_Context):
            self.object.pop()
            self.predicate.pop()
            self.subject.pop()
            return
        if isinstance(ctx, SparqlParser.PropertyListNotEmptyContext):
            self.lastListNode.pop()
            return
        if isinstance(ctx, SparqlParser.RelationalExpressionContext):
            self.lastListNode.pop()
            return
        if isinstance(ctx, SparqlParser.VerbContext):
            self.terminalType = 'nothing'
            return
        if isinstance(ctx, SparqlParser.Var_Context):
            self.terminalType = 'nothing'
            return
        if isinstance(ctx, SparqlParser.PrefixedNameContext):
            self.terminalType = 'nothing'
            return
        if isinstance(ctx, SparqlParser.String_Context):
            self.terminalType = 'nothing'
            return
        if isinstance(ctx, SparqlParser.NumericLiteralContext):
            self.terminalType = 'nothing'
            return

    def enterEveryRule(self, ctx):
        self.depth += 1
        # pre = ''
        # i = 0
        # while(i< self.depth):
        #     pre = pre + '  '
        #     i = i+1
        # print(pre + ctx.getText())
        # if isinstance(ctx, SparqlParser.TriplesBlockMyContext):
        #     print("YEA")
        if isinstance(ctx, SparqlParser.TriplesSameSubjectContext):
            # self.searching_for.append(3)
            # self.searching_for.append(2)
            self.searching_for.append(1)
            return
        if isinstance(ctx, SparqlParser.VerbContext):
            self.predicate.pop()
            self.searching_for.append(2)
            self.terminalType = 'verb'
            return
        if isinstance(ctx, SparqlParser.Object_Context):
            self.object.pop()
            self.searching_for.append(3)
            return
        if isinstance(ctx, SparqlParser.Filter_Context):
            self.searching_for.append(3)
            self.searching_for.append(2)
            self.searching_for.append(1)
            return
        if isinstance(ctx, SparqlParser.PropertyListNotEmptyContext):
            self.lastListNode.append('PropertyListNotEmptyContext')
            return
        if isinstance(ctx, SparqlParser.RelationalExpressionContext):
            self.lastListNode.append('RelationalExpressionContext')
            return
        # if isinstance(ctx, SparqlParser.VerbContext):
        #     self.terminalType = 'verb'
        #     return
        if isinstance(ctx, SparqlParser.Var_Context):
            self.terminalType = 'var'
            return
        if isinstance(ctx, SparqlParser.PrefixedNameContext):
            self.terminalType = 'konzept'
            return
        if isinstance(ctx, SparqlParser.String_Context):
            self.terminalType = 'string'
            return
        if isinstance(ctx, SparqlParser.NumericLiteralContext):
            self.terminalType = 'numeric'
            return
        pass

    def visitErrorNode(self, node):
        # print('visitErrorNode ' + str(self.depth) + '---------------------------------')
        # print(Fore.RED + 'visitErrorNode ' + str(self.depth) + '---------------------------------' + Style.RESET_ALL)
        self.error = True
        pass

    def visitTerminal(self, node):
        # print('TerminalNode   ' + str(self.depth) + ' ' + node.getText())

        name = node.getText()
        ignore = {'.', '(', ')', 'FILTER', ';'}
        if name in ignore:
            # print("nothing here to check for")
            return

        if name == '#update_new':
            self.update_mode_is_set = True
            return
        if name == '#update_end':
            self.update_mode_is_set = False
            return

        if name == ',' and self.lastListNode[len(self.lastListNode)-1] == 'RelationalExpressionContext':
            self.object.pop()
            self.searching_for.append(3)
            return

        if len(self.searching_for)<= 0:
            # print("test nothing to search for")
            return
        if self.terminalType == 'konzept':
            name = name[1:]
        elif self.terminalType == 'var':
            name = name[1:]
        elif self.terminalType == 'string':
            name = name[1:-1]

        gram = self.searching_for.pop()

        match gram:
            case 1:
                self.subject.append(MyNode(self.terminalType, name, self.update_mode_is_set))
            case 2:
                self.predicate.append(MyNode(self.terminalType, name, self.update_mode_is_set))
            case 3:
                self.object.append(MyNode(self.terminalType, name, self.update_mode_is_set))
                subj = self.subject[len(self.subject)-1]
                pred = self.predicate[len(self.predicate)-1]
                obj = self.object[len(self.object)-1]
                self.tree.add(subj, pred, obj)

        pass


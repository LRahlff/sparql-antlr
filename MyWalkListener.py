import antlr4
from antlr4 import ParseTreeListener

from MyNode import MyNode, Relation
from gen import SparqlLexer
from gen.SparqlParser import SparqlParser

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
        self.nr_of_values_in_interval = 10
        self.get_nr_of_interval = False

    def exitEveryRule(self, ctx):
        self.depth -= 1
        if isinstance(ctx, SparqlParser.TriplesSameSubjectContext):
            self.object.pop()
            self.object.append(None)
            self.predicate.pop()
            self.predicate.append(None)
            self.subject.pop()
            return
        if isinstance(ctx, SparqlParser.Filter_Context):
            self.object.pop()
            self.predicate.pop()
            self.subject.pop()
            return
        if isinstance(ctx, SparqlParser.PropertyListNotEmptyContext):
            self.lastListNode.pop()
            return
        if isinstance(ctx, SparqlParser.InclusionExpressionContext):
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
        if isinstance(ctx, SparqlParser.CompilerSetInstructionContext):
            self.get_nr_of_interval = False
            return

    def enterEveryRule(self, ctx):
        self.depth += 1
        # pre = ''
        # i = 0
        # while(i< self.depth):
        #     pre = pre + '  '
        #     i = i+1
        # print(pre + str(type(ctx)) + " " + ctx.getText())
        if isinstance(ctx, SparqlParser.TriplesSameSubjectContext):
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
        if isinstance(ctx, SparqlParser.InclusionExpressionContext):
            self.lastListNode.append('InclusionExpressionContext')
            return
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
        if isinstance(ctx, SparqlParser.CompilerSetInstructionContext):
            name = ctx.getText()
            if name.find("update_amount_values") == 0:
                self.get_nr_of_interval = True
                return
            if name == 'update_new':
                self.update_mode_is_set = True
                return
            if name == 'update_end':
                self.update_mode_is_set = False
                return
        pass

    def visitErrorNode(self, node):

        # print(str(type(node)) + " " + node.getText())
        # print('visitErrorNode ' + str(self.depth) + '---------------------------------')
        # print(Fore.RED + 'visitErrorNode ' + str(self.depth) + '---------------------------------' + Style.RESET_ALL)
        self.error = True
        pass

    def visitTerminal(self, node):
        # print('TerminalNode   ' + str(self.depth) + ' ' + str(type(node)) + '  ' + node.getText())
        name = node.getText()
        ignore = {'.', '(', ')', 'FILTER', ';'}
        if name in ignore:
            # print("nothing here to check for")
            return
        # print(type(node))
        if self.get_nr_of_interval:
            try:
                self.nr_of_values_in_interval = int(node.getText())
            except:
                # print("error")
                pass
        #     self.update_mode_is_set = False
        if name == ',' and self.lastListNode[len(self.lastListNode)-1] == 'InclusionExpressionContext':
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
                if node.getText() == '<' or node.getText() == '<=':
                    rel = Relation.LESS
                elif node.getText() == '>' or node.getText() == '>=':
                    rel = Relation.GREATER
                else:
                    rel = Relation.EQUAL
                self.predicate.append(MyNode(self.terminalType, name, self.update_mode_is_set, rel, self.nr_of_values_in_interval))
            case 3:
                self.object.append(MyNode(self.terminalType, name, self.update_mode_is_set))
                subj = self.subject[len(self.subject)-1]
                pred = self.predicate[len(self.predicate)-1]
                pred.setNrInInterval(self.nr_of_values_in_interval)
                obj = self.object[len(self.object)-1]
                obj.setNrInInterval(self.nr_of_values_in_interval)
                self.tree.add(subj, pred, obj)

        pass


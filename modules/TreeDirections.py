from antlr4 import *
from antlr4 import ParseTreeVisitor
from modules.Symbol import Symbol, SymboTable
from modules.Type import TypeSystem
from yapl.YAPLParser import YAPLParser


class TreeDirections(ParseTreeVisitor):
    def __init__(self,symbol_table):
        self.symbol_table = symbol_table
        self.type_system = TypeSystem()
        self.triplets = []
        self.temporals = []

    def visit(self, tree):
        if isinstance(tree, YAPLParser.ProgramContext):
            result = self.visitProgram(tree)
        elif isinstance(tree, YAPLParser.ClassDefContext):
            result = self.visitClassDef(tree)
        elif isinstance(tree, YAPLParser.FeatureDefContext):
            result = self.visitFeatureDef(tree)
        elif isinstance(tree, YAPLParser.FormalDefContext):
            result = self.visitFormalDef(tree)
        elif isinstance(tree, YAPLParser.ExprContext):
            result = self.visitExpr(tree)
        else:
            result = self.visitChildren(tree)

        return result
    
    def visitChildren(self, node):
        result = None
        if not isinstance(node, TerminalNode) and node.children:
            for child in node.children:  # Recorre los hijos en orden inverso
                result = self.visit(child)

        # Si es terminal regresar el tipo
        if isinstance(node, TerminalNode):
            visitTerminal = self.visitTerminal(node)

            result = visitTerminal
            pass
        
        return result


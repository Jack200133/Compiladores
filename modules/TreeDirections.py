from antlr4 import *
from antlr4 import ParseTreeVisitor
from modules.Symbol import Symbol, SymboTable
from modules.Type import TypeSystem
from modules.Tripleta import Tripleta
from modules.Temporal import Temporal
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
    
    def visitTerminal(self, ctx: TerminalNode):
        symbol_type = ctx.getSymbol().type
        obj = ctx.getText()

        temp = Temporal(len(self.temporals), obj)
        if symbol_type == YAPLParser.INT \
        or symbol_type == YAPLParser.TRUE \
        or symbol_type == YAPLParser.FALSE \
        or symbol_type == YAPLParser.STRING:
            self.temporals.append(temp)
            return temp
        else:
            # Buscar su tipo en la tabla de símbolos
            symbol = self.symbol_table.lookup(ctx.getText())
            if symbol is not None:

                temp.datos = symbol
                self.temporals.append(temp)
                return temp
            else:
                return None
            
    def visitProgram(self, ctx: YAPLParser.ProgramContext):
        for child in ctx.children:
            self.visit(child)
        return None
    
    def visitClassDef(self, ctx: YAPLParser.ClassDefContext):
        for child in ctx.children:
            self.visit(child)
        return None
    
    def visitFeatureDef(self, ctx: YAPLParser.FeatureDefContext):

        if ctx.LPAREN():
            return None
        else:
            obj = ctx.getText()
            children = []
            for child in ctx.children:
                chil = self.visit(child)
                if chil is not None:
                    children.append(chil)
            
        return None
    
    def visitFormalDef(self, ctx: YAPLParser.FormalDefContext):
        return None
    
    def visitExpr(self, ctx: YAPLParser.ExprContext):
        if not isinstance(ctx, YAPLParser.ExprContext):
            return
        obj = ctx.getText()

        children = []
        for child in ctx.children:
            chil = self.visit(child)
            if chil is not None:
                children.append(chil)

        newT = Tripleta("VAR", children[0])

        return newT


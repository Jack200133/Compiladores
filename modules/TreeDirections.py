from antlr4 import *
from antlr4 import ParseTreeVisitor
from modules.Symbol import Symbol, SymboTable
from modules.Type import TypeSystem
from modules.Tripleta import Tripleta
from modules.Temporal import Temporal
from yapl.YAPLParser import YAPLParser 




class TreeDirections(ParseTreeVisitor):
    def __init__(self,symbol_table : SymboTable):
        self.symbol_table = symbol_table
        self.type_system = TypeSystem()
        self.triplets = []
        self.temporals = []
        self.sp = "_GLOBAL"
        self.clean()

    def clean(self):
        with open('./output/3D/tripletas.txt', 'w') as file:
            pass

    def write(self,triplet):
        with open('./output/3D/tripletas.txt', 'a') as file:
            file.write(str(triplet) + '\n')

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
        obj = node.getText()
        if not isinstance(node, TerminalNode) and node.children:
            for child in node.children:  # Recorre los hijos en orden inverso
                result = self.visit(child)

        # Si es terminal regresar el tipo
        else:
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
            self.write(f"\tt{temp.number} = {temp.datos}")
            return temp
        else:
            # Buscar su tipo en la tabla de símbolos
            symbol = self.symbol_table.lookup(ctx.getText())
            if symbol is not None and symbol.definicion is not "ClassDef":

                temp.datos = f"sp{self.sp}[{symbol.memory_position}]"
                self.write(f"\tt{temp.number} = {temp.datos}")
                self.temporals.append(temp)
                return temp
            else:
                return None
            
    def visitProgram(self, ctx: YAPLParser.ProgramContext):
        for child in ctx.children:
            self.visit(child)
        return None
    
    def visitClassDef(self, ctx: YAPLParser.ClassDefContext):
        class_name = ctx.TYPE_ID()[0].getText()
        inherits_from = None  # Inicializamos la variable
        obj = ctx.getText()

        trip = f"CLASS {class_name}"
        if ctx.INHERITS():  # Si hay herencia
            # Obtenemos el tipo padre
            inherits_from = ctx.TYPE_ID()[1].getText()
            trip += f" INHERITS ['{inherits_from}']"

        symbol = self.symbol_table.lookup(class_name)
        class_scope = self.symbol_table.current_scope
        for scope in symbol.myscope.children:
            if scope.name == class_name:
                class_scope = scope
                break
        self.symbol_table.current_scope = class_scope
        #self.symbol_table.current_scope = symbol

        self.write(trip)
        for child in ctx.children:
            self.visit(child)

        self.symbol_table.current_scope = self.symbol_table.current_scope.parent

        trip2 = f"END CLASS {class_name}\n"
        self.write(trip2)
        return None
    
    def visitFeatureDef(self, ctx: YAPLParser.FeatureDefContext):
        obj = ctx.getText()
        name = ctx.OBJECT_ID().getText()
        if ctx.LPAREN():
            
            self.sp = ""
            simbol: Symbol = self.symbol_table.lookup(name)
            function_scope = self.symbol_table.current_scope
            self.write(f"\nFUNCTION {simbol.scope}")
            for scope in simbol.myscope.children:
                if scope.name == name:
                    function_scope = scope
                    break
            self.symbol_table.current_scope = function_scope
            children = []
            for child in ctx.children:
                chil = self.visit(child)
                if chil is not None:
                    children.append(chil)

            self.symbol_table.current_scope = self.symbol_table.current_scope.parent
            self.sp = "_GLOBAL"

        else:
            children = []
            for child in ctx.children:
                chil = self.visit(child)
                if chil is not None:
                    children.append(chil)
            
            sms = f"ASSIGN t{children[0].number} t{children[1].number}"
            temp = Temporal(len(self.temporals), sms)
            tempis = f"\tt{temp.number} = {sms}"
            self.temporals.append(temp)
            self.write(tempis)


            
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


        if ctx.PLUS():
            triplet = f"PLUS "
            temporal = Temporal(len(self.temporals), obj)

        if ctx.MINUS():
            triplet = f"MINUS "
            temporal = Temporal(len(self.temporals), obj)
        
        if ctx.MULT():
            triplet = f"MULT "
            temporal = Temporal(len(self.temporals), obj)
        
        if ctx.DIV():
            triplet = f"DIV "
            temporal = Temporal(len(self.temporals), obj)

        if ctx.EQ():
            triplet = f"EQ t{children[0].number} t{children[1].number}"
            temporal = Temporal(len(self.temporals), triplet)
            sms = f"\tt{temporal.number} = t{children[0].number} == t{children[1].number}"
            self.write(sms)
        
        return children[0]


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
        self.labels = []
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
            if symbol is not None and symbol.isvar:
                temp.datos = f"sp{self.sp}[{symbol.memory_position}]"
                ##self.write(f"\t{symbol.name} t{temp.number} = {temp.datos}")
                ##self.temporals.append(temp)
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
            self.write(f"RETURN t{children[-1].number}\n")
            self.write(f"END FUNCTION {simbol.scope}\n")

            self.symbol_table.current_scope = self.symbol_table.current_scope.parent
            self.sp = "_GLOBAL"

        else:
            children = []
            for child in ctx.children:
                chil = self.visit(child)
                if chil is not None:
                    children.append(chil)
            if len(children) == 1:
                sms = f"ASSIGN t{children[0].number} {0}"
                sms = f"{children[0].datos} = {0}"
                temp = Temporal(len(self.temporals), sms)
                tempis = f"\t{sms}"
                self.temporals.append(temp)
                self.write(sms)
                return temp
            sms = f"ASSIGN t{children[0].number} t{children[1].number}"
            sms = f"{children[0].datos} = t{children[1].number}"
            temp = Temporal(len(self.temporals), sms)
            tempis = f"\t{sms}"
            self.temporals.append(temp)
            self.write(tempis)


            
        return None
    
    def visitFormalDef(self, ctx: YAPLParser.FormalDefContext):
        return None
    
    def visitExpr(self, ctx: YAPLParser.ExprContext):
        if not isinstance(ctx, YAPLParser.ExprContext):
            return
        obj = ctx.getText()

        #expr  (AT TYPE_ID)? DOT OBJECT_ID LPAREN  (expr (COMMA expr)*)? RPAREN
        if ctx.DOT():
            children = []
            for child in ctx.getChildren():
                children.append(child)
            params = []
            for index, child in enumerate(children):

                if isinstance(child, YAPLParser.ExprContext):

                    params.append({"expr": index})

            funcChild = params.pop(0)
            visitFunc = self.visit(children[funcChild["expr"]])
            
            tempsParams = []
            for param in params:
                visit = self.visit(children[param["expr"]])
                tempsParams.append(visit)
            
            for index, param in enumerate(tempsParams):
                sms = f"\tPARAM t{param.number}"
                self.write(sms)

            isAtt = "."
            if ctx.AT():
                nameatt = ctx.TYPE_ID()[0].getText()
                isAtt = f".{nameatt}."
            
            triplet = f"CALL {visitFunc.datos}{isAtt}{ctx.OBJECT_ID()[0].getText()} {len(tempsParams)}"
            sms = f"\tt{len(self.temporals)} = {triplet}"
            self.write(sms)
            temporal = Temporal(len(self.temporals), sms)
            self.temporals.append(temporal)
            return temporal

        # OBJECT_ID LPAREN (expr (COMMA expr)*)? RPAREN
        elif ctx.OBJECT_ID() and ctx.LPAREN():
            children = []
            for child in ctx.getChildren():
                children.append(child)
            params = []
            for index, child in enumerate(children):

                if isinstance(child, YAPLParser.ExprContext):

                    params.append({"expr": index})
            tempsParams = []
            for param in params:
                visit = self.visit(children[param["expr"]])
                tempsParams.append(visit)
            
            for index, param in enumerate(tempsParams):
                sms = f"\tPARAM t{param.number}"
                self.write(sms)
            
            triplet = f"CALL {ctx.OBJECT_ID()[0].getText()} {len(tempsParams)}"
            sms = f"\tt{len(self.temporals)} = {triplet}"
            self.write(sms)
            temporal = Temporal(len(self.temporals), sms)
            self.temporals.append(temporal)
            return temporal

        #IF expr THEN expr ELSE expr FI
        if ctx.IF():    
            condition = ctx.children[1]
            condition= self.visit(condition)

            trulabel = f"LABEL_L{len(self.labels)}"
            self.labels.append(trulabel)
            falselabel = f"LABEL_L{len(self.labels)}"
            self.labels.append(falselabel)
            endIfLabel = f"LABEL_L{len(self.labels)}"
            self.labels.append(endIfLabel)

            self.write(f"\tIF t{condition.number} GOTO {trulabel}")
            self.write(f"\tGOTO {falselabel}")
            self.write(f"{trulabel}:")
            trueVisit = self.visit(ctx.children[3])
            self.write(f"\tGOTO {endIfLabel}")
            self.write(f"{falselabel}:")
            falseVisit = self.visit(ctx.children[5])

            self.write(f"{endIfLabel}:")

            pass
            
        #OBJECT_ID LPAREN (expr (COMMA expr)*)? RPAREN
        elif ctx.OBJECT_ID() and ctx.LPAREN():
            children = []
            for child in ctx.getChildren():
                children.append(child)
            params = []
            for index, child in enumerate(children):

                if isinstance(child, YAPLParser.ExprContext):

                    params.append({"expr": index})
            tempsParams = []
            for param in params:
                visit = self.visit(children[param["expr"]])
                tempsParams.append(visit)
            
            for index, param in enumerate(tempsParams):
                sms = f"\tPARAM t{param.number}"
                self.write(sms)
            
            triplet = f"CALL {ctx.OBJECT_ID()[0].getText()} {len(tempsParams)}"
            sms = f"\tt{len(self.temporals)} = {triplet}"
            self.write(sms)
            temporal = Temporal(len(self.temporals), sms)
            self.temporals.append(temporal)
            return temporal
            

        #WHILE expr LOOP expr POOL
        

        elif ctx.LBRACE():
            children = []
            for child in ctx.getChildren():
                children.append(child)

            exprs = []
            for index, child in enumerate(children):
                    
                    if isinstance(child, YAPLParser.ExprContext):
    
                        exprs.append({"expr": index})
            
            cisitedExprs = []
            for expr in exprs:
                visit = self.visit(children[expr["expr"]])
                cisitedExprs.append(visit)

            return cisitedExprs[-1]
        
        elif ctx.LET():
            children = []
            for child in ctx.getChildren():
                children.append(child)

            asignaciones = []
            new_simbol = 0
            for index, child in enumerate(children):

                if isinstance(child, YAPLParser.ExprContext):

                    asignaciones.append({"name":index-4,"simbol": index-2, "expr": index})

            lasExpresion = asignaciones.pop(-1)

            for asignacion in asignaciones:
                visitname = self.visit(children[asignacion["name"]])
                visitexpr = self.visit(children[asignacion["expr"]])

                ##triplet = f"ASSIGN t{ visitname.number} t{visitexpr.number}"
                sms = f"{visitname.datos} = t{visitexpr.number}"
                temporal = Temporal(len(self.temporals), sms)
                ##sms = f"\tt{temporal.number} = {triplet}"
                self.write(f"\t{sms}")
                self.temporals.append(temporal)

            vistLastExp = self.visit(children[lasExpresion["expr"]]) 
            return vistLastExp

        elif ctx.NEW():
            triplet = f"NEW {ctx.TYPE_ID()[0].getText()}"
            sms = f"\tt{len(self.temporals)} = {triplet}"
            self.write(sms)
            temporal = Temporal(len(self.temporals), sms)
            self.temporals.append(temporal)
            return temporal


        elif ctx.NOT():
            expr = ctx.children[1]
            visit = self.visit(expr)
            triplet = f"NOT t{visit.number}"
            sms = f"\tt{len(self.temporals)} = {triplet}"
            self.write(sms)
            temporal = Temporal(len(self.temporals), sms)
            self.temporals.append(temporal)
            return temporal
        
        elif ctx.NEG():
            expr = ctx.children[1]
            visit = self.visit(expr)
            triplet = f"NEG t{visit.number}"
            sms = f"\tt{len(self.temporals)} = {triplet}"
            self.write(sms)
            temporal = Temporal(len(self.temporals), sms)
            self.temporals.append(temporal)
            return temporal

        elif ctx.PLUS():
            left = ctx.children[0]
            right = ctx.children[2]
            children = []
            visitLeft = self.visit(left)
            visitRight = self.visit(right)


            triplet = f"PLUS t{visitLeft.number} t{visitRight.number}"
            temporal = Temporal(len(self.temporals), triplet)
            sms = f"\tt{temporal.number} = PLUS t{visitLeft.number} t{visitRight.number}"
            self.write(sms)
            self.temporals.append(temporal)
            return temporal

        elif ctx.MINUS():
            left = ctx.children[0]
            right = ctx.children[2]
            children = []
            visitLeft = self.visit(left)
            visitRight = self.visit(right)

            triplet = f"MINUS t{visitLeft.number} t{visitRight.number}"
            temporal = Temporal(len(self.temporals), triplet)
            sms = f"\tt{temporal.number} = MINUS t{visitLeft.number} t{visitRight.number}"
            self.write(sms)
            self.temporals.append(temporal)
            return temporal
        
        elif ctx.MULT():
            left = ctx.children[0]
            right = ctx.children[2]
            children = []
            visitLeft = self.visit(left)
            visitRight = self.visit(right)

            triplet = f"MULT t{visitLeft.number} t{visitRight.number}"
            temporal = Temporal(len(self.temporals), triplet)
            sms = f"\tt{temporal.number} = MULT t{visitLeft.number} t{visitRight.number}"
            self.write(sms)
            self.temporals.append(temporal)
            return temporal
        
        elif ctx.DIV():
            left = ctx.children[0]
            right = ctx.children[2]
            children = []
            visitLeft = self.visit(left)
            visitRight = self.visit(right)

            triplet = f"DIV t{visitLeft.number} t{visitRight.number}"
            temporal = Temporal(len(self.temporals), triplet)
            sms = f"\tt{temporal.number} = DIV t{visitLeft.number} t{visitRight.number}"
            self.write(sms)
            self.temporals.append(temporal)
            return temporal

        elif ctx.LE():
            left = ctx.children[0]
            right = ctx.children[2]

            visitLeft = self.visit(left)
            visitRight = self.visit(right)

            triplet = f"LE t{visitLeft.number} t{visitRight.number}"
            temporal = Temporal(len(self.temporals), triplet)
            sms = f"\tt{temporal.number} = LE t{visitLeft.number} t{visitRight.number}"
            self.write(sms)
            self.temporals.append(temporal)
            return temporal
        
        elif ctx.LT():
            left = ctx.children[0]
            right = ctx.children[2]

            visitLeft = self.visit(left)
            visitRight = self.visit(right)

            triplet = f"LT t{visitLeft.number} t{visitRight.number}"
            temporal = Temporal(len(self.temporals), triplet)
            sms = f"\tt{temporal.number} = LT t{visitLeft.number} t{visitRight.number}"
            self.write(sms)
            self.temporals.append(temporal)
            return temporal
        
        elif ctx.EQ():
            left = ctx.children[0]
            right = ctx.children[2]

            visitLeft = self.visit(left)
            visitRight = self.visit(right)
            
            triplet = f"EQ t{visitLeft.number} t{visitRight.number}"
            temporal = Temporal(len(self.temporals), triplet)
            sms = f"\tt{temporal.number} = EQ t{visitLeft.number} t{visitRight.number}"
            self.write(sms)
            return temporal
        
        elif ctx.ASSIGN():
            left = ctx.children[0]
            right = ctx.children[2]
            children = []
            visitLeft = self.visit(left)
            visitRight = self.visit(right)

            ## triplet = f"ASSIGN t{visitLeft.number} t{visitRight.number}"
            triplet = f"{visitLeft.datos} = t{visitRight.number}"
            temporal = Temporal(len(self.temporals), triplet)
            sms = f"\t{triplet}"
            self.write(sms)
            return temporal


        elif ctx.LPAREN():
            expr = ctx.children[1]
            return self.visit(expr)


        elif ctx.FALSE():
            temporal = Temporal(len(self.temporals), "false")
            self.temporals.append(temporal)

            triplet = f"t{temporal.number} = false"
            sms = f"\tt{temporal.number} = false"
            self.write(sms)
            return temporal
    
        elif ctx.TRUE():
            temporal = Temporal(len(self.temporals), "true")
            self.temporals.append(temporal)

            triplet = f"t{temporal.number} = true"
            sms = f"\tt{temporal.number} = true"
            self.write(sms)
            return temporal
        
        elif ctx.INT():
            number = ctx.INT().getText()
            temporal = Temporal(len(self.temporals), number)
            self.temporals.append(temporal)

            triplet = f"t{temporal.number} = {number}"
            sms = f"\tt{temporal.number} = {number}"
            self.write(sms)
            return temporal
        
        elif ctx.STRING():
            string = ctx.STRING().getText()
            temporal = Temporal(len(self.temporals), string)
            self.temporals.append(temporal)

            triplet = f"t{temporal.number} = {string}"
            sms = f"\tt{temporal.number} = {string}"
            self.write(sms)
            return temporal
        
        elif ctx.OBJECT_ID():
            name = ctx.OBJECT_ID()[0].getText()

            if name == "self":
                temporal = Temporal(len(self.temporals), "self")
                self.temporals.append(temporal)

                triplet = f"t{temporal.number} = self"
                sms = f"\tt{temporal.number} = self"
                self.write(sms)
                return temporal

            symbol = self.symbol_table.lookup(name)
            smm = f"sp{self.sp}[{symbol.memory_position}]"
            if symbol is not None:
                temporal = Temporal(len(self.temporals), smm)
                self.temporals.append(temporal)

                triplet = f"t{temporal.number} = {smm}"
                sms = f"\tt{temporal.number} = {smm}"
                self.write(sms)
                return temporal
            
        


        return None


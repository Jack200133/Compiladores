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
                    
            self.symbol_table.current_scope = function_scope    
            children = []
            for child in ctx.children:
                chil = self.visit(child)
                if chil is not None:
                    children.append(chil)
            
            retunr_srt = self.dobleinstance(children[-1],"")

            self.write(f"RETURN {retunr_srt}\n")
            self.write(f"END FUNCTION {simbol.scope}\n")

            self.symbol_table.current_scope = self.symbol_table.current_scope.parent
            self.sp = "_GLOBAL"

        else:
            if ctx.ASSIGN():
                visitexpr = self.visit(ctx.children[-1])
                name = ctx.OBJECT_ID().getText()
                simbol: Symbol = self.symbol_table.lookup(name)
                if isinstance(visitexpr, Temporal):
                    triplet = f"ASSIGN sp{self.sp}[{simbol.memory_position}] t{visitexpr.number}"
                else:
                    triplet = f"ASSIGN sp{self.sp}[{simbol.memory_position}] {visitexpr}"
                # temp = Temporal(len(self.temporals), triplet)
                # tempis = f"\t{triplet}"
                # self.temporals.append(temp)
                self.write(f"\t{triplet}")
                return f"sp{self.sp}[{simbol.memory_position}]"

            else:
                return


            for child in ctx.children:
                chil = self.visit(child)
                if chil is not None:
                    children.append(chil)
            if len(children) == 1:
                return
                sms = f"ASSIGN t{children[0].number} {0}"
                sms = f"{children[0].datos} = {0}"
                temp = Temporal(len(self.temporals), sms)
                tempis = f"\t{sms}"
                self.temporals.append(temp)
                self.write(sms)
                return temp
            
            if isinstance(children[0], Temporal) and isinstance(children[1], Temporal):
                triplet = f"ASSIGN t{children[0].number} t{children[1].number}"
            elif isinstance(children[0], Temporal) and isinstance(children[1], str):
                triplet = f"ASSIGN t{children[0].number} {children[1]}"
            elif isinstance(children[0], str) and isinstance(children[1], Temporal):
                triplet = f"ASSIGN {children[0]} t{children[1].number}"
            else:
                triplet = f"ASSIGN {children[0]} {children[1]}"
            
            #sms = f"{children[0].datos} = t{children[1].number}"
            temp = Temporal(len(self.temporals), triplet)
            tempis = f"\t{triplet}"
            self.temporals.append(temp)
            self.write(tempis)


            
        return None
    
    def dobleinstance(self,izq,der):

        if isinstance(izq, Temporal) and isinstance(der, Temporal):
            triplet = f"t{izq.number} t{der.number}"
        elif isinstance(izq, Temporal) and isinstance(der, str):
            triplet = f"t{izq.number} {der}"
        elif isinstance(izq, str) and isinstance(der, Temporal):
            triplet = f"{izq} t{der.number}"
        else:
            triplet = f"{izq} {der}"
        
        return triplet
    
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
                param_str = self.dobleinstance(param,"")
                sms = f"\tPARAM {param_str}"
                self.write(sms)

            isAtt = "."
            if ctx.AT():
                nameatt = ctx.TYPE_ID()[0].getText()
                isAtt = f".{nameatt}."

            if isinstance(visitFunc,Temporal):
                func_str = f"t{visitFunc.number}"
            else:
                func_str = visitFunc

            triplet = f"CALL {func_str}{isAtt}{ctx.OBJECT_ID()[0].getText()} {len(tempsParams)}"
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
                pram_str = self.dobleinstance(param,"")
                sms = f"\tPARAM {pram_str}"
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
            
            if isinstance(condition, Temporal):
                condition_str = f"t{condition.number}"
            else:
                condition_str = condition

            trulabel = f"LABEL_L{len(self.labels)}"
            self.labels.append(trulabel)
            falselabel = f"LABEL_L{len(self.labels)}"
            self.labels.append(falselabel)
            endIfLabel = f"LABEL_L{len(self.labels)}"
            self.labels.append(endIfLabel)

            temporal = Temporal(len(self.temporals), "Object")
            self.temporals.append(temporal)

            self.write(f"\tIF {condition_str} GOTO {trulabel}")
            self.write(f"\tGOTO {falselabel}")
            self.write(f"{trulabel}:")
            trueVisit = self.visit(ctx.children[3])

            if isinstance(trueVisit, Temporal):
                triplet = f"t{temporal.number} = t{trueVisit.number}"
            else:
                triplet = f"t{temporal.number} = {trueVisit}"

            sms = f"\t{triplet}"
            self.write(sms)


            self.write(f"\tGOTO {endIfLabel}")
            self.write(f"{falselabel}:")
            falseVisit = self.visit(ctx.children[5])

            if isinstance(falseVisit, Temporal):
                triplet = f"t{temporal.number} = t{falseVisit.number}"
            else:
                triplet = f"t{temporal.number} = {falseVisit}"

            sms = f"\t{triplet}"
            self.write(sms)
            self.write(f"{endIfLabel}:")

            return temporal

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
                param_str = self.dobleinstance(param,"")
                sms = f"\tPARAM {param_str}"
                self.write(sms)
            
            triplet = f"CALL {ctx.OBJECT_ID()[0].getText()} {len(tempsParams)}"
            sms = f"\tt{len(self.temporals)} = {triplet}"
            self.write(sms)
            temporal = Temporal(len(self.temporals), sms)
            self.temporals.append(temporal)
            return temporal
            

        #WHILE expr LOOP expr POOL
        elif ctx.WHILE():
            condition = ctx.children[1]
            condition= self.visit(condition)

            if isinstance(condition, Temporal):
                condition_str = f"t{condition.number}"
            else:
                condition_str = condition

            labelstart = f"LABEL_L{len(self.labels)}"
            self.labels.append(labelstart)
            labelend = f"LABEL_L{len(self.labels)}"
            self.labels.append(labelend)

            looplabel = f"LABEL_L{len(self.labels)}"
            self.labels.append(looplabel)

            self.write(f"{labelstart}:")
            self.write(f"\tIF {condition_str} GOTO {looplabel}")
            self.write(f"\tGOTO {labelend}")
            self.write(f"{looplabel}:")
            trueVisit = self.visit(ctx.children[3])
            self.write(f"\tGOTO {labelstart}")
            self.write(f"{labelend}:")

            temporal = Temporal(len(self.temporals), "Object")
            self.temporals.append(temporal)
            return temporal


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
            for index, child in enumerate(children):

                if isinstance(child, YAPLParser.ExprContext):

                    asignaciones.append({"name":index-4,"simbol": index-2, "expr": index})

            lasExpresion = asignaciones.pop(-1)

            for asignacion in asignaciones:
               # visitname = self.visit(children[asignacion["name"]])
                simbol_name = children[asignacion["name"]].getText()
                symbol = self.symbol_table.lookup(simbol_name)
                scope = self.symbol_table.current_scope

                if symbol is not None:
                    if symbol.name not in scope.symbols.keys():
                        sp = "_GLOBAL"
                    else:
                        sp = self.sp
                smm = f"sp{sp}[{symbol.memory_position}]"

                visitexpr = self.visit(children[asignacion["expr"]])

                asign_str = self.dobleinstance(smm,visitexpr)

                ##triplet = f"ASSIGN t{ visitname.number} t{visitexpr.number}"
                sms = f"ASSIGN {asign_str}"
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

            neg_str = self.dobleinstance(visit,"")
            triplet = f"NOT {neg_str}"
            sms = f"\tt{len(self.temporals)} = {triplet}"
            self.write(sms)
            temporal = Temporal(len(self.temporals), sms)
            self.temporals.append(temporal)
            return temporal
        
        elif ctx.NEG():
            expr = ctx.children[1]
            visit = self.visit(expr)

            neg_str = self.dobleinstance(visit,"")

            triplet = f"NEG {neg_str}"
            sms = f"\tt{len(self.temporals)} = {triplet}"
            self.write(sms)
            temporal = Temporal(len(self.temporals), sms)
            self.temporals.append(temporal)
            return temporal
        
        elif ctx.ISVOID():
            expr = ctx.children[1]
            visit = self.visit(expr)

            neg_str = self.dobleinstance(visit,"")

            triplet = f"ISVOID {neg_str}"
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
            asing = self.dobleinstance(visitLeft,visitRight)

            triplet = f"PLUS {asing}"
            temporal = Temporal(len(self.temporals), triplet)
            sms = f"\tt{temporal.number} = {triplet}"
            self.write(sms)
            self.temporals.append(temporal)
            return temporal

        elif ctx.MINUS():
            left = ctx.children[0]
            right = ctx.children[2]
            children = []
            visitLeft = self.visit(left)
            visitRight = self.visit(right)

            asing = self.dobleinstance(visitLeft,visitRight)

            triplet = f"MINUS {asing}"
            temporal = Temporal(len(self.temporals), triplet)
            sms = f"\tt{temporal.number} = {triplet}"
            self.write(sms)
            self.temporals.append(temporal)
            return temporal
        
        elif ctx.MULT():
            left = ctx.children[0]
            right = ctx.children[2]
            children = []
            visitLeft = self.visit(left)
            visitRight = self.visit(right)
            asing = self.dobleinstance(visitLeft,visitRight)

            triplet = f"MULT {asing}"
            temporal = Temporal(len(self.temporals), triplet)
            sms = f"\tt{temporal.number} = MULT {asing}"
            self.write(sms)
            self.temporals.append(temporal)
            return temporal
        
        elif ctx.DIV():
            left = ctx.children[0]
            right = ctx.children[2]
            children = []
            visitLeft = self.visit(left)
            visitRight = self.visit(right)
            asing = self.dobleinstance(visitLeft,visitRight)

            triplet = f"DIV {asing}"
            temporal = Temporal(len(self.temporals), triplet)
            sms = f"\tt{temporal.number} = DIV {asing}"
            self.write(sms)
            self.temporals.append(temporal)
            return temporal

        elif ctx.LE():
            left = ctx.children[0]
            right = ctx.children[2]

            visitLeft = self.visit(left)
            visitRight = self.visit(right)
            asing = self.dobleinstance(visitLeft,visitRight)

            triplet = f"LE {asing}"
            temporal = Temporal(len(self.temporals), triplet)
            sms = f"\tt{temporal.number} = LE {asing}"
            self.write(sms)
            self.temporals.append(temporal)
            return temporal
        
        elif ctx.LT():
            left = ctx.children[0]
            right = ctx.children[2]

            visitLeft = self.visit(left)
            visitRight = self.visit(right)
            asing = self.dobleinstance(visitLeft,visitRight)

            triplet = f"LT {asing}"
            temporal = Temporal(len(self.temporals), triplet)
            sms = f"\tt{temporal.number} = LT {asing}"
            self.write(sms)
            self.temporals.append(temporal)
            return temporal
        
        elif ctx.EQ():
            left = ctx.children[0]
            right = ctx.children[2]

            visitLeft = self.visit(left)
            visitRight = self.visit(right)
            asing = self.dobleinstance(visitLeft,visitRight)

            triplet = f"EQ {asing}"
            temporal = Temporal(len(self.temporals), triplet)
            self.temporals.append(temporal)
            sms = f"\tt{temporal.number} = {triplet}"
            self.write(sms)
            return temporal


        
        # OBJECT_ID ASSIGN expr
        elif ctx.ASSIGN():
            name = ctx.OBJECT_ID()[0].getText()
            symbol = self.symbol_table.lookup(name)
            scope = self.symbol_table.current_scope


            if symbol.name not in scope.symbols.keys():
                sp = "_GLOBAL"
            else:
                sp = self.sp
            smm = f"sp{sp}[{symbol.memory_position}]"
            right = ctx.children[2]
            children = []

            visitRight = self.visit(right)
            if isinstance(visitRight, Temporal):
                triplet = f"ASSIGN {smm} t{visitRight.number}"
            else:
                triplet = f"ASSIGN {smm} {visitRight}"
            ## triplet = f"ASSIGN t{visitLeft.number} t{visitRight.number}"
            #triplet = f"{smm} = t{visitRight.number}"
            #temporal = Temporal(len(self.temporals), triplet)
            sms = f"\t{triplet}"
            self.write(sms)
            return smm


        elif ctx.LPAREN():
            expr = ctx.children[1]
            return self.visit(expr)


        elif ctx.FALSE():
            return "false"
            temporal = Temporal(len(self.temporals), "false")
            self.temporals.append(temporal)

            triplet = f"t{temporal.number} = false"
            sms = f"\tt{temporal.number} = false"
            self.write(sms)
            return temporal
    
        elif ctx.TRUE():
            return "true"
            temporal = Temporal(len(self.temporals), "true")
            self.temporals.append(temporal)

            triplet = f"t{temporal.number} = true"
            sms = f"\tt{temporal.number} = true"
            self.write(sms)
            return temporal
        
        elif ctx.INT():
            number = ctx.INT().getText()
            return number
            temporal = Temporal(len(self.temporals), number)
            self.temporals.append(temporal)

            triplet = f"t{temporal.number} = {number}"
            sms = f"\tt{temporal.number} = {number}"
            self.write(sms)
            return temporal
        
        elif ctx.STRING():
            string = ctx.STRING().getText()
            return string
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
            scope = self.symbol_table.current_scope


            if symbol.name not in scope.symbols.keys():
                sp = "_GLOBAL"
            else:
                sp = self.sp
            smm = f"sp{sp}[{symbol.memory_position}]"
            return smm
            
        


        return None


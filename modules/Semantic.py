from antlr4 import *
from antlr4 import ParseTreeVisitor
from modules.Symbol import Symbol, SymboTable
from modules.Type import TypeSystem
from yapl.YAPLParser import YAPLParser

class SemanticAnalyzer(ParseTreeVisitor):

    def __init__(self):
        self.symbol_table = SymboTable()
        self.type_system = TypeSystem()
        self.nodes = {}

    def visit(self, tree):
        # Obten el método de visita apropiado para el tipo de nodo.
        # result = self.visitChildren(tree)

        # Aquí puedes poner código adicional que se ejecuta después de visitar el nodo.
        # Segun el tipo de nodo, vamosa llamar a su funcion visit
        if isinstance(tree, YAPLParser.ProgramContext):
            result = self.visitProgram(tree)
        elif isinstance(tree, YAPLParser.ClassDefContext):
            result = self.visitClassDef(tree)
        elif isinstance(tree,YAPLParser.FeatureDefContext):
            result = self.visitFeatureDef(tree)
        elif isinstance(tree, YAPLParser.FormalDefContext):
            result = self.visitFormalDef(tree)

        # CAmbier esto porque hay que hacer el return implicito con el ultimo hijo a la derecha
        # elif isinstance(tree, YAPLParser.ReturnFuncContext):
        #     result = self.visitReturnFunc(tree)
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
            # result = node.getSymbol().type
        # Aquí puedes poner código adicional que se ejecuta después de visitar todos los hijos del nodo.

        return result


    def visitTerminal(self, ctx: TerminalNode):
        symbol_type = ctx.getSymbol().type
        txt = ctx.getText()
        if symbol_type == YAPLParser.INT:
            return {"type":'Int', "hasError": False}
        elif symbol_type == YAPLParser.TRUE or symbol_type == YAPLParser.FALSE:
            return {"type":'Bool', "hasError": False}
        elif symbol_type == YAPLParser.STRING:
            return {"type":'String', "hasError": False}

        else:
            # Buscar su tipo en la tabla de símbolos
            symbol = self.symbol_table.lookup(ctx.getText())
            if symbol is not None:
                return {"type":symbol.type, "hasError": False}
            else:
                return {"type":None, "hasError": True}



    def visitProgram(self, ctx: YAPLParser.ProgramContext):
        self.symbol_table = SymboTable()
        # self.symbol_table.open_scope()
        self.visitChildren(ctx)
        # self.symbol_table.close_scope()
        # Buscar la clase Main si no existe, error
        main_symbol = self.symbol_table.lookup('Main')
        if main_symbol is None:
            print("Error semántico: No se encontró la clase Main.")
            return
        return

    def visitClassDef(self, ctx: YAPLParser.ClassDefContext):
        class_name = ctx.TYPE_ID()[0].getText()
        inherits_from = None  # Inicializamos la variable

        if ctx.INHERITS():  # Si hay herencia
            inherits_from = ctx.TYPE_ID()[1].getText()  # Obtenemos el tipo padre


        # Comprobar el ClassMain
        if class_name == 'Main':
            if inherits_from is not None:
                print(f"Error semántico: la clase Main no puede heredar de otra clase.")
            
       

        
        type = "Object" if inherits_from is None else inherits_from
        if self.type_system.add_type(class_name, inherits_from):  # Añadimos el tipo a la tabla de tipos
            myscope = self.symbol_table.current_scope
            definition = Symbol(class_name, type, 'ClassDef', f"{class_name} -> {inherits_from if inherits_from else 'Object'}", f"{inherits_from if inherits_from else 'Object'}.{class_name}",myscope=myscope)
            self.symbol_table.add(definition)  # Añadimos el símbolo a la tabla de símbolos

            self.symbol_table.open_scope(class_name,type)  # Abrimos un nuevo alcance en la tabla de símbolos
             # TODO: Si hereda de alguna clase ya definida, copiar los métodos de la clase padre a la clase hija
            #self.symbol_table.displayTree()
            if inherits_from is not None:
                symbol_parent = self.symbol_table.lookup(inherits_from)
                if symbol_parent is None:
                    print(f"Error semántico: la clase {class_name} hereda de una clase inexistente.")
                else:
                    childrealnode = None
                    for child in symbol_parent.myscope.children:
                        if child.name == symbol_parent.name:
                            childrealnode = child
                            break

                    if childrealnode is not None:
                        parent_scope = childrealnode
                        for symbol_name, symbol in parent_scope.symbols.items():
                            new_symbol = Symbol(name=symbol_name, _type=symbol.type,
                                                definicion=symbol.definicion, 
                                                derivation=symbol.derivation,
                                                scope=self.symbol_table.current_scope)
                            self.symbol_table.add(new_symbol)
                        for child_scope in parent_scope.children:
                            self.symbol_table.open_scope(name=child_scope.name, type=child_scope.type)
                            print(f"Abriendo alcance {child_scope.name},Scope: {child_scope.number},Current: {self.symbol_table.current_scope.number}")
                            for symbol_name, symbol in child_scope.symbols.items():
                                new_symbol = Symbol(name=symbol_name, _type=symbol.type,
                                                    definicion=symbol.definicion, 
                                                    derivation=symbol.derivation,
                                                    scope=self.symbol_table.current_scope)
                                self.symbol_table.add(new_symbol)
                            self.symbol_table.close_scope()
            result = self.visitChildren(ctx)  # Visitamos los hijos del nodo actual
            self.symbol_table.close_scope()  # Cerramos el alcance en la tabla de símbolos
            return result  # Retornamos el resultado

        else:  # Si add_type retorna False, hubo un error semántico y no procedemos
            print(f"Error semántico: No se pudo añadir la clase {class_name}.")
            return None  # Podrías manejar el error como mejor te parezca

    def visitFormalDef(self, ctx: YAPLParser.FormalDefContext):
        name = ctx.OBJECT_ID().getText()
        type = ctx.TYPE_ID().getText()
        node_data = {"type": type, "hasError": False}

        # Verificar de que featureDef proviene
        feature_context = ctx.parentCtx
        feature_name = feature_context.OBJECT_ID().getText()
        class_context = feature_context.parentCtx
        class_name = class_context.TYPE_ID()[0].getText()

        # Verificar si el nombre del símbolo ya está en la tabla de símbolos actual
        if self.symbol_table.lookup(name) is not None:
            #TODO: Cuando se agregen las clases heredadas se deberia podever cerificar aca el override de una 
            node_data = {"type": type, "hasError": True}
            pass
            
            #print(f"Error semántico: el símbolo '{name}' ya ha sido declarado en el ámbito actual.")
        else:
            # Si el nombre del símbolo no está en la tabla, agregarlo como nuevo símbolo.
            dev = f"{feature_name}.{name}"
            myscope = self.symbol_table.current_scope
            symbol = Symbol(name, type, 'FormalDef', f"{dev} -> {type}",f"{class_name}.{dev}",myscope=myscope)
            #self.symbol_table.open_scope()

            self.symbol_table.add(symbol)
            self.visitChildren(ctx)

            #self.symbol_table.close_scope()

        #self.symbol_table.display()

        return node_data
    
    # featureDef : ID LPAREN (formalDef (COMMA formalDef)*)? RPAREN DOBLE TYPE_ID LBRACE (expr)* (returnFunc)? RBRACE
    #       | ID DOBLE TYPE_ID (LEFT_ARROW expr)?
    #       ;

    def visitFeatureDef(self, ctx: YAPLParser.FeatureDefContext):
        node_data = {"type": None, "hasError": False}
        name = ctx.OBJECT_ID().getText()
        type = ctx.TYPE_ID().getText()

        


        class_context = ctx.parentCtx
        class_name = class_context.TYPE_ID()[0].getText()
        dev = f"{class_name}.{name}"

        if type == 'SELF_TYPE':
            type = class_name

        # Verificar si el nombre del símbolo ya está en la tabla de símbolos actual
        if self.symbol_table.lookup(name) is not None:
            pass
            print(f"Error semántico: el símbolo '{name}' ya ha sido declarado en el ámbito actual. En la linea {ctx.start.line}, columna {ctx.start.column}.")

        myscope = self.symbol_table.current_scope
        symbol = Symbol(name, type, 'FeatureDef', f"{dev} -> {type}", dev,myscope=myscope)
        self.symbol_table.add(symbol)
        
        if ctx.LPAREN():
            self.symbol_table.open_scope(name,type)
        

        
        children_types = []
        for child in ctx.children:
            if child in self.nodes:
                children_types.append(self.nodes[child])
            else:
                children_types.append(self.visit(child))
                node_data2 = {"type": children_types[-1]["type"], "hasError": False}
                self.nodes[child] = node_data2

        if ctx.LPAREN():
            self.symbol_table.close_scope()

        result = children_types[-1]


        # Si es una funcion
        #OBJECT_ID LPAREN (formalDef (COMMA formalDef)*)? RPAREN COLON TYPE_ID LBRACE expr RBRACE 
        if ctx.LPAREN():
            pass



        # Si es una asignacion
        # OBJECT_ID COLON TYPE_ID (ASSIGN expr)? ;
        else:
            if type == result["type"]:
                
                node_data = {"type": type, "hasError": False}
                self.nodes[ctx] = node_data
                return node_data
            else:
                print(f"Error semántico: el tipo de la expresión no coincide con el tipo del símbolo '{type}' <- '{result['type']}'. En la linea {ctx.start.line}, columna {ctx.start.column}.")
                node_data = {"type": type, "hasError": True}
                self.nodes[ctx] = node_data
                return node_data
        
        return node_data
    

        if result["type"] != type:
            print("ERROR ALV")
            node_data = {"type": type, "hasError": True}
            self.nodes[ctx] = node_data
            return node_data
        else:
            node_data = {"type": type, "hasError": False}
            self.nodes[ctx] = node_data
            return node_data
        


    def visitExpr(self, ctx: YAPLParser.ExprContext):
        if ctx in self.nodes:
            return self.nodes[ctx]
        
        if ctx is None:
            return
        
        if not isinstance(ctx, YAPLParser.ExprContext):
            return

        node_data = {"type": None, "hasError": False}
        print(f"Visitando expresión: {ctx.getText()}")
        

        # children_types = []
        # for child in ctx.children:
        #     if child in self.nodes:
        #         children_types.append(self.nodes[child])
        #     else:
        #         children_types.append(self.visit(child))
        #         node_data2 = {"type": children_types[-1]["type"], "hasError": False}
        #         self.nodes[child] = node_data2

        #Comprobar si es instance de un LET para crear el simbolo del valor de let
        if ctx.LET():
            name = ctx.OBJECT_ID()[0].getText()
            type = ctx.TYPE_ID()[0].getText()
            dev = f"{name}"
            self.symbol_table.open_scope(name,type)
            myscope = self.symbol_table.current_scope
            symbol = Symbol(name, type, 'Let', f"{dev} -> {type}",f"{dev}",myscope=myscope)
            self.symbol_table.add(symbol)
            result = self.visitChildren(ctx)

            self.symbol_table.close_scope()
            # TODO: Comprobar si tiene (ASSIGN expr)? y ver ese error
            node_data = {"type": type, "hasError": False}
            self.nodes[ctx] = node_data
            return node_data

        children = []
        for child in ctx.getChildren():
            children.append(child)

        children_types = []
        for index,child in enumerate(children):
            if child in self.nodes:
                children_types.append(self.nodes[child])
            else:
                children_types.append(self.visit(child))
                node_data2 = {"type": children_types[-1]["type"], "hasError": False}
                self.nodes[child] = node_data2

        # Expresiones de LET OBJECT_ID COLON TYPE_ID (ASSIGN expr)? (COMMA OBJECT_ID COLON TYPE_ID (ASSIGN expr)?)* IN expr
        if (ctx.LET() and ctx.IN()):
            #El valor del nodo sera del ultimo hijo
            node_data = {"type": children_types[-1]["type"], "hasError": False}
            self.nodes[ctx] = node_data
            return node_data
        
        # LBRACE (expr SEMICOLON)+ RBRACE

        elif (ctx.LBRACE() and ctx.RBRACE()):
            expr_indices = [index for index, child in enumerate(children) if isinstance(child, YAPLParser.ExprContext)]
            last_expr_index = expr_indices[-1]
            
            node_data = {"type": children_types[last_expr_index]["type"], "hasError": False}
            self.nodes[ctx] = node_data
            return node_data
        
        #TODO: expr  (AT TYPE_ID)? DOT OBJECT_ID LPAREN  (expr (COMMA expr)*)? RPAREN
        elif (ctx.DOT() and ctx.OBJECT_ID() and ctx.LPAREN() and ctx.RPAREN()):
            # TODO: Buscar tambien los tipos de los argumentos y ver que esten bien? osea el exp = al que se manda
            # print(self.symbol_table.current_scope.number)
            self.symbol_table.displayTree()
            print(ctx.getText())
            print(children[0].getText())
            godly_dad = self.symbol_table.lookup_scope(children_types[0]["type"])
            print(godly_dad)

            functionReveal = None
            for child in godly_dad.children:
                if child.name == ctx.OBJECT_ID()[0].getText():
                    functionReveal = child
                    print("Encontrado")
            print(ctx.OBJECT_ID())

            for data in ctx.OBJECT_ID():
                print("---",data.getText())
            print(ctx.OBJECT_ID()[0].getText())
            print(self.symbol_table.lookup(ctx.OBJECT_ID()[0].getText()))
            #self.symbol_table.displayTree()
            objID_type = self.symbol_table.lookup(ctx.OBJECT_ID()[0].getText()).type
            node_data = {"type": objID_type, "hasError": False}
            self.nodes[ctx] = node_data
            return node_data
        
        #TODO: OBJECT_ID LPAREN (expr (COMMA expr)*)? RPAREN
        elif (ctx.OBJECT_ID() and ctx.LPAREN() and ctx.RPAREN()):

            node_data = {"type": children_types[-1]["type"], "hasError": False}
            self.nodes[ctx] = node_data
            return node_data

        # Expresiones de Asignacion <id> <- <expr>
        elif (ctx.OBJECT_ID() and ctx.ASSIGN()):
            symbol = children_types[0]
            if symbol["type"] is None:
                pass
                print(f"Error semántico: el símbolo '{ctx.OBJECT_ID()[0]}' no ha sido declarado. En la linea {ctx.start.line}, columna {ctx.start.column}.")
                node_data = {"type": children_types[-1]["type"], "hasError": True}
                self.nodes[ctx] = node_data
                
            else:
                if not self.type_system.checkAssigment(symbol['type'],children_types[-1]["type"]):
                    pass
                    print(f"Error semántico: el tipo de la expresión no coincide con el tipo del símbolo '{ctx.OBJECT_ID()}'. En la linea {ctx.start.line}, columna {ctx.start.column}.")
                    node_data = {"type": children_types[-1]["type"], "hasError": True}
                    self.nodes[ctx] = node_data
                else:
                    node_data = {"type": children_types[-1]["type"], "hasError": False}
                    self.nodes[ctx] = node_data

        # Expresiones de Comparacion <expr> <op> <expr>

        elif (ctx.PLUS() or ctx.MINUS() or ctx.MULT() or ctx.DIV()):
            # self.symbol_table.display()
            isnum =  self.type_system.checkNumeric(children_types[0]["type"], children_types[2]["type"])
            if not isnum:
                pass
                operador = ctx.PLUS().getText() if ctx.PLUS() else ctx.MINUS().getText() if ctx.MINUS() else ctx.MULT().getText() if ctx.MULT() else ctx.DIV().getText()
                print(f"Error semántico: los tipos de las expresiones no coinciden. En la linea {ctx.start.line}, columna {ctx.start.column}. No se puede operar ({operador}) entre {children_types[0]['type']} y {children_types[2]['type']}.")
                node_data = {"type": children_types[-1]["type"], "hasError": True}
                self.nodes[ctx] = node_data
            else:
                node_data = {"type": children_types[-1]["type"], "hasError": False}
                self.nodes[ctx] = node_data
        
        # LPAREN expr RPAREN
        elif (ctx.LPAREN() and ctx.RPAREN()):
            node_data = {"type": children_types[1]["type"], "hasError": False}
            self.nodes[ctx] = node_data

        # Return type OBJECT_ID 
        elif ctx.OBJECT_ID():
            object_id = ctx.OBJECT_ID()[0].getText()  # Obtener el texto del token

            if object_id == "self":
                # Aquí, sabemos que estamos tratando con 'self'.
                # Obtener el tipo del padre del alcance actual
                type = self.symbol_table.current_scope.type
                node_data = {"type":type, "hasError": False}

            else:
                # Aquí, object_id es una variable y puedes buscar su tipo en tu tabla de símbolos.
                symbol = self.symbol_table.lookup(object_id)
                if symbol:
                    variable_type = symbol.type  # Suponiendo que tu símbolo tiene un campo 'type'
                    node_data = {"type":variable_type, "hasError": False}
                else:
                    print(f"Error: la variable {object_id} no está definida. En la linea {ctx.start.line}, columna {ctx.start.column}.")
                    # Manejar el error como prefieras

        #NEW TYPE_ID 
        elif ctx.NEW():
            type_id = ctx.TYPE_ID()[0].getText()
            node_data = {"type":type_id, "hasError": False}

        elif ctx.NEG():
            type = children_types[-1]["type"]
            if type == "Bool" or type == "Int":
                node_data = {"type":type, "hasError": False}
            else:
                print(f"Error semántico: No se puede negar una expresión de tipo {type}. En la linea {ctx.start.line}, columna {ctx.start.column}.")
 
        elif ctx.IF():
            print(ctx.getText())

            type = children_types[1]["type"]


        elif (ctx.INT()):
            return {"type":'Int', "hasError": False}
        elif (ctx.STRING()):
            return {"type":'String', "hasError": False}
        elif (ctx.TRUE() or ctx.FALSE()):
            return {"type":'Bool', "hasError": False}


        return node_data
        return self.visitChildren(ctx)


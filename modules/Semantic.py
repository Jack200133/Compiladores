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
        self.ErrorList = []

    def add_error(self, error_mesagge, line, column, full_error):
        # Verificar si el error no existe ya en la misma linea
        for err in self.ErrorList:
            if err["line"] == line and err["error_mesagge"] == error_mesagge:
                return
        self.ErrorList.append({"error_mesagge": error_mesagge,
                              "line": line, "column": column, "full_error": full_error})

    def visit(self, tree):
        # Obten el método de visita apropiado para el tipo de nodo.
        # result = self.visitChildren(tree)

        # Aquí puedes poner código adicional que se ejecuta después de visitar el nodo.
        # Segun el tipo de nodo, vamosa llamar a su funcion visit
        if isinstance(tree, YAPLParser.ProgramContext):
            result = self.visitProgram(tree)
        elif isinstance(tree, YAPLParser.ClassDefContext):
            result = self.visitClassDef(tree)
        elif isinstance(tree, YAPLParser.FeatureDefContext):
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
            return {"type": 'Int', "hasError": False}
        elif symbol_type == YAPLParser.TRUE or symbol_type == YAPLParser.FALSE:
            return {"type": 'Bool', "hasError": False}
        elif symbol_type == YAPLParser.STRING:
            return {"type": 'String', "hasError": False}

        else:
            # Buscar su tipo en la tabla de símbolos
            symbol = self.symbol_table.lookup(ctx.getText())
            if symbol is not None:
                return {"type": symbol.type, "hasError": False}
            else:
                return {"type": None, "hasError": True}

    def visitProgram(self, ctx: YAPLParser.ProgramContext):
        self.symbol_table = SymboTable()
        # self.symbol_table.open_scope()
        # CREAR LA CLASE IO

        self.symbol_table.add(Symbol("IO", "Object", "SpecialClass",
                              "IO -> Object", "IO", myscope=self.symbol_table.current_scope))

        self.symbol_table.open_scope("IO", "Object")
        self.symbol_table.add(Symbol(
            "out_string", "String", "FeatureDef", "out_string -> SELF_TYPE", "IO.out_string"))
        self.symbol_table.open_scope("out_string", "String")
        self.symbol_table.add(
            Symbol("x", "String", "FormalDef", "x -> String", "IO.out_string.x"))
        self.symbol_table.close_scope()

        self.symbol_table.add(
            Symbol("out_int", "Int", "FeatureDef", "out_int -> SELF_TYPE", "IO.out_int"))
        self.symbol_table.open_scope("out_int", "Int")
        self.symbol_table.add(
            Symbol("x", "Int", "FormalDef", "x -> Int", "IO.out_int.x"))
        self.symbol_table.close_scope()

        self.symbol_table.add(Symbol(
            "in_string", "String", "FeatureDef", "in_string -> String", "IO.in_string"))
        self.symbol_table.open_scope("in_string", "String")
        self.symbol_table.close_scope()

        self.symbol_table.add(
            Symbol("in_int", "Int", "FeatureDef", "in_int -> Int", "IO.in_int"))
        self.symbol_table.open_scope("in_int", "Int")
        self.symbol_table.close_scope()
        self.symbol_table.close_scope()

        # Crear la clase Object
        self.symbol_table.add(Symbol("Object", "Object", "SpecialClass",
                              "Object -> Object", "Object", myscope=self.symbol_table.current_scope))

        self.symbol_table.open_scope("Object", "Object")
        self.symbol_table.add(
            Symbol("abort", "Object", "FeatureDef", "abort -> Object", "Object.abort"))
        self.symbol_table.open_scope("abort", "Object")
        self.symbol_table.close_scope()

        self.symbol_table.add(Symbol(
            "type_name", "String", "FeatureDef", "type_name -> String", "Object.type_name"))
        self.symbol_table.open_scope("type_name", "String")
        self.symbol_table.close_scope()

        self.symbol_table.add(
            Symbol("copy", "SELF_TYPE", "FeatureDef", "copy -> SELF_TYPE", "Object.copy"))
        self.symbol_table.open_scope("copy", "SELF_TYPE")
        self.symbol_table.close_scope()

        self.symbol_table.close_scope()

        # Crear la clase String
        self.symbol_table.add(Symbol("String", "Object", "SpecialClass",
                              "String -> Object", "String", myscope=self.symbol_table.current_scope))

        self.symbol_table.open_scope("String", "Object")
        self.symbol_table.add(
            Symbol("length", "Int", "FeatureDef", "length -> Int", "String.length"))
        self.symbol_table.open_scope("length", "Int")
        self.symbol_table.close_scope()

        self.symbol_table.add(
            Symbol("concat", "String", "FeatureDef", "concat -> String", "String.concat"))
        self.symbol_table.open_scope("concat", "String")
        self.symbol_table.add(
            Symbol("s", "String", "FormalDef", "s -> String", "String.concat.s"))
        self.symbol_table.close_scope()

        self.symbol_table.add(
            Symbol("substr", "String", "FeatureDef", "substr -> String", "String.substr"))
        self.symbol_table.open_scope("substr", "String")
        self.symbol_table.add(
            Symbol("i", "Int", "FormalDef", "i -> Int", "String.substr.i"))
        self.symbol_table.add(
            Symbol("l", "Int", "FormalDef", "l -> Int", "String.substr.l"))
        self.symbol_table.close_scope()

        self.symbol_table.close_scope()

        self.visitChildren(ctx)
        # self.symbol_table.close_scope()
        # Buscar la clase Main si no existe, error
        main_symbol = self.symbol_table.lookup('Main')
        if main_symbol is None:
            sms = f"Error Semántico. En la línea {ctx.stop.line}, columna {ctx.start.column}. No se encontró la clase Main."
            # print(sms)
            self.add_error("No se encontró la clase Main",
                           ctx.stop.line, ctx.stop.column, sms)
            return

        main_real_scope = None
        for child in main_symbol.myscope.children:
            if child.name == main_symbol.name:
                main_real_scope = child
                break

        # Buscar la funcion main, si no existe es error
        main_function = main_real_scope.lookup('main')
        if main_function is None:
            sms = f"Error Semántico. En la línea {ctx.end.line}, columna {ctx.start.column}. No se encontró la función main en la Clase Main"
            # print(sms)
            self.add_error("No se encontró la función main en la Clase Main",
                           ctx.start.line, ctx.start.column, sms)
            return

        return

    def recursiveCompi(self, parent_scope, current_scope):
        # Copiamos los símbolos del alcance padre al alcance actual
        for symbol_name, symbol in parent_scope.symbols.items():
            new_symbol = Symbol(
                name=symbol_name,
                _type=symbol.type,
                definicion=symbol.definicion,
                derivation=symbol.derivation,
                myscope=current_scope,
                is_heredado=True
            )
            current_scope.add(new_symbol)

        # Copiamos los hijos del alcance padre (si los tiene)
        for child_scope in parent_scope.children:
            # Abrimos un nuevo alcance
            self.symbol_table.open_scope(
                name=child_scope.name, type=child_scope.type)

            # Copiamos los símbolos y alcances del hijo del alcance padre al nuevo alcance
            self.recursiveCompi(child_scope, self.symbol_table.current_scope)

            # Cerramos el alcance
            self.symbol_table.close_scope()

    def addIO(self):
        self.symbol_table.open_scope("IO", "Object")

        self.symbol_table.add(Symbol(
            "out_string", "String", "FeatureDef", "out_string -> SELF_TYPE", "IO.out_string"))
        self.symbol_table.open_scope("out_string", "String")
        self.symbol_table.add(
            Symbol("x", "String", "FormalDef", "x -> String", "IO.out_string.x"))
        self.symbol_table.close_scope()

        self.symbol_table.add(
            Symbol("out_int", "Int", "FeatureDef", "out_int -> SELF_TYPE", "IO.out_int"))
        self.symbol_table.open_scope("out_int", "Int")
        self.symbol_table.add(
            Symbol("x", "Int", "FormalDef", "x -> Int", "IO.out_int.x"))
        self.symbol_table.close_scope()

        self.symbol_table.add(Symbol(
            "in_string", "String", "FeatureDef", "in_string -> String", "IO.in_string"))
        self.symbol_table.open_scope("in_string", "String")
        self.symbol_table.close_scope()

        self.symbol_table.add(
            Symbol("in_int", "Int", "FeatureDef", "in_int -> Int", "IO.in_int"))
        self.symbol_table.open_scope("in_int", "Int")
        self.symbol_table.close_scope()

        self.symbol_table.close_scope()

    def visitClassDef(self, ctx: YAPLParser.ClassDefContext):
        class_name = ctx.TYPE_ID()[0].getText()
        inherits_from = None  # Inicializamos la variable

        if ctx.INHERITS():  # Si hay herencia
            # Obtenemos el tipo padre
            inherits_from = ctx.TYPE_ID()[1].getText()

        # Comprobar el ClassMain
        if class_name == 'Main':
            if inherits_from is not None:
                sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}: La clase Main no puede heredar de otra clase."
                # print(sms)
                self.add_error("La clase Main no puede heredar de otra clase",
                               ctx.start.line, ctx.start.column, sms)

        type = "Object" if inherits_from is None else inherits_from
        # Añadimos el tipo a la tabla de tipos
        if self.type_system.add_type(class_name, inherits_from, ctx, self.add_error):
            myscope = self.symbol_table.current_scope
            definition = Symbol(class_name, type, 'ClassDef', f"{class_name} -> {inherits_from if inherits_from else 'Object'}",
                                f"{inherits_from if inherits_from else 'Object'}.{class_name}", myscope=myscope)
            # Añadimos el símbolo a la tabla de símbolos
            self.symbol_table.add(definition)

            # Abrimos un nuevo alcance en la tabla de símbolos
            self.symbol_table.open_scope(class_name, type)
            if inherits_from is not None:
                symbol_parent = self.symbol_table.lookup(inherits_from)
                if symbol_parent is None:
                    if inherits_from == "IO":
                        self.addIO()
                    else:
                        pass
                        # print(
                        # f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. La clase {class_name} hereda de una clase inexistente.")
                else:
                    # self.recursiveCompi(symbol_parent)
                    parent_scope = None
                    for child in symbol_parent.myscope.children:
                        if child.name == symbol_parent.name:
                            parent_scope = child
                            break

                    if parent_scope is not None:
                        self.recursiveCompi(
                            parent_scope, self.symbol_table.current_scope)

            # Visitamos los hijos del nodo actual

            result = self.visitChildren(ctx)
            self.symbol_table.close_scope()  # Cerramos el alcance en la tabla de símbolos
            return result  # Retornamos el resultado

        else:  # Si add_type retorna False, hubo un error semántico y no procedemos
            if (class_name == "IO"):
                sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}: No se puede redefinir la clase IO."
                # print(sms)
                self.add_error("No se puede redefinir la clase IO",
                               ctx.start.line, ctx.start.column, sms)
            else:
                sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}: No se pudo añadir la clase {class_name}."
                # print(sms)
                self.add_error(
                    f"No se pudo añadir la clase {class_name}", ctx.start.line, ctx.start.column, sms)
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

        # TODO: cuando un meto es override, verificar que los parametros sean iguales

        # Verificar si el nombre del símbolo ya está en la tabla de símbolos actual
        if self.symbol_table.lookup(name) is not None:
            # TODO: Cuando se agregen las clases heredadas se deberia podever cerificar aca el override de una
            node_data = {"type": type, "hasError": True}
            pass

            #print(f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. el símbolo '{name}' ya ha sido declarado en el ámbito actual.")
        else:
            # Si el nombre del símbolo no está en la tabla, agregarlo como nuevo símbolo.
            dev = f"{feature_name}.{name}"
            myscope = self.symbol_table.current_scope
            symbol = Symbol(name, type, 'FormalDef',
                            f"{dev} -> {type}", f"{class_name}.{dev}", myscope=myscope)
            # self.symbol_table.open_scope()

            self.symbol_table.add(symbol)
            self.visitChildren(ctx)

            # self.symbol_table.close_scope()

        # self.symbol_table.display()

        return node_data

    # featureDef : ID LPAREN (formalDef (COMMA formalDef)*)? RPAREN DOBLE TYPE_ID LBRACE (expr)* (returnFunc)? RBRACE
    #       | ID DOBLE TYPE_ID (LEFT_ARROW expr)?
    #       ;

    def visitFeatureDef(self, ctx: YAPLParser.FeatureDefContext):
        node_data = {"type": None, "hasError": False}
        name = ctx.OBJECT_ID().getText()
        obj = ctx.getText()
        if ctx.TYPE_ID():
            type = ctx.TYPE_ID().getText()
        else:
            type = "Object"

        class_context = ctx.parentCtx
        class_name = class_context.TYPE_ID()[0].getText()
        dev = f"{class_name}.{name}"

        if type == 'SELF_TYPE':
            type = class_name

        # Verificar si el nombre del símbolo ya está en la tabla de símbolos actual
        sym = self.symbol_table.lookup(name)
        if sym is not None and sym.is_heredado == False:
            sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. El símbolo '{name}' ya ha sido declarado en el ámbito actual."
            # print(sms)
            self.add_error(
                f"El símbolo '{name}' ya ha sido declarado en el ámbito actual.", ctx.start.line, ctx.start.column, sms)

        myscope = self.symbol_table.current_scope

        symbol = Symbol(name, type, 'FeatureDef',
                        f"{dev} -> {type}", dev, myscope=myscope)
        self.symbol_table.add(symbol)

        buscarFirma = False
        if sym is not None and sym.is_heredado == True:
            buscarFirma = True

        if ctx.LPAREN():
            self.symbol_table.open_scope(name, type)

        children = []
        for child in ctx.getChildren():
            children.append(child)

        children_types = []
        for index, child in enumerate(children):
            if child in self.nodes:
                children_types.append(self.nodes[child])
            else:
                children_types.append(self.visit(child))
                node_data2 = {
                    "type": children_types[-1]["type"], "hasError": False}
                self.nodes[child] = node_data2

        if ctx.LPAREN():
            self.symbol_table.close_scope()

        result = children_types[-1]


        # Error si main tiene params

        if name == "main" and symbol.scope == "Main.main":
            bandera_ = False
            for child_ in children:
                if isinstance(child_,YAPLParser.FormalDefContext):
                    bandera_ = True
                    break

            if bandera_:
                sms = f"Error Sémantico. En la línea {ctx.start.line}, columna {ctx.start.column}: La funcion Main no debe tener parametros"
                #print(sms)
                self.add_error(f"La funcion Main no debe tener parametros",
                                ctx.start.line, ctx.start.column, sms)


        # Si es una funcion
        # OBJECT_ID LPAREN (formalDef (COMMA formalDef)*)? RPAREN COLON TYPE_ID LBRACE expr RBRACE
        # TODO:
        if ctx.LPAREN():
            # print(ctx.getText())
            returns = []
            args = []
            for index, child in enumerate(children):
                if isinstance(child, YAPLParser.ExprContext):
                    returns.append(index)
                if isinstance(child, YAPLParser.FormalDefContext):
                    args.append(index)
            # self.symbol_table.display()
            tipo = children_types[returns[0]]["type"]
            tipo_func = children_types[0]["type"]

            if buscarFirma:
                # verificar la firma
                # params de sym
                old_params = []
                real_scope = None
                for child in sym.myscope.children:
                    if child.name == sym.name:
                        real_scope = child
                        break
                for param in real_scope.symbols:
                    old_params.append(real_scope.symbols[param].type)

                # params de ctx
                new_params = []
                for index in args:
                    new_params.append(children_types[index]["type"])

                signature = self.type_system.checkMethodSignature(
                    symbol, sym, old_params, new_params, ctx, self.add_error)
            else:
                signature = True

            retunr_tip = self.type_system.checkAssigment(
                tipo, tipo_func, ctx, self.add_error)
            if retunr_tip and signature:
                node_data = {"type": tipo_func, "hasError": False}
                self.nodes[ctx] = node_data
                return node_data
            else:
                sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}: El tipo de retorno de la funcion no coincide con el tipo de la clase."
                # print(sms)
                self.add_error(f"El tipo de retorno de la funcion no coincide con el tipo de la clase.",
                               ctx.start.line, ctx.start.column, sms)
                node_data = {"type": tipo_func, "hasError": True}
                self.nodes[ctx] = node_data
                return node_data

        # Si es una asignacion
        # OBJECT_ID COLON TYPE_ID (ASSIGN expr)? ;
        else:
            # print(ctx.getText())
            if type == result["type"] or ctx.ASSIGN() is None:

                node_data = {"type": type, "hasError": False}
                self.nodes[ctx] = node_data
                return node_data
            else:
                sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. El tipo de la expresión no coincide con el tipo del símbolo '{type}' <- '{result['type']}'."
                # print(sms)
                self.add_error(
                    f"El tipo de la expresión no coincide con el tipo del símbolo '{type}' <- '{result['type']}'.", ctx.start.line, ctx.start.column, sms)
                node_data = {"type": type, "hasError": True}
                self.nodes[ctx] = node_data
                return node_data

        return node_data

    def visitExpr(self, ctx: YAPLParser.ExprContext):
        if ctx in self.nodes:
            return self.nodes[ctx]

        if ctx is None:
            return

        if not isinstance(ctx, YAPLParser.ExprContext):
            return

        node_data = {"type": None, "hasError": False}
        obj = ctx.getText()

        # Comprobar si es instance de un LET para crear el simbolo del valor de let
        # LET OBJECT_ID COLON TYPE_ID (ASSIGN expr)? (COMMA OBJECT_ID COLON TYPE_ID (ASSIGN expr)?)* IN expr
        if ctx.LET():
            name = ctx.OBJECT_ID()[0].getText()
            type = ctx.TYPE_ID()[0].getText()
            dev = f"{name}"
            self.symbol_table.open_scope(name, type)
            myscope = self.symbol_table.current_scope
            symbol = Symbol(name, type, 'Let',
                            f"{dev} -> {type}", f"{dev}", myscope=myscope)
            #print("DEFINO X para la funcion ",self.symbol_table.current_scope.parent.name)
            self.symbol_table.add(symbol)
            result = self.visitChildren(ctx)

            self.symbol_table.close_scope()

            # TODO: Comprobar si tiene (ASSIGN expr)? y ver ese error
            node_data = {"type": result["type"], "hasError": False}
            self.nodes[ctx] = node_data
            return node_data
        children = []
        for child in ctx.getChildren():
            children.append(child)

        children_types = []
        for index, child in enumerate(children):
            if child in self.nodes:
                children_types.append(self.nodes[child])
            else:
                children_types.append(self.visit(child))
                node_data2 = {
                    "type": children_types[-1]["type"], "hasError": False}
                self.nodes[child] = node_data2

        # Expresiones de LET OBJECT_ID COLON TYPE_ID (ASSIGN expr)? (COMMA OBJECT_ID COLON TYPE_ID (ASSIGN expr)?)* IN expr
        if (ctx.LET() and ctx.IN()):
            # El valor del nodo sera del ultimo hijo
            node_data = {"type": children_types[-1]["type"], "hasError": False}
            self.nodes[ctx] = node_data
            return node_data

        # LBRACE (expr SEMICOLON)+ RBRACE

        elif (ctx.LBRACE() and ctx.RBRACE()):
            expr_indices = [index for index, child in enumerate(
                children) if isinstance(child, YAPLParser.ExprContext)]
            last_expr_index = expr_indices[-1]

            node_data = {
                "type": children_types[last_expr_index]["type"], "hasError": False}
            self.nodes[ctx] = node_data
            return node_data

        # expr  (AT TYPE_ID)? DOT OBJECT_ID LPAREN  (expr (COMMA expr)*)? RPAREN
        elif (ctx.DOT() and ctx.OBJECT_ID() and ctx.LPAREN() and ctx.RPAREN()):
            class_name = children_types[0]["type"]
            if ctx.AT():
                class_name = ctx.TYPE_ID()[0].getText()
                heredado = self.type_system.is_inherited_from(
                    children_types[0]["type"], class_name, ctx, self.add_error)
                if not heredado:
                    sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. La clase {children_types[0]['type'] } no hereda de {class_name}."
                    # print(sms)
                    self.add_error(
                        f"La clase {children_types[0]['type'] } no hereda de {class_name}.", ctx.start.line, ctx.start.column, sms)
                    node_data = {
                        "type": children_types[-1]["type"], "hasError": True}

            godly_dad = self.symbol_table.lookup_scope(class_name)

            functionReveal = None
            for child in godly_dad.children:
                if child.name == ctx.OBJECT_ID()[0].getText():
                    functionReveal = child

            args = []
            for index, child in enumerate(children):
                if isinstance(child, YAPLParser.ExprContext):

                    args.append(index)
            if functionReveal:
                # Vamos a bsucar todos los paramtros de la funcion que seran sus symbolos
                # Hagarrar todos los expr despues de LPAREN
                # Ignoramos el primer argumento porque es la clase
                objID_type_index = args.pop(0)
                functionargs = functionReveal.symbols

                if len(args) != len(functionargs):
                    sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. La funcion {functionReveal.name} esperaba {len(functionargs)} y se recibieron {len(args)}."
                    # print(sms)
                    self.add_error(
                        f"La funcion {functionReveal.name} esperaba {len(functionargs)} y se recibieron {len(args)}.", ctx.start.line, ctx.start.column, sms)
                    node_data = {"type": functionReveal.type, "hasError": True}
                    self.nodes[ctx] = node_data
                    return node_data
                else:
                    list_params = []
                    node_data = {
                        "type": functionReveal.type, "hasError": False}
                    for param in functionargs:
                        list_params.append(param)
                    for index in range(len(args)):
                        arg_type = children_types[args[index]]["type"]
                        param_type = functionargs[list_params[index]].type
                        if arg_type != param_type:
                            childLine = children[args[index]].start.column
                            sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. El tipo del parametro {list_params[index]} no coincide con el tipo del argumento {list_params[index]} de la funcion {functionReveal.name}. En la linea {ctx.start.line}, columna {childLine}."
                            # print(sms)
                            self.add_error(
                                f"El tipo del parametro {list_params[index]} no coincide con el tipo del argumento {list_params[index]} de la funcion {functionReveal.name}. En la linea {ctx.start.line}, columna {childLine}.", ctx.start.line, ctx.start.column, sms)
                            node_data = {
                                "type": functionReveal.type, "hasError": True}

                objID_type = children_types[objID_type_index]["type"]
                # objID_type = self.symbol_table.lookup(ctx.OBJECT_ID()[0].getText()).type
                #node_data = {"type": objID_type, "hasError": False}
                self.nodes[ctx] = node_data
                return node_data

            else:
                sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. La clase {class_name} no tiene el metodo {ctx.OBJECT_ID()[0].getText()}."
                # print(sms)
                self.add_error(
                    f"La clase {class_name} no tiene el metodo {ctx.OBJECT_ID()[0].getText()}.", ctx.start.line, ctx.start.column, sms)
                tipos = children_types[args[-1]]["type"]
                node_data = {"type": tipos, "hasError": True}

        # OBJECT_ID LPAREN (expr (COMMA expr)*)? RPAREN
        elif (ctx.OBJECT_ID() and ctx.LPAREN() and ctx.RPAREN()):

            args = []
            for index, child in enumerate(children):
                if isinstance(child, YAPLParser.ExprContext):
                    args.append(index)

            symbol = self.symbol_table.lookup(ctx.OBJECT_ID()[0].getText())
            if symbol is None:
                sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. La funcion {ctx.OBJECT_ID()[0].getText()} no esta definida."
                # print(sms)
                self.add_error(
                    f"La funcion {ctx.OBJECT_ID()[0].getText()} no esta definida.", ctx.start.line, ctx.start.column, sms)
                node_data = {
                    "type": children_types[0]["type"], "hasError": True}
                self.nodes[ctx] = node_data
                return node_data
            godly_dad = symbol.myscope
            functionReveal = None
            for child in godly_dad.children:
                if child.name == ctx.OBJECT_ID()[0].getText():
                    functionReveal = child

            if functionReveal:
                functionargs = functionReveal.symbols

                if len(args) != len(functionargs):
                    sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. La funcion {functionReveal.name} esperaba {len(functionargs)} y se recibieron {len(args)}."
                    # print(sms)
                    self.add_error(
                        f"La funcion {functionReveal.name} esperaba {len(functionargs)} y se recibieron {len(args)}.", ctx.start.line, ctx.start.column, sms)
                    node_data = {"type": functionReveal.type, "hasError": True}
                    self.nodes[ctx] = node_data
                    return node_data
                else:
                    list_params = []
                    node_data = {
                        "type": functionReveal.type, "hasError": False}
                    for param in functionargs:
                        list_params.append(param)
                    for index in range(len(args)):
                        arg_type = children_types[args[index]]["type"]
                        param_type = functionargs[list_params[index]].type
                        if arg_type != param_type:
                            childLine = children[args[index]].start.column
                            sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. El tipo del parametro {list_params[index]} no coincide con el tipo del argumento {list_params[index]} de la funcion {functionReveal.name}. En la linea {ctx.start.line}, columna {childLine}."
                            # print(sms)
                            self.add_error(
                                f"El tipo del parametro {list_params[index]} no coincide con el tipo del argumento {list_params[index]} de la funcion {functionReveal.name}. En la linea {ctx.start.line}, columna {childLine}.", ctx.start.line, ctx.start.column, sms)

            node_data = {"type": children_types[0]["type"], "hasError": False}
            self.nodes[ctx] = node_data
            return node_data

        # Expresiones de Asignacion <id> <- <expr>
        elif (ctx.OBJECT_ID() and ctx.ASSIGN()):
            symbol = children_types[0]
            if symbol["type"] is None:
                sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. El símbolo '{ctx.OBJECT_ID()[0]}' no ha sido declarado."
                # print(sms)
                self.add_error(
                    f"El símbolo '{ctx.OBJECT_ID()[0]}' no ha sido declarado.", ctx.start.line, ctx.start.column, sms)
                node_data = {
                    "type": children_types[-1]["type"], "hasError": True}
                self.nodes[ctx] = node_data

            else:
                if not self.type_system.checkAssigment(symbol['type'], children_types[-1]["type"], ctx, self.add_error):
                    sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. El tipo de la expresión no coincide con el tipo del símbolo '{ctx.getText()}', {symbol['type']} <- {children_types[-1]['type']}."
                    # print(sms)
                    self.add_error(
                        f"El tipo de la expresión no coincide con el tipo del símbolo '{ctx.getText()}', {symbol['type']} <- {children_types[-1]['type']}.", ctx.start.line, ctx.start.column, sms)
                    node_data = {
                        "type": children_types[-1]["type"], "hasError": True}
                    self.nodes[ctx] = node_data
                else:
                    # Aquí es donde buscarías el símbolo en tu tabla y actualizarías su valor
                    actual_symbol = self.symbol_table.lookup(
                        ctx.OBJECT_ID()[0].getText())
                    if actual_symbol:
                        # Simplificación para obtener el valor
                        expression_value = ctx.getText().split('<-')[1].strip()
                        actual_symbol.initial_value = expression_value

                    node_data = {
                        "type": children_types[-1]["type"], "hasError": False}
                    self.nodes[ctx] = node_data

        # Expresiones de Comparacion <expr> <op> <expr>
        elif (ctx.PLUS() or ctx.MINUS() or ctx.MULT() or ctx.DIV()):
            # self.symbol_table.display()
            isnum = self.type_system.checkNumeric(
                children_types[0]["type"], children_types[2]["type"])
            # Si no es numerico, intentar hacer el casteo implicito
            if not isnum:
                if children_types[0]["type"] == "Bool":
                    children_types[0]["type"] = "Int"
                elif children_types[2]["type"] == "Bool":
                    children_types[2]["type"] = "Int"
                # Verifica nuevamente si ahora son numericos
                isnum = self.type_system.checkNumeric(
                    children_types[0]["type"], children_types[2]["type"])
            # Si despues de intentar el casteo todavia no es numerico,
            # entonces es un error.
            if not isnum:
                pass
                operador = ctx.PLUS().getText() if ctx.PLUS() else ctx.MINUS().getText(
                ) if ctx.MINUS() else ctx.MULT().getText() if ctx.MULT() else ctx.DIV().getText()
                sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. Los tipos de las expresiones no coinciden. No se puede operar ({operador}) entre {children_types[0]['type']} y {children_types[2]['type']}."
                # print(sms)
                self.add_error(
                    f"Los tipos de las expresiones no coinciden. No se puede operar ({operador}) entre {children_types[0]['type']} y {children_types[2]['type']}.", ctx.start.line, ctx.start.column, sms)
                node_data = {
                    "type": children_types[-1]["type"], "hasError": True}
                self.nodes[ctx] = node_data
                return node_data
            else:
                node_data = {
                    "type": children_types[-1]["type"], "hasError": False}
                self.nodes[ctx] = node_data
                return node_data

        # LPAREN expr RPAREN
        elif (ctx.LPAREN() and ctx.RPAREN()):
            node_data = {"type": children_types[1]["type"], "hasError": False}
            self.nodes[ctx] = node_data

        # Return type OBJECT_ID
        elif ctx.OBJECT_ID():
            # Obtener el texto del token
            object_id = ctx.OBJECT_ID()[0].getText()

            if object_id == "self":
                # Aquí, sabemos que estamos tratando con 'self'.
                # Obtener el tipo del padre del alcance actual
                type = self.symbol_table.current_scope.type
                node_data = {"type": type, "hasError": False}

            else:
                # Aquí, object_id es una variable y puedes buscar su tipo en tu tabla de símbolos.
                symbol = self.symbol_table.lookup(object_id)
                if symbol:
                    variable_type = symbol.type  # Suponiendo que tu símbolo tiene un campo 'type'
                    node_data = {"type": variable_type, "hasError": False}
                else:
                    sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}: la variable {object_id} no está definida."
                    print(sms)
                    self.add_error(f"Error: la variable {object_id} no está definida.",ctx.start.line,ctx.start.column,sms)
                    # Manejar el error como prefieras

        # NEW TYPE_ID
        elif ctx.NEW():
            type_id = ctx.TYPE_ID()[0].getText()  # Obtener el nombre del tipo

            default_value = None  # Valor predeterminado para asignar al nuevo objeto
            if type_id == 'Int':
                default_value = 0
            elif type_id == 'String':
                default_value = ""
            elif type_id == 'Bool':
                default_value = False

            node_data = {"type": type_id, "hasError": False,
                         "defaultValue": default_value}

        elif ctx.NEG():
            type = children_types[-1]["type"]
            if type == "Int" or type == "Object":
                node_data = {"type": type, "hasError": False}
            else:
                sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. No se puede negar una expresión de tipo {type}."
                # print(sms)
                self.add_error(
                    f"No se puede negar una expresión de tipo {type}.", ctx.start.line, ctx.start.column, sms)

        elif ctx.NOT():
            type = children_types[-1]["type"]
            if type == "Bool" or type == "Object":
                node_data = {"type": type, "hasError": False}
            else:
                sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. No se puede negar una expresión de tipo {type}."
                # print(sms)
                self.add_error(
                    f"No se puede negar una expresión de tipo {type}.", ctx.start.line, ctx.start.column, sms)

        # IF expr THEN expr ELSE expr FI
        elif ctx.IF():
            args = []
            for index, child in enumerate(children):
                if isinstance(child, YAPLParser.ExprContext):
                    args.append(index)
            comparador = args.pop(0)
            compType = children_types[comparador]["type"]

            # Intento de casteo implícito de Int a Bool
            if compType == "Int":
                compType = "Bool"

            accep = ["Bool", "Object"]
            if compType not in accep:
                print(
                    f"Error semantico: la condicion del if debe ser de tipo Bool. ")

            typeif = self.type_system.comperIF(
                children_types[args[0]]["type"], children_types[args[1]]["type"])

            node_data = {"type": typeif, "hasError": False}
            self.nodes[ctx] = node_data
            return node_data

        elif ctx.WHILE():
            # print(ctx.getText())
            args = []
            for index, child in enumerate(children):
                if isinstance(child, YAPLParser.ExprContext):
                    args.append(index)
            comparador = args.pop(0)

            tipo_comparador = children_types[comparador]["type"]

            # Intento de casteo implícito de Int a Bool
            if tipo_comparador == "Int":
                tipo_comparador = "Bool"

            if tipo_comparador != "Bool":
                print(
                    f"Error semantico: la condicion del if debe ser de tipo Bool. ")

            node_data = {"type": "Object", "hasError": False}
            self.nodes[ctx] = node_data
            return node_data

        elif ctx.ISVOID():
            node_data = {"type": "Bool", "hasError": False}
            self.nodes[ctx] = node_data
            return node_data

        elif ctx.LE() or ctx.LT() or ctx.EQ():
            posible, type = self.type_system.CheckComp(
                children_types[0]["type"], children_types[2]["type"])
            if posible:
                node_data = {"type": type, "hasError": False}
            else:
                sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. No se puede comparar una expresión de tipo {type} con una expresión de tipo {children_types[2]['type']}."
                # print(sms)
                self.add_error(
                    f"No se puede comparar una expresión de tipo {type} con una expresión de tipo {children_types[2]['type']}.", ctx.start.line, ctx.start.column, sms)
                node_data = {"type": "Object", "hasError": True}

            self.nodes[ctx] = node_data
            return node_data

        elif (ctx.INT()):
            return {"type": 'Int', "hasError": False}
        elif (ctx.STRING()):
            return {"type": 'String', "hasError": False}
        elif (ctx.TRUE() or ctx.FALSE()):
            return {"type": 'Bool', "hasError": False}

        return node_data

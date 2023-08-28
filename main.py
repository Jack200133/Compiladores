import argparse
from graphviz import Digraph
from antlr4 import *
from antlr4 import ParseTreeVisitor
from antlr4.error.ErrorListener import ErrorListener
from yapl.YAPLLexer import YAPLLexer
from yapl.YAPLParser import YAPLParser
from yapl.YAPLListener import YAPLListener
import os

class MyErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        tokenError = offendingSymbol.text
        if "extraneous input" in msg:
            print(f"Error en la línea {line}, posición {column}: {tokenError}; Entrada no esperada.")
        elif "no viable alternative at input" in msg:
            print(f"Error en la línea {line}, posición {column}: {tokenError}; Entrada no reconocida.")
        elif "missing ';' at" in msg:
            print(f"Error en la línea {line}, posición {column}: Falta ';' en la entrada.")
        elif "mismatched input" in msg:
            print(f"Error en la línea {line}, posición {column}: Entrada no coincide con lo esperado.")
        else:
            print(f"Error de sintaxis en la línea {line}, posición {column}: {msg}")


    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        print("Error de ambigüedad entre tokens.")

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        print("Error al intentar contexto completo.")

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        print("Error de sensibilidad de contexto.")


class Symbol:
    def __init__(self, name, _type, definicion=None, derivation=None,scope = None):
        self.name = name
        self.type = _type
        self.definicion = definicion
        self.derivation = derivation
        self.scope = scope

    def __str__(self):
        if len(self.name) < 8:
            return f"{self.name}\t\t{self.type}\t{self.definicion}\t{self.derivation}"
        else:
            return f"{self.name}\t{self.type}\t{self.definicion}\t{self.derivation}"

class Scope:
    def __init__(self, parent=None, number=0,name="global", type="Object"):
        self.number = number
        self.symbols = {}
        self.parent = parent
        self.children = []
        self.name = name
        self.type = type

    def add_child(self, child):
        self.children.append(child)

    def add(self, symbol):
        self.symbols[symbol.name] = symbol

    def lookup(self, name):
        return self.symbols.get(name, None)

    def display(self):
        print(f"\nAlcance: {self.number} \t{self.name} \t{self.type}")
        for symbol in self.symbols.values():
            print(str(symbol))
        for child in self.children:
            child.display()

    def __str__(self):
        return ', '.join(str(symbol) for symbol in self.symbols.values())


class SymboTable:
    def __init__(self):
        self.root = Scope()
        self.current_scope = self.root
        self.scope_counter = 0

    def open_scope(self, name,type):
        self.scope_counter += 1
        new_scope = Scope(parent=self.current_scope, number=self.scope_counter,name=name,type=type)
        self.current_scope.add_child(new_scope)
        self.current_scope = new_scope

    def close_scope(self):
        self.current_scope = self.current_scope.parent


    def add(self, symbol):
        self.current_scope.add(symbol)

    def lookup(self, name):
        scope = self.current_scope 
        while scope:
            symbol = scope.lookup(name)
            if symbol:
                return symbol
            scope = scope.parent
        return None

    def replace(self, symbol, scope=None):
        scope_to_replace = scope if scope else self.current_scope
        if scope_to_replace in self.table:
            for i, existing_symbol in enumerate(self.table[scope_to_replace]):
                if existing_symbol.name == symbol.name:
                    self.table[scope_to_replace][i] = symbol
                    return
        raise Exception("Símbolo no encontrado. No se puede reemplazar.")

    def delete(self, name, scope=None):
        scope_to_delete = scope if scope else self.current_scope
        if scope_to_delete in self.table:
            self.table[scope_to_delete] = [symbol for symbol in self.table[scope_to_delete] if symbol.name != name]

    def display(self):
        print("Tabla de Símbolos:")
        print("Nombre\t\tTipo\tdefinicion\tderivation")
        self.root.display()
        print(self.root)
        # for scope, symbols in self.table.items():
        #     print(f"\nAlcance: {scope}")
        #     for symbol in symbols:
        #         print(str(symbol))

class TypeSystem:
    def __init__(self):
        self.table = {}
        self.basic_types = ['Int', 'Bool', 'String']
        self.special_types = ['IO', 'Object']
        
        for t in self.basic_types:
            self.table[t] = []
        
        self.table['IO'] = []  # Puedes añadir aquí los métodos predefinidos de IO
        self.table['Object'] = []  # Clase base para todos los objetos
        
    def add_type(self, type_name, parent_type=None):
        if type_name in self.table:
            print(f"Error semántico: El tipo {type_name} ya existe.")
            return False

        if parent_type:
            if parent_type in self.basic_types:
                print(f"Error semántico: No se puede heredar de un tipo básico.")
                return False

            if parent_type not in self.table:
                print(f"Error semántico: el tipo '{parent_type}' no existe. No se puede heredar de un tipo inexistente.")
                return False
        else:
            parent_type = 'Object'  # Si no se especifica un tipo padre, se hereda de Object

        self.table[type_name] = [parent_type]
        return True
    
    def check(self, type1, type2):
        if type1 in self.table[type2]:
            return True
        return False

    def checkNumeric(self, type1, type2):
        if type1 in self.basic_types and type1 == 'Int' and type2 in self.basic_types and type2 == 'Int':
            return True
        return False

    def checkAssigment(self, id_type, expr_type):
        if expr_type == id_type:
            return True

        if self.is_inherited_from(expr_type, id_type):
            return True
        
        return False

    def is_inherited_from(self, child_type, parent_type):
        if child_type in self.table and parent_type in self.table[child_type]:
            return True

        for inherited_type in self.table.get(parent_type, []):
            if self.is_inherited_from(child_type, inherited_type):
                return True
        
        return False
    
    def checkMethodSignature(self, method_A, method_B):
        # Asumiendo que los métodos son diccionarios con claves "return_type" y "arg_types"
        # Verifica que los métodos A y B tengan la misma firma
        if method_A['return_type'] != method_B['return_type']:
            return False
        if method_A['arg_types'] != method_B['arg_types']:
            return False
        return True

    def __str__(self):
        return str(self.table)

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
            #self.symbol_table.display()
            #print(self)
            if symbol is not None:
                return {"type":symbol.type, "hasError": False}
            else:
                return {"type":None, "hasError": True}



    def visitProgram(self, ctx: YAPLParser.ProgramContext):
        #print("Programa analizado correctamente.")
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
            definition = Symbol(class_name, type, 'ClassDef', f"{class_name} -> {inherits_from if inherits_from else 'Object'}", f"{inherits_from if inherits_from else 'Object'}.{class_name}")
            self.symbol_table.add(definition)  # Añadimos el símbolo a la tabla de símbolos

            self.symbol_table.open_scope(class_name,type)  # Abrimos un nuevo alcance en la tabla de símbolos
            result = self.visitChildren(ctx)  # Visitamos los hijos del nodo actual
            self.symbol_table.close_scope()  # Cerramos el alcance en la tabla de símbolos
            return result  # Retornamos el resultado

        else:  # Si add_type retorna False, hubo un error semántico y no procedemos
            print(f"Error semántico: No se pudo añadir la clase {class_name}.")
            return None  # Podrías manejar el error como mejor te parezca

    def visitFormalDef(self, ctx: YAPLParser.FormalDefContext):
        name = ctx.OBJECT_ID().getText()
        # print(ctx.ID())
        type = ctx.TYPE_ID().getText()
        node_data = {"type": type, "hasError": False}

        # Verificar de que featureDef proviene
        feature_context = ctx.parentCtx
        feature_name = feature_context.OBJECT_ID().getText()
        print(feature_name)
        class_context = feature_context.parentCtx
        class_name = class_context.TYPE_ID()[0].getText()

        # Verificar si el nombre del símbolo ya está en la tabla de símbolos actual
        if self.symbol_table.lookup(name) is not None:
            node_data = {"type": type, "hasError": True}
            pass
            #print(f"Error semántico: el símbolo '{name}' ya ha sido declarado en el ámbito actual.")
        else:
            # Si el nombre del símbolo no está en la tabla, agregarlo como nuevo símbolo.
            dev = f"{feature_name}.{name}"
            symbol = Symbol(name, type, 'FormalDef', f"{dev} -> {type}",f"{class_name}.{dev}")
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

        symbol = Symbol(name, type, 'FeatureDef', f"{dev} -> {type}", dev)
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
        print(children_types,"\n")
        if (ctx.LET() and ctx.IN()):
            #Agregar el simbolo nuevo a la tabla 
            name = ctx.OBJECT_ID()[0].getText()
            type = ctx.TYPE_ID()[0].getText()
            dev = f"{name}"
            self.symbol_table.open_scope(name,type)
            symbol = Symbol(name, type, 'Let', f"{dev} -> {type}",f"{dev}")
            self.symbol_table.add(symbol)
            self.visitChildren(ctx)
            self.symbol_table.close_scope()
            node_data = {"type": children_types[-1]["type"], "hasError": False}
            self.nodes[ctx] = node_data
            return node_data
        
        # LBRACE (expr SEMICOLON)+ RBRACE

        elif (ctx.LBRACE() and ctx.RBRACE()):
            print(ctx.getText())
            expr_indices = [index for index, child in enumerate(children) if isinstance(child, YAPLParser.ExprContext)]
            last_expr_index = expr_indices[-1]
            
            node_data = {"type": children_types[last_expr_index]["type"], "hasError": False}
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
            print("MULTIPLICACION: ")
            ## Texto de la multiplicacion
            print(ctx.getText())
            self.symbol_table.display()
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

                
        elif (ctx.INT()):
            return {"type":'Int', "hasError": False}


        return node_data
        return self.visitChildren(ctx)



def build_tree(dot, node, parser, parent=None):
    if isinstance(node, TerminalNode):
        dot.node(str(id(node)), node.getText())
    else:
        name = parser.ruleNames[node.getRuleIndex()]
        dot.node(str(id(node)), name)
    if parent is not None:
        dot.edge(str(id(parent)), str(id(node)))

    # Check if the node is not terminal
    if hasattr(node, 'children'):
        for child in node.children:
            build_tree(dot, child, parser, node)


def main():
    #     # Set up command line argument parsing
    # parser = argparse.ArgumentParser(description='Process some file.')
    # parser.add_argument('input_file', type=str, help='The input file to process.')

    # # # Parse command line arguments
    # args = parser.parse_args()

    # Verifica si Graphviz está instalado y agregado al PATH del sistema
    # Si no lo está, agrega la ubicación correcta del ejecutable "dot"
    # if "C:\\Program Files\\Graphviz\\bin" not in os.environ['PATH']:
    #     os.environ['PATH'] += os.pathsep + "C:\\Program Files\\Graphviz\\bin"

    # # Set up the input and lexer
    # input_stream = FileStream(args.input_file)
    input_stream = FileStream('./realinput.txt')
    lexer = YAPLLexer(input_stream)
    # Remove the default error listener and add the custom one
    lexer.removeErrorListeners()
    lexer.addErrorListener(MyErrorListener())

    # Set up the parser
    stream = CommonTokenStream(lexer)
    parser = YAPLParser(stream)

    # Remove the default error listener and add the custom one
    parser.removeErrorListeners()
    parser.addErrorListener(MyErrorListener())

    # Parse the input
    tree = parser.program()

    # Check for errors before building tree
    if parser.getNumberOfSyntaxErrors() == 0:  # Añadido para verificar errores sintácticos
        # Build the graph
        dot = Digraph()
        build_tree(dot, tree, parser)

        # Render the graph
        dot.render(filename='./output/grafo', format='png', cleanup=True)
        dot.view()
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.visit(tree)
        print("\nTabla de Símbolos:")
        print("Nombre\t\tTipo")
        #for symbol, value in semantic_analyzer.symbol_table.table.items():
            #print(f"{symbol}\t\t{value.type}")

        print("\n\nTipos:")
        semantic_analyzer.symbol_table.display()


if __name__ == '__main__':
    main()

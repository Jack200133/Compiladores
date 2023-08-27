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
    def __init__(self, parent=None, number=0):
        self.number = number
        self.symbols = {}
        self.parent = parent
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def add(self, symbol):
        self.symbols[symbol.name] = symbol

    def lookup(self, name):
        return self.symbols.get(name, None)

    def display(self):
        print(f"\nAlcance: {self.number}")
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

    def open_scope(self):
        self.scope_counter += 1
        new_scope = Scope(parent=self.current_scope, number=self.scope_counter)
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
        self.table['Int'] = ['Int']
        self.table['Bool'] = ['Bool']
        self.table['String'] = ['String']

    def check(self, type1, type2):
        if type1 in self.table[type2]:
            return True
        else:
            return False

    def checkNumeric(self, type1, type2):
        type1 = type1["type"]
        type2 = type2["type"]
        if type1 in self.table['Int'] and type2 in self.table['Int']:
            return True
        # Buscar si es heredado de Int
        elif self.is_inherited_from(type1, 'Int') and self.is_inherited_from(type2, 'Int'):
            return True
        else:
            return False

    def checkAssigment(self, id_type, expr_type):
        # Comprobar si el tipo de la expresión coincide con el tipo declarado para el ID o es de un tipo heredado.
        if expr_type == id_type or expr_type in self.table[id_type]:
            return True

        if self.is_inherited_from(expr_type, id_type):
            return True

        return False

    def is_inherited_from(self, childe_type, parent_type):
        if childe_type in self.table[parent_type]:
            return True

        for inherited_type in self.table[parent_type]:
            if self.is_inherited_from(childe_type, inherited_type):
                return True

        return False

    def add_type(self, type_name, parent_type):
        # Solo se pueden agregar a tipos que ya existen
        if parent_type in self.table:
            self.table[type_name] = [parent_type]
        else:
            print(f"Error semántico: el tipo '{parent_type}' no existe. No se puede heredar de un tipo inexistente & la herencia múltiple no es soportada.")


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
        elif isinstance(tree, YAPLParser.ReturnFuncContext):
            result = self.visitReturnFunc(tree)
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
        #print("Programa analizado correctamente.")
        self.symbol_table = SymboTable()
        self.symbol_table.open_scope()
        self.visitChildren(ctx)
        self.symbol_table.close_scope()
        return

    def visitClassDef(self, ctx: YAPLParser.ClassDefContext):
        class_name = ctx.TYPE_ID()[0].getText()
        inherits_from = None
        if ctx.INHERITS():
            inherits_from = ctx.TYPE_ID()[1].getText()
            self.type_system.add_type(class_name, inherits_from)
        definition = Symbol(class_name, 'Class', 'ClassDef', f"{class_name} -> {inherits_from}", f"{inherits_from}.{class_name}")
        self.symbol_table.add(definition)
        self.symbol_table.open_scope()
        result = self.visitChildren(ctx)
        self.symbol_table.close_scope()
        return result

    # featureDef : ID LPAREN (formalDef (COMMA formalDef)*)? RPAREN DOBLE TYPE_ID LBRACE (expr)* (returnFunc)? RBRACE
    #       | ID DOBLE TYPE_ID (LEFT_ARROW expr)?
    #       ;

    def visitFeatureDef(self, ctx: YAPLParser.FeatureDefContext):
        node_data = {"type": None, "hasError": False}
        name = ctx.ID().getText()
        type = ctx.TYPE_ID().getText()

        class_context = ctx.parentCtx
        class_name = class_context.TYPE_ID()[0].getText()
        dev = f"{class_name}.{name}"

        # Verificar si el nombre del símbolo ya está en la tabla de símbolos actual
        if self.symbol_table.lookup(name) is not None:
            pass
            print(f"Error semántico: el símbolo '{name}' ya ha sido declarado en el ámbito actual.")

        symbol = Symbol(name, type, 'FeatureDef', f"{dev} -> {type}", dev)
        self.symbol_table.add(symbol)
        result = self.visitChildren(ctx)


        # Si es una funcion
        #ID LPAREN (formalDef (COMMA formalDef)*)? RPAREN DOBLE TYPE_ID LBRACE (expr)* (returnFunc)? RBRACE
        if ctx.LPAREN():
            pass



        # Si es una asignacion
        # ID DOBLE TYPE_ID (LEFT_ARROW expr)?
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
        



    def visitFormalDef(self, ctx: YAPLParser.FormalDefContext):
        name = ctx.ID().getText()
        # print(ctx.ID())
        type = ctx.TYPE_ID().getText()


        # Verificar de que featureDef proviene
        feature_context = ctx.parentCtx
        feature_name = feature_context.ID().getText()
        print(feature_name)
        class_context = feature_context.parentCtx
        class_name = class_context.TYPE_ID()[0].getText()

        # Verificar si el nombre del símbolo ya está en la tabla de símbolos actual
        if self.symbol_table.lookup(name) is not None:
            pass
            #print(f"Error semántico: el símbolo '{name}' ya ha sido declarado en el ámbito actual.")
        else:
            # Si el nombre del símbolo no está en la tabla, agregarlo como nuevo símbolo.
            dev = f"{feature_name}.{name}"
            symbol = Symbol(name, type, 'FormalDef', f"{dev} -> {type}",dev)
            self.symbol_table.open_scope()
            self.symbol_table.add(symbol)
            self.symbol_table.close_scope()

        return self.visitChildren(ctx)
    

    def visitReturnFunc(self, ctx: YAPLParser.ReturnFuncContext):
        expr_type = self.visit(ctx.expr())
        if not self.type_system.check(expr_type, 'Int'):  # Reemplazar 'Int' con el tipo de retorno esperado
            pass
            #print(f"Error semántico: tipo de retorno incorrecto para función, esperado Int pero se obtuvo {expr_type}")
        return self.visitChildren(ctx)
    

    def visitExpr(self, ctx: YAPLParser.ExprContext):
        node_data = {"type": None, "hasError": False}
        print(f"Visitando expresión: {ctx.getText()}")
        
        if ctx in self.nodes:
            return self.nodes[ctx]

        if ctx is None:
            return

        children_types = []
        for child in ctx.children:
            if child in self.nodes:
                children_types.append(self.nodes[child])
            else:
                children_types.append(self.visit(child))
                node_data = {"type": children_types[-1]["type"], "hasError": False}
                self.nodes[child] = node_data

        # Expresiones de Asignacion <id> <- <expr>
        print(children_types,"\n")
        if (ctx.ID() and ctx.LEFT_ARROW()):
            symbol = children_types[0]
            if symbol["type"] is None:
                pass
                print(f"Error semántico: el símbolo '{ctx.ID().getText()}' no ha sido declarado.")
                node_data = {"type": children_types[-1]["type"], "hasError": True}
                self.nodes[ctx] = node_data
                
            else:
                if not self.type_system.checkAssigment(symbol['type'],children_types[-1]["type"]):
                    pass
                    print(f"Error semántico: el tipo de la expresión no coincide con el tipo del símbolo '{ctx.ID().getText()}'. En la linea {ctx.start.line}, columna {ctx.start.column}.")
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
            if not self.type_system.checkNumeric(children_types[0], children_types[2]):
                pass
                operador = ctx.PLUS().getText() if ctx.PLUS() else ctx.MINUS().getText() if ctx.MINUS() else ctx.MULT().getText() if ctx.MULT() else ctx.DIV().getText()
                print(f"Error semántico: los tipos de las expresiones no coinciden. En la linea {ctx.start.line}, columna {ctx.start.column}. No se puede operar ({operador}) entre {children_types[0]['type']} y {children_types[2]['type']}.")
                node_data = {"type": children_types[-1]["type"], "hasError": True}
                self.nodes[ctx] = node_data
            else:
                node_data = {"type": children_types[-1]["type"], "hasError": False}
                self.nodes[ctx] = node_data


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
    input_stream = FileStream('./shapes.txt')
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

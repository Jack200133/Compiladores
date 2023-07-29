import argparse
from graphviz import Digraph
from antlr4 import *
from antlr4 import ParseTreeVisitor
from antlr4.error.ErrorListener import ErrorListener
from yapl.YAPLLexer import YAPLLexer
from yapl.YAPLParser import YAPLParser
from yapl.YAPLListener import YAPLListener


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
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __str__(self):
        return f"{self.name} : {self.type}"

class SymboTable:
    def __init__(self):
        self.table = {}

    def add(self, symbol):
        self.table[symbol.name] = symbol
    
    def lookup(self, name):
        return self.table[name]
    
    def __str__(self):
        return str(self.table)
    

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

    def __str__(self):
        return str(self.table)


class SemanticAnalyzer(ParseTreeVisitor):

    def __init__(self):
        self.symbol_table = SymboTable()
        self.type_system = TypeSystem()

    def visit(self, tree):
        # Obten el método de visita apropiado para el tipo de nodo.
        result = self.visitChildren(tree)

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

        return result

    def visitChildren(self, node):
        result = None
        if not isinstance(node, TerminalNode) and node.children:
            for child in node.children:  # Recorre los hijos en orden inverso
                result = self.visit(child)

        # Si es terminal regresar el tipo
        if isinstance(node, TerminalNode):
            result = node.getSymbol().type
        # Aquí puedes poner código adicional que se ejecuta después de visitar todos los hijos del nodo.

        return result

    

    def visitProgram(self, ctx: YAPLParser.ProgramContext):
        print("Programa analizado correctamente.")
        self.symbol_table = SymboTable()
        return self.visitChildren(ctx)
    
    def visitClassDef(self, ctx: YAPLParser.ClassDefContext):
        print(f"Visitando clase: {ctx.TYPE_ID().getText()}")
        class_name = ctx.TYPE_ID().getText()
        symbol = Symbol(class_name, 'Class')
        self.symbol_table.add(symbol)
        return self.visitChildren(ctx)
    
    # featureDef : ID LPAREN (formalDef (COMMA formalDef)*)? RPAREN DOBLE TYPE_ID LBRACE (expr)* (returnFunc)? RBRACE
    #       | ID DOBLE TYPE_ID (LEFT_ARROW expr)?
    #       ;

    def visitFeatureDef(self, ctx: YAPLParser.FeatureDefContext):
        print(f"Visitando función: {ctx.ID().getText()}")
        name = ctx.ID().getText()
        type = ctx.TYPE_ID().getText()
        symbol = Symbol(name, type)
        self.symbol_table.add(symbol)
        return self.visitChildren(ctx)
    
    def visitFormalDef(self, ctx: YAPLParser.FormalDefContext):
        name = ctx.ID().getText()
        type = ctx.TYPE_ID().getText()
        symbol = Symbol(name, type)
        self.symbol_table.add(symbol)
        return self.visitChildren(ctx)

    def visitReturnFunc(self, ctx: YAPLParser.ReturnFuncContext):
        expr_type = self.visit(ctx.expr())
        if not self.type_system.check(expr_type, 'Int'):  # Reemplazar 'Int' con el tipo de retorno esperado
            print(f"Error semántico: tipo de retorno incorrecto para función, esperado Int pero se obtuvo {expr_type}")
        return self.visitChildren(ctx)

    def visitExpr(self, ctx: YAPLParser.ExprContext):
        print(f"Visitando expresión: {ctx.getText()}")
        if ctx.PLUS():
            self.verify_operation(ctx, ctx.PLUS().getText())
        elif ctx.MINUS():
            self.verify_operation(ctx, ctx.MINUS().getText())
        # Agrega aquí más operadores según sea necesario

        return self.visitChildren(ctx)
    
    def verify_operation(self, ctx, operator):
        type1 = self.visit(ctx.expr(0))  # obtener el tipo de la primera expresión
        type2 = self.visit(ctx.expr(1))  # obtener el tipo de la segunda expresión

        if not self.type_system.check(type1, type2):
            print(f"Operación inválida: {operator} no se puede aplicar a {type1} y {type2}.")


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

    # # Set up the input and lexer
    # input_stream = FileStream(args.input_file)
    input_stream = FileStream('./math.txt')
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


if __name__ == '__main__':
    main()

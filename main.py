from antlr4 import *
from yapl.YAPLLexer import YAPLLexer
from yapl.YAPLParser import YAPLParser
from graphviz import Digraph
from antlr4.error.ErrorListener import ErrorListener
import argparse

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
        # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Process some file.')
    parser.add_argument('input_file', type=str, help='The input file to process.')

    # Parse command line arguments
    args = parser.parse_args()

    # Set up the input and lexer
    input_stream = FileStream(args.input_file)
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

if __name__ == '__main__':
    main()

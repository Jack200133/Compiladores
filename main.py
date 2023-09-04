import tkinter as tk
from tkinter import filedialog
from graphviz import Digraph
from antlr4 import *
from modules.ErrorListener import MyErrorListener
from modules.Semantic import SemanticAnalyzer
from yapl.YAPLLexer import YAPLLexer
from yapl.YAPLParser import YAPLParser


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
    input_stream = FileStream('./inputs/recu.txt', encoding="utf-8")
    #input_stream = FileStream('./coolExp/recur.cl', encoding="utf-8")
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

    # Build the graph
    dot = Digraph()
    build_tree(dot, tree, parser)

    # Render the graph
    dot.render(filename='./output/grafo', format='png', cleanup=True)
    dot.view()
    semantic_analyzer = SemanticAnalyzer()
    semantic_analyzer.visit(tree)
    semantic_analyzer.symbol_table.displayTree()
    print(len(semantic_analyzer.ErrorList))
    for Error in semantic_analyzer.ErrorList:
        print(Error['full_error'])
    # semantic_analyzer.symbol_table.display()
    # symbols = semantic_analyzer.symbol_table.get_all_symbols()
    # print("\nTabla de Símbolos:")
    # for symbol in symbols:
    #     print(symbol)


if __name__ == '__main__':
    main()

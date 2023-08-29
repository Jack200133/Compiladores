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
    input_stream = FileStream('./inputs/realinput.txt')
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

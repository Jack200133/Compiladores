from graphviz import Digraph
from antlr4 import *
from modules.ErrorListener import MyErrorListener
from modules.TreeDirections import TreeDirections
from modules.Semantic import SemanticAnalyzer
from yapl.YAPLParser import YAPLParser
from yapl.YAPLLexer import YAPLLexer


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

def recycle_temporals(code):
    instructions = code.strip().split('\n')
    
    # Get lifespan of each temporary
    lifespan = {}
    for idx, line in enumerate(instructions):
        tokens = line.split()
        for token in tokens:
            if token.startswith('t'):
                if token not in lifespan:
                    lifespan[token] = [idx, idx]
                else:
                    lifespan[token][1] = idx
                    
    # Recycle temporaries
    recycled = {}
    free_temps = set()
    new_instructions = []
    for idx, line in enumerate(instructions):
        tokens = line.split()
        
        # Substitute temporaries based on recycled mapping
        for token_idx, token in enumerate(tokens):
            if token.startswith('t'):
                if token in recycled:
                    tokens[token_idx] = recycled[token]
                elif free_temps:
                    recycled_token = free_temps.pop()
                    recycled[token] = recycled_token
                    tokens[token_idx] = recycled_token
                else:
                    recycled[token] = token
        
        # Check for temporaries that are not used anymore and add to free_temps
        for temp, (start, end) in lifespan.items():
            if idx == end and temp in recycled and recycled[temp] == temp:
                free_temps.add(temp)
                
        new_instructions.append(' '.join(tokens))
    
    return '\n'.join(new_instructions)

def main():
    # # Set up the input and lexer
    # input_stream = FileStream(args.input_file)
    input_stream = FileStream('./inputs/realinput.txt', encoding="utf-8")
    #input_stream = FileStream('./coolExp/recur.cl', encoding="utf-8")
    lexer = YAPLLexer(input_stream)
    # Remove the default error listener and add the custom one
    lexer.removeErrorListeners()
    lexer_listener = MyErrorListener()
    lexer.addErrorListener(lexer_listener)

    # Set up the parser
    stream = CommonTokenStream(lexer)
    parser = YAPLParser(stream)

    # Remove the default error listener and add the custom one
    parser.removeErrorListeners()
    parser.addErrorListener(lexer_listener)

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
    for Error in lexer_listener.ErrorList:
        print(Error)
    for Error in semantic_analyzer.ErrorList:
        print(Error['full_error'])
    symbols = semantic_analyzer.symbol_table.get_all_symbols()
    print("\nTabla de Símbolos:")
    print(f"{'Nombre':15}{'Tipo':15}{'Definición':15}{'Derivación':30}{'Valor Inicial':15}{'Heredado':10}{'Alcance':10}{'Pos Memoria':15}{'Uso Memoria':10}")
    for symbol in symbols:
        print(symbol)

    #semantic_analyzer.symbol_table.display()
    #semantic_analyzer.symbol_table.displayTree()
    

    if len(semantic_analyzer.ErrorList) > 0 or len(lexer_listener.ErrorList) > 0:
        return
    treedirectionsInfoPath = "./output/3D/tripletasR.txt"
    my3D = TreeDirections(semantic_analyzer.symbol_table,treedirectionsInfoPath)
    my3D.visit(tree)

    treedirectionsInfo = ""

    with open(treedirectionsInfoPath, 'r') as file:
        treedirectionsInfo = file.read()

    result = recycle_temporals(treedirectionsInfo)
    # with open('./output/3D/tripletasR.txt', 'a') as file:
    #     file.write(result)


if __name__ == '__main__':
    main()

from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import os
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

# (importa otras bibliotecas necesarias aquí)

app = Flask(__name__)
CORS(app, origins=['http://localhost:5173', 'http://127.0.0.1:5173'])

@app.route('/has_errors', methods=['POST'])
def generate_images():
    # Obtén el código del cuerpo de la solicitud
    code = request.json['code']
    print(code)
    input_stream = InputStream(code)
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
    #dot.view()
    semantic_analyzer = SemanticAnalyzer()
    semantic_analyzer.visit(tree)
    semantic_analyzer.symbol_table.displayTree()
    print(len(semantic_analyzer.ErrorList))
    
    complete_error_list = lexer_listener.ErrorList + semantic_analyzer.ErrorList

    # semantic_analyzer.symbol_table.display()
    # (Usa el código para generar las imágenes y el array de errores aquí)

    # Convierte las imágenes a base64
    with open('./output/grafo.png', 'rb') as grafo_image:
        grafo_base64 = base64.b64encode(grafo_image.read()).decode('utf-8')

    with open('./output/symbol_table.png', 'rb') as symbol_table_image:
        symbol_table_base64 = base64.b64encode(symbol_table_image.read()).decode('utf-8')


    # Devuelve las imágenes en base64 y el array de errores como respuesta JSON
    response = {
        'grafo_image': grafo_base64,
        'symbol_table_image': symbol_table_base64,
        'errors': complete_error_list
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)

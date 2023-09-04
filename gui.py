import tkinter as tk
from tkinter import ttk
from antlr4 import InputStream, CommonTokenStream
from graphviz import Digraph
import platform
import subprocess
import os

from modules.ErrorListener import MyErrorListener
from modules.Semantic import SemanticAnalyzer
from yapl.YAPLLexer import YAPLLexer
from yapl.YAPLParser import YAPLParser
from antlr4.tree.Tree import TerminalNode

# Colores
colors = {
    'light_blue': '#8EA4D2',
    'medium_blue': '#6279B8',
    'dark_blue': '#49516F',
    'dark_green': '#496F5D',
    'light_green': '#4C9F70',
    'black': '#000000'
}

# Obtener el directorio
dir_path = os.path.dirname(os.path.realpath(__file__))

# Configuración de estilo
style = ttk.Style()
style.configure('TFrame', background=colors['light_blue'])
style.configure("Custom.TButton",
                background=colors['dark_green'],
                foreground=colors['black'],
                borderwidth=0,
                relief="flat",
                padding=(10, 5)
                )

# Función para actualizar los números de línea


def update_line_numbers(event=None):
    line_number_content = ""
    num_lines = code_text.index('end - 1 line').split('.')[0]
    for i in range(1, int(num_lines) + 1):
        line_number_content += str(i) + '\n'
    line_numbers.config(state=tk.NORMAL)
    line_numbers.delete('1.0', tk.END)
    line_numbers.insert('1.0', line_number_content)
    line_numbers.config(state=tk.DISABLED)


def open_file(filename):
    # Usa rutas absolutas para abrir el archivo
    absolute_path = os.path.join(dir_path, filename)
    os.startfile(absolute_path)


def build_tree(dot, node, parser, parent=None):
    if isinstance(node, TerminalNode):
        dot.node(str(id(node)), node.getText())
    else:
        name = parser.ruleNames[node.getRuleIndex()]
        dot.node(str(id(node)), name)
    if parent is not None:
        dot.edge(str(id(parent)), str(id(node)))

    if hasattr(node, 'children'):
        for child in node.children:
            build_tree(dot, child, parser, node)


def show_tree():
    open_file('output/grafo.png')


def show_inheritance():
    open_file('output/symbol_table.png')


# Funciones para copiar, pegar y cortar
def copy_text():
    code_text.event_generate("<<Copy>>")


def paste_text():
    code_text.event_generate("<<Paste>>")


def cut_text():
    code_text.event_generate("<<Cut>>")


def analyze_code(code):
    input_stream = InputStream(code)
    lexer = YAPLLexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(MyErrorListener())

    stream = CommonTokenStream(lexer)
    parser = YAPLParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(MyErrorListener())

    tree = parser.program()

    dot = Digraph()
    build_tree(dot, tree, parser)
    dot.render(filename=os.path.join(dir_path, 'output',
               'grafo'), format='png', cleanup=True)

    semantic_analyzer = SemanticAnalyzer()
    semantic_analyzer.visit(tree)
    semantic_analyzer.symbol_table.displayTree()

    return semantic_analyzer.ErrorList


def open_file(filename):
    if platform.system() == 'Windows':
        os.startfile(filename)
    elif platform.system() == 'Darwin':  # macOS
        subprocess.call(["open", filename])
    elif platform.system() == 'Linux':
        subprocess.call(["xdg-open", filename])


def perform_analysis():
    code = code_text.get("1.0", tk.END)
    errors = analyze_code(code)

    error_text.delete("1.0", tk.END)
    code_text.tag_delete("highlight")  # Clear existing highlights

    for error in errors:
        line_number = error.get('line', 'Unknown')
        col_number = error.get('column', 'Unknown')
        sms = error.get('error_mesagge', 'Unknown')
        formatted_error = f"Error Semántico (Línea {line_number}, Columna {col_number}): {sms}\n"

        end_index = error_text.index(tk.END)
        error_text.insert(tk.END, formatted_error)

        start_index = f"{end_index.split('.')[0]}.{int(end_index.split('.')[1])}"
        end_index = error_text.index(tk.END)

        error_text.tag_add(
            "error", start_index, f"{end_index.split('.')[0]}.{int(end_index.split('.')[1])-1}")

        if line_number != 'Unknown':
            code_text.tag_add(
                "highlight", f"{line_number}.0", f"{line_number}.end")

    # Habilite los botones después del análisis
    #show_tree_button['state'] = tk.NORMAL
    #show_inheritance_button['state'] = tk.NORMAL


# Configuración del GUI principal
root = tk.Tk()
root.title("YAPL Analyzer GUI")
root.geometry("1000x600")
root.configure(bg=colors['light_blue'])

main_paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

frame_left = ttk.Frame(main_paned, style='TFrame')

# Área de texto para los números de línea
line_numbers = tk.Text(frame_left, width=4, padx=3, takefocus=0,
                       bd=0, bg='lightgrey', state=tk.DISABLED, wrap=tk.NONE)
line_numbers.pack(side=tk.LEFT, fill=tk.Y)

code_text = tk.Text(frame_left, wrap=tk.WORD, height=20,
                    width=50, bg=colors['medium_blue'], fg='white')
code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
code_text.tag_configure("highlight", background="yellow", foreground="black")

# Llamar a la función update_line_numbers cuando hay un cambio en code_text
code_text.bind('<KeyPress>', update_line_numbers)
code_text.bind('<KeyRelease>', update_line_numbers)
code_text.bind('<MouseWheel>', update_line_numbers)

frame_buttons = ttk.Frame(frame_left)
frame_buttons.pack(fill=tk.X, padx=10, pady=(0, 10))

analyze_button = ttk.Button(
    frame_buttons, text="Analyze", command=perform_analysis, style="Custom.TButton")
analyze_button.pack(side=tk.TOP, padx=5, pady=5)

copy_button = ttk.Button(frame_buttons, text="📋 Copiar",
                         command=copy_text, style="Custom.TButton")
copy_button.pack(side=tk.TOP, padx=5, pady=5)

paste_button = ttk.Button(frame_buttons, text="📌 Pegar",
                          command=paste_text, style="Custom.TButton")
paste_button.pack(side=tk.TOP, padx=5, pady=5)

cut_button = ttk.Button(frame_buttons, text="✂️ Cortar",
                        command=cut_text, style="Custom.TButton")
cut_button.pack(side=tk.TOP, padx=5, pady=5)


main_paned.add(frame_left, weight=1)

frame_right = ttk.Frame(main_paned, style='TFrame')
error_text = tk.Text(frame_right, wrap=tk.WORD, height=20,
                     width=50, bg='white', fg='red')
error_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
error_text.tag_configure("error", foreground="red")

main_paned.add(frame_right, weight=1)

# Llamada inicial a update_line_numbers para asegurarse de que se muestren los números de línea iniciales
update_line_numbers()

root.mainloop()

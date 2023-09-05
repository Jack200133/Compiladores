import re
import tkinter as tk
from tkinter import ttk
from antlr4 import InputStream, CommonTokenStream
from graphviz import Digraph
import platform
import subprocess
import os
from PIL import Image
from modules.ErrorListener import MyErrorListener
from modules.Semantic import SemanticAnalyzer
from yapl.YAPLLexer import YAPLLexer
from yapl.YAPLParser import YAPLParser
from antlr4.tree.Tree import TerminalNode
print(os.listdir('.'))
semantic_analyzer = None  # Declarar como variable global

# Colores
colors = {
    'light_blue': '#8EA4D2',
    'medium_blue': '#6279B8',
    'dark_blue': '#49516F',
    'dark_green': '#496F5D',
    'light_green': '#4C9F70',
    'black': '#000000',
    'dark_background': '#1E1E1E',
    'dark_text': '#D4D4D4',
    'dark_selection': '#264F78',
    'dark_cursor': '#89CFF0',
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


def abrir_imagen_ruta(ruta):
    try:
        imagen = Image.open(ruta)
        imagen.show()
    except Exception as e:
        print("Error al abrir la imagen:", e)


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
    carpeta_output = os.path.join(os.path.dirname(__file__), 'output')
    ruta_imagen = os.path.join(carpeta_output, 'grafo.png')
    abrir_imagen_ruta(ruta_imagen)


def show_inheritance():
    open_file('output/symbol_table.png')


# Funciones para copiar, pegar y cortar
def copy_text():
    code_text.event_generate("<<Copy>>")


def paste_text():
    code_text.event_generate("<<Paste>>")


def cut_text():
    code_text.event_generate("<<Cut>>")


# Función para procesar comandos
def process_command(entry, error_text):
    command = entry.get()
    if command:
        # Tu lógica para manejar comandos aquí
        error_text.insert(tk.END, f"Ejecutando comando: {command}\n")
    entry.delete(0, tk.END)


def analyze_code(code):
    global semantic_analyzer  # Usar la variable global
    input_stream = InputStream(code)
    lexer = YAPLLexer(input_stream)
    # Remove the default error listener and add the custom one
    lexer.removeErrorListeners()
    lexer_listener = MyErrorListener()
    lexer.addErrorListener(lexer_listener)

    stream = CommonTokenStream(lexer)
    parser = YAPLParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(lexer_listener)

    tree = parser.program()

    dot = Digraph()
    build_tree(dot, tree, parser)
    dot.render(filename=os.path.join(dir_path, 'output',
               'grafo'), format='png', cleanup=True)

    semantic_analyzer = SemanticAnalyzer()
    semantic_analyzer.visit(tree)
    semantic_analyzer.symbol_table.displayTree()

    return semantic_analyzer.ErrorList,lexer_listener.ErrorList


def show_symbol_table():
    # Crear una ventana emergente para la tabla de símbolos
    new_window = tk.Toplevel()
    new_window.title("Tabla de Símbolos")
    symbol_text = tk.Text(new_window, wrap=tk.WORD, height=20,
                          width=50, bg='white', fg='black')
    symbol_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Ya que 'semantic_analyzer' es una variable global, podemos acceder a ella aquí
    symbols = semantic_analyzer.symbol_table.get_all_symbols()
    symbol_text.insert(tk.END, "Tabla de Símbolos:\n")
    for symbol in symbols:
        symbol_text.insert(tk.END, f"{symbol}\n")


def open_file(filename):
    if platform.system() == 'Windows':
        os.startfile(filename)
    elif platform.system() == 'Darwin':  # macOS
        subprocess.call(["open", filename])
    elif platform.system() == 'Linux':
        subprocess.call(["xdg-open", filename])


def highlight_cool_syntax(event):
    code_text.tag_remove("keyword", "1.0", tk.END)
    code_text.tag_remove("comment", "1.0", tk.END)

    code = code_text.get("1.0", tk.END)
    keyword_pattern = r"\b(class|else|fi|if|in|inherits|isvoid|let|loop|pool|then|while|case|esac|new|of|not)\b"
    comment_pattern = r"--[^\n]*"
    type_pattern = r"\b(Int|Bool|String)\b"

    for match in re.finditer(keyword_pattern, code):
        start, end = match.span()
        start_line = code.count("\n", 0, start) + 1
        start_col = start - code.rfind("\n", 0, start) - 1
        end_line = code.count("\n", 0, end) + 1
        end_col = end - code.rfind("\n", 0, end) - 1

        # Para diagnóstico
        print(f"For keyword, start_col={start_col}, end_col={end_col}")

        code_text.tag_add(
            "keyword", f"{start_line}.{start_col}", f"{end_line}.{end_col}")

    for match in re.finditer(type_pattern, code):
        start, end = match.span()
        start_line = code.count("\n", 0, start) + 1
        start_col = start - code.rfind("\n", 0, start) - 1
        end_line = code.count("\n", 0, end) + 1
        end_col = end - code.rfind("\n", 0, end) - 1
        code_text.tag_add(
            "type", f"{start_line}.{start_col}", f"{end_line}.{end_col}")

        # Para diagnóstico
        #print(f"For keyword, start_col={start_col}, end_col={end_col}")

        # code_text.tag_add(
        # "keyword", f"{start_line}.{start_col}", f"{end_line}.{end_col}")

    for match in re.finditer(comment_pattern, code):
        start, end = match.span()
        start_line = code.count("\n", 0, start) + 1
        start_col = start - code.rfind("\n", 0, start) - 1  # añadir + 1 aquí
        end_line = code.count("\n", 0, end) + 1
        end_col = end - code.rfind("\n", 0, end) + 1  # añadir + 1 aquí también
        code_text.tag_add(
            "comment", f"{start_line}.{start_col}", f"{end_line}.{end_col}")


def perform_analysis():
    show_tree_button['state'] = tk.DISABLED
    show_symbol_button['state'] = tk.DISABLED
    code = code_text.get("1.0", tk.END)
    errors,error_lexer = analyze_code(code)

    error_text.delete("1.0", tk.END)
    code_text.tag_delete("highlight")  # Clear existing highlights
    # Inicialmente asumimos que no hay error de "clase Main"
    main_class_error_present = False

    for error in error_lexer:
        line_number = error.get('line', 'Unknown')
        col_number = error.get('column', 'Unknown')
        sms = error.get('full_error', 'Unknown')
        formatted_error = f"{sms}\n"

        end_index = error_text.index(tk.END)
        error_text.insert(tk.END, formatted_error)

        start_index = f"{end_index.split('.')[0]}.{int(end_index.split('.')[1])}"
        end_index = error_text.index(tk.END)

        error_text.tag_add(
            "error", start_index, f"{end_index.split('.')[0]}.{int(end_index.split('.')[1])-1}")

        if line_number != 'Unknown':
            code_text.tag_add(
                "highlight", f"{line_number}.0", f"{line_number}.end")

        # Verificar si el mensaje de error contiene la frase sobre la "clase Main"
        if "No se encontró la clase Main" in sms:
            main_class_error_present = True

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

        # Verificar si el mensaje de error contiene la frase sobre la "clase Main"
        if "No se encontró la clase Main" in sms:
            main_class_error_present = True

    if not main_class_error_present:
        show_tree_button['state'] = tk.NORMAL
        show_symbol_button['state'] = tk.NORMAL
    else:
        show_tree_button['state'] = tk.DISABLED
        show_symbol_button['state'] = tk.DISABLED


# Configurar el estilo
style = ttk.Style()
style.theme_use('clam')

style.configure("Custom.TButton",
                background="#007BFF",  # Color de fondo
                foreground="#FFFFFF",  # Color de texto
                font=("Arial", 12, "bold"),  # Fuente
                borderwidth=3,  # Ancho del borde
                relief="raised",  # Tipo de borde
                padding=(20, 10))  # Padding (horizontal, vertical)

# Aumentar el tamaño y añadir un borde verde a los botones 'Show Tree' y 'Show Symbol'
style.configure("LargeGreenBorder.TButton",
                background="#007BFF",
                foreground="#FFFFFF",
                font=("Arial", 16, "bold"),
                borderwidth=5,
                relief="raised",
                padding=(50, 20),
                bordercolor="green")

# Configuración del GUI principal
root = tk.Tk()
root.title("YAPL Analyzer GUI")
root.geometry("1000x600")
root.configure(bg=colors['dark_selection'])

main_paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

frame_left = ttk.Frame(main_paned, style='TFrame')

# Área de texto para los números de línea
line_numbers = tk.Text(frame_left, width=4, padx=3, takefocus=0,
                       bd=0, bg='lightgrey', state=tk.DISABLED, wrap=tk.NONE)
line_numbers.pack(side=tk.LEFT, fill=tk.Y)

code_text = tk.Text(frame_left, wrap=tk.WORD, height=20,
                    width=50, bg=colors['dark_background'], fg='white',insertbackground='red')
code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
code_text.tag_configure("highlight", background="yellow", foreground="black")

# Configuración para resaltado de sintaxis
code_text.tag_configure("keyword", foreground="orange", background=None)
code_text.tag_configure("comment", foreground="green", background=None)
code_text.tag_configure(
    "type", foreground=colors["medium_blue"], background=None)

# Llamar a la función update_line_numbers cuando hay un cambio en code_text
code_text.bind('<KeyPress>', update_line_numbers)
code_text.bind('<KeyRelease>', update_line_numbers)
code_text.bind('<MouseWheel>', update_line_numbers)

# Llamar a la función highlight_cool_syntax cuando hay un cambio en code_text
code_text.bind('<KeyPress>', highlight_cool_syntax)
code_text.bind('<KeyRelease>', highlight_cool_syntax)

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

# Creo un nuevo marco para los errores y los botones
frame_bottom = ttk.Frame(frame_right, style='TFrame')

error_text = tk.Text(frame_bottom, wrap=tk.WORD, height=20,
                     width=50, bg=colors['black'], fg='red')
error_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
error_text.tag_configure("error", foreground="red")

# Añado botones en la parte inferior
show_tree_button = ttk.Button(
    frame_bottom, text="Mostrar Árbol", command=show_tree, state=tk.DISABLED, style="LargeGreenBorder.TButton")
show_tree_button.pack(side=tk.LEFT, padx=5, pady=5)

show_symbol_button = ttk.Button(
    frame_bottom, text="Mostrar Tabla de Símbolos", command=show_symbol_table, state=tk.DISABLED, style="LargeGreenBorder.TButton")
show_symbol_button.pack(side=tk.RIGHT, padx=5, pady=5)

frame_bottom.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

main_paned.add(frame_right, weight=1)

# Llamada inicial a update_line_numbers para asegurarse de que se muestren los números de línea iniciales
update_line_numbers()

root.mainloop()

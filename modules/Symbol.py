from graphviz import Digraph


class Scope:
    def __init__(self, parent=None, number=0, name="global", type="Object"):
        self.number = number
        self.symbols = {}
        self.parent = parent
        self.children = []
        self.name = name
        self.type = type
        self.current_memory_position = 0

    def add_child(self, child):
        self.children.append(child)

    def add(self, symbol):
        symbol.memory_position = self.current_memory_position
        self.current_memory_position += symbol.memory_usage
        self.symbols[symbol.name] = symbol

    def new_usage(self, symbol, new_usage):
        
        self.symbols[symbol.name].memory_usage += new_usage
        self.current_memory_position += new_usage

    def lookup(self, name):
        return self.symbols.get(name, None)

    def lookup_scope(self, name):
        if self.name == name:
            return self

    def display(self):
        print(f"\nAlcance: {self.number} \t{self.name} \t{self.type}")
        for symbol in self.symbols.values():
            print(str(symbol))
        for child in self.children:
            child.display()

    def __str__(self):
        return ', '.join(str(symbol) for symbol in self.symbols.values())


class Symbol:
    def __init__(self, name, _type, definicion=None, derivation=None, scope=None, myscope: Scope = None, initial_value=None, is_heredado=False,memory_usage=16):
        self.name = name
        self.type = _type
        self.definicion = definicion
        self.derivation = derivation
        self.scope = scope
        self.myscope = myscope
        self.value = initial_value
        self.is_heredado = is_heredado
        if self.type == "Int":
            self.memory_usage = 8
        elif self.type == "String":
            self.memory_usage = 16
        elif self.type == "Bool":
            self.memory_usage = 1
        else:
            self.memory_usage = memory_usage
        self.memory_position = 0

    def __str__(self):
        initial_value = None
        if self.type == "Int":
            initial_value = "0"
        elif self.type == "String":
            initial_value = '""'
        elif self.type == "Bool":
            initial_value = "False"
        elif self.type == "Object":
            initial_value = 'void'
        else:
            initial_value = "void"
        
        
        return f"{self.name:15}{self.type:15}{self.definicion:15}{self.derivation:30}{initial_value:10}{self.is_heredado:14}{self.myscope.number:10}{self.memory_position:15}{self.memory_usage:10}"

        base_str = f"{self.name}\t\t{self.type}\t\t\t{self.definicion}\t\t\t{self.derivation}\t\t\t{initial_value}\t\t\t{self.is_heredado}\t\t\t{self.myscope.number}\t\t\t{self.memory_position}\t\t\t{self.memory_usage}"
        if len(self.name) < 8:
            base_str = f"{self.name}\t\t\t{self.type}\t\t\t{self.definicion}\t\t\t{self.derivation}\t\t\t{initial_value}\t\t\t{self.is_heredado}\t\t\t{self.myscope.number}\t\t\t{self.memory_position}\t\t\t{self.memory_usage}"

        return base_str


class SymboTable:
    def __init__(self):
        self.root = Scope()
        self.current_scope = self.root
        self.scope_counter = 0
        # self.current_memory_position = 0

    def open_scope(self, name, type):
        self.scope_counter += 1
        new_scope = Scope(parent=self.current_scope,
                          number=self.scope_counter, name=name, type=type)
        self.current_scope.add_child(new_scope)
        self.current_scope = new_scope
        #self.current_memory_position = 0

    def close_scope(self):
        self.current_scope = self.current_scope.parent

    def add(self, symbol:Symbol):
        self.current_scope.add(symbol)
        #symbol.memory_position = self.current_memory_position
        #self.current_memory_position += symbol.memory_usage

    def lookup(self, name):
        scope = self.current_scope
        while scope:
            symbol = scope.lookup(name)
            if symbol:
                return symbol
            scope = scope.parent
        return None

    def lookup_scope(self, name):
        scope = self.current_scope
        while scope:
            symbol = scope.lookup_scope(name)
            if symbol:
                return scope

            if scope and scope.name == 'global':
                for child in scope.children:
                    if child.name == name:
                        return child
            scope = scope.parent
        return None

    def replace(self, symbol: Symbol, scope: Scope = None):
        scope_to_replace = scope if scope else self.current_scope
        if symbol.name in scope_to_replace.symbols:
            scope_to_replace.symbols[symbol.name] = symbol
        else:
            raise Exception(f"Símbolo '{symbol.name}' no encontrado. No se puede reemplazar.")

    def delete(self, name: str, scope: Scope = None):
        scope_to_delete = scope if scope else self.current_scope
        if name in scope_to_delete.symbols:
            del scope_to_delete.symbols[name]
        else:
            raise Exception(f"Símbolo '{name}' no encontrado. No se puede eliminar.")

    def update_value(self, name: str, new_value):
        symbol = self.lookup(name)
        if symbol:
            symbol.value = new_value
        else:
            raise Exception(f"Símbolo '{name}' no encontrado. No se puede actualizar el valor.")

    def new_usage(self, symbol: str, new_usage):
        symbol = self.lookup(symbol)
        if symbol:
            symbol.myscope.new_usage(symbol, new_usage)
        else:
            raise Exception(f"Símbolo '{symbol}' no encontrado. No se puede actualizar el valor.")

    def display(self):
        print("Tabla de Símbolos:")
        print(f"{'Nombre':15}{'Tipo':15}{'Definición':15}{'Derivación':20}{'Valor Inicial':15}{'Heredado':10}{'Alcance':10}{'Pos Memoria':15}{'Uso Memoria':10}")
        self.root.display()

    def copyTree(self, scope):
        if not scope:
            return None

        new_scope = Scope(parent=scope.parent, number=scope.number,
                          name=scope.name, type=scope.type)
        for symbol in scope.symbols.values():
            new_scope.add(symbol)

        for child in scope.children:
            new_scope.add_child(self.copyTree(child))

        return new_scope

    def displayTree(self):
        dot = Digraph(comment="SYMBOL TABLE")
        self._buildGraph(dot, self.root)
        dot.render(filename='./output/symbol_table', format='png',
                   cleanup=True)  # Guarda como imagen PNG

    def _buildGraph(self, dot, node):
        if not node:
            return

        dot.node(f'{node.number}',
                 f'Scope: {node.number}\n{node.name}\n{node.type}')

        for child in node.children:
            dot.edge(f'{node.number}', f'{child.number}')
            self._buildGraph(dot, child)

        # for scope, symbols in self.table.items():
        #     print(f"\nAlcance: {scope}")
        #     for symbol in symbols:
        #         print(str(symbol))

    def get_all_symbols(self):
        symbols = []

        def collect_symbols(scope):
            for symbol in scope.symbols.values():
                symbols.append(symbol)
            for child in scope.children:
                collect_symbols(child)

        collect_symbols(self.root)
        return symbols

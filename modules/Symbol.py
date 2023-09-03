from graphviz import Digraph


class Scope:
    def __init__(self, parent=None, number=0, name="global", type="Object"):
        self.number = number
        self.symbols = {}
        self.parent = parent
        self.children = []
        self.name = name
        self.type = type

    def add_child(self, child):
        self.children.append(child)

    def add(self, symbol):
        self.symbols[symbol.name] = symbol

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
    def __init__(self, name, _type, definicion=None, derivation=None, scope=None, myscope: Scope = None, initial_value=None, is_heredado=False):
        self.name = name
        self.type = _type
        self.definicion = definicion
        self.derivation = derivation
        self.scope = scope
        self.myscope = myscope
        self.initial_value = initial_value
        self.is_heredado = is_heredado

    def __str__(self):
        base_str = f"{self.name}\t{self.type}\t{self.definicion}\t{self.derivation}\t{self.initial_value}"
        if len(self.name) < 8:
            return base_str + "\t"
        else:
            return base_str


class SymboTable:
    def __init__(self):
        self.root = Scope()
        self.current_scope = self.root
        self.scope_counter = 0

    def open_scope(self, name, type):
        self.scope_counter += 1
        new_scope = Scope(parent=self.current_scope,
                          number=self.scope_counter, name=name, type=type)
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
            self.table[scope_to_delete] = [
                symbol for symbol in self.table[scope_to_delete] if symbol.name != name]

    def display(self):
        print("Tabla de Símbolos:")
        print("Nombre\t\tTipo\tdefinicion\tderivation")
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

from modules.Symbol import Symbol

class TypeSystem:
    def __init__(self):
        self.table = {}
        self.basic_types = ['Int', 'Bool', 'String']
        self.special_types = ['IO', 'Object']
        
        for t in self.basic_types:
            self.table[t] = ["Object"]
        
        self.table['IO'] = []  # Puedes añadir aquí los métodos predefinidos de IO
        self.table['Object'] = []  # Clase base para todos los objetos
        
    def add_type(self, ctx,type_name, parent_type=None):
        if type_name in self.special_types:
            print(f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}: No se puede definir el tipo {type_name} porque es un tipo especial. ")

            return True

        if type_name in self.basic_types:
            print(f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}: No se puede definir el tipo {type_name} porque es un tipo básico.")
            return True
        if type_name in self.table:
            print(f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}: El tipo {type_name} ya existe.")
            return True

        if parent_type:
            if parent_type in self.basic_types:
                print(f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}: No se puede heredar de un tipo básico. ({parent_type})")
                return True

            if parent_type not in self.table:
                print(f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}: El tipo '{parent_type}' no existe. No se puede heredar de un tipo inexistente.")
                return True
        else:
            parent_type = 'Object'  # Si no se especifica un tipo padre, se hereda de Object

        self.table[type_name] = [parent_type]
        return True
    
    def check(self, type1, type2):
        if type1 in self.table[type2]:
            return True
        return False

    def checkNumeric(self, type1, type2):
        acepted = ["Int","Object"]
        if type1 in acepted and type2 in acepted:
            return True
        return False

    def checkAssigment(self, id_type, expr_type):
        if expr_type == id_type:
            return True

        if self.is_inherited_from(expr_type, id_type):
            return True
        
        return False
    
    def comperIF(self, type1, type2):
        if type1 == type2:
            return type1
        else:
            return "Object"
    
    def checkNOT(self, type1):
        if type1 == "Bool" or type1 == "Object":
            return True
        return False
    

    def CheckComp(self, type1, type2):
        if type1 == type2:
            return True, "Bool"
        if type1 == "Object" or type2 == "Object":
            return True, "Object"
        return False, "Object"

    def is_inherited_from(self, child_type, parent_type):
        if child_type is None or parent_type is None:
            return False
        if child_type in self.table and parent_type in self.table[child_type]:
            return True
        
        looktype = self.table[child_type]
        while looktype:
            if parent_type in looktype:
                return True
            looktype = self.table[looktype[0]]
            if looktype == []:
                return False

        for inherited_type in self.table.get(parent_type, []):
            if self.is_inherited_from(child_type, inherited_type):
                return True
        
        return False
    
    def checkMethodSignature(self, method_A:Symbol, method_B:Symbol,params_A, params_B,ctx):
        # Verifica que los métodos A y B tengan la misma firma
        firma = True
        if self.is_inherited_from(method_A.type, method_B.type) == False and method_A.type != method_B.type:
            print(f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. El tipo de retorno del método {method_A.derivation} no coincide con el tipo de retorno del método {method_B.derivation}")
            firma= False
        if len(params_A) != len(params_B):
            print(f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. El número de parámetros del método {method_A.name} no coincide con el número de parámetros del método {method_B.name}")
            firma= False
        for i in range(len(params_A)):
            if params_A[i] != params_B[i]:
                print(f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. El tipo del parámetro {params_A[i]} del método {method_A.name} no coincide con el tipo del parámetro {params_B[i]} del método {method_B.name}")
                firma= False
        return firma

    def __str__(self):
        return str(self.table)

class TypeSystem:
    def __init__(self):
        self.table = {}
        self.basic_types = ['Int', 'Bool', 'String']
        self.special_types = ['IO', 'Object']
        
        for t in self.basic_types:
            self.table[t] = ["Object"]
        
        self.table['IO'] = []  # Puedes añadir aquí los métodos predefinidos de IO
        self.table['Object'] = []  # Clase base para todos los objetos
        
    def add_type(self, type_name, parent_type=None):
        if type_name in self.table:
            print(f"Error semántico: El tipo {type_name} ya existe.")
            return False

        if parent_type:
            if parent_type in self.basic_types:
                print(f"Error semántico: No se puede heredar de un tipo básico.")
                return False

            if parent_type not in self.table:
                print(f"Error semántico: el tipo '{parent_type}' no existe. No se puede heredar de un tipo inexistente.")
                return False
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
    
    def checkMethodSignature(self, method_A, method_B):
        # Asumiendo que los métodos son diccionarios con claves "return_type" y "arg_types"
        # Verifica que los métodos A y B tengan la misma firma
        if method_A['return_type'] != method_B['return_type']:
            return False
        if method_A['arg_types'] != method_B['arg_types']:
            return False
        return True

    def __str__(self):
        return str(self.table)

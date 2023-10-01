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
        
    def add_type(self, type_name, parent_type,ctx,adError):
        if type_name in self.special_types:
            sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}: No se puede definir el tipo {type_name} porque es un tipo especial. "
            #print(sms)
            adError(f"No se puede definir el tipo {type_name} porque es un tipo especial.",ctx.start.line,ctx.start.column,sms)

            return True
        elif type_name == parent_type:
            sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}: No se puede heredar de sí mismo ni herencia recursiva."
            #print(sms)
            adError(f"No se puede heredar de sí mismo ni herencia recursiva.",ctx.start.line,ctx.start.column,sms)
            return True

        elif type_name in self.basic_types:
            sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}: No se puede definir el tipo {type_name} porque es un tipo básico."
            #print(sms)
            adError(f"No se puede definir el tipo {type_name} porque es un tipo básico.",ctx.start.line,ctx.start.column,sms)
            return True
        
        elif type_name in self.table:
            sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}: El tipo {type_name} ya existe."
            #print(sms)
            adError(f"El tipo {type_name} ya existe.",ctx.start.line,ctx.start.column,sms)
            return True

        elif parent_type:
            if parent_type in self.basic_types:
                sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}: No se puede heredar de un tipo básico. ({parent_type})"
                #print(sms)
                adError(f"No se puede heredar de un tipo básico. ({parent_type})",ctx.start.line,ctx.start.column,sms)
                return True

            if parent_type not in self.table:
                sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}: El tipo '{parent_type}' no existe. No se puede heredar de un tipo inexistente."
                #print(sms)
                adError(f"El tipo '{parent_type}' no existe. No se puede heredar de un tipo inexistente.",ctx.start.line,ctx.start.column,sms)
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

    def checkAssigment(self, id_type, expr_type,ctx,adError):
        if expr_type == id_type:
            return True

        if self.is_inherited_from(expr_type, id_type,ctx,adError):
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
        elif (type1 == "Int" and type2 == "Bool") or (type1 == "Bool" and type2 == "Int"):
            return True, "Bool"
        elif type1 == "Object" or type2 == "Object":
            return True, "Object"
        return False, "Object"

    def is_inherited_from(self, child_type, parent_type,ctx,adError):
        if child_type == parent_type:
            return True
        if child_type is None or parent_type is None:
            return False
        if child_type in self.table and parent_type in self.table[child_type]:
            return True
        try:
            looktype = self.table[child_type]
        except KeyError:
            sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. El tipo {child_type} no esta definido."
            #print(sms)
            adError(f"El tipo {child_type} no esta definido.",ctx.start.line,ctx.start.column,sms)
            return False
        while looktype:
            if parent_type in looktype:
                return True
            looktype = self.table[looktype[0]]
            if looktype == []:
                return False

        for inherited_type in self.table.get(parent_type, []):
            if self.is_inherited_from(child_type, inherited_type,ctx,adError):
                return True
        
        return False
    
    def checkMethodSignature(self, method_A:Symbol, method_B:Symbol,params_A, params_B,ctx,adError):
        # Verifica que los métodos A y B tengan la misma firma
        firma = True
        herencia = self.is_inherited_from(method_A.type, method_B.type,ctx,adError)
        if self.is_inherited_from(method_A.type, method_B.type,ctx,adError) == False and method_A.type != method_B.type:
            sms = f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. El método ({method_A.name}, {method_A.type}) no está usando el retorno del método heredando ({method_B.name},{method_B.type})"
            #print(sms)
            adError(f"El método ({method_A.name}, {method_A.type}) no está usando el retorno del método heredando ({method_B.name},{method_B.type})",ctx.start.line,ctx.start.column,sms)
            firma= False
        if len(params_A) != len(params_B):
            sms =f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. El número de parámetros del método {method_A.name} no coincide con el número de parámetros del método {method_B.name}"
            #print(sms)
            adError(f"El número de parámetros del método {method_A.name} no coincide con el número de parámetros del método {method_B.name}",ctx.start.line,ctx.start.column,sms)
            firma= False
            return firma
        for i in range(len(params_A)):
            if params_A[i] != params_B[i]:
                sms =f"Error Semántico. En la línea {ctx.start.line}, columna {ctx.start.column}. El tipo del parámetro {params_A[i]} del método {method_A.name} no coincide con el tipo del parámetro {params_B[i]} del método {method_B.name}"
                #print(sms)
                adError(f"El tipo del parámetro {params_A[i]} del método {method_A.name} no coincide con el tipo del parámetro {params_B[i]} del método {method_B.name}",ctx.start.line,ctx.start.column,sms)
                firma= False
        return firma

    def __str__(self):
        return str(self.table)

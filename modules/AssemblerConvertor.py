# autor: Juan Angel Carrera
# Version: 1.0
# Descripcion: Genera la traduccion de un archivo codigo de 3 direcciones a assembler MIPS
# Ultima modificacion: 26/10/2023
from modules.Symbol import Symbol, SymboTable

class AssemblerConvertor:

    def __init__(self, code:str,symbol_table:SymboTable, file = "output/assembler.txt") -> None:
        self.__code = code.split('\n')
        self.output = file
        self.symbol_table = symbol_table
        self.use_temps = []
        self.use_stemps = []
        self.reserved = ['out_int', 'out_string', 'in_int', 'in_string', 'concat', 'substr', 'length']
        self.param_num = 0
        self.ass_temp = []
        self.v_table = {}
        self.main_isCalled = False
        self.main_isStarted = False

        # self.clean()
        self.convert()
    
    def getNextTemp(self):
        numbers_of_temps = []
        for temp in self.use_temps:
            numbers_of_temps.append(temp)
        
        conjunto = set(numbers_of_temps)

        # Empezamos buscando desde el 0 en adelante
        numero = 0
        while True:
            if numero not in conjunto:
                return numero
            numero += 1

    def getLastTemp(self):
        numbers_of_temps = []
        for temp in self.use_temps:
            numbers_of_temps.append(temp)
        
        conjunto = set(numbers_of_temps)

        # Empezamos buscando desde el 0 en adelante
        numero = 8
        while True:
            if numero not in conjunto:
                return numero
            numero -= 1

    def prepare_aritmetic(self, a:str, b:str):
        if a.startswith("t"):
            temp1 = a
        elif a.startswith("sp_GLOBAL"):
            sp_index = a.split("[")[1]
            sp_index = sp_index.split("]")[0]
            sp_index = int(sp_index) + 8
            temp1 = "s7"
            assm = f"\tlw ${temp1}, {sp_index}($s7)"
            self.write(assm)

        elif a.startswith("sp"):
            sp_index = a.split("[")[1]
            sp_index = sp_index.split("]")[0]
            sp_index = int(sp_index) + 4
            temp1 = "s1"
            assm = f"\tlw ${temp1}, {sp_index}($sp)"
            self.write(assm)
        else:
            temp1 = "s1"

            assmbler = f"\tli ${temp1}, {a}"
            self.write(assmbler)


        if b.startswith("t"):
            temp2 = b
        elif b.startswith("sp_GLOBAL"):
            sp_index = b.split("[")[1]
            sp_index = sp_index.split("]")[0]
            sp_index = int(sp_index) + 8
            temp2 = "s2"
            assm = f"\tlw ${temp2}, {sp_index}($s7)"
            self.write(assm)
            

        elif b.startswith("sp"):
            sp_index = b.split("[")[1]
            sp_index = sp_index.split("]")[0]
            sp_index = int(sp_index) + 4
            temp2 = "s2"
            assm = f"\tlw ${temp2}, {sp_index}($sp)"
            self.write(assm)
        else:
            temp2 = "s2"

            assmbler = f"\tli ${temp2}, {b}"
            self.write(assmbler)
        return temp1, temp2

    def convert(self):
        self.write_basic()
        self.write("# ======== CODIGO ========")
        for instruction in self.__code:
            instruction = instruction.strip()
            if instruction.startswith("t"):
                op = instruction.split("=")
                opcion = op[1].strip().split(" ")
                if opcion[0] == "PLUS":
                    restemp = op[0].strip()
                    self.use_stemps.append(int(restemp[1:]))
                    restemp = f"t{restemp[1:]}"
                    temp1, temp2 = self.prepare_aritmetic(opcion[1], opcion[2])
                    
                    assmbler = f"\tadd ${restemp}, ${temp1}, ${temp2}"
                    self.write(assmbler)
                    # Liberar temp2

                elif opcion[0] == "MINUS":
                    restemp = op[0].strip()
                    self.use_stemps.append(int(restemp[1:]))
                    restemp = f"t{restemp[1:]}"
                    temp1, temp2 = self.prepare_aritmetic(opcion[1], opcion[2])
                    
                    assmbler = f"\tsub ${restemp}, ${temp1}, ${temp2}"
                    self.write(assmbler)
                    # Liberar temp2

                elif opcion[0] == "MULT":
                    restemp = op[0].strip()
                    self.use_stemps.append(int(restemp[1:]))
                    restemp = f"t{restemp[1:]}"
                    temp1, temp2 = self.prepare_aritmetic(opcion[1], opcion[2])
                    
                    assmbler = f"\tmult ${temp1}, ${temp2}"
                    self.write(assmbler)

                    assmbler = f"\tmflo ${restemp}"
                    self.write(assmbler)
                    # Liberar temp2

                elif opcion[0] == "DIV":
                    restemp = op[0].strip()
                    self.use_stemps.append(int(restemp[1:]))
                    restemp = f"t{restemp[1:]}"
                    temp1, temp2 = self.prepare_aritmetic(opcion[1], opcion[2])
                    
                    assmbler = f"\tdiv ${temp1}, ${temp2}"
                    self.write(assmbler)

                    assmbler = f"\tmflo ${restemp}"
                    self.write(assmbler)
                    # Liberar temp2

                
                # TODO: CALL
                elif opcion[0] == "CALL":
                    param_num = opcion[2]
                    is_reserved = False
                    # REVISAR SI TIENE FUNCION RESERVADA
                    for res in self.reserved:
                        if res in opcion[1]:
                            self.call_reserved(opcion)
                                
                            is_reserved = True
                            break
                    if not is_reserved:
                        self.write(f"# ======== CALL {opcion[1]} ========")

                        self.write(f"\tlw $s2, 4($s1)")

                        # Buscar en v_table
                        calling = opcion[1].split(".")

                        if len(calling) == 2:
                            
                            function_name = calling[1]
                            class_name = calling[0]


                        index = self.v_table[class_name].index(opcion[1])

                        temp = self.getLastTemp()
                        self.use_temps.append(temp)

                        self.write(f"\tlw $t{temp}, {index}($s2)")
                        self.write(f"\tmove $a0, $s1")
                        
                        self.write(f"\tjal save_registers")
                        self.write(f"\tjal $t{temp}")
                        self.write(f"\tjal restore_registers")
                        restemp = op[0].strip()
                        self.write(f"\tmove ${restemp}, $v0")
                    self.param_num -= int(param_num)

            elif instruction.startswith("FUNCTION"):
                
                if self.main_isStarted and not self.main_isCalled:
                    self.write(f"\tjal Main.main")
                    self.main_isCalled = True

                tokens = instruction.split(" ")
                name = tokens[1]
                assmbler = f"\n{name}:"

                class_name = name.split(".")[0]
                self.v_table[class_name].append(name)

                self.write(assmbler)
                assmbler = f"\tmove $s1, $a0"
                self.reserva_memoria_func(tokens)
                
                self.write('\tsw $s7, 0($sp)')
                self.write('\tlw $s2, 0($sp)')
                self.write('\tmove $s1, $s2')
            
            elif instruction.startswith("sp"):
                tokens = instruction.split(" ")
                self.read_sp_param(tokens)


            elif instruction.startswith("PARAM"):
                tokens = instruction.split(" ")
                name = tokens[1]
                self.param_num += 1
                # Name sp || sp_GLOBAL || string || int || float
                if name.startswith("sp_GLOBAL") :
                    self.assign_spGlobal_param(tokens)
                elif name.startswith("sp"):
                    self.assign_sp_param(tokens)
                elif name.startswith('"'):

                    value = instruction.split('PARAM ')[1]
                    value = value[1:-1]
                    value = value.replace("\\n", "\n")
                    value = value.replace("\\t", "\t")
                    temp = self.reserva_cadena_en_heap(value)
                    self.write(f"\tmove $a{self.param_num}, $t{temp}")
                    self.use_temps.remove(temp)


            elif instruction.startswith("END FUNCTION"):
                if name == "Main":
                    self.main_isStarted = False
                tokens = instruction.split(" ")
                self.write(f"# ======== FIN FUNCION {tokens[2]} ========") # Restaurar el return address
                self.write(f"\tmove $sp, $fp") # Restaurar el stack pointer
                self.write(f"\tlw $ra, 4($sp)") # Restaurar el return address
                self.write(f"\tlw $fp, 0($sp)") # Restaurar el frame pointer
                self.write(f"\taddi $sp, $sp, 8") # Liberar el espacio del frame pointer y el return address

                if tokens[2] != "Main.main":
                    self.write(f"\tjr $ra")


            elif instruction.startswith("CLASS"):
                tokens = instruction.split(" ")
                name = tokens[1]
                assmbler = f"CLASS_{name}:\n"
                self.write(assmbler)

                if name == "Main":
                    self.main_isStarted = True

                self.v_table[name] = []

                self.reserva_memoria_class(tokens)

            elif instruction.startswith("ASSIGN"):
                tokens = instruction.split(" ")
                name = tokens[1]
                value = tokens[2]

                if name.startswith("sp_GLOBAL"):
                    self.assign_sp_global(tokens)
                elif name.startswith("sp"):
                    self.assing_sp(tokens)
                elif name.startswith('"'):
                    temp = self.reserva_cadena_en_heap(value[1:-1])

                    self.write(f"")

            elif instruction.startswith("RETURN"):
                tokens = instruction.split(" ")
                name = tokens[1]

                if name.startswith("sp_GLOBAL"):
                    self.write(f"#TODO ======== RETURN sp_GLOBAL[index] ========")
                    sp_index = name.split("[")[1]
                    sp_index = sp_index.split("]")[0]
                    sp_index = int(sp_index) + 8

                    self.write(f"\tlw $v0, {sp_index}($s7)")

                elif name.startswith("sp"):
                    self.write(f"# ======== RETURN sp[index] ========")
                    sp_index = name.split("[")[1]
                    sp_index = sp_index.split("]")[0]
                    sp_index = int(sp_index) + 4
                    
                    assm = f"\tlw $v0, {sp_index}($sp)"
                    self.write(assm)
                elif name.startswith("t"):
                    self.write(f"# ======== RETURN t ========")
                    
                    self.write(f"\tmove $v0, ${name}")



                # assmbler = f"\tli ${name}, {value}"
                # self.write(assmbler)

            # TODO: LIMPIAR MEMORIA
            # elif instruction.startswith("END CLASS"):

            #     tokens = instruction.split(" ")
            #     self.write(f"# ======== FIN MEMORIA CLASS {tokens[2]} ========") # Restaurar el return address

            #     self.write(f"\tlw $t0, 0($sp)")
            #     self.write(f"\taddi $sp, $sp, 4")


        self.end()

    def call_reserved(self, tokens):
        tipe = tokens[1]
        func_name = tokens[1].split(".")[1]
        if func_name == "out_string":
            self.write(f"# ======== CALL out_string ========")
            self.write(f"\tmove $a0, $a1")
            self.write(f"\tjal out_string\n")

            self.write(f"\tlw $s2, 0($sp)")
            self.write(f"\tmove $s1, $s2")
        elif func_name == "out_int":
            self.write(f"# ======== CALL out_int ========")
            self.write(f"\tmove $a0, $a1")
            self.write(f"\tjal out_int\n")

            self.write(f"\tlw $s2, 0($sp)")
            self.write(f"\tmove $s1, $s2")



    def assign_sp_param(self, tokens):
        self.write(f"# ======== PARAM = sp[index] ========")
        sp_index = tokens[1].split("sp[")[1]
        sp_index = int(sp_index[:-1]) + 4

        sp_param = self.param_num
        
        self.write(f"\tlw $a{sp_param}, {sp_index}($sp)\n")

    def assign_spGlobal_param(self, tokens):
        self.write(f"# ======== PARAM = sp_GLOBAL[index] ========")
        sp_index = tokens[1].split("sp_GLOBAL[")[1]
        sp_index = int(sp_index[:-1]) + 8
        
       
        self.write(f"\tlw $s1, 0($sp)")
        self.write(f"\tlw $a1, {sp_index}($s1)\n")

    def read_sp_param(self, tokens):
        self.write(f"# ======== sp[index] = PARAM_X ========")
        sp_index = tokens[0].split("sp[")[1]
        sp_index = int(sp_index[:-1]) + 4

        sp_param = tokens[2].split("PARAM_")[1]
        sp_param = int(sp_param) + 1

        
        self.write(f"\tsw $a{sp_param}, {sp_index}($sp)\n")

    def assign_sp_global(self, tokens):
        
        sp_index = tokens[1].split("sp_GLOBAL[")[1]
        sp_index = sp_index[:-1]
        sp_index = int(sp_index) + 8

        if tokens[2].startswith('"'):
            self.write(f"# ======== sp_GLOBAL[index] = value ========")
            value = tokens[2][1:-1]
            value = value.replace("\\n", "\n")
            value = value.replace("\\t", "\t")
            tvalue = len(value) +1 
            temp = self.reserva_bytes_en_heap(tvalue)
        
            self.alamcenar_cadena_en_heap(value, temp)
            

            self.write(f"\tsw $t{temp}, {sp_index}($s7)")
            self.use_temps.remove(temp)

        elif tokens[2].startswith("sp"):
            self.write(f"# ======== sp_GLOBAL[index] = sp[index] ========")
            sp_index = tokens[1].split("sp_GLOBAL[")[1]
            sp_index = sp_index[:-1]
            sp_index = int(sp_index) + 8

            sp_index2 = tokens[2].split("sp[")[1]
            sp_index2 = sp_index2[:-1]
            sp_index2 = int(sp_index2) + 4
            
            #TODO: REVISAR CON STEFANO
            self.write(f"\tlw $t0, {sp_index2}($sp)")
            self.write(f"\tsw $t0, {sp_index}($s7)")



        elif tokens[2].startswith("t"):
            self.write(f"# ======== sp_GLOBAL[index] = temp# ========")
            sp_index = tokens[1].split("sp_GLOBAL[")[1]
            sp_index = sp_index[:-1]
            sp_index = int(sp_index) + 8

            assm = f"\tsw ${tokens[2]}, {sp_index}($s7)"
            self.write(assm)

        elif tokens[2].startswith("NEW"):
            pass
        else:
            self.write(f"# ======== sp_GLOBAL[index] = value ========")
            temp = self.getLastTemp()
            self.use_temps.append(temp)

            self.write(f"\tli $t{temp}, {tokens[2]}")
            self.write(f"\tsw $t{temp}, {sp_index}($s7)")
            self.use_temps.remove(temp)

            #


        
    def assing_sp(self, tokens):
        
        sp_index = tokens[1].split("sp[")[1]
        sp_index = sp_index[:-1]
        sp_index = int(sp_index) + 4

        if tokens[2].startswith('"'):
            self.write(f"# ======== sp[index] = value ========")
            value = tokens[2][1:-1]
            value = value.replace("\\n", "\n")
            value = value.replace("\\t", "\t")
            tvalue = len(value) +1 
            temp = self.reserva_bytes_en_heap(tvalue)
        
            self.alamcenar_cadena_en_heap(value, temp)
            

            self.write(f"\tsw $t{temp}, {sp_index}($sp)")
            self.use_temps.remove(temp)

        elif tokens[2].startswith("sp"):
            sp_index = tokens[1].split("sp[")[1]
            sp_index = sp_index[:-1]
            sp_index = int(sp_index) + 4

            sp_index2 = tokens[2].split("sp[")[1]
            sp_index2 = sp_index2[:-1]
            sp_index2 = int(sp_index2) + 4

            #TODO: REVISAR CON STEFANO
            self.write(f"# ======== sp[index] = sp[index] ========")
            self.write(f"\tlw $t0, {sp_index2}($sp)")
            self.write(f"\tsw $t0, {sp_index}($sp)")

        elif tokens[2].startswith("t"):
            self.write(f"# ======== sp[index] = temp# ========")
            sp_index = tokens[1].split("sp[")[1]
            sp_index = sp_index[:-1]
            sp_index = int(sp_index) + 4

            assm = f"\tsw ${tokens[2]}, {sp_index}($sp)"
            self.write(assm)
            
        elif tokens[2].startswith("NEW"):
            pass
        else:
            self.write(f"# ======== sp[index] = value ========")
            temp = self.getLastTemp()
            self.use_temps.append(temp)

            self.write(f"\tli $t{temp}, {tokens[2]}")
            self.write(f"\tsw $t{temp}, {sp_index}($sp)")
            self.use_temps.remove(temp)
            


        

    def reserva_cadena_en_heap(self, cadena):

        name_len = len(cadena) + 1
        name_mem = self.reserva_bytes_en_heap(name_len)
        self.alamcenar_cadena_en_heap(cadena, name_mem)

        return name_mem

    def reserva_memoria_class(self, tokens):
        self.write(f"# ======== RESERVA DE MEMORIA para CLASS_{tokens[1]} ========")
        size = 0

        for index, token in enumerate(tokens):
            if token == 'SIZE':
                size = tokens[index + 1]
                break

        temp = self.getLastTemp()
        self.use_temps.append(temp)

        self.write(f"\tli $a0, {size}")
        self.write(f"\tli $v0, 9")
        self.write(f"\tsyscall")
        self.write(f"\tmove $t{temp}, $v0")

        name_len = len(tokens[1]) + 1
        name_mem = self.reserva_bytes_en_heap(name_len)
        self.alamcenar_cadena_en_heap(tokens[1], name_mem)

        self.write(f"\tsw $t{name_mem}, 0($t{temp})")
        self.write(f"\tla $t0 vt_{tokens[1]}")
        self.write(f"\tsw $t0, 4($t{temp})")
        self.write(f"\tmove $s7, $t{temp}")

        self.use_temps.remove(temp)
        self.use_temps.remove(name_mem)


    def reserva_bytes_en_heap(self, num_bytes):
        self.write(f"# ======== RESERVA DE {num_bytes} BYTES EN HEAP ========")

        temp = self.getLastTemp()
        self.use_temps.append(temp)

        self.write(f"\tli $t{temp}, {num_bytes}")
        self.write(f"\tmove $a0, $t{temp}")
        self.write(f"\tli $v0, 9")
        self.write(f"\tsyscall")
        self.write(f"\tmove $t{temp}, $v0")

        return temp

    def alamcenar_cadena_en_heap(self, cadena,mem_pos):
        self.write(f"# ======== ALMACENAR CADENA EN HEAP ========")

        temp = self.getLastTemp()
        self.use_temps.append(temp)

        for index, charac in enumerate(cadena):
            self.write(f"\tli $t{temp}, {self.string_to_ASCII(charac)}")
            self.write(f"\tsb $t{temp}, {index}($t{mem_pos})")
        
        self.write(f"\tsb $zero, {len(cadena)}($t{mem_pos})\n")

        self.use_temps.remove(temp)
    
    def string_to_ASCII(self, charac):
        return ord(charac)


    def reserva_memoria_func(self, tokens):
        self.write("\tmove $s1, $a0")
        self.write(f"# ======== INICIALIZAR DE MEMORIA FUNCION {tokens[1]} ========")
        size = 0

        for index, token in enumerate(tokens):
            if token == 'SIZE':
                size = int(tokens[index + 1]) + 4
                break

        self.write(f"\taddi $sp, $sp, -{8}") # mover el stack pointer para hacer espacio para el $fp y $ra
        self.write(f"\tsw $fp, 0($sp)") # guardar el frame pointer en el stack
        self.write(f"\tsw $ra, 4($sp)") # guardar el return addres en el stack

        # mover el fr\tame pointer y reservar espacio para las variables locales
        self.write(f"\tmove $fp, $sp") # Actualizar el frame pointer
        self.write(f"\taddi $sp, $sp, -{size}")# reservar espacio para las variables locales


    def write_basic(self):
        self.write("\nmain:")
        self.write("\tjal CLASS_Main")


        self.write("# ======== FUNCIONES BASICAS ========")
        self.write("out_int:")
        self.write("\tli $v0, 1")
        self.write("\tsyscall")
        self.write("\tjr $ra\n")

        self.write("out_string:")
        self.write("\tli $v0, 4")
        self.write("\tsyscall")
        self.write("\tjr $ra\n")

        self.write("in_int:")
        self.write("\tli $v0, 5")
        self.write("\tsyscall")
        self.write("\tjr $ra\n")

        self.write("in_string:")
        self.write("\tli $v0, 8")
        self.write("\tsyscall")
        self.write("\tjr $ra\n")

        self.write("save_registers:")
        self.write("\taddi $sp, $sp, -36")
        self.write("\tsw $t0, 0($sp)")
        self.write("\tsw $t1, 4($sp)")
        self.write("\tsw $t2, 8($sp)")
        self.write("\tsw $t3, 12($sp)")
        self.write("\tsw $t4, 16($sp)")
        self.write("\tsw $t5, 20($sp)")
        self.write("\tsw $t6, 24($sp)")
        self.write("\tsw $t7, 28($sp)")
        self.write("\tsw $t8, 32($sp)")
        self.write("\tsw $t9, 36($sp)")
        self.write("\tjr $ra\n")

        self.write("restore_registers:")
        self.write("\tlw $t0, 0($sp)")
        self.write("\tlw $t1, 4($sp)")
        self.write("\tlw $t2, 8($sp)")
        self.write("\tlw $t3, 12($sp)")
        self.write("\tlw $t4, 16($sp)")
        self.write("\tlw $t5, 20($sp)")
        self.write("\tlw $t6, 24($sp)")
        self.write("\tlw $t7, 28($sp)")
        self.write("\tlw $t8, 32($sp)")
        self.write("\tlw $t9, 36($sp)")
        self.write("\taddi $sp, $sp, 36")
        self.write("\tjr $ra\n")

        # TODO: STRINGS FUNCS
        # TODO concat
        # Ejemplo en ASS/concat

        # TODO substr
        # Ejemplo en ASS/substr

        # TODO length


    def write(self,triplet):
        # with open(self.output, 'a') as file:
        #     file.write(str(triplet) + '\n')
        self.ass_temp.append(str(triplet) + '\n')

    def clean(self):

        formated_V_table = ""

        for key in self.v_table:
            current_ = f"vt_{key}:\n"
            formated_V_table += current_
            for item in self.v_table[key]:
                word = f"\t.word {item}\n"
                formated_V_table += word


        init = f".data\n{formated_V_table}\n.text\n"
        with open(self.output, 'w') as file:
            file.write(init)

    def end(self):
        self.clean()

        end = "\n# ======== Salida del Programa ========\n\tli $v0, 10\n\tsyscall"
        self.write(end)

        complete_Ass = "".join(self.ass_temp)
        with open(self.output, 'a') as file:
            file.write(str(complete_Ass) + '\n')
        print('fin')

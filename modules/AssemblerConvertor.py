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
        self.current_tab = ""
        self.use_temps = []
        self.use_stemps = []

        self.clean()
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

    def prepare_aritmetic(self, a:str, b:str):
        if a.startswith("t"):
            temp1 = a
        else:
            temp1 = self.getNextTemp()
            self.use_temps.append(temp1)
            temp1 = f"t{temp1}"
            assmbler = f"{self.current_tab}li ${temp1}, {a}"
            self.write(assmbler)
        if b.startswith("t"):
            temp2 = b
        else:
            temp2 = self.getNextTemp()
            self.use_temps.append(temp2)
            temp2 = f"t{temp2}"
            assmbler = f"{self.current_tab}li ${temp2}, {b}"
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
                    restemp = f"s{restemp[1:]}"
                    temp1, temp2 = self.prepare_aritmetic(opcion[1], opcion[2])
                    
                    assmbler = f"{self.current_tab}add ${restemp}, ${temp1}, ${temp2}"
                    self.write(assmbler)
                    # Liberar temp2
                    self.use_temps.remove(int(temp1[1:]))  # Free temp1
                    self.use_temps.remove(int(temp2[1:]))  # Free temp2
                elif opcion[0] == "MINUS":
                    restemp = op[0].strip()
                    self.use_stemps.append(int(restemp[1:]))
                    restemp = f"s{restemp[1:]}"
                    temp1, temp2 = self.prepare_aritmetic(opcion[1], opcion[2])
                    
                    assmbler = f"{self.current_tab}sub ${restemp}, ${temp1}, ${temp2}"
                    self.write(assmbler)
                    # Liberar temp2
                    self.use_temps.remove(int(temp1[1:]))  # Free temp1
                    self.use_temps.remove(int(temp2[1:]))  # Free temp2
                elif opcion[0] == "MULT":
                    restemp = op[0].strip()
                    self.use_stemps.append(int(restemp[1:]))
                    restemp = f"s{restemp[1:]}"
                    temp1, temp2 = self.prepare_aritmetic(opcion[1], opcion[2])
                    
                    assmbler = f"{self.current_tab}mult ${temp1}, ${temp2}"
                    self.write(assmbler)

                    assmbler = f"{self.current_tab}mflo ${restemp}"
                    self.write(assmbler)
                    # Liberar temp2
                    self.use_temps.remove(int(temp1[1:]))  # Free temp1
                    self.use_temps.remove(int(temp2[1:]))  # Free temp2
                elif opcion[0] == "DIV":
                    restemp = op[0].strip()
                    self.use_stemps.append(int(restemp[1:]))
                    restemp = f"s{restemp[1:]}"
                    temp1, temp2 = self.prepare_aritmetic(opcion[1], opcion[2])
                    
                    assmbler = f"{self.current_tab}div ${temp1}, ${temp2}"
                    self.write(assmbler)

                    assmbler = f"{self.current_tab}mflo ${restemp}"
                    self.write(assmbler)
                    # Liberar temp2
                    self.use_temps.remove(int(temp1[1:]))  # Free temp1
                    self.use_temps.remove(int(temp2[1:]))  # Free temp2
                
                # TODO: CALL
                elif opcion[0] == "CALL":
                    pass

            elif instruction.startswith("FUNCTION"):
                tokens = instruction.split(" ")
                name = tokens[1]
                assmbler = f"\n{name}:"
                self.write(assmbler)
                self.current_tab += "\t"
                assmbler = f"\tmove $s1, $a0"
                self.reserva_memoria_func(tokens)

            # TODO: LIMPIAR MEMORIA
            elif instruction.startswith("END FUNCTION"):
                self.current_tab = self.current_tab[:-1]

            elif instruction.startswith("CLASS"):
                tokens = instruction.split(" ")
                name = tokens[1]
                assmbler = f"CLASS_{name}\n"
                self.write(assmbler)
                self.current_tab += "\t"
                self.reserva_memoria_class(tokens)

            elif instruction.startswith("ASSIGN"):
                tokens = instruction.split(" ")
                name = tokens[1]
                value = tokens[2]
                assmbler = f"{self.current_tab}li ${name}, {value}"
                self.write(assmbler)

            # TODO: LIMPIAR MEMORIA
            elif instruction.startswith("END CLASS"):
                self.current_tab = self.current_tab[:-1]

        self.end()

    def reserva_memoria_class(self, tokens):
        self.write(f"# ======== RESERVA DE MEMORIA para ClASS_{tokens[1]} ========")
        size = 0

        for index, token in enumerate(tokens):
            if token == 'SIZE':
                size = tokens[index + 1]
                break

        self.write(f"\tli $a0, {size}")
        self.write(f"\tli $v0, 9")
        self.write(f"\tsyscall")
        self.write(f"\tmove $t0, $v0")
        self.write(f"\tsw $t0, CLASS_{tokens[1]}")
        

    def reserva_memoria_func(self, tokens):
        self.write(f"# ======== INICIALIZAR DE MEMORIA FUNCION {tokens[1]} ========")
        size = 0

        for index, token in enumerate(tokens):
            if token == 'SIZE':
                size = tokens[index + 1]
                break

        self.write(f"addi $sp, $sp, -{8}") # mover el stack pointer para hacer espacio para el $fp y $ra
        self.write(f"sw $fp, 0($sp)") # guardar el frame pointer en el stack
        self.write(f"sw $ra, 4($sp)") # guardar el return addres en el stack

        # mover el frame pointer y reservar espacio para las variables locales
        self.write(f"move $fp, $sp") # Actualizar el frame pointer
        self.write(f"addi $sp, $sp, -{size}")# reservar espacio para las variables locales
        



        

    def write_basic(self):
        self.write("jal CLASS_Main")


        self.write("# ======== FUNCIONES BASICAS ========")
        self.write("out_int:")
        self.write("\tli $v0, 1")
        self.write("\tsyscall")
        self.write("\tjr $ra")

        self.write("out_string:")
        self.write("\tli $v0, 4")
        self.write("\tsyscall")
        self.write("\tjr $ra")

        self.write("in_int:")
        self.write("\tli $v0, 5")
        self.write("\tsyscall")
        self.write("\tjr $ra")

        self.write("in_string:")
        self.write("\tli $v0, 8")
        self.write("\tsyscall")
        self.write("\tjr $ra")

        # TODO: STRINGS FUNCS
        # TODO concat
        # Ejemplo en ASS/concat

        # TODO substr
        # Ejemplo en ASS/substr

        # TODO length


    def write(self,triplet):
        with open(self.output, 'a') as file:
            file.write(str(triplet) + '\n')

    def clean(self):
        init = ".data\n.text\n"
        with open(self.output, 'w') as file:
            file.write(init)

    def end(self):
        end = "\n#Salida del Programa\n\tli $v0, 10\n\tsyscall"
        self.write(end)


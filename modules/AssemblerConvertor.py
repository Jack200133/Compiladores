# autor: Juan Angel Carrera
# Version: 1.0
# Descripcion: Genera la traduccion de un archivo codigo de 3 direcciones a assembler MIPS
# Ultima modificacion: 26/10/2023

class AssemblerConvertor:

    def __init__(self, code, file = "output/assembler.txt") -> None:
        self.__code = code.split('\n')
        self.output = file

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

    def prepare_aritmetic(self, a, b):
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



            elif instruction.startswith("FUNCTION"):
                name = instruction.split(".")[1]
                assmbler = f"{self.current_tab}{name}:"
                self.write(assmbler)
                self.current_tab += "\t"

            elif instruction.startswith("END FUNCTION"):
                self.current_tab = self.current_tab[:-1]

        self.end()

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


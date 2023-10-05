import re
import heapq
from collections import deque
# La funcion tiene que ir bsucando linea por linea si se uso algun temporal t# y
#  si se uso revisar que en las siguientes líneas no fuera utilizado otra vez 
# esa misma temporal y si no era utilizado otra vez, entonces podía volver 
# a usar la misma temporal


def write(triplet):
    not_tab = ["CLASS","FUNCTION","RETURN","END"]
    # Si no empieza con ninguna de las palabras de arriba se le agrera un tab
    if not any(x in triplet for x in not_tab):
        if triplet.startswith("LABEL_L"):
            triplet = triplet
        else:
            triplet = "\t" + triplet
    with open('./output/3D/tripletasR.txt', 'a') as file:
        file.write(str(triplet) + '\n')

def recycle_temporals(code):
    lines = code.strip().split("\n")
    
    # Get lifespan of each temporary
    lifespan = {}
    for idx, line in enumerate(lines):
        matches = re.findall(r't\d+', line)
        for token in matches:
            if token not in lifespan:
                lifespan[token] = [idx, idx]
            else:
                lifespan[token][1] = idx

    recycled = {}
    recyclable_temps = set()
    max_temp = 0
    new_instructions = []

    for idx, line in enumerate(lines):
        matches = re.findall(r't\d+', line)

        # Find the maximum temp for creating new temps later
        for match in matches:
            temp_num = int(match[1:])
            max_temp = max(max_temp, temp_num)

        tokens = line.split()
        for token_idx, token in enumerate(tokens):
            if token.startswith('t') and token in matches:
                # If the temporary has ended its lifespan
                if lifespan[token][1] <= idx and token not in recyclable_temps:
                    recyclable_temps.add(token)
                
                # If token can be recycled
                if token not in recycled and recyclable_temps:
                    recycled_token = min(recyclable_temps, key=lambda x: int(x[1:]))
                    recycled[token] = recycled_token
                    tokens[token_idx] = recycled_token
                    recyclable_temps.remove(recycled_token)
                elif token not in recycled:
                    max_temp += 1
                    recycled_token = f"t{max_temp}"
                    recycled[token] = recycled_token
                    tokens[token_idx] = recycled_token

        new_instructions.append(' '.join(tokens))
        write(' '.join(tokens))

    return '\n'.join(new_instructions)
treedirectionsInfoPath = "./output/3D/tripletas.txt"
treedirectionsInfo = ""

with open(treedirectionsInfoPath, 'r') as file:
    treedirectionsInfo = file.read()
with open('./output/3D/tripletasR.txt', 'w') as file:
    pass
result = recycle_temporals(treedirectionsInfo)


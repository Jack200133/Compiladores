import re
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
    # Split the code into lines
    lines = code.strip().split("\n")
    number_used_temps = 0

    # Get lifespan of each temporary
    lifespan = {}

    for idx, line in enumerate(lines):
        tokens = line.split()
        for token in tokens:
            if token.startswith('t'):
                if token not in lifespan:
                    lifespan[token] = [idx, idx]
                else:
                    lifespan[token][1] = idx
    
    # Recycle temporaries
    recycled = {}
    free_temps = []
    new_instructions = []
    active_temps = []
    max_temp = -1

    for idx, line in enumerate(lines):
        tokens = line.split()
        # Substitute temporaries based on recycled mapping
        for token_idx, token in enumerate(tokens):
            if token.startswith('t'):
                max_temp = max(max_temp, int(token[1:]))  # track the highest temp
                if token in recycled:
                    tokens[token_idx] = recycled[token]
                elif free_temps and token not in active_temps:
                    recycled_token = free_temps[0]
                    free_temps = free_temps[1:]  # remove the first element
                    recycled[token] = recycled_token
                    tokens[token_idx] = recycled_token
                    active_temps.append(recycled_token)
                    #free_temps.add(token)
                else:
                    recycled[token] = "t" + str(number_used_temps + max_temp)
                    tokens[token_idx] = "t" + str(number_used_temps + max_temp)
                    number_used_temps += 1
  
                    #free_temps.add(token)
        # Check for temporaries that are not used anymore and add to free_temps
        for temp, (start, end) in lifespan.items():
            if idx >= end and temp not in free_temps and temp not in active_temps:
                free_temps.append(temp)
                free_temps.sort(key=lambda x: int(x[1:]))  # sort the list by temp number

            if idx == end and temp in recycled and recycled[temp] == temp:
                active_temps.remove(temp)
                free_temps.append(temp)
                free_temps.sort(key=lambda x: int(x[1:]))
            
        

        
        new_instructions.append(' '.join(tokens))
        write(' '.join(tokens))

    return '\n'.join(new_instructions)


treedirectionsInfoPath = "./output/3D/tripletas.txt"
treedirectionsInfo = ""

with open(treedirectionsInfoPath, 'r') as file:
    treedirectionsInfo = file.read()
result = recycle_temporals(treedirectionsInfo)
with open('./output/3D/tripletasR.txt', 'w') as file:
    file.write(result)

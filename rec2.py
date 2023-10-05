def recycle_temporaries(code):
    # Split the code into lines
    lines = code.strip().split("\n")
    
    # Function to get temporary number
    def get_temp_num(line):
        return int(line.split('t', 1)[1].split()[0])
    
    # The function processes a block of code
    def process_block(block):
        recycled = {}  # Map from old temp to new temp
        max_temp = -1  # Track the highest temp number in use
        
        for i, line in enumerate(block):
            # Check if a temp variable is being assigned to
            if line.strip().startswith('t'):
                temp_num = get_temp_num(line)
                
                # If this temp has been used before
                if temp_num in recycled:
                    new_temp = recycled[temp_num]
                else:
                    max_temp += 1
                    new_temp = max_temp
                    recycled[temp_num] = new_temp
                
                # Replace in current line
                block[i] = line.replace(f't{temp_num}', f't{new_temp}', 1)
            
            # Check for usage of temp in other parts of the line
            for temp_num in recycled:
                if f't{temp_num}' in line:
                    block[i] = block[i].replace(f't{temp_num}', f't{recycled[temp_num]}')
        
        return block
    
    # Find the start and end of each block and process it
    output_lines = []
    block_start = None
    
    for i, line in enumerate(lines):
        if line.strip().startswith("FUNCTION"):
            block_start = i
        elif line.strip().startswith("END FUNCTION"):
            block_end = i
            output_lines.extend(process_block(lines[block_start:block_end+1]))
            block_start = None
        elif block_start is None:
            output_lines.append(line)
    
    return "\n".join(output_lines)


treedirectionsInfoPath = "./output/3D/tripletas.txt"
treedirectionsInfo = ""

with open(treedirectionsInfoPath, 'r') as file:
    treedirectionsInfo = file.read()
result = recycle_temporaries(treedirectionsInfo)
with open('./output/3D/tripletasR.txt', 'w') as file:
    file.write(result)



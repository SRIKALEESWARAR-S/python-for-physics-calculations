def adventday1(start_pos: int):
    MOD = 100  # 0-99 cycle
    hits_exact = 0
    crosses_zero = 0
    
    with open("/home/srikaleeswarar/பதிவிறக்கங்கள்/advent202511.txt", "r") as f:
        for line in f:
            move = line.strip()
            if not move:
                continue
            
            # Parse: first L/R, rest as int
            dir_char = move[0]
            try:
                step = int(move[1:])
            except ValueError:
                continue
            
            if dir_char == 'R':
                step = +step
            else:  # 'L'
                step = -step
            
            # Crossings formula
            if step > 0:
                crosses_zero += (start_pos + step) // MOD
            elif step < 0:
                crosses_zero += (MOD - 1 - start_pos + (-step)) // MOD
            
            # Update position
            start_pos = (start_pos + step) % MOD
            
            # Exact hit
            if start_pos == 0:
                hits_exact += 1
    
    return hits_exact, crosses_zero

# Usage
print(adventday1(50))  # Starts at 50
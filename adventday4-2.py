import numpy as np
from scipy.ndimage import convolve

def load_grid(filename="/home/srikaleeswarar/adventday4input.txt"):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    max_len = max(len(line) for line in lines)
    lines = [line.ljust(max_len) for line in lines]
    return np.array([[c == '@' for c in line] for line in lines], dtype=bool)

def count_accessible(grid):
    kernel = np.ones((3,3), dtype=int)
    kernel[1,1] = 0
    neighbors = convolve(grid.astype(int), kernel, mode='constant')
    return grid & (neighbors < 4)

def solve():
    grid = load_grid()
    total_removed = 0
    
    while True:
        accessible = count_accessible(grid)
        count = accessible.sum()
        
        if count == 0:
            break
            
        total_removed += count
        grid[accessible] = False  # Remove accessible rolls
    
    print(f"Total rolls removed: {total_removed}")
    return total_removed

solve()

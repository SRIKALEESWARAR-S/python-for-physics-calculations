import numpy as np
from scipy.ndimage import convolve

# Read your input.txt file
with open("/home/srikaleeswarar/adventday4input.txt",'r',encoding = "utf-8-sig") as f:
    lines = [line.strip() for line in f.readlines()]
max_len = max(len(line) for line in lines)
lines = [line.ljust(max_len) for line in lines]  # Pad with spaces
# Convert to boolean grid (True = @)
grid = np.array([[c == '@' for c in line] for line in lines])

# Count 8 neighbors (exclude center)
kernel = np.ones((3,3), dtype=int)
kernel[1,1] = 0
neighbors = convolve(grid.astype(int), kernel, mode='constant')

# Count accessible rolls: @ with < 4 neighbors
accessible = grid & (neighbors < 4)
print(f"Accessible rolls: {accessible.sum()}")
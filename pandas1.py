import pandas as pd

# Read the two columns (whitespace or comma-separated)
df = pd.read_excel("/home/srikaleeswarar/பதிவிறக்கங்கள்/splited.ods", header=None, names=["left", "right"])

# Sort each column separately
left_sorted = df["part1"].sort_values(ignore_index=True)
right_sorted = df["part2"].sort_values(ignore_index=True)

# Compute absolute differences
differences = (left_sorted - right_sorted).abs()

# Compute total distance
total_distance = differences.sum()

print("Total distance:", total_distance)
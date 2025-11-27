left, right = [], []
with open("input.txt") as f:
    for line in f:
        a, b = map(int, line.split())
        left.append(a)
        right.append(b)

# Sort both lists
left_sorted = sorted(left)
right_sorted = sorted(right)

# Calculate sum of absolute differences
part1_answer = sum(abs(a - b) for a, b in zip(left_sorted, right_sorted))

print("Part 1 answer:", part1_answer)
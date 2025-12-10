def load_data(filename="/home/srikaleeswarar/adventday5input.txt",encoding = "utf-8-sig"):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    # First few lines are ranges (format: "1-10" or "1,10")
    ranges = []
    i = 0
    while i < len(lines) and ('-' in lines[i] or ',' in lines[i]):
        line = lines[i].replace(',', '-')
        start, end = map(int, line.split('-'))
        ranges.append((start, end))
        i += 1
    
    # Rest are numbers
    numbers = [int(line) for line in lines[i:] if line.isdigit()]
    
    return ranges, numbers

def find_matches(ranges, numbers):
    matches = []
    for num in numbers:
        for start, end in ranges:
            if start <= num <= end:
                matches.append(num)
                break
    return matches

# Load and solve
ranges, numbers = load_data()
matches = find_matches(ranges, numbers)

print(f"Ranges: {len(ranges)}")
print(f"Numbers: {len(numbers)}")
print(f"Matches: {matches}")
print(f"Match count: {len(matches)}")
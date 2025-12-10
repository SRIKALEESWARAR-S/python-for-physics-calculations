def adventday5(ranges_file = "/home/srikaleeswarar/adventday5ranges.txt"):
    total = 0

    with open("/home/srikaleeswarar/adventday5ranges.txt", "r", encoding = "utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    start,end = map(int,line.split('-'))
                    total += end - start + 1
                except:
                    continue

    print(f"numbers in all ranges:{total}")
    return total
adventday5("/home/srikaleeswarar/adventday5ranges.txt")
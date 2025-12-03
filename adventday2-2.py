def find_half(num):
    s = str(num)
    n = len(s)
    for size in range(1, n // 2 + 1):
        if n % size == 0:
            chunk = s[:size]
            if chunk * (n // size) == s:
                return True

    return False

with open("/home/srikaleeswarar/பதிவிறக்கங்கள்/adventday2input.txt",encoding = "utf-8-sig") as f:
    ranges = f.read().split(",")
all_matches = []


for r in  ranges:
    r = r.strip()
    start,end = map(int, r.split("-"))
    for number in range (start,end+1):
        if  find_half(number):
            all_matches.append(number)
print("Matching numbers", all_matches)
print("password",sum(all_matches))
def find_half(n):
    s = str(n)
    if len(s)%2 != 0:
        return False
    half = len(s)//2
    return s[:half] == s[half:]

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
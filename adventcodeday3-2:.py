def final_advent3(number):
    s = str(number)  
    larger_find = s[:-11]
    # largest subsequence length
    k = 12

    # greedy select
    take = k
    result = []
    start = 0

    while take > 0:
        end = len(s) - take    # last valid index to search for this digit

        # largest digit in this window
        max_digit = max(s[start:end+1])

        # pick the first occurrence of this digit
        idx = s.index(max_digit, start, end+1)

        result.append(max_digit)
        start = idx + 1
        take -= 1

    # result is a list of characters → make int
    return int("".join(result))
total_sum = 0

with open("/home/srikaleeswarar/adventcodeday3input.txt",encoding="utf-8-sig") as f:
    for line in f:
       digits = line.strip()
       if not digits:
           continue
       value = final_advent3(digits)
       total_sum += value
print("Total sum",total_sum)      

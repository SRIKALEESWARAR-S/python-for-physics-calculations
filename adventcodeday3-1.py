def final_advent3(number):
    s = str(number)  
    fd = max(s)
    last = s[-1]
    first_digit = None
    second_digit = None
    if fd == last:
        s = sorted(s)
        first_digit = s[-2]
        second_digit = fd
        return int(first_digit+second_digit)
    else:
        fd = max(s) #fd means first digit and sd means second digit
        first_digit = fd
        position = s.index(fd)
        sd = s[position + 1:]
        second_digit = max(sd)
        return int(first_digit+second_digit)
total_sum = 0

with open("/home/srikaleeswarar/adventcodeday3input.txt",encoding="utf-8-sig") as f:
    for line in f:
       digits = line.strip()
       if not digits:
           continue
       value = final_advent3(digits)
       total_sum += value
print("Total sum",total_sum)      

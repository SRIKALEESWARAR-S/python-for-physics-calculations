def adventday1(a):
    password = 0
    count = 0
    MOD = 100  # for values 0..100

    with open("/home/srikaleeswarar/பதிவிறக்கங்கள்/advent202511.txt", "r",encoding="utf-8-sig") as f:
        for line in f:
            move = line.strip()
            if not move:
                continue
            print(repr(move))   # debug: see exact content

            d = move[0]         # 'L' or 'R'
            n = int(move[1:])   # number after it
            count += n//MOD
            if d == "L":
                a = (a - n) % MOD
            else:               # assume 'R'
                a = (a + n) % MOD

            if a == 0:
                password += 1
           
          

    return password,count,password+count
   


a = 50
print(adventday1(a))
print("Part 2 answer")
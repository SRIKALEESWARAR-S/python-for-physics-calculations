def advent5(input_file = "/home/srikaleeswarar/adventday5ranges.txt"):
   #Code by SRI KALEESWARAR S
   ranges = []

   #open and analyze the file
   with open ( "/home/srikaleeswarar/adventday5ranges.txt",encoding="utf-8-sig") as f:
      for line in f:
         if '-' in line:
            start,end = map(int,line.strip().split('-'))
            ranges.append([start,end])
   ranges.sort()
   merged = [ranges[0]]
   for r in ranges [1:]:
       if r[0] <= merged[-1][1]:
          merged[-1][1] = max(merged[-1][1],r[1])
       else:
          merged.append(r)
  #count the numbers values
   total = sum(end - start + 1 for start,end in merged)
   print(total)


advent5( "/home/srikaleeswarar/adventday5ranges.txt")
import pandas as pan
df = pan.read_excel("/home/srikaleeswarar/பதிவிறக்கங்கள்/splited.ods")
sum_column1 = df['Part1'].sum()
sum_column2 = df['Part2'].sum()
answer = abs(sum_column1-sum_column2)
print(answer)
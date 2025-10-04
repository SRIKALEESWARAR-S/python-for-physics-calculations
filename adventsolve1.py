import pandas as pan

df = pan.read_excel('splited.xlsx')
df_sorted = df.sort_values(by=["Part1", "Part2"], ascending=[True, True])
diffrence = (abs((df["Part1"])-df["Part2"])).sum()

print("diffrence",diffrence)
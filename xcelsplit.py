import pandas as pan

df = pan.read_excel("/home/srikaleeswarar/பதிவிறக்கங்கள்/advendcodeinput.xlsx",header=None)

df[['Part1','Part2']] = df[0].astype(str).str.split(expand=True)

df.to_excel("/home/srikaleeswarar/பதிவிறக்கங்கள்/splited.xlsx",index=False)
print(df.head(1000))
print(type(df.iloc[0,0]))


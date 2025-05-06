#welcome to this wonderful beginner friendly python. Here we gonna write python code to find the hartmann's formula using few initial readings
print("welcome to this wonderful piece programme for finding the hartmanns formula using inital six readings")
print('''Given wavelengths are
 violet = 4040,blue = 4400,green = 5461,yellow=5893,orange=6089,red=6290''')
LAMDA = [4040,4400,5461,5893,6089,6290]
inputs = []
for i in range(6):
   while True:
      try:
        values = float(input(f"enter the readings,{i+1} (that your measured in the scale):"))
        inputs.append(values)
        break
      except ValueError as ve:
          print("enter numerical values only",ve)
A = (LAMDA[1] - LAMDA[0])/(LAMDA[2] - LAMDA[1])
print("A is",A)
B = (inputs[1] - inputs[0])/(inputs[2] - inputs[1])
print("B is",B)


from math import sqrt
print("""welcome to this wonderful and very easy to
 learn calculator created by srikaleeswarar""")

print("""In this calculator you can easily do the
addition(1)
subtraction(2)
multiplication(3)
division(4)
power(5)
square root(6)
please select the opeartion whic is in the bracket""")

try: 
     op = int(input("select the operation that you want to proceed"))
     if op > 6 or op <= 0:
          print("enter a correct option ")
     if op < 7:
           a = float(input("enter the first value"))
     if op == 5:
           p = int(input("enter the power value"))
           print("the {p} power value of {a} is",p**a)
     if op == 6:
           print("square root of {a} is",sqrt(a))
     for op in range(1,4):
          b = float(input("enter the second value:"))
          if op == 1:
             print("sum of {a} + {b} is", a+b)
          if op == 2:
             print("the subtracted value of {a}-{b}:",a-b)
          if op == 3:
             print("the multiplied value of {a}x{b}:",a*b)
          if op == 4:
             print("the diveded value of {a} by {b}:",a//b)
     else:
             print("just a calculator")
 
except ValueError:
       print("enter numbers only")
except:
       print("sorry folks theres a error")
       
          


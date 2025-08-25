#this is a universal graph plotter using matplotlib
import matplotlib.pyplot as mlt
import numpy as np

class graph():
     def readings():
        while True:
          try:
        #defining arrays as x and y
             x = []
             y = []
        #getting input from user to haw many values are there for both axis
             value_count = int(input("how many values do you have now?kindly enter less than 20 "))
             if value_count < 21:
                for i in range(value_count):
                    x1 = float(input("x axis - enter your {i+1} value :"))  
                    x.append(x1)   
                    y1 = float(input("y axis - enter your {i+1} value:"))     
                    y.append(y1)
             else:
                print("enter values below 20")    
                continue
             break
          except ValueError as ve:


import matplotlib.pyplot as plt
import numpy as np
#this is a code to draw graph for values

print("welcome to the graph drawing code")
def graph():
  while True:
    try:
      readings = int(input("How many readings do you have?"))
      if readings > 10 or readings < 1:
       print("enter 1 to 10 readings")
       continue
    except ValueError:
       print("value error")
       continue


    x_axis = []
    y_axis = []
    title = input("enter the Title of the graph")
    x_name = input("enter the name of the x_axis")
    y_name = input("enter the name of the y_axis")
    for i in range(readings):
      while True:
        try:
          x_values = float(input(f"enter your {i+1} reading in {x_name}"))
          y_values = float(input(f"enter your {i+1} reading in {y_name}"))
          x_axis.append(x_values)
          y_axis.append(y_values)
          break
        except ValueError:
          print("value error")
    
    plt.title(title)
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    plt.plot(x_axis,y_axis,marker ='o')
    plt.grid(True)
    plt.show()
    continue 
graph()

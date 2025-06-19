#this is a piece of code written by srikaleeswarar to calculate the HIGH RESISTENCE USING LEAKAGE METHOD
import numpy as np
import math
import matplotlib.pyplot as plt
print("Well this is code to calculate the high resistence value using the leakage method")
try:
    #getting first part values
    def theta_f():
      while True:
         left_values1 = []
         right_values1 = []
         theta_zero = 0
         print("you have to enter the values of 0-zero")
        #to find how many values are there
         value_count = int(input("how many values to you have right now?"))
        #rejecting if they have lot of values
         if value_count > 10:
          print("you have a lot of values i think, better enter upto 10 values")
          break
        #main calculation part
         elif 0 < value_count <= 10:
          #declaring arrays 
          
          #getting values
           for i in range(value_count):
               lvalues = float(input(f"enter your{i+1} in {value_count} left side reading:"))
               left_values1.append(lvalues)
               rvalues = float(input(f"enter your{i+1} in {value_count} of right side reading:"))
               right_values1.append(rvalues)
               #finding mean
           a = np.array(left_values1)
           b = np.array(right_values1)
           mean = (a+b)/2
           print("the meaning of both readings:",mean)
           total_mean = np.mean(mean)
           theta_zero = total_mean
           print("the found out 0-Zero value is:",theta_zero)
         else:
            print("value count is very low")
            return theta_zero
            
    def log_value(theta_zero):
          while True:
            left_values2 = []
            right_values2 = []
            leak_time =[]
            log_values = []
            print("In this part youre going to calculate the ratio of log 0")
            #to find how many values are there
            value_count = int(input("how many values do you have right now?"))
            #rejecting if they have lot of values
            if value_count > 10:
                 print("you have a lot of values i think, better enter upto 10 values")
                 break
            #main calculation part
            elif 0 < value_count <= 10:
                #declaring arrays 
                
                
                 for i in range(value_count):
                    lvalues = float(input(f"enter your{i+1} in {value_count} left side reading:"))
                    left_values2.append(lvalues)
                    rvalues = float(input(f"enter your{i+1} in {value_count} right side reading:"))
                    right_values2.append(rvalues)
                    ltime = float(input(f"enter your{i+1} in {value_count} leakage time reading:"))
                    leak_time.append(ltime)
                 a = np.array(left_values2)
                 b = np.array(right_values2)
                 means = (a+b)/2
                 print("the meaning of both readings:",means)
                 ratios = theta_zero / means 
                 print("0zero by 0 ratio is",ratios)
                 log_values = 2.303 * np.log10(ratios)
                 print("2.303 log(O/0) is",log_values)  
                 return log_values.tolist(),leak_time
    def graph(leak_time,log_values):
           if len(leak_time) != len(log_values):
             print("theres a mismatch length")
             return
           x = np.array(leak_time)
           y = np.array(log_values)
           plt.title("leakage method graph")
           plt.xlabel("time")
           plt.ylabel("2.303 log(θ₀ / θ)")
           plt.plot(x,y)
           plt.grid(True)
           plt.show()
    def main():
           theta = theta_f()
           leak_time,log_vals = log_value(theta)
           graph(leak_time,log_vals)
           
    main()
except ValueError as ve:
        print("value error",ve)

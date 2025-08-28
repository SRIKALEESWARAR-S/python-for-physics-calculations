#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 26 16:34:32 2025

@author: srikaleeswarar
"""

#This is a code to calculate the percetage error formula
def percentage_error():
  while True:
   try:  
    print("welcome to the code calculate the percentage error")
    name = input("""For which thing,you're calculating the percentage error?
                 kindly enter here:""")
    true_value = float(input(f"enter the true value of {name}:"))
    measured_value = float(input(f"enter the measured value of {name}:"))
    if true_value <= 0:
        print("i think you have entered a wrong true value:")
        continue
    elif measured_value == true_value:
        print("congradulations! there's no percentage error !")
        continue
    elif measured_value <= 0:
        print("i think you made a mistake on the measured value")
        continue
    else:
        tv = true_value
        mv = measured_value
        percentage_error = abs((mv-tv)/tv)*100
        pe = percentage_error
        print(f"you have a percentage error of {pe}% in {name}")
        if pe > 50:
            print("well you have a higher error rate,this is not so great.")
        break
   except ValueError as ve:
       print("well you made a value error here,please retry",ve)
       continue
percentage_error()
        
                           
                       
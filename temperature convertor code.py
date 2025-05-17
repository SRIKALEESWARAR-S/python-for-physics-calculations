#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 16 19:35:10 2025

@author: srikaleeswarar
"""

#this is code to convert the units of temperature
print("welcome to the temperature unit convertor program")
print('''press 1 for kelvin to celcius
         press 2 for celsius to kelvin
         press 3 for kelvin to faren heit
         press 4 for farenheit to kelvin
         press 5 for farenheit to celcius
         press 6 for celcius to farenheit''')
      
option = int(input("enter which conversion do you want to execute:"))
                     


try:
    def get_input(option):
        
           if option > 6 or option < 1:
            print("sorry wrong option ")
            return
           else:
               user_input = float(input("enter the value:"))
               return user_input
    def option1(user_input):
        celcius = user_input- 273.15
        print(f"celcius value is {celcius}:")
        return celcius
    def option2(user_input):
        kelvin = user_input + 273.15
        print(f"kelvin value is {kelvin}:")
        return kelvin
    def option3(user_input):
        faren =( user_input-273.15)*(9/5)+(32)
        print(f"farenheit value is{faren}:")
        return faren
    def option5(user_input):
        faren_tocel =(user_input - 32)*(5/9)
        print(f"the celcius value is{faren_tocel}:")
        return faren_tocel
    def option4(user_input):
        faren_kel = (user_input-32)*(5/9)+273.15
        print(f"the celcius value is{faren_kel}:")
        return faren_kel
    def option6(user_input):
        cel_faren = (user_input)*(9/5) + 32
        print(f"celcius value is{cel_faren}:")  
        return cel_faren
    def main(option):
        user_input = get_input(option)
        if option == 1:
            option1(user_input)
        elif option == 2:
            option2(user_input)
        elif option == 3:
            option3(user_input)           
        elif option == 4:
            option4(user_input)
        elif option == 5:
            option5(user_input)
        elif option == 6:
            option6(user_input)
           
    main(option)      
               
except ValueError as ve:
    print("value error",ve)
        
        
        
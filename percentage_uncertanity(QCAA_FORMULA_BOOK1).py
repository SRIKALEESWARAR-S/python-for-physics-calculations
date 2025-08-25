
"""
Created on Mon Aug 25 18:54:44 2025

@author: srikaleeswarar
"""
# This is a code to calculate the percentage uncertainity
def uncertanity():
    while True:
       try: 
          absolute_uncertanity = float(input("enter the value of absolute uncertanity:"))
          measurement = float(input("enter the value of measurement:"))
          au = absolute_uncertanity 
          mea = measurement
          if au <= 0:
              print("theres no uncertanity here")
              continue
          elif mea <= 0:
              
              print("i think there's a issue.measurement would not be have this value")
              continue
          else:
              percentage_uncertanity = (au/mea)*100
              pu = percentage_uncertanity
              print(f"The Percentage Uncertanity value is {pu}%")
              break
       except ValueError as ve:
           print("Theres a value error",ve)
           continue
uncertanity()
          
              
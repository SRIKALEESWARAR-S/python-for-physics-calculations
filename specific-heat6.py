#Welcome to this code to calculate the Q value in radiation
def heat_capacity():
    try:
      while True:
    
       print("welcome to the code to calculate the heat capacity of a system")
       mass = float(input("enter the mass of the system:"))
       if mass <= 0:
           print("kindly enter a correct mass")
           continue
       specific_heat = float(input("enter the specific heat capacity of the system:"))
       if specific_heat <= 0:
           print("specific heat value is wrong, kindly recheck")
           continue
       initial_temperature = float(input ("enter the initial temperature of the system in kelvins:"))
       if initial_temperature <= 0:
           print("wrong initial temperature value, kindly recheck")
           continue
       final_temperature = float(input("enter the final temperature of the system:"))
       if initial_temperature <= 0:
           print("wrong final temperature value, kindly recheck!")
           continue
       change_in_temperature = abs(initial_temperature - final_temperature)
       if change_in_temperature == 0:
           print("theres no change in temperature")
           break
       else:
           
          specific_heat = mass*specific_heat*change_in_temperature
          print(f" the specific heat is {specific_heat} ! ")
    except ValueError as ve:
        print("Theres a value error",ve)
heat_capacity()
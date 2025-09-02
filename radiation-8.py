#this is a code to calculate the change in energy interms of ionising radiation
def radiation():
  try:
     while True:
       print("Welcome to the code to calculate change in energy due to ionising adiation")
       initial_mass = float(input("enter the initial mass of the system in kg:"))
       c = 297000
       if initial_mass <= 0:
           print("enter a correct mass value, without mass nothing can be exist")
           continue
       final_mass = float(input("enter the final mass of the system after radiation:"))
       if initial_mass > final_mass:
           print("final mass could be gained, it should be less than the initial one")
           continue
       initial_energy = initial_mass * c**2
       final_energy = final_mass * c**2
       if initial_energy == final_energy:
           print(f"theres no decay, energy is same as {initial_energy} ")
       else:
           print(f"you have a initial energy {initial_energy} and final energy {final_energy}")
           lose = final_energy//initial_energy
           print(f"you have losed {lose} % of energy in  radiation")
           break
  except ValueError as ve:
      print("you have a value error, retry!",ve)
radiation()
      
           
                         
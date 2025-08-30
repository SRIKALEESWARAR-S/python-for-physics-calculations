# this is a code to find out how much of energy needed to change the state of a material at constant temperature
def heat_energy():
  while True:
   try:
      print('''This is a code to calculate the amount of energy needed to 
          change the state of a material at constant temperature''')
      latent_energy = float(input("enter the Latent Energy value you have:"))
      mass = float(input("enter the mass of the material:"))
      energy = latent_energy*mass
      if latent_energy <= 0:
           print("without latent energy, you cant do anything")
           continue
      elif mass <= 0:
          print("without mass theres nothing,even for photon it cant be negligeble")
          continue
      else:
          print(f"The energy required is {energy} joules")
          break
   except ValueError as ve:
       print("you have a value error, try again",ve)
       continue
heat_energy()
      
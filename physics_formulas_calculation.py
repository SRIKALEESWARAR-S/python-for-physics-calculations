#This a code to calculate various physics formulas
print('''welcome to the code for calculating various physics formulas''')
try:
    def select_option():
      print('''press 1 for ohms law
               press 2 for speed
               press 3 for e_power
               press 4 for accelaration
               press 5 for kinetic energy
               press 6 for depth
               press 7 for mass in earth
               press 8 for foce''')
      option = int(input("enter your option:"))
      if option > 8 or option < 1:
        print("wrong option")
        exit()
      else:
         return option

    def ohm_law():
       select_option = int(input(''' for find R press 1
                                     for find V press 2
                                     for find I press 3:'''))
       if select_option not in [1,2,3]:
          print("wrong option")
          exit()
       elif select_option == 1:
          v = float(input("enter the resistence value:"))
          i = float(input("enter the current value:"))
          print("resistence in ohms:",v/i) 
       elif select_option == 2:
          r = float(input("enter the resistence value:"))
          i = float(input("enter the current value:"))
          print("voltage is:",i*r)
       elif select_option == 3:
          r = float(input("enter the resistence value:"))
          v = float(input("enter the voltage:"))
          print("the current value in amps:",v/r)

     def e_power():
        select_option = int(input('''if you have V press 1
                                     if you have R press 2
                                     I is mandatory'''))
        if select_option not in [1,2]:
           print("wrong option")
           exit()
        elif select_option in [1,2]:
            i = float(input("enter current value:"))
            if select_option == 1:
               v = float(input("enter voltage:"))
               print("power is:",v*i)
            elif select_option == 2:
               r = float(input("enter the resistence in ohms:"))
               print("power is",(i**2)*r )
     def speed():
          distance = float(input("enter distance in meteres:"))
          time = float(input("enter time in seconds:"))
          if time <=0:
             print("I think youre than light")
          else:
             print("speed in m/s:",distance/time)
      

     def accelaration():
         f_v = float(input("enter the final velocity:"))
         i_v = float(input("enter the initial velocity:"))
         time = float(input("enter time in seconds:"))
         if time <= 0:
            print("I think thats pratically not possible")
         else:
            print("accelaration is:",(f_v-i_v)/time)
     def ke():
         mass = float(input("enter mass:"))
         velocity = float(input("enter velocity:"))
         if mass <= 0 or velocity <=0:
            print("I think its against physics")
         else:
            print("kinetic energy:",0.5*mass*(velocity**2) )
     def depth():
          time = float(input("enter time in seconds:"))
          if time <= 0:
             print("youre not throwing the rock")
          else:
             print("depth in meters:",time*9.8 )
     def mass_e():
          weight = float(input("enter your weight in kg:"))
          if weight <= 0 :
             print("ha ha nice joke, even light has some mass")
          else:
             print("your real mass is:",weight/9.8)
     def force():
          mass = float(input("enter mass:"))
          accelarqation = float(input("enter accelaration:"))
          if mass <= 0 or accelaration <= 0:
             print(" I think theres some problem")
          else:
             print("force",mass*accelaration)
     def main(option):
          
          if option == 1:
             ohm_law()
          elif option == 3:
             e_power()
          elif option == 2:
             speed()
          elif option == 4:
             accelaration()
          elif option == 5:
             ke()
          elif option == 6:
             depth()
          elif option == 7:
             mass_e()
          elif option == 8:
             force()
          print("நன்றி வணக்கம்! படைப்பு ஸ்ரீ காளீஸ்வரர் ")
     selection = select_option()
     main(selection)
except ValueError as ve:
      print("value error",ve)


               

     



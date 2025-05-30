#This is a python code written to explore various scale regions
print("welcome to the world of scales with examples")
try:
   def choice():
    while True:
     try:
      print('''in this code if you enter a value it'll show a
              similar real world think on that sscale range
              For Nano scale region press 1
              For micron scale region press 2
              For millimeter scale region press 3
              For centimeter scale region press 4
              For metre scale region press 5
              For KM scale region press 6
              For light seconds region press 7
              For light hours region press 8 
              For light years region press 9
              press 10 or any number to exit''')

 
       choice = int(input("Enter your choice:"))
       if choice not in range (1,10):
        print("you have selected a wrong option")
        exit()
       if choice in range (1,10):
         print(f"you had selected {choice} option")
         return choice
      except ValueError:
         print("value error")
   def nano():
      print("welcome to the Nano world")
      value = float( input("enter the nanometer value:"))
      if value < 0.1:
        print("things that are smaller than atoms. but theres a lot")
      elif 0.1 <= value < 0.5:
          print("things like gold atoms")
      elif 0.5 <= value < 5 :
          print("it may be a DNA")
      elif 5 <= value < 10 :
          print("it may be a protein")
      elif 10 <= value < 100 :
          print("it may be a virus like corona")
      elif 100 <= value < 1000 :
          print("there're tons of wavelength like green 541NM")
      elif value > 1000:
          print("better try micro world")

   def micro():
       print("welcome to the micro world")
       value =float(input("enter the micro meter value:"))
       if value < 0.5:
         print(" its smaller than bacterium,i think youre still try the best in nano world")
       elif 0.5 <= value < 5 :
         print("it may be a bacteria discovered after 1670s")
       elif value in range (5,10):
         print(" i think red blood cells in this range 6~8 microns")
       elif value in range (10,100):
         print("pollens found here")
       elif value in range(50,120):
         print("hey thats  a diameter human hair")
       elif value in range(100,200):
         print("also dust mites")
       elif value > 1000:
         print("better try switch millimeter range")

   def millimeter():
        print("Welcome to the millimeter ~ human eye world")
        value = float(input("enter your mm value:"))
        if value < 0.5:
          print("its smaller than the thickness of a normal paper!")
        elif 0.5 <= value < 1:
          print("pencil tip usually has this thickness")
        elif 1 <= value < 10:
          print("crayon,eraser and needle all are similar to this mm value")
        elif value >= 10:
          print("hey thats centimeter, better try with values less than 10")
   def centimeter():
        print("welcome to the normal and usual centimeter world")
        value = float(input("enter your centimeter value:"))
        if value < 1:
           print("hey better try the millimeter world!")
        elif 1 <= value < 2 :
           print("that's may be thickess of notepad or staple")
        elif 2 <= value < 3 :
           print("width of 5 CD's stake together")
        elif 3 <= value < 5 :
           print("it may be popsicle stick or a small stick(குச்சி)")
        elif 5 <= value < 10 :
          print("it may be a small plant(சின்ன செடி) ")
        elif 10 <= value < 20 :
          print("it may be a small book")
        elif 20 <= value <= 30 :
          print("standard ruler comes in the range of 30cm")
        elif 30 < value <= 100:
          print("it may be leg,hand of human or a table")
        elif value > 100:
          print("its higher than a meter")
   def meter():
         print("welcome to meter range")
         value = float(input("enter your meter value:"))
         if value < 1:
           print("hahh thats less than a meter dude")
         elif 1<= value < 3:
           print("well you can find humans at this range maybe")
         elif 3 <= value < 10:
           print("some cars or minitrucks can be found out")
         elif 10 <= value < 100:
          print("its less than hussain bolts race track")
         elif 100 <= value < 1000:
           print("in chennai city you can find store with in this range")
         elif value > 1000:
           print("well its kilometer scale")
   def kilo_meter():
         print("welcome to the kilometers range")
         value = float(input("enter your kilometer value:"))
         if value < 1:
            print("hey thats less than a kilometer")
         elif 1 <= value < 1000:
            print("youre still traveling inside india")
         elif 400 < value < 450:
            print("its the distance between the earth and ISS")
         elif 1000 <= value < 15000:
            print("This distance is usually in between the countries")
         elif 15000 <= value < 50000:
            drive = value/365
            print(f"if you drive {drive} kilometers per day for a year")
         elif 40000 < value < 50000:
            print("well the solar impulse 2 solar plane flown over 43,000kms")
         elif 50000 <= value < 384000:
            moon = 384000 - value
            print(f"your value is {moon} kilometers lower than the distance between earth and moon")
         elif value < 300000:
            print("you had reached into the world of light")
   def light_s():
             print("welcome to light seconds")
             value = float(input("enter your seconds:"))
             if value < 1:
               print("well its smaller than a second but light travells 1km within 0.3micro second")
             elif 1 <= value < 5:
               print("well had travelled to moon already,it take roughly 1.5seconds")
             elif 5 <= value < 500 :
               kilo = value*0.3
               print(f"well you had your flash light travelled {kilo}million kilometers already")
             elif 450 < value <= 500:
               print("I think youre very close to reach the sun")
             elif value > 500:
               km = value*0.0003
               print(f"well your flash has {km}billion kilometers from the earth")
   def light_h():
              print("welcome to the world of light hours")
              value = float(input("enter your hours of journey:"))
              kilo = (3600*value)*300000
              if value < 1:
                 print(f"well thats less than a hour,but you had still travlled {kilo} billion kilometers")
              elif value >= 1:
                 print(f"well its a very big calculation! you had travelled {kilo} billion kilometers")
              print("for know more about light.kindly read 'breif history of time'by stephen hawking")
   def light_y():
              print("welcome to light years")
              value = float(input("enter your hours of journey:"))
              kilo = 9.46*value
              if value < 1:
                 print(f"its less than a year but you had travelled {kilo} trillion kilo meters")
              elif value > 1:
                 print(f"you had travelled almost{kilo} trillion kilometers")
              elif value > 93000000000:
                 print("you had exceeded the diamter of universe! nothing apart this")
              print("well this is a very intersting topic will make another special code for light years")
   def main():
        while True:
             interest = choice()  
             if interest == 1:
               print("you have selected nano world")
               nano()
             elif interest == 2:
                print('you have selected micro world')
                micro()
             elif interest == 3:
                print("you have selected milli meter world")
                millimeter()
             elif interest == 4:
                print("you have selected centimeter world")
                centimeter()
             elif interest == 5:
                print("you have selected meter world,just meter")
                meter()
             elif interest == 6:
                print("you're travelling in kilo meter!")
                kilo_meter()
             elif interest == 7:
                print("you have selected light seconds ")
                light_s()
             elif interest == 8:
                print("you have selected light in hours")
                light_h()
             elif interest == 9:
                print("you have selected light years!")
                light_y()
             elif interest >= 10:
                print("thanks for using this code")
                break
             print("நன்றி வணக்கம்! படைப்பு ஸ்ரீ காளீஸ்வரர் ")

   main()
except ValueError as ve:
      print("value error",ve)
      
             
            
         
        

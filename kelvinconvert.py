#This a simple piece of code to convert the celcius value into the kelvin
def kelvin():
   while True:
       try:
           print("welcome to the code to convert celcius into kelvin")
           celcius = float(input("What is the celcius value? :"))
           ce = celcius
           kelvin = ce + 273
           if ce < -273:
               print(f"{ce} Celcius value couldnt be existed in physics")
               continue
           elif kelvin < 2:
               print("its below the made lowest temperature!")
               continue
           else:
               if kelvin > 5772:
                   print("its hotter than sun")
               print(f"The calculated kelvin value is {kelvin}K")
               break
       except ValueError as ve:
           print("you have a value error! kindly retry",ve)
kelvin()

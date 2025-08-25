# 0-100 units 0
#101-200 units 2.35
#201-400 units 4.70
#401-500 units 6.30
#501-600 units 8.40
#601-800 units 9.45
#801-1000 units 10.50
#Above 1000 units 11.55 

class ebtn:
    def value():
     while True:
        try:
            last_reading = int(input("enter last time eb reading in whole numbers:"))
            new_reading = int(input("enter this month eb reading in whole numbers:"))
            units = new_reading - last_reading
            if units < 0:
               print("i think you have entered a wrong reading")
               continue
            else:  
               print("total units that you have used in last two months:",units)
               break
            return units
     def 
	



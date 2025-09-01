#In this piece of code we will going to calculate the change in internal energy using first law of thermodynamics
def internal_energy():
    try:
        while True:
            print("welcome to the code to calculate the internal energy using first law of thermodynamics")
            added_heat = float(input("how much of heat added to the system:"))
            if added_heat <= 0:
                print("if no heat is added there would be any need for this formula")
                continue
            work_done = float(input("enter the value of workdone:"))
            if work_done <= 0:
                print("theres no work done, so no use to calculate")
                continue
            else:
                delta_u = added_heat + work_done
                print(f" The calculated change in internal energy value is {delta_u}")
                
                break
    except ValueError as ve:
        print("there may be a value error",ve)
internal_energy()
        
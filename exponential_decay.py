# In this piece of code we are going to calculate the exponential decay
def exponential_decay():
    print("welcome to this piece of code to calculate the exponential decay")
    try:
        while True:
            initial_quantity = float(input("enter the initial quantity of atoms present in the system:"))
            half_life = int(input("enter how many halfwaves happen during the decay:"))
            half_life = abs(half_life)
            final_quantity = initial_quantity * (0.5) **half_life
            if initial_quantity <= 0:
                print("i think you have entered a wrong initial value, kindly try again")
                break
            elif half_life == 0:
                print("thats not even possible, without a half life, theres nothing exist")
                continue
            else:
                print(f"The calculated value of the exponential decay is {final_quantity}")
                break
    except ValueError as ve:
         print("there may be a value error",ve)
exponential_decay()
            
                            
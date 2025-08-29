#This is a code calculate the energy efficiency
def energy_efficiency():
    while True:
        try:
            print("welcome to the code to calculate the energy efficiency")
            energy_name = input('''Enter the name of which energy 
                                you're going to calculate,namely kinectic,potential
                                enter your input : ''')
            if energy_name == "none":
                energy_name = ["kinetic"]            
            energy_input = float(input("Enter the energy input value in joules:"))
            energy_output = float(input("enter the energy output value in joules :"))
            energy_efficiency = (energy_output/energy_output)
            if energy_name == "none":
                print("we are taking it as kinetic energy")                
            if energy_input == 0:
                print("without any energy input that would not be any output")
            if energy_output == 0:
                print("you lost all the energy")
            
            else:
                print(f"you have the energy efficiency of {energy_name} is {energy_efficiency}%")
        except ValueError as ve:
             print("theres a value error",ve)
energy_efficiency()
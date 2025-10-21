#this is a code to calculate the youngs modulus

m1 = 250e-3
m2 = 200e-3
g = 9.8
a = 50e-2
wavelength = 5891e-10
slope1 = 12e4
slope2 = 10e4
b = 3.742e-2
d = 3.15e-2
q = (6*(m1-m2)*g*a)/(wavelength*(slope1-slope2)*b*d**3)
print(f"youngs modulus is {q} N/M^2")
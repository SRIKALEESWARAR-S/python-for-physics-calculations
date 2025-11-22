from sympy import symbols,solve

x = symbols('x')
equation = x**3 - 9
solutions = solve(equation,x)
print(f"the solution for the equatrion is {solutions}")

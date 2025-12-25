#protype  code for physics formulas
class classical_mechanics():
   
    def newton2law(self,mass,accelaration):
      self.mass = mass
      self.accelaration = accelaration
      if mass <= 0:
         print("check the mass value")
      return mass*accelaration
c = classical_mechanics()
print(c.newton2law(545,767))
print(c.newton2law(0,546))
print(c.newton2law(-456,767))
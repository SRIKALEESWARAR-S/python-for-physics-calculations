#formulas for physics formulas project
class thermodynamics():
  def kelvin( self,celsius = 1):
    self.celsius = celsius
    ''' this is code to calculate the kelvin value prototype'''
    if celsius <= -272:
      print("This value shouldnt be exist")
    return celsius + 273
t = thermodynamics()
print(t.kelvin(54))
print(t.kelvin(0))
print(t.kelvin(-52763))
print(t.kelvin(-131))
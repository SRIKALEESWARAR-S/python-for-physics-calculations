class electronics:
  """
    Electronics:
    This a module in the library to compute
    various Electronics. As already mentioned 
    we have added certain limitations for the
    output values to met with the realworld 
    Scenarios.
   """
   def __init__(self,voltage = 1,current = 1,resistance =1,inductance =1,
                 frequency =1,time =1,capacitance =1) -> None:
     self.v = voltage
     self.i = current
     self.r = resistance
     self.l = inductance
     self.f = frequency
     self.t = time
     self.c = capacitance

  def ohms_law(self) -> float:
    self.v = self.i * self.r
    if self.v > 25e6:
      raise ValueError("The value can't be above 25Million Volts in pratical")
    else:
      return self.v
    


                                                    
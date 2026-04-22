import math as m
@staticmethod
def keplers_thirdlaw(G,M,a):

    G = 6.674e-11
    T = m.sqrt(4*(3.14*3.14)*a**3 / G*M)

    return T,T*T
@staticmethod
def T_comparison(t1,t2,a1,a2):

    if t1**2/t2**2 == a1**3/a2**3:
        print("compared",t1**2/t2**2 == a1**3/a2**3)
    else:
        print("ratio is wrong")
    return t1**2/t2**2,a1**3/a2**3
@staticmethod
def orbital_eccentricity(c,a):
    e = c/a
    return e
@staticmethod
def semi_rectus_lactum(b,a):
    l = b**2/a
    return l
@staticmethod
def abc_relation(a,e):
    b_sqr = (a**2)*(1-e**2)
    return b_sqr
@staticmethod
def Perihelion_Distance(a,e):
    r_min = a(1-e)
    return r_min


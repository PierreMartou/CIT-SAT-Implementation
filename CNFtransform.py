from sympy import *

def test():
    x, y = symbols('x,y')
    print((y & x).subs({x: True, y: True}))
    array = [1, 2, 3]
    array = symbols("x1:"+str(len(array)+1))
    print(array)

test()
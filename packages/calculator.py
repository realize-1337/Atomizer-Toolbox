import math
import sympy as sp

class Calculator():
    def __init__(self, targetTemp, targetViscosity=0) -> None:
        self.c = sp.Symbol('c')
        self.a = sp.Symbol('a')
        self.T = targetTemp
        self.my = targetViscosity
        
    def createEq(self, a, b, alpha):
        eq = sp.Eq(alpha, 1-self.c+(a*b*self.c*(1-self.c))/(a*self.c+b*(1-self.c)))
        return eq

    def createViscosity(self, w, g):
        eq = sp.Eq(self.my, w**self.a*g**(1-self.a))
        return eq

    def calcMy_g(self):
        return 12100*math.exp((-1233+self.T)*self.T/(9900+70*self.T))

    def calcMy_w(self):
        return 1.790*math.exp((-1230-self.T)*self.T/(36100+360*self.T))
    
    def rhoGlycerin(self):
        return 1277-0.654*self.T
        
    def calcAB(self):
        a = 0.705 - 0.0017*self.T
        b = (4.9 + 0.036*self.T)*a**2.5
        return [a,b]
    
    def solve(self):
        eq_alpha = self.createViscosity(self.calcMy_w(), self.calcMy_g())
        alpha = sp.solve(eq_alpha, self.a)[0]
        eq = self.createEq(self.calcAB()[0], self.calcAB()[1], alpha)
        results = [x for x in sp.solve(eq, self.c) if x <=1 and x >= 0]
        return results[0]


if __name__ == '__main__':
    targetViscosity = float(input('Ziel-Viskosität in mPa s angeben: '))
    T = float(input('Aktuelle Umgebungtemperatur in °C angeben: '))

    print(f'Ziel-Viskosität {targetViscosity} mPa s bei {T} °C')
    
    calc = Calculator(T, targetViscosity)
    result = calc.solve()
    print(f'Bei {T} °C werden für eine Zielviskosität von {targetViscosity} mPa s {"%.2f" % (result*100)} wt-% Glycerin benötigt!')
    input('Bitte Enter zum beednden...')

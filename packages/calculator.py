import math
import sympy as sp

class Calculator():
    def __init__(self, targetTemp, targetViscosity=0) -> None:
        self.c = sp.Symbol('c')
        self.a = sp.Symbol('a')
        self.T = targetTemp
        self.my = targetViscosity
        

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
    
    def newcalcAB(self):
        a = 0.705 - 0.0017*self.T
        b = (4.9 + 0.036*self.T)*a**2.5
        return a,b
    
    def solve(self):
        a, b = self.calcAB()
        w = self.calcMy_w()
        g = self.calcMy_g()
        al = math.log(self.my/g, math.e)/math.log(w/g, math.e)
        result = (math.sqrt(a**2*(b-al+1)**2-2*a*b*al*(b+al-1)+b**2*al**2)+a*(b-al+1)+b*al-2*b) / (2*(a*b+a-b))
        if result <= 1 or result <= 0:
            return result
        else: return ValueError


if __name__ == '__main__':
    targetViscosity = float(input('Ziel-Viskosität in mPa s angeben: '))
    T = float(input('Aktuelle Umgebungtemperatur in °C angeben: '))

    print(f'Ziel-Viskosität {targetViscosity} mPa s bei {T} °C')
    
    calc = Calculator(T, targetViscosity)
    a, b = calc.newcalcAB()
    result = calc.newSolve(a, b, calc.calcMy_w(), calc.calcMy_g())
    print(f'Bei {T} °C werden für eine Zielviskosität von {targetViscosity} mPa s {"%.2f" % (result*100)} wt-% Glycerin benötigt!')
    input('Bitte Enter zum beednden...')

import math

class dimLess():
    def __init__(self, vel, rho, visc, Lc) -> None:
        self.vel = vel
        self.rho = rho
        self.visc = visc
        self.Lc = Lc


    def GLR(self, m1, m2):
        return m1/m2

    def Re(self):
        return self.vel*self.rho*self.Lc/self.visc

    def We_aero(self, v_rel, sigma):
        return v_rel**2*self.rho*self.Lc/sigma
        
    def We(self, sigma):
        return self.vel**2*self.rho*self.Lc/sigma

    def Ohnesorge(self, sigma):
        return self.visc/(math.sqrt(sigma*self.rho*self.Lc))

    def impuls(self):
        pass

if __name__ == '__main__':
    pass
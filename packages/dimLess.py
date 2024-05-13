import math

def Re(vel, rho, Lc, visc):
    '''
    Returns Reynolds Number
    '''
    return vel*rho*Lc/visc

def GLR(m1,m2):
    '''
    Returns Gas to Liquid Ratio
    '''
    return m1/m2

def We_aero(v_rel, rho, Lc, sigma):
    '''
    Returns Weber aero Number
    '''
    return v_rel**2*rho*Lc/sigma

def We(vel, rho, Lc, sigma):
    '''
    Returns Weber Number
    '''
    return vel**2*rho*Lc/sigma

def Oh(visc, rho, Lc, sigma):
    '''
    Returns Ohnesorge Number
    '''
    return visc/(math.sqrt(sigma*rho*Lc))

def impuls(rho, vel, a):
    '''
    Returns Impuls
    '''
    return (rho*vel**2*a)

def IR(rho1, vel1, a1, rho2, vel2, a2):
    '''
    Returns Impuls Ratio
    '''
    return (impuls(rho1, vel1, a1)/impuls(rho2, vel2, a2))

def We_GLR(rho, sigma, Lc, GLI, GLO, v_i, v_o):
    '''
    Returns GLR weighted Weber number
    '''
    return (rho*Lc/sigma*(GLI*v_i**2+GLO*v_o**2))
import math
import numpy as np

import coolpi.colour.colour_space_conversion as csc

# CCT 
# -------

# Correlated color temperature is defined by the CIE in terms of the CIE 1960 UCS chromaticity diagram 
# (uv chromaticity diagram)

# Ohta, N., and Robertson, A. 2005. Colorimetry: fundamentals and applications. John Wiley & Sons.
# https://www.wiley.com/en-us/Colorimetry%3A+Fundamentals+and+Applications-p-9780470094723


# Colour Space Conversion ---> Using CIE 1960 u,v chromaticity diagram

def XYZ_to_uv_1960(X, Y, Z):
    '''
    Function to transform CIE XYZ tristimulus values into CIE 1960 uv chromaticity coordinates

    Chapter 3. CIE Standar Colorimetric System
    Note 3.7. Simple methods for obtaining CCT. Eq. 3.74 (pp.110)
    
    Ohta, N., and Robertson, A. 2005. Colorimetry: fundamentals and applications. John Wiley & Sons.
    https://www.wiley.com/en-us/Colorimetry%3A+Fundamentals+and+Applications-p-9780470094723

    '''

    u = 4*X/(X + 15*Y + 3*Z)
    v = 6*Y/(X + 15*Y + 3*Z)
    return u, v

def uvY_1960_to_XYZ(u, v, Y):
    ''' 
    Function to compute the transformation between CIE 1960 uv and CIE XYZ colour spaces

    Solved using a linear equation system
        
    Parameters:
        u, v, Y        float    CIE 1976 u'v' coordinates
    
    Returns:
        X,Y,Z          float    CIE XYZ tristimulus values
        
    '''

    B = np.array([-15*u*Y, Y*(6-15*v)])
    A = np.array([[u-4, 3*u], [v, 3*v]])

    sol_equation = np.linalg.pinv(A).dot(B) if np.linalg.det(A)==0 else np.linalg.inv(A).dot(B)
        
    X = sol_equation[0]
    Z = sol_equation[1]

    return X, Y, Z


def xy_to_uv_1960(x,y):
    '''
    Funtion to transform CIE 1931 x,y chromaticity coordinates to CIE 1960 u,v chromaticity coordinates
    
    Ohta, N., & Robertson, A. 2005. Colorimetry: fundamentals and applications. John Wiley & Sons.
    Eq.4.1. (pp.119)
    https://www.wiley.com/en-us/Colorimetry%3A+Fundamentals+and+Applications-p-9780470094723

    '''

    u = 4*x/(12*y-2*x+3)
    v = 6*y/(12*y-2*x+3)
    return u,v

def uv_1960_to_xy(u,v):
    '''
    Funtion to transform CIE 1960 u,v chromaticity coordinates to CIE 1931 x,y chromaticity coordinates
    
    '''
    
    x = 3*u/(2*u-8*v+4)
    y = 2*v/(2*u-8*v+4)
    return x, y


# Delta_uv

def compute_Delta_uv(u,v):
    '''
    Function to compute Duv from uv coordinates

    Ohno, Yoshi. 2014. Practical Use and Calculation of CCT and Duv, LEUKOS, 10:1, 47-55, 
    doi: 10.1080/15502724.2014.839020

    Parameters:    
        u, v          float     u', v' coordinates
    Returns:       
        Delta_uv      float     Duv 

    '''

    k6, k5, k4, k3, k2, k1, k0 = -0.00616793, 0.0893944, -0.5179722, 1.5317403, -2.4243787, 1.925865, -0.471106
    
    L_FP = np.sqrt(math.pow((u-0.292),2) + math.pow((v-0.24), 2))
    a = np.arccos((u-0.292)/L_FP)
    L_BB = k6*math.pow(a, 6) + k5*math.pow(a, 5) + k4*math.pow(a, 4) + k3*math.pow(a, 3) + k2*math.pow(a, 2) + k1*a + k0 
    Delta_uv = L_FP - L_BB
    return Delta_uv 


# x,y chromaticity coordinates to CCT ----> McCammy, 1992; Hernandez-Andrés, 1999; Ohno (modified)

def xy_to_CCT_McCamy(x,y):
    ''' 
    Function to compute CCT (º K) from CIE 1931 x y chromaticity coordinates using the
    McCamy third order polynomial equation 
    
    McCamy, C.S. 1992. Correlated color temperature as an explicit function of chromaticity 
    coordinates,Color Res. Appl. 17, 142-144.
    https://onlinelibrary.wiley.com/doi/10.1002/col.5080170211
    
    McCamy, C.S. 1993. Correlated color temperature as an explicit function of chromaticity 
    coordinates (Erratum), Color Res. Appl. 18, 150.
    
    Parameters:    
        x,y           float     x,y chromaticity coordinates of illuminant
    Returns:       
        cct           float     CCT (º K)
    
    '''
    
    # CCT epicenter 
    xe = 0.3320
    ye = 0.1858
    n = (x-xe)/(y-ye)
    # McCamy equation
    cct = -449*(math.pow(n, 3)) + 3525*(math.pow(n, 2)) - 6823.3*n + 5520.33

    return cct

def apply_Hernandez_exponential_equation(x, y, recalculate=False):
    '''
    Function to apply the Hernandez-Andres exponential equation to compute the CCT from xy coordinates

    Hernandez-Andres, J., Lee, R. L., & Romero, J. 1999. Calculating correlated color temperatures 
    across the entire gamut of daylight and skylight chromaticities. Applied optics, 38(27), 5703-5709.
    https://opg.optica.org/ao/abstract.cfm?uri=ao-38-27-5703

    Parameters:    
        x,y           float     x,y chromaticity coordinates of illuminant
        recalculate   Bool      If False, the use the parameters for the assumption CCT <= 50.000ºK. 
                                If True, recalculate for CCT>50.000ºK.
                                Default, False
    Returns:       
        cct           float     computed CCT (º K)

    '''

    if recalculate:
        xe, ye, A0, A1, t1, A2, t2, A3, t3 = 0.3356, 0.1691, 36284.48953, 0.00228, 0.07861, 5.4535e-36, 0.01543, 0, 0
    else:
        xe, ye, A0, A1, t1, A2, t2, A3, t3 = 0.3366, 0.1735, -949.86315, 6253.80338, 0.92159, 28.70599, 0.20039, 0.00004, 0.07125

    n = (x-xe)/(y-ye)
    cct = A0 + A1*np.exp(-n/t1) + A2*np.exp(-n/t2) + A3*np.exp(-n/t3)
    return cct

def xy_to_CCT_Hernandez(x,y):
    ''' 
    Function to compute CCT (º K) from CIE 1931 x y chromaticity coordinates using the method
    proposed by Hernandez et.al. 
    
    Hernandez-Andres, J., Lee, R. L., & Romero, J. 1999. Calculating correlated color temperatures 
    across the entire gamut of daylight and skylight chromaticities. Applied optics, 38(27), 5703-5709.
    https://opg.optica.org/ao/abstract.cfm?uri=ao-38-27-5703

    Parameters:    
        x,y           float x,y chromaticity coordinates of illuminant
    Returns:       
        cct           float CCT (º K)
    
    ''' 
    
    # Assumption that CCT <= 50.000ºK    
    cct = apply_Hernandez_exponential_equation(x, y)   
    # Recalculate if CCT>50.000ºK
    cct = apply_Hernandez_exponential_equation(x, y, recalculate =True) if cct>50000 else cct

    return cct

# tested, but modified

def xy_to_CCT_Ohno(x, y):
    ''' 
    Function to compute CCT (º K) from CIE 1931 x y chromaticity coordinates using the method
    proposed by Ohno

    Ohno, Yoshi. 2014. Practical Use and Calculation of CCT and Duv, LEUKOS, 10:1, 47-55
    https://www.tandfonline.com/doi/abs/10.1080/15502724.2014.839020
    
    Parameters:    
        x, y          float     x,y chromaticity coordinates of illuminant
    Returns:       
        cct           float     CCT (º K)
    
    ''' 
    
    u, v = xy_to_uv_1960(x,y)
    
    L_FP = np.sqrt(math.pow((u-0.292),2) + math.pow((v-0.24), 2))
    a1 = np.arctan((v-0.24)/(u-0.292))
    a = a1 if a1>=0 else (a1 + np.pi)

    k06, k05, k04, k03, k02, k01, k00 = -3.7146e-3, 5.60614e-2, -3.307009e-1, 9.750013e-1, -1.5008606, 1.115559, -1.77348e-1
    k16, k15, k14, k13, k12, k11, k10 = -3.23255e-5, 3.570016e-4, -1.589747e-3, 3.6196568e-3, -4.3534788e-3, 2.1595434e-3, 5.308409e-4
    k26, k25, k24, k23, k22, k21, k20 = -2.6653835e-3, 4.17781315e-2, -2.73172022e-1, 9.53570888e-1, -1.873907584, 1.964980251, -8.58308927e-1
    k36, k35, k34, k33, k32, k31, k30 = -2.352495e+1, 2.7183365e+2, -1.1785121e+3, 2.51170136e+3, -2.7966888e+3, 1.49284136e+3, -2.3275027e+2
    k46, k45, k44, k43, k42, k41, k40 = -1.731364909e+6, 2.7482732935e+7, -1.81749963507e+8, 6.40976356945e+8, -1.27141290956e+9, 1.34488160614e+9, -5.926850606e+8
    k56, k55, k54, k53, k52, k51, k50 = -9.4353083e+2, 2.10468274e+4, -1.9500061e+5, 9.60532935e+5, -2.65299138e+6, 3.89561742e+6, -2.3758158e+6
    k66, k65, k64, k63, k62, k61, k60 = 5.0857956e+2, -1.321007e+4, 1.4101538e+5, -7.93406005e+5, 2.48526954e+6, -4.11436958E+6, 2.8151771E+6

    L_BB = k06*math.pow(a, 6) + k05*math.pow(a, 5) + k04*math.pow(a, 4) + k03*math.pow(a, 3) + k02*math.pow(a, 2) + k01*a + k00
    Delta_uv = L_FP - L_BB # correct
    
    if a<2.54:
        T1 = 1/(k16*math.pow(a, 6) + k15*math.pow(a, 5) + k14*math.pow(a, 4) + k13*math.pow(a, 3) + k12*math.pow(a, 2) + k11*a + k10)
        ATc1 = ((k36*math.pow(a, 6) + k35*math.pow(a, 5) + k34*math.pow(a, 4) + k33*math.pow(a, 3) + k32*math.pow(a, 2) + k31*a + k30)*(L_BB+0.01)/L_FP)*(Delta_uv/0.01) 
    
    elif a>=2.54:
        T1 = 1/(k26*math.pow(a, 6) + k25*math.pow(a, 5) + k24*math.pow(a, 4) + k23*math.pow(a, 3) + k22*math.pow(a, 2) + k21*a + k20)
        ATc1 = ((1/(k46*math.pow(a, 6) + k45*math.pow(a, 5) + k44*math.pow(a, 4) + k43*math.pow(a, 3) + k42*math.pow(a, 2) + k41*a + k40))*(L_BB+0.01)/L_FP)*(Delta_uv/0.01) 
    
    T2 = T1 - ATc1

    c = math.log(T2)

    # I have changed the formula where I think there is mistake. Inverse (1/)
    if Delta_uv>=0:
        #ATc2 = (k56*math.pow(c, 6) + k55*math.pow(c, 5) + k54*math.pow(c, 4) + k53*math.pow(c, 3) + k52*math.pow(c, 2) + k51*c + k50) # original
        ATc2 = 1/(k56*math.pow(c, 6) + k55*math.pow(c, 5) + k54*math.pow(c, 4) + k53*math.pow(c, 3) + k52*math.pow(c, 2) + k51*c + k50)
    elif Delta_uv<0:
        #ATc2 = (k66*math.pow(c, 6) + k65*math.pow(c, 5) + k64*math.pow(c, 4) + k63*math.pow(c, 3) + k62*math.pow(c, 2) + k61*c + k60)*math.pow((Delta_uv/0.03), 2) #original
        ATc2 = 1/(k66*math.pow(c, 6) + k65*math.pow(c, 5) + k64*math.pow(c, 4) + k63*math.pow(c, 3) + k62*math.pow(c, 2) + k61*c + k60)*math.pow(Delta_uv/0.03, 2)

    cct_K = T2 - ATc2

    return cct_K

# xy from CCT

# CIE --> [4000, 25000]

# tested
def compute_xy_from_CCT_CIE_D_illuminants(cct_K):
    '''
    Function to compute the x,y chromaticity coordinates using the CIE formulation

    For D illuminants from CCT into the range 4000<CCT<25000
    
    CIE015:2018. 4.1.2. Other D illuminants. (pp.12)
    eq. 4.7, 4.8, 4.9. For CCT from approximately 4000 ºK to 25000 ºK

    pp. 13. Note 6. For CCT: 5000, 5500, 6500 or 7500. 
    
    Parameters:    
        cct_K         float     CCT in ºK

    Returns:       
        x, y          float     x,y chromaticity coordinates

    '''

    try:
        cct_ini = int(cct_K)
    except:
        raise Exception("CCT not in valid units")    
    
    list_D_illuminants = [5000,5500,6500,7500] # D illuminants

    if cct_K in list_D_illuminants:
        ratio = 1.4388/1.4380
    else:
        ratio = 1.

    cct = cct_ini*ratio
    
    # Compute Chromaticity xD, yD
    if cct>4000 and cct<=7000:
        xD = -4.6070*math.pow(10,9)/math.pow(cct, 3) + 2.9678*math.pow(10,6)/math.pow(cct, 2) + 0.09911*math.pow(10,3)/cct + 0.244063

    elif cct>7000 and cct<25000:
        xD = -2.0064*math.pow(10,9)/math.pow(cct, 3) + 1.9018*math.pow(10,6)/math.pow(cct, 2) + 0.24748*math.pow(10,3)/cct + 0.237040

    else:
        raise Exception("CTT not in valid range 4000-25000 ºK. Please use the m coefficients interpolation function")

    yD = -3.000*math.pow(xD,2) + 2.870*xD - 0.275
    
    return xD, yD


# Kim cubic spline --> [1667, 25000]

# seems to be ok
def compute_xy_from_CCT_cubic_spline_Kim(cct_k):
    '''
    Function to compute the xy chromaticity coordinates from CCT in ºK

    The CCT should be in the range [1667, 25000 ºK]
    
    Kim, Y. et al. 2002. Design of advanced color-temperature control system for HDTV applications. 
    Journal of the Korean Physical Society, 41(6), 865.

    Parameters:    
        cct           float     CCT (º K)
    Returns:       
        x,y           float     x,y chromaticity coordinates of illuminant

    '''

    if 1667<=cct_k <=4000:
        x = -0.2661239e9/math.pow(cct_k, 3) - 0.2343589e6/(math.pow(cct_k, 2)) + 0.8776956e3/cct_k + 0.17991
    elif 4000<cct_k<=25000:
        x = -3.0258469e9/math.pow(cct_k, 3) + 2.1070379e6/(math.pow(cct_k, 2)) + 0.2226347e3/cct_k + 0.24039

    if 1667<=cct_k <=2222:
        y = -1.1063814*math.pow(x, 3) - 1.3481102*math.pow(x, 2) + 2.18555832*x - 0.20219683
    elif 2222<cct_k<=4000:
        y = -0.9549476*math.pow(x, 3) - 1.37418593*math.pow(x, 2) + 2.09137015*x - 0.16748867
    elif 4000<cct_k<25000:
        y = 3.081758*math.pow(x, 3) - 5.8733867*math.pow(x, 2) + 3.75112997*x - 0.37001483
    
    return x, y

# Ohno CCT, Duv --> xy

# the results are no accurate, search for a better algorithm
def compute_uv_from_CCT_Krystek(cct_k):

    '''

    Krystek, Michael P. 1985. An algorithm to calculate correlated colour temperature, 
    Color Research & Application. 10 (1): 38-40.

    '''

    # u,v CIE 1960 color space
    u = (0.860117757 + 1.54118254e-4*cct_k + 1.28641212e-7*math.pow(cct_k, 2))/(1 + 8.42420235e-4*cct_k + 7.08145163e-7*math.pow(cct_k, 2))
    v = (0.317398726 + 4.22806245e-5*cct_k + 4.20481691e-8*math.pow(cct_k, 2))/(1 - 2.89741816e-5*cct_k + 1.61456053e-7*math.pow(cct_k, 2))
    return u, v


def compute_xy_from_CCT_and_Duv_Ohno(cct_k, Delta_uv, DT = 0.01):
    '''
    

    Steps:
    - Calculate u0, v0 of the Plackian radiator at CCT
    - Calculate u1, v1 of the Plackian radiator at CCT + AT = 0.01 ºK


    Ohno, Yoshi. 2014. Practical Use and Calculation of CCT and Duv, LEUKOS, 10:1, 47-55, 
    doi: 10.1080/15502724.2014.839020
    
    '''

    u0, v0 = compute_uv_from_CCT_Krystek(cct_k) # Ohno uses other, but I don't know what is
    u1, v1 = compute_uv_from_CCT_Krystek((cct_k + DT))
    du = u1 - u0
    dv = v1 - v0

    u = u0 + Delta_uv*dv/(np.sqrt(math.pow(du, 2) + math.pow(dv, 2)))
    v = v0 + Delta_uv*du/(np.sqrt(math.pow(du, 2) + math.pow(dv, 2)))

    u_ = u  # u', v' CIE 1976 colour space
    v_ = 1.5*v

    x = 9*u_/(6*u_ - 16*v_ + 12)
    y = 2*v_/(3*u_ - 8*v_ + 6)

    return x, y


# NOT RECOMMENDED: Search for alternative method (does not provide accurate results for CCT out of range 4000<CCT<25000)

def compute_xy_from_CCT_CIE_D_illuminants_extended_range(cct_K):
    
    # without ºK limits defined by CIE
    
    try:
        cct_ini = int(cct_K)
    except:
        raise Exception("CCT not in valid units")    
    
    list_D_illuminants = [5000,5500,6500,7500] # D illuminants

    if cct_K in list_D_illuminants:
        ratio = 1.4388/1.4380
    else:
        ratio = 1.

    cct = cct_ini*ratio
    
    # Compute Chromaticity xD, yD
    if cct<=7000:
        xD = -4.6070*math.pow(10,9)/math.pow(cct, 3) + 2.9678*math.pow(10,6)/math.pow(cct, 2) + 0.09911*math.pow(10,3)/cct + 0.244063

    elif cct>7000 :
        xD = -2.0064*math.pow(10,9)/math.pow(cct, 3) + 1.9018*math.pow(10,6)/math.pow(cct, 2) + 0.24748*math.pow(10,3)/cct + 0.237040

    else:
        raise Exception("CTT not in valid range 4000-25000 ºK. Please use the m coefficients interpolation function")

    yD = -3.000*math.pow(xD,2) + 2.870*xD - 0.275
    
    return xD, yD
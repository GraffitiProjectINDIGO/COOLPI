import math
import numpy as np

from scipy import interpolate

from coolpi.auxiliary.errors import ExtrapolationError, InterpolationError
import coolpi.colour.cct_operations as cct
import coolpi.colour.colour_space_conversion as csc

# esta no me parece util con estos parametros
def find_common_range(lista_range):
    
    range_max, range_min = float('inf'), -float('inf')

    for rango in lista_range:
        minimum, maximum = rango[0], rango[1]
        range_min =  minimum if minimum > range_min else range_min
        range_max =  maximum if maximum < range_max else range_max
            
    return [range_min, range_max]

def range_is_valid(nm_range_original, nm_interval_original, nm_range_output, nm_interval_output):
    if nm_range_output[0] < nm_range_original[0]:
        return False
    if nm_range_output[1] > nm_range_original[1]:
        return False
    if nm_interval_output < nm_interval_original:
        return False
    return True
    
def extract_nm_range(lambda_values, nm_range_original, nm_interval_original, nm_range_output, nm_interval_output):
    ini = int((nm_range_output[0]-nm_range_original[0])/nm_interval_original)
    end = int((nm_range_original[1]-nm_range_output[1])/nm_interval_original)
    step = int(nm_interval_output/nm_interval_original)
    if ini == 0:
        if end == 0:
            slice = lambda_values[:len(lambda_values):step]
        else:
            slice = lambda_values[:-end:step]
    elif end == 0:
        slice = lambda_values[ini:len(lambda_values):step]
    else:
        slice = lambda_values[ini:-end:step]
    return slice

def create_wavelength_space(nm_ini, nm_end, nm_interval):
    num = ((nm_end-nm_ini)/nm_interval) + 1
    return np.linspace(nm_ini, nm_end, int(num))

# for spd illuminant

# linearise
def normalise_spectral_data(array):
    return array/np.amax(array)

def scale_reflectance(reflectance):
    spc = np.array(reflectance)
    max_lambda = spc.max()
    spc = spc*100 if 0<max_lambda<1 else spc # range [0-1] to [0-100]
    spc = list(spc)
    return spc

# CIE D illuminants: only from CCT in range [4000, 25000]

# CCT in ºK
def m_coefficients_cct(cct_K):
    ''' CIE 015:2018. 4.1.2. Other D illuminants (pp.12-13 (note 6)).
        When none f these daylight illuminants (D65, D50, D55 or D75), a daylight illuminant
        at a nominal correlated colour temperature (CCT) can be calculated usign this function.
        This function returns the coefficients for the computation of an illuminant whose CCT
        is aproxproximately equal to the nominal value, but not exactly so. 
    '''
    try:
        cct_ini = int(cct_K)
    except:
        raise Exception("CCT not in valid units")    
    
    xD, yD = cct.compute_xy_from_CCT_CIE_D_illuminants(cct_K)

    #print("Chromaticity = ", xD, yD)

    # Relative SPD SD = S0+M1*S1+M2*S2
    # M coefficients
    M1 = (-1.3515-1.7703*xD+5.9114*yD)/(0.0241+0.2562*xD-0.7341*yD)
    M2 = (0.0300 -31.4424*xD+30.0717*yD)/(0.0241+0.2562*xD-0.7341*yD)

    return xD, yD, M1, M2

def compute_SPD_from_CCT(cct_K, S0, S1, S2):
    xD, yD, M1, M2 = m_coefficients_cct(cct_K)
    #print("Chromaticity coordinates: ", xD, yD)
    #print("M coefficients: ", M1, M2)
    spd = []        
    for i in range(0,len(S0)):
        S = S0[i] + M1*S1[i] + M2*S2[i]
        spd.append(S)
    #print("SPD: ", spd)    
    return spd

# does not work. search for an alternative method
def compute_SPD_from_xy_and_M_coefficients(xD, yD, M1, M2, S0, S1, S2):
    s_nm_range = [300,830] # s component range
    # usual range for CIE illuminants
    nm_range = [380, 780]
    nm_interval = 5
    # has to be normalised
    spd = []        
    for i in range(0,len(S0)):
        S = S0[i] + M1*S1[i] + M2*S2[i]
        spd.append(S)
    #print("SPD: ", spd)    

    spd = extract_nm_range(spd, s_nm_range, nm_interval, nm_range, nm_interval)

    spd = np.array(spd)
    spd = spd/spd.max()
    spd = list(spd)

    return nm_range, nm_interval, spd

def m_coefficients_interpolation(cct_K):
    pass


# review Sprague method, it doesn't work ??
def sprague_interpolation(x, y, xn): 

    """ Sprague interpolation method. Fifth-order polynomial

        f(x) = a0 + a1 x + a2 x^2 + a3 x^3 + a4 x^4 + a5 * x^5

        x           wavelengh linspace with original interval
        y           lambda values
        xn          wavelengh linspace with new interval
        
        return:

        y_inter values interpolated

    """

    # Westland S. (2015) Interpolation of Spectral Data. In: Luo R. (eds) Encyclopedia of Color Science
    # and Technology. Springer, Berlin, Heidelberg. https://doi.org/10.1007/978-3-642-27851-8_366-1


    # a) Extrapolating four additional points 

    nm = x[1]-x[0] # nm for the original interval

    x_extend = np.linspace(x[0]-2*nm,x[x.shape[0]-1]+2*nm,(x.shape[0]+4))     # 4 Additional points
        
    y_extend = np.zeros(x.shape[0]+4)                                         # Empty array

    i = 0
    f = x.shape[0]-1

    i_ext = 0
    f_ext = x_extend.shape[0]-1

    y_extend[i_ext+1]  = (884.*y[i] - 1960.*y[i+1] + 3033.*y[i+2] - 2648.*y[i+3] + 1080.*y[i+4] - 180.*y[i+5])/209. # P0
    y_extend[i_ext]    = (508.*y[i] - 540.*y[i+1] + 488.*y[i+2] - 367.*y[i+3] + 144.*y[i+4] - 24.*y[i+5])/209. # P-1
    y_extend[f_ext-1]  = (-24.*y[f-5] + 144.*y[f-4] -367.*y[f-3] + 488.*y[f-2] - 540.*y[f-1] + 508.*y[f])/209. # PN+1
    y_extend[f_ext]    = (-180.*y[f-5] + 1080.*y[f-4] -2648.*y[f-3] + 3033.*y[f-2] - 1960.*y[f-1] + 884.*y[f])/209. # PN+2

    y = np.array(y)

    for j in range(0,y.shape[0]):
        y_extend[j+2] = y[j]    # Add the rest points
                
    # b) Interpolation

    new_values = []

    for value in range(0, x.shape[0]-1):

        i = value + 2

        new_values.append(y_extend[i]) # Add First value without interpolation

        w = x_extend[i] 

        d = (xn[1]-xn[0])/(x_extend[i+1]-x_extend[i]) 

        # Coefficients

        a0 =                                               y_extend[i]
        a1 = ( 2.*y_extend[i-2] - 16.*y_extend[i-1]                    +  16.*y_extend[i+1] -  2.*y_extend[i+2]                    )/24. 
        a2 = (  - y_extend[i-2] + 16.*y_extend[i-1] -  30.*y_extend[i] +  16.*y_extend[i+1] -     y_extend[i+2]                    )/24.
        a3 = (-9.*y_extend[i-2] + 39.*y_extend[i-1] -  70.*y_extend[i] +  66.*y_extend[i+1] - 33.*y_extend[i+2] +  7.*y_extend[i+3])/24.
        a4 = (13.*y_extend[i-2] - 64.*y_extend[i-1] + 126.*y_extend[i] - 124.*y_extend[i+1] + 61.*y_extend[i+2] - 12.*y_extend[i+3])/24.
        a5 = (-5.*y_extend[i-2] + 25.*y_extend[i-1] -  50.*y_extend[i] +  50.*y_extend[i+1] - 25.*y_extend[i+2] +  5.*y_extend[i+3])/24.

        # Compute interpolated values

        for j in range(1,int(x_extend[i+1]-x_extend[i])):
            nv = a0 + a1 *(d*j) + a2 * math.pow(d*j, 2) + a3 * math.pow(d*j, 3) +  a4 * math.pow(d*j, 4) + a5 * math.pow(d*j, 5)
            new_values.append(nv)

    new_values.append(y_extend[x.shape[0]-1]) # Add the last value

    y_inter = np.array(new_values) # As array

    return y_inter


def lambda_interpolation(x, y, xn, method = "Akima"):
    '''
    Function to interpolate the spectral data (illuminant / reflectance)

    Parameters:
        x           wavelengh linspace with original interval
        y           values
        xn          wavelengh linspace with new interval
        method      str: Linear, Spline, CubicHermite, Fifth, Sprague. Default "Akima"

    Returns:
        yn          list    values interpolated 

    '''

    implemented_methods = ["Linear", "Spline", "CubicHermite", "Fifth", "Sprague", "Akima"]

    if method not in implemented_methods:        
        raise InterpolationError("Interpolation method not implemented")

    if x[0]!=xn[0] or x[-1]!=xn[-1]:
        raise InterpolationError("The methods implemented are for iterpolate data nor for extrapolation")

    if method == "Sprague": # Method recommended by the CIE (CIE 2018, pg.25)
                            # CIE, 2005. Recommended practice for tabulating spectral data for use in colour computations.
                            # However, this method produce peaks at the edges. Spline interpolation gives better results, and fits better.
            
        yn = sprague_interpolation(x, y, xn)
        return yn

    if method == "Linear":
        f = interpolate.interp1d(x, y, kind='linear')

    elif method == "Spline": # smoothed method but fits very well on the edges    
        f = interpolate.InterpolatedUnivariateSpline(x, y, k=2, ext=2) # k=1, linear. k must be <>5. k=2 it's okay

    elif method == "CubicHermite": # less smoothed than Splines
        f = interpolate.PchipInterpolator(x, y) # Cubic Hermite Interpolating Polynomial

    elif method == "Fifth": # slighty smoothed method and peaks at the edges
        f = interpolate.InterpolatedUnivariateSpline(x, y, k=5, ext=2) # Order > 5 dosn't works

    # Only for interpolation in the same intervale, works very well
    elif method == "Akima":
        '''
        docs.scipy.org. Akima interpolator: Fit piecewise cubic polynomials, given vectors x and y.
        The interpolation method by Akima uses a continuously differentiable sub-spline built from
        piecewise cubic polynomials.The resultant curve passes through the given data points and
        will appear smooth and natural.

        '''

        f = interpolate.Akima1DInterpolator(x, y)
    
    yn = f(xn)

    return list(yn) # not numpy


# SEARCH FOR BETTER ALGORIMTHS

# be careful with the method used for extrapolation data, maybe provide incoherent result
# for extrapolation can be used only for a range nearby the original interval

def lambda_extrapolation(x, y, xn, method="Spline"):
    '''
    Function to extrapolate the spectral data (illuminant / reflectance)

    Parameters:
        x           wavelengh linspace with original interval
        y           values
        xn          wavelengh linspace with new interval
        method      str: Spline, CubicHermite, Fourth, Fifth. Default "Spline"

    Returns:
        yn          list    values interpolated 

    '''
    
    implemented_methods = ["Spline", "CubicHermite", "Fourth", "Fifth"]

    if method not in implemented_methods:        
        raise ExtrapolationError("Extrapolation method not implemented")

    if method == "Spline": # smoothed method but fits very well on the edges    
        f = interpolate.InterpolatedUnivariateSpline(x, y, k=2) # k=1, linear. k must be <>5. k=2 it's okay

    elif method == "CubicHermite": # less smoothed than Splines
        f = interpolate.PchipInterpolator(x, y) # Cubic Hermite Interpolating Polynomial

    elif method == "Fourth": # slighty smoothed method and peaks at the edges
        f = interpolate.InterpolatedUnivariateSpline(x, y, k=4) # Order > 5 dosn't works

    elif method == "Fifth": # slighty smoothed method and peaks at the edges
        f = interpolate.InterpolatedUnivariateSpline(x, y, k=5) # Order > 5 dosn't works
    
    yn = f(xn)
    return yn

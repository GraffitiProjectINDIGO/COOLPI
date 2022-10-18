import math
import numpy as np

import coolpi.colour.lambda_operations as lo

# CSC Colour space transform functions
# -----------------------------------------------------------------------------------------------

# Direct/Reverse transforms from XYZ

def XYZ_to_xyY(X, Y, Z):
    ''' 
    Function to compute the transformation between CIE XYZ and CIE xyY colour spaces

    CIE 015:2018. 7.3 Calculation of chromaticity coordinates, Eq. 7.5, p. 26.
    https://cie.co.at/publications/colorimetry-4th-edition/

    Parameters:
        X, Y, Z    float    CIE XYZ tristimulus values
        
    Returns:
        x, y, Y    float    CIE xyY coordinates

    '''
    
    x = X / (X + Y + Z)
    y = Y / (X + Y + Z)
    z = Z / (X + Y + Z)
    return x, y, Y

def xyY_to_XYZ(x, y, Y):
    ''' 
    Function to compute the transformation between CIE xyY and CIE XYZ colour spaces

    Kruschwitz, J. D. 2018. Field guide to colorimetry and fundamental color modeling. Society of Photo-Optical 
    Instrumentation Engineers. SPIE. p. 18
    
    https://spie.org/Publications/Book/2500913?SSO=1

    Parameters:    
        x, y, Y       float     CIE xyY coordinates
    Returns:       
        X, Y, Z       float     CIE XYZ tristimulus values
        
    '''

    X = Y * (x / y)
    Z = Y * (1 - x - y)/y

    return X, Y, Z

def XYZ_to_uvY(X,Y,Z):
    ''' 
    Function to compute the transformation between CIE XYZ and CIE 1976 u'v' colour spaces
    
    CIE015:2018. 8.1. CIE 1976 uniform chromaticity scale (UCS) diagram. Eq. 8.1. (p.27)
    https://cie.co.at/publications/colorimetry-4th-edition/
    
    Parameters:
        X, Y, Z       float    CIE XYZ tristimulus values
    
    Returns:
        u, v          float    CIE 1976 u'v' coordinates
        
    '''
    
    u = 4*X / (X + 15*Y + 3*Z)
    v = 9*Y / (X + 15*Y + 3*Z)
    
    return u, v, Y

def uvY_to_XYZ(u,v,Y):
    ''' 
    Function to compute the transformation between CIE 1976 u'v' and CIE XYZ colour spaces

    Solved using a linear equation system
        
    Parameters:
        u, v, Y        float    CIE 1976 u'v' coordinates
    
    Returns:
        X,Y,Z          float    CIE XYZ tristimulus values
        
    '''

    B = np.array([-15*u*Y, Y*(9-15*v)])
    A = np.array([[u-4, 3*u], [v, 3*v]])

    sol_equation = np.linalg.pinv(A).dot(B) if np.linalg.det(A)==0 else np.linalg.inv(A).dot(B)
        
    X = sol_equation[0]
    Z = sol_equation[1]

    return X, Y, Z

def XYZ_to_LAB(X, Y, Z, Xn=95.04, Yn=100.00, Zn=108.88):
    ''' 
    Function to compute the transformation between CIE XYZ and CIELAB colour spaces

    A reference WhitePoint Xn,Yn,Zn is required to perform this conversion

    CIE015:2018. 8.2.1. CIELAB colour space. 8.2.1.1. Basic coordinates. Eq. 8.3-8.11. p.28
    https://cie.co.at/publications/colorimetry-4th-edition/
        
    Parameters:
        X, Y, Z       float    CIE XYZ tristimulus values
        Xn, Yn, Zn    float    Illuminant WhitePoint coordinates (tristimulus values of white source, Yn=100)
                               Default D65 WhitePoint: Xn=95.04, Yn=100.00, Zn=108.88)
    
    Returns:
        L, a, b       float    CIELAB coordinates
    
    '''

    Xaux = X/Xn
    Yaux = Y/Yn
    Zaux = Z/Zn

    value = math.pow((24/116), 3)

    fX = math.pow(Xaux, (1/3)) if Xaux>value else (841/108)*(Xaux)+(24/116)
    fY = math.pow(Yaux, (1/3)) if Yaux>value else (841/108)*(Yaux)+(24/116)
    fZ = math.pow(Zaux, (1/3)) if Zaux>value else (841/108)*(Zaux)+(24/116)

    L = 116*fY-16   
    a = 500*(fX-fY)    
    b = 200*(fY-fZ)    
    
    return L, a, b

def LAB_to_XYZ(L, a, b, Xn=95.04, Yn=100.00, Zn=108.88):
    ''' 
    Function to compute the transformation between CIELAB and CIE XYZ colour spaces

    A reference WhitePoint Xn,Yn,Zn is required to perform this conversion

    CIE015:2018. Annex C. Reverse transformation from values Lab to tristimulus values XYZ (p.89)
    https://cie.co.at/publications/colorimetry-4th-edition/
    
    Parameters:
        L, a, b       float    CIELAB coordinates
        Xn, Yn, Zn    float    Illuminant WhitePoint coordinates (tristimulus values of white source, Yn=100)
                               Default D65 WhitePoint: Xn=95.04, Yn=100.00, Zn=108.88)

    Returns:
        X, Y, Z       float    CIE XYZ tristimulus values
    
    '''

    fy = (L+16)/116
    fx = a/500 + fy
    fz = fy - b/200

    X = Xn*math.pow(fx,3) if fx>24/116 else Xn*(fx-(16/116)*(108/841))
    Y = Yn*math.pow(fy,3) if fy>24/116 else Yn*(fy-(16/116)*(108/841))
    Z = Zn*math.pow(fz,3) if fz>24/116 else Zn*(fz-(16/116)*(108/841))

    return X, Y, Z

def XYZ_to_LUV(X, Y, Z, Xn=95.04, Yn=100.00, Zn=108.88):
    '''
    Function to compute the transformation between CIE XYZ and CIELUV colour spaces

    A reference WhitePoint Xn,Yn,Zn is required to perform this conversion

    CIE 015:2018. 8.2.2.1. Basic coordinates. Eq.8.26 to 8.30 (p.30)
    https://cie.co.at/publications/colorimetry-4th-edition/

    Parameters:    
        X, Y, Z        float    CIE XYZ tristimulus values
        Xn, Yn, Zn     float    Illuminant WhitePoint coordinates (tristimulus values of white source, Yn=100)
                                Default D65 WhitePoint: Xn=95.04, Yn=100.00, Zn=108.88)

    Returns:       
        L, U, V        float    CIELUV coordinates

    '''
    
    u, v, _ = XYZ_to_uvY(X,Y,Z)
    un, vn, _ = XYZ_to_uvY(Xn,Yn,Zn)
    
    Yaux = Y/Yn
    value = math.pow((24/116), 3)
    fY = math.pow(Yaux, (1/3)) if Yaux>value else (841/108)*(Yaux)+(16/116)
    
    L = 116*fY-16   
    U = 13*L*(u-un)
    V = 13*L*(v-vn)

    return L, U, V

def LUV_to_XYZ(L, U, V, Xn=95.04, Yn=100.00, Zn=108.88):
    '''
    Function to compute the transformation between CIELUV and CIE XYZ colour spaces

    A reference WhitePoint Xn,Yn,Zn is required to perform this conversion

    Parameters:
        L, U, V        float    CIELUV coordinates
        Xn, Yn, Zn     float    Illuminant WhitePoint coordinates (tristimulus values of white source, Yn=100)
                                Default D65 WhitePoint: Xn=95.04, Yn=100.00, Zn=108.88)

    Returns:       
        X, Y, Z        float    CIE XYZ tristimulus values

    '''

    un, vn, _ = XYZ_to_uvY(Xn, Yn, Zn)
    
    u = U/(13*L) + un
    v = V/(13*L) + vn
    
    fy = (L+16)/116

    Y = Yn*math.pow(fy,3) if fy>24/116 else Yn*(fy-(16/116)*(108/841))

    X, Y, Z = uvY_to_XYZ(u,v,Y)

    return X, Y, Z


# tested
# problem with sRGB gamut
def XYZ_to_RGB(X, Y, Z, rgb_space="sRGB", scaled = False):
    '''
    Function to compute the transformation between XYZ and RGB colour spaces (sRGB, AdobeRGB, AppleRGB)

    Implemented only for CIE D65 standard illuminant

    Parameters:
        X, Y, Z           float    CIE XYZ tristimulus values
        scaled            bool     If True, CIE XYZ in rage [0-1]. Default: False.
        
    Returns:       
        R, G, B           float    RGB coordinates
        
    '''
    # M coefficients only for D65
    # If the illuinant is defferent, appy cat to XYZ first
    dict_D65_M_xyz_to_rgb ={
        "Adobe": np.array([[2.04159, -0.56501, -0.34473], [-0.96924, 1.87597, 0.04156], [0.01344, - 0.11836, 1.01517]]),
        # Adobe RGB (1998) Color Image Encoding
        "Apple": np.array([[2.9515373, -1.2894116, -0.4738445], [-1.0851093, 1.9908566, 0.0372026], [0.0854934, -0.2694964, 1.0912975]]),
        #"Bruce": np.array([[2.7454669, -1.1358136, -0.4350269], [-0.9692660, 1.8760108, 0.0415560], [0.0112723, -0.1139754, 1.0132541]]),
        #"PAL/SECAM": np.array([[3.0628971, -1.3931791, -0.4757517], [-0.9692660, 1.8760108, 0.0415560], [0.0678775, -0.2288548, 1.0693490]]),
        #"SMPTE-C": np.array([[3.5053960, -1.7394894, -0.5439640], [-1.0690722, 1.9778245, 0.0351722], [0.0563200,-0.1970226, 1.0502026]]),
        "sRGB": np.array([[3.2406, -1.5372, -0.4986],[-0.9689, 1.8758, 0.0415], [0.0557, -0.2040,  1.0570]])}
        # IEC/4WD 61966-2-1: Colour Measurement and Management in Multimedia Systems and
        # Equipment - Part 2-1: Default RGB Colour Space - sRGB
    
    if rgb_space not in dict_D65_M_xyz_to_rgb.keys():
        raise Exception("RGB working space not implemented")

    X, Y, Z = [X, Y, Z] if scaled else [X/100, Y/100, Z/100] 

    M = dict_D65_M_xyz_to_rgb[rgb_space]

    RGB = np.dot(M, [X,Y,Z])
    R, G, B = [RGB[0], RGB[1], RGB[2]]

    # clipping
    R = 1 if R>1 else R
    R = 0 if R<0 else R

    G = 1 if G>1 else G
    G = 0 if G<0 else G

    B = 1 if B>1 else B
    B = 0 if B<0 else B

    # sRGB non-linear values
    non_linear = lambda coordinate: 1.055 * math.pow(coordinate,(1/2.4))- 0.055 if coordinate > 0.0031308 else 12.92 * coordinate
    R, G, B = [non_linear(R), non_linear(G), non_linear(B)] # range [0-1]

    # sRGB a RGB
    # RGB correction WDC, KDC (white and black digital count) R(255-0)+0, G(255-0)+0, B(255-0)+0 
    #correct_bits = lambda value: abs(int(round(value*255,0))) if bits == 8 else abs(int(round(value*255*255,0))) # 16 bits
    #R, G, B = [correct_bits(R), correct_bits(G), correct_bits(B)]

    return R, G, B

# RGB [0-1]
# tested, but consider the problem with the RGB colour space gamut
# The XYZ could be different
def RGB_to_XYZ(R, G, B, rgb_space="sRGB", scaled = False):
    '''
    Function to compute the transformation between RGB colour spaces (sRGB, AdobeRGB, AppleRGB) and CIE XYZ

    Implemented only for CIE D65 standard illuminant

    Parameters:
        R, G, B           float    RGB coordinates
        scaled            bool     If True, CIE XYZ in rage [0-1]. Default: False.
        
    Returns:       
        X, Y, Z           float    CIE XYZ tristimulus values
        
    '''
    dict_D65_M_rgb_to_xyz ={
        "Adobe": np.array([[0.57667, 0.18556, 0.18823], [0.29734, 0.62736, 0.07529], [0.02703, 0.07069, 0.99134]]),
        # Adobe RGB (1998) Color Image Encoding
        "Apple": np.array([[0.4497288, 0.3162486, 0.1844926], [0.2446525, 0.6720283, 0.0833192], [0.0251848, 0.1411824, 0.9224628]]),
        #"Bruce": np.array([[0.4674162, 0.2944512, 0.1886026], [0.2410115, 0.6835475, 0.0754410], [0.0219101, 0.0736128, 0.9933071]]),
        #"PAL/SECAM": np.array([[0.4306190, 0.3415419, 0.1783091], [0.2220379, 0.7066384, 0.0713236], [0.0201853, 0.1295504, 0.9390944]]),
        #"SMPTE-C": np.array([[0.3935891, 0.3652497, 0.1916313], [0.2124132, 0.7010437, 0.0865432], [0.0187423, 0.1119313, 0.9581563]]),
        "sRGB": np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])}
        # IEC/4WD 61966-2-1: Colour Measurement and Management in Multimedia Systems and
        # Equipment - Part 2-1: Default RGB Colour Space - sRGB

    if rgb_space not in dict_D65_M_rgb_to_xyz.keys():
        raise Exception("RGB working space not implemented")

    non_linear = lambda coordinate: math.pow(((coordinate+0.055)/1.055), 2.4) if coordinate > 0.04045 else coordinate/12.92
    R, G, B = [non_linear(R), non_linear(G), non_linear(B)]

    # Observer. = 2°, Illuminant = D65
    M = dict_D65_M_rgb_to_xyz[rgb_space]
    # particularizar M
    XYZ = np.dot(M,[R,G,B])
    X, Y, Z = [XYZ[0], XYZ[1], XYZ[2]] if scaled else [XYZ[0]*100, XYZ[1]*100, XYZ[2]*100]

    return X, Y, Z


# Direct/Reverse transforms from xy

def xy_to_uv(x,y):
    '''
    Function to compute the transformation between CIE 1931 xy chromaticity coordinates and CIE 1976 u',v' chromaticity coordinates

    CIE015:2018. 8.1. CIE 1976 uniform chromaticity scale (UCS) diagram
    Note. 3. p. 27. Eq. 8.2
    https://cie.co.at/publications/colorimetry-4th-edition/

    Parameters:    
        x, y            float     CIE x,y chromaticity coordinates
    
    Returns:       
        u, v            float     CIE 1976 u',v' chromaticity coordinates

    '''

    u = 4*x/(-2*x + 12*y + 3)
    v = 9*y/(-2*x + 12*y + 3)
    return u, v

def uv_to_xy(u,v):
    '''
    Function to compute the transformation between the CIE 1976 u',v'chromaticity coordinates and xy chromaticity coordinates

    Solved using a linear equation system

    Parameters:    
        u, v          float    CIE 1976 u', v' chromaticity coordinates

    Returns:       
        x, y          loat     x,y chromaticity coordinates of illuminant

    '''

    # equation system
    B = np.array([-3*u, -3*v])
    A = np.array([[-2*u-4, 12*u], [-2*v, 12*v-9]])

    sol_equation = np.linalg.pinv(A).dot(B) if np.linalg.det(A)==0 else np.linalg.inv(A).dot(B)
        
    x = sol_equation[0]
    y = sol_equation[1]
    return x,y

def xyY_to_LUV(x, y, Y, Xn=95.04, Yn=100.00, Zn=108.88):
    '''
    Function to compute the transformation between the CIE xyY and CIELUV colour spaces

    A reference WhitePoint Xn,Yn,Zn is required to perform this conversion

    CIE015:2018. 8.2.2. CIE 1976 L*u*v* colour space; CIELUV. 8.2.2.1 Basic coordinates (p.30)
    Note. 3. p. 27. Eq. 8.2
    https://cie.co.at/publications/colorimetry-4th-edition/

    Parameters:    
        x, y, Y         float     CIE xyY chromaticity coordinates
        Xn, Yn, Zn      float     Illuminant WhitePoint coordinates (tristimulus values of white source, Yn=100)
                                  Default D65 WhitePoint: Xn=95.04, Yn=100.00, Zn=108.88)

    Returns:       
        L, U, V         float     CIELUV coordinates

    '''

    u, v = xy_to_uv(x, y)

    un, vn, _ = XYZ_to_uvY(Xn, Yn, Zn)
    
    fY = math.pow(Y/Yn, (1/3)) if Y/Yn>math.pow((24/116), 3) else (841/108)*(Y/Yn)+(16/116)
    
    L = 116*fY-16   
    U = 13*L*(u-un) # u^*
    V = 13*L*(v-vn) # v^*
        
    return L, U, V

def LUV_to_xyY(L, U, V, Xn=95.04, Yn=100.00, Zn=108.88):
    '''
    Function to compute the transformation between CIELUV and CIE xyY colour space

    A reference WhitePoint Xn,Yn,Zn is required to perform this conversion

    Parameters:    
        L, U, V         float     CIELUV coordinates
        Xn, Yn, Zn      float     Illuminant WhitePoint coordinates (tristimulus values of white source, Yn=100)
                                  Default D65 WhitePoint: Xn=95.04, Yn=100.00, Zn=108.88)

    Returns:       
        x, y, Y         float     CIE xyY chromaticity coordinates

    '''

    un, vn, _ = XYZ_to_uvY(Xn, Yn, Zn)
    u = U/(13*L) + un
    v = V/(13*L) + vn
    
    fy = (L+16)/116

    Y = Yn*math.pow(fy,3) if fy>24/116 else Yn*(fy-(16/116)*(108/841))
    
    x,y = uv_to_xy(u,v)
    
    return x, y, Y


# Direct/Reverse transforms from LAB

def compute_saturation_uv(L, U, V, Xn=95.04, Yn=100.00, Zn=108.88):
    '''
    Function to compute the CIE 1976 u*, v* (CIELUV) saturatuion s_uv
    
    A reference WhitePoint Xn,Yn,Zn is required to perform this conversion

    CIE015:2018. 8.2.2.2. Correlates of lightness, saturation, chroma and hue. Eq. 8.31 (pg.29)
    
    Parameters:
        L, U, V         float     CIELUV coordinates
        Xn, Yn, Zn      float     Illuminant WhitePoint coordinates (tristimulus values of white source, Yn=100)
                                  Default D65 WhitePoint: Xn=95.04, Yn=100.00, Zn=108.88)

    Returns:
        s_uv            float     s_uv saturation value
    
    '''
    
    X, Y, Z = LUV_to_XYZ(L, U, V, Xn, Yn, Zn)
    u, v, _ = XYZ_to_uvY(X,Y,Z)
    un, vn, _ = XYZ_to_uvY(Xn,Yn,Zn)
    s_uv = 13*np.sqrt(math.pow((u-un), 2) + math.pow((v-vn), 2))
    return s_uv

def compute_chroma(a, b):
    '''
    Function to compute the Chroma value: Cab for CIELAB or Cuv for CIELUV is computed.
    
    CIE015:2018. 8.2.1.2. Correlates of lightness, chroma and hue. Eq. 8.12 (pg.29)
    CIE015:2018. 8.2.2.2. Correlates of lightness, saturation, chroma and hue. Eq. 8.32 (pg.29)
    
    Parameters:
        a, b     float    a, b CIELAB coordinates
                          U, V CIELUV coordinates
    Returns:
        C        float    Cab (for CIE LAB coordinates) or Cuv (for CIE LUV)

    '''
    
    C = np.sqrt(math.pow(a, 2) + math.pow(b, 2)) 
    return C

def compute_hue_angle_degree(a, b):
    '''
    Function to compute the hue-angle in degrees: hab for CIE LAB or huv for CIE LUV is computed.
    
    CIE015:2018. 8.2.1.2. Correlates of lightness, chroma and hue. Eq. 8.13 (pg.29)
    CIE015:2018. 8.2.2.2. Correlates of lightness, saturation, chroma and hue. Eq. 8.33 (pg.29)

    Parameters:
        a, b         float    a, b CIELAB coordinates
                              U, V CIELUV coordinates
    
    Returns:
        hue          float    hue-angle in degrees (quadrant corrected): hab for CIELAB, huv for CIELUV

    '''

    hue_ab = np.arctan2(b, a)
    hue_ab_degree = np.rad2deg(hue_ab)
    hue_ab = hue_ab_degree if hue_ab_degree >=0 else (360 + hue_ab_degree) # quadrant
    return hue_ab

    #hue_ab = np.arctan(b/a) # using arctan: same results
    #hue_ab_degree = np.abs(np.rad2deg(hue))

    #if a>0 and b>0:
    #    hue_ab = hue_ab_degree
    #elif a<0 and b>0:
    #    hue_ab = 180 - hue_ab_degree
    #elif a<0 and b<0:
    #    hue_ab = 180 + hue_ab_degree
    #else:
    #    hue_ab = 360 - hue_ab_degree

def LAB_to_LCHab(L, a, b):
    ''' 
    Function to compute the transformation between CIELAB and CIE LCHab colour spaces
    
    CIE015:2018. 8.2.1.2 Correlates of lightness, chroma and hue. Eq. 8.12-8.13 (p. 29)
    https://cie.co.at/publications/colorimetry-4th-edition/
    
    Note: consider angle quadrant
    a>0 and b>0 0<hab<90; a>0 and b>0 90<hab<180; a<0 and b<0 180<hab<270; a>0 and b<0 270<hab<360
    
    Parameters:
        L, a, b          float    CIELAB coordinates
    
    Returns:
        L, Cab, Hab      float    CIE LCHab. Hab in degrees
    
    '''
    
    Cab = compute_chroma(a, b)
    Hab = compute_hue_angle_degree(a, b)
    return L, Cab, Hab

def LCHab_to_LAB(L, Cab, Hab):    
    ''' 
    Function to compute the transformation between CIE LCHab and CIELAB colour spaces
    
    Parameters:
        L, Cab, Hab      float    CIELCHab. Hab in degrees 
    
    Returns:
        L, a, b          float    CIELAB coordinates
    
    '''
    
    a = Cab*np.cos(np.deg2rad(Hab))
    b = Cab*np.sin(np.deg2rad(Hab))
    return L, a, b


# Direct/Reverse transforms from LUV

def LUV_to_LCHuv(L, U, V):
    ''' 
    Function to compute the transformation between CIELUV and CIE LCHuv colour spaces
    
    CIE015:2018. 8.2.2.2 Correlates of lightness, chroma and hue. Eq. 8.32-8.33 (p. 31)
    https://cie.co.at/publications/colorimetry-4th-edition/
    
    Parameters:
        L, U, V              float    CIELUV coordinates
    
    Returns:
        L, Cuv, Huv          float    CIELCHuv. Huv in degrees
    
    '''

    Cuv = compute_chroma(U, V)
    Huv = compute_hue_angle_degree(U, V)
    return L, Cuv, Huv

def LCHuv_to_LUV(L, Cuv, Huv):
    ''' 
    Function to compute the transformation between CIELCHuv and CIELUV colour spaces
    
    Parameters:
        L, Cuv, Huv      float    CIELCHuv. Huv in degrees 
    
    Returns:
        L, U, V          float    CIELAB coordinates
    
    '''
    U = Cuv*np.cos(np.deg2rad(Huv))
    V = Cuv*np.sin(np.deg2rad(Huv))
    return L, U, V

# SPECTRAL to CIE XYZ
# -------------------

# Auxilizr functions

def compute_k_value(spd, y_cmf):
    suma= 0
    for i in range(0,len(spd)):
        suma += spd[i] * y_cmf[i]
    return 100/suma
    
def compute_summation_integral(reflectance, spd, cmf):
    suma = 0
    for i in range(0,len(reflectance)):
        suma += reflectance[i] * spd[i] * cmf[i]
    return suma

def spectral_to_XYZ(reflectance, spd, x_cmf, y_cmf, z_cmf):
    '''
    Function to compute the CIE XYZ tristimulus values from spectral data

    CIE015:2018. 7. Recommendations concerning the calculation of tristimulus values
    and crhromaticity coordinates. 7.1. Calculation of tristimulus values.
    7.1.1. Secondary light sources (reflecting or transmittign object) (pp.21-22)
    https://cie.co.at/publications/colorimetry-4th-edition/
 
    Parameters:
        reflectance            list     Spectral data measured for the colour sample
        spd                    list     SPD of refernce illuminant
        x_cmf, y_cmf, z_cmf    list     CIE CMFs 

        Note: The refflectance, spd and CMFs should to be into the same range

    Returns:
        X, Y, Z                float    CIE XYZ tristimulus values
    '''

    reflectance = lo.scale_reflectance(reflectance) # some instruments [0,1] scale to [1-100]
    
    k = compute_k_value(spd, y_cmf) # Eq. 7.3-7.4, pg. 22

    suma_x = compute_summation_integral(reflectance, spd, x_cmf) # Eq. 7.1-7.2, pg. 21
    suma_y = compute_summation_integral(reflectance, spd, y_cmf)
    suma_z = compute_summation_integral(reflectance, spd, z_cmf)

    X = k * suma_x / 100
    Y = k * suma_y / 100
    Z = k * suma_z / 100

    return X, Y, Z

# spectral to CIE XYZ using arrays, for one reflectance

def spectral_to_XYZ_using_arrays(reflectance, spd, x_cmf, y_cmf, z_cmf):
    '''
    Function to compute the CIE XYZ tristimulus values from spectral data (using np.dot)

    CIE015:2018. 7. Recommendations concerning the calculation of tristimulus values
    and crhromaticity coordinates. 7.1. Calculation of tristimulus values.
    7.1.1. Secondary light sources (reflecting or transmittign object) (pp.21-22)
    https://cie.co.at/publications/colorimetry-4th-edition/
 
    Parameters:
        reflectance            list     Spectral data measured for the colour sample.
        spd                    list     SPD of the illuminant.
        x_cmf, y_cmf, z_cmf    list     CIE CMFs.

        Note: The refflectance, spd and CMFs should to be into the same range

    Returns:
        X, Y, Z                float    CIE XYZ tristimulus values
    '''

    reflectance = lo.scale_reflectance(reflectance) # some instruments [0,1] scale to [1-100]
    # as diagonal array
    reflectance = np.diag(reflectance)
    spd = np.diag(spd)
    x_cmf = np.diag(x_cmf)
    y_cmf = np.diag(y_cmf)
    z_cmf = np.diag(z_cmf)

    k = 100/np.sum(np.dot(spd, y_cmf))

    # compute tristimulus values
    X = k*np.sum(np.dot(reflectance, np.dot(spd, x_cmf)))/100
    Y = k*np.sum(np.dot(reflectance, np.dot(spd, y_cmf)))/100
    Z = k*np.sum(np.dot(reflectance, np.dot(spd, z_cmf)))/100

    return X, Y, Z

# Note: Both functions provide the same result

# refeclectance as nx31 array 
def convert_image_spectral_data_to_XYZ(reflectance, spd, x_cmf, y_cmf, z_cmf):
    # as diagonal array
    spd = np.diag(spd)
    x_cmf = np.diag(x_cmf)
    y_cmf = np.diag(y_cmf)
    z_cmf = np.diag(z_cmf)

    k = 100/np.sum(np.dot(spd, y_cmf)) 

    spd_x = np.dot(spd, x_cmf).reshape(x_cmf.shape[0],1) # avoid error
    spd_y = np.dot(spd, y_cmf).reshape(y_cmf.shape[0],1)
    spd_z = np.dot(spd, z_cmf).reshape(z_cmf.shape[0],1)

    X_values = (k/100)*np.sum(np.dot(reflectance, spd_x), axis = 1)
    Y_values = (k/100)*np.sum(np.dot(reflectance, spd_y), axis = 1)
    Z_values = (k/100)*np.sum(np.dot(reflectance, spd_z), axis = 1)

    n_samples = reflectance.shape[0]

    XYZ = np.zeros((n_samples, 3))

    XYZ[:,0] = X_values
    XYZ[:,1] = Y_values
    XYZ[:,2] = Z_values

    return XYZ



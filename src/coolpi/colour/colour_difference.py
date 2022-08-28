import math
import numpy as np

import coolpi.auxiliary.common_operations as cop
import coolpi.colour.colour_space_conversion as csc

# CIE76. CIELAB

def delta_E_ab(L1, a1, b1, L2, a2, b2):
    '''
    Funtion to compute the CIE76 colour difference between two colour samples in CIELAB units
    
    CIE015:2018. 8.2.1.3. Colour differences. Eq. 8.14, 8.15, 8.16 and 8.21 (p.29)
    https://cie.co.at/publications/colorimetry-4th-edition/

    Parameters:
        L1, a1, b1    float    CIELAB coordinates of sample 1
        L2, a2, b2    float    CIELAB coordinates of sample 2
    
    Returns:
        delta_e_ab    float    CIE76 colour difference value in CIELAB units

    '''
    AL = L2 - L1 
    Aa = a2 - a1 
    Ab = b2 - b1
    delta_e_ab = cop.euclidean_distance(AL, Aa, Ab)
    return delta_e_ab

# CIE76. CIELCHab

def compute_hue_angle_difference(C1, H1, C2, H2):
    '''
    Function to compute the Hue difference for colour samples in CIELAB or CIELUV coordinates

    CIE015:2018. 8.2.1.3. Colour differences. Eq. 8.18 (pg.29). 8.2.3. Note 3. (p.31)
    https://cie.co.at/publications/colorimetry-4th-edition/

    Eq.10, p.22.
    Sharma, G., Wu, W., & Dalal, E. N. (2005). The CIEDE2000 color-difference formula: Implementation notes, 
    supplementary test data, and mathematical observations. Color Research & Application 30(1), 21-30.
    https://onlinelibrary.wiley.com/doi/abs/10.1002/col.20070

    Parameters:
        C1, H1    float    Chroma  and Hue (degree) sample 1
        C2, H2    float    Chroma  and Hue (degree) sample 2

    Returns:
        Ah   float    Ahab for CIELAB or Ahuv for CIELUV 

    '''

    if C1*C2 == 0:
        dif = 0
    else:
        if abs(H2-H1)<=180:
            dif = H2-H1
        elif (H2-H1)>180:
            dif = (H2-H1) - 360
        elif (H2-H1)<(-180):
            dif = (H2-H1) + 360

    Ah = np.deg2rad(dif)
    return Ah

def compute_Delta_H_difference(C1, C2, Ah):
    '''
    Function to compute the Delta_Hue difference for colour samples in CIELAB or CIELUV coordinates

    CIE015:2018. 8.2.1.3. Colour differences. Eq. 8.19 (pg.29). 8.2.3. Note 3. (p.31)
    CIE015:2018. 8.2.2.3. Colour differences. Eq. 8.34 (pg.31). 8.2.3. Note 3. (p.31)
    https://cie.co.at/publications/colorimetry-4th-edition/

    Parameters:
        C1          float    Chroma  sample 1
        C2          float    Chroma  sample 2
        Ah          float    Hue-angle difference in degrees

    Returns:
        Delta_H     float    Delta_Hab for CIELAB or Delta_Huv for CIELUV 

    '''
    
    Delta_H = 2*np.sqrt(C2*C1)*np.sin(Ah/2)
    return Delta_H

def delta_E_ab_cielchab(L1, Cab1, Hab1, L2, Cab2, Hab2):
    '''
    Funtion to compute the CIE76 colour difference between two colour samples in CIELHab coordinates

    CIE015:2018. 8.2.1.3. Colour differences. Eq. 8.22 (p.30)
    https://cie.co.at/publications/colorimetry-4th-edition/

    Parameters:
        L1, C1, Hab1    float    CIELAB coordinates of sample 1
        L2, C2, Hab2    float    CIELAB coordinates of sample 2

    Returns:
        delta_e_ab      float    CIE76 colour difference value in CIELAB units

    '''

    AL = L1 - L2 # Lighteness difference
    ACab = Cab2 - Cab1 # CIELAB chroma difference
    Ah = compute_hue_angle_difference(Cab1, Hab1, Cab2, Hab2)
    AHab = compute_Delta_H_difference(Cab1, Cab2, Ah)
    delta_e_ab =cop.euclidean_distance(AL, ACab, AHab) 
    return delta_e_ab

# CIE 1976 AEuv

def delta_E_uv(L1, U1, V1, L2, U2, V2):
    '''
    Funtion to compute the CIE76 colour difference between two colour samples in CIELUV units

    CIE015:2018. 8.2.2.3. Colour differences. Eq. 8.35 (p.31)
    https://cie.co.at/publications/colorimetry-4th-edition/

    Parameters:
        L1, U1, V1    float    CIELUV coordinates of sample 1
        L2, U2, V2    float    CIELUV coordinates of sample 2
    
    Returns:
        delta_e_uv    float    CIE76 colour difference value in CIELUV units

    '''

    AL = L2 - L1
    AU = U2 - U1
    AV = V2 - V1
    delta_e_uv = cop.euclidean_distance(AL, AU, AV)
    return delta_e_uv

def delta_E_uv_cielchuv(L1, Cuv1, Huv1 , L2, Cuv2, Huv2):
    '''
    Funtion to compute the CIE76 colour difference between two colour samples in CIELHab coordinates

    CIE015:2018. 8.2.1.3. Colour differences. Eq. 8.22 (p.30)
    https://cie.co.at/publications/colorimetry-4th-edition/

    Parameters:
        L1, C1, Hab1    float    CIELAB coordinates of sample 1
        L2, C2, Hab2    float    CIELAB coordinates of sample 2

    Returns:
        delta_e_uv      float    CIE76 colour difference value in CIELUV units

    '''

    AL = L1 - L2 # Lighteness difference
    ACuv = Cuv2 - Cuv1 # CIELAB chroma difference
    Ah = compute_hue_angle_difference(Cuv1, Huv1, Cuv2, Huv2)
    AHuv = compute_Delta_H_difference(Cuv1, Cuv2, Ah)
    delta_e_uv = cop.euclidean_distance(AL, ACuv, AHuv) 
    return delta_e_uv


# CIEDE2000

def compute_Hab_average(Cab1, Hab1, Cab2, Hab2):
    '''
    Funtion to compute the hue average for the CIEDE2000 formula
    
    Eq.14 (p.22)
    Sharma, G., Wu, W., & Dalal, E. N. (2005). The CIEDE2000 color-difference formula: Implementation notes, 
    supplementary test data, and mathematical observations. Color Research & Application 30(1), 21-30.
    https://onlinelibrary.wiley.com/doi/abs/10.1002/col.20070
    
    Parameters:
        C1, h1    float    Chroma, hue for the sample 1
        C2, h2    float    Chroma, hue for the sample 2

    Returns:
        Hab         float    hue average
    
    '''

    if Cab1*Cab2 != 0:
        if abs(Hab1-Hab2)<=180:
            Hab = np.average([Hab1, Hab2])
        elif abs(Hab1-Hab2)>180 and (Hab1+Hab2)<360:
            Hab = np.average([Hab1, (Hab2+360)])
        elif abs(Hab1-Hab2)>180 and (Hab1+Hab2)>=360:
            Hab = np.average([Hab1, (Hab2-360)])
    else:
        Hab = Hab1+Hab2
    return Hab

def compute_G_equation(Cab):
    '''
    Funtion to apply the G equation

    CIE015:2018. 8.3.1 CIEDE2000 colour-difference formula. Eq. 8.38 (p.33)
    https://cie.co.at/publications/colorimetry-4th-edition/
    
    Parameters:
        Cab           float    Cab    Chroma value
    
    Returns:
        G             float    G value computed for the input Cab 

    '''

    Cab_7 = math.pow(Cab,7)
    G = 0.5*(1-np.sqrt(Cab_7/(Cab_7+math.pow(25,7)))) # Eq. 8.38
    return G
    
def compute_weighting_functions(L, Cab, Hab):
    '''
    Funtion to apply the SL, SC and SH weighting functions

    CIE015:2018. 8.3.1 CIEDE2000 colour-difference formula. Eq. 8.39 to 8.42 (p.33)
    https://cie.co.at/publications/colorimetry-4th-edition/
    
    Parameters:
        L, Cab, Hab       float    L, Cab and Hab average values
        
    Returns:
        SL, SC, SH, T        float    SL, SC and SH weighting functions (T for testing)

    '''

    SL = 1 + (0.015*math.pow((L-50), 2) / np.sqrt(20 + math.pow((L-50), 2)) ) # Eq. 8.39
    SC = 1 + 0.045*Cab # Eq. 8.40
    T = 1 - 0.17*np.cos(np.deg2rad(Hab-30)) + 0.24*np.cos(np.deg2rad(2*Hab)) + 0.32*np.cos(np.deg2rad(3*Hab + 6)) - 0.2*np.cos(np.deg2rad(4*Hab-63)) # Eq. 8.42
    SH = 1 + 0.015*Cab*T # Eq. 8.41
    return SL, SC, SH, T

def compute_RT(Cab, Hab):
    '''
    Funtion to apply the RT equation
    
    CIE015:2018. 8.3.1 CIEDE2000 colour-difference formula. Eq. 8.43 to 8.45 (p.34)
    https://cie.co.at/publications/colorimetry-4th-edition/
    
    Parameters:
        Cab, Hab       float    Cab and Hab average values
        
    Returns:
        RT             float    RT value

    '''

    Cab_7 = math.pow(Cab, 7)
    RC = 2*np.sqrt(Cab_7/(Cab_7 + math.pow(25, 7))) # Eq. 8.45
    AT = 30*np.exp(-(math.pow(((Hab-275)/25), 2))) # Eq. 8.44
    RT = - (np.sin(np.deg2rad(2*AT)))*RC # Eq. 8.43
    return RT

def CIEDE2000(L1, a1, b1, L2, a2, b2, kl=1, kc=1, kh=1):
    '''
    Funtion to compute the CIEDE2000 colour difference between two colour samples in CIELAB coordinates

    CIEDE2000 - Improved industrial colour-difference evaluation
    CIE015:2018. 8.3.1. CIEDE2000 colour-difference formula. Eq. 8.36 (pg.33) to Eq. 8.45 (and NOTES)
    https://cie.co.at/publications/colorimetry-4th-edition/

    Sharma, G., Wu, W., & Dalal, E. N. (2005). The CIEDE2000 color-difference formula: Implementation notes, 
    supplementary test data, and mathematical observations. Color Research & Application, 30(1), 21-30.
    https://onlinelibrary.wiley.com/doi/abs/10.1002/col.20070

    Note: Validate using Table 1. CIEDE2000 total color difference test data (Sharma et al., 2005)

    Parameters:
        L1, a1, b1    float    CIELAB coordinates of sample 1
        L2, a2, b2    float    CIELAB coordinates of sample 2
        kl, kc, kh    float    kl, kc, kh parametric factors. Default values set to 1
                                                              (CIE,2018. NOTE 1, p.34)
    
    Returns:
        AE00          float    CIEDE2000 value in CIELAB units 

    '''
    
    Cab1 = csc.compute_chroma(a1, b1) # (2)
    Cab2 = csc.compute_chroma(a2, b2)
    Cab = np.average([Cab1, Cab2]) # (3)

    G = compute_G_equation(Cab) # (4)

    # L,a,b scaled
    a1_ = (1+G)*a1 # (5)
    a2_ = (1+G)*a2
    Cab1_ = csc.compute_chroma(a1_, b1) # (6)
    Cab2_ = csc.compute_chroma(a2_, b2)
    Hab1_ = csc.compute_hue_angle_degree(a1_, b1) # (7)
    Hab2_ = csc.compute_hue_angle_degree(a2_, b2)

    AL_ = L2 - L1 # (8)
    AC_ = Cab2_ - Cab1_ #(9)
    Ah_ = compute_hue_angle_difference(Cab1_, Hab1_, Cab2_, Hab2_) # (10)
    AH_ = compute_Delta_H_difference(Cab1_, Cab2_, Ah_) # (11)

    L_ = np.average([L1, L2]) # (12)
    Cab_ = np.average([Cab1_, Cab2_]) # (13)
    Hab_ = compute_Hab_average(Cab1_, Hab1_, Cab2_, Hab2_) # (14)

    SL, SC, SH, _ = compute_weighting_functions(L_, Cab_, Hab_) # (19), (20), (21)

    RT = compute_RT(Cab_, Hab_) # (21)

    AE00 = np.sqrt(math.pow((AL_/(kl*SL)), 2) + math.pow((AC_/(kc*SC)), 2) + math.pow((AH_/(kh*SH)), 2) + RT*((AC_/(kc*SC))*((AH_/(kh*SH))))) # Eq. 8.36
    return AE00
import numpy as np
import math

import coolpi.auxiliary.common_operations as cop
import coolpi.auxiliary.errors as exc

def XYZ_to_LMS(X, Y, Z):
    # LMS or CIE RGB
    # Ec. 2.7. Digital Imaging Color Handbook (2.6.4. von Kries Model) D65
    XYZ = np.array([X,Y,Z])
    M = np.matrix("0.4002 0.7076 -0.0808;-0.2263 1.1653 0.0457; 0.0 0.0 0.9182") # Von Kries Model
    LMS = np.transpose(np.dot(M, XYZ))
    L, M, S = float(LMS[0]), float(LMS[1]), float(LMS[2])
    return L, M, S

# CAT's (Chromatic Adaptation Transforms)
# "LMSw WhiteRef en LMS, XYZ un objeto colour en coordenadas CIE XYZ"
# LMS to XYZ
def apply_von_Kries_model(X, Y, Z, L, M, S):

    # gain control coefficients, described to be the inverse of the maximum LMS response in the scene (WhiteReference)
    # white point normalization
    aL = 1/L
    aM = 1/M
    aS = 1/S
    
    # coefficients as matrix
    C = np.matrix([[aL,0.,0.],[0.,aM,0.],[0.,0.,aS]])

    M = np.matrix("0.4002 0.7076 -0.0808;-0.2263 1.1653 0.0457; 0.0 0.0 0.9182") # M matrix D65
    
    MI = cop.compute_inverse_array(M)
        
    # dot product
    XYZ = np.matrix([[X],[Y],[Z]])
    LMS = np.dot(M,XYZ)
    LMSad = np.dot(C,LMS)

    XYZad = np.dot(MI,LMSad)*100 # Escalar

    # tristimulus values 
    Xa, Ya, Za = float(XYZad[0]), float(XYZad[1]), float(XYZad[2])

    return Xa, Ya, Za  # Que devuelva una matriz, o que devuelva un objeto de tipo colour?

def apply_von_Kries_transform(X, Y, Z, L1, M1, S1, L2, M2, S2):

    # gain control coefficients, described to be the inverse of the maximum LMS response in the scene (WhiteReference)
    # white point normalization
    aL = 1/L1
    aM = 1/M1
    aS = 1/S1
    
    # coefficients as matrix
    C1 = np.matrix([[aL,0.,0.],[0.,aM,0.],[0.,0.,aS]])
    C2 = np.matrix([[L2,0.,0.],[0.,M2,0.],[0.,0.,S2]])

    M = np.matrix("0.4002 0.7076 -0.0808;-0.2263 1.1653 0.0457; 0.0 0.0 0.9182") # M matrix
    MI = cop.compute_inverse_array(M)

    # dot product

    # XYZ as matrix
    XYZm = np.matrix([[X],[Y],[Z]])

    LMS     = np.dot(M,XYZm)
    LMSad   = np.dot(C1,LMS)
    LMS2    = np.dot(C2,LMSad)

    XYZad   = np.dot(MI,LMS2) # No hace falta escalar multiplicando por 100

    Xa, Ya, Za = float(XYZad[0]),float(XYZad[1]),float(XYZad[2])

    return Xa, Ya, Za 

# La transformacion de Bradford sirve de base para la definicion del CIECAM97s
def apply_Bradford_non_linear_transform(X, Y, Z, Xn1, Yn1, Zn1, Xn2, Yn2, Zn2):

    # Step1. XYZ To RGB ("Spectral sharpening and the Bradford transformation. Finlayson.2000)
    Mbfd = np.matrix("0.8951 0.2664 -0.1614;-0.7502 1.7135 0.0367; 0.0389 -0.0685 1.0296") # Mbfd matrix
    XYZ = np.matrix([[X/Y],[Y/Y],[Z/Y]])

    RGBm = np.dot(Mbfd, XYZ) # RGB or LMS

    R = float(RGBm[0])
    G = float(RGBm[1])
    B = float(RGBm[2])

    # Test illuminants
    XYZw1 = np.matrix([[Xn1/Yn1],[Yn1/Yn1],[Zn1/Yn1]])
    XYZw2 = np.matrix([[Xn2/Yn2],[Yn2/Yn2],[Zn2/Yn2]])

    RGBw1 = np.dot(Mbfd, XYZw1)
            
    Rw1 = float(RGBw1[0])
    Gw1 = float(RGBw1[1])
    Bw1 = float(RGBw1[2])
            
    RGBw2 = np.dot(Mbfd, XYZw2)
            
    Rw2 = float(RGBw2[0])
    Gw2 = float(RGBw2[1])
    Bw2 = float(RGBw2[2])

    # Step2. RGB - R'G'B' (Notacion mia Rr Gg Bb)
    Rr = Rw2*(R/Rw1)
    Gg = Gw2*(G/Gw1)
    p = math.pow((Bw1/Bw2),0.0834)
    Bb = math.pow(Bw2*(B/Bw1),p)

    # Step3. R'G'B' To X'Y'Z'
    MbfdI = cop.compute_inverse_array(Mbfd)
    RrGgBb = np.matrix([[Rr*Y],[Gg*Y],[Bb*Y]]) # En forma de matriz
    XYZinw2 = np.dot(MbfdI,RrGgBb)

    X2, Y2, Z2 = float(XYZinw2[0]),float(XYZinw2[1]),float(XYZinw2[2])

    return X2, Y2, Z2

# No hay diferencias significativas entre el modelo no-lineal / lineal
def apply_Bradford_linear_transform(X, Y, Z, Xn1, Yn1, Zn1, Xn2, Yn2, Zn2):
    
    Mbfd = np.matrix("0.8951 0.2664 -0.1614;-0.7502 1.7135 0.0367; 0.0389 -0.0685 1.0296") # Mbfd matrix
    
    MbfdI = cop.compute_inverse_array(Mbfd)

    XYZm = np.matrix([[X],[Y],[Z]])

    # Test illuminants
    XYZw1 = np.matrix([[Xn1/Yn1],[Yn1/Yn1],[Zn1/Yn1]])
    XYZw2 = np.matrix([[Xn2/Yn2],[Yn2/Yn2],[Zn2/Yn2]])
    
    RGBw1 = np.dot(Mbfd, XYZw1)
            
    Rw1 = float(RGBw1[0])
    Gw1 = float(RGBw1[1])
    Bw1 = float(RGBw1[2])
            
    RGBw2 = np.dot(Mbfd,XYZw2)
            
    Rw2 = float(RGBw2[0])
    Gw2 = float(RGBw2[1])
    Bw2 = float(RGBw2[2])

    d1 = Rw2/Rw1
    d2 = Gw2/Gw1
    d3 = Bw2/Bw1

    D = np.matrix([[d1,0,0],[0,d2,0],[0,0,d3]])

    S1 = np.dot(Mbfd, XYZm)
    S2 = np.dot(D, S1)
    XYZinw2 = np.dot(MbfdI, S2)

    X2, Y2, Z2 = float(XYZinw2[0]),float(XYZinw2[1]),float(XYZinw2[2])

    return X2, Y2, Z2
            
# D array
def compute_degree_of_adaptation(Xn1, Yn1, Zn1, Xn2, Yn2, Zn2, cat_model):

    dict_cat_M_array ={
        "von Kries": np.matrix("0.3897 0.6890 -0.0787;-0.2298 1.1834 0.0464; 0.0 0.0 1.0"),
        "Bradford":  np.matrix("0.8951 0.2664 -0.1614;-0.7502 1.7135 0.0367; 0.0389 -0.0685 1.0296"),
        "Sharp": np.matrix("1.2694 0.0988 -0.1706;-0.8364 1.8006 0.0357; 0.0297 -0.0315 1.0018"),
        "CMCCAT200": np.matrix("0.7982 0.3389 -0.1371;-0.5918 1.5512 0.0406; 0.0008  0.2390 0.9753"),
        "CAT02": np.matrix("0.7328 0.4296 -0.1624;-0.7036 1.6975 0.0061; 0.0030  0.0136 0.9834"),
        "BS": np.matrix("0.8752 0.2787 -0.1539;-0.8904 1.8709 0.0195;-0.0061  0.0162 0.9899"),
        "BSPC": np.matrix("0.6489 0.3915 -0.0404;-0.3775 1.3055 0.0720;-0.0271  0.0888 0.9383")}

    '''
    CAT coefficient from Bianco and Schettini, 2010
    Bianco, S., and Schettini, R. 2010. Two new von Kries based chromatic adaptation transforms found by 
    numerical optimization. Color Research & Application, 35(3), 184-192.
    https://onlinelibrary.wiley.com/doi/abs/10.1002/col.20573 
    
    '''
    
    if cat_model not in dict_cat_M_array.keys():
        raise exc.CatModelError(f"CAT model not implemented. Please, select : {dict_cat_M_array.keys()}")
    
    M = dict_cat_M_array[cat_model]
    MI = cop.compute_inverse_array(M)
        
    # Test illuminants
    XYZw1 = np.matrix([[Xn1/Yn1],[Yn1/Yn1],[Zn1/Yn1]])
    XYZw2 = np.matrix([[Xn2/Yn2],[Yn2/Yn2],[Zn2/Yn2]])
            
    # en realidad es LMS, en otros libros lo llama RGB
    RGBw1 = np.dot(M, XYZw1)
            
    Rw1 = float(RGBw1[0])
    Gw1 = float(RGBw1[1])
    Bw1 = float(RGBw1[2])
            
    RGBw2 = np.dot(M, XYZw2)
            
    Rw2 = float(RGBw2[0])
    Gw2 = float(RGBw2[1])
    Bw2 = float(RGBw2[2])

    d1 = Rw2/Rw1
    d2 = Gw2/Gw1
    d3 = Bw2/Bw1

    D = np.matrix([[d1,0,0],[0,d2,0],[0,0,d3]])
    
    return D

# Funcion CATs. Aplica la transformacion deseada. Solo hay que especificar la matriz M
# Model="von Kries" "Bradford" "Sharp" "CMCCAT200" "CAT02" "BS" "BSPC"

def apply_CATs_transform(X, Y, Z, Xn1, Yn1, Zn1, Xn2, Yn2, Zn2, cat_model):

    dict_cat_M_array ={
        "von Kries": np.matrix("0.3897 0.6890 -0.0787;-0.2298 1.1834 0.0464; 0.0 0.0 1.0"),
        "Bradford":  np.matrix("0.8951 0.2664 -0.1614;-0.7502 1.7135 0.0367; 0.0389 -0.0685 1.0296"),
        "Sharp": np.matrix("1.2694 0.0988 -0.1706;-0.8364 1.8006 0.0357; 0.0297 -0.0315 1.0018"),
        "CMCCAT200": np.matrix("0.7982 0.3389 -0.1371;-0.5918 1.5512 0.0406; 0.0008  0.2390 0.9753"),
        "CAT02": np.matrix("0.7328 0.4296 -0.1624;-0.7036 1.6975 0.0061; 0.0030  0.0136 0.9834"),
        "BS": np.matrix("0.8752 0.2787 -0.1539;-0.8904 1.8709 0.0195;-0.0061  0.0162 0.9899"),
        "BSPC": np.matrix("0.6489 0.3915 -0.0404;-0.3775 1.3055 0.0720;-0.0271  0.0888 0.9383")}

    if cat_model not in dict_cat_M_array.keys():
        raise exc.CatModelError(f"CAT model not implemented. Please, select : {dict_cat_M_array.keys()}")
    
    M = dict_cat_M_array[cat_model]
    
    MI = cop.compute_inverse_array(M)
        
    
    XYZm = np.matrix([[X],[Y],[Z]])

    # Test illuminants
    XYZw1 = np.matrix([[Xn1/Yn1],[Yn1/Yn1],[Zn1/Yn1]])
    XYZw2 = np.matrix([[Xn2/Yn2],[Yn2/Yn2],[Zn2/Yn2]])
            
    # en realidad es LMS, en otros libros lo llama RGB
    RGBw1 = np.dot(M, XYZw1)
            
    Rw1 = float(RGBw1[0])
    Gw1 = float(RGBw1[1])
    Bw1 = float(RGBw1[2])
            
    RGBw2 = np.dot(M,XYZw2)
            
    Rw2 = float(RGBw2[0])
    Gw2 = float(RGBw2[1])
    Bw2 = float(RGBw2[2])

    d1 = Rw2/Rw1
    d2 = Gw2/Gw1
    d3 = Bw2/Bw1

    D = np.matrix([[d1,0,0],[0,d2,0],[0,0,d3]])

    S1 = np.dot(M,XYZm)
    S2 = np.dot(D,S1)
    XYZinw2 = np.dot(MI,S2)

    X2, Y2, Z2 = float(XYZinw2[0]),float(XYZinw2[1]),float(XYZinw2[2])
    
    return X2, Y2, Z2 

import cv2
import numpy as np
from scipy.optimize import least_squares

import coolpi.auxiliary.common_operations as cop

# RGB to XYZ Optimization for XYZspd

def compute_model_residuals(a, x, y):
    '''
    Function which computes the vector of residuals (function to minimise)

    '''
    
    return y - np.dot(a, x)

def compute_non_linear_optimization_model(fun, x0, x_data, y_data):
    '''
    Function to computhe the non-liear optimization problem using scipy

    '''
    
    ls_sol = least_squares(compute_model_residuals, x0, args=(x_data, y_data))
    return ls_sol

def apply_non_linear_optimization(fun, RGB_to_XYZ, XYZspd):
    '''
    Function to obtain the RGB_to_XYZ optimization matrix for the SPD of the shot
    
    '''

    Xspd, Yspd, Zspd = XYZspd[0]/XYZspd[1], XYZspd[1]/XYZspd[1],  XYZspd[2]/XYZspd[1] # range [0,1]

    x0 = [1, 1, 1] # initial values
    sol_x = compute_non_linear_optimization_model(fun, x0, RGB_to_XYZ[0], Xspd)
    sol_y = compute_non_linear_optimization_model(fun, x0, RGB_to_XYZ[1], Yspd)
    sol_z = compute_non_linear_optimization_model(fun, x0, RGB_to_XYZ[2], Zspd)

    RGB_to_XYZ_norm = [[RGB_to_XYZ[0][0]*sol_x.x[0], RGB_to_XYZ[0][1]*sol_x.x[1], RGB_to_XYZ[0][2]*sol_x.x[2]],
                       [RGB_to_XYZ[1][0]*sol_y.x[0], RGB_to_XYZ[1][1]*sol_y.x[1], RGB_to_XYZ[1][2]*sol_y.x[2]],
                       [RGB_to_XYZ[2][0]*sol_z.x[0], RGB_to_XYZ[2][1]*sol_z.x[1], RGB_to_XYZ[2][2]*sol_z.x[2]]]

    return np.array(RGB_to_XYZ_norm)

# COLOUR TRANSFORM

# CIE XYZ D65 to sRGB (using np.einsum)

def apply_xyz_d65_to_rgb_linear(xyz_d65_data, rgb_space="sRGB"):

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

    xyz_to_rgb = np.array(dict_D65_M_xyz_to_rgb[rgb_space], dtype=np.double)
    sRGB_linear = np.einsum('ij,...j', xyz_to_rgb, xyz_d65_data)
    sRGB_linear = np.clip(sRGB_linear, 0, 1)
    return sRGB_linear

# using np.dot

def apply_xyz_d65_to_rgb_linear_using_dot_product(xyz_d65_data, rgb_space="sRGB"):

    # reshape
    col, row, channels = xyz_d65_data.shape[0], xyz_d65_data.shape[1], xyz_d65_data.shape[2]
    XYZ_data = np.reshape(xyz_d65_data, (col*row, channels))
    #print(XYZ_data.shape)

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

    M = dict_D65_M_xyz_to_rgb[rgb_space]

    sRGB_linear = np.dot(M, XYZ_data.T) # xyz in range [0,1]
    sRGB_linear = np.array(sRGB_linear.T).reshape(col,row,channels)
    sRGB_linear = np.clip(sRGB_linear, 0, 1)

    return sRGB_linear

# Note: Both functions provide the same resuls, but np.eisum is optimised 

# reverse

def apply_rgb_linear_to_xyz_d65(rgb_linear, rgb_space="sRGB"):

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

    rgb_to_xyz = np.array(dict_D65_M_rgb_to_xyz[rgb_space], dtype=np.double)
    xyz_data = np.einsum('ij,...j', rgb_to_xyz, rgb_linear)

    return xyz_data


# sRGB linear to sRGB non-linear (gamma)

def compute_nonlinear_sRGB(sRGB_linear):
    # IEC/4WD 61966-2-1: Colour Measurement and Management in Multimedia Systems and
    # Equipment - Part 2-1: Default RGB Colour Space - sRGB

    sRGB_linear = np.clip(sRGB_linear, 0, 1) if sRGB_linear.max()>1 else sRGB_linear

    sRGB_nonlinear = sRGB_linear.copy()
    i = sRGB_nonlinear < 0.0031308
    j = np.logical_not(i)
    sRGB_nonlinear[i] = 12.92 * sRGB_nonlinear[i]
    sRGB_nonlinear[j] = 1.055 * sRGB_nonlinear[j]**(1.0/2.4) - 0.055
    sRGB_nonlinear = np.clip(sRGB_nonlinear, 0, 1) 
    return sRGB_nonlinear

# Gamma correction (2.2)

def apply_gamma_correction(sRGB_data, gamma=2.2):
    # 8 bits
    #img_1_22 = 255.0 * (sRGB_data/ 255.0)**(1/gamma)
    #img_22 = 255.0 * (sRGB_data/255.0)**gamma
    #img_gamma = np.concatenate((img_1_22, sRGB_data, img_22), axis=1)
    
    img_gamma = sRGB_data**(1/gamma)
    return img_gamma

# using OpenCV
def apply_gamma_correction_cv(sRGB_data, gamma): # 8bits
    sRGB_data = 255*sRGB_data # [0-255]
    sRGB_data = np.uint8(sRGB_data) # int 8 bits 

    gama_inv = 1 / gamma
    table = [((i / 255) ** gama_inv) * 255 for i in range(256)]
    table = np.array(table, np.uint8)
 
    rgb_gamma = cv2.LUT(sRGB_data, table)
 
    rgb_gamma = rgb_gamma/255.
 
    return rgb_gamma


# Colour rotation matrix CRM

# CAM to sRGB linear
def compute_rotation_matrix_for_CAM_to_XYZ_to_sRGB_transform(CAM_to_XYZ):
    # CAM (RAW RGB) ---> XYZ --> sRGB
    xyz_to_srgb = np.array([[3.2406, -1.5372, -0.4986],[-0.9689, 1.8758, 0.0415], [0.0557, -0.2040,  1.0570]], dtype=np.double)
    cam_to_srgb = np.dot(xyz_to_srgb, CAM_to_XYZ)
    cam_to_srgb_norm = cop.normalise_matrix(cam_to_srgb)
    return cam_to_srgb_norm


# 1) RAW RGB normalised ---> WB

def normalise_raw_data(raw_rgb_data):
    R_max = np.max(raw_rgb_data[:,:,0])
    G_max = np.max(raw_rgb_data[:,:,1])
    B_max = np.max(raw_rgb_data[:,:,2])
    print("RGB max = ", R_max, G_max, B_max)
    max_value = np.max(raw_rgb_data) # usually, max_value in green channel
    print(max_value)
    raw_rgb_data = raw_rgb_data/max_value    
    return raw_rgb_data


def normalise_raw_data_(raw_rgb_data):
    raw_rgb_data = np.array(raw_rgb_data).astype(np.float32)
    R_max = np.max(raw_rgb_data[:,:,0])
    G_max = np.max(raw_rgb_data[:,:,1])
    B_max = np.max(raw_rgb_data[:,:,2])
    
    raw_rgb_data[:,:,0] = raw_rgb_data[:,:,0]/R_max
    raw_rgb_data[:,:,1] = raw_rgb_data[:,:,1]/G_max
    raw_rgb_data[:,:,2] = raw_rgb_data[:,:,2]/B_max
    
    return raw_rgb_data


# 2) RGB to CIE XYZ (under SPD conditions)
def apply_RGB_to_XYZ_transform_matrix(RGB_to_XYZ, rgb_data):
    xyz_data = np.einsum('ij,...j', RGB_to_XYZ, rgb_data)
    return xyz_data

def apply_RGB_to_XYZ_transform_matrix_using_dot_product(RGB_to_XYZ, rgb_data):
    # reshape rgb data for dot product
    col, row, channels = rgb_data.shape[0], rgb_data.shape[1], rgb_data.shape[2]
    rgb_data = np.reshape(rgb_data, (col*row, channels))
    # usign dot
    xyz_data = np.dot(RGB_to_XYZ, rgb_data.T) # xyz in range [0,1]
    # reshape
    xyz_data = np.array(xyz_data.T).reshape(col,row,channels)

    return xyz_data

def apply_RGB_to_XYZ_transform_matrix_(RGB_to_XYZ, rgb_data):
    if isinstance(RGB_to_XYZ, list):
        RGB_to_XYZ = np.array(RGB_to_XYZ)

    if RGB_to_XYZ.shape[0]==4:
        RGB_to_XYZ = RGB_to_XYZ[0:3,:]
        RGB_to_XYZ = cop.compute_inverse_array(RGB_to_XYZ)

    # reshape rgb data for dot product
    col, row, channels = rgb_data.shape[0], rgb_data.shape[1], rgb_data.shape[2]
    rgb_data = np.reshape(rgb_data, (col*row, channels))

    #norm = np.tile(np.sum(RGB_to_XYZ, 1), (3, 1)).transpose()
    #RGB_to_XYZ = RGB_to_XYZ / norm

    #xyz_data = np.einsum('ij,...j', RGB_to_XYZ, rgb_data) # probar diferentes opciones

    #xyz_data = np.einsum('ij...,jk', RGB_to_XYZ, rgb_data)
    
    # usign dot
    XYZ_data = np.dot(RGB_to_XYZ, rgb_data.T) # xyz in range [0,1]
    print(XYZ_data.T.shape)
    XYZ_data = np.array(XYZ_data.T).reshape(col,row,channels)
    print(XYZ_data.shape)

    return XYZ_data

# 3) CIE XYZ spd to D65 (CATs, using arrays)
# Xn1, Yn1, Zn1 WhitePoint shot illuminant
# Xn2, Yn2, Zn2 D65 WhitePoint 0.9504, 1.00, 1.0888
def apply_CAT_XYZ_to_D65(XYZ_data, Xn1, Yn1, Zn1, Xn2=0.9504, Yn2=1.00, Zn2=1.0888, cat_model = "von Kries"):
    
    # reshape
    col, row, channels = XYZ_data.shape[0], XYZ_data.shape[1], XYZ_data.shape[2]
    XYZ_data = np.reshape(XYZ_data, (col*row, channels))
    
    dict_cat_M_array ={
        "von Kries": np.matrix("0.3897 0.6890 -0.0787;-0.2298 1.1834 0.0464; 0.0 0.0 1.0"),
        "Bradford":  np.matrix("0.8951 0.2664 -0.1614;-0.7502 1.7135 0.0367; 0.0389 -0.0685 1.0296"),
        "Sharp": np.matrix("1.2694 0.0988 -0.1706;-0.8364 1.8006 0.0357; 0.0297 -0.0315 1.0018"),
        "CMCCAT200": np.matrix("0.7982 0.3389 -0.1371;-0.5918 1.5512 0.0406; 0.0008  0.2390 0.9753"),
        "CAT02": np.matrix("0.7328 0.4296 -0.1624;-0.7036 1.6975 0.0061; 0.0030  0.0136 0.9834"),
        "BS": np.matrix("0.8752 0.2787 -0.1539;-0.8904 1.8709 0.0195;-0.0061  0.0162 0.9899"),
        "BSPC": np.matrix("0.6489 0.3915 -0.0404;-0.3775 1.3055 0.0720;-0.0271  0.0888 0.9383")}

    if cat_model not in dict_cat_M_array.keys():
        raise Exception(f"CAT model not implemented. Please, select : {dict_cat_M_array.keys()}")

    M = dict_cat_M_array[cat_model] # CATs model array
    
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

    D = np.diag([d1,d2,d3])
    #print(D)
    #D2 = np.matrix([[d1,0,0],[0,d2,0],[0,0,d3]])
    #print(D2)

    S1 = np.dot(M, XYZ_data.T)
    #print(S1.shape)
    S2 = np.dot(D, S1)
    #print(S2.shape)
    XYZ_D65_data = np.dot(MI, S2)
    #print(XYZ_D65_data.T.shape)

    # reshape
    #XYZ_D65_data = np.reshape(XYZ_D65_data.T, (col,row,channels))
    XYZ_D65_data = np.array(XYZ_D65_data.T).reshape(col,row,channels)

    #S1 = np.einsum('ij,...j', M, XYZ_data) 
    #S2 = np.einsum('ij,...j', D, S1) 
    #XYZ_D65_data = np.einsum('ij,...j', MI, S2) 

    return XYZ_D65_data











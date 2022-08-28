import math
import numpy as np

import coolpi.auxiliary.common_operations as cop
import coolpi.image.raw_operations as rwo

# Auxiliary functions

def get_max_rgb_values(rgb_data):
    '''
    Function to get the RGB max values

    Parameter:
        rgb_data      numpy.array    RGB data
    
    Returns:
        max_values    list           r,g,b,g max values as list
    
    '''

    r_max, g_max, b_max = rgb_data[:,:,0].max(), rgb_data[:,:,1].max(), rgb_data[:,:,2].max()
    if rgb_data.shape[2] == 4:
        g_max_2 = rgb_data[:,:,3].max()
        max_values = [r_max, g_max, b_max, g_max_2]
    else:
        max_values = [r_max, g_max, b_max, g_max]

    return max_values

def get_average_rgb_values(rgb_data):
    '''
    Function to get the RGB average values

    Parameter:
        rgb_data      numpy.array    RGB data
    
    Returns:
        avg_values    list           computed r,g,b,g average values as list
    
    '''
    # from images where the colorchecker has been removed, min value =-1
    rgb_avg =  [np.average(rgb_data[:,:,0][np.where(rgb_data[:,:,0]>0)]), np.average(rgb_data[:,:,1][np.where(rgb_data[:,:,1]>0)]), np.average(rgb_data[:,:,2][np.where(rgb_data[:,:,2]>0)])] if np.amin(rgb_data)<0 else [np.average(rgb_data[:,:,0]), np.average(rgb_data[:,:,1]), np.average(rgb_data[:,:,2])]
    
    if rgb_data.shape[2] == 4:
        g_avg_2 = np.average(rgb_data[:,:,3][np.where(rgb_data[:,:,3]>0)]) if np.amin(rgb_data)<0 else np.average(rgb_data[:,:,3])
        avg_values = [rgb_avg[0], rgb_avg[1], rgb_avg[2], g_avg_2]
    else:
        avg_values = [rgb_avg[0], rgb_avg[1], rgb_avg[2], rgb_avg[1]]
    
    return avg_values

#corners_colourchecker = {"TopLeft":[2191.69,3735.09], "BottomRight":[2945.04,2350.83]}
def mask_colourchecker(rgb_data, corners_colourchecker, mask_value=-1):
    '''
    Function to remove a colorchecker from an image

    Parameters:
        rgb_data                 numpy.array         RGB data
        corners_colourchecker    dict                Colourchecker corners as dict. 
                                                     {"TopLeft":[2191.69,3735.09], "BottomRight":[2945.04,2350.83]}
        mask_value               int                 Mask value. Default: -1.

    Returns:
        rgb_mask                 numpy.array         The new RGB data without the colourchecker
    
    '''

    rgb_mask = rgb_data.copy()
    x1, y1 = corners_colourchecker["TopLeft"]
    x2, y2 = corners_colourchecker["BottomRight"]
    
    rgb_mask[y1:y2, x1:x2, :] = mask_value
    
    return rgb_mask

# Compute white-balance multiliers

def compute_wb_multipliers(r_grey, g_grey, b_grey):
    '''
    Funtion to compute the white balance multipliers

    Parameters:
        r_grey, g_grey, b_grey    float    RGB data of the grey/white patche (extracted from a colourchecker, 
                                           or estimated using a white balance algorithm).
    
    Returns:
        wb_multipliers            list     Computed wb multipliers

    '''

    # From grey/white patche (colourchecker)
    # Estimated using wb algorithm

    r_mult, g_mult, b_mult = 1/r_grey, 1/g_grey, 1/b_grey
    r_mult, g_mult, b_mult = r_mult/g_mult, g_mult/g_mult, b_mult/g_mult
    wb_multipliers = [r_mult, g_mult, b_mult, g_mult]
    return wb_multipliers

# Estimation of white balance multipliers using different algorithms

def estimate_white_balance_multipliers(rgb_data, method="GreyWorld"):
    methods_implemented = ["Average", "GreyWorld", "MaxWhite", "Retinex"]
    if method not in methods_implemented:
        raise Exception("White balance algorithm not implemented")

    if method=="Average":
        r_avg, g_avg, b_avg, _ = get_average_rgb_values(rgb_data)
        estimated_wb_multipliers = compute_wb_multipliers(r_avg, g_avg, b_avg)
    elif method=="GreyWorld":
        estimated_wb_multipliers = compute_grey_world_multipliers_Nikitenko(rgb_data)
    elif method=="MaxWhite":
        estimated_wb_multipliers = compute_max_white_multipliers(rgb_data)
    elif method=="Retinex":
        estimated_wb_multipliers = compute_retinex_multipliers(rgb_data)
    else:
        raise Exception("Method not implemented")
    return estimated_wb_multipliers


# Auziliar functions

# A. Grey world

def compute_grey_world_multipliers_Nikitenko(rgb_data):
    '''     
    Function to compute the Grey world gain multipliers using the Nikitenko method
    
    It assumes that the average intensities of the red, green, and blue channels should be equal
    
    Nikitenko, D., Wirth, M., & Trudel, K. 2008. Applicability of White-Balancing Algorithms to 
    Restoring Faded Colour Slides: An Empirical Evaluation. Journal of Multimedia, 3(5), 9-18.
        
    II. Algorithms. A. Grey World
    
    Parameters:
        rgb_data                np.array    RGB image values 
    Returns:
        grey_world_multipliers  list        Grey world computed multipliers
    
    '''
    
    rgb_avg_values = get_average_rgb_values(rgb_data)
    
    g_avg = rgb_avg_values[1] if rgb_data.shape[2] == 3 else (rgb_avg_values[1]+rgb_avg_values[3])/2
    
    r_gain = g_avg/rgb_avg_values[0]
    b_gain = g_avg/rgb_avg_values[2]
    
    grey_world_multipliers = [r_gain, 1.0, b_gain, 1.0] if rgb_data.shape[2] == 3 else [r_gain, g_avg/rgb_avg_values[1], b_gain, g_avg/rgb_avg_values[3]]
    
    return grey_world_multipliers

def compute_k_grey_world_multipliers(rgb_data):
    
    rgb_avg_values = get_average_rgb_values(rgb_data)
    
    k =(rgb_avg_values[0]+rgb_avg_values[1]+rgb_avg_values[2])/3 if rgb_data.shape[2] == 3 else (rgb_avg_values[0]+rgb_avg_values[1]+rgb_avg_values[2]+rgb_avg_values[3])/4
    
    kr = k/rgb_avg_values[0]
    kg = k/rgb_avg_values[1]
    kb = k/rgb_avg_values[2]
    
    grey_world_multipliers = [kr/kg, kg/kg, kb/kg, kg/kg] # normalised with respect to the green channel
        
    return grey_world_multipliers

# B. Max White

def compute_max_white_multipliers(rgb_data):
    '''     
    Function to compute the Max White multipliers
    
    '''
    
    n_bits = rwo.get_bits_image(rgb_data)
    max_white_point = math.pow(2, n_bits)

    r_max, g_max, b_max, g_max_ = get_max_rgb_values(rgb_data)
    r_mult, g_mult, b_mult = max_white_point/r_max, max_white_point/g_max, max_white_point/b_max
    
    gain_multipliers = [r_mult/g_mult, g_mult/g_mult, b_mult/g_mult, g_mult/g_mult]
    return gain_multipliers

# C. Retinex

def compute_retinex_multipliers(rgb_data):
    '''     
    Function to compute the Retinex gain multipliers
    
    Parameters:
        rgb_data                np.array    RGB image values 
    Returns:
        retinex_multipliers     list        Grey world computed multipliers
    
    '''

    rgb_max_values = get_max_rgb_values(rgb_data)

    r_mult = rgb_max_values[1]/rgb_max_values[0]
    b_mult = rgb_max_values[1]/rgb_max_values[2]

    retinex_multipliers = [r_mult, 1.0, b_mult, 1.0]
        
    return retinex_multipliers

# WB algorithms

def grey_world_algorithm(rgb_data, method = "Nikitenko"):
    '''
    Function to apply the Grey World algorithm (GW)
    
    It assumes that the average intensities of the red, green, and blue channels should be equal.

    Two options implemented: 

    Nikitenko, D., Wirth, M., & Trudel, K. 2008. Applicability of White-Balancing Algorithms to 
    Restoring Faded Colour Slides: An Empirical Evaluation. Journal of Multimedia, 3(5), 9-18.
    
    II. Algorithms. A. Grey world
    
    k multipliers
    

    Parameters:
        rgb_data              np.array    RGB image values 
        method                str         Method to compute GW multipliers. Default "Nikitenko"
    Returns:
        rgb_grey_world_data   np.array    RGB grey world data

    '''

    implmented_methods = ["Nikitenko", "k"]
    
    if method not in implmented_methods:
        raise Exception("The method introduced for computing the gain multipliers is not a valid method: {implemented_methods}")

    grey_world_multipliers = compute_grey_world_multipliers_Nikitenko(rgb_data) if method == "Nikitenko" else compute_k_grey_world_multipliers(rgb_data)
    rgb_grey_world_data = apply_wb_multipliers_to_rgb_image(rgb_data, grey_world_multipliers)
    return rgb_grey_world_data    


def max_white_algorithm(rgb_data):
    '''
    Function for the Max White algorithm (MWA)
    
    MWA assumes that the maximum values of the RGB channels are white and the brightest white point should 
    correspond to 1 (rgb in range [0-1], or 2^n, for n bits per channel)

    Nikitenko, D., Wirth, M., & Trudel, K. 2008. Applicability of White-Balancing Algorithms to 
    Restoring Faded Colour Slides: An Empirical Evaluation. Journal of Multimedia, 3(5), 9-18.
    
    II. Algorithms. B. Max White
    
    Parameters:
        rgb_data              np.array    RGB image values 
    Returns:
        rgb_data_max_white    np.array    RGB max white data

    '''

    gain_multipliers = compute_max_white_multipliers(rgb_data)
    rgb_data_max_white = apply_wb_multipliers_to_rgb_image(rgb_data, gain_multipliers)
    return rgb_data_max_white

def retinex_algorithm(rgb_data):
    '''
    Function for the Retinex algorithm (MWA)
    
    Nikitenko, D., Wirth, M., & Trudel, K. 2008. Applicability of White-Balancing Algorithms to 
    Restoring Faded Colour Slides: An Empirical Evaluation. Journal of Multimedia, 3(5), 9-18.
    
    II. Algorithms. C. Retinex
    
    Parameters:
        rgb_data              np.array    RGB image values 
    Returns:
        rgb_data_max_white    np.array    RGB max white data
    
    '''
    
    retinex_multipliers = compute_retinex_multipliers(rgb_data)
    rgb_data_retinex = apply_wb_multipliers_to_rgb_image(rgb_data, retinex_multipliers)
    return  rgb_data_retinex

# Combined graw word and Retinex

def solve_linear_system(x, y):
    '''
    Solve a linear matrix equation, or system of linear scalar equations using NumPy
    
    y = Ax
    
    Parameters:
        x              np.array    Coefficient array with independent variable data
        y              np.array    Ordinate or "dependent variable" values
    Returns:
        coeff          np.array    Solution to the system y = Ax
    
    '''
    
    coeff = np.linalg.solve(x,y)
    return coeff

 
def combined_grey_world_and_retinex_algorithm(rgb_data):
    '''
    
    Combined Grey world and Retinex algorithm
    
    Lam, E. Y. 2005. Combining gray world and retinex theory for automatic white balance 
    in digital photography. In Proceedings of the Ninth International Symposium on Consumer 
    Electronics (ISCE), 134-139.

    Parameters:
        rgb_data               np.array    RGB image values 
    Returns:
        rgb_data_gw_retinex    np.array    RGB Grey word and retinex data
    
    '''
    
    rgb_data_gw_retinex = rgb_data.copy()
    
    sum_r = np.sum(rgb_data[:,:,0])
    sum_r2 = np.sum(rgb_data[:,:,0]**2)     
    max_r = rgb_data[:,:,0].max()
    max_r2 = math.pow(max_r, 2)
    
    sum_g = np.sum(rgb_data[:,:,1])
    max_g = rgb_data[:,:,1].max()

    sum_b = np.sum(rgb_data[:,:,2])
    sum_b2 = np.sum(rgb_data[:,:,2]**2)
    max_b = rgb_data[:,:,2].max()
    max_b2 = math.pow(max_b, 2)

    x_1 = np.array([[sum_r2, sum_r], [max_r2, max_r]])
    y = np.array([sum_g, max_g])

    coeff_1 = solve_linear_system(x_1,y)
    
    x_2 = np.array([[sum_b2, sum_b], [max_b2, max_b]])
    
    coeff_2 = solve_linear_system(x_2, y)

    rgb_data_gw_retinex[:,:,0] = (rgb_data[:,:,0]**2)*coeff_1[0] +  rgb_data[:,:,0]*coeff_1[1]     
    rgb_data_gw_retinex[:,:,2] = (rgb_data[:,:,2]**2)*coeff_2[0] +  rgb_data[:,:,2]*coeff_2[1] 
    
    return rgb_data_gw_retinex

# D. Histogram Equalization + Max White

def histogram_equalization(rgb_data):
    '''
    Function for the histogram equalization of the RGB values of an image.
    
    The brightest colour should be white, the darkest colour should be black.
    Auto levels: Rescale each channel's histogram to span the full range.
    
    Nikitenko, D., Wirth, M., & Trudel, K. 2008. Applicability of White-Balancing Algorithms to 
    Restoring Faded Colour Slides: An Empirical Evaluation. Journal of Multimedia, 3(5), 9-18.
    
    II. Algorithms. D. Stretch (only histogram equalization)
    
    Parameters:
        rgb_data            np.array    RGB image values 
    Returns:
        rgb_data_hist_eq    np.array    RGB histogram equalization data

    '''
        
    # split channels
    r, g, b = rgb_data[:,:,0], rgb_data[:,:,1], rgb_data[:,:,2]
    # min rgb value
    r_min, g_min, b_min = r.min(), g.min(), b.min()
    # histo equalization
    r_new = r - r_min
    g_new = g - g_min
    b_new = b - b_min
    # new data
    rgb_data_hist_eq = rgb_data.copy()
    rgb_data_hist_eq[:,:,0] = r_new
    rgb_data_hist_eq[:,:,1] = g_new
    rgb_data_hist_eq[:,:,2] = b_new
    
    return rgb_data_hist_eq


# To apply white-balance multiliers

def apply_wb_multipliers_to_rgb_image(rgb_data, wb_list_gain_factors):
    '''
    Function to apply the input white balance gain factors to an image
    
    Parameters:    
        rgb_data               np.array     RGB data
        wb_list_gain_factors   list         list with the white balance multipliers
                                            r_mult, g_mult, b_mult, g_mult_2 (for RGBG images)
        
    Returns:       
        rgb_data_wb            np.array     RGB white balance data
        
    '''
    # using arrays
    Krgb = np.diag(wb_list_gain_factors)[0:rgb_data.shape[2],0:rgb_data.shape[2]]
    rgb_data_wb = np.einsum('ij,...j', Krgb, rgb_data) 

    return rgb_data_wb

# same result
def apply_wb_multipliers_to_rgb_image_(rgb_data, wb_list_gain_factors):
    '''
    Function to apply the input white balance gain factors to an image
    
    Parameters:    
        rgb_data               np.array     RGB data
        wb_list_gain_factors   list         list with the white balance multipliers
                                            r_mult, g_mult, b_mult, g_mult_2 (for RGBG images)
        
    Returns:       
        rgb_data_wb            np.array     RGB white balance data
        
    '''

    rgb_data_wb = np.zeros((rgb_data.shape[0], rgb_data.shape[1], rgb_data.shape[2]))
    
    wb_list_gain_factors = [1,1,1,1] if wb_list_gain_factors==None else wb_list_gain_factors
    
    rgb_data_wb[:,:,0] = rgb_data[:,:,0]*wb_list_gain_factors[0]
    rgb_data_wb[:,:,1] = rgb_data[:,:,1]*wb_list_gain_factors[1]
    rgb_data_wb[:,:,2] = rgb_data[:,:,2]*wb_list_gain_factors[2]
    
    if rgb_data.shape[2] == 4:
        rgb_data_wb[:,:,3] = rgb_data[:,:,3]*wb_list_gain_factors[3]

    return rgb_data_wb

# old functions
def compute_raw_multipliers(RGB_to_XYZ):

    # 2020, Rowlands, A.

    MI = cop.compute_inverse_array(RGB_to_XYZ)
    RGBwpp = np.dot(MI, np.array([1,1,1])) # WPP
    r_mult = 1/RGBwpp[0]
    g_mult = 1/RGBwpp[1]
    b_mult = 1/RGBwpp[2]
    return [r_mult/g_mult, g_mult/g_mult, b_mult/g_mult]
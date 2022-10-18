import cv2
import math
import numpy as np
import rawpy

import coolpi.auxiliary.common_operations as cop
import coolpi.image.raw_colour_correction as rcc
import coolpi.image.raw_operations as rwo

# Automatic RAW Image Processing using rawpy (without colour correction)

def automatic_raw_image_processing(path_raw_img, **krawargs):
    ''' 
    Function for the automatic processing of a RAW image (using rawpy.postprocess).
    
    Dcraw decoder using rawpy package.

    Without colour-correction.
        
    Default arguments are used for image processing. However, custom parameters can be introduced as optional krawargs.
    demosaicing algoritm AHD, full size, without noise reduction, white balance, sRGB 8 bits.

    Parameters:
        path_raw_img            os        path of the RAW image
        krawargs                dict      custom arguments, optional.

    Returns:
        processed_rgb_array     np.array  numpy array with the automatic rgb processed values
    
    '''
    
    # rawpy tested default parameters
    default_kargs = dict(demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD, half_size=False, 
        four_color_rgb=False, dcb_iterations=0, dcb_enhance=False, fbdd_noise_reduction=rawpy.FBDDNoiseReductionMode.Off,
        user_flip=None,
        noise_thr=0, median_filter_passes=0, use_camera_wb=False, use_auto_wb=False, user_wb=None,
        output_color=rawpy.ColorSpace.sRGB, output_bps=8, user_black=None, user_sat=None, 
        no_auto_bright=False, auto_bright_thr=0.01, adjust_maximum_thr=0.75,bright=1.0, highlight_mode=rawpy.HighlightMode.Clip, 
        exp_shift=1, exp_preserve_highlights=0.0, no_auto_scale=False, gamma=(2.222, 4.5), # default BT.709
        chromatic_aberration=(1,1), bad_pixels_path=None) # user_flip=None Fujifilm has 45 flip set default
    
    #krawargs = default_kargs if krawargs == None else krawargs
    default_kargs.update(krawargs)

    with rawpy.imread(path_raw_img) as raw:
        processed_rgb_array = raw.postprocess(**default_kargs) # is preferred to have control of the parameters
        #processed_rgb_array = raw.postprocess() # default

    return processed_rgb_array


# RAW Colour Image Procesing Workflow

# [0]

def get_raw_attributes(path_raw_img):
    ''' 
    Function to extract RAW attributes of a RAW image using rawpy (based on LibRaw)
        
    For further details, please refer to the rawpi documentation
    Rawpy API documentation: https://letmaik.github.io/rawpy/api/rawpy.RawPy.html
    
    Note: The "raw_image" data may contain a rotation due to the camera's sensor (i.e. Fujifilm IS PRO).
    We recommend obtaining the raw data using rawpy, since it is possible to undo the rotation automatically.
    The original "raw_image" is stored for computational use if its required.

    Parameter:
        path_raw_img      os       path of the RAW image
        
    Returns:
        raw_attributes    dict     RAW image attributes extracted using rawpy
     
    '''
    
    raw_attributes = {}
    with rawpy.imread(path_raw_img) as raw:
        raw_attributes["black_level_per_channel"] = raw.black_level_per_channel # Per-channel black level correction

        #white_level_data = raw.camera_white_level_per_channel

        # maybe it is not required, only "white_level"
        #if isinstance(white_level_data, type(None)):
        #    raw_attributes["camera_white_level_per_channel"] = float(np.amax(raw.raw_image)) #Per-channel saturation levels read from raw file metadata
        #elif isinstance(white_level_data, list):
        #    raw_attributes["camera_white_level_per_channel"] = float(white_level_data[0])
        #elif isinstance(white_level_data, np.array):
        #    raw_attributes["camera_white_level_per_channel"] = float(np.amax(white_level_data))

        raw_attributes["camera_whitebalance"] = raw.camera_whitebalance # White balance coefficients (as shot)
        raw_attributes["colour_desc"] = raw.color_desc # String description of colours numbered from 0 to 3 (RGBG,RGBE,GMCY, or GBTG). 
        #raw_attributes["colour_matrix"] = raw.color_matrix # Colour matrix
        raw_attributes["daylight_whitebalance"] = raw.daylight_whitebalance # White balance coefficients for daylight (daylight balance). 
        raw_attributes["num_colours"] = raw.num_colors # Number of colours (int)
        
        try:
            raw_attributes["raw_colours"] = raw.raw_colors # An array of colour indices for each pixel in the RAW image
        except:
            raw_attributes["raw_colours"] = None # For SIGMA FOVEON (otherwise it would give an error)

        raw_attributes["raw_image"] = raw.raw_image # raw rgb data array without processing 
                                                    # PROBLEM WITH FLIP image, i.e. Fujifilm
                                                    # If processed with rawpy, the data can be obtained by automatically undoing the rotation.
        raw_attributes["raw_image_visible"] = raw.raw_image_visible # without margin (same dim)
        raw_attributes["raw_pattern"] = raw.raw_pattern # The smallest possible Bayer pattern of this image
        raw_attributes["xyz_cam_matrix"] = raw.rgb_xyz_matrix # XYZ to CAM conversion matrix
        raw_attributes["tone_curve"] = raw.tone_curve # Camera tone curve
        raw_attributes["white_level"] = raw.white_level # Level at which the raw pixel value is considered to be saturated. 2^n (n=14 bits)
        raw_attributes["raw_image_size"] = [raw.sizes.raw_height, raw.sizes.raw_width]
        raw_attributes["processed_image_size"] = [raw.sizes.height, raw.sizes.width]
        #print(raw.raw_color(0,0)) # Return colour index for the given coordinates relative to the full RAW size
        #print(raw.raw_value(0,0)) # Return RAW value at given position relative to the full RAW image

    return raw_attributes


# [1] RAW RGB demosaiced image

# COMMON WORKFLOW: To obtain raw_data as close as sensor as posible

# Method A: "raw_image"

def get_raw_image_demosaiced_visible_subtrack_black(path_raw_img, shape_visible):
    '''
    Function to get the raw_image as RAW RGB image

    Steps:
    raw_image --> extract visible --> demosaicing (undo bayer pattern) ---> subtrack black

    Parameters:
        path_raw_img                     os           path of the raw image
        shape_visible                    list         Shape visible area [col, row] 

    Returns:
        raw_demosaiced_subtrack_black     np.array    numpy array with the RAW RGB data

    '''
    
    raw_attributes = get_raw_attributes(path_raw_img)
    raw_image_data = get_raw_image_single_shannel_data(path_raw_img)
    raw_image_visible = rwo.extract_image_visible(raw_image_data, shape_visible)

    if len(raw_image_visible.shape)==2:
        raw_pattern = raw_attributes["raw_pattern"]
        colour_description = raw_attributes["colour_desc"]
        indexes_per_channel = get_bayer_pattern_indexes_per_channel(colour_description, raw_pattern)

        num_colours = num_colours = raw_attributes["num_colours"]
        raw_demosaiced_half = undo_bayer_pattern_demosaicing_half(raw_image_visible, indexes_per_channel, num_colours)
    
        raw_demosaiced = rwo.full_size_image(raw_demosaiced_half)

    # test
    else: # FOVEON image, demosaicing not required
        raw_demosaiced = raw_image_visible

    black_level_per_channel = raw_attributes["black_level_per_channel"]
    raw_demosaiced_subtrack_black = subtract_black_level_single_channel(raw_demosaiced, black_level_per_channel)

    return np.array(raw_demosaiced_subtrack_black, dtype = np.double)


# Method B: "postprocess"

def get_raw_data_using_postprocess_rawpy(path_raw_img, **krawargs):
    ''' 
    Function to extract the RAW values of a RAW image with minimum processing
    
    Dcraw decoder using rawpy package
        
    Note: The default_args used for this function are configured to obtain the RAW RGB data as close as possible 
    to the data captured by the sensor. For computational purpuses we need a demosaiced linear image in 16 bits.
    If user's requirements are different, the desired krawargs parameters can be entered as function optional arguments.
    
    rawpy params documentation: https://letmaik.github.io/rawpy/api/rawpy.Params.html# 
    
    Parameters:
        path_raw_img      os           path of the RAW image
        krawargs          dict      custom arguments, optional.

    Returns:
        raw_rgb_array     np.array     RAW RGB data: subtract black, demosaiced half, raw colour space, 16 bits
    
    '''

    # half size, without interpolation
    default_kargs = dict(half_size=True, four_color_rgb = False, fbdd_noise_reduction = rawpy.FBDDNoiseReductionMode(0),         
        use_camera_wb = False, use_auto_wb = False, user_wb = None, output_color = rawpy.ColorSpace(0), 
        output_bps = 16, no_auto_scale = True, no_auto_bright = True, highlight_mode = rawpy.HighlightMode(1), 
        gamma = (1,1), chromatic_aberration = (1,1), bad_pixels_path = None) # demosaic_algorithm = rawpy.DemosaicAlgorithm(3), user_flip=None, median_filter_passes = 0, 
        
    default_kargs.update(krawargs)
    
    with rawpy.imread(path_raw_img) as raw:
            raw_rgb_array = raw.postprocess(**default_kargs)

    return raw_rgb_array

def compute_raw_demosaiced_visible_using_postprocess_rawpy(path_raw_img, shape_visible):
    ''' 
    Function to obtain the full demosaiced image using postprocess
    
    Parameters:
        path_raw_img               os           path of the RAW image
        shape_visible              list         Shape visible area [col, row] 

    Returns:
        raw_demosaiced_visible     np.array     RAW RGB data: full demosaiced, visible, subtract black, 16 bits
    
    '''

    raw_demosaiced_half = get_raw_data_using_postprocess_rawpy(path_raw_img) # demosaiced, subtract black corrected
    
    #print(raw_demosaiced_half.shape)
    #rwo.show_rgb_as_bgr_image(raw_demosaiced_half, "matplotlib")

    # check if the raw_image is single chanel / trichromatic
    raw_attributes = get_raw_attributes(path_raw_img) # get the attributes from the raw file using rawpy
    raw_image = raw_attributes["raw_image"]
    raw_image_shape = raw_image.shape
    
    raw_demosaiced = rwo.full_size_image(raw_demosaiced_half) if len(raw_image_shape)==2 else raw_demosaiced_half
  
    #print(raw_demosaiced.shape)
    #rwo.show_rgb_as_bgr_image(raw_demosaiced, "matplotlib")

    col, row, _ = raw_demosaiced.shape
    col_vis, row_vis = shape_visible[0], shape_visible[1]

    if col_vis<col and row_vis<row:
        raw_demosaiced_visible = rwo.extract_image_visible(raw_demosaiced, shape_visible)
    else:
        raw_demosaiced_visible = raw_demosaiced

    return np.array(raw_demosaiced_visible, dtype = np.double) 

# Note: Since the results are identical using both methods (data from raw_image, or postprocessing), 
# we will use the rawpy postprocess function: in this way it is not necessary to take into account the sensor rotation (flip)
# of some cameras (i.e. Fujifilm). We obtain the raw data automatically.


# [2] Compute / Estimate WB multipliers (using white_balance.py)


# [3] Apply WB multipliers to the RAW RGB demosaiced image


# RAW Image processing: STEB by STEP workflow from raw_image data 

# OPTION 1

# STEP 1: Get raw_image from metadata using rawpy
def get_raw_image_single_shannel_data(path_raw):
    with rawpy.imread(path_raw) as raw:
        raw_image_single_channel_data = np.array(raw.raw_image, dtype=np.double) # raw_image single data channel
    return raw_image_single_channel_data

# STEP 2: Subtract black level
def subtract_black_level_single_channel(raw_image_data, black_level_per_channel):
    black_level_per_channel = black_level_per_channel[0] if isinstance(black_level_per_channel, list) else black_level_per_channel # avoid negative values
    raw_image_subtract_black_level = raw_image_data.copy()
    raw_image_subtract_black_level = np.clip((raw_image_subtract_black_level - black_level_per_channel), 0, math.pow(2,14)) # If image in range [0,1] it works as well
    return raw_image_subtract_black_level

# STEP 3: normalised [0-1]
def normalise_black_level(raw_image_subtract_black_level, white_level, black_level_per_channel):
    black_level_per_channel = black_level_per_channel[0] if isinstance(black_level_per_channel, list) else black_level_per_channel # avoid negative values
    raw_image_normalised = raw_image_subtract_black_level/(white_level-black_level_per_channel)
    return raw_image_normalised

# this function is no longer required
def raw_rgb_linearization_(raw_rgb_data, black_level, white_level):
    '''
    Function for the linearization of RAW RGB image data 

    Parameters:    
        raw_rgb_data        np.array      RAW RGB data
        black_level         int           Black level of RAW image (from raw_attributes)
        white_level         int           White level of RAW image (from raw_attributes)
    
    Returns:       
        raw_linearizated    np.array      RAW RGB subtract black level 
    
    '''
    
    #raw_rgb_data = np.array(raw_rgb_data, dtype = np.double) # type conversion to double to avoid computational errors
    raw_linearizated = raw_rgb_data/(white_level - black_level)
    return raw_linearizated


# STEP 4: White-balance (to single channel)

def get_bayer_pattern_indexes_per_channel(colour_description, raw_pattern):
    colours = np.frombuffer(colour_description, dtype=np.byte)
    bayer_pattern = np.array(raw_pattern)
    indexes_per_channel = [np.where(colours[bayer_pattern] == colours[i]) for i in range(0, len(colours))]
    return indexes_per_channel

def apply_wb_multipliers_to_single_channel_image(raw_image_normalised, wb_list_gain_factors, indexes_per_channel, num_colours):
    index_0, index_1, index_2, index_3 = [index for index in indexes_per_channel]
    white_balance = np.zeros((2, 2), dtype=np.double) 
    white_balance[index_0] = wb_list_gain_factors[0] if wb_list_gain_factors[1]==1 else wb_list_gain_factors[0]/wb_list_gain_factors[1] # wb_list_gain_factors normalised to green channel 
    white_balance[index_1] = wb_list_gain_factors[1] if wb_list_gain_factors[1]==1 else wb_list_gain_factors[1]/wb_list_gain_factors[1]
    white_balance[index_2] = wb_list_gain_factors[2] if wb_list_gain_factors[1]==1 else wb_list_gain_factors[2]/wb_list_gain_factors[1]
    if num_colours == 4:
        white_balance[index_3] = wb_list_gain_factors[3] if wb_list_gain_factors[1]==1 else wb_list_gain_factors[3]/wb_list_gain_factors[1]
    white_balance = np.tile(white_balance, (raw_image_normalised.shape[0]//2, raw_image_normalised.shape[1]//2))
    raw_image_wb = raw_image_normalised * white_balance
    return raw_image_wb # single channel image

# STEP 5: Demosaicing half size
def undo_bayer_pattern_demosaicing_half(raw_image, indexes_per_channel, num_colours):
    '''
    Function to undo the Bayer Pattern of a RAW image (downsample / half sice)
    
    '''

    index_0, index_1, index_2, index_3 = [index for index in indexes_per_channel]
    raw_demosaiced_half = np.zeros((raw_image.shape[0]//2, raw_image.shape[1]//2, num_colours))
    raw_demosaiced_half[:,:,0] = raw_image[index_0[0][0]::2, index_0[1][0]::2]
    raw_demosaiced_half[:,:,1] = (raw_image[index_1[0][0]::2, index_1[1][0]::2] + raw_image[index_1[0][1]::2, index_1[1][1]::2]) / 2 if num_colours == 3 else raw_image[index_1[0][0]::2, index_1[1][0]::2]
    raw_demosaiced_half[:,:,2] = raw_image[index_2[0][0]::2, index_2[1][0]::2]
    if num_colours == 4:
        raw_demosaiced_half[:,:, 3] = raw_image[index_3[0][0]::2, index_3[1][0]::2]
    
    return raw_demosaiced_half


# STEP 6: Colour transform

# Esto esta mal
def compute_color_transform(rgb_data_demosaic_interpolate, rgb_xyz_matrix):
    
    col, row, n_channels = rgb_data_demosaic_interpolate.shape[0], rgb_data_demosaic_interpolate.shape[1], rgb_data_demosaic_interpolate.shape[2] 

    # Camera RGB - XYZ conversion matrix (between CIE XYZ and camera RGB (device dependent))    
    # [R,G,B]t = M1*[Y,Y,Z]t
    #M1 = np.array(raw_attributes["rgb_xyz_matrix"], dtype = np.double) # Camera RGB - XYZ conversion matrix
    M1 = np.array(rgb_xyz_matrix, dtype = np.double) # Camera RGB - XYZ conversion matrix
    M1 = M1[0:n_channels,:] if n_channels == 3 else M1
    
    # Theroretical transform array between sRGB and CIE XYZ (D65 illuminant)
    # [X,Y,Z]t = M2*[sR,sB,sG]t
    M2 = np.array([[0.4124, 0.3576, 0.1805],[0.2126, 0.7152, 0.0722],[0.0193, 0.1192, 0.9505]], dtype = np.double)

    # IEC/4WD 61966-2-1: Colour Measurement and Management in Multimedia Systems and
    # Equipment - Part 2-1: Default RGB Colour Space - sRGB

    # sRGB to camera RGB color space matrix transform
    # [R,G,b]t = M1*[X,Y,Z]t = M1*M2*[sR,sG,sB]t = M*[sR,SG,sB]t
    M = np.dot(M1, M2)
    N = np.tile(np.sum(M, 1), (3, 1)).transpose() # Normalised, White point preservation
    
    M = M / N
    
    # White point preservation
    # Finlayson, G. D., & Drew, M. S. (1997, January). White-point preserving color correction. 
    # In Color and Imaging Conference(Vol. 1997, No. 1, pp. 258-261). Society for Imaging Science and Technology.

    # Sumner, R. (2014). Processing raw images in matlab. Department of Electrical Engineering, 
    # University of California Sata Cruz.
    
    # Compute M-1 inv/pinv array ---> transform between camera device dependent RGB into sRGB
    M_inverse = cop.compute_inverse_array(M)
    
    # raw rgb to XYZ. rgb image in [0,1] range
    # numpy einsum ---> faster and more memory-efficiently 
    # ij matrix multiplication
    # ...j
    # linear sRGB
    image_sRGB = np.einsum('ij,...j', M_inverse, rgb_data_demosaic_interpolate)  # one step
    
    # nonlinear sRGB [IEC/4WD 61966-2-1]
    image_nonlinear_sRGB = compute_nonlinear_sRGB(image_sRGB) # direct

    # sRGB to XYZ
    #M3 = np.array([[3.2406, -1.5372, -0.4986],[-0.9689, 1.8758, 0.0415],[0.0557, -0.2040, 1.0570]], dtype = np.double)
    #image_XYZ = np.einsum('ij,...j', M3, image_sRGB)
    #save_rgb_array_as_image(image_XYZ, "XYZ.tif")
    
    # using inverse
    M1_inverse = cop.compute_inverse_array(M1)
    N1= np.tile(np.sum(M1_inverse, 1), (3, 1)).transpose() # Normalised, White point preservation
    M1_inverse = M1_inverse / N1
    
    image_XYZ = np.einsum('ij,...j', M1_inverse, rgb_data_demosaic_interpolate) # CAM RGB to CIE XYZ
 
    # i'm not sure about this last step
    M2_inverse = cop.compute_inverse_array(M2)
    N2= np.tile(np.sum(M2_inverse, 1), (3, 1)).transpose() # Normalised, White point preservation
    M2_inverse = M2_inverse / N2
    
    image_sRGB_L = np.einsum('ij,...j', M2_inverse, image_XYZ) # CIE XYZ to sRGB linear
    
    image_nonlinear_sRGB_L = compute_nonlinear_sRGB(image_sRGB_L) # final sRGB nonlinear
    
    return image_nonlinear_sRGB_L

# gamma
def compute_nonlinear_sRGB(sRGB_array):
    # IEC/4WD 61966-2-1: Colour Measurement and Management in Multimedia Systems and
    # Equipment - Part 2-1: Default RGB Colour Space - sRGB
    nonlinear_sRGB = sRGB_array.copy()
    i = nonlinear_sRGB < 0.0031308
    j = np.logical_not(i)
    nonlinear_sRGB[i] = 12.92 * nonlinear_sRGB[i]
    nonlinear_sRGB[j] = 1.055 * nonlinear_sRGB[j]**(1.0/2.4) - 0.055
    nonlinear_sRGB = np.clip(nonlinear_sRGB, 0, 1)
    return nonlinear_sRGB
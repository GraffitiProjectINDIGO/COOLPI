import os

import cv2
import math
import matplotlib.pyplot as plt        
import numpy as np

import coolpi.auxiliary.common_operations as cop

def bgr_to_rgb(bgr_array):
    '''
    Function for the conversion of an image in BGR (OpenCV) format to RGB using numpy
    
    Parameters:    
        bgr_array    np.array   BGR image
    
    Returns:       
        rgb_array    nd.array   RGB image
    
    '''
    
    b, g, r = np.dsplit(bgr_array, 3)
    rgb_array = np.dstack([r,g,b])

    #b, g, r = split_img_channels(bgr_array)
    #rgb_array = merge_img_channels(r,g,b)

    return rgb_array

def extract_image_visible(raw_image_data, shape_visible):
    '''
    Function to remove the margin of a RAW image to get the sensor visible area

    Parameters:    
        raw_image_data       np.array     RAW RGB data as numpy array
        shape_visible        list         Shape visible area [col, row] 

    Returns:       
        raw_image_visible    np.array     Clip image with visible area

    '''

    # visible image
    col_visible, row_visible = shape_visible[0], shape_visible[1]

    col_raw_image, row_raw_image = raw_image_data.shape[0], raw_image_data.shape[1] 
    diff_col = int((col_raw_image-col_visible)/2)
    diff_row = int((row_raw_image-row_visible)/2)
    raw_image_visible = raw_image_data[diff_col:(col_raw_image-diff_col), diff_row:(row_raw_image-diff_row)]
    return raw_image_visible
    
def full_size_image(rgb_array):
    ''' 
    Function to resize a half demosaiced image to a full size using OpenCV
    
    Parameter:
        rgb_array            np.array     RAW RGB demosaiced half size image
        
    Returns:
        rgb_resize_array     np.array     RAW RGB demosaiced full size image
    
    '''

    rgb_resize_array = cv2.resize(rgb_array, (rgb_array.shape[1]*2, rgb_array.shape[0]*2), interpolation = cv2.INTER_NEAREST)
    return rgb_resize_array

def get_bits_image(rgb_array):
    '''
    Function to get the bits of an image
    
    Parameters:    
        rgb_array           np.array    RGB data
    Returns:       
        bits_image          int         Bits
    
    '''
        
    max = np.amax(rgb_array)
    if 0<max<=1:
        bits_image = 0 # linearizated image ---> rgb values between [0-1] 
    elif 1<max<math.pow(2, 8):
        bits_image = 8
    elif 1<max<math.pow(2, 10):
        bits_image = 10
    elif 1<max<=math.pow(2, 12):
        bits_image = 12
    elif  1<max<=math.pow(2, 14):
        bits_image = 14
    elif  1<max<=math.pow(2, 16):
        bits_image = 16
    return bits_image

def load_rgb_image_openCV(path_image):
    '''
    Function to load an image using OpenCV
    
    https://docs.opencv.org/4.x/db/deb/tutorial_display_image.html
    
    Parameters:    path_image          path
    Returns:       rgb_image           RGB Image data 
    
    '''
    
    bgr_image = cv2.imread(path_image, -1) # as is
    rgb_image = bgr_to_rgb(bgr_image)

    #b, g, r = np.dsplit(bgr_image, 3)# split_img_channels(bgr_image)  # openCV reads the image as BRG
    #rgb_image = np.dstack([r, g, b]) # merge_img_channels(r,g,b)
    return rgb_image

def rgb_to_bgr(rgb_array):
    '''
    Function for the conversion of an image in RGB to BGR (OpenCV) format
    
    Parameters:    rgb_array    nd.array
    Returns:       bgr_array    nd.array
    
    '''
    
    r, g, b = np.dsplit(rgb_array, 3)# split_img_channels(bgr_array)
    bgr_array = np.dstack([b, g, r])

    #r,g,b = split_img_channels(rgb_array)
    #bgr_array = merge_img_channels(b,g,r)
    
    return bgr_array

def save_rgb_array_as_image(rgb_array, path_output_image, bits=16):
    '''
    Function to save an rgb image using OpenCV 
    
    WARNING! only for diaplay/save, not for computing!!!
    Loss of information in the digital levels of the image due to truncation (a type conversion is required)
    
    Parameters:    rgb_array              nd.array RGB image data
                   path_output_image      os path
                   show_method            method to show the image ("OpenCV", "matplotlib"). Ignored if None. Default value is None
                   bits                   bits for the output image. Default 16 

    '''
    format_image_allowed = [8, 16]
    
    if bits not in format_image_allowed:
        raise Exception("Only output images of 8 or 16 bits are allowed")
    
    # jpg only 8 bits
    file_extension = cop.get_file_extension(path_output_image)

    if file_extension in ["jpg", "jpeg", "JPG", "JPEG"] and bits==16:
        raise Exception("Output JPG/JPEG images are allowed only for 8 bits. Please, change extension to TIF")

    image_rgb_bits = np.array(rgb_array.copy(), dtype=np.double)

    bits_image = get_bits_image(image_rgb_bits)
    image_rgb_bits = image_rgb_bits/(math.pow(2,bits_image)-1) if bits_image>0 else image_rgb_bits # range [0,1]

    # to output bits
    image_rgb_bits = np.clip(image_rgb_bits*(math.pow(2,bits)-1), 0, (math.pow(2, bits)-1)) #if 0<np.amax(image_rgb_bits)<=1 else image_rgb_bits # only for linearised images

    # conversion needed
    # original is CV_64F depth, error to display using OpenCv. datatype conversion is required
    image_rgb_bits = np.uint16(image_rgb_bits) if bits==16 else np.uint8(image_rgb_bits)

    image_bgr_bits = rgb_to_bgr(image_rgb_bits)

    cv2.imwrite(path_output_image, image_bgr_bits) # options
    
def show_rgb_as_bgr_image(rgb_array, method = "OpenCV"): 
    ''' 
    Function to show a image (np.darray format) using OpenCV or matplotlib
    
    Highly recommended to use OpenCV rather than matplotlib for computing time reasons
    For jupyter notebooks, matplotlib method is recommended (to avoid notebook crash)
    
    Parameters:    rgb_array    np.darray
                   method       str    "OpenCV" or "matplotlib". Default "OpenCV"
                   
    '''
    methods_implemented = ["OpenCV", "matplotlib"]
    
    if method not in methods_implemented:
        raise Exception("Graphic method not implemented. Choose between: OpenCV or matplotlib")
    
    if method == "OpenCV":
        bgr_img = rgb_to_bgr(rgb_array) # BGR OpenCV default format
        cv2.imshow("Image", bgr_img) 
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        bits_img = get_bits_image(rgb_array)
        rgb_array_to_display = rgb_array/math.pow(2,bits_img) # [0-1] matplotlib
        plt.imshow(rgb_array_to_display)
        plt.show()

def single_channel_image_to_grey_image(raw_data_single_channel, n_channels = 3):
    '''
    Function to create a n-channel grey image from raw single channel data
    
    Parameters:    raw_data_single_channel    n.darray
                   n_channels                 number of channels, default 3
    Returns:       raw_image_grey             n_channel n.darray
    '''

    col, row = raw_data_single_channel.shape[0], raw_data_single_channel.shape[1]
    raw_image_grey = np.empty((col,row, n_channels))
    for i in range(0, n_channels):
        raw_image_grey[:,:,i] = raw_data_single_channel
    return raw_image_grey # as rgb
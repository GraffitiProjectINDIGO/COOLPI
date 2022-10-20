from importlib import resources
import json
import os

import numpy as np
import cv2

# RGB/XYZ data extraction of a coluorchecker from an image

def is_colourchecker_implemented(colourchecker_name):
    ''' 
    Function to check if the colourchecker_name is a valid colourchecker
    
    Parameters:    colourchecker_name    str    colourchecker name
    Returns:       bool
    '''
    with resources.path("coolpi.data.colourchecker.coordinates", "patches_coordinates.json") as json_path:
        chart_json = open(json_path, "r")
        colour_checker_coordinates = json.loads(chart_json.read())  

    if colourchecker_name in colour_checker_coordinates.keys():
        return True
    else:
        return False

def sort_corners_as_list(corners_dict):
    ''' 
    Function to sort the colourchecker corners coordinates
    Useful to compute the M homography matrix
    
    Parameters:    corners_dict    dict    colourchecker corners xy coordinates
    Returns:       corners_list    list    list of sorted coordinates ["TopLeft","TopRight", "BottomRight", "BottomLeft"]
    '''
    corners_id_sorted = ["TopLeft","TopRight", "BottomRight", "BottomLeft"]
    corners_list = []
    for corner in corners_id_sorted:
        corners_list.append(corners_dict[corner])
    return corners_list

def openCV_homography_method(method):
    ''''
    Funtion to check the OpenCV method to compute the M homography array
    
    Parameter:    method   str   a valid method ("RANSAC":cv2.RANSAC, "LMEDS":cv2.LMEDS, "RHO": cv2.RHO)
    '''
    methods_implemented = {"LSTSQ": 0, "RANSAC":cv2.RANSAC, "LMEDS":cv2.LMEDS, "RHO": cv2.RHO}
    if method not in methods_implemented.keys():
        method_homography = methods_implemented["LSTSQ"] # default, least squares method
    else:
        method_homography = methods_implemented[method]
    return method_homography

def compute_M_homography(src_pts, dst_pts, method = "RANSAC", threshold = 5.0):
    ''' 
    Function to compute the M homography matrix using OpenCV
    
    Parameters:    src_pts    list    corners source xy coordinates (original)
                   dst_pts    list    corners output xy coordinates (target)
    Returns:       M          np.darray   computed homography matrix
    '''
    src_pts = np.float32(src_pts).reshape(-1,1,2)
    dst_pts = np.float32(dst_pts).reshape(-1,1,2)
    
    method_homography = openCV_homography_method(method)
    threshold_homography = threshold if isinstance(threshold,float) or isinstance(threshold,int) else 5.0 # default value
        
    M, mask = cv2.findHomography(src_pts, dst_pts, method_homography, threshold_homography) # default RANSAC algorithm / threshold
    return M

def apply_M_transform(M, point):
    ''''
    Function to apply the M homography matrix to a list or np.darray of points
    
    Parameters:    M       np.darray   M homography array coefficients
                   point   list os np.darray with the input image points coordinates 
    Returns        dst     list with the transformed coordinates
    '''
    point = np.float32(point).reshape(-1,1,2)
    dst = cv2.perspectiveTransform(point, M)
    dst = list([int(dst[0][0][0]), int(dst[0][0][1])])
    return dst 

def draw_image_corners(input_image, corners_src, radius = 5, thickness = 3, color = (0,0,0.5)):
    for corner in corners_src:
        corner = (int(corner[0]), int(corner[1]))
        cv2.circle(input_image, corner, radius, color, thickness)

# col, row
def draw_image_patches(input_image, patches_xy, size_rect = 40, thickness = 3, color = (0.5,0,0)):
    half_size = int(size_rect/2)
    for patch_id, center in patches_xy.items():
        rectng = [[int(center[0])-half_size, int(center[1])-half_size], [int(center[0])+half_size, int(center[1])+half_size]]
        cv2.rectangle(input_image, (rectng[0][0], rectng[0][1]), (rectng[1][0], rectng[1][1]), color, thickness)

def draw_image_label(input_image, patches_xy, size_rect = 40, size_font = 2.5, thickness_text = 3, color_text = (0,0.5,0)):
    for patch_id, center in patches_xy.items():
        #cv2.putText(input_image, patch_id, (center[0]-int(size_rect/4),center[1]+int(size_rect/2)), fontFace = cv2.FONT_HERSHEY_PLAIN, fontScale = size_font, color = color_text , thickness = thickness_text, lineType =cv2.LINE_AA) # text
        cv2.putText(input_image, patch_id, (center[0],center[1]), fontFace = cv2.FONT_HERSHEY_PLAIN, fontScale = size_font, color = color_text , thickness = thickness_text, lineType =cv2.LINE_AA) # text

# image row, col
def crop_patch_image(input_image, patch_xy, size_rect = 40):
    half_size = int(size_rect/2)
    rectng = [[int(patch_xy[0])-half_size, int(patch_xy[1])-half_size], [int(patch_xy[0])+half_size, int(patch_xy[1])+half_size]]
    # row, col
    crop = input_image[rectng[0][1]:rectng[1][1], rectng[0][0]:rectng[1][0],:] # esto es correcto
    return crop

def get_colourchecker_patches_coordinates_as_dict(colourchecker_name):
    with resources.path("coolpi.data.colourchecker.coordinates", "patches_coordinates.json") as json_path:
        chart_json = open(json_path, "r")
        colour_checker_coordinates = json.loads(chart_json.read())  
        
    if colourchecker_name in colour_checker_coordinates.keys():
        return colour_checker_coordinates[colourchecker_name]
    else:
        return None

def compute_patches_image_coordinates(M, patches_src_xy):
    patches_dst_xy = {}
    for patch_id, center in patches_src_xy.items():
        new_center_xy = apply_M_transform(M, center)
        patches_dst_xy[patch_id] = new_center_xy
    return patches_dst_xy

def get_patches_data(input_image, patches_xy, size_rect):
    patches_data = {}
    for patch_id, patch_xy in patches_xy.items():
        crop_patch = crop_patch_image(input_image, patch_xy, size_rect)
        # compute mean for the all the pixels
        # patches_data[patch_id] = crop_patch # all pixels
        patches_data[patch_id] = crop_patch[:,:,0].mean(), crop_patch[:,:,1].mean(), crop_patch[:,:,2].mean()
        # same result using average
        #patches_data[patch_id] = np.average(crop_patch[:,:,0]), np.average(crop_patch[:,:,1]), np.average(crop_patch[:,:,2])
        # max R, G, B values
        #print("R,G,B max  = ", crop_patch[:,:,0].max(), crop_patch[:,:,1].max(), crop_patch[:,:,2].max())
        # mean
        #print("R,G,B mean = ", crop_patch[:,:,0].mean(), crop_patch[:,:,1].mean(), crop_patch[:,:,2].mean())
        # std
        #print("R,G,B std = ", crop_patch[:,:,0].std(), crop_patch[:,:,1].std(), crop_patch[:,:,2].std())
    return patches_data

def show_patch(patch_data):
    r,g,b = cv2.split(patch_data)
    bgr_patch = cv2.merge([b,g,r])
    cv2.imshow("Patch", bgr_patch)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# default rect size to 40 instead of 50 px
def get_parameters_draw(parameters_draw):
    params_draw_default = {"radius":5, "thickness":3, "color_corner": (0.5,0,0),
                           "size_rect":40, "color_rect":(0,0,0.5),
                           "size_font":2.5, "thickness_text":3, "color_text": (0,0.5,0)}
    
    if parameters_draw == None:
        parameters= params_draw_default
    else:
        parameters = {}
        for key,value in params_draw_default.items():
            try:
                param = parameters_draw[key]
                parameters[key] = param
            except:
                parameters[key] = value # default
    return parameters

# Same function to extract RGB/XYZ data from image

def patch_extraction(input_image, colourchecker_name, corners_image, patches_coordinates=None, size_rect = 40):    
    draw_patches = input_image.copy() # draw patches
    # get colourchecker coordinates
    colour_checker_coordinates = get_colourchecker_patches_coordinates_as_dict(colourchecker_name) if patches_coordinates==None else patches_coordinates
    corners_original = colour_checker_coordinates["corners"]
    # sort corners
    corners_src = sort_corners_as_list(corners_original)
    corners_dst = sort_corners_as_list(corners_image)
    # compute M
    M = compute_M_homography(corners_src, corners_dst)
    # transform coordinates
    patches_src_xy = colour_checker_coordinates["patches"] # original
    patches_dst_xy = compute_patches_image_coordinates(M, patches_src_xy)
    size_rect = 40 if size_rect==None else size_rect
    patches_data = get_patches_data(input_image, patches_dst_xy, size_rect)
    checker_coordinates = [corners_dst, patches_dst_xy]
    return  checker_coordinates, patches_data

def draw_patches(input_image, corners_dst, patches_dst_xy, parameters_draw = None):
    draw_patches = input_image.copy() # draw patches
    parameters = get_parameters_draw(parameters_draw)
    draw_image_corners(draw_patches, corners_dst, radius = parameters["radius"], thickness = parameters["thickness"], color = parameters["color_corner"])
    draw_image_patches(draw_patches, patches_dst_xy, size_rect = parameters["size_rect"], thickness = parameters["thickness"], color = parameters["color_rect"])
    draw_image_label(draw_patches, patches_dst_xy, size_rect = parameters["size_rect"], size_font = parameters["size_font"], thickness_text = parameters["thickness_text"], color_text = parameters["color_text"])
    return draw_patches

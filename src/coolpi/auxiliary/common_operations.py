import os

import math
import numpy as np

def get_file_extension(path_file):
    filename, file_extension = os.path.splitext(path_file)
    try:
        extension = file_extension.lower().split(".")[1]
    except:
        return None
    return extension

def get_dir_folders(path_dir):
    list_dir = []
    current_dir_list = os.listdir(path_dir)
    for element in current_dir_list:
        if not element.startswith('.'): # pass hidden files
            path = os.path.join(path_dir, element)
            if os.path.isdir(path):
                list_dir.append(element)
    return list_dir

def get_dir_list_file_for_extension(path_dir, list_extension):
    list_file = []
    current_dir_list = os.listdir(path_dir)
    for element in current_dir_list:
        if not element.startswith('.'): # pass hidden files
            path = os.path.join(path_dir, element)
            if os.path.isfile(path):
                ext = get_file_extension(path)
                if ext in list_extension:
                    list_file.append(element)
    return list_file

def euclidean_distance(Ax, Ay, Az):
    '''
    Function to compute the Euclidean distance between two points

    Parameters:    
        Ax, Ay, Az    float     Ax, Ay and Az difference between the two samples
    
    Returns:       
        dist           float     Euclidena distance 

    '''
    
    dist = np.sqrt(math.pow(Ax, 2) + math.pow(Ay, 2) + math.pow(Az, 2))
    return dist

def euclidean_distance_between_2D_points(x1, y1, x2, y2):
    '''
    Function to compute the Euclidean distance between two points (in 2D)

    Parameters:    
        x1, y1    float     Coordinates point 1
        x2, y3    float     Coordinates point 2
    
    Returns:       
        dist           float     Euclidena distance 

    '''

    Ax = x2-x1
    Ay = y2-y1
    dist = np.sqrt(math.pow(Ax, 2) + math.pow(Ay, 2))
    return dist

def compute_inverse_array(M):
    '''
    Function to compute the inverse of a matrix
    
    Parameters:    
        M              np.array     Input array
    Returns:       
        M_inverse      np.array     Inverse

    '''

    M_inverse = np.linalg.pinv(M) if np.linalg.det(M) == 0 else np.linalg.inv(M) # if M is a singular array, compute pseudo-inverse
    return M_inverse

def apply_optimised_dot_product(array_1, array_2):
    '''
    Function to compute the dot product between two matrices using np.einsum

    Parameters:    
        array_1         np.array     First matrix
        array_2         np.array     Second matrix

    Returns:       
        dot_product     np.array     Result of dot product
    
    '''

    dot_product = np.einsum('ij,...j', array_1, array_2)
    return dot_product

# Improve definition

def apply_norm_to_matrix(array):
    '''
    Function to compute the norm to a given array

    Parameters:    
        array           np.array     First matrix

    Returns:       
        matrix_norm     np.array     Normalised array

    '''
    
    norm = np.tile(np.sum(array, 1), (3, 1)).transpose()
    matrix_norm = array / norm
    return matrix_norm
import os

import math
import numpy as np

def get_file_extension(path_file):
    filename, file_extension = os.path.splitext(path_file)
    extension = file_extension.lower().split(".")[1]
    return extension

def euclidean_distance(Ax, Ay, Az):
    '''
    Function to compute the Euclidean distance between two points

    Parameters:    
        Ax, Ay, Az    float     Ax, Ay and Az difference between the two samples
    
    Returns:       
        dst           float     Euclidena distance 

    '''
    
    dst = np.sqrt(math.pow(Ax, 2) + math.pow(Ay, 2) + math.pow(Az, 2))
    return dst

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
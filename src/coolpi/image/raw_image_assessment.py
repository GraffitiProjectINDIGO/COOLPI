import pandas as pd

from coolpi.colour.cie_colour_spectral import CIEXYZ, CIELAB
from coolpi.image.colourchecker import ColourCheckerSpectral

def reference_colourchecker_as_pandas_dataframe(checker_name):
    '''
    Function to compute the XYZ values from the measured colour checker spectral data loaded from coolpi resources.

    Parameter:
        checker_name         str          ColourChecker name.
    
    Returns:
        colourchecker_xyz    DataFrame    Computed XYZ data.

    '''

    reference_colourchecker = checker_name.split("_")[0] if "_" in checker_name else checker_name
    colourchecker_xyz = ColourCheckerSpectral(reference_colourchecker).to_ColourCheckerXYZ().as_pandas_dataframe()
    return colourchecker_xyz

def merge_colourchecker_dataframe(reference_colourchecker, image_colourchecker):
    '''
    Function to merge the reference measured XYZ data and the XYZ data extracted from an image.

    Parameters:
        reference_colourchecker      DataFrame    Measured ColourChecker XYZ data
        image_colourchecker          DataFrame    ColourChecker XYZ data extracted from an image
    
    Returns:
        colourchecker_xyz            DataFrame    Merged data

    '''

    colourchecker_xyz =  pd.merge(reference_colourchecker, image_colourchecker, on="patch_id")
    return colourchecker_xyz

# To compute solour-difference metrics

def compute_res(X, X_pred):
    return X - X_pred

def compute_LAB_d65(X,Y,Z):
    ciexyz = CIEXYZ("sample", X,Y,Z, "D65", 2)
    L, a, b = ciexyz.to_LAB().coordinates
    return L, a, b

def compute_delta_e(LAB1, LAB2):
    L1, a1, b1 = LAB1
    lab1 = CIELAB("sample1", L1, a1, b1, "D65", 2)
    L2, a2, b2 = LAB2
    lab2 = CIELAB("sample1", L2, a2, b2, "D65", 2)
    ae = lab1.delta_e_ab(lab2)
    return ae

def compute_ciede200(LAB1, LAB2):
    L1, a1, b1 = LAB1
    lab1 = CIELAB("sample1", L1, a1, b1, "D65", 2)
    L2, a2, b2 = LAB2
    lab2 = CIELAB("sample1", L2, a2, b2, "D65", 2)
    ciede2000 = lab1.CIEDE2000(lab2)
    return ciede2000

def compute_colour_differences(colourchecker_xyz):
    '''
    Function to compute the CIE76 and CIEDE2000 colour difference between the reference and the computed XYZ data

    Parameter:
        colourchecker_xyz            DataFrame    Original data
    
    Returns:
        dataframe_assesment_model    DataFrame    Quality assessment data including colour difference metrics.

    '''

    dataframe_assesment_model = colourchecker_xyz.copy()
    dataframe_assesment_model["resX"] = dataframe_assesment_model.apply(lambda x: compute_res(x["X"], x["X'"]), axis=1) 
    dataframe_assesment_model["resY"] = dataframe_assesment_model.apply(lambda x: compute_res(x["Y"], x["Y'"]), axis=1) 
    dataframe_assesment_model["resZ"] = dataframe_assesment_model.apply(lambda x: compute_res(x["Z"], x["Z'"]), axis=1) 
    dataframe_assesment_model["LAB(D65)"] = dataframe_assesment_model.apply(lambda x: compute_LAB_d65(x["X"],x["Y"],x["Z"]), axis=1)
    dataframe_assesment_model["LAB'(D65)"] = dataframe_assesment_model.apply(lambda x: compute_LAB_d65(x["X'"],x["Y'"],x["Z'"]), axis=1)
    dataframe_assesment_model["DeltaE"] = dataframe_assesment_model.apply(lambda x: compute_delta_e(x["LAB(D65)"],x["LAB'(D65)"]), axis=1)
    dataframe_assesment_model["CIEDE2000"] = dataframe_assesment_model.apply(lambda x: compute_ciede200(x["LAB(D65)"],x["LAB'(D65)"]), axis=1)
    return dataframe_assesment_model

# old

def colourchecker_xyz_data_from_dict_to_data_pandas_frame(patches_xyz_dict):
    colourchecker_pd = pd.DataFrame.from_dict(patches_xyz_dict, orient="index", columns=["X'", "Y'", "Z'"]).reset_index()
    colourchecker_pd =  colourchecker_pd.rename( columns={"index":"patch_id"})
    colourchecker_pd["X'"] = colourchecker_pd["X'"]*100		
    colourchecker_pd["Y'"] = colourchecker_pd["Y'"]*100
    colourchecker_pd["Z'"] = colourchecker_pd["Z'"]*100
    return colourchecker_pd
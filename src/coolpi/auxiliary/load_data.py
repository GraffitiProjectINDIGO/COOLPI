from importlib import resources
import json
import os

import numpy as np

from coolpi.auxiliary.errors import ClassTypeError, InvalidType, PathError

def illuminant_is_cie(illuminant_name):
    ''''
    Function to check if the input illuminant is a valid CIE standard illuminant
    
    Parameter:    
        illuminant_name    str    String with the name of the illuminant 

    Returns:      
        bool                      Returns True if the illumant is CIE. False on the contrary

    '''

    with resources.path("coolpi.data.cie", "cie_spd.json") as spd_json_path:
        spd_json = open(spd_json_path, "r")
        cie_spd   = json.loads(spd_json.read())
    
    if illuminant_name.upper() in cie_spd.keys():
        return True
    else:
        return False

def observer_is_cie(observer):
    ''''
    Function to check if the input observer is a valid CIE standard observer
    
    Parameter:    
        illuminant_name    str    String with the name of the illuminant 

    Returns:      
        bool                      Returns True if the observer is CIE. False on the contrary

    '''
    observer_implemented = [2, 10]
    try:
        observer = int(observer)
    except:
        raise ClassTypeError("The input observer its not a valid type argument")

    if observer not in observer_implemented:
        return False
        #raise CIEObserverError("The observer should be a CIE standard 1931 or 1964 observer (2º or 10º)")
    else:
        return True

def load_cie_illuminant(illuminant_name):
    '''
    Function to load the SPD (spectral power distribution) of the input CIE illuminant
    
    CIE 015:2018. 11.2. Table 5. (p.51); Table 7 (p.56); Table 10.1 (p.59); Table 10.2 (p.61); 
    Table 10.3 (p.63); Table 11 (p.65); Table 12.1 (p.67) and Table 12.2 (p.69)
    https://cie.co.at/publications/colorimetry-4th-edition/

    Parameter:    
        illuminant_name    str    String with the name of the CIE illuminant 

    Returns:     
        cie_illuminant     dict   CIE Illuminant data as dict as follows
                                  {"lambda_values":spd, "lambda_nm_range": spd_nm_range, "lambda_nm_interval": spd_nm_interval}
    
    '''
    
    if illuminant_is_cie(illuminant_name):    
        with resources.path("coolpi.data.cie", "cie_spd.json") as spd_json_path:
            spd_json = open(spd_json_path, "r")
            cie_spd   = json.loads(spd_json.read())
    
        spd = cie_spd[illuminant_name]["lambda_values"]
        spd_nm_range = cie_spd[illuminant_name]["lambda_nm_range"]
        spd_nm_interval = cie_spd[illuminant_name]["lambda_nm_interval"]
        cie_illuminant = {"lambda_values":spd, "lambda_nm_range": spd_nm_range, "lambda_nm_interval": spd_nm_interval}
        return cie_illuminant
    else:
        #raise CIEIlluminantError("The input illuminant name is not a valid CIE standard illuminant")
        return None
        
def load_cie_cmf(observer):
    '''
    Function to load the CMF (colour-matching-function) related to the input CIE observer
    
    CIE015:2018. 11.1. Table 1. Colour-matching functions of the CIE 1931 standard colorimetric observer (pp.43-44)
    CIE015:2018. 11.1. Table 2. Colour-matching functions of the CIE 1964 standard colorimetric observer (pp.45-46)
    https://cie.co.at/publications/colorimetry-4th-edition/
    
    Parameter:   
        observer    str, int    CIE observer

    Returns:     
        cmf         dic         CMF data as dict as follows
                                {"x_cmf": x_cmf, "y_cmf": y_cmf, "z_cmf": z_cmf, "lambda_nm_range": cmf_nm_range,
                                 "lambda_nm_interval": cmf_nm_interval}

    '''
    
    if observer_is_cie(observer):
        with resources.path("coolpi.data.cie", "cie_cmf.json") as cie_json_path:
            cie_json = open(cie_json_path, "r")
            cie_cmf   = json.loads(cie_json.read())    
    else:
        return None
        #raise CIEObserverError("The observer should be a CIE standard 1931 or 1964 observer (2º or 10º)")
            
    obs = "2 observer" if int(observer) == 2 else "10 observer"
        
    x_cmf, y_cmf, z_cmf = cie_cmf[obs]["x_cmf"], cie_cmf[obs]["y_cmf"], cie_cmf[obs]["z_cmf"]
    cmf_nm_range    = cie_cmf[obs]["lambda_nm_range"]
    cmf_nm_interval = cie_cmf[obs]["lambda_nm_interval"]

    cmf = {"x_cmf": x_cmf, "y_cmf": y_cmf, "z_cmf": z_cmf, "lambda_nm_range": cmf_nm_range, "lambda_nm_interval": cmf_nm_interval}
    return cmf

def load_cie_cfb(observer):
    '''
    Function to load the CFB (cone-fundamental-based) CMFs related to the input CIE observer

    CIE015:2018. 11.1. Table 3. Cone-fundamental-based tristimulus functions for 2º field size (pg.47-48)
    CIE015:2018. 11.1. Table 4. Cone-fundamental-based tristimulus functions for 10º field size (pg.49-50)
    https://cie.co.at/publications/colorimetry-4th-edition/

    Parameter:   
        observer    str, int    CIE observer
    
    Returns:     
        cfb         dict        CFB data as dict as follows
                                {"x_cfb": x_cfb, "y_cfb": y_cfb, "z_cfb": z_cfb, "lambda_nm_range": cfb_nm_range, 
                                "lambda_nm_interval": cfb_nm_interval}

    '''
    
    if observer_is_cie(observer):
        with resources.path("coolpi.data.cie", "cie_cfb.json") as cie_json_path:
            cie_json = open(cie_json_path, "r")
            cie_cfb   = json.loads(cie_json.read())    
    else:
        return None
        #raise CIEObserverError("The observer should be a CIE standard 1931 or 1964 observer (2º or 10º)")
   
    obs = "2 observer" if int(observer) == 2 else "10 observer"
        
    x_cfb, y_cfb, z_cfb = cie_cfb[obs]["xf_cmf"], cie_cfb[obs]["yf_cmf"], cie_cfb[obs]["zf_cmf"]
    cfb_nm_range    = cie_cfb[obs]["lambda_nm_range"]
    cfb_nm_interval = cie_cfb[obs]["lambda_nm_interval"]

    cfb = {"xf_cmf": x_cfb, "yf_cmf": y_cfb, "zf_cmf": z_cfb, "lambda_nm_range": cfb_nm_range, "lambda_nm_interval": cfb_nm_interval}
    return cfb

def load_cie_rgbcmf(observer):
    '''
    Function to load the RGB CMF (colour-matching-function) related to the input CIE observer
    
    CIE015:2018. Annex B. Table B1. RGB Colour-matching functions for the CIE 1931 standard colorimetric observer (pg.85-86)
    CIE015:2018. Annex B. Table B1. RGB Colour-matching functions for the CIE 1931 standard colorimetric observer (pg.87-88)
    https://cie.co.at/publications/colorimetry-4th-edition/

    Parameter:   
        observer:   str or int    CIE observer

    Returns:     
        rgbcmf:     dict          RGB CMF data as dict as follows
                                  {"r_cmf": r_cmf, "g_cmf": g_cmf, "b_cmf": b_cmf, "lambda_nm_range": rgbcmf_nm_range, 
                                  "lambda_nm_interval": rgbcmf_nm_interval}

    '''  

    if observer_is_cie(observer):
        with resources.path("coolpi.data.cie", "cie_rgbcmf.json") as cie_json_path:
            cie_json = open(cie_json_path, "r")
            cie_rgbcmf   = json.loads(cie_json.read())    
    else:
        return None
        #raise CIEObserverError("The observer should be a CIE standard 1931 or 1964 observer (2º or 10º)")

    obs = "2 observer" if int(observer) == 2 else "10 observer"
        
    r_cmf, g_cmf, b_cmf = cie_rgbcmf[obs]["r_cmf"], cie_rgbcmf[obs]["g_cmf"], cie_rgbcmf[obs]["b_cmf"]
    rgbcmf_nm_range    = cie_rgbcmf[obs]["lambda_nm_range"]
    rgbcmf_nm_interval = cie_rgbcmf[obs]["lambda_nm_interval"]

    rgbcmf = {"r_cmf": r_cmf, "g_cmf": g_cmf, "b_cmf": b_cmf, "lambda_nm_range": rgbcmf_nm_range, "lambda_nm_interval": rgbcmf_nm_interval}
    return rgbcmf

def load_cie_s_ctt_components():
    '''
    Function to load the CIE S components (S0, S1, S2) 
    
    CIE015:2018. 11.1. Table 6. S Components of the relative SPD of daylight used in the calculation of relative SPD of 
    CIE daylight illuminants of different correlated colour temperatures (CTT). (pp.54-55)
    https://cie.co.at/publications/colorimetry-4th-edition/

    Returns:     
        S0, S1, S2    list    S components to compute the SPD from a CCT

    '''      
    with resources.path("coolpi.data.cie", "cie_s_ctt.json") as wp_json_path:
        cie_json = open(wp_json_path, "r")
        cie_s_ctt  = json.loads(cie_json.read())
        S0, S1, S2 = cie_s_ctt["S0"], cie_s_ctt["S1"], cie_s_ctt["S2"] 
    
    return S0, S1, S2
    
def load_cie_white_point(illuminant_name, observer):
    '''
    Function to load the CIE XYZ WhitePoint coordinates for the input CIE Illuminant and observer 
    
    CIE015:2018. 11.2. Tables representing the relative spectral power distribution of illuminants and other colorimetric data
    Table 9.1. Colorimetric data (tristimulus values XYZ, chromaticity coodidinates xy and u'v') for CIE illuminants, computed 
    for the CIE 1935 standard colorimetric observer
    Table 9.2. Colorimetric data (tristimulus values XYZ, chromaticity coodidinates xy and u'v') for CIE illuminants, computed 
    for the CIE 1964 standard colorimetric observer
    https://cie.co.at/publications/colorimetry-4th-edition/

    Parameters:    
        illuminant_name    str         String with the name of the illuminant 
        observer           str, int    CIE observer
    
    Returns:     
        Xn, Yn, Zn:        float       CIE XYZ theoretical coordinates for the WhitePoint illuminant 
    
    '''   

    if illuminant_is_cie(illuminant_name):
        with resources.path("coolpi.data.cie", "cie_white_point.json") as wp_json_path:
            cie_json = open(wp_json_path, "r")
            cie_wp  = json.loads(cie_json.read())
    else:
        return None, None, None
        #raise CIEIlluminantError("The input illuminant name is not a valid CIE standard illuminant")

    if observer_is_cie(observer):
        obs = "2 observer" if int(observer) == 2 else "10 observer"
    else:
        return None, None, None
        #raise CIEObserverError("The observer should be a CIE standard 1931 or 1964 observer (2º or 10º)")
    
    Xn, Yn, Zn = cie_wp[obs][illuminant_name]["XYZ"]
    return float(Xn), float(Yn), float(Zn)


# MeasuredIlluminant

# CSV Sekonic

def load_metadata_sekonic_from_csv(path_sekonic_file):
    '''
    Function to load the measured illuminant data from a csv sekonic file 
    
    Parameter:   
        path_sekonic_file   path    Path for the sekonic measurement csv data file

    Returns:     
        measured_data       dict    Illuminant data with the keys: 
                                    "Date", "Measuring Mode", "Viewing Angle [º]", "CCT [K]", "Illuminance [lx]"
                                    "XYZ", "CIE1931 xyz", "CIE1931 u'v'"
                                    "lambda_values_5nm", "lambda_values_1nm"

    '''    

    if not os.path.exists(path_sekonic_file):
        raise PathError("File not found")

    measured_data = {}

    XYZ = []
    xyz = []
    uv = []

    measured_data["nm_range"] = [380,780]

    lambda_values = []

    with open(path_sekonic_file, "r", encoding="utf-8") as file_data:
        for line in file_data:
            line = line.rstrip("\n")
            #fila = fila.translate(str.maketrans("", "", string.punctuation))
            info = line.split(",")
            if "Date Saved" in line:
                measured_data["Date"] = tuple(info[1].split())
            if "Measuring Mode" in line:
                measured_data["Measuring Mode"] = info[1]
            if "Viewing Angle" in line:
                measured_data["Viewing Angle [º]"] = int(info[1])
            if "[K]" in line:
                measured_data["CCT"] = int(info[1])
            if "uv" in line:
                measured_data["Delta_uv"] = float(info[1])
            if "[lx]" in line:
                measured_data["Illuminance [lx]"] = float(info[1])
            if "Value X" in line:
                X = float(info[1])/10
                XYZ.append(X)
            if "Value Y" in line:
                Y = float(info[1])/10
                XYZ.append(Y)
            if "Value Z" in line:
                Z = float(info[1])/10
                XYZ.append(Z)
                measured_data["XYZ"]= tuple(XYZ)
            if "CIE1931 x" in line:
                x = float(info[1])
                xyz.append(x)
            if "CIE1931 y" in line:
                y = float(info[1])
                xyz.append(y)
            if "CIE1931 z" in line:
                z = float(info[1])
                xyz.append(z)
                measured_data["xyz"]= tuple(xyz)
            if "u'" in line:
                u = float(info[1])
                uv.append(u)
            if "v'" in line:
                v = float(info[1])
                uv.append(v)
                measured_data["u'v'"]= tuple(uv)
            if "Spectral Data" in line:
                lambda_values.append(float(info[1]))

        measured_data["lambda_values_5nm"] = np.array(lambda_values[:81])
        measured_data["lambda_values_1nm"] = np.array(lambda_values[81:])
        
    return measured_data

def load_spd_from_json(path_json):
    with open(path_json) as json_file:
        measured_data = json.load(json_file)
    return measured_data

def is_valid_spd_data_dict(data_as_dict):
    required_label = set(["nm_range", "nm_interval", "lambda_values"])
    label_data = set(data_as_dict.keys())
    set_intersect = required_label.intersection(label_data)
    valid = True if len(set_intersect) == len(required_label) else False
    return valid

def rgb_dict_to_array(rgb_dict):
    '''
    Function to cast rgb dict data to a np.darray 
    
    Parameter:   
        rgb_dict     dict         RGB values as dict, with the patch_id, and the rgb_values as list

    Returns:     
        rgb_array    np.darray    RGB values as numpy array

    '''  

    rgb = []
    for patch_id, rgb_data in rgb_dict.items():
        rgb.append(rgb_data)
    rgb_array = np.array(rgb)
    return rgb_array

# ColourChecherSpectral

colour_checker_implemented= {
    "CCC": "Calibrite CLASSIC",
    "CCPP2": "Calibrite PASSPORT PHOTO 2",
    "CCPPV": "Calibrite PASSPORT VIDEO",
    "CCDSG": "Calibrite DIGITAL SG",
    "GM": "GretagMacbeth" , 
    "MSCB_1994": "Munsell Soil Colour Book (Ed. 1994)", 
    "MSCB_2009": "Munsell Soil Colour Book (Ed. 2009/2022)", 
    "PM": "Pantone Metallics",
    "QPGQP202": "QPcard 202",
    "RALK5": "RAL K5 CLASSIC",
    "RALK7": "RAL K7 CLASSIC",
    "SCK100": "Spyder Checker",
    "XRCCPP": "X-rite PASSPORT PHOTO",
    "XRCCSG": "X-rite Digital SG"}

def is_checker_implemented(checker_name, colour_checker_dict = colour_checker_implemented):
    if checker_name in colour_checker_dict.keys():
        return True
    return False

def get_full_colourchecker_name(checker_name, colour_checker_dict = colour_checker_implemented):
    if checker_name in colour_checker_dict.keys():
        full_name = colour_checker_dict[checker_name]
        return full_name
    return None

def load_theoretical_colourchecker_using_resources(checker_name):
    with resources.path("coolpi.data.colourchecker.reflectance", "colour_checker_reflectance_data.json") as json_path:
        chart_json = open(json_path, "r")
        chart_dict = json.loads(chart_json.read())  
    return chart_dict[checker_name]

# JSON

def load_colourchecker_from_json(path_json):
    with open(path_json) as json_file:
        measured_data = json.load(json_file)
    return measured_data

def is_valid_colourchecker_spectral_data_dict(data_as_dict):
    required_label = set(["nm_range", "nm_interval", "patches", "Illuminant", "Observer"])
    label_data = set(data_as_dict.keys())
    set_intersect = required_label.intersection(label_data)
    valid = True if len(set_intersect) == len(required_label) else False
    return valid

# ColourCheckerXYZ


# XYZ, LAB, RGB data from CSV file

# csv_cols={"label":col_pos, "X":col_pos, "Y":col_pos, "Z":col_pos}

def load_coordinates_from_csv(path_csv, csv_cols, head=True, data_type="RGB"):
    '''
    Function to load coordinates from a csv file 
    
    Parameters:   
        path_csv        path    Path for the CSV data file 
        csv_cols        dict    Col position for label and coordinates
        head            bool    True if the CSV has file. False on the contrary.
        data_type       str     Coordinates: "RGB", "LAB", "XYZ"

    Returns:     
        patches_dict    dict    Coordinates as dict

    '''
    
    data_type_valid = ["RGB", "XYZ", "LAB"]
    
    if not os.path.exists(path_csv):
        raise PathError("File not found")
    
    if data_type not in data_type_valid:
        raise ClassTypeError(f"Coordinates data type not valid: {data_type_valid}")

    patches_dict = {} # easy search 
    coordinates = []
    label_c1, label_c2, label_c3 = [label for label in list(data_type)]

    with open(path_csv, "r") as f_rgb:
        if head:
            f_rgb.readline() # pass header

        for linea in f_rgb:
            data = linea.split(";")
            # get data
            patche_id = data[csv_cols["label"]]
            c1 = float(data[csv_cols[label_c1]])
            c2 = float(data[csv_cols[label_c2]])
            c3 = float(data[csv_cols[label_c3]])
            patches_dict[patche_id] = (c1,c2,c3) 
            coordinates.append([c1,c2,c3]) # to get the rgb values as array

    return patches_dict

# not tested
def load_reflectance_from_csv(path_csv, head=True):
    if not os.path.exists(path_csv):
        raise PathError("File not found")
    
    patches_reflectance_dict = {} # easy search 

    with open(path_csv, "r") as f_reflectance:
        if head:
            f_reflectance.readline() # pass header
        
        for linea in f_reflectance:
            data = linea.split(";")
            sample_id = data[0]
            reflectance = data[1:len(data)]
            patches_reflectance_dict[sample_id] = reflectance
    return patches_reflectance_dict
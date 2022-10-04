import os
import json
import numpy as np
import pandas as pd

import coolpi.auxiliary.common_operations as cop
import coolpi.auxiliary.export_data as ed
from coolpi.colour.cie_colour_spectral import MeasuredIlluminant
import coolpi.image.colourchecker_detection as ccd
from coolpi.image.image_objects import RawImage
import coolpi.image.white_balance as wb

def get_spd_dict_data(path_spd, spd_extension=["csv", "CSV"]):
    spd_folders = cop.get_dir_folders(path_spd)  
    spd_dict_data = {}
    for folder in spd_folders:
        spd_dict_data[folder] = {} # measurement date
        path_dir = os.path.join(path_spd, folder)
        csv_list = cop.get_dir_list_file_for_extension(path_dir, spd_extension)
        # get data from illuminant
        for spd in csv_list:
            spd_name = spd.split("_")[1]
            path_csv = os.path.join(path_spd, *[folder, spd]) # path to csv
            meas_spd = MeasuredIlluminant(illuminant_name=spd_name, path_file = path_csv)
            spd_dict_data[folder][spd_name] = {}
            spd_dict_data[folder][spd_name]["spd"]  = meas_spd
            spd_dict_data[folder][spd_name]["path"] = path_csv
    return spd_dict_data

def show_spd_dict_data(spd_dict_data):
    print("SPD Measurement Information:")
    print("----------------------------\n")
    for date in spd_dict_data.keys():
        print("Measurement Date = ", date)               
        print("Num. meas.       = ", len(spd_dict_data[date].keys())) 
        print("Meas. ID         = ", sorted(spd_dict_data[date].keys()))
        print("\n")

def get_image_dict_data(path_img, img_extension=["nef","NEF"]):
    image_folders = cop.get_dir_folders(path_img) 
    image_dict_data = {}
    for folder in image_folders:
        meas_date, num_graffito = folder.split("_")
        path_dir = os.path.join(path_img, folder)
        list_img = cop.get_dir_list_file_for_extension(path_dir, img_extension)
        if meas_date not in image_dict_data.keys():
            image_dict_data[meas_date] = {}
        image_dict_data[meas_date][num_graffito] = list_img
    return image_dict_data

def show_image_dict_data(image_dict_data):
    print("Image Acquisition Information:")
    print("-----------------------------\n")
    for date in image_dict_data.keys():
        print("Measurement Date = ", date)               
        print("Num. meas.       = ", len(image_dict_data[date].keys())) 
        print("Graffito. ID     = ", sorted(image_dict_data[date].keys()))
        for graffito_id in image_dict_data[date].keys():
            print("\n")
            print("Graffito:    ", graffito_id)
            print("Num. images: ", len(image_dict_data[date][graffito_id]))
            print("Images:      ", image_dict_data[date][graffito_id])
        print("\n")

def get_sRGB_dict_data(path_sRGB, sRGB_extension=["tif","TIF"]):
    sRGB_folders = cop.get_dir_folders(path_sRGB) 
    sRGB_dict_data = {}
    for folder in sRGB_folders:
        meas_date, num_graffito = folder.split("_")
        path_dir = os.path.join(path_sRGB, folder)
        list_img = cop.get_dir_list_file_for_extension(path_dir, sRGB_extension)
        if meas_date not in sRGB_dict_data.keys():
            sRGB_dict_data[meas_date] = {}
        sRGB_dict_data[meas_date][num_graffito] = list_img
    return sRGB_dict_data

def show_sRGB_dict_data(sRGB_dict_data):    
    print("Processed Image Information:")
    print("---------------------------\n")
    for date in sRGB_dict_data.keys():
        print("Measurement Date     = ", date)               
        print("Num. img. processed  = ", len(sRGB_dict_data[date].keys())) 
        print("Image                = ", sorted(sRGB_dict_data[date].keys()))
        print("\n")

def check_sRGB_folder():
    data_folders = cop.get_dir_folders(os.path.join(os.getcwd(), "data"))
    if "sRGB" not in data_folders:
        os.mkdir(os.path.join(os.getcwd(), *["data", "sRGB"]))

# Automatic workflow

def get_graffito_illuminant(date, graffito, spd_dict_data):
    for key in spd_dict_data[date].keys():
        if int(graffito)==int(key):
            has_illuminant = True
            illum_spd = spd_dict_data[date][key]
            return has_illuminant, illum_spd
    return False, None     

def get_colourchecker_corners(rgb_data, opencv_descriptor= "SIFT", checker_name="XRCCPP"):
    corners = ccd.colourchecker_patch_detection(rgb_data, opencv_descriptor, checker_name)
    if corners is not None:
        has_colourchecker = True
        return has_colourchecker, corners
    return False, corners

def get_rgb_to_xyz_matrix(path_rgb_to_xyz):
    # RGB to XYZ
    if path_rgb_to_xyz is not None:
        try:
            rgb_to_xyz = np.genfromtxt(path_rgb_to_xyz, delimiter=';')
            computed_rgb_to_xyz = True
            return computed_rgb_to_xyz, rgb_to_xyz
        except:
            return False, "camera" # embedded
    return False, "camera" # embedded

def compute_wb_patches(raw_image, checker_name, patches_id):
    wb_computed = []
    for patch in patches_id:
        params = dict(checker_name=checker_name, patch_id=patch)
        wb_patch = raw_image.compute_wb_multipliers(**params)
        wb_computed.append(wb_patch)
    return wb_computed

def automatic_image_processing(path_graffiti_images, path_graffiti_spd, path_sRGB, path_rgb_to_xyz, checker_name="XRCCPP", opencv_descriptor="SIFT", wb_algorithm= "GreyWorld", output_bits=16):
    
    # 0) Prepare data information as dict: image, spd, sRGB
    image_dict_data = get_image_dict_data(path_graffiti_images)
    #show_image_dict_data(image_dict_data)
    spd_dict_data = get_spd_dict_data(path_graffiti_spd)
    #show_spd_dict_data(spd_dict_data)
    check_sRGB_folder() # Create sRGB folder if it does not exists
    sRGB_dict_data = get_sRGB_dict_data(path_sRGB)
    #show_sRGB_dict_data(sRGB_dict_data)

    for date in image_dict_data.keys():
        print("Measurement Date : ", date)
        for graffito in image_dict_data[date].keys():
            print("Graffito ID      : ", graffito)
            # 1) Project structure
            folder = date + "_" + graffito
            # check if sRGB folder exist       
            if date not in sRGB_dict_data.keys():
                sRGB_dict_data[date] = {}
            if graffito not in sRGB_dict_data[date].keys():
                os.mkdir(os.path.join(path_sRGB, folder)) # folder sRGB -> date-graffito
                #update
                sRGB_dict_data[date][graffito] = {}
                            
            # 2) Get illuminant
            has_illuminant, illum_spd = get_graffito_illuminant(date, graffito, spd_dict_data)

            # 3) Image Processing
            total_images = image_dict_data[date][graffito] # raw images in graffito folder  
            for image in total_images:
                #image_processed = cop.get_dir_list_file_for_extension(os.path.join(path_sRGB, folder), ["tif","TIF"])   
                name_images = [item.split("_sRGB")[0] for item in sRGB_dict_data[date][graffito]] # get list of processed images to be removed from the process
                if image[:-4] not in name_images:
                    # Create RawImage instance
                    path_raw = os.path.join(path_graffiti_images, *[folder, image]) # root dir (graffiti images)
                    if os.path.exists(path_raw):                
                        raw_image = RawImage(path_raw)
                        #raw_image.show(data="raw", method="matplotlib")
                    else:
                        raw_image = None
                    
                    if raw_image is not None:
                        # set init variables to False
                        colourchecker_extracted = False
                        wb_average_computed = False
                        colour_corrected = False
                        AE_computed = False
                        computed_wb_algorithm = False
                        computed_wb_from_illuminant = False
                        
                        print("Image            : ", image)
                        image_processing_information = {} # dict with the process details (to JSON)
                        image_processing_information["date"] = date
                        image_processing_information["graffito"] = graffito # id
                        image_processing_information["image"] = image # name
                        image_processing_information["path"] = path_raw # full path
                        # RGB to XYZ
                        computed_rgb_to_xyz, rgb_to_xyz = get_rgb_to_xyz_matrix(path_rgb_to_xyz) 
                        raw_image.set_RGB_to_XYZ_matrix(rgb_to_xyz) # set RGB to XYZ
                        # set illuminant
                        if has_illuminant:
                            raw_image.set_image_illuminant(illum_spd["spd"]) # Set illuminant
                        
                        image_processing_information["rgb_to_xyz"] = path_rgb_to_xyz if computed_rgb_to_xyz else rgb_to_xyz
                        image_processing_information["Illuminant"] = illum_spd["path"] if has_illuminant else illum_spd # None
                        image_processing_information["white_balance_multipliers"] = {} # empty
        
                        # A) If image has a colour checker
                        checker_name_to_extract = "XRCCPP_24" if "XRCCPP" in checker_name else checker_name
                        has_colourchecker, corners, size_rect = raw_image.automatic_colourchecker_extraction(checker_name_to_extract, opencv_descriptor)
                        # full patches
                        #checker_name_to_extract = "XRCCPP_26" if "XRCCPP" in checker_name else checker_name
                        #has_colourchecker, corners, size_rect = raw_image.automatic_colourchecker_extraction(checker_name_to_extract, opencv_descriptor)

                        if has_colourchecker:           
                            # extract colourchecker                 
                            try:
                                # save image with colourchecker
                                output_name = image[:-4] + "_colourchecker.tif"
                                output_path_checker = os.path.join(path_sRGB, *[folder, output_name])     
                                raw_image.show_colourchecker(checker_name=checker_name, show_image=False, save_image=True, output_path=output_path_checker, bits=output_bits)
                                # update
                                image_processing_information["colourchecker"] = {}
                                image_processing_information["colourchecker"]["corners"] = corners
                                image_processing_information["colourchecker"]["size_rect"] = size_rect                        
                                colourchecker_extracted = True
                            except:
                                colourchecker_extracted = False
                            
                            if colourchecker_extracted:
                                # compute average wb
                                try:
                                    patches_id = ["D2", "D3", "D4"]
                                    wb_computed = compute_wb_patches(raw_image, checker_name, patches_id)
                                    # compute average 
                                    wb_average = wb.compute_wb_average(wb_computed)
                                    raw_image.set_whitebalance_multipliers(wb_average)
                                    # update
                                    image_processing_information["white_balance_multipliers"]["D2-D3-D4"] = wb_computed
                                    image_processing_information["white_balance_multipliers"]["wb_average"] = wb_average
                                    wb_average_computed = True
                                except:
                                    wb_average_computed = False
                        
                            if wb_average_computed:
                                try:
                                    # compute colour corrected
                                    raw_image.apply_colour_correction()
                                    # save
                                    output_name = image[:-4] + "_sRGB.tif"
                                    output_path_sRGB = os.path.join(path_sRGB, *[folder,output_name])               
                                    raw_image.save(output_path=output_path_sRGB, data="sRGB", bits=output_bits)
                                    colour_corrected = True
                                except:
                                    colour_corrected = False

                            if colour_corrected and has_illuminant:
                                # update
                                image_processing_information["output_sRGB"] ={}
                                image_processing_information["output_sRGB"]["path"] = output_path_sRGB
                                image_processing_information["output_sRGB"]["bits"] = output_bits
                                try:
                                    # AE00
                                    colourchecker_metrics = raw_image.compute_image_colour_quality_assessment(checker_name)
                                    colourchecker_metrics["illuminant_x"] = "D65" # as str, avoid utf-8 error
                                    colourchecker_metrics["illuminant_y"] = illum_spd["path"] # as str, avoid utf-8 error    
                                    # DataFrame to dict
                                    colourchecker_metrics_dict = colourchecker_metrics.to_dict("index")
                                    # export dict as JSON
                                    name_json_mtr = image[:-4] + "_colourchecker_metrics.json"
                                    path_json_mtr = os.path.join(path_sRGB, *[folder, name_json_mtr])    
                                    ed.export_dict_as_json(colourchecker_metrics_dict, path_json_mtr)
                                    AE_computed = True
                                except:
                                    AE_computed = False

                            if AE_computed:
                                image_processing_information["CIEDE2000"] = colourchecker_metrics["CIEDE2000"].mean()
                                print("Average CIEDE2000 (from colour checker) = ", colourchecker_metrics["CIEDE2000"].mean())

                            # using different options for wb
                            # wb algorithm
                            if wb_algorithm is not None:
                                try:
                                    if colourchecker_extracted:
                                        params = dict(algorithm=wb_algorithm, remove_colourckecker=True, corners_colourchecker=corners)
                                    else:
                                        params = dict(algorithm=wb_algorithm, remove_colourckecker=False, corners_colourchecker=None)
                                    
                                    wb_multipliers_algorithm = raw_image.estimate_wb_multipliers(method="wb_algorithm", **params)
                                    raw_image.set_whitebalance_multipliers(wb_multipliers_algorithm)
                                    raw_image.apply_colour_correction()
                                    output_name = image[:-4] + "_sRGB_wb_algorithm.tif"
                                    output_path_wb_algorithm = os.path.join(path_sRGB, *[folder, output_name])               
                                    raw_image.save(output_path=output_path_wb_algorithm, data="sRGB", bits=output_bits)

                                    image_processing_information["output_sRGB_wb_algorithm"] ={}
                                    image_processing_information["output_sRGB_wb_algorithm"]["path"] = output_path_wb_algorithm
                                    image_processing_information["output_sRGB_wb_algorithm"]["bits"] = output_bits
                                    
                                    if has_illuminant:
                                        colourchecker_metrics_wb_algorithm = raw_image.compute_image_colour_quality_assessment(checker_name)
                                        colourchecker_metrics_wb_algorithm["illuminant_x"] = "D65" # as str, avoid utf-8 error
                                        colourchecker_metrics_wb_algorithm["illuminant_y"] = illum_spd["path"] # as str, avoid utf-8 error
                                        # DataFrame to dict
                                        colourchecker_metrics_alg_dict = colourchecker_metrics_wb_algorithm.to_dict("index")
                                        # export dict as JSON
                                        name_json_mtr_alg = image[:-4] + "_colourchecker_metrics_algorithm.json"
                                        path_json_mtr_alg = os.path.join(path_sRGB, *[folder, name_json_mtr_alg])    
                                        ed.export_dict_as_json(colourchecker_metrics_alg_dict, path_json_mtr_alg)
                                        computed_wb_algorithm = True
                                except:
                                    computed_wb_algorithm = False

                            if computed_wb_algorithm:
                                image_processing_information["white_balance_multipliers"]["wb_algorithm"] = wb_multipliers_algorithm
                                print("Average CIEDE2000 (wb using algorithm) = ", colourchecker_metrics_wb_algorithm["CIEDE2000"].mean())
                                
                            # from illuminant
                            if has_illuminant:
                                try:
                                    wb_from_illuminant = raw_image.estimate_wb_multipliers(method="illuminant")
                                    raw_image.set_whitebalance_multipliers(wb_from_illuminant)
                                    raw_image.apply_colour_correction()
                                    output_name = image[:-4] + "_sRGB_wb_from_illuminant.tif"

                                    image_processing_information["output_sRGB_wb_from_illuminant"] ={}
                                    image_processing_information["output_sRGB_wb_from_illuminant"]["path"] = output_path_wb_algorithm
                                    image_processing_information["output_sRGB_wb_from_illuminant"]["bits"] = output_bits

                                    output_path = os.path.join(path_sRGB, *[folder,output_name])               
                                    raw_image.save(output_path=output_path, data="sRGB", bits=output_bits)
                                    colourchecker_metrics_from_illuminant = raw_image.compute_image_colour_quality_assessment(checker_name)
                                    colourchecker_metrics_from_illuminant["illuminant_x"] = "D65" # as str, avoid utf-8 error
                                    colourchecker_metrics_from_illuminant["illuminant_y"] = illum_spd["path"] # as str, avoid utf-8 error
                                    # DataFrame to dict
                                    colourchecker_metrics_illum_dict = colourchecker_metrics_from_illuminant.to_dict('index')
                                    # export dict as JSON
                                    name_json_mtr_illum = image[:-4] + "_colourchecker_metrics_illuminant.json"
                                    path_json_mtr_illum = os.path.join(path_sRGB, *[folder, name_json_mtr_illum])    
                                    ed.export_dict_as_json(colourchecker_metrics_illum_dict, path_json_mtr_illum)
                                    computed_wb_from_illuminant = True
                                except:
                                    computed_wb_from_illuminant = False

                            if computed_wb_from_illuminant:
                                image_processing_information["white_balance_multipliers"]["wb_from_illuminant"] = wb_from_illuminant
                                print("Average CIEDE2000 (wb from illuminant) = ", colourchecker_metrics_from_illuminant["CIEDE2000"].mean())

                            if colour_corrected:
                                # export dict as JSON
                                name_json = image[:-4] + ".json"
                                path_json = os.path.join(path_sRGB, *[folder, name_json])    
                                ed.export_dict_as_json(image_processing_information, path_json)
                            else:
                                print(f"The image {image} could not be processed. Path: {path_raw}")

                        else:
                            # options for wb
                            if wb_algorithm is not None:
                                try:
                                    params = dict(algorithm="GreyWorld", remove_colourckecker=False, corners_colourchecker=None)
                                    wb_algorithm = raw_image.estimate_wb_multipliers(method="wb_algorithm", **params)
                                    image_processing_information["white_balance_multipliers"]["wb_algorithm"] = wb_algorithm
                                    raw_image.set_whitebalance_multipliers(wb_algorithm)
                                    raw_image.apply_colour_correction()
                                    output_name = image[:-4] + "_sRGB_wb_algorithm.tif"
                                    output_path = os.path.join(path_sRGB, *[folder,output_name])               
                                    raw_image.save(output_path=output_path, data="sRGB", bits=output_bits)
                                    computed_wb_algorithm = True
                                except:
                                    computed_wb_algorithm = False

                            if has_illuminant:
                                try:
                                    wb_from_illuminant = raw_image.estimate_wb_multipliers(method="illuminant")
                                    image_processing_information["white_balance_multipliers"]["wb_from_illuminant"] = wb_from_illuminant
                                    raw_image.set_whitebalance_multipliers(wb_from_illuminant)
                                    raw_image.apply_colour_correction()
                                    output_name = image[:-4] + "_sRGB_wb_from_illuminant.tif"
                                    output_path = os.path.join(path_sRGB, *[folder,output_name])               
                                    raw_image.save(output_path=output_path, data="sRGB", bits=output_bits)
                                    computed_wb_from_illuminant = True
                                except:
                                    computed_wb_from_illuminant = False
                        
                            if computed_wb_algorithm or computed_wb_from_illuminant:                
                                # export dict as JSON
                                name_json = image[:-4] + ".json"
                                path_json = os.path.join(path_sRGB, *[folder, name_json])    
                                ed.export_dict_as_json(image_processing_information, path_json)

                            if computed_wb_algorithm==False and computed_wb_from_illuminant==False:
                                print(f"The image {image} could not be processed. Path: {path_raw}")
                    del raw_image # reset

if __name__ == '__main__':
    # General options
    # path
    current_dir = os.getcwd()
    path_graffiti_images = os.path.join(current_dir, *["data", "Images"])        # root dir (graffiti images)
    path_graffiti_spd = os.path.join(current_dir, *["data", "SpectrometerData"]) # root dir (spd)
    path_sRGB = os.path.join(current_dir, *["data", "sRGB"])                     # root dir processed images
    # options
    path_rgb_to_xyz = os.path.join(current_dir, *["data", "RGB_to_XYZ", "rgb_to_xyz_nikon_z7ii.csv"])  
    checker_name = "XRCCPP"
    opencv_descriptor = "SIFT"
    wb_algorithm = "GreyWorld"
    output_bits = 16
    automatic_image_processing(path_graffiti_images, path_graffiti_spd, path_sRGB, path_rgb_to_xyz, checker_name, opencv_descriptor, wb_algorithm, output_bits)
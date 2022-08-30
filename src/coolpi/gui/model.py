from curses import meta
import os
import json

from coolpi.gui.config import Config

import coolpi.auxiliary.plot as cpt
from coolpi.colour.cie_colour_spectral import CIEXYZ, CIExyY, CIELAB, CIELCHab, CIELCHuv, CIELUV, Reflectance
from coolpi.colour.cie_colour_spectral import SpectralColour
from coolpi.colour.cie_colour_spectral import Illuminant, IlluminantFromCCT, MeasuredIlluminant
from coolpi.image.colourchecker import ColourCheckerSpectral
from coolpi.image.image_objects import RawImage

class Model:

    __colour_checker_implemented = Config.instance().data["cci"]["colourchecker_implemented"]
    __current_colourchecker = None
    __current_raw_image = None

    @property
    def current_colourchecker(self):
        return self.__current_colourchecker
    
    @current_colourchecker.setter
    def current_colourchecker(self, checker):
        if isinstance(checker, str):
            self.__current_colourchecker = ColourCheckerSpectral(checker_name=checker) # implemented
        if isinstance(checker, dict):
            name = checker["NameColorChart"]
            self.__current_colourchecker = XRCCPP = ColourCheckerSpectral(checker_name=name, data=checker)

    @property
    def current_raw_image(self):
        return self.__current_raw_image
    
    @current_raw_image.setter
    def current_raw_image(self, raw_image):
        self.__current_raw_image = raw_image

    def __init__(self):

        self.__prepare_data_folder_structure__()

    def __prepare_data_folder_structure__(self):
        current_dir = os.getcwd()
        list_dir, list_file = self.__get_dir_adn_file_from_path__(current_dir)
        list_dir_to_create = ["csv", "img", "json", "plot", "spd"]
        if "data" not in list_dir:
            # create new "data" folder
            path_data = os.path.join(current_dir, "data")
            os.mkdir(path_data)
            for directory in list_dir_to_create:
                os.mkdir(os.path.join(path_data, directory))
        else:
            path_data = os.path.join(current_dir, "data")
            data_dir, data_file = self.__get_dir_adn_file_from_path__(path_data)
            for directory in list_dir_to_create:
                if directory not in data_dir:    
                    os.mkdir(os.path.join(path_data, directory))

    def __get_dir_adn_file_from_path__(self, current_path):
        list_file = []
        list_dir = []
        current_dir_list = os.listdir(current_path)
        for element in current_dir_list:
            path = os.path.join(current_path, element)
            if os.path.isdir(path):
                list_dir.append(element)
            elif os.path.isfile(path):
                list_file.append(element)
        return list_dir, list_file

    # CSC - Colour Space Conversion
    def compute_colour_space_conversion(self, sample_id, colour_space, illuminant, observer, c1, c2, c3):
        coordinates = {}
        coordinates["Sample_id"] = sample_id
        coordinates["Illuminant"] = illuminant
        coordinates["Observer"] = observer        
        
        if colour_space == "CIE XYZ":
            colour_xyz = CIEXYZ(sample_id, c1, c2, c3, illuminant, observer)
            colour = colour_xyz
            colour_xyY = colour_xyz.to_xyY()
            colour_lab = colour_xyz.to_LAB()
            colour_lchab = colour_xyz.to_LCHab()
            colour_lchuv = colour_xyz.to_LCHuv()
            colour_luv = colour_xyz.to_LUV()
            
            #colour = CIEXYZ(sample_id, c1, c2, c3, illuminant, observer)
            #CIEXYZ_X, CIEXYZ_Y, CIEXYZ_Z = colour.coordinates
            
            #colour.to_xyY().plot(show_figure = False, save_figure = True, output_path = "prueba.png")
            
            #CIExyY_x, CIExyY_y,CIExyY_Y  = colour.to_xyY().coordinates
            #CIELAB_L, CIELAB_a, CIELAB_b = colour.to_LAB().coordinates
            #CIELCHab_L, CIELCHab_C, CIELCHab_Hab = colour.to_LCHab().coordinates
            #CIELCHuv_L, CIELCHuv_C, CIELCHuv_Huv = colour.to_LCHuv().coordinates
            #CIELUV_L, CIELUV_U, CIELUV_V = colour.to_LUV().coordinates
                        
        elif colour_space == "CIE xyY":
            colour_xyY = CIExyY(sample_id, c1, c2, c3, illuminant, observer)
            colour = colour_xyY
            colour_xyz = colour_xyY.to_XYZ()
            colour_lab = colour_xyY.to_LAB()
            colour_lchab = colour_xyY.to_LCHab()
            colour_lchuv = colour_xyY.to_LCHuv()
            colour_luv = colour_xyY.to_LUV()
            
            #x,y,Y = colour.coordinates
            #X,Y,Z = colour.to_XYZ().coordinates
            #L,a,b = colour.to_LAB().coordinates
            #L,C,Hab = colour.to_LCHab().coordinates
            #L,C,Huv = colour.to_LCHuv().coordinates
            #L,U,V = colour.to_LUV().coordinates        
            
        elif colour_space == "CIELAB":
            colour_lab = CIELAB(sample_id, c1, c2, c3, illuminant, observer)
            colour = colour_lab
            colour_xyz = colour_lab.to_XYZ()
            colour_xyY = colour_lab.to_xyY()
            colour_lchab = colour_lab.to_LCHab()
            colour_lchuv = colour_lab.to_LCHuv()
            colour_luv = colour_lab.to_LUV()
            
            #colour = CIELAB(sample_id, c1, c2, c3, illuminant, observer)
            #L,a,b = colour.coordinates
            #X,Y,Z = colour.to_XYZ().coordinates
            #x,y,Y = colour.to_xyY().coordinates
            #L,C,Hab = colour.to_LCHab().coordinates
            #L,C,Huv = colour.to_LCHuv().coordinates
            #L,U,V = colour.to_LUV().coordinates   
        
        elif colour_space == "CIE LCHab":
            colour_lchab = CIELCHab(sample_id, c1, c2, c3, illuminant, observer)
            colour = colour_lchab
            colour_xyz = colour_lchab.to_XYZ()
            colour_xyY = colour_lchab.to_xyY()
            colour_lab = colour_lchab.to_LCHab()
            colour_lchuv = colour_lchab.to_LCHuv()
            colour_luv = colour_lchab.to_LUV()
        
            #colour = CIELCHab(sample_id, c1, c2, c3, illuminant, observer)
            #L,C,Hab = colour.coordinates
            #X,Y,Z = colour.to_XYZ().coordinates
            #x,y,Y = colour.to_xyY().coordinates
            #L,a,b = colour.to_LAB().coordinates
            #L,C,Huv = colour.to_LCHuv().coordinates
            #L,U,V = colour.to_LUV().coordinates   

        elif colour_space == "CIE LCHuv":
            colour_lchuv = CIELCHuv(sample_id, c1, c2, c3, illuminant, observer)
            colour = colour_lchuv
            colour_xyz = colour_lchuv.to_XYZ()
            colour_xyY = colour_lchuv.to_xyY()
            colour_lab = colour_lchuv.to_LCHab()
            colour_lchab = colour_lchuv.to_LCHab()
            colour_luv = colour_lchuv.to_LUV()
            
            #colour = CIELCHuv(sample_id, c1, c2, c3, illuminant, observer)
            #L,C,Huv = colour.coordinates
            #X,Y,Z = colour.to_XYZ().coordinates
            #x,y,Y = colour.to_xyY().coordinates
            #L,a,b = colour.to_LAB().coordinates
            #L,C,Hab = colour.to_LCHab().coordinates
            #L,U,V = colour.to_LUV().coordinates   

        elif colour_space == "CIELUV":
            colour_luv = CIELUV(sample_id, c1, c2, c3, illuminant, observer)
            colour = colour_luv
            colour_xyz = colour_luv.to_XYZ()
            colour_xyY = colour_luv.to_xyY()
            colour_lab = colour_luv.to_LCHab()
            colour_lchab = colour_luv.to_LCHab()
            colour_lchuv = colour_luv.to_LCHuv()
            
            #colour = CIELUV(sample_id, c1, c2, c3, illuminant, observer)
            #L,U,V = colour.coordinates  
            #X,Y,Z = colour.to_XYZ().coordinates
            #x,y,Y = colour.to_xyY().coordinates
            #L,a,b = colour.to_LAB().coordinates
            #L,C,Hab = colour.to_LCHab().coordinates
            #L,C,Huv = colour.to_LCHuv().coordinates 

        # sRGB D65
        if colour_space!= "CIE XYZ":
            XYZ = colour.to_XYZ()
        else:
            XYZ = colour

        if illuminant!="D65":
            XYZ_d65 = XYZ.to_CIE_illuminant("D65", observer, cat_model="von Kries")
        else:
            XYZ_d65 = XYZ
            
        # get coordinates
        r, g, b = XYZ_d65.to_RGB().coordinates
        sR = str(int(255*r))
        sG = str(int(255*g))
        sB = str(int(255*b))    

        # update dict
        coordinates["CIE XYZ"] = [f'{coordinate:4.6f}' for coordinate in colour_xyz.coordinates]
        coordinates["CIE xyY"] = [f'{coordinate:4.6f}' for coordinate in colour_xyY.coordinates]
        coordinates["CIELAB"] = [f'{coordinate:4.6f}' for coordinate in colour_lab.coordinates]
        coordinates["CIE LCHab"] = [f'{coordinate:4.6f}' for coordinate in colour_lchab.coordinates]
        coordinates["CIE LCHuv"] = [f'{coordinate:4.6f}' for coordinate in colour_lchuv.coordinates]
        coordinates["CIELUV"] = [f'{coordinate:4.6f}' for coordinate in colour_luv.coordinates]
        
        #coordinates["CIE XYZ"] = [f'{CIEXYZ_X:4.6f}', f'{CIEXYZ_Y:4.6f}', f'{CIEXYZ_Z:4.6f}']
        #coordinates["CIE xyY"] = [f'{CIExyY_x:4.6f}', f'{CIExyY_y:4.6f}', f'{CIExyY_Y:4.6f}']
        #coordinates["CIELAB"] = [f'{CIELAB_L:4.6f}', f'{CIELAB_a:4.6f}', f'{CIELAB_b:4.6f}']
        #coordinates["CIE LCHab"] = [f'{CIELCHab_L:4.6f}', f'{CIELCHab_C:4.6f}', f'{CIELCHab_Hab:4.6f}']
        #coordinates["CIE LCHuv"] = [f'{CIELCHuv_L:4.6f}', f'{CIELCHuv_C:4.6f}', f'{CIELCHuv_Huv:4.6f}']
        #coordinates["CIELUV"] = [f'{CIELUV_L:4.6f}', f'{CIELUV_U:4.6f}', f'{CIELUV_V:4.6f}']
        
        coordinates["sRGB"] = [sR, sG, sB]
        
        return coordinates

    # CDE - Colour Differences
    def compute_colour_difference(self, data_sample_1, data_sample_2):
        coordinates = {}
        # colour space conversion 
        # LAB
        LAB1 = self.colour_to_LAB(data_sample_1)
        L1, a1, b1 = LAB1.coordinates
        coordinates["CIELAB 1"] = [f'{L1:4.6f}', f'{a1:4.6f}', f'{b1:4.6f}']
        LAB2 = self.colour_to_LAB(data_sample_2)
        L2, a2, b2 = LAB2.coordinates
        coordinates["CIELAB 2"] = [f'{L2:4.6f}', f'{a2:4.6f}', f'{b2:4.6f}']
        cie76 = LAB1.delta_e_ab(LAB2)
        ciede2000 = LAB1.CIEDE2000(LAB2)
        #sRGB
        r1,g1,b1 = LAB1.to_RGB().coordinates
        sR1 = int(255*r1)
        sG1 = int(255*g1)
        sB1 = int(255*b1) 
        coordinates["sRGB 1"] = [sR1, sG1, sB1]
        r2,g2,b2 = LAB2.to_RGB().coordinates
        sR2 = int(255*r2)
        sG2 = int(255*g2)
        sB2 = int(255*b2)  
        coordinates["sRGB 2"] = [sR2, sG2, sB2]
        
        return coordinates, f'{cie76:4.6f}', f'{ciede2000:4.6f}'

    def colour_to_LAB(self, data):
        sample_id = data["sample_id"]
        colour_space = data["colour_space"]
        illuminant = data["illuminant"]
        observer = data["observer"]
        c1 = data["coordinates"][0]
        c2 = data["coordinates"][1]
        c3 = data["coordinates"][2]

        # To CIEXYZ illuminat as is
        if colour_space == "CIE XYZ":
            XYZ = CIEXYZ(sample_id, c1, c2, c3, illuminant, observer)
        elif colour_space == "CIE xyY":
            colour = CIExyY(sample_id, c1, c2, c3, illuminant, observer)
            XYZ = colour.to_XYZ()
        elif colour_space == "CIELAB":
            colour = CIELAB(sample_id, c1, c2, c3, illuminant, observer)    
            XYZ = colour.to_XYZ()
        elif colour_space == "CIE LCHab":
            colour = CIELCHab(sample_id, c1, c2, c3, illuminant, observer)
            XYZ = colour.to_XYZ()
        elif colour_space == "CIE LCHuv":
            colour = CIELCHuv(sample_id, c1, c2, c3, illuminant, observer)
            XYZ = colour.to_XYZ()
        elif colour_space == "CIELUV":
            colour = CIELUV(sample_id, c1, c2, c3, illuminant, observer)
            XYZ = colour.to_XYZ()
        
        # sRGB CIEXYZ To D65
        if illuminant!="D65":
            XYZ_d65 = XYZ.to_CIE_illuminant(to_cie_illuminant_name="D65", to_observer=observer, cat_model="von Kries")
            # To LAB D65
            LAB = XYZ_d65.to_LAB()
        else:
            LAB = XYZ.to_LAB()
        return LAB

    # SPC - Spectral Colour
    def create_spc_figure(self, json_data, path_img):
        name_id = json_data["Sample_id"]
        illuminant = json_data["Illuminant"].upper()
        observer = json_data["Observer"]
        nm_range = json_data["nm_range"]
        nm_interval = int(json_data["nm_interval"])
        lambda_values = json_data["lambda_values"]
        spc_colour = SpectralColour(name_id, nm_range, nm_interval, lambda_values, illuminant, observer)
        # create figure
        spc_colour.plot(show_figure = False, save_figure = True, output_path = path_img)
        return spc_colour
    
    def compute_colour_coordinates_from_spc(self, spc_colour):
        # compute colour transform
        X, Y, Z = spc_colour.to_XYZ()
        XYZ = CIEXYZ(spc_colour.name_id, X, Y, Z, spc_colour.illuminant, spc_colour.observer)
        x, y, Y = XYZ.to_xyY().coordinates
        L, a, b = XYZ.to_LAB().coordinates

        # sRGB should be referred to D65
        if spc_colour.illuminant.illuminant_name != "D65":
            spc_colour_d65 = SpectralColour(spc_colour.name_id, spc_colour.nm_range, spc_colour.nm_interval, spc_colour.lambda_values, "D65", spc_colour.observer)
            X_, Y_, Z_ = spc_colour_d65.to_XYZ()
            XYZ_ = CIEXYZ(spc_colour_d65.name_id, X_, Y_, Z_, spc_colour_d65.illuminant, spc_colour_d65.observer)
            r_, g_, b_ = XYZ_.to_RGB().coordinates
        else:
            r_, g_, b_ = XYZ.to_RGB().coordinates
        
        sR = str(int(255*r_))
        sG = str(int(255*g_))
        sB = str(int(255*b_))    

        # update dict
        coordinates = {}
        coordinates["CIE XYZ"] = [f'{X:4.6f}', f'{Y:4.6f}', f'{Z:4.6f}']
        coordinates["CIE xyY"] = [f'{x:4.6f}', f'{y:4.6f}', f'{Y:4.6f}']
        coordinates["CIELAB"] = [f'{L:4.6f}', f'{a:4.6f}', f'{b:4.6f}']
        coordinates["sRGB"] = [sR, sG, sB]
        
        return coordinates
    
    def check_spc_labels(self, label, data):
        if label =="observer":
            valid_observer = [2, 10]
            observer = data
            if isinstance(observer, str):
                try:
                    observer = int(observer)
                    if observer not in valid_observer:
                        return False
                    else:
                        return True
                except:
                    return False
            else:
                observer = int(observer)
                if observer not in valid_observer:
                    return False
                else:
                    return True            
                
        elif label =="illuminant":
            valid_illuminant = ["D65", "D50"]
            illuminant = data
            if isinstance(illuminant, str):
                if illuminant.upper() not in valid_illuminant:
                    return False
                else:
                    return True
        elif label == "nm_range":
            nm_range = data
            if isinstance(nm_range, list):
                if len(nm_range)>2:
                    return False
                else:
                    try:
                        # range
                        nm_min = int(nm_range[0])     
                        nm_max = int(nm_range[1])
                        if nm_min>nm_max:
                            return False
                        else:
                            return True
                    except:
                        return False   
        elif label =="nm_interval":
            try:
                nm_interval = int(data)
                return True
            except:
                return False
    
    def check_lambda_values(self, nm_range, nm_interval, lambda_values):
        if isinstance(lambda_values, list):
            nm_min = int(nm_range[0])
            nm_interval = int(nm_interval)
            nm_max = int(nm_range[1]) + nm_interval
            lambda_labels = len([x for x in range(nm_min, nm_max, nm_interval)])
            if lambda_labels!=len(lambda_values):
                return False
            else:
                return True
        else:
            return False
    
    # Plot
    def save_cielab_diagram(self, samples, path_out):
        cpt.plot_cielab(samples, show_figure = False, save_figure = True, output_path = path_out)

    # Plot
    def create_chromaticity_and_cielab_plot(self, sample_id, input_colour_space, illuminant, observer, c1, c2, c3, path_out_chroma, path_out_cielab):
        # create objects
        if input_colour_space == "CIE XYZ":
            colour = CIEXYZ(sample_id, c1, c2, c3, illuminant, observer)
            colour.to_xyY().plot(show_figure = False, save_figure = True, output_path = path_out_chroma)
            colour.to_LAB().plot(show_figure = False, save_figure = True, output_path = path_out_cielab)
            
        elif input_colour_space == "CIE xyY":
            colour = CIExyY(sample_id, c1, c2, c3, illuminant, observer)
            colour.plot(show_figure = False, save_figure = True, output_path = path_out_chroma)
            colour.to_LAB().plot(show_figure = False, save_figure = True, output_path = path_out_cielab)

        elif input_colour_space == "CIELAB":
            colour = CIELAB(sample_id, c1, c2, c3, illuminant, observer)
            colour.plot(show_figure = False, save_figure = True, output_path = path_out_cielab)
            colour.to_xyY().plot(show_figure = False, save_figure = True, output_path = path_out_chroma)
    
    # SPD

    # illuminant_type = "CIE", "CTT", "User"
    def create_spd_figure(self, illuminant_name, illuminant_type, path_img, path_spd=None):
        if illuminant_type == "CIE":
            illuminant = Illuminant(illuminant_name)
        elif illuminant_type == "CCT":
            illuminant = IlluminantFromCCT(illuminant_name)
        elif illuminant_type == "Measured":
            illuminant = MeasuredIlluminant(illuminant_name=illuminant_name, path_file = path_spd, normalised=True)
        
        # create default image
        illuminant.plot(show_figure = False, save_figure = True, output_path = path_img)
                
        return illuminant
    
    def get_spd_white_point(self, illuminant, observer, illuminant_type):
        coordinates = {}
        coordinates["theoretical"] = {}
        coordinates["computed"] = {}
        # get theoretical, only for some CIE illuminants
        if illuminant_type=="CIE":    
            Xnt, Ynt, Znt = illuminant.get_theoretical_white_point_XYZ(observer)
            if Xnt!= None:
                coordinates["theoretical"]["CIE XYZ"] = [f'{Xnt:4.6f}', f'{Ynt:4.6f}', f'{Znt:4.6f}']
                XYZt = CIEXYZ("Theoretical WP", Xnt, Ynt, Znt, illuminant, observer)
                xt, yt, Yt = XYZt.to_xyY().coordinates
                coordinates["theoretical"]["CIE xyY"] = [f'{xt:4.6f}', f'{yt:4.6f}', f'{Yt:4.6f}']
            else:
                coordinates["theoretical"]["CIE XYZ"] = ["None", "None", "None"]
                coordinates["theoretical"]["CIE xyY"] = ["None", "None", "None"]
        else:
            coordinates["theoretical"]["CIE XYZ"] = ["None", "None", "None"]
            coordinates["theoretical"]["CIE xyY"] = ["None", "None", "None"]

        Xnc, Ync, Znc = illuminant.compute_white_point_XYZ(observer)
        coordinates["computed"]["CIE XYZ"] = [f'{Xnc:4.6f}', f'{Ync:4.6f}', f'{Znc:4.6f}']
        xnc, ync = illuminant.compute_white_point_xy(observer)
        coordinates["computed"]["CIE xyY"] = [f'{xnc:4.6f}', f'{ync:4.6f}', f'{Ync:4.6f}']        
        
        return coordinates
        
    # CCI - ColourChecker
    def get_full_data_colourchecker(self, colourchecker_name):
        checker_id = [name for name, full_name in self.__colour_checker_implemented.items() if full_name == colourchecker_name]
        self.current_colourchecker = checker_id[0]
        metadata = self.current_colourchecker.metadata
        # add items
        metadata["nm_range"] = f"{self.current_colourchecker.nm_range[0]} , {self.current_colourchecker.nm_range[1]}"
        metadata["nm_interval"] = str(self.current_colourchecker.nm_interval)
        metadata["num_patches"] = str(len(self.current_colourchecker.data["patches"].keys()))
        metadata["patches"] = self.current_colourchecker.data["patches"]
        return metadata
    
    def plot_reflectance_patche(self, patch_id, path_img):
        self.current_colourchecker.plot_patches([patch_id], show_figure = False, save_figure = True, output_path = path_img) 
    
    def patch_spectral_to_XYZ(self, patch_id):
        csc_coordinates={}
        X, Y, Z  = self.current_colourchecker.patch_spectral_to_XYZ(patch_id)
        # CSC
        XYZ = CIEXYZ(patch_id, X, Y, Z, self.current_colourchecker.illuminant, self.current_colourchecker.observer)
        x, y, _ = XYZ.to_xyY().coordinates
        L, a, b = XYZ.to_LAB().coordinates

        # sRGB should be referred to D65
        if self.current_colourchecker.illuminant.illuminant_name != "D65":
            rfc_d65 = Reflectance(patch_id, self.current_colourchecker.nm_range, self.current_colourchecker.nm_interval, self.current_colourchecker.get_patch_lambda_values(patch_id), "D65", self.current_colourchecker.observer)
            X_, Y_, Z_ = rfc_d65.to_XYZ()
            XYZ_ = CIEXYZ(patch_id, X_, Y_, Z_, rfc_d65.illuminant, rfc_d65.observer)
            r_, g_, b_ = XYZ_.to_RGB().coordinates
        else:
            r_, g_, b_ = XYZ.to_RGB().coordinates
        
        sR = str(int(255*r_))
        sG = str(int(255*g_))
        sB = str(int(255*b_))    

        csc_coordinates["CIE XYZ"] = [f'{X:4.6f}', f'{Y:4.6f}', f'{Z:4.6f}']
        csc_coordinates["CIE xyY"] = [f'{x:4.6f}', f'{y:4.6f}', f'{Y:4.6f}']
        csc_coordinates["CIELAB"] = [f'{L:4.6f}', f'{a:4.6f}', f'{b:4.6f}']
        csc_coordinates["sRGB"] = [sR, sG, sB]

        return csc_coordinates

    def metadata_from_json(self, json_data):
        # create current colourchecker
        self.current_colourchecker = json_data

        metadata = {}
        metadata["Instrument"] = json_data["Illuminant"]
        metadata["Measurement Date"] = json_data["Measurement Date"]
        metadata["NameColorChart"] = json_data["NameColorChart"]
        metadata["Illuminant"]=json_data["Illuminant"]
        metadata["Observer"]=json_data["Observer"]
        metadata["Date"] = json_data["Measurement Date"]
        metadata["nm_range"] = f"{self.current_colourchecker.nm_range[0]} , {self.current_colourchecker.nm_range[1]}"
        metadata["nm_interval"] = str(self.current_colourchecker.nm_interval)
        metadata["num_patches"] = str(len(self.current_colourchecker.data["patches"].keys()))
        metadata["patches"] = self.current_colourchecker.data["patches"]

        return metadata

    # RCIP
    def create_raw_image(self, path_raw):
        self.current_raw_image = RawImage(path_raw)

    def compute_white_balanced_raw_image(self, wb_multipliers):
        self.current_raw_image.set_whitebalance_multipliers(wb_multipliers)
        self.current_raw_image.apply_white_balance()

    def compute_colour_corrected_raw_image(self, wb_multipliers, RGB_to_XYZ):
        self.current_raw_image.set_whitebalance_multipliers(wb_multipliers)
        self.current_raw_image.set_RGB_to_XYZ_matrix(RGB_to_XYZ)
        self.current_raw_image.apply_colour_correction()

    def save_raw_image(self, output_path, data, bits):
        self.current_raw_image.save(output_path, data, bits)

    def get_output_bits_from_extension(self, output_path):
        filename, file_extension = os.path.splitext(output_path)
        extension = file_extension.lower().split(".")[1]
        bits = 8 if extension in ["jpg", "JPG", "jpeg", "JPEG"] else 8
        return bits

    def load_matrix_coefficients_from_csv(self, path_csv):
        rgb_to_xyz_array = []
        with open(path_csv, "r", encoding="utf-8") as file_csv:
            for linea in file_csv:
                try:
                    c1, c2, c3 = linea.split(";")
                    rgb_to_xyz_array.append([float(c1), float(c2), float(c3)])
                except:
                    return None
        return rgb_to_xyz_array
            
from abc import ABC
from abc import abstractmethod
import copy
import os

import cv2
import math
import numpy as np
import rawpy

from coolpi.auxiliary.errors import CIEIlluminantError, ClassMethodError, ColourCheckerError, FileImageError, PatchError
import coolpi.auxiliary.load_data as ld
import coolpi.auxiliary.common_operations as cop
import coolpi.auxiliary.plot as cpt
from coolpi.colour.cie_colour_spectral import Illuminant, IlluminantFromCCT, MeasuredIlluminant, Observer
import coolpi.image.patch_extraction as pte
import coolpi.image.raw_colour_correction as rcc
import coolpi.image.raw_image_assessment as rwa
import coolpi.image.raw_operations as rwo
import coolpi.image.raw_processing as rwp
import coolpi.image.white_balance as wb
from coolpi.image.colourchecker import ColourCheckerSpectral, ColourCheckerXYZ, ColourCheckerRGB

class Image(ABC):
    ''' 
    Image abstrac class

    Attributes:
        type                   str                   "Image object".
        path                   os                    Image path.
        rgb_data               numpy.array           RGB data.
        illuminant             Illuminant,           Illuminant.
                               IlluminantFromCCT
                               MeasuredIlluminant
        observer               Observer              CIE Observer.
        metadata               dict                  Image information as metadata (if available).
        colourchecker_RGB      dict                  ColourCheckerRGB data as dict: {checker_name: ColourCheckerRGB}.
        
    Methods:
        .set_metadata(metadata)
        .set_image_illuminant(illuminant)
        .set_observer(observer)
        .extract_rgb_patch_data_from_image(center, size)
        .extract_colourchecker_rgb_patches(colourchecker_name, corners_image, parameters_draw)
        .get_ColourCheckerRGB(checker_name)
        .get_patch_from_colourchecker(colourchecker_name, patch_id)
        .show_colourchecker(checker_name, parameters_draw, show_image, method, save_image, output_path, bits)
        .plot_rgb_histogram(show_figure, save_figure, output_path, split_per_channel)
        .show(method)
        .save(output_path, bits)

    '''

    __type = "Image object"
    __path = None
    __metadata = None
    __rgb_data = None
    __illuminant = None
    __observer = None 
    __colourchecker_RGB = {} # dict objects only property, not setter
    __patch_size = {}

    @property
    def type(self):
        return self.__type

    @property
    def path(self):
        return self.__path
    
    @path.setter
    def path(self, path_img):
        self.__path = path_img

    @property
    def metadata(self):
        return self.__metadata
    
    @metadata.setter
    def metadata(self, metadata):
        self.__metadata = metadata

    def set_metadata(self, metadata):
        self.metadata = metadata

    @property
    def rgb_data(self):
        return self.__rgb_data
    
    @rgb_data.setter
    def rgb_data(self, rgb_data):
        self.__rgb_data = rgb_data

    @property
    def illuminant(self):
        return self.__illuminant

    @illuminant.setter
    def illuminant(self, illuminant):
        if isinstance(illuminant, str):
            if ld.illuminant_is_cie(illuminant):
                self.__illuminant = Illuminant(illuminant)
            else:
                raise CIEIlluminantError("The input illuminant is not a valid CIE standard illuminant")
        elif isinstance(illuminant, Illuminant):
            self.__illuminant = illuminant
        elif isinstance(illuminant, MeasuredIlluminant):
            self.__illuminant = illuminant
        elif isinstance(illuminant, IlluminantFromCCT):
            self.__illuminant = illuminant

    def set_image_illuminant(self, illuminant): # setter function easier for users
        self.illuminant = illuminant

    @property
    def observer(self):
        return self.__observer
    
    @observer.setter
    def observer(self, observer):
        if isinstance(observer, Observer):
            self.__observer  = observer
        else:
            self.__observer = Observer(observer)

    def set_observer(self, observer):
        self.observer = observer

    @property
    def colourchecker_RGB(self):
        return self.__colourchecker_RGB

    def get_ColourCheckerRGB(self, checker_name):
        '''
        Method to get a ColourCheckerRGB extracted from the image.

        Parameter:
            checker_name         str                colour checker name.
        
        Returns:
            colourchecker_rgb    ColourCheckerRGB    colour checker.

        '''
        if checker_name in self.colourchecker_RGB.keys():
            return self.colourchecker_RGB[checker_name]["data"]
        else:
            raise ColourCheckerError(f"ColourChecker not present on image: {self.colourchecker_RGB.keys()}")

    def get_patch_from_colourchecker(self, checker_name, patch_id):
        '''
        Method to get the RGB data from a colour patch of a ColourCheckerRGB extracted from the image.

        Parameter:
            checker_name         str            Colour checker name.
            patch_id             str            Patch id.
        
        Returns:
            r,g,b                float          RGB data.

        '''

        if checker_name in self.colourchecker_RGB.keys():
            if patch_id in self.colourchecker_RGB[checker_name]["data"].patches.keys():
                r,g,b = self.colourchecker_RGB[checker_name]["data"].get_patch_data(patch_id)
                return r,g,b
            else:
                raise PatchError(f"Patch id not present in the ColourChecker {checker_name}")
        else:
            raise ColourCheckerError(f"ColourChecker not present on image: {self.colourchecker_RGB.keys()}")

    @property
    def patch_size(self):
        return self.__patch_size

    @abstractmethod
    def __init__(self):
        pass

    # Patch extraction
    def extract_rgb_patch_data_from_image(self, center, size):
        '''
        Method to extract the RGB data of a patch from an image.

        Parameters:
            center    list    Center coordinates of the patch as [x=col, y=row].
            size      int     Patch size in px.

        Returns:
            r,g,b     float    RGB average data.
        
        '''

        crop_patch = pte.crop_patch_image(self.rgb_data, center, size)
        r, g, b = np.average(crop_patch[:,:,0]), np.average(crop_patch[:,:,1]), np.average(crop_patch[:,:,2])
        return r, g, b

    # Extract ColourCheckerRGB
    def extract_colourchecker_rgb_patches(self, checker_name, corners_image, size_rect = 40):
        '''
        Method to extract the RGB data of a colour checker from an image.

        Parameters:
            checker_name     str    Colour checker name.
            corners_image    dict   Colour checker corner coordinaes as {"TopLeft":[x,y], "TopRight":[x,y],"BottomRight":[x.y], "BottomLeft":[x,y]}.
            size_rect        int    Patch size in pz. Default: 40

        '''

        if pte.is_colourchecker_implemented(checker_name):
            checker_coordinates, rgb_patches = pte.patch_extraction(self.rgb_data, checker_name, corners_image, patches_coordinates=None, size_rect=size_rect)            
            checker_name = checker_name.split("_")[0] if "_" in checker_name else checker_name
            self.__patch_size[checker_name] = {}
            self.__patch_size[checker_name]["size_rect"] = size_rect

            # update            
            current_colourchecker_rgb = self.colourchecker_RGB.keys()
            if checker_name not in current_colourchecker_rgb:
                #create new
                colourchecker = ColourCheckerRGB(checker_name=checker_name, illuminant=self.illuminant, observer=self.observer, data=rgb_patches, metadata=self.metadata)
                # update
                self.colourchecker_RGB[checker_name] = {}
                self.colourchecker_RGB[checker_name]["data"] = colourchecker
                self.colourchecker_RGB[checker_name]["draw"] = [checker_coordinates]
            else:
                #update
                self.colourchecker_RGB[checker_name]["data"].update_patches(rgb_patches)
                current_draw = self.colourchecker_RGB[checker_name]["draw"]
                current_draw.append(checker_coordinates)
        else:
            raise ColourCheckerError("ColourChecker not implemented")

    # Histogram
    def plot_rgb_histogram(self, show_figure = True, save_figure = False, output_path = None, split_per_channel = False):
        '''
        Method to create and display the RGB Histogram using Matplotlib.

        Parameters:
            show_figure         bool    If True, the plot is shown. Default: True.
            save_figure         bool    If True, the figure is saved. Default: False. 
            output_path         os      path for the ouput figure. Default: None.
            split_per_channel   bool    If True, show the histogram per channel. Default: False.

        '''
        if split_per_channel:
            cpt.plot_rgb_channel_histogram_split(self.rgb_data, show_figure, save_figure, output_path, title="RGB Histogram")
        else:
            cpt.plot_rgb_channel_histogram(self.rgb_data, show_figure, save_figure, output_path, title="RGB Histogram")
        
    def show_colourchecker(self, checker_name, parameters_draw=None, show_image = True, method ="OpenCV", save_image = False, output_path = None, bits=16):
        '''
        Method to show the patches of a ColourCheckerRGB extracted from the image using OpenCV tools.

        The default draw parameters are as follows:

        params_draw_default = {"radius":5, "thickness":3, "color_corner": (0.5,0,0),
                               "size_rect":40, "color_rect":(0,0,0.5),
                               "size_font":2.5, "thickness_text":3, "color_text": (0,0.5,0)}

        Parameters:
            checker_name       str     Colour checker name.
            parameters_draw    dict    Custom parameters to create the draw. Default: None.
            show_image         bool    If True, the image is shown. Default: True.
            method             str     Method to display the image. Default: "OpenCV".
            save_image         bool    If True, the image is saved. Default: False. 
            output_path        os      path for the ouput figure. Default: None.
            bits               int     Output image bits. Default: 16.

        '''
        # get coordinates
        coordinates_list = self.colourchecker_RGB[checker_name]["draw"]
        rgb_data_with_patches = self.rgb_data.copy()
        for coordinates in coordinates_list:
            corners_dst = coordinates[0]
            patches_dst_xy = coordinates[1]
            rgb_data_with_patches = pte.draw_patches(rgb_data_with_patches, corners_dst, patches_dst_xy, parameters_draw)

        if show_image:
            rwo.show_rgb_as_bgr_image(rgb_data_with_patches, method)

        if save_image:
            rwo.save_rgb_array_as_image(rgb_data_with_patches, output_path, bits)

    # Show image
    def show(self, method="OpenCV"):
        ''' 
        Method to display the RGB data of the image.

        Parameter:
            method    str    Method to display the image. Default: "OpenCV".

        '''
        rwo.show_rgb_as_bgr_image(self.rgb_data, method)

    # Save image
    def save(self, output_path, bits=16):
        ''' 
        Method to save the RGB data of the image.

        Parameter:
            output_path    os    Output path.
            bits           int   Output image bits.

        '''

        rwo.save_rgb_array_as_image(self.rgb_data, output_path, bits)
        self.path = output_path if self.path ==None else self.path # update, for None path


class ProcessedImage(Image):
    '''
    ProcessedImage class

    The ProcessedImage class represents the RGB data extracted from an non-raw image.

    Parameters:
        path_img              os                    Image path.    
        rgb_data              numpy.ndarray         RGB data (e.g. from RawImage)
        metadata              dict                  Image information as metadata. Optional.  

    Attributes:
        subtype                str                   "Processed Image object".
        path                   os                    Image path.
        rgb_data               numpy.array           RGB data
        illuminant             Illuminant,           Illuminant
                               IlluminantFromCCT
                               MeasuredIlluminant
        observer               Observer              CIE Observer 
        metadata               dict                  Image information as metadata (if available).
        colourchecker_RGB      dict                  ColourCheckerRGB data as dict: {checker_name: ColourCheckerRGB}

    Methods:
        .set_metadata(metadata)
        .set_image_illuminant(illuminant)
        .set_observer(observer)
        .get_patch_from_colourchecker(colourchecker_name, patch_id)
        .extract_rgb_patch_data_from_image(center, size)
        .extract_colourchecker_rgb_patches(colourchecker_name, corners_image, parameters_draw)
        .get_ColourCheckerRGB(checker_name)
        .plot_colourchecker(colourchecker_name, show_figure, save_figure, output_path, method, parameters_draw, bits)
        .plot_rgb_histogram(show_figure, save_figure, output_path, split_per_channel)
        .show(method)
        .save(output_path, bits)

    '''

    __subtype = "Processed Image object"


    @property
    def subtype(self):
        return self.__subtype

    # from path
    # from data (e.g. processed image dat from RawImage)
    def __init__(self, path_img=None, rgb_data=None, metadata={}):
        self.metadata = metadata
        self.path = path_img
        if self.path!=None:
            if os.path.exists(self.path):
                self.__load__rgb_data__()
        else:
            self.rgb_data = rgb_data

        self.observer = metadata["observer"] if "observer" in metadata.keys() else 2 # default 2 observer
        self.illuminant = metadata["illuminant"] if "illuminant" in metadata.keys() else None
        
        self.colourchecker_RGB.clear() # reset
        self.patch_size.clear()

    def __load__rgb_data__(self):
        self.rgb_data = rwo.load_rgb_image_openCV(self.path)

    def __str__(self):
        if self.path != None:
            return f"ProcessedImage object from path: {self.path}"
        else:
            return f"ProcessedImage object from RawImage: {self.metadata['path_raw']}"


# metadata = {"Camera": "Nikon D5600", "image_size": [col, row], "Date": [[2021, 11, 26], [11, 17, 00]], "ColourChecker": "CCSDG"}
# implement using EXIF (only for processed images)

class RawImage(Image):
    '''
    RawImage class

    The RawImage class represents the RGB RAW data extracted from a RAW image.

    Parameters:
        path_raw                 os                     Image path.
        metadata                 dict                   Image information as metadata.
        method                   str                    Method to get the RAW RGB demosaiced data. Default: "postprocess".

    Attributes:
        subtype                   str                    "RAW Image object"   
        path                      os                    Image path.
        rgb_data                  numpy.array           RGB data.
        illuminant                Illuminant,           Illuminant.
                                  IlluminantFromCCT
                                  MeasuredIlluminant
        observer                  Observer              CIE Observer.
        metadata                  dict                  Image information as metadata (if available).
        colourchecker_RGB         dict                  ColourCheckerRGB data as dict: {checker_name: ColourCheckerRGB}.

        raw_attributes            dict                  Attributes of the raw image extracted using rawpy.
        RGB_to_XYZ_matrix         numpy.ndarray         Colour transform matrix.
        whitebalance_multipliers  list                  White balance multipliers.
        raw_rgb_wb                numpy.ndarray         RGB white balanced image data.
        xyz_data                  numpy.ndarray         XYZ computed data.
        sRGB_data                 numpy.ndarray         sRGB non linear image data.
        computed_matrix           bool                  True for RGB to XYZ computed matrix. Otherwise, use the camera embedded XYZ to CAM matrix.

    Methods:
        .get_raw_image_information()
        .get_raw_single_channel_from_metadata()

        .automatic_image_processing(show_image, save_image, output_path, method, **krawargs)

        .get_camera_whitebalance()
        .get_daylight_whitebalance()

        .compute_wb_multipliers(**params)
        .estimate_wb_multipliers(method, **params)
        .set_whitebalance_multipliers(wb_multipliers)
        .get_whitebalance_multipliers()
        .apply_white_balance(show_image, method, save_image, output_path, bits)
        .get_raw_rgb_white_balanced_image()

        .set_RGB_to_XYZ_matrix(RGB_to_XYZ)
        .apply_colour_correction(show_image, method, save_image, output_path, bits)
        .get_colour_corrected_image()

        .compute_image_colour_quality_assessment(colourchecker_name)
        .show(data, method)
        .save(output_path, data, bits)

    '''

    __subtype = "RAW Image object"
    __path = None
    __raw_attributes = None
    __RGB_to_XYZ_matrix = None   
    __whitebalance_multipliers = None
    __raw_rgb_wb = None
    __xyz_data = None # D65
    __sRGB_data = None
    __computed_matrix = False # default

    @property
    def subtype(self):
        return self.__subtype

    @property
    def path(self):
        return self.__path
    
    @path.setter
    def path(self, path_img):
        if os.path.exists(path_img):
            self.__path = path_img
        else:
            raise FileImageError("File not found")

    @property
    def raw_attributes(self):
        return self.__raw_attributes

    def __get_raw_attributes__(self):
        self.raw_attributes = rwp.get_raw_attributes(self.path)
        
    def get_raw_image_information(self):
        '''
        Method to get the raw_attributes of the image
        '''
        return self.raw_attributes

    def get_raw_single_channel_from_metadata(self):
        '''
        Method to get the original raw_image using rawpy.
        
        Plase, consider the sensor rotation angle if aplicable.

        '''
        return self.raw_attributes["raw_image"]

    def get_camera_embedded_XYZ_to_CAM_matrix(self):
        '''
        Method to get the embedded XYZ to CAM tranform matrix from the raw_attributes of the image.
        '''
        return self.raw_attributes["xyz_cam_matrix"]

    @raw_attributes.setter
    def raw_attributes(self, raw_attributes):
        self.__raw_attributes = raw_attributes

    @property
    def RGB_to_XYZ_matrix(self):
        return self.__RGB_to_XYZ_matrix

    @RGB_to_XYZ_matrix.setter
    def RGB_to_XYZ_matrix(self, rgb_to_xyz):
        if isinstance(rgb_to_xyz, str):
            if rgb_to_xyz == "camera":
                XYZ_to_CAM = self.get_camera_embedded_XYZ_to_CAM_matrix()
                if XYZ_to_CAM.shape[0]==4:
                    XYZ_to_CAM = XYZ_to_CAM[0:3,:]
                MI = cop.compute_inverse_array(XYZ_to_CAM)
                self.__RGB_to_XYZ_matrix = MI
                self.__computed_matrix=False
        elif isinstance(rgb_to_xyz, list):
            self.__RGB_to_XYZ_matrix = np.array(rgb_to_xyz, dtype = np.double)
            self.__computed_matrix=False
        elif isinstance(rgb_to_xyz, np.ndarray):
            self.__RGB_to_XYZ_matrix = rgb_to_xyz
            self.__computed_matrix=False

    def set_RGB_to_XYZ_matrix(self, RGB_to_XYZ): # setter function easier for users
        self.RGB_to_XYZ_matrix = RGB_to_XYZ

    @property
    def whitebalance_multipliers(self):
        return self.__whitebalance_multipliers
    
    @whitebalance_multipliers.setter
    def whitebalance_multipliers(self, wb_multipliers):
        # "camera", "daylight", None [1,1,1,1], [r_gain, g_gain, b_gain, g_gain]
        self.__whitebalance_multipliers = self.__get_wb_list_gain_factors__(wb_multipliers)

    def __get_wb_list_gain_factors__(self, whitebalance):
        if whitebalance == "camera":
            wb_list_gain_factors = self.get_camera_whitebalance()
        elif whitebalance == "daylight":
            wb_list_gain_factors = self.get_daylight_whitebalance()
        elif whitebalance == None:
            wb_list_gain_factors = [1,1,1,1]
        elif isinstance(whitebalance, list):
            wb_list_gain_factors = whitebalance
        else:
            raise Exception("Whitebalance gain values wrong type.") # improve
        return wb_list_gain_factors

    def get_camera_whitebalance(self):
        '''
        Method to get the camera white balance multipliers from raw_attributes.
        '''
        return self.raw_attributes["camera_whitebalance"]
    
    def get_daylight_whitebalance(self):
        '''
        Method to get the camera daylight white balance multipliers from raw_attributes.
        '''
        return self.raw_attributes["daylight_whitebalance"]

    def set_whitebalance_multipliers(self, wb_multipliers):
        '''
        Method to set the white balance multipliers of an image.

        Options: "camera", "daylight", None ([1,1,1,1] is setted) or custom = [r_gain, g_gain, b_gain, g_gain2]

        Parameters:
            wb_multipliers   str, list   wb multipliers.

        '''
        self.whitebalance_multipliers = wb_multipliers

    def get_whitebalance_multipliers(self):
        return self.whitebalance_multipliers

    @property
    def raw_rgb_wb(self):
        return self.__raw_rgb_wb

    def get_raw_rgb_white_balanced_image(self):
        '''
        Method to get the white balanced image.

        Returns:
            raw_rgb_wb    numpy.ndarray    White balanced image.

        '''
        return self.__raw_rgb_wb

    @property
    def xyz_data(self):
        return self.__xyz_data

    def __set_xyz_data__(self, xyz):
        self.__xyz_data = xyz

    @property
    def sRGB_data(self):
        return self.__sRGB_data

    def __set_sRGB_data__(self, sRGB_data):
        self.__sRGB_data = sRGB_data

    def get_colour_corrected_image(self):
        return  self.sRGB_data

    # metadata = {"Camera": "Nikon D5600", "image_size":[4008, 6008], "Date": [[2022, 6, 19], [8, 29, 00]], "ColorChecker": "XRCCPP", "illuminant": illuminant, "observer": obs}
    def __init__(self, path_raw, metadata={}, method="postprocess"):
        self.path = path_raw
        self.metadata = metadata

        self.observer = metadata["observer"] if "observer" in metadata.keys() else 2 # default 2 observer
        self.illuminant = metadata["illuminant"] if "illuminant" in metadata.keys() else None

        self.__get_raw_attributes__() # [0]
        self.__load_rgb_data__(method) # [1]
        
        self.colourchecker_RGB.clear() # reset
        self.patch_size.clear()

    # load RGB data
    def __load_rgb_data__(self, method):
        method = "postprocess" if method==None else method # Avoid error if method = None. Use default
        methods_implemented = ["raw_image", "postprocess"]
        if method not in methods_implemented:
            raise ClassMethodError(f"Method to get the raw_rgb_demosaiced data not implemented: {methods_implemented}")
        else:
            image_size = self.metadata["image_size"] if "image_size" in self.metadata.keys() else self.raw_attributes["processed_image_size"]
            if method == "postprocess":            
                self.rgb_data = rwp.compute_raw_demosaiced_visible_using_postprocess_rawpy(self.path, shape_visible=image_size)
            else:
                self.rgb_data = rwp.get_raw_image_demosaiced_visible_subtrack_black(self.path, shape_visible=image_size)

    # to use a user white balance:
    # krawargs = dict(use_camera_wb=False, use_auto_wb=False, user_wb=[1.185664, 1.0, 2.636556, 1.0])
    def automatic_image_processing(self, show_image = True, save_image = False, output_path = None, method="OpenCV", **krawargs):
        '''
        Method for the automatic processing of the RAW image (using rawpy.postprocess).

        Parameters:
            show_image       bool              If True, the image is shown. Default: True.
            save_image       bool              If True, the image is saved. Default: False.
            output_path      os                Output path to save the processed image. Default: None.
            method           str               Method to show the image (if show_image=True). Default: "OpenCV".
                                               "OpenCV", "matplotlib"
            krawargs         dict              Optional parameters.
                                               e.g. to use a custom white balance
                                               krawargs = dict(use_camera_wb=False, use_auto_wb=False, user_wb=[1.185664, 1.0, 2.636556, 1.0])
        
        Returns:
            processed_img    ProcessedImage    Processed image.

        '''
        
        rgb_processed = rwp.automatic_raw_image_processing(self.path, **krawargs)
        additional_keys = dict(image_size=[rgb_processed.shape[0], rgb_processed.shape[1]], path_raw = self.path)
        metadata = self.metadata
        metadata.update(additional_keys)
        if show_image:
            rwo.show_rgb_as_bgr_image(rgb_processed, method)
            processed_img = ProcessedImage(path_img=output_path, rgb_data=rgb_processed, metadata=self.metadata)
        if save_image:
            rwo.save_rgb_array_as_image(rgb_processed, output_path, bits=rwo.get_bits_image(rgb_processed))
            processed_img = ProcessedImage(path_img=output_path, metadata=self.metadata)

        return processed_img # rgb_processed 

    # [2] Compute WB multipliers

    # params = dict(colourchecker_name=str, patch_id=str)
    # params = dict(patch_rgb=[r,g,b])

    def compute_wb_multipliers(self, **params):
        '''
        Method to compute the raw wb multipliers from a given patch.
        
        To compute the wb multipliers from a patch of a ColourCheckerRGB extracted from image use:
            params = dict(colourchecker_name=str, patch_id=str)

        To compute the wb multipliers from a r,g,b values use:
            params = dict(patch_rgb=[r,g,b])

        Parameter:
            params            dict    Parameters as dict.

        Returns:
            wb_multipliers    list    Computed wb multipliers.
        
        '''
        # crompute from a grey patch of a colourchecker
        if "colourchecker_name" and "patch_id" in params.keys():
            wb_multipliers = self.__compute_white_balance_multipliers_from_grey_patch__(params["colourchecker_name"], params["patch_id"])

        if "patch_rgb" in params.keys():
            r, g, b = params["patch_rgb"]
            wb_multipliers = wb.compute_wb_multipliers(r,g,b)
        return wb_multipliers

    def __compute_white_balance_multipliers_from_grey_patch__(self, colourchecker_name, patch_id):
        r_grey, g_grey, b_grey = self.get_patch_from_colourchecker(colourchecker_name, patch_id)
        computed_wb_multipliers = wb.compute_wb_multipliers(r_grey, g_grey, b_grey)
        return list(computed_wb_multipliers)

    # [2] Estimate WB multipliers

    # method="wb_algorithm",
    # method="illuminant", params = dict(use_transform_matrix="embedded") # "embedded", "computed"
    def estimate_wb_multipliers(self, method, **params):
        '''
        Method to estimate the raw wb multipliers of an image.

        Methods implemented: "wb_algorithm", "illuminant".

        To estimate the wb multipliers using a wb algorithm use:
            params = dict(algorithm=str, remove_colourckecker=bool, corners_colourchecker=dict)
            wb algorithms implemented: "Average", "GreyWorld", "MaxWhite", "Retinex".
        
        To estimate from the illuminant:
            params = dict(use_transform_matrix="embedded") 
            the methods uses the "embedded" or the "computed" RGB to XYZ transforma matrix

        Parameter:
            method            str     Method to estimate the wb multipliers.
            params            dict    Parameters as dict.

        Returns:
            wb_multipliers    list    Estimated wb multipliers.
        
        '''

        methods_implemented = ["wb_algorithm", "illuminant"]
        if method not in methods_implemented:
            raise ClassMethodError(f"Method to estimate the white balance multipliers not implemented: {methods_implemented}")
        elif method== "wb_algorithm":
            algorithm = params["algorithm"] if "algorithm" in params.keys() else "GreyWorld"
            remove_colourckecker= params["remove_colourckecker"] if "remove_colourckecker" in params.keys() else False # Default
            corners_colourchecker= params["corners_colourchecker"] if "corners_colourchecker" in params.keys() else None # Default
            wb_multipliers = self.__estimate_white_balance_multipliers_using_wb_algorithm__(params["algorithm"], remove_colourckecker,corners_colourchecker)
        elif method=="illuminant":
            use_transform_matrix = params["use_transform_matrix"] if "use_transform_matrix" in params.keys() else "embedded"
            wb_multipliers = self.__estimate_white_balance_multipliers_from_illuminant_white_point__(use_transform_matrix)
        
        # From CCT
        return wb_multipliers

    def __estimate_white_balance_multipliers_using_wb_algorithm__(self, method = "GreyWorld", remove_colourckecker=False, corners_colourchecker=None):
        method = "GreyWorld" if method==None else method
        rgb_data = wb.mask_colourchecker(self.rgb_data, corners_colourchecker, -1) if remove_colourckecker else self.rgb_data
        
        estimated_wb_multipliers = wb.estimate_white_balance_multipliers(rgb_data, method)

        return estimated_wb_multipliers

    def __estimate_white_balance_multipliers_from_illuminant_white_point__(self, use_transform_matrix="embedded"):
        method = "embedded" if use_transform_matrix==None else use_transform_matrix
        
        if method=="embedded":
            # using embedded XYZ to CAM array
            Xn, Yn, Zn = self.illuminant.compute_white_point_XYZ()
            XYZ_to_CAM = self.get_camera_embedded_XYZ_to_CAM_matrix()
            if XYZ_to_CAM.shape[0]==4:
                XYZ_to_CAM = XYZ_to_CAM[0:3,:]

            CAMrgb = np.dot(XYZ_to_CAM, [Xn/100,Yn/100,Zn/100])
            estimated_wb_multipliers = wb.compute_wb_multipliers(CAMrgb[0], CAMrgb[1], CAMrgb[2])
        else:
            if isinstance(self.RGB_to_XYZ_matrix, np.ndarray):
                # using computed RGB to XYZ 
                XYZ_to_RGB = cop.compute_inverse_array(self.RGB_to_XYZ_matrix)
                RGBaw = np.dot(XYZ_to_RGB, [1,1,1])
                r_avg, g_avg, b_avg, _ = wb.get_average_rgb_values(self.rgb_data)
                estimated_wb_multipliers= wb.compute_wb_multipliers(r_avg/RGBaw[0], g_avg/RGBaw[1], b_avg/RGBaw[2])
            else:
                raise ClassMethodError("RGB to XYZ ransformation matrix required: set using .set_RGB_to_XYZ_matrix(RGB_to_XYZ)")
                
        return estimated_wb_multipliers

    # [3] RAW WB RGB 

    def apply_white_balance(self, show_image = False, method="OpenCV", save_image = False, output_path = None, bits=16):
        '''
        Method to apply the wb multipliers to obtain the white balanced image.

        Parameters:
            show_image     bool    If True, the image is shown. Default: True.
            method         str     Method to show the image. Default: "OpenCV".
            save_image     bool    If True, the figure is saved. Default: False. 
            output_path    os      path for the ouput figure. Default: None.
            bits           int     Output image bits. Default: 16.
            
        '''

        if self.whitebalance_multipliers!= None:
            # define a function
            rgb_data_wb = wb.apply_wb_multipliers_to_rgb_image(self.rgb_data, wb_list_gain_factors=self.whitebalance_multipliers)    
            rgb_data_wb = np.array(rgb_data_wb, dtype=np.int16) # to int16
            min_max = np.min([rgb_data_wb[:,:,0].max(),rgb_data_wb[:,:,1].max(),rgb_data_wb[:,:,2].max()])
            rgb_data_wb_clip = np.clip(rgb_data_wb, 0, min_max)
            rgb_data_wb_scaled_norm = rgb_data_wb_clip/rgb_data_wb_clip.max()

            if show_image:
                rwo.show_rgb_as_bgr_image(rgb_data_wb_scaled_norm, method)

            if save_image:
                rwo.save_rgb_array_as_image(rgb_data_wb_scaled_norm, output_path, bits)
            
            self.__raw_rgb_wb = rgb_data_wb_scaled_norm

        else:
            raise Exception("Please set fist the whitebalance multipliers: .set_whitebalance_multipliers(wb_multipliers)")


    # [4] Colour Correction

    def apply_colour_correction(self, show_image=False, method="OpenCV", save_image=False, output_path=None, bits=16):
        '''
        Method to obtain the colour-corrected image.

        Parameters:
            show_image     bool    If True, the image is shown. Default: True.
            method         str     Method to show the image. Default: "OpenCV".
            save_image     bool    If True, the figure is saved. Default: False. 
            output_path    os      path for the ouput figure. Default: None.
            bits           int     Output image bits. Default: 16.
            
        '''
        self.apply_white_balance() 

        rgb_data_wb_scaled_norm = self.raw_rgb_wb

        if self.__computed_matrix:
            # optimised RGB to XYZ array to D65
            XYZd65 = [0.9504, 1.00, 1.0888]
            RGB_to_XYZ = rcc.apply_non_linear_optimization(rcc.compute_model_residuals, self.RGB_to_XYZ_matrix, XYZd65)
            # raw rgb to xyz d65
            self.__set_xyz_data__(rcc.apply_RGB_to_XYZ_transform_matrix(RGB_to_XYZ, rgb_data_wb_scaled_norm))
            # xyz d65 to sRGB
            #sRGB_linear = rcc.apply_xyz_d65_to_rgb_linear(self.XYZ_D65_data, rgb_space="sRGB") # einsum
            sRGB_linear = rcc.apply_xyz_d65_to_rgb_linear_using_dot_product(self.xyz_data, rgb_space="sRGB") # dot
            # test reverse transform
            #self.__set_XYZ_D65_data__(rcc.apply_rgb_linear_to_xyz_d65(sRGB_linear, rgb_space="sRGB"))
            # same results
            
        else: # metadata, use rotation matrix
            # worst results, but I don't know why
            #XYZ_to_sRGB = np.array([[3.2406, -1.5372, -0.4986],[-0.9689, 1.8758, 0.0415], [0.0557, -0.2040,  1.0570]],dtype=np.double)
            #XYZd65 = [0.9504, 1.00, 1.0888]
            #CAM_to_XYZ_norm = rcc.normalise_matrix(self.RGB_to_XYZ_matrix)
            #cam_to_sRGB = np.dot(XYZ_to_sRGB, CAM_to_XYZ_norm)
            #cam_to_sRGB = rcc.normalise_matrix(cam_to_sRGB)
            
            # provisional
            n_colours = self.raw_attributes["num_colours"]
            XYZ_to_cam = np.array(self.raw_attributes["xyz_cam_matrix"][0:n_colours, :], dtype=np.double)
            sRGB_to_XYZ = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]], dtype=np.double)
            sRGB_to_cam = np.dot(XYZ_to_cam, sRGB_to_XYZ)
            norm = np.tile(np.sum(sRGB_to_cam, 1), (3, 1)).transpose()
            sRGB_to_cam = sRGB_to_cam / norm
            cam_to_sRGB = cop.compute_inverse_array(sRGB_to_cam)

            sRGB_linear = np.einsum('ij,...j', cam_to_sRGB, rgb_data_wb_scaled_norm) 
            self.__set_xyz_data__(rcc.apply_rgb_linear_to_xyz_d65(sRGB_linear, rgb_space="sRGB"))

        sRGB_non_linear = rcc.compute_nonlinear_sRGB(sRGB_linear)
        self.__set_sRGB_data__(sRGB_non_linear)

        if show_image:
            rwo.show_rgb_as_bgr_image(self.sRGB_data, method)

        if save_image:
            rwo.save_rgb_array_as_image(self.sRGB_data, output_path, bits)

    # [5] Colour Quality Assessment

    def compute_image_colour_quality_assessment(self, checker_name, data=None):
        '''
        Method to perform the quality assessment of the colour-corrected image obtained.

        Parameters:
            checker_name             str                 Colour checker name.
            data                     ColourCheckerXYZ    Reference XYZ data. Default: None
        
        Returns:
            colourchecker_metrics    DataFrame           CIE XYZ residuals and colour-difference metrics.

        '''
        colourchecker = self.__extract_colourchecker_xyz_patches__(checker_name)
        image_colourchecker = colourchecker.as_pandas_dataframe()
        # rename col
        image_colourchecker.rename(columns = {"X": "X'", "Y": "Y'", "Z": "Z'"}, inplace = True)
        
        if isinstance(data, ColourCheckerXYZ):
           reference_colourchecker = data.as_pandas_dataframe()
        elif ld.is_checker_implemented(checker_name):
            reference_colourchecker = rwa.reference_colourchecker_as_pandas_dataframe(checker_name)
        else:
            raise ClassMethodError("It is not possible to carry out an analysis of the quality of the image.")

        colourchecker_xyz = rwa.merge_colourchecker_dataframe(reference_colourchecker, image_colourchecker)
        colourchecker_metrics = rwa.compute_colour_differences(colourchecker_xyz)
        return colourchecker_metrics

    def __extract_colourchecker_xyz_patches__(self, checker_name):
        if checker_name in self.colourchecker_RGB.keys():
            size_rect = self.patch_size[checker_name]["size_rect"]
            coordinates_list = self.colourchecker_RGB[checker_name]["draw"]
            xyz_data_as_dict = {}
            for coordinates in coordinates_list:
                #corners_image = coordinates[0] # not required
                patches_coordinates = coordinates[1] # dict
                for patch in patches_coordinates.keys():
                    name_id = patch
                    center = patches_coordinates[name_id]
                    x,y,z = self.__extract_xyz_patch_data_from_image(center, size_rect)
                    xyz_data_as_dict[name_id] = [x*100,y*100,z*100]
            colourchecker = ColourCheckerXYZ(checker_name=checker_name, illuminant=self.illuminant, observer=self.observer, data=xyz_data_as_dict, metadata=self.metadata)
            return colourchecker
        else:
            raise ColourCheckerError("ColourChecker not implemented")

    def __extract_xyz_patch_data_from_image(self, center, size):
        crop_patch = pte.crop_patch_image(self.xyz_data, center, size)
        x,y,z = np.average(crop_patch[:,:,0]), np.average(crop_patch[:,:,1]), np.average(crop_patch[:,:,2])
        return x,y,z

    def show(self, data = "raw", method="OpenCV"):
        ''' 
        Method to display the RAW RGB Image ("raw"), the white balanced image ("wb") or the final sRGB image ("sRGB").

        Parameter:
            data      str    Data to show. Default: "raw".
            method    str    Method to display the image. Default: "OpenCV".

        '''
        
        if data=="raw":
            data_to_show = self.rgb_data
        elif data=="wb":
            data_to_show = self.raw_rgb_wb
        elif data == "sRGB":
            data_to_show = self.sRGB_data

        rwo.show_rgb_as_bgr_image(data_to_show, method)

    def save(self, output_path, data = "raw", bits=16):
        ''' 
        Method to save the the RAW RGB Image ("raw"), the white balanced image ("wb") or the final sRGB image ("sRGB").

        Parameter:
            output_path    os     Output path
            data           str    Data to show. Default: "raw".
            bits           int    Output image bits. Default: 16.

        '''
        if data=="raw":
            data_to_save = self.rgb_data
        elif data=="wb":
            data_to_save = self.raw_rgb_wb
        elif data == "sRGB":
            data_to_save = self.sRGB_data

        rwo.save_rgb_array_as_image(data_to_save, output_path, bits)

    def __str__(self):
        return f"RawImage object from path: {self.path}"

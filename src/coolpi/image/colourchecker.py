from abc import ABC
from abc import abstractmethod
from importlib import resources
import json

import numpy as np
import pandas as pd

import coolpi.auxiliary.common_operations as cop
from coolpi.auxiliary.errors import CIEIlluminantError, ClassInstantiateError, ColourCheckerError, DictLabelError, FileExtensionError, PatchError, PlotSpectralSampleError
import coolpi.auxiliary.load_data as ld
import coolpi.auxiliary.export_data as ed
import coolpi.auxiliary.plot as cpt
import coolpi.colour.cat_models as cat
import coolpi.colour.colour_space_conversion as csc
from coolpi.colour.cie_colour_spectral import CIEXYZ, IlluminantFromCCT, WhitePoint, CameraRGB, Illuminant, Observer
from coolpi.colour.cie_colour_spectral import MeasuredIlluminant, Reflectance

class ColourChecker(ABC):    
    ''' 
    ColourChecker abstract class

    Attributes:
        type       str    "ColourChecker object"
        name                    str                  ColourChecker name or description.
        illuminant              Illuminant           Illuminat.
                                IlluminantFromCCT
                                MeasuredIlluminant
        
        observer                Observer             CIE Observer.
        patches                 dict                 spectral data
        patches_id              list                 patches id
        metadata                dict                 Instrument measurement information as dict

    Methods:
        .set_instrument_measurement_as_metadata(metadata)
        .get_colourchecker_number_of_patches()
        .get_patch_data(patch_id)
        .add_patch()
        .remove_patch(patch_id)
        .export_data_to_json_file(path_json)

    '''
    
    __type = "ColourChecker object"
    __name = None
    __illuminant = None 
    __observer = None
    __patches = {}
    __patches_id = []
    __metadata = None

    @property
    def type(self):
        return self.__type

    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, checker_name):
        self.__name = checker_name

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
        elif isinstance(illuminant, IlluminantFromCCT):
            self.__illuminant = illuminant
        elif isinstance(illuminant, MeasuredIlluminant):
            self.__illuminant = illuminant

    @property
    def observer(self):
        return self.__observer
    
    @observer.setter
    def observer(self, observer):
        if isinstance(observer, Observer):
            self.__observer  = observer
        else:
            self.__observer = Observer(observer)

    @property
    def metadata(self):
        return self.__metadata
    
    @metadata.setter
    def metadata(self, metadata):
        #min_metadata_key = []
        self.__metadata = metadata

    def set_instrument_measurement_as_metadata(self, metadata):
        self.metadata = metadata

    @property
    def patches(self):
        return self.__patches

    @patches.setter
    def patches(self, patches):
        self.__patches = patches
        self.__patches_id = patches.keys() # setter

    def __is_valid_patch__(self, patch_id):
        if patch_id not in self.patches.keys():
            raise PatchError("Patch id not present in the current ColourChecker")
        return True

    def get_patch_data(self, patch_id):
        '''
        Method to get the data of a given colour patch

        '''

        if self.__is_valid_patch__(patch_id):
            return self.patches[patch_id]

    @property   
    def patches_id(self):
        return self.__patches_id

    @abstractmethod
    def __init__(self):
        pass

    def get_colourchecker_number_of_patches(self):
        '''
        Method to get the total number of colour patches of the colour checker.

        Returns:
            num_patches    int    Total number of patches.
            
        '''
        return len(self.patches_id)

    def remove_patch(self, patch_id):
        '''
        Method to remove a patch from the colour checker.
        
        Parameter:
            patch_id    str    Patch id.

        '''

        if self.__is_valid_patch__(patch_id):
            del self.patches[patch_id]
            self.__patches_id = self.patches.keys() # update

    @abstractmethod
    def add_patch(self):
        pass

    @abstractmethod
    def export_data_to_json_file(self, path_json):
        pass


class ColourCheckerSpectral(ColourChecker):
    '''
    ColourCheckerSpectral class

    The ColourCheckerSpectral class represents the spectral data of the colour patches of a given colour checker 
    measured using a colorimetric instrument.

    Parameters:
        checker_name            str                 ColourChecker name or description
        data                    dict                Measured data as dict. Default: None
                                                    Required keys: "illuminant", "observer", "nm_range", "nm_interval", "patches" 
        path_json               os                  Valid path. JSON file with the measured data. Default: None
                                                    Required keys: "illuminant", "observer", "nm_range", "nm_interval", "patches"
        metadata                dict                Instrument measurement information as dict. Default: {}

    Attributes:
        subtype                 str                  "ColourCheker Reflectance data".
        name                    str                  ColourChecker name or description.
        illuminant              Illuminant           Illuminat.
                                IlluminantFromCCT
                                MeasuredIlluminant
        
        observer                Observer             CIE Observer.
        nm_range                list                 lambda range [min,max] in nm.
        nm_interval             int                  lambda interval in nm.
        patches                 dict                 spectral data
        patches_id              list                 patches id
        data                    dict                 Full measured data
        metadata                dict                 Instrument measurement information as dict
        scaled                  bool                 True for spectral data into the range (0,1)

    Methods:
        .set_instrument_measurement_as_metadata(metadata)
        .get_colourchecker_number_of_patches()
        .get_patch_data(patch_id)
        .get_patch_lambda_values(patch_id)
        .add_patch(patch_id, nm_range, nm_interval, lambda_values)
        .remove_patch(patch_id)
        .set_reflectance_into_visible_range_spectrum(visible_nm_range, visible_nm_interval)
        .scale_reflectance_data()
        .patch_spectral_to_XYZ(patch_id, illuminant, observer, visible)
        .to_ColourCheckerXYZ(illuminant, observer, visible)
        .to_ColourCheckerLAB(illuminant, observer, visible)
        .as_pandas_dataframe()
        .export_data_to_json_file(path_json)
        .plot_colourchecker(show_figure, save_figure, output_path)
        .plot_patches(patches_id, show_figure, save_figure, output_path)

    '''

    __subtype = "ColourCheker Reflectance data"
    __nm_range = None
    __nm_interval = None
    __data = None 
    __scaled = False

    @property
    def subtype(self):
        return self.__subtype

    @property
    def nm_range(self):
        return self.__nm_range
    
    @nm_range.setter
    def nm_range(self, nm_range):
        self.__nm_range = nm_range

    @property
    def nm_interval(self):
        return self.__nm_interval
    
    @nm_interval.setter
    def nm_interval(self, nm_interval):
        self.__nm_interval = int(nm_interval)
        
    @property
    def data(self):
        return self.__data
    
    @data.setter
    def data(self, data):
        self.__data = data    

    @property
    def scaled(self):
        return self.__scaled
    
    @scaled.setter
    def scaled(self, scaled):
        if isinstance(scaled, bool):
            self.__scaled = scaled

    def __load_patches_reflectance__(self, patches_dict):
        patches_reflectance = {}
        for patch_id, lambda_values in patches_dict.items():
            reflectance = Reflectance(patch_id, self.nm_range, self.nm_interval, lambda_values, self.illuminant, self.observer, metadata=self.metadata)
            if self.__scaled:
                reflectance.scale_lambda_values()
            # update
            self.data["patches"][patch_id] = reflectance.lambda_values
            patches_reflectance[patch_id] = reflectance      
        return patches_reflectance

    def __update_from_json__(self, path_json):
        data_json = ld.load_colourchecker_from_json(path_json)
        self.__update_from_dict__(data_json)

    def __update_from_dict__(self, data_as_dict):
        self.data = data_as_dict
        if ld.is_valid_colourchecker_spectral_data_dict(data_as_dict):
            self.illuminant = data_as_dict["Illuminant"]
            self.observer = data_as_dict["Observer"]
            self.nm_range = data_as_dict["nm_range"]
            self.nm_interval = data_as_dict["nm_interval"]
            self.patches = self.__load_patches_reflectance__(data_as_dict["patches"])
        else:
            raise DictLabelError("Error in the dict or file with measurement data: Incomplete data or wrong labels.")

    def __update_from_resources__(self, checker_name):
        self.data = ld.load_theoretical_colourchecker_using_resources(checker_name)
        self.name = ld.get_full_colourchecker_name(checker_name) # Full Name
        # keys 'Metadata', 
        self.metadata = self.data["Metadata"]
        self.illuminant = self.data["Metadata"]["Illuminant"]
        self.observer = self.data["Metadata"]["Observer"]
        #'lambda_nm_interval', 'lambda_nm_range', 'patches']
        self.nm_range = self.data["lambda_nm_range"]
        self.nm_interval = self.data["lambda_nm_interval"]
        self.patches = self.__load_patches_reflectance__(self.data["patches"])

    def __init__(self, checker_name, data = None, path_json = None, metadata = {}):
        self.metadata = metadata

        if ld.is_checker_implemented(checker_name) and data == None and path_json == None:
            self.__update_from_resources__(checker_name)
        elif data != None:
            self.name = checker_name
            self.__update_from_dict__(data)
        elif path_json != None:
            # get extension
            file_extension = cop.get_file_extension(path_json) 
            if file_extension == "json":
                self.name = checker_name
                self.__update_from_json__(path_json)
            else:
                raise FileExtensionError("Type file not allowed: Only data from CSV or JSON files can be uploaded.")
        else:
            raise ClassInstantiateError("ColourCheckerSpectral class could not be instantiated.")
    
    def get_patch_lambda_values(self, patch_id):
        '''
        Method to get the spectral data of a given patch as list.
        
        Parameter:
            patch_id         str    Patch id to remove.
        
        Returns:
            lambda_values    list    spectral data..

        '''
        # Reflectance or Reflectance
        if self.__is_valid_patch__(patch_id):
            return self.patches[patch_id].lambda_values

    def add_patch(self, patch_id, nm_range, nm_interval, lambda_values):
        '''
        Method to add a patch into the colour checker.

        Parameters:
            patch_id         str      patch_id
            nm_range         list     lambda range [min,max] in nm.
            nm_interval      int      lambda interval in nm.
            lambda_values    list     spectral data
            
        '''
        if patch_id in self.patches.keys():
            raise PatchError(f"The patch {patch_id} is already implemented")
        if nm_range != self.nm_range:
            raise PatchError(f"The reflectance nm_range should be into the range {self.nm_range}.")
        if nm_interval != self.nm_interval:
            raise PatchError(f"The reflectance nm_interval should be {self.nm_interval}.")
        if len(lambda_values) != (nm_range[1]+nm_interval-nm_range[0])/10:
            raise PatchError("Wrong reflectance lambda_values.")

        reflectance = Reflectance(patch_id, nm_range, nm_interval, lambda_values, self.illuminant, self.observer)
        # add patch
        self.patches[patch_id] = reflectance
        self.data["patches"][patch_id] = reflectance.lambda_values
        self.__patches_id = self.patches.keys() # update

    def set_reflectance_into_visible_range_spectrum(self, visible_nm_range = [400,700], visible_nm_interval = 10):
        '''
        Method to set the reflectance data of the colour patches into the visible spectrum.

        Parameters:
            visible_nm_range        list  lambda [min, max] range in $nm$. Default: [400,700].
            visible_nm_interval     int   lambda nterval in nm. Default: 10.
        
        '''
        
        for patch_id in self.patches.keys():
            spc = self.patches[patch_id]
            spc.set_into_visible_range_spectrum(visible_nm_range, visible_nm_interval)
            self.patches[patch_id] = spc
            #update data dict
            self.data["patches"][patch_id] = spc.lambda_values
        # update attributes
        self.nm_range = visible_nm_range
        self.nm_interval = visible_nm_interval

    def scale_reflectance_data(self):
        '''
        Method to scale the reflectance data of the colour patches into the range (0,1).
        '''
        if not self.scaled:
            for patch_id, reflectance in self.patches.items():
                reflectance.scale_lambda_values()
                # update
                self.patches[patch_id] = reflectance
                self.data["patches"][patch_id] = reflectance.lambda_values
            self.scaled = True
        else:
            raise Exception("Reflectance data is scaled")

    def patch_spectral_to_XYZ(self, patch_id, illuminant = "D65", observer = 2, visible = False):
        '''
        Method to compute the XYZ values from the reflectance data of a given colour patch.

        Parameters:
            patch_id           str                  Patch id. 
            illuminant         str, Illuminant      Illuminant. Default: "D65".
                               IlluminantFromCCT
                               MeasuredIlluminant
            observer           str, int             CIE Observer. Default. 2.
                               Observer
            visible            bool                 If True, compute XYZ from spectral data into the visible range spectrum. Default: False.

        Returns:
            X,Y,Z              float                Computed XYZ values.

        '''

        if self.__is_valid_patch__(patch_id):
            if illuminant==None and observer==None:
                reflectance = self.get_patch_data(patch_id) # as is
            elif illuminant!=None and observer==None:
                reflectance = Reflectance(patch_id, self.nm_range, self.nm_interval, self.get_patch_lambda_values(patch_id), illuminant, self.observer) 
            elif illuminant==None and observer!=None:
                reflectance = Reflectance(patch_id, self.nm_range, self.nm_interval, self.get_patch_lambda_values(patch_id), self.illuminant, observer) 
            else:
                reflectance = Reflectance(patch_id, self.nm_range, self.nm_interval, self.get_patch_lambda_values(patch_id), illuminant, observer) 
            
            if visible:
                reflectance.set_into_visible_range_spectrum()

            X, Y, Z = reflectance.to_XYZ()
        
        return X, Y, Z

    def to_ColourCheckerXYZ(self, illuminant = "D65", observer = 2, visible = False):
        '''
        Method to export the XYZ data computed form the spectral data as a ColourChecker XYZ.

        Parameters:
            illuminant           str, Illuminant      Illuminant.
                                 IlluminantFromCCT
                                 MeasuredIlluminant
            observer             str, int             CIE Observer.
                                 Observer
            visible              bool                 If True, compute XYZ from spectral data into the visible range spectrum. Default: False.

        Returns:
            colour_checker_XYZ   ColourCheckerXYZ     Computed XYZ values. 

        '''

        patches_XYZ = {}
        for patch_id in self.patches.keys():
            lambda_values = self.get_patch_lambda_values(patch_id)
            rfc = Reflectance(patch_id, self.nm_range, self.nm_interval, lambda_values, illuminant, observer)
            if visible:
                rfc.set_into_visible_range_spectrum()
            X, Y, Z = rfc.to_XYZ()
            patches_XYZ[patch_id] = [X, Y, Z]
        colour_checker_XYZ = ColourCheckerXYZ(checker_name=self.name, illuminant=illuminant, observer=observer, data=patches_XYZ)
        return colour_checker_XYZ

    def to_ColourCheckerLAB(self, illuminant = "D65", observer = 2, visible = False):
        '''
        Method to export the LAB data computed from the spectral data as a ColourCheckerLAB object.

        Parameters:
            illuminant           str, Illuminant      Illuminant.
                                 IlluminantFromCCT
                                 MeasuredIlluminant
            observer             str, int             CIE Observer.
                                 Observer
            visible              bool                 If True, compute XYZ from spectral data into the visible range spectrum. Default: False.

        Returns:
            colour_checker_LAB   ColourCheckerLAB     Computed LAB values. 

        '''

        patches_LAB = {}
        for patch_id in self.patches.keys():
            lambda_values = self.get_patch_lambda_values(patch_id)
            rfc = Reflectance(patch_id, self.nm_range, self.nm_interval, lambda_values, illuminant, observer)
            if visible:
                rfc.set_into_visible_range_spectrum()
            X, Y, Z = rfc.to_XYZ()
            Xn, Yn, Zn = rfc.illuminant.compute_white_point_XYZ()
            L, a, b = csc.XYZ_to_LAB(X, Y, Z, Xn, Yn, Zn)
            patches_LAB[patch_id] = [L, a, b]
        colour_checker_LAB = ColourCheckerLAB(checker_name=self.name, illuminant=illuminant, observer=observer, data=patches_LAB)
        return colour_checker_LAB

    def as_pandas_dataframe(self):
        '''
        Method to export the spectral data as a pandas DataFrame object.

        Returns:
            dataframe   DataFrame     Reflectance data. 

        '''

        try:
            name_illuminant = self.illuminant.illuminant_name
        except:
            raise Exception("It is required to specify the illuminant")
        patches = {}
        indx = 0
        for patch_id in self.patches.keys():
            reflectance = self.get_patch_data(patch_id)
            nm_range = reflectance.nm_range
            nm_interval = reflectance.nm_interval
            lambda_values = np.array(reflectance.lambda_values)
            patches[indx] = patch_id, self.illuminant, nm_range, nm_interval, lambda_values # illuminant object
            indx += 1
        # dict to pandas
        dataframe = pd.DataFrame.from_dict(patches, orient="index", columns=["patch_id", "illuminant", "nm_range", "nm_interval", "lambda_values"])
        return dataframe

    def export_data_to_json_file(self, path_json):
        '''
        Method to export the spectral data to a JSON file.

        Parameter:
            path_json    os     path for the ouput JSON file.

        '''

        data_as_dict = {}
        data_as_dict["metadata"] = {}
        data_as_dict["metadata"].update(self.metadata)
        data_as_dict["patches"] = {}
        for patch_id in self.patches_id:
            data_as_dict["patches"][patch_id] = self.get_patch_lambda_values(patch_id)
        ed.export_dict_as_json(data_as_dict, path_json)

    # Plot

    def plot_colourchecker(self, show_figure = True, save_figure = False, output_path = None):
        '''
        Method to create and display the spectral data of a colour checker using Matplotlib.

        Parameters:
            show_figure   bool    If True, the plot is shown. Default: True.
            save_figure   bool    If True, the figure is saved. Default: False.
            output_path   os      path for the ouput figure. Default: None.

        '''

        title = self.name
        samples = {}
        for patch_id in self.patches.keys():
            lambda_values = self.get_patch_lambda_values(patch_id)
            samples[patch_id] = [self.nm_range, self.nm_interval, lambda_values]
        cpt.plot_spectral(samples, show_figure, save_figure, output_path, title)

    # patches_id: list with the name patche
    def plot_patches(self, patches_id, show_figure = True, save_figure = False, output_path = None):
        '''
        Method to plot the spectral data of a given colour patches.

        Parameters:
            patches_id    list    Patches id to plot.
            show_figure   bool    If True, the plot is shown. Default: True.
            save_figure   bool    If True, the figure is saved. Default: False.
            output_path   os      path for the ouput figure. Default: None.

        '''

        if len(patches_id)>10:
            raise PlotSpectralSampleError("Too many samples to plot: the maximun refelctance samples allowed to compare is 10")

        title = self.name
        lambda_nm_interval = self.nm_interval
        lambda_nm_range = self.nm_range
        samples = {}
        for patch_id in patches_id:
            if patch_id in self.patches.keys():
                lambda_values = self.get_patch_lambda_values(patch_id)
                samples[patch_id] = [lambda_nm_range, lambda_nm_interval, lambda_values]
        
        cpt.plot_spectral(samples, show_figure, save_figure, output_path, title)

    def __str__(self):
        return f"ColourCheckerSpectral object: {self.name}"


class ColourCheckerXYZ(ColourChecker):
    '''
    ColourCheckerXYZ class
    
    The ColourCheckerXYZ class represents the XYZ data of the colour patches of a given colour checker measured 
    using a colorimetric instrument, or computed from measured data (e.g. CIELAB or Reflectance).

    Parameters:
        checker_name            str                  ColourChecker name or description.
        illuminant              str, Illuminant      Illuminant. Default: "D65".
                                IlluminantFromCCT
                                MeasuredIlluminant
        observer                str, int             CIE Observer. Default: 2.
                                Observer                              
        data                    dict                 Measured XYZ data. Default: None.
        path_json               os                   Valid path. JSON file with the measured data. Default: None.
        params_csv              dict                 Params to load a CSV file. Default: None.
        metadata                dict                 Instrument measurement information as dict. Default: {}.

    Attributes:
        subtype                 str                  "ColourCheker Reflectance data"
        name                    str                  ColourChecker name or description
        illuminant              Illuminant           Illuminat
                                IlluminantFromCCT
                                MeasuredIlluminant
        
        observer                Observer             CIE Observer
        patches                 dict                 spectral data
        patches_id              list                 patches id
        metadata                dict                 Instrument measurement information as dict

    Methods:
        .add_patch(patch_id, X, Y, Z)
        .update_patches(new_patches)
        .to_ColourCheckerLAB(illuminant)
        .as_pandas_dataframe()
        .export_data_to_json_file(path_json)
    
    '''

    __subtype = "ColourChecker XYZ data"

    @property
    def subtype(self):
        return self.__subtype

    def __update_from_json__(self, path_json):
        patches_dict = ld.load_colourchecker_from_json(path_json)
        self.patches = patches_dict
        
    def __update_from_csv__(self, params_csv):
        path_csv = params_csv["path_csv"]
        csv_rows = params_csv["csv_cols"]
        head = params_csv["head"]
        patches_dict = ld.load_coordinates_from_csv(path_csv, csv_rows, head, data_type="XYZ")
        self.patches = patches_dict

    # params_csv = dict(path_csv=path_file, csv_cols={"label":col_pos, "X":col_pos, "Y":col_pos, "Z":col_pos}, head=True)

    # json: {"patch_id": [X,Y,Z]} # only patch_id, X, Y, Z

    def __init__(self, checker_name, illuminant="D65", observer="2", data = None, path_json = None, params_csv = None, metadata = {}):
        self.name = checker_name
        self.illuminant = illuminant
        self.observer = observer
        self.metadata = metadata

        if data!=None:
            self.patches = data
        elif path_json!=None:
            self.__update_from_json__(path_json)
        elif params_csv!=None:
            self.__update_from_csv__(params_csv)
        else:
            raise ClassInstantiateError("ColourCheckerSpectral class could not be instantiated.")

    def add_patch(self, patch_id, X, Y, Z):
        '''
        Method to add a patch into the colour checker.

        Parameters:
            patch_id         str      patch_id
            X, Y, Z          float    X,Y,Z data
            
        '''

        if patch_id in self.patches.keys():
            raise PatchError("The patch {patch_id} is already implemented")
        else:
            self.patches[patch_id] = [X, Y, Z]
            self.__patches_id = self.patches.keys() # update

    def update_patches(self, new_patches):
        set_1 = set(new_patches.keys())
        set_2 = set(self.patches.keys())
        set_inter = set_1.intersection(set_2) 
        if len(set_inter)==0:
            self.patches.update(new_patches)
            self.__patches_id = self.patches.keys() # update
        else:
            raise PatchError(f"Update failed: Duplicated patches: {set_inter}")
    
    def to_ColourCheckerLAB(self, illuminant = "D65"):
        '''
        Method to export the LAB data computed from the XYZ values as a ColourCheckerLAB object.

        Parameters:
            illuminant           str, Illuminant      Illuminant.
                                 IlluminantFromCCT
                                 MeasuredIlluminant

        Returns:
            colour_checker_LAB   ColourCheckerLAB     Computed LAB values. 

        '''

        # compute white point
        if isinstance(illuminant, str):
            illuminant = Illuminant(illuminant)
        Xn, Yn, Zn = illuminant.compute_white_point_XYZ()
        patches_LAB = {}
        for patch_id in self.patches.keys():
            X, Y, Z = self.get_patch_data(patch_id)
            L, a, b = csc.XYZ_to_LAB(X,Y,Z,Xn,Yn,Zn)
            patches_LAB[patch_id] = [L, a, b]
        colour_checker_LAB = ColourCheckerLAB(checker_name=self.name, illuminant=illuminant, observer=self.observer, data=patches_LAB)
        return colour_checker_LAB

    def as_pandas_dataframe(self):
        '''
        Method to export the XYZ data as a pandas DataFrame object.

        Returns:
            dataframe   DataFrame     XYZ data. 

        '''

        patches = {}
        indx = 0
        for patch_id in self.patches.keys():
            X, Y, Z = self.get_patch_data(patch_id)
            patches[indx] = patch_id, self.illuminant, X, Y, Z # illuminant object
            indx += 1
        # dict to pandas
        dataframe = pd.DataFrame.from_dict(patches, orient="index", columns=["patch_id", "illuminant", "X", "Y", "Z"])
        return dataframe

    def export_data_to_json_file(self, path_json):
        '''
        Method to export the XYZ data to a JSON file.

        Parameter:
            path_json    os     path for the ouput JSON file.

        '''
        data_as_dict = {}
        data_as_dict["metadata"] = {}
        data_as_dict["metadata"].update(self.metadata)
        data_as_dict["patches"] = {}
        data_as_dict["patches"].update(self.patches)
        ed.export_dict_as_json(data_as_dict, path_json)

    def __str__(self):
        return f"ColourCheckerXYZ object: {self.name}"

class ColourCheckerLAB(ColourChecker):
    '''
    ColourCheckerLAB class
    
    The ColourCheckerLAB class represents the LAB data of the colour patches of a given colour checker measured 
    using a colorimetric instrument, or computed from measured data (e.g. XYZ or Reflectance).

    Parameters:
        checker_name            str                  ColourChecker name or description.
        illuminant              str, Illuminant      Illuminant. Default: "D65".
                                IlluminantFromCCT
                                MeasuredIlluminant
        observer                str, int             CIE Observer. Default: 2.
                                Observer                              
        data                    dict                 Measured XYZ data. Default: None.
        path_json               os                   Valid path. JSON file with the measured data. Default: None.
        params_csv              dict                 Params to load a CSV file. Default: None.
        metadata                dict                 Instrument measurement information as dict. Default: {}.

    Attributes:
        subtype                 str                  "ColourCheker Reflectance data"
        name                    str                  ColourChecker name or description
        illuminant              Illuminant           Illuminat
                                IlluminantFromCCT
                                MeasuredIlluminant
        
        observer                Observer             CIE Observer
        patches                 dict                 spectral data
        patches_id              list                 patches id
        metadata                dict                 Instrument measurement information as dict

    Methods:
        .add_patch(patch_id, L, a, b)
        .update_patches(new_patches)
        .to_ColourCheckerLAB(illuminant)
        .as_pandas_dataframe()
        .export_data_to_json_file(path_json)
        .plot_colourchecker(show_figure, save_figure, output_path)
    
    '''
    
    __subtype = "ColourChecker LAB data"


    @property
    def subtype(self):
        return self.__subtype

    def __update_from_json__(self, path_json):
        patches_dict = ld.load_colourchecker_from_json(path_json)
        self.patches = patches_dict
        
    def __update_from_csv__(self, params_csv):
        path_csv = params_csv["path_csv"]
        csv_rows = params_csv["csv_cols"]
        head = params_csv["head"]
        patches_dict = ld.load_coordinates_from_csv(path_csv, csv_rows, head, data_type="LAB")
        self.patches = patches_dict

    # params_csv = dict(path_csv=path_file, csv_cols={"label":col_pos, "L":col_pos, "a":col_pos, "b":col_pos}, head=True)

    # json: {"patch_id": [L,a,b]} # only patch_id, L, a, b

    def __init__(self, checker_name, illuminant="D65", observer="2", data = None, path_json = None, params_csv = None, metadata = {}):
        self.name = checker_name
        self.illuminant = illuminant
        self.observer = observer
        self.metadata = metadata
        if data!=None:
            self.patches = data
        elif path_json!=None:
            self.__update_from_json__(path_json)
        elif params_csv!=None:
            self.__update_from_csv__(params_csv)
        else:
            raise ClassInstantiateError("ColourCheckerLAB class could not be instantiated.")

    def add_patch(self, patch_id, L, a, b):
        '''
        Method to add a patch into the colour checker.

        Parameters:
            patch_id         str      patch_id
            L, a, b          float    L,a,b data
            
        '''

        if patch_id in self.patches.keys():
            raise PatchError("The patch {patch_id} is already implemented")
        else:
            self.patches[patch_id] = [L, a, b]
            self.__patches_id = self.patches.keys() # update

    def update_patches(self, new_patches):
        set_1 = set(new_patches.keys())
        set_2 = set(self.patches.keys())
        set_inter = set_1.intersection(set_2) 
        if len(set_inter)==0:
            self.patches.update(new_patches)
            self.__patches_id = self.patches.keys() # update
        else:
            raise PatchError(f"Update failed: Duplicated patches: {set_inter}")

    def to_ColourCheckerXYZ(self, illuminant = "D65"):
        '''
        Method to export the XYZ data computed from the LAB data as a ColourCheckerXYZ object.

        Parameters:
            illuminant           str, Illuminant      Illuminant.
                                 IlluminantFromCCT
                                 MeasuredIlluminant

        Returns:
            colour_checker_XYZ   ColourCheckerXYZ     Computed XYZ values. 

        '''
        # compute white point
        if isinstance(illuminant, str):
            illuminant = Illuminant(illuminant)
        Xn, Yn, Zn = illuminant.compute_white_point_XYZ()
        patches_XYZ = {}
        for patch_id in self.patches.keys():
            L, a, b = self.get_patch_data(patch_id)
            X, Y, Z = csc.LAB_to_XYZ(L, a, b, Xn, Yn, Zn)
            patches_XYZ[patch_id] = [X, Y, Z]
        colour_checker_XYZ = ColourCheckerXYZ(checker_name=self.name, illuminant=illuminant, observer=self.observer, data=patches_XYZ)
        return colour_checker_XYZ

    def as_pandas_dataframe(self):
        '''
        Method to export the LAB data as a pandas DataFrame object.

        Returns:
            dataframe   DataFrame     LAB data. 

        '''

        patches = {}
        indx = 0
        for patch_id in self.patches.keys():
            L, a, b = self.get_patch_data(patch_id)
            patches[indx] = patch_id, self.illuminant, L, a, b # illuminant object
            indx += 1
        # dict to pandas
        dataframe = pd.DataFrame.from_dict(patches, orient="index", columns=["patch_id", "illuminant", "L", "a", "b"])
        return dataframe

    def export_data_to_json_file(self, path_json):
        '''
        Method to export the LAB data to a JSON file.

        Parameter:
            path_json    os     path for the ouput JSON file.

        '''

        data_as_dict = {}
        data_as_dict["metadata"] = {}
        data_as_dict["metadata"].update(self.metadata)
        data_as_dict["patches"] = {}
        data_as_dict["patches"].update(self.patches)
        ed.export_dict_as_json(data_as_dict, path_json)

    def plot_colourchecker(self, show_figure = True, save_figure = False, output_path = None):
        '''
        Method to create and display the LAB data of a colour checker using Matplotlib.

        Parameters:
            show_figure   bool    If True, the plot is shown. Default: True.
            save_figure   bool    If True, the figure is saved. Default: False.
            output_path   os      path for the ouput figure. Default: None.

        '''

        title = f"CIELAB Diagram: {self.name}"
        samples = {}
        for patch_id in self.patches.keys():
            L, a, b = self.get_patch_data(patch_id)
            samples[patch_id] = [L, a, b]
        cpt.plot_cielab(samples, show_figure, save_figure, output_path, title)
        #cpt.plot_spectral(samples, show_figure, save_figure, output_path, title)

        # improve, 3D figure

    def __str__(self):
        return f"ColourCheckerLAB object: {self.name}"


class ColourCheckerRGB(ColourChecker):
    '''
    ColourCheckerRGB class
    
    The ColourCheckerRGB class represents the RGB data of the colour patches of a given colour checker extracted 
    from an image.
    
    Parameters:
        checker_name            str                  ColourChecker name or description.
        illuminant              str, Illuminant      Illuminant. Default: "D65".
                                IlluminantFromCCT
                                MeasuredIlluminant
        observer                str, int             CIE Observer. Default: 2.
                                Observer                              
        data                    dict                 Measured XYZ data. Default: None.
        path_json               os                   Valid path. JSON file with the measured data. Default: None.
        params_csv              dict                 Params to load a CSV file. Default: None.
        metadata                dict                 Instrument measurement information as dict. Default: {}.

    Attributes:
        subtype                 str                  "ColourCheker Reflectance data"
        name                    str                  ColourChecker name or description
        illuminant              Illuminant           Illuminat
                                IlluminantFromCCT
                                MeasuredIlluminant
        
        observer                Observer             CIE Observer
        patches                 dict                 spectral data
        patches_id              list                 patches id
        metadata                dict                 Instrument measurement information as dict

    Methods:
        .add_patch(patch_id, R, G, B)
        .update_patches(new_patches)
        .as_pandas_dataframe()
        .export_data_to_json_file(path_json)
    
    '''

    __subtype = "ColourChecker RGB data"

    @property
    def subtype(self):
        return self.__subtype

    def __update_from_json__(self, path_json):
        patches_dict = ld.load_colourchecker_from_json(path_json)
        self.patches = patches_dict
        
    def __update_from_csv__(self, params_csv):
        path_csv = params_csv["path_csv"]
        csv_rows = params_csv["csv_cols"]
        head = params_csv["head"]
        patches_dict = ld.load_coordinates_from_csv(path_csv, csv_rows, head, data_type="RGB")
        self.patches = patches_dict

    # params_csv = dict(path_csv=path_file, csv_cols={"label":col_pos, "X":col_pos, "Y":col_pos, "Z":col_pos}, head=True)

    # json: {"patch_id": [X,Y,Z]} # only patch_id, X, Y, Z

    def __init__(self, checker_name, illuminant="D65", observer="2", data = None, path_json = None, params_csv = None, metadata = {}):
        self.name = checker_name
        self.illuminant = illuminant
        self.observer = observer
        self.metadata = metadata

        if data!=None:
            self.patches = data
        elif path_json!=None:
            self.__update_from_json__(path_json)
        elif params_csv!=None:
            self.__update_from_csv__(params_csv)
        else:
            raise ClassInstantiateError("ColourCheckerSpectral class could not be instantiated.")

    def add_patch(self, patch_id, R, G, B):
        '''
        Method to add a patch into the colour checker.

        Parameters:
            patch_id         str      patch_id
            R, G, B          float    R,G,B data
            
        '''

        if patch_id in self.patches.keys():
            raise PatchError("The patch {patch_id} is already implemented")
        else:
            self.patches[patch_id] = [R, G, B]
            self.__patches_id = self.patches.keys() # update

    def update_patches(self, new_patches):
        set_1 = set(new_patches.keys())
        set_2 = set(self.patches.keys())
        set_inter = set_1.intersection(set_2) 
        if len(set_inter)==0:
            self.patches.update(new_patches)
            self.__patches_id = self.patches.keys() # update
        else:
            raise PatchError(f"Update failed: Duplicated patches: {set_inter}")

    def as_pandas_dataframe(self):
        '''
        Method to export the RGB data as a pandas DataFrame object.

        Returns:
            dataframe   DataFrame     RGB data. 

        '''

        patches = {}
        indx = 0
        for patch_id in self.patches.keys():
            R, G, B = self.get_patch_data(patch_id)
            patches[indx] = patch_id, self.illuminant, R, G, B# illuminant object
            indx += 1
        # dict to pandas
        dataframe = pd.DataFrame.from_dict(patches, orient="index", columns=["patch_id", "illuminant", "R", "G", "B"])
        return dataframe

    def export_data_to_json_file(self, path_json):
        '''
        Method to export the RGB data to a JSON file.

        Parameter:
            path_json    os     path for the ouput JSON file.

        '''
        data_as_dict = {}
        data_as_dict["metadata"] = {}
        data_as_dict["metadata"]["Illuminant"] = self.illuminant.illuminant_name
        data_as_dict["metadata"]["Observer"] = self.observer.observer
        data_as_dict["metadata"]["measurement"] = {} 
        for key in self.metadata:
            data_as_dict["metadata"]["measurement"][key] = str(self.metadata[key])
        data_as_dict["patches"] = {}
        data_as_dict["patches"].update(self.patches)
        ed.export_dict_as_json(data_as_dict, path_json)

    def __str__(self):
        return f"ColourCheckerRGB object: {self.name}"

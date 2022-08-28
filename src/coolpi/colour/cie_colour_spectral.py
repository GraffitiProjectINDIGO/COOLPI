from abc import ABC
from abc import abstractmethod
from importlib import resources
import json

import numpy as np

from coolpi.auxiliary.errors import CCTNotInValidRangeError, CIEIlluminantError, CIEObserverError, ClassTypeError, ColourError, ColourConversionError, ClassMethodError, DictLabelError, SpectralRangeError, FileExtensionError
import coolpi.auxiliary.common_operations as cop
import coolpi.auxiliary.load_data as ld
import coolpi.auxiliary.plot as cpt
import coolpi.colour.cat_models as cat
import coolpi.colour.cct_operations as cct
import coolpi.colour.colour_difference as cde
import coolpi.colour.colour_space_conversion as csc
import coolpi.colour.lambda_operations as lo

class CIE(ABC):
    ''' 
    CIE abstrac class.

    Attributes:
        type        str      "CIE Object"

    '''

    __type = "CIE Object"

    @property
    def type(self):
        return self.__type
    
    @abstractmethod
    def __init__(self):
        pass
    
class Spectral(ABC):
    
    ''' 
    Spectral abstract class.

    Attributes:
        type             str     "Spectral object".
        nm_range         list    lambda nm range [min, max].
        nm_interval      int     lambda nm interval.
        lambda_values    list    spectral lambda values.

    Methods:
        .as_diagonal_array()
        .get_visible_lambda_values(nm_range, nm_interval, lambda_values, visible_nm_range, visible_nm_interval)
        .set_into_visible_range_spectrum(visible_nm_range, visible_nm_interval)
        .get_lambda_values_interpolate(nm_range, nm_interval, lambda_values, new_nm_range, new_nm_interval, method)
        .set_lambda_values_interpolate(new_nm_range, new_nm_interval, method)
        .get_lambda_values_extrapolate(nm_range, nm_interval, lambda_values, new_nm_range, new_nm_interval, method)
        .set_lambda_values_extrapolate(new_nm_range, new_nm_interval, method)

    '''

    __type = "Spectral Object"
    __nm_range = None 
    __nm_interval = None
    __lambda_values = None
        
    @property
    def type(self):
        return self.__type
  
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
        try:
            nm_interval = int(nm_interval)
        except:
            raise ClassTypeError("The input lambda nm interval is not a valid type argument.")
        self.__nm_interval = nm_interval
    
    @property
    def lambda_values(self):
        return self.__lambda_values

    @lambda_values.setter
    def lambda_values(self, lambda_values):
        self.__lambda_values = lambda_values

    @abstractmethod
    def __init__(self):
        pass

    def __update__(self, nm_range, nm_interval, lambda_values):
        self.nm_range = nm_range
        self.nm_interval = nm_interval
        self.lambda_values = lambda_values

    def as_diagonal_array(self):
        '''
        Method to get the spectral data as a numpy diagonal array.

        Returns:
            as_diag   numpy.ndarray    spectral data as numpy diagonal array.
        
        '''
        as_diag = np.diag(self.lambda_values)
        return as_diag

    @staticmethod
    def get_visible_lambda_values(nm_range, nm_interval, lambda_values, visible_nm_range = [400,700], visible_nm_interval = 10):
        '''
        Static method to get the spectral data into the visible spectrum.

        Parameters:
            nm_range                list    lambda range in nm [max, min].
            nm_interval             int     lambda interval in nm.
            lambda_values           list    lambda values.
            visible_nm_range        list    visible range. Default: [400,700].
            visible_nm_interval      int    visible interval in nm. Default: 10.

        Returns:
            lambda_values_visible    list    lambda values into the visible spectrum.

        '''

        if nm_range == visible_nm_range and nm_interval == visible_nm_interval:
            raise SpectralRangeError("The implemented spectral is already in the spectral visible range.")
        
        if lo.range_is_valid(nm_range, nm_interval, visible_nm_range, visible_nm_interval):
            lambda_values_visible = lo.extract_nm_range(lambda_values, nm_range, nm_interval, visible_nm_range, visible_nm_interval)
            return lambda_values_visible
        else:
            raise SpectralRangeError("The implemented spectral lambda values cannot be defined intro the visible range.")

    def set_into_visible_range_spectrum(self, visible_nm_range = [400,700], visible_nm_interval = 10):
        '''
        Method to set the spectral data into the visible range spectrum.

        Parameters:
            visible_nm_range        list    visible range. Default: [400,700].
            visible_nm_interval      int    visible interval in nm. Default: 10 .       

        '''

        if self.nm_range == visible_nm_range and self.nm_interval == visible_nm_interval:
            raise SpectralRangeError("The implemented spectral is already in the spectral visible range.")
        lambda_values_visible = self.get_visible_lambda_values(self.nm_range, self.nm_interval, self.lambda_values)
        self.__update__(visible_nm_range, visible_nm_interval, lambda_values_visible)

    @staticmethod
    def get_lambda_values_interpolate(nm_range, nm_interval, lambda_values, new_nm_range, new_nm_interval, method = "Akima"):
        '''
        Static method to interpolate the spectral data into the new range and interval.
        
        The interpolation methods implemented are: “Linear”, “Spline”, “CubicHermite”, 
        “Fifth”, “Sprague” and “Akima”.

        Parameters:
            new_nm_range                 list    new lambda range in nm [max, min].
            new_nm_interval              int     new interval in nm.
            method                       str     Interpolation method. Default: “Akima”.
        
        Returns:
            lambda_values_interpolate    list    Interpolated data.

        '''

        wavelength_spd = lo.create_wavelength_space(nm_range[0], nm_range[1], nm_interval)
        spd = np.array(lambda_values)

        wavelength_interpolate = lo.create_wavelength_space(new_nm_range[0], new_nm_range[1], new_nm_interval)
        lambda_values_interpolate = lo.lambda_interpolation(wavelength_spd, spd , wavelength_interpolate, method)        
        
        return lambda_values_interpolate
    
    def set_lambda_values_interpolate(self, new_nm_range, new_nm_interval, method = "Akima"):
        '''
        Method to interpolate and set the spectral data into the new range and interval.
        
        The interpolation methods implemented are: “Linear”, “Spline”, “CubicHermite”, 
        “Fifth”, “Sprague” and “Akima”.

        Parameters:
            new_nm_range                 list    new lambda range in nm [max, min].
            new_nm_interval              int     new interval in nm.
            method                       str     Interpolation method. Default: “Akima”.
        
        '''

        lambda_values_interpolate = self.get_lambda_values_interpolate(self.nm_range, self.nm_interval, self.lambda_values, new_nm_range, new_nm_interval, method)
        self.__update__(new_nm_range, new_nm_interval, lambda_values_interpolate)

    @staticmethod
    def get_lambda_values_extrapolate(nm_range, nm_interval, lambda_values, new_nm_range, new_nm_interval, method = "Spline"):
        '''
        Static method to extrapolate the spectral data into the new range and interval.
        
        The extrapolate methods implemented are: “Spline”, “CubicHermite”, “Fourth” and “Fifth”.

        Note: Extrapolation of measured data may cause errors and shold be used only if it can be 
        demostrated that the resulting errors are insignificant for the porpoue of the user.
        
        CIE 015:2018. 7.2.3 Extrapolation and interpolation (pp. 24) (CIE, 2018).

        Parameters:
            new_nm_range                 list    new lambda range in nm [max, min].
            new_nm_interval              int     new interval in nm.
            method                       str     Extrapolation method. Default: “Akima”.
        
        Returns:
            lambda_values_extrapolate    list    Extrapolated data.

        '''

        print("!!!Alert Message to users: Extrapolation of measured data may cause errors and shold be used only if it can be demostrated that the resulting errors are insignificant for the porpoue of the user (CIE, 2018. pf.24, 7.2.3).")
        wavelength_spd = lo.create_wavelength_space(nm_range[0], nm_range[1], nm_interval)
        spd = np.array(lambda_values)

        wavelength_extrapolate = lo.create_wavelength_space(new_nm_range[0], new_nm_range[1], new_nm_interval)
        lambda_values_extrapolate = lo.lambda_extrapolation(wavelength_spd, spd , wavelength_extrapolate, method)      
        
        return lambda_values_extrapolate

    def set_lambda_values_extrapolate(self, new_nm_range, new_nm_interval, method = "Spline"):
        '''
        Method to extrapolate and set the spectral data into the new range and interval.
        
        The extrapolate methods implemented are: “Spline”, “CubicHermite”, “Fourth” and “Fifth”.

        Note: Extrapolation of measured data may cause errors and shold be used only if it can be 
        demostrated that the resulting errors are insignificant for the porpoue of the user.
        
        CIE 015:2018. 7.2.3 Extrapolation and interpolation (pp. 24) (CIE, 2018).

        Parameters:
            new_nm_range                 list    new lambda range in nm [max, min].
            new_nm_interval              int     new interval in nm.
            method                       str     Extrapolation method. Default: “Akima”.
        
        '''

        lambda_values_extrapolate = self.get_lambda_values_extrapolate(self.nm_range, self.nm_interval, self.lambda_values, new_nm_range, new_nm_interval, method)
        self.__update__(new_nm_range, new_nm_interval, lambda_values_extrapolate)

class Observer(CIE):
    ''' 
    Observer class.
    
    The Observer class represents a valid CIE standard colorimetric observer.

    CIE 015:2018. 3. Recomendations concerning standard observer data (pp.3-5).

    Parameter:
        observer    str, int    CIE standard observer. Default: 2.

    Attributes:
        subtype     str    "CIE Observer".
        observer    int    CIE standard observer.
        
    '''
    
    __subtype = "CIE Observer"
    __observer = None
    
    @property
    def subtype(self):
        return self.__subtype

    @property   
    def observer(self):
        return self.__observer
    
    @observer.setter
    def observer(self, observer):
        if  ld.observer_is_cie(observer):
            self.__observer = int(observer)
        else:
            raise CIEObserverError("The observer should be a CIE standard 1931 or 1964 observer (2º or 10º).")

    def __init__(self, observer=2):     
        '''
        The Observer class receives a valid `str` or `int` type for the specification of the 2º or 
        10º degree CIE standard observer.

        '''   
        self.observer = observer
        
    def __str__(self):
        if self.__observer == 2:
            return "2º standard observer (CIE 1931)" 
        else:
            return "10º standard observer (CIE 1964)"

class Component(CIE, Spectral):
    
    ''' 
    Component class.
    
    The Component class represents a valid CIE spectral component.

    It is an auxiliar class designed to support the SComponents, CMF, CFB and RGBCMF CIE classes. 
    Users can create an instance of the Component class, however, it makes no sense from a practical point of view.

    Parameters:
        name_id          str     Description.
        nm_range         list    lambda range in nm [max, min].
        nm_interval      int     lambda interval in nm.
        lambda_values    list    lambda values.

    Attributes:
        subtype          str     "CIE Component".
        name_id          str     Description.
        nm_range         list    lambda nm range [min, max].
        nm_interval      int     lambda nm interval.
        lambda_values    list    spectral lambda values.

    '''
    
    __subtype = "CIE Component"
    __name_id = None # Descriptor

    @property
    def subtype(self):
        return self.__subtype
    
    @property
    def name_id(self):
        return self.__name_id

    @name_id.setter
    def name_id(self, name_id):
        self.__name_id = name_id

    def __init__(self, name_id, nm_range, nm_interval, lambda_values):
        self.name_id = name_id
        self.__update__(nm_range, nm_interval, lambda_values)
                
class SComponents(CIE):
    
    ''' 
    SComponents class.

    The SComponents class is the implementation of the CIE S0, S1 adn S2 components of 
    daylignt used in the calculation of relative spectral distribution (SPD) of CIE dayligh illuminants of 
    different correlated colour temperatures or CCT.

    CIE 015:2018. 11.1. Table 6. S Components of the relative SPD of daylight used in 
    the calculation of relative SPD of CIE daylight illuminants of different correlated colour temperatures (CTT). (pp.54-55).

    No parameters are required to instanciate the class. 
    
    Attributes:
        subtype          str          "CIE S Components".
        nm_range         list         lambda nm range [min, max].
        nm_interval      int          lambda nm interval.
        S0               Component    S0 Component.
        S1               Component    S1 Component.
        S2               Component    S2 Component.

    Methods:
        .get_S_components()
        .get_S_components_lambda_values()
        .CCT_to_SPD(cct_K)
        .plot(show_figure, save_figure, output_path)
        
    '''
    
    __subtype = "CIE S Components"
    __nm_range = None
    __nm_interval = None
    __S0 = None
    __S1 = None
    __S2 = None
    
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
        try:
            nm_interval = int(nm_interval)
        except:
            raise ClassTypeError("The input lambda nm interval is not a valid type argument.")
        self.__nm_interval = nm_interval

    @property
    def S0(self):
        return self.__S0
    
    @S0.setter
    def S0(self, S0_dict):
        nm_range = S0_dict["lambda_nm_range"]
        nm_interval = S0_dict["lambda_nm_interval"]
        lambda_values = S0_dict["lambda_values"]
        self.__S0 = Component("S0", nm_range, nm_interval, lambda_values)
    
    @property
    def S1(self):
        return self.__S1
    
    @S1.setter
    def S1(self, S1_dict):
        nm_range = S1_dict["lambda_nm_range"]
        nm_interval = S1_dict["lambda_nm_interval"]
        lambda_values = S1_dict["lambda_values"]
        self.__S1 = Component("S1", nm_range, nm_interval, lambda_values) 

    @property
    def S2(self):
        return self.__S2
    
    @S2.setter
    def S2(self, S2_dict):
        nm_range = S2_dict["lambda_nm_range"]
        nm_interval = S2_dict["lambda_nm_interval"]
        lambda_values = S2_dict["lambda_values"]
        self.__S2 = Component("S2", nm_range, nm_interval, lambda_values)

    def __init__(self):
        '''
        No parameters are required to instanciate the class.
        
        '''
        
        S0_dict, S1_dict, S2_dict  = ld.load_cie_s_ctt_components()
        
        self.nm_range = S0_dict["lambda_nm_range"]
        self.nm_interval = S0_dict["lambda_nm_interval"]

        self.S0 = S0_dict
        self.S1 = S1_dict
        self.S2 = S2_dict

    def get_S_components(self):
        '''
        Method to get each of the S0, S1 and S2 components as a Component object.

        Returns:
            S0, S1, S2      Component   S0, S1, S2.
            
        '''
        return self.S0, self.S1, self.S2

    def get_S_components_lambda_values(self):
        '''
        Method to get the spectral lambda values for each of the SComponents as list object.

        Returns:
            S0, S1, S2      list   S0, S1, S2 lambda values.
        
        '''
        return self.S0.lambda_values, self.S1.lambda_values, self.S2.lambda_values

    def CCT_to_SPD(self, cct_K):
        '''
        Method to obtain the SPD of the illuminant from the correlated colour temperature in º Kelvin
        entered as a parameter.
        
        For CCT in range [4000, 25000] the CIE formulation is used.
        
        CIE015:2018. 4.1.2 Other D illuminants. Eq. 4.7 to 4.11 (p. 12); Note 6 (p. 13).
        https://cie.co.at/publications/colorimetry-4th-edition/

        Parameters:
            cct_k           float      CCT (º Kelvin) into the range (4000-25000).
        
        Returns:
            nm_range        list       Range for the spectral values.
            nm_interval     int        Interval.
            spd             list       Computed spectral power distribution lambda values.
            
        '''

        if 4000<cct_K<25000:
            spd = lo.compute_SPD_from_CCT(cct_K, self.S0.lambda_values, self.S1.lambda_values, self.S2.lambda_values) # using CIE
            return self.nm_range, self.nm_interval, spd

        # alternative method for CCT out of range

        else:
            raise Exception(f"CCT {cct_K}ºK out of range: The valid range is 4000ºK -25000ºK.")

    def plot(self, show_figure = True, save_figure = False, output_path = None):
        '''
        Method to create and display the plot of the S0, S1 and S2 components using matplotlib.
        
        Parameters:
            show_figure    bool    If True, the plot is shown. Default: True.
            save_figure    bool    If True, the figure is saved at the output_path. Default: False.
            output_path    os      Path for the ouput figure. Default: None.
        
        '''
        cpt.plot_s_components(self.nm_range, self.nm_interval, self.S0.lambda_values, self.S1.lambda_values, self.S2.lambda_values, show_figure, save_figure, output_path)

    def __str__(self):
        return "CIE S0, S1 and S2 components"


class CMF(CIE): 
    ''' 
    CMF class.

    The CMF class represents the CIE x_cmf, y_cmf and z_cmf colour-matching-functions (CMFs).
    
    CIE 015:2018. 3.1. CIE 1931 standard colorimetric observer (pp. 3).
    CIE 015:2018. 11.1. Table 1. CMF and corresponding xy coordinates of the CIE 1931 colorimetric 
    observer (pp.43-44). Table 2. CMF and corresponding xy coordinates of the CIE 1964 colorimetric 
    observer (pp.45-46).
    
    Parameters:
        observer    str, int    CIE standard observer. Default: 2.
                    Observer    

    Attributes:
        subtype     str         "CIE colour-matching-functions".
        nm_range    list        lambda nm range [min, max].
        nm_interval int         lambda nm interval.
        observer    Observer    CIE Observer.
        x_cmf       Component   CIE x_cmf spectral data.
        y_cmf       Component   CIE y_cmf spectral data.
        z_cmf       Component   CIE z_cmf spectral data.

    Methods:
        .get_colour_matching_functions()
        .set_cmf_into_visible_range_spectrum(visible_nm_range=[400-700], visible_nm_interval=10)
        .cmf_interpolate(new_nm_range, new_nm_interval, method = “Akima”)
        .cmf_extrapolate(new_nm_range, new_nm_interval, method = “Spline”)
        .plot(show_figure = True, save_figure = False, output_path = None)
        
    '''

    __subtype = "CIE colour-matching-functions"
    __nm_range = None
    __nm_interval = None
    __observer = None
    __x_cmf = None
    __y_cmf = None
    __z_cmf = None

    @property
    def subtype(self):
        return self.__subtype

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
        try:
            nm_interval = int(nm_interval)
        except:
            raise ClassTypeError("The input lambda nm interval is not a valid type argument.")
        self.__nm_interval = nm_interval

    @property
    def x_cmf(self):
        return self.__x_cmf
    
    @x_cmf.setter
    def x_cmf(self, x_cmf_components):
        nm_range, nm_interval, lambda_values  = x_cmf_components[0], x_cmf_components[1], x_cmf_components[2]
        self.__x_cmf = Component("x_cmf", nm_range, nm_interval, lambda_values)

    @property
    def y_cmf(self):
        return self.__y_cmf
    
    @y_cmf.setter
    def y_cmf(self, y_cmf_components):
        nm_range, nm_interval, lambda_values  = y_cmf_components[0], y_cmf_components[1], y_cmf_components[2]
        self.__y_cmf = Component("y_cmf", nm_range, nm_interval, lambda_values)

    @property
    def z_cmf(self):
        return self.__z_cmf
    
    @z_cmf.setter
    def z_cmf(self, z_cmf_components):
        nm_range, nm_interval, lambda_values  = z_cmf_components[0], z_cmf_components[1], z_cmf_components[2]
        self.__z_cmf = Component("z_cmf", nm_range, nm_interval, lambda_values)

    def __init__(self, observer=2):
        '''
        The CMF class receives a valid str or int type for the specification of the 
        2º or 10º degree CIE standard observer, or an Observer instance class. 
        Default: 2.
        
        '''  
        self.observer = observer
        cmf = ld.load_cie_cmf(self.observer.observer)

        self.nm_range = cmf["lambda_nm_range"]
        self.nm_interval = cmf["lambda_nm_interval"]

        self.x_cmf = [cmf["lambda_nm_range"], cmf["lambda_nm_interval"], cmf["x_cmf"]]
        self.y_cmf = [cmf["lambda_nm_range"], cmf["lambda_nm_interval"], cmf["y_cmf"]]
        self.z_cmf = [cmf["lambda_nm_range"], cmf["lambda_nm_interval"], cmf["z_cmf"]]
        
    def get_colour_matching_functions(self):
        '''
        Method to get the x_cmf, y_cmf and z_cmf CMFs as Component objects.

        Returns:
            x_cmf, y_cmf, z_cmf    Component    colour-matching-functions as a Component objects.

        '''
        return self.x_cmf, self.y_cmf, self.z_cmf

    def __get_full_data__(self):
        return self.nm_range, self.nm_interval, self.x_cmf, self.y_cmf, self.z_cmf

    def set_cmf_into_visible_range_spectrum(self, visible_nm_range = [400,700], visible_nm_interval = 10):
        '''
        Method to set the spectral data into the visible spectrum.

        Parameters:
            visible_nm_range        list    visible range [min, max] in nm. Default: [400,700].
            visible_nm_interval     int     visible interval in nm. Default: 10.

        '''

        self.x_cmf.set_into_visible_range_spectrum(visible_nm_range, visible_nm_interval)
        self.y_cmf.set_into_visible_range_spectrum(visible_nm_range, visible_nm_interval)
        self.z_cmf.set_into_visible_range_spectrum(visible_nm_range, visible_nm_interval)
        # update
        self.nm_range = visible_nm_range
        self.nm_interval = visible_nm_interval
    
    # Akima works very well for cmf interpolation
    def cmf_interpolate(self, new_nm_range, new_nm_interval, method = "Akima"):
        '''
        Method to interpolate the spectral data of the x_cmf, y_cmf and z_cmf.
        
        The interpolation methods implemented are: “Linear”, “Spline”, “CubicHermite”, 
        “Fifth”, “Sprague” and “Akima”.

        Parameters:
            new_nm_range       list    new range [min, max] to interpolate.
            new_nm_interval    int     new interval in nm.
            method             str     Interpolation method. Default: “Akima”.
        
        '''
        
        self.x_cmf.set_lambda_values_interpolate(new_nm_range, new_nm_interval, method)
        self.y_cmf.set_lambda_values_interpolate(new_nm_range, new_nm_interval, method)
        self.z_cmf.set_lambda_values_interpolate(new_nm_range, new_nm_interval, method)
        # update
        self.nm_range = new_nm_range
        self.nm_interval = new_nm_interval        

    def cmf_extrapolate(self, new_nm_range, new_nm_interval, method = "Spline"):
        '''
        Method to extrapolate the spectral data of the x_cmf, y_cmf and z_cmf.
        
        The extrapolate methods implemented are: “Spline”, “CubicHermite”, “Fourth” and “Fifth”.

        Note: Extrapolation of measured data may cause errors and shold be used only if it can be 
        demostrated that the resulting errors are insignificant for the porpoue of the user.
        
        CIE 015:2018. 7.2.3 Extrapolation and interpolation (pp. 24) (CIE, 2018).

        Parameters:
            new_nm_range       list    new range [min, max] to extrapolate.
            new_nm_interval    int     new interval in nm.
            method             str     Extrapolation method. Default: “Spline”.
        
        '''
        
        self.x_cmf.set_lambda_values_extrapolate(new_nm_range, new_nm_interval, method)
        self.y_cmf.set_lambda_values_extrapolate(new_nm_range, new_nm_interval, method)
        self.z_cmf.set_lambda_values_extrapolate(new_nm_range, new_nm_interval, method)
        # update
        self.nm_range = new_nm_range
        self.nm_interval = new_nm_interval
        
    def plot(self, show_figure = True, save_figure = False, output_path = None):
        '''
        Method to create and display the plot of the x_cmf, y_cmf and z_cmf using matplotlib.
        
        Parameters:
            show_figure    bool    If True, the plot is shown. Default: True.
            save_figure    bool    If True, the figure is saved at the output_path. Default: False.
            output_path    os      Path for the ouput figure. Default: None.
        
        '''     
        
        cpt.plot_cmf(self.nm_range, self.nm_interval, self.x_cmf.lambda_values, self.y_cmf.lambda_values, self.z_cmf.lambda_values, self.observer.observer, show_figure, save_figure, output_path)

    def __str__(self):
        obs = "2º standard observer (CIE 1931)" if self.observer.observer else "10º standard observer (CIE 1964)"
        return f"CIE colour-matching-functions for the {obs}."

class CFB(CIE):
    ''' 
    CFB class.

    The CFB class represents the CIE xf_cmf, yf_cmf and zf_cmf cone-fundamental-based CMFs.
    
    CIE 015:2018. 3.3.1. Cone-fundamental-based tristimulus functions (pp. 6).
    CIE 015:2018. 11.1. Table 3. CFB for 2º field size (pp.47-48). Table 4. CFB for 10º field size (pp.49-50).
    
    Parameters:
        observer    str, int    CIE standard observer (2º or 10). Default: 2.
                    Observer    Instance Observer class.

    Attributes:
        subtype     str         "CIE cone-fundamental-based".
        nm_range    list        lambda nm range [min, max].
        nm_interval int         lambda nm interval.
        observer    Observer    CIE Observer.
        xf_cmf      Component   CIE xf_cmf spectral data.
        yf_cmf      Component   CIE yf_cmf spectral data.
        zf_cmf      Component   CIE zf_cmf spectral data.

    Methods:
        .get_colour_matching_functions()
        .set_cmf_into_visible_range_spectrum(visible_nm_range, visible_nm_interval)
        .cmf_interpolate(new_nm_range, new_nm_interval, method)
        .cmf_extrapolate(new_nm_range, new_nm_interval, method)
        .plot(show_figure, save_figure, output_path)
        
    '''

    __subtype = "CIE cone-fundamental-based"
    __nm_range = None
    __nm_interval = None
    __observer = None
    __xf_cmf  = None
    __yf_cmf  = None
    __zf_cmf  = None

    @property
    def subtype(self):
        return self.__subtype

    @property
    def oberver(self):
        return self.__observer
    
    @oberver.setter
    def observer(self, observer):
        if isinstance(observer, Observer):
            self.__observer  = observer
        else:
            self.__observer = Observer(observer)

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
        try:
            nm_interval = int(nm_interval)
        except:
            raise ClassTypeError("The input lambda nm interval is not a valid type argument.")
        self.__nm_interval = nm_interval

    @property
    def xf_cmf(self):
        return self.__xf_cmf
    
    @xf_cmf.setter
    def xf_cmf(self, xf_cmf_components):
        nm_range, nm_interval, lambda_values  = xf_cmf_components[0], xf_cmf_components[1], xf_cmf_components[2]
        self.__xf_cmf = Component("xf_cmf", nm_range, nm_interval, lambda_values)

    @property
    def yf_cmf(self):
        return self.__yf_cmf
    
    @yf_cmf.setter
    def yf_cmf(self, yf_cmf_components):
        nm_range, nm_interval, lambda_values  = yf_cmf_components[0], yf_cmf_components[1], yf_cmf_components[2]
        self.__yf_cmf = Component("yf_cmf", nm_range, nm_interval, lambda_values)

    @property
    def zf_cmf(self):
        return self.__zf_cmf
    
    @zf_cmf.setter
    def zf_cmf(self, zf_cmf_components):
        nm_range, nm_interval, lambda_values  = zf_cmf_components[0], zf_cmf_components[1], zf_cmf_components[2]
        self.__zf_cmf = Component("zf_cmf", nm_range, nm_interval, lambda_values)

    def __init__(self, observer=2):
        '''
        The CFB class receives a valid str or int type for the specification of the 
        2º or 10º degree CIE standard observer, or an Observer instance class.
        Default: 2.
        
        '''  
        self.observer = observer
        cfb = ld.load_cie_cfb(self.observer.observer)

        self.nm_range = cfb["lambda_nm_range"]
        self.nm_interval = cfb["lambda_nm_interval"]

        self.xf_cmf = [cfb["lambda_nm_range"], cfb["lambda_nm_interval"], cfb["xf_cmf"]]
        self.yf_cmf = [cfb["lambda_nm_range"], cfb["lambda_nm_interval"], cfb["yf_cmf"]]
        self.zf_cmf = [cfb["lambda_nm_range"], cfb["lambda_nm_interval"], cfb["zf_cmf"]]
        
    def get_colour_matching_functions(self):
        '''
        Returns the xf_cmf, yf_cmf and zf_cmf as a Component objects.

        Returns:
            xf_cmf, yf_cmf, zf_cmf   Component    CFB CMF as a Component objects.

        '''
        return self.xf_cmf, self.yf_cmf, self.zf_cmf

    def __get_full_data__(self):
        return self.nm_range, self.nm_interval, self.xf_cmf, self.yf_cmf, self.zf_cmf
    
    def set_cmf_into_visible_range_spectrum(self, visible_nm_range = [400,700], visible_nm_interval = 10):
        '''
        Method to set the spectral data into the visible spectrum.

        Parameters:
            visible_nm_range        list    [min, max] range in nm. Default: [400,700].
            visible_nm_interval     int     Interval in nm. Default: 10.

        '''
        self.xf_cmf.set_into_visible_range_spectrum(visible_nm_range, visible_nm_interval)
        self.yf_cmf.set_into_visible_range_spectrum(visible_nm_range, visible_nm_interval)
        self.zf_cmf.set_into_visible_range_spectrum(visible_nm_range, visible_nm_interval)
        # update
        self.nm_range = visible_nm_range
        self.nm_interval = visible_nm_interval
        
    # Akima works very well for cmf interpolation
    def cmf_interpolate(self, new_nm_range, new_nm_interval, method = "Akima"):
        '''
        Method to interpolate the spectral data of the xf_cmf, yf_cmf and zf_cmf.
        
        The interpolation methods implemented are: “Linear”, “Spline”, “CubicHermite”, 
        “Fifht”, “Sprague” and “Akima”.

        Parameters:
            new_nm_range       list    [min, max] range to interpolate.
            new_nm_interval    int     Interval in nm.
            method             str     Interpolation method. Default: “Akima”.
        
        '''
        self.xf_cmf.set_lambda_values_interpolate(new_nm_range, new_nm_interval, method)
        self.yf_cmf.set_lambda_values_interpolate(new_nm_range, new_nm_interval, method)
        self.zf_cmf.set_lambda_values_interpolate(new_nm_range, new_nm_interval, method)
        # update
        self.nm_range = new_nm_range
        self.nm_interval = new_nm_interval
        
    def cmf_extrapolate(self, new_nm_range, new_nm_interval, method = "Spline"):
        '''
        Method to extrapolate the spectral data of the xf_cmf, yf_cmf and zf_cmf CMFs.
        
        The extrapolate methods implemented are: “Spline”, “CubicHermite”, “Fourth” and “Fifht”.

        Note: Extrapolation of measured data may cause errors and shold be used only if it can be 
        demostrated that the resulting errors are insignificant for the porpoue of the user.
        
        CIE 015:2018. 7.2.3 Extrapolation and interpolation (pp. 24) (CIE, 2018).

        Parameters:
            new_nm_range       list    [min, max] range to interpolate.
            new_nm_interval    int     Interval in nm.
            method             str     Extrapolation method. Default: “Spline”.
        
        '''

        self.xf_cmf.set_lambda_values_extrapolate(new_nm_range, new_nm_interval, method)
        self.yf_cmf.set_lambda_values_extrapolate(new_nm_range, new_nm_interval, method)
        self.zf_cmf.set_lambda_values_extrapolate(new_nm_range, new_nm_interval, method)
        # update
        self.nm_range = new_nm_range
        self.nm_interval = new_nm_interval
                
    def plot(self, show_figure = True, save_figure = False, output_path = None):
        '''
        Method to create and display the plot of the xf_cmf, yf_cmf and zf_cmf CMFs using matplotlib.
        
        Parameters:
            show_figure    bool    If True, the plot is shown. Default: True.
            save_figure    bool    If True, the figure is saved at the output_path. Default: False.
            output_path    os      Path for the ouput figure. Default: None.
        
        '''

        cpt.plot_cfb(self.nm_range, self.nm_interval, self.xf_cmf.lambda_values, self.yf_cmf.lambda_values, self.zf_cmf.lambda_values, self.observer.observer, show_figure, save_figure, output_path)
    
    def __str__(self):
        obs = "2º standard observer (CIE 1931)" if self.observer.observer else "10º standard observer (CIE 1964)"
        return f"CIE cone-fundamental-based CMFs implementation for the {obs}."

class RGBCMF(CIE):
    ''' 
    RGBCMF class

    The RGBCMF class represents the CIE r_cmf, g_cmg and b_cmf colour-matching-functions

    CIE 015:2018. Annex B. B1. Determination of the r,g,b colour-matching-functions (pp. 82).
    CIE 015:2018. Table B.1 (pp.85-86). Table B.2 (pp.87-88).
    
    Parameters:
        observer    str, int    CIE standard observer. Default: 2.
                    Observer    

    Attributes:
        subtype     str         "CIE RGB colour-matching-functions"
        nm_range    list        lambda nm range [min, max]
        nm_interval int         lambda nm interval
        observer    Observer    CIE Observer
        r_cmf       Component   CIE r_cmf spectral data
        g_cmf       Component   CIE g_cmf spectral data
        b_cmf       Component   CIE b_cmf spectral data

    Methods:
        .get_colour_matching_functions()
        .set_cmf_into_visible_range_spectrum(visible_nm_range, visible_nm_interval)
        .cmf_interpolate(new_nm_range, new_nm_interval, method)
        .cmf_extrapolate(new_nm_range, new_nm_interval, method)
        .plot(show_figure, save_figure, output_path)
        
    '''

    __subtype = "CIE RGB colour-matching-functions"
    __nm_range = None
    __nm_interval = None
    __observer = None
    __r_cmf = None
    __g_cmf = None
    __b_cmf = None

    @property
    def subtype(self):
        return self.__subtype

    @property
    def oberver(self):
        return self.__observer
    
    @oberver.setter
    def observer(self, observer):
        if isinstance(observer, Observer):
            self.__observer  = observer
        else:
            self.__observer = Observer(observer)

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
        try:
            nm_interval = int(nm_interval)
        except:
            raise ClassTypeError("The input lambda nm interval is not a valid type argument.")
        self.__nm_interval = nm_interval

    @property
    def r_cmf(self):
        return self.__r_cmf
    
    @r_cmf.setter
    def r_cmf(self, r_cmf_components):
        nm_range, nm_interval, lambda_values  = r_cmf_components[0], r_cmf_components[1], r_cmf_components[2]
        self.__r_cmf = Component("r_cmf", nm_range, nm_interval, lambda_values)

    @property
    def g_cmf(self):
        return self.__g_cmf
    
    @g_cmf.setter
    def g_cmf(self, g_cmf_components):
        nm_range, nm_interval, lambda_values  = g_cmf_components[0], g_cmf_components[1], g_cmf_components[2]
        self.__g_cmf = Component("g_cmf", nm_range, nm_interval, lambda_values)

    @property
    def b_cmf(self):
        return self.__b_cmf
    
    @b_cmf.setter
    def b_cmf(self, b_cmf_components):
        nm_range, nm_interval, lambda_values  = b_cmf_components[0], b_cmf_components[1], b_cmf_components[2]
        self.__b_cmf = Component("b_cmf", nm_range, nm_interval, lambda_values)

    def __init__(self, observer=2):
        '''
        The RGBCMF class receives a valid str or int type for the specification of the 
        2º or 10º degree CIE standard observer, or an Observer instance class.
        Default: 2.
        
        '''  
        self.observer = observer
        rgbcmf = ld.load_cie_rgbcmf(self.observer.observer)

        self.nm_range = rgbcmf["lambda_nm_range"]
        self.nm_interval = rgbcmf["lambda_nm_interval"]

        self.r_cmf = [rgbcmf["lambda_nm_range"], rgbcmf["lambda_nm_interval"], rgbcmf["r_cmf"]]
        self.g_cmf = [rgbcmf["lambda_nm_range"], rgbcmf["lambda_nm_interval"], rgbcmf["g_cmf"]]
        self.b_cmf = [rgbcmf["lambda_nm_range"], rgbcmf["lambda_nm_interval"], rgbcmf["b_cmf"]]
        
    def get_colour_matching_functions(self):
        '''
        Returns the r_cmf, g_cmf and b_cmf CMFs as a Component objects.

        Returns:
            r_cmf, g_cmf, b_cmf    Component    RGB CMF

        '''
        return self.r_cmf, self.g_cmf, self.b_cmf

    def __get_full_data__(self):
        return self.nm_range, self.nm_interval, self.r_cmf, self.g_cmf, self.b_cmf
        
    def set_cmf_into_visible_range_spectrum(self, visible_nm_range = [400,700], visible_nm_interval = 10):
        '''
        Method to set the spectral data into the visible spectrum.

        Parameters:
            visible_nm_range        list    [min, max] range in nm. Default: [400,700]
            visible_nm_interval     int     Interval in nm. Default: 10

        '''
        self.r_cmf.set_into_visible_range_spectrum(visible_nm_range, visible_nm_interval)
        self.g_cmf.set_into_visible_range_spectrum(visible_nm_range, visible_nm_interval)
        self.b_cmf.set_into_visible_range_spectrum(visible_nm_range, visible_nm_interval)
        # update
        self.nm_range = visible_nm_range
        self.nm_interval = visible_nm_interval
            
    # Akima works very well for cmf interpolation
    def cmf_interpolate(self, new_nm_range, new_nm_interval, method = "Akima"):
        '''
        Method to interpolate the spectral data of the r_cmf, g_cmf and b_cmf CMFs.
        
        The interpolation methods implemented are: “Linear”, “Spline”, “CubicHermite”, 
        “Fifht”, “Sprague” and “Akima”.

        Parameters:
            new_nm_range       list    [min, max] range to interpolate.
            new_nm_interval    int     Interval in nm.
            method             str     Interpolation method. Default: “Akima”.
        
        '''

        self.r_cmf.set_lambda_values_interpolate(new_nm_range, new_nm_interval, method)
        self.g_cmf.set_lambda_values_interpolate(new_nm_range, new_nm_interval, method)
        self.b_cmf.set_lambda_values_interpolate(new_nm_range, new_nm_interval, method)
        # update
        self.nm_range = new_nm_range
        self.nm_interval = new_nm_interval
        
    def cmf_extrapolate(self, new_nm_range, new_nm_interval, method = "Spline"):
        '''
        Method to extrapolate the spectral data of the r_cmf, g_cmf and b_cmf.
        
        The extrapolate methods implemented are: “Spline”, “CubicHermite”, “Fourth” and “Fifht”.

        Note: Extrapolation of measured data may cause errors and shold be used only if it can be 
        demostrated that the resulting errors are insignificant for the porpoue of the user.
        
        CIE 015:2018. 7.2.3 Extrapolation and interpolation (pp. 24) (CIE, 2018).

        Parameters:
            new_nm_range       list    [min, max] range to interpolate.
            new_nm_interval    int     Interval in nm.
            method             str     Extrapolation method. Default: “Spline”.
        
        '''

        self.r_cmf.set_lambda_values_extrapolate(new_nm_range, new_nm_interval, method)
        self.g_cmf.set_lambda_values_extrapolate(new_nm_range, new_nm_interval, method)
        self.b_cmf.set_lambda_values_extrapolate(new_nm_range, new_nm_interval, method)
        # update
        self.nm_range = new_nm_range
        self.nm_interval = new_nm_interval
          
    def plot(self, show_figure = True, save_figure = False, output_path = None):
        '''
        Method to create and display the plot of the r_cmf, g_cmf and b_cmf CMFs using matplotlib.
        
        Parameters:
            show_figure    bool    If True, the plot is shown. Default: True.
            save_figure    bool    If True, the figure is saved at the output_path. Default: False.
            output_path    os      Path for the ouput figure. Default: None.
        
        '''   

        cpt.plot_rgbcmf(self.nm_range, self.nm_interval, self.r_cmf.lambda_values, self.g_cmf.lambda_values, self.b_cmf.lambda_values, self.observer.observer, show_figure, save_figure, output_path)

    def __str__(self):
        obs = "2º standard observer (CIE 1931)" if self.observer.observer else "10º standard observer (CIE 1964)"
        return f"CIE RGB colour-matching-functions implementation for the {obs}."


class Colour(ABC):
    ''' 
    Colour abstrac class

    Attributes:
        type             str                 "Colour Object"
        illuminant       str                 CIE illuminant 
                         Illuminant,         
                         IlluminantFromCCT,   
                         MeasuredIlluminant
        observer         Observer            CIE Observer
        coordinates      list                Colour coordinates

    Methods:
        .get_sample()

    '''

    __type = "Colour Object"
    __illuminant = None
    __observer = None
    __coordinates = None
        
    @property
    def type(self):
        return self.__type

    @property
    def illuminant(self):
        return self.__illuminant

    @illuminant.setter
    def illuminant(self, illuminant):
        if isinstance(illuminant, str):
            if ld.illuminant_is_cie(illuminant):
                self.__illuminant = Illuminant(illuminant)
            else:
                raise CIEIlluminantError("The input illuminant is not a valid CIE standard illuminant.")
        elif isinstance(illuminant, Illuminant):
            self.__illuminant = illuminant
        elif isinstance(illuminant, MeasuredIlluminant):
            self.__illuminant = illuminant
        elif isinstance(illuminant, IlluminantFromCCT):
            self.__illuminant = illuminant

    def __illuminant_is_CIE__(self, illuminant):
        if isinstance(illuminant, str):
            if ld.illuminant_is_cie(illuminant):
                return True
            else:
                raise CIEIlluminantError("The input illuminant is not a valid CIE standard illuminant.")
        elif isinstance(illuminant, Illuminant):
            return True
        else:
            raise CIEIlluminantError("The input illuminant is not a valid CIE standard illuminant.")

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
    def coordinates(self):
        return self.__coordinates
    
    @coordinates.setter
    def coordinates(self, list_coordinates):
        try:
            c1, c2, c3 = float(list_coordinates[0]), float(list_coordinates[1]), float(list_coordinates[2])
        except:
            raise ClassTypeError("The input coordinates are not in a valid type format.")
        self.__coordinates = [c1, c2, c3]

    @abstractmethod
    def __init__(self):
        pass
    
    def get_sample(self):
        '''
        Returns the colour object information as a dict
        
        '''
        sample = {self.name_id: self.coordinates}
        return sample 

    def __update__(self, illuminant, observer, coordinates):
        self.illuminant = illuminant
        self.observer = observer
        self.coordinates = coordinates

class CIEXYZ(Colour, CIE):
    ''' 
    CIEXYZ colour class

    The CIEXYZ class represents a colour object in the CIE XYZ colour space

    Parameters:
        name_id               str           Sample ID
        X                     float         X tristimulus value
        Y                     float         Y tristimulus value
        Z                     float         Z tristimulus value
        cie_illuminant        str           CIE illuminant. Default: "D65"
                              Illuminant,   
        observer              str, int      CIE Observer
                              Observer
                        
    Attributes:
        subtype               str           "CIE XYZ" 
        name_id               str           Sample ID
        illuminant            Illuminant    CIE Illuminant
        observer              Observer      CIE Observer
        coordinates           list, float   X, Y, Z coordinates

    Methods:
        .to_xyY()
        .to_uvY()
        .to_LAB()
        .to_LCHab()
        .to_LUV()
        .to_LCHuv()
        .to_RGB(rgb_name_space="sRGB")
        .to_CIE_illuminant(to_cie illuminant_name, to_observer, cat_model)
        .to_user_illuminant(Xn2, Yn2, Zn2, to_illuminant_name, to_observer, cat_model)

    '''

    __subtype = "CIE XYZ" 
    __name_id = None
                
    @property
    def subtype(self):
        return self.__subtype

    @subtype.setter
    def subtype(self, subtype):
        self.__subtype = subtype

    @property
    def name_id(self):
        return self.__name_id
    
    @name_id.setter
    def name_id(self, name_id):
        self.__name_id = name_id
    
    def __init__(self, name_id, X, Y, Z, cie_illuminant = "D65", observer = 2):
        self.__illuminant_is_CIE__(cie_illuminant)
        self.__update__(name_id, cie_illuminant, observer, [X, Y, Z])

    def colour_space(self):
        return self.__subtype
    
    def __update__(self, name_id, illuminant, observer, coordinates):
        super().__update__(illuminant, observer, coordinates)
        self.name_id = name_id
    
    def __get_illuminant_xyz_white_point__(self):
        WP = WhitePoint(self.illuminant, self.observer.observer)
        return WP.coordinates
    
    # tested with colormath and fits perfect
    def to_xyY(self):
        X, Y, Z = self.coordinates
        x, y, Y = csc.XYZ_to_xyY(X, Y, Z)
        return CIExyY(self.name_id, x, y, Y, self.illuminant, self.observer)
    
    def to_uvY(self):
        X, Y, Z = self.coordinates
        u, v, _ = csc.XYZ_to_uvY(X, Y, Z)
        return CIEuvY(self.name_id, u, v, Y, self.illuminant, self.observer)
    
    # tested with colormath. 
    # Slight differences in the second decimal place (depending on the accuracy of the input white point)
    # I'm using the CIE published standard white point values
    def to_LAB(self):
        X, Y, Z = self.coordinates
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        L, a, b = csc.XYZ_to_LAB(X, Y, Z, Xn, Yn, Zn) 
        return CIELAB(self.name_id, L, a, b, self.illuminant, self.observer)
    
    def to_LCHab(self):
        X, Y, Z = self.coordinates
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__() 
        L, a, b = csc.XYZ_to_LAB(X, Y, Z, Xn, Yn, Zn)
        L, Cab, Hab = csc.LAB_to_LCHab(L, a, b)
        return CIELCHab(self.name_id, L, Cab, Hab, self.illuminant, self.observer)
        
    # tested with colormath. 
    # Slight differences in the second decimal place (depending on the accuracy of the input white point)
    # I'm using the CIE published standard white point values
    def to_LUV(self):
        X, Y, Z = self.coordinates
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        L, U, V = csc.XYZ_to_LUV(X, Y, Z, Xn, Yn, Zn)
        return CIELUV(self.name_id, L, U, V, self.illuminant, self.observer)

    def to_LCHuv(self):
        X, Y, Z = self.coordinates
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__() 
        L, U, V = csc.XYZ_to_LUV(X, Y, Z, Xn, Yn, Zn)
        L, Cuv, Huv = csc.LUV_to_LCHuv(L,U,V)
        return CIELCHuv(self.name_id, L, Cuv, Huv, self.illuminant, self.observer)     

    # check illuminant first: XYZ--->sRGB only for D65 and 2º obs
    def to_RGB(self, rgb_name_space = "sRGB"):
        X, Y, Z = self.coordinates
        # only for "D65" and 2 observer
        if self.illuminant.illuminant_name == "D65" and self.observer.observer == 2:         
            R, G, B = csc.XYZ_to_RGB(X, Y, Z, rgb_name_space) #, rgb_name_space, bits)
        else:
            Xn1, Yn1, Zn1 = self.__get_illuminant_xyz_white_point__()
            WP2 = WhitePoint(illuminant="D65", observer=self.observer.observer)
            Xn2, Yn2, Zn2 = WP2.coordinates
            X2, Y2, Z2 = cat.apply_CATs_transform( X, Y, Z, Xn1, Yn1, Zn1, Xn2, Yn2, Zn2, cat_model="von Kries")           
            R, G, B = csc.XYZ_to_RGB(X2, Y2, Z2, rgb_name_space) #, rgb_name_space, bits)
            
        if rgb_name_space=="sRGB":
            return sRGB(self.name_id, R, G, B, self.observer.observer)
        elif rgb_name_space=="Adobe":
            return AdobeRGB(self.name_id, R, G, B, self.observer.observer)
        elif rgb_name_space=="Apple":
            return AppleRGB(self.name_id, R, G, B, self.observer.observer)

    # CAT's
    def to_CIE_illuminant(self, to_cie_illuminant_name, to_observer, cat_model="von Kries"): # cat
        X, Y, Z = self.coordinates
        Xn1, Yn1, Zn1 = self.__get_illuminant_xyz_white_point__()
        WP2 = WhitePoint(to_cie_illuminant_name, to_observer)
        Xn2, Yn2, Zn2 = WP2.coordinates
        X2, Y2, Z2 = cat.apply_CATs_transform(X, Y, Z, Xn1, Yn1, Zn1, Xn2, Yn2, Zn2, cat_model)
        return  CIEXYZ(self.name_id, X2, Y2, Z2, to_cie_illuminant_name, to_observer)      

    # to another CIE illuminant or other white point
    # params = {"cie_illuminant": cie_illuminant_name, "observer": observer}
    # params = {"X": X, "Y":Y, "Z": Z, "observer":observer}
    def to_user_illuminant(self, Xn2, Yn2, Zn2, cat_model="Sharp"):
        X, Y, Z = self.coordinates
        Xn1, Yn1, Zn1 = self.__get_illuminant_xyz_white_point__()
        X2, Y2, Z2 = cat.apply_CATs_transform(X, Y, Z, Xn1, Yn1, Zn1, Xn2, Yn2, Zn2, cat_model)
        return  X2, Y2, Z2 

    def __str__(self):
        return f"CIEXYZ object: {self.name_id} : X ={self.coordinates[0]}, Y={self.coordinates[1]}, Z={self.coordinates[2]}"

class CIExyY(Colour, CIE):
    ''' 
    CIExyY class

    Parameters:
        name_id               str           Sample ID
        x                     float         x coordinate
        y                     float         y coordinate
        Y                     float         Y
        cie_illuminant        str           CIE illuminant. Default: "D65"
                              Illuminant,   
        observer              str, int      CIE Observer
                              Observer

    Attributes:
        subtype               str           "CIE xyY" 
        name_id               str           Sample ID
        illuminant            Illuminant    CIE Illuminant
        observer              Observer      CIE Observer
        coordinates           list, float   x, y, Y coordinates

    Methods:
        .to_xyY()
        .to_uvY()
        .to_LAB()
        .to_LCHab()
        .to_LUV()
        .to_LCHuv()
        .to_RGB(rgb_name_space = "sRGB")
        .plot(show_figure = True, save_figure = False, output_path = None)

    '''

    __subtype = "CIE xyY" 
    __name_id = None
    
    @property
    def subtype(self):
        return self.__subtype
    
    @property
    def name_id(self):
        return self.__name_id
    
    @name_id.setter
    def name_id(self, name_id):
        self.__name_id = name_id

    def __init__(self, name_id, x, y , Y, cie_illuminant = "D65", observer = 2):
        self.__illuminant_is_CIE__(cie_illuminant)
        self.__update__(name_id, cie_illuminant, observer, [x, y, Y])

    def colour_space(self):
        return self.__subtype
            
    def __update__(self, name_id, illuminant_name, observer, coordinates):
        super().__update__(illuminant_name, observer, coordinates)
        self.name_id = name_id
    
    def __get_illuminant_xyz_white_point__(self):
        WP = WhitePoint(self.illuminant, self.observer.observer)
        return WP.coordinates
        
    # tested and fits perfect
    def to_XYZ(self):
        x, y, Y = self.coordinates
        X, Y, Z = csc.xyY_to_XYZ(x, y, Y)
        return CIEXYZ(self.name_id, X, Y, Z, self.illuminant, self.observer)

    def to_uvY(self):
        x, y, Y = self.coordinates
        u, v = csc.xy_to_uv(x,y)
        return CIEuvY(self.name_id, u, v, Y, self.illuminant, self.observer)

    def to_LAB(self):
        x, y, Y = self.coordinates
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.xyY_to_XYZ(x, y, Y)
        L, a, b = csc.XYZ_to_LAB(X, Y, Z, Xn, Yn, Zn)
        return CIELAB(self.name_id, L, a, b, self.illuminant, self.observer)       
        
    def to_LCHab(self):
        x, y, Y = self.coordinates
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.xyY_to_XYZ(x, y, Y)
        L, a, b = csc.XYZ_to_LAB(X, Y, Z, Xn, Yn, Zn)
        L, Cab, Hab = csc.LAB_to_LCHab(L, a, b)
        return CIELCHab(self.name_id, L, Cab, Hab, self.illuminant, self.observer)
    
    # tested with colormath. 
    # Slight differences in the second decimal place (depending on the accuracy of the input white point)
    # I'm using the CIE published standard white point values    
    def to_LUV(self):
        x, y, Y = self.coordinates
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        L, U, V = csc.xyY_to_LUV(x, y, Y, Xn, Yn, Zn)
        return CIELUV(self.name_id, L, U, V, self.illuminant, self.observer)

    def to_LCHuv(self):
        x, y, Y = self.coordinates
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()     
        L, U, V = csc.xyY_to_LUV(x, y, Y, Xn, Yn, Zn)
        L, Cuv, Huv = csc.LUV_to_LCHuv(L, U, V)
        return CIELCHuv(self.name_id, L, Cuv, Huv, self.illuminant, self.observer)

    def to_RGB(self, rgb_name_space = "sRGB"):
        x, y, Y = self.coordinates
        if self.illuminant.illuminant_name == "D65" and self.observer.observer == 2:         
            X, Y, Z = csc.xyY_to_XYZ(x, y, Y)
            R, G, B = csc.XYZ_to_RGB(X, Y, Z, rgb_name_space)
        else:
            X, Y, Z = csc.xyY_to_XYZ(x, y, Y)
            Xn1, Yn1, Zn1 = self.__get_illuminant_xyz_white_point__()
            WP2 = WhitePoint(to_cie_illuminant_name="D65", to_observer=self.observer.observer)
            Xn2, Yn2, Zn2 = WP2.coordinates
            X2, Y2, Z2 = cat.apply_CATs_transform(X, Y, Z, Xn1, Yn1, Zn1, Xn2, Yn2, Zn2, cat_model="von Kries")           
            R, G, B = csc.XYZ_to_RGB(X2, Y2, Z2, rgb_name_space) #, rgb_name_space, bits)
            
        if rgb_name_space=="sRGB":
            return sRGB(self.name_id, R, G, B, self.observer.observer)
        elif rgb_name_space=="Adobe":
            return AdobeRGB(self.name_id, R, G, B, self.observer.observer)
        elif rgb_name_space=="Apple":
            return AppleRGB(self.name_id, R, G, B, self.observer.observer)

    def plot(self, show_figure = True, save_figure = False, output_path = None): # add optinal params: plot or not boundary
        '''
        Method to create and display the x,y into the CIE 1931 x,y Chromaticity Diagram using Matplotlib
        
        Parameters:
            show_figure    bool    If True, the plot is shown. Default: True.
            save_figure    bool    If True, the figure is saved at the output_path. Default: False.
            output_path    os      Path for the ouput figure. Default: None.
        
        '''   

        cpt.plot_chromaticity_diagram(self.get_sample(), show_figure, save_figure, output_path)    

    def __str__(self):
        return f"CIExyY object: {self.name_id} : x ={self.coordinates[0]}, y={self.coordinates[1]}, Y={self.coordinates[2]}"


class CIEuvY(Colour, CIE):
    ''' 
    CIEuvY class

    Parameters:
        name_id               str           Sample ID
        u                     float         u' coordinate
        v                     float         v' coordinate
        Y                     float         Y
        cie_illuminant        str           CIE illuminant. Default: "D65"
                              Illuminant,   
        observer              str, int      CIE Observer
                              Observer

    Attributes:
        subtype               str           "CIE u'v'Y" 
        name_id               str           Sample ID
        illuminant            Illuminant    CIE Illuminant
        observer              Observer      CIE Observer
        coordinates           list, float   u', v', Y coordinates

    Methods:
        .to_XYZ()
        .to_xyY()
        .to_LAB()
        .to_LCHab()
        .to_LUV()
        .to_LCHuv()
        .to_RGB(rgb_name_space = "sRGB")

    '''

    __subtype = "CIE u'v'Y" 
    __name_id = None

    @property
    def subtype(self):
        return self.__subtype
    
    @property
    def name_id(self):
        return self.__name_id
    
    @name_id.setter
    def name_id(self, name_id):
        self.__name_id = name_id

    def __init__(self, name_id, u, v, Y, cie_illuminant = "D65", observer = 2):
        self.__illuminant_is_CIE__(cie_illuminant)
        self.__update__(name_id, cie_illuminant, observer, [u, v, Y])

    def colour_space(self):
        return self.__subtype
            
    def __update__(self, name_id, illuminant, observer, coordinates):
        super().__update__(illuminant, observer, coordinates)
        self.name_id = name_id
    
    def __get_illuminant_xyz_white_point__(self):
        WP = WhitePoint(self.illuminant, self.observer.observer)
        return WP.coordinates

    def to_XYZ(self):
        u, v, Y = self.coordinates
        X, Y, Z = csc.uvY_to_XYZ(u, v, Y)
        return CIEXYZ(self.name_id, X, Y, Z, self.illuminant, self.observer)

    def to_xyY(self):
        u, v, Y = self.coordinates
        x, y = csc.uv_to_xy(u, v)
        return CIExyY(self.name_id, x, y, Y, self.illuminant, self.observer)
    
    def to_LAB(self):
        u, v, Y = self.coordinates
        X, Y, Z = csc.uvY_to_XYZ(u, v, Y)
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        L, a, b = csc.XYZ_to_LAB(X, Y, Z, Xn, Yn, Zn)
        return CIELAB(self.name_id, L, a, b, self.illuminant, self.observer)
        
    def to_LCHab(self):
        u, v, Y = self.coordinates
        X, Y, Z = csc.uvY_to_XYZ(u, v, Y)
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        L, a, b = csc.XYZ_to_LAB(X, Y, Z, Xn, Yn, Zn)
        L, Cab, Hab = csc.LAB_to_LCHab(L, a, b)
        return CIELCHab(self.name_id, L, Cab, Hab, self.illuminant, self.observer)
    
    # tested with colormath. 
    # Slight differences in the second decimal place (depending on the accuracy of the input white point)
    # I'm using the CIE published standard white point values    
    def to_LUV(self):
        u, v, Y = self.coordinates
        X, Y, Z = csc.uvY_to_XYZ(u, v, Y)
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        L, U, V = csc.XYZ_to_LUV(X, Y, Z, Xn, Yn, Zn)
        return CIELUV(self.name_id, L, U, V, self.illuminant, self.observer)

    def to_LCHuv(self):
        u, v, Y = self.coordinates
        X, Y, Z = csc.uvY_to_XYZ(u, v, Y)
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        L, U, V = csc.XYZ_to_LUV(X, Y, Z, Xn, Yn, Zn)
        L, Cuv, Huv = csc.LUV_to_LCHuv(L, U, V)
        return CIELCHuv(self.name_id, L, Cuv, Huv, self.illuminant, self.observer)

    def to_RGB(self, rgb_name_space = "sRGB"):
        u, v, Y = self.coordinates
        if self.illuminant.illuminant_name == "D65" and self.observer.observer == 2:         
            X, Y, Z = csc.uvY_to_XYZ(u, v, Y)
            R, G, B = csc.XYZ_to_RGB(X, Y, Z, rgb_name_space)
        else:
            X, Y, Z = csc.uvY_to_XYZ(u, v, Y)
            Xn1, Yn1, Zn1 = self.__get_illuminant_xyz_white_point__()
            WP2 = WhitePoint(illuminant="D65", observer=self.observer.observer)
            Xn2, Yn2, Zn2 = WP2.coordinates
            X2, Y2, Z2 = cat.apply_CATs_transform(X, Y, Z, Xn1, Yn1, Zn1, Xn2, Yn2, Zn2, cat_model="von Kries")           
            R, G, B = csc.XYZ_to_RGB(X2, Y2, Z2, rgb_name_space) #, rgb_name_space, bits)
            
        if rgb_name_space=="sRGB":
            return sRGB(self.name_id, R, G, B, self.observer.observer)
        elif rgb_name_space=="Adobe":
            return AdobeRGB(self.name_id, R, G, B, self.observer.observer)
        elif rgb_name_space=="Apple":
            return AppleRGB(self.name_id, R, G, B, self.observer.observer)

    def __str__(self):
        return f"CIEuvY object: {self.name_id} : u' ={self.coordinates[0]}, v'={self.coordinates[1]}, Y={self.coordinates[2]}"


class CIELAB(Colour, CIE):
    ''' 
    CIELAB class
    
    Parameters:
        name_id               str            Sample ID
        L                     float          L coordinate
        a                     float          a coordinate
        b                     float          b coordinate
        cie_illuminant        str            CIE illuminant. Default: "D65"
                              Illuminant,    
        observer              str, int       CIE Observer
                              Observer

    Attributes:
        subtype               str            "CIE LAB" 
        name_id               str            Sample ID
        illuminant            Illuminant     CIE Illuminant 
        observer              Observer       CIE Observer
        coordinates           list, float    L, a, b coordinates

    '''

    __subtype = "CIE LAB" 
    __name_id = None
                
    @property
    def subtype(self):
        return self.__subtype
        
    @property
    def name_id(self):
        return self.__name_id
    
    @name_id.setter
    def name_id(self, name_id):
        self.__name_id = name_id

    def __init__(self, name_id, L, a, b, cie_illuminant = "D65", observer = 2):
        self.__illuminant_is_CIE__(cie_illuminant)
        self.__update__(name_id, cie_illuminant, observer, [L, a, b])

    def colour_space(self):
        return self.subtype
    
    def __update__(self, name_id, illuminant, observer, coordinates):
        super().__update__(illuminant, observer, coordinates)
        self.name_id = name_id
    
    def __get_illuminant_xyz_white_point__(self):
        WP = WhitePoint(self.illuminant, self.observer.observer)
        return WP.coordinates

    # tested with colormath. 
    # Slight differences in the second decimal place (depending on the accuracy of the input white point)
    # I'm using the CIE published standard white point values   
    def to_XYZ(self):
        L, a, b = self.coordinates
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.LAB_to_XYZ(L, a, b, Xn, Yn, Zn)
        return CIEXYZ(self.name_id, X, Y, Z, self.illuminant, self.observer)
    
    def to_xyY(self):
        L, a, b = self.coordinates
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.LAB_to_XYZ(L, a, b, Xn, Yn, Zn)
        x, y, Y = csc.XYZ_to_xyY(X, Y, Z)
        return CIExyY(self.name_id, x, y, Y, self.illuminant, self.observer)        
    
    def to_uvY(self):
        L, a, b = self.coordinates
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.LAB_to_XYZ(L, a, b, Xn, Yn, Zn)    
        u, v, Y = csc.XYZ_to_uvY(X, Y, Z)
        return CIEuvY(self.name_id, u, v, Y, self.illuminant, self.observer)   

    # tested with colormath. 
    # Slight differences in the second decimal place (depending on the accuracy of the input white point)
    # I'm using the CIE published standard white point values   
    def to_LCHab(self):
        L, a, b = self.coordinates
        L, Cab, Hab = csc.LAB_to_LCHab(L, a, b)
        return CIELCHab(self.name_id, L, Cab, Hab, self.illuminant, self.observer)
    
    def to_LCHuv(self):
        L, a, b = self.coordinates
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.LAB_to_XYZ(L, a, b, Xn, Yn, Zn)
        L, U, V = csc.XYZ_to_LUV(X, Y, Z, Xn, Yn, Zn)
        L, Cuv, Huv = csc.LUV_to_LCHuv(L, U, V)
        return CIELCHuv(self.name_id, L, Cuv, Huv, self.illuminant, self.observer)

    def to_LUV(self):
        L, a, b = self.coordinates
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.LAB_to_XYZ(L, a, b, Xn, Yn, Zn)
        L, U, V = csc.XYZ_to_LUV(X, Y, Z, Xn, Yn, Zn)
        return CIELUV(self.name_id, L, U, V, self.illuminant, self.observer)

    def to_RGB(self, rgb_name_space = "sRGB"):
        L, a, b = self.coordinates
        if self.illuminant.illuminant_name == "D65" and self.observer.observer == 2:         
            Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
            X, Y, Z = csc.LAB_to_XYZ(L, a, b, Xn, Yn, Zn)
            R, G, B = csc.XYZ_to_RGB(X, Y, Z, rgb_name_space)
        else:
            Xn1, Yn1, Zn1 = self.__get_illuminant_xyz_white_point__()
            X, Y, Z = csc.LAB_to_XYZ(L,a,b, Xn1, Yn1, Zn1)  
            WP2 = WhitePoint(illuminant="D65", observer=self.observer.observer)
            Xn2, Yn2, Zn2 = WP2.coordinates
            X2, Y2, Z2 = cat.apply_CATs_transform(X, Y, Z, Xn1, Yn1, Zn1, Xn2, Yn2, Zn2, cat_model="von Kries")           
            R, G, B = csc.XYZ_to_RGB(X2, Y2, Z2, rgb_name_space) #, rgb_name_space, bits)
            
        if rgb_name_space=="sRGB":
            return sRGB(self.name_id, R, G, B, self.observer.observer)
        elif rgb_name_space=="Adobe":
            return AdobeRGB(self.name_id, R, G, B, self.observer.observer)
        elif rgb_name_space=="Apple":
            return AppleRGB(self.name_id, R, G, B, self.observer.observer)

    def delta_e_ab(self, target):
        '''
        Funtion to compute the CIE76 colour difference between two colour samples in CIELAB units
    
        CIE015:2018. 8.2.1.3. Colour differences. Eq. 8.14, 8.15, 8.16 and 8.21 (p.29)

        Parameters:
            target        CIELAB object    CIELAB target sample

        Returns:
            delta_e_ab    float            CIE76 colour difference value in CIELAB units

        '''

        if isinstance(target, CIELAB):
            if target.illuminant.illuminant_name == self.illuminant.illuminant_name:
                L1, a1, b1 = self.coordinates
                L2, a2, b2 = target.coordinates
                AE_ab = cde.delta_E_ab(L1, a1, b1, L2, a2, b2)
                return AE_ab
            else:
                raise CIEIlluminantError(f"The CIELAB target must be referred to the same illuminant {self.illuminant.illuminant_name}.")
        else:
            raise ClassTypeError("The input target is not a CIELAB colour object.")

    def CIEDE2000(self, target, kl=1, kc=1, kh=1):
        '''
        Funtion to compute the CIEDE000 colour difference between two colour samples in CIELAB units
    
        CIE015:2018. 8.3.1 CIEDE2000 colour-difference formula. Eq. 8.39 to 8.42 (p.33)

        Parameters:
            target        CIELAB object   CIELAB target sample

        Returns:
            AE00          float           CIEDE200 colour difference value in CIELAB units

        '''

        if isinstance(target, CIELAB):
            if target.illuminant.illuminant_name == self.illuminant.illuminant_name:
                L1, a1, b1 = self.coordinates
                L2, a2, b2 = target.coordinates
                AE00 = cde.CIEDE2000(L1, a1, b1, L2, a2, b2, kl, kc, kh)
                return AE00
            else:
                raise CIEIlluminantError(f"The CIELAB target must be referred to the same illuminant {self.illuminant.illuminant_name}.")
        else:
            raise ClassTypeError("The input target is not a CIELAB colour object.")            

    def plot(self, show_figure = True, save_figure = False, output_path = None): # add optinal params: plot or not boundary
        '''
        Method to create and display the L*a*b into the CIELAB diagram using Matplotlib
        
        Parameters:
            show_figure    bool    If True, the plot is shown. Default: True.
            save_figure    bool    If True, the figure is saved at the output_path. Default: False.
            output_path    os      Path for the ouput figure. Default: None.
        
        '''   

        cpt.plot_cielab(self.get_sample(), show_figure, save_figure, output_path)

    def __str__(self):
        return f"CIELAB object: {self.name_id} : L* ={self.coordinates[0]}, a*={self.coordinates[1]}, b*={self.coordinates[2]}"


class CIELCHab(Colour, CIE):
    ''' 
    CIELChab class

    Parameters:
        name_id               str           Sample ID
        L                     float         Lightness
        C                     float         Chroma
        hab                   float         hue in degrees
        cie_illuminant        str           CIE illuminant. Default: "D65"
                              Illuminant,   
        observer              str, int      CIE Observer
                              Observer

    Attributes:
        subtype               str            "CIE LCHab" 
        name_id               str            Sample ID
        illuminant            Illuminant     CIE Illuminant
        observer              Observer       CIE Observer
        coordinates           list, float    L, Cab, hab coordinates    
    
    '''

    __subtype = "CIE LCHab" 
    __name_id = None
                
    @property
    def subtype(self):
        return self.__subtype
        
    @property
    def name_id(self):
        return self.__name_id
    
    @name_id.setter
    def name_id(self, name_id):
        self.__name_id = name_id

    def __init__(self, name_id, L, Cab, Hab, cie_illuminant = "D65", observer = 2):
        self.__illuminant_is_CIE__(cie_illuminant)
        self.__update__(name_id, cie_illuminant, observer, [L, Cab, Hab])

    def colour_space(self):
        return self.__subtype
        
    def __update__(self, name_id, illuminant, observer, coordinates):
        super().__update__(illuminant, observer, coordinates)
        self.name_id = name_id
    
    def __get_illuminant_xyz_white_point__(self):
        WP = WhitePoint(self.illuminant, self.observer.observer)
        return WP.coordinates

    def to_XYZ(self):
        L, Cab, Hab = self.coordinates      
        L, a, b = csc.LCHab_to_LAB(L, Cab, Hab)
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.LAB_to_XYZ(L, a, b, Xn, Yn, Zn)
        return CIEXYZ(self.name_id, X, Y, Z, self.illuminant, self.observer)
    
    def to_xyY(self):
        L, Cab, Hab = self.coordinates      
        L, a, b = csc.LCHab_to_LAB(L, Cab, Hab)
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.LAB_to_XYZ(L, a, b, Xn, Yn, Zn)
        x, y, Y = csc.XYZ_to_xyY(X, Y, Z)
        return CIExyY(self.name_id, x, y, Y, self.illuminant, self.observer)

    def to_uvY(self):
        L, Cab, Hab = self.coordinates      
        L, a, b = csc.LCHab_to_LAB(L, Cab, Hab)
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.LAB_to_XYZ(L, a, b, Xn, Yn, Zn)  
        u, v, Y = csc.XYZ_to_uvY(X, Y, Z)
        return CIEuvY(self.name_id, u, v, Y, self.illuminant, self.observer)  

    # tested with colormath. 
    # Slight differences in the second decimal place (depending on the accuracy of the input white point)
    # I'm using the CIE published standard white point values      
    def to_LAB(self):
        L, Cab, Hab = self.coordinates      
        L, a, b = csc.LCHab_to_LAB(L, Cab, Hab)
        return CIELAB(self.name_id, L, a, b, self.illuminant, self.observer)
        
    def to_LCHuv(self):
        L, Cab, Hab = self.coordinates      
        L, a, b = csc.LCHab_to_LAB(L, Cab, Hab)
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.LAB_to_XYZ(L, a, b, Xn, Yn, Zn)
        L, U, V = csc.XYZ_to_LUV(X, Y, Z, Xn, Yn, Zn)
        L, Cuv, Huv = csc.LUV_to_LCHuv(L, U, V)
        return CIELCHuv(self.name_id, L, Cuv, Huv, self.illuminant, self.observer)

    def to_LUV(self):
        L, Cab, Hab = self.coordinates      
        L, a, b = csc.LCHab_to_LAB(L, Cab, Hab)
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.LAB_to_XYZ(L, a, b, Xn, Yn, Zn)
        L, U, V = csc.XYZ_to_LUV(X, Y, Z, Xn, Yn, Zn)
        return CIELUV(self.name_id, L, U, V, self.illuminant, self.observer)

    def to_RGB(self, rgb_name_space = "sRGB"):
        L, Cab, Hab = self.coordinates 
        if self.illuminant.illuminant_name == "D65" and self.observer.observer == 2: 
            L, a, b = csc.LCHab_to_LAB(L, Cab, Hab)
            Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
            X, Y, Z = csc.LAB_to_XYZ(L, a, b, Xn, Yn, Zn)
            R, G, B = csc.XYZ_to_RGB(X, Y, Z, rgb_name_space)
        else:    
            L, a, b = csc.LCHab_to_LAB(L, Cab, Hab)
            Xn1, Yn1, Zn1 = self.__get_illuminant_xyz_white_point__()
            X, Y, Z = csc.LAB_to_XYZ(L, a, b, Xn1, Yn1, Zn1)
            WP2 = WhitePoint(illuminant="D65", observer=self.observer.observer)
            Xn2, Yn2, Zn2 = WP2.coordinates
            X2, Y2, Z2 = cat.apply_CATs_transform(X, Y, Z, Xn1, Yn1, Zn1, Xn2, Yn2, Zn2, cat_model="von Kries")           
            R, G, B = csc.XYZ_to_RGB(X2, Y2, Z2, rgb_name_space) #, rgb_name_space, bits)
            
        if rgb_name_space=="sRGB":
            return sRGB(self.name_id, R, G, B, self.observer.observer)
        elif rgb_name_space=="Adobe":
            return AdobeRGB(self.name_id, R, G, B, self.observer.observer)
        elif rgb_name_space=="Apple":
            return AppleRGB(self.name_id, R, G, B, self.observer.observer)

    def delta_e_ab(self, target):
        '''
        Funtion to compute the CIE76 colour difference between two colour samples in CIELAB units
    
        CIE015:2018. 8.2.1.3. Colour differences. Eq. 8.14, 8.15, 8.16 and 8.21 (p.29)

        Parameters:
            target        CIELAB object    CIELAB target sample

        Returns:
            delta_e_ab    float            CIE76 colour difference value in CIELAB units

        '''

        if isinstance(target, CIELCHab):
            if target.illuminant.illuminant_name == self.illuminant.illuminant_name:
                L1, Cab1, Hab1 = self.coordinates
                L2, Cab2, Hab2 = target.coordinates
                AE_ab = cde.delta_E_ab_cielchab(L1, Cab1, Hab1, L2, Cab2, Hab2)
                return AE_ab
            else:
                raise CIEIlluminantError(f"The CIELCHab target must be referred to the same illuminant {self.illuminant.illuminant_name}.")
        else:
            raise ClassTypeError("The input target is not a CIELCHab colour object.")

    def hue_difference(self, target):
        '''
        Function to compute the Delta_Hue difference for colour samples in CIELAB coordinates

        CIE015:2018. 8.2.1.3. Colour differences. Eq. 8.19 (pg.29). 8.2.3. Note 3. (p.31)

        Parameters:
            target        CIELAB object    CIELAB target sample
    
        Returns:
            Delta_H       float            Delta_Hab for CIELAB 

        '''

        if isinstance(target, CIELCHab):
            if target.illuminant.illuminant_name == self.illuminant.illuminant_name:
                L1, Cab1, Hab1 = self.coordinates
                L2, Cab2, Hab2 = target.coordinates
                Ah = cde.compute_hue_angle_difference(Cab1, Hab1, Cab2, Hab2)
                AHab = cde.compute_Delta_H_difference(Cab1, Cab2, Ah)
                return AHab
            else:
                raise CIEIlluminantError(f"The CIELCHab target must be referred to the same illuminant {self.illuminant.illuminant_name}.")
        else:
            raise ClassTypeError("The input target is not a CIELCHab colour object.")

    def __str__(self):
        return f"CIELCHab object: {self.name_id} : L* ={self.coordinates[0]}, C*ab={self.coordinates[1]}, h*ab={self.coordinates[2]}"


class CIELUV(Colour, CIE):
    ''' 
    CIE LUV colour class
        
    Parameters:
        name_id               str            Sample ID
        L                     float          Lightness
        U                     float          u* coordinate
        V                     float          v* coordinate
        cie_illuminant        str            CIE illuminant name. Default: "D65"
                              Illuminant,    Valid Illuminant object
        observer              str, int       Valid CIE Observer
                              Observer

    Attributes:
        subtype               str            "CIE LUV" 
        name_id               str           Sample ID
        illuminant            str           CIE Illuminant 
        observer              Observer      CIE Observer
        coordinates           list, float   L, U, V coordinates    

    '''

    __subtype = "CIE LUV" 
    __name_id = None
                
    @property
    def subtype(self):
        return self.__subtype
    
    @property
    def name_id(self):
        return self.__name_id
    
    @name_id.setter
    def name_id(self, name_id):
        self.__name_id = name_id
        
    def __init__(self, name_id, L, U, V, cie_illuminant = "D65", observer = 2):
        self.__illuminant_is_CIE__(cie_illuminant)
        self.__update__(name_id, cie_illuminant, observer, [L, U, V])

    def colour_space(self):
        return self.__subtype
       
    def __update__(self, name_id, illuminant, observer, coordinates):
        super().__update__(illuminant, observer, coordinates)
        self.name_id = name_id
    
    def __get_illuminant_xyz_white_point__(self):
        WP = WhitePoint(self.illuminant, self.observer.observer)
        return WP.coordinates

    # tested with colormath. 
    # Slight differences in the second decimal place (depending on the accuracy of the input white point)
    # I'm using the CIE published standard white point values         
    def to_XYZ(self):
        L, U, V = self.coordinates
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.LUV_to_XYZ(L, U, V, Xn, Yn, Zn)
        return CIEXYZ(self.name_id, X, Y, Z, self.illuminant, self.observer)
    
    # tested with colormath. 
    # Slight differences in the second decimal place (depending on the accuracy of the input white point)
    # I'm using the CIE published standard white point values      
    def to_xyY(self):
        L, U, V = self.coordinates
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        x, y, Y = csc.LUV_to_xyY(L, U, V, Xn, Yn, Zn)
        return CIExyY(self.name_id, x, y, Y, self.illuminant, self.observer)

    def to_uvY(self):
        L, U, V = self.coordinates
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.LUV_to_XYZ(L, U, V, Xn, Yn, Zn)
        u, v, Y = csc.XYZ_to_uvY(X, Y, Z)
        return CIEuvY(self.name_id, u, v, Y, self.illuminant, self.observer)  

    def to_LAB(self):
        L, U, V = self.coordinates
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.LUV_to_XYZ(L, U, V, Xn, Yn, Zn)
        L, a, b = csc.XYZ_to_LAB(X, Y, Z, Xn, Yn, Zn)
        return CIELAB(self.name_id, L, a, b, self.illuminant, self.observer)
    
    def to_LCHab(self):
        L, U, V = self.coordinates
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.LUV_to_XYZ(L, U, V, Xn, Yn, Zn)
        L, a, b = csc.XYZ_to_LAB(X, Y, Z, Xn, Yn, Zn)
        L, Cab, Hab = csc.LAB_to_LCHab(L, a, b)
        return CIELCHab(self.name_id, L, Cab, Hab, self.illuminant, self.observer)
    
    def to_LCHuv(self):
        L, U, V = self.coordinates
        L, C, Huv = csc.LUV_to_LCHuv(L, U, V)
        return CIELCHuv(self.name_id, L, C, Huv, self.illuminant, self.observer)

    def to_RGB(self, rgb_name_space = "sRGB"):
        L, U, V = self.coordinates
        if self.illuminant.illuminant_name == "D65" and self.observer.observer == 2:         
            Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
            X, Y, Z = csc.LUV_to_XYZ(L, U, V, Xn, Yn, Zn)    
            R, G, B = csc.XYZ_to_RGB(X, Y, Z, rgb_name_space)
        else:
            Xn1, Yn1, Zn1 = self.__get_illuminant_xyz_white_point__()
            X, Y, Z = csc.LUV_to_XYZ(L, U, V, Xn1, Yn1, Zn1)
            WP2 = WhitePoint(illuminant="D65", observer=self.observer.observer)
            Xn2, Yn2, Zn2 = WP2.coordinates
            X2, Y2, Z2 = cat.apply_CATs_transform( X, Y, Z, Xn1, Yn1, Zn1, Xn2, Yn2, Zn2, cat_model="von Kries")           
            R, G, B = csc.XYZ_to_RGB(X2, Y2, Z2, rgb_name_space) #, rgb_name_space, bits)
            
        if rgb_name_space=="sRGB":
            return sRGB(self.name_id, R, G, B, self.observer.observer)
        elif rgb_name_space=="Adobe":
            return AdobeRGB(self.name_id, R, G, B, self.observer.observer)
        elif rgb_name_space=="Apple":
            return AppleRGB(self.name_id, R, G, B, self.observer.observer)
    
    def get_saturation(self):
        '''
        Function to compute the CIE 1976 u*, v* (CIELUV) saturatuion s_uv
    
        CIE015:2018. 8.2.2.2. Correlates of lightness, saturation, chroma and hue. Eq. 8.31 (pg.29)
    
        Returns:
            s_uv            float     s_uv saturation value
    
        '''
    
        L, U, V = self.coordinates
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        s_uv = csc.compute_saturation_uv(L, U, V, Xn, Yn, Zn)
        return s_uv

    def delta_e_uv(self, target):
        '''
        Funtion to compute the CIE76 colour difference between two colour samples in CIELUV units

        CIE015:2018. 8.2.2.3. Colour differences. Eq. 8.35 (pg.31)

        Parameters:
            target        CIELAB object    CIELAB target sample
    
        Returns:
            delta_e_uv    float    CIE76 colour difference value in CIELUV units

        '''
    
        if isinstance(target, CIELUV):
            if target.illuminant.illuminant_name == self.illuminant.illuminant_name:
                L1, U1, V1 = self.coordinates
                L2, U2, V2 = target.coordinates
                AEuv = cde.delta_E_uv(L1, U1, V1, L2, U2, V2)
                return AEuv
            else:
                raise CIEIlluminantError(f"The CIELUV sample must be referred to the same illuminant {self.illuminant.illuminant_name}.")
        else:
            raise ClassTypeError("The input sample is not a CIELUV colour object.")

    def __str__(self):
        return f"CIELUV object: {self.name_id} : L* ={self.coordinates[0]}, u*={self.coordinates[1]}, v*={self.coordinates[2]}"


class CIELCHuv(Colour, CIE):
    ''' 
    CIE LCHuv colour class
        
    Parameters:
        name_id               str           Sample ID
        L                     float         Lightness
        C                     float         Chroma
        huv                   float         hue in degree
        cie_illuminant        str           CIE illuminant name. Default: "D65"
                              Illuminant,   Valid Illuminant object
        observer              str, int      Valid CIE Observer
                              Observer

    Attributes:
        subtype               str            "CIE LCHuv" 
        name_id               str            Sample ID
        illuminant            Illuminant     CIE Illuminant
        observer              Observer       CIE Observer
        coordinates           list, float    L, Cuv, huv coordinates    

    '''

    __subtype = "CIE LCHuv" 
    __name_id = None
                
    @property
    def subtype(self):
        return self.__subtype
        
    @property
    def name_id(self):
        return self.__name_id
    
    @name_id.setter
    def name_id(self, name_id):
        self.__name_id = name_id
        
    def __init__(self, name_id, L, Cuv, Huv, cie_illuminant = "D65", observer = 2):
        self.__illuminant_is_CIE__(cie_illuminant)
        self.__update__(name_id, cie_illuminant, observer, [L, Cuv, Huv])
             
    def colour_space(self):
        return self.__subtype
    
    def __update__(self, name_id, illuminant, observer, coordinates):
        super().__update__(illuminant, observer, coordinates)
        self.name_id = name_id
    
    def __get_illuminant_xyz_white_point__(self):
        WP = WhitePoint(self.illuminant, self.observer.observer)
        return WP.coordinates

    def to_XYZ(self):
        L, Cuv, Huv = self.coordinates      
        L, U, V = csc.LCHuv_to_LUV(L, Cuv, Huv)
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.LUV_to_XYZ(L, U, V, Xn, Yn, Zn)
        return CIEXYZ(self.name_id, X, Y, Z, self.illuminant, self.observer)

    def to_xyY(self):
        L, Cuv, Huv = self.coordinates      
        L, U, V = csc.LCHuv_to_LUV(L, Cuv, Huv)
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        x, y, Y = csc.LUV_to_xyY(L, U, V, Xn, Yn, Zn)
        return CIExyY(self.name_id, x, y, Y, self.illuminant, self.observer)

    def to_uvY(self):
        L, Cuv, Huv = self.coordinates      
        L, U, V = csc.LCHuv_to_LUV(L, Cuv, Huv)
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.LUV_to_XYZ(L, U, V, Xn, Yn, Zn)
        u, v, Y = csc.XYZ_to_uvY(X, Y, Z)
        return CIEuvY(self.name_id, u, v, Y, self.illuminant, self.observer)  

    # tested with colormath. 
    # Slight differences in the second decimal place (depending on the accuracy of the input white point)
    # I'm using the CIE published standard white point values      
    def to_LAB(self):
        L, Cuv, Huv = self.coordinates      
        L, U, V = csc.LCHuv_to_LUV(L, Cuv, Huv)
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.LUV_to_XYZ(L, U, V, Xn, Yn, Zn)
        L, a, b = csc.XYZ_to_LAB(X, Y, Z, Xn, Yn, Zn)
        return CIELAB(self.name_id, L, a, b, self.illuminant, self.observer)

    def to_LCHab(self):
        L, Cuv, Huv = self.coordinates      
        L, U, V = csc.LCHuv_to_LUV(L, Cuv, Huv)
        Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
        X, Y, Z = csc.LUV_to_XYZ(L, U, V, Xn, Yn, Zn)
        L, a, b = csc.XYZ_to_LAB(X, Y, Z, Xn, Yn, Zn)
        L, Cab, Hab = csc.LAB_to_LCHab(L, a, b)
        return CIELCHab(self.name_id, L, Cab, Hab, self.illuminant, self.observer)

    def to_LUV(self):
        L, C, Huv = self.coordinates  
        L, U, V = csc.LCHuv_to_LUV(L, C, Huv)
        return CIELUV(self.name_id, L, U, V, self.illuminant, self.observer)
    
    def to_RGB(self, rgb_name_space = "sRGB"):
        L, C, Huv = self.coordinates 
        if self.illuminant.illuminant_name == "D65" and self.observer.observer == 2:         
            L, U, V = csc.LCHuv_to_LUV(L, C, Huv)
            Xn, Yn, Zn = self.__get_illuminant_xyz_white_point__()
            X, Y, Z = csc.LUV_to_XYZ(L, U, V, Xn, Yn, Zn)
            R, G, B = csc.XYZ_to_RGB(X, Y, Z, rgb_name_space)
        else:
            L, C, Huv = self.coordinates      
            L, U, V = csc.LCHuv_to_LUV(L, C, Huv)
            Xn1, Yn1, Zn1 = self.__get_illuminant_xyz_white_point__()
            X, Y, Z = csc.LUV_to_XYZ(L, U, V, Xn1, Yn1, Zn1)
            WP2 = WhitePoint(illuminant="D65", observer=self.observer.observer)
            Xn2, Yn2, Zn2 = WP2.coordinates
            X2, Y2, Z2 = cat.apply_CATs_transform(X, Y, Z, Xn1, Yn1, Zn1, Xn2, Yn2, Zn2, cat_model="von Kries")           
            R, G, B = csc.XYZ_to_RGB(X2, Y2, Z2, rgb_name_space) #, rgb_name_space, bits)
            
        if rgb_name_space=="sRGB":
            return sRGB(self.name_id, R, G, B, self.observer.observer)
        elif rgb_name_space=="Adobe":
            return AdobeRGB(self.name_id, R, G, B, self.observer.observer)
        elif rgb_name_space=="Apple":
            return AppleRGB(self.name_id, R, G, B, self.observer.observer)

    def delta_e_uv(self, target):
        '''
        Funtion to compute the CIE76 colour difference between two colour samples in CIELUV units

        CIE015:2018. 8.2.2.3. Colour differences. Eq. 8.35 (p.31)

        Parameters:
            target        CIELAB object    CIELAB target sample
    
        Returns:
            delta_e_uv    float    CIE76 colour difference value in CIELUV units

        '''
        if isinstance(target, CIELCHuv):
            if target.illuminant.illuminant_name == self.illuminant.illuminant_name:
                L1, Cuv1, Huv1 = self.coordinates
                L2, Cuv2, Huv2 = target.coordinates
                AEuv = cde.delta_E_uv_cielchuv(L1, Cuv1, Huv1, L2, Cuv2, Huv2)
                return AEuv
            else:
                raise CIEIlluminantError(f"The CIELCHuv target must be referred to the same illuminant {self.illuminant.illuminant_name}.")
        else:
            raise ClassTypeError("The input target is not a CIELCHuv colour object.")

    def hue_difference(self, target):
        '''
        Function to compute the Delta_Hue difference for colour samples in CIE LCHuv coordinates

        CIE015:2018. 8.2.2.3. Colour differences. Eq. 8.34 (p.31). 8.2.3. Note 3. (pp.31)

        Parameters:
            target      CIELCHuv  object    CIE LCHuv target sample
    
        Returns:
            Delta_H     float               Delta_Huv

        '''
        if isinstance(target, CIELCHuv):
            if target.illuminant.illuminant_name == self.illuminant.illuminant_name:
                L1, Cuv1, Huv1 = self.coordinates
                L2, Cuv2, Huv2 = target.coordinates
                Ah = cde.compute_hue_angle_difference(Cuv1, Huv1, Cuv2, Huv2)
                AHuv = cde.compute_Delta_H_difference(Cuv1, Cuv2, Ah)
                return AHuv
            else:
                raise CIEIlluminantError(f"The CIELCHab target must be referred to the same illuminant {self.illuminant_name}.")
        else:
            raise ClassTypeError("The input target is not a CIELCHab colour object.")

    def __str__(self):
        return f"CIELCHuv object: {self.name_id} : L* ={self.coordinates[0]}, C*uv={self.coordinates[1]}, h*uv={self.coordinates[2]}"


class GenericRGB(Colour):
    '''  
    Class for a generic RGB colour

    '''

    __subtype = "Generic RGB colour"
    __name_id = None

    def __init__(self, name_id, R, G, B, illuminant_name, observer):
        super().__update__(illuminant_name, observer, [R, G, B])
        self.name_id = name_id

    @property
    def subtype(self):
        return self.__subtype
    
    @property
    def name_id(self):
        return self.__name_id
    
    @name_id.setter
    def name_id(self, name_id):
        self.__name_id = name_id
    
    @abstractmethod
    def to_XYZ(self):
        pass

class CameraRGB(GenericRGB):
    
    __subtype = "Camera RGB data"
    __name_id = None
    __mode_raw = None
    
    def __init__(self, name_id, R, G, B, illuminant_name, observer, mode_raw = True):
        super().__init__(name_id, R, G, B, illuminant_name, observer)
        self.mode_raw = mode_raw

    @property
    def subtype(self):
        return self.__subtype

    def colour_space(self):
        return self.__subtype

    @property
    def name_id(self):
        return self.__name_id
    
    @name_id.setter
    def name_id(self, name_id):
        self.__name_id = name_id

    @property
    def mode_raw(self):
        return self.__mode_raw
    
    @mode_raw.setter
    def mode_raw(self, mode_raw):
        if isinstance(mode_raw, bool):
            self.__mode_raw = mode_raw
        else:
            raise ClassTypeError("Type not valid for the mode raw.")

    # use a 3x3 array
    def to_XYZ(self, rgb_xyz_matrix):
        M = np.array(rgb_xyz_matrix, dtype = np.double)
        rgb = self.coordinates
        R = np.array(rgb, dtype = np.double)
        X, Y, Z = np.dot(M,R)
        if ld.illuminant_is_cie(self.illuminant_name.upper()):
            return CIEXYZ(self.name_id, X*100, Y*100, Z*100, self.illuminant_name, self.observer)
        else:
            return X*100, Y*100, Z*100
    
class AdobeRGB(GenericRGB):
    
    __subtype = "Adobe"
    __name_id = None
    
    def __init__(self, name_id, aR, aG, aB, observer = 2):
        self.__update__("D65", observer, [aR, aG, aB])
        self.name_id = name_id

    @property
    def subtype(self):
        return self.__subtype

    @property
    def name_id(self):
        return self.__name_id
    
    @name_id.setter
    def name_id(self, name_id):
        self.__name_id = name_id

    def colour_space(self):
        return self.__subtype

    def to_XYZ(self):
        print("Not implemented yet")


class AppleRGB(GenericRGB):
    
    __subtype = "Adobe"
    __name_id = None
    
    def __init__(self, name_id, iR, iG, iB, observer = 2):
        self.__update__("D65", observer, [iR, iG, iB])
        self.name_id = name_id

    @property
    def subtype(self):
        return self.__subtype
    
    def colour_space(self):
        return self.__subtype
    
    @property
    def name_id(self):
        return self.__name_id
    
    @name_id.setter
    def name_id(self, name_id):
        self.__name_id = name_id

    def to_XYZ(self):
        print("Not implemented yet")
        pass

class sRGB(GenericRGB, CIE):
    
    __subtype = "sRGB"
    __name_id = None
    
    def __init__(self, name_id, sR, sG, sB, observer = 2):
        self.__update__("D65", observer, [sR, sG, sB])
        self.name_id = name_id

    @property
    def subtype(self):
        return self.__subtype

    @property
    def name_id(self):
        return self.__name_id
    
    @name_id.setter
    def name_id(self, name_id):
        self.__name_id = name_id

    def colour_space(self):
        return self.__subtype

    def to_XYZ(self):
        sR, sG, sB = self.coordinates
        X, Y, Z = csc.RGB_to_XYZ(sR,sG,sB, self.colour_space())
        XYZ = CIEXYZ( self.name_id, X, Y, Z, self.illuminant, self.observer.observer)
        return XYZ

    def __str__(self):
        return f"sRGB object: {self.name_id} : sR ={self.coordinates[0]}, sG={self.coordinates[1]}, sB={self.coordinates[2]}"

class WhitePoint(Colour):
    '''
    WhitePoint class 

    The WhitePoint class represents a white point (or reference target) object of a given illuminant in XYZ coordinates.

    Theoretical data are available only for CIE Illuminants: A, C, D50, D55, D65, D75
    Computed data is performed for all remaining illuminants

    Parameters:
        illuminant            str, Illuminant          Illuminant. Default: "D65"
                              IlluminantFromCCT,
                              measuredIlluminant         
        observer              str, int                 CIE Observer. Default: 2
                              Observer
                        
    Attributes:
        subtype               str                      "WhitePoint XYZ" 
        name_id               str                      Description
        illuminant            Illuminant,              Illuminant
                              IlluminantFromCCT,
                              MeasuredIlluminant
        observer              Observer                 CIE Observer
        coordinates           list, float              Xn, Yn, Zn coordinates

    Methods:
        .to_xyY()
        .to_uvY()
        .plot_xy_white_point(show_figure, save_figure, output_path)

    '''

    __subtype = "WhitePoint XYZ"
    __name_id = None
                
    @property
    def subtype(self):
        return self.__subtype
        
    @property
    def name_id(self):
        return self.__name_id
    
    @name_id.setter
    def name_id(self, name_id):
        self.__name_id = str(name_id)

    def colour_space(self):
        if self.__illuminant_is_CIE__(self.illuminant):
            return "CIE XYZ"
        return "XYZ"

    def __update__(self, name_id, illuminant, observer, coordinates):
        super().__update__(illuminant, observer, coordinates)
        self.name_id = name_id

    def __init__(self, illuminant = "D65", observer = 2):
        self.illuminant = illuminant

        valid_theoretical_wp = ["A", "C", "D50", "D55", "D65", "D75"]
        name_id = f"WhitePoint for illuminant {self.illuminant.illuminant_name} and {observer} º observer"  

        obs = observer.observer if isinstance(observer, Observer) else observer

        if self.illuminant.illuminant_name in valid_theoretical_wp:
            # load theoretical 
            Xn, Yn, Zn = ld.load_cie_white_point(self.illuminant.illuminant_name, obs)
        else:
            #compute Xn,Yn,Zn
            Xn, Yn, Zn = self.illuminant.compute_white_point_XYZ(observer)
        
        self.__update__(name_id, illuminant, observer, [Xn, Yn, Zn])
        
    def to_xyY(self):
        X, Y, Z = self.coordinates
        x, y, Y = csc.XYZ_to_xyY(X, Y, Z)
        return CIExyY(self.name_id, x, y, Y, self.illuminant, self.observer)
    
    def to_uvY(self):
        X, Y, Z = self.coordinates
        u, v, _ = csc.XYZ_to_uvY(X, Y, Z)
        return CIEuvY(self.name_id, u, v, Y, self.illuminant, self.observer)

    def plot_xy_white_point(self, show_figure = True, save_figure = False, output_path = None):
        '''
        Method to create and display the x,y into the CIE 1931 x,y Chromaticity Diagram using Matplotlib.
        
        Parameters:
            show_figure    bool    If True, the plot is shown. Default: True.
            save_figure    bool    If True, the figure is saved at the output_path. Default: False.
            output_path    os      Path for the ouput figure. Default: None.
        
        '''   

        x, y, _ = self.to_xyY().coordinates
        short_name = f"WhitePoint ({self.illuminant.illuminant_name}, {self.observer.observer}º)" 
        sample = {short_name: (x,y)}
        cpt.plot_chromaticity_diagram(sample, show_figure, save_figure, output_path)    

    def __str__(self):
        return f"WhitePoint for {self.illuminant.illuminant_name} illuminant and {self.observer.observer}º observer: Xn={self.coordinates[0]}, Yn={self.coordinates[1]}, Zn={self.coordinates[2]}"

class Illuminant(Spectral, CIE):
    
    ''' 
    Illuminant class.

    The Illuminant class represents a valid CIE standard illuminant defined by their relative spectral power 
    distribution (SPD).

    Parameters:
        cie_illuminant_name   str          CIE illuminant name.
        normalised            bool         If True, the SPD is normalised. Default: False.

    Attributes:
        subtype               str          "CIE Illuminant (SPD)".
        illuminant_name       str          CIE Illuminant name.
        normalised            bool         True for SPD normalised data.
        nm_range              list         lambda nm range [min, max].
        nm_interval           int          lambda nm interval.
        lambda_values         list         SPD data.

    Methods:
        .as_diagonal_array()
        .set_into_visible_range_spectrum(visible_nm_range, visible_nm_interval)
        .normalise_lambda_values()
        .get_theoretical_white_point_XYZ(observer)
        .compute_white_point_XYZ(observer)
        .compute_white_point_xy(observer)
        .compute_white_point_uv_1976(observer)
        .compute_white_point_uv_1960(observer)
        .compute_CCT(method)
        .compute_Duv()
        .plot(show_figure, save_figure, output_path, title)
        .plot_xy_white_point(observer, show_figure, save_figure, output_path)

    '''
    
    __subtype = "CIE Illuminant (SPD)"
    __illuminant_name = None
    __normalised = False
    
    @property
    def subtype(self):
        return self.__subtype

    @property
    def illuminant_name(self):
        return self.__illuminant_name
    
    @illuminant_name.setter
    def illuminant_name(self, illuminant_name):
        if ld.illuminant_is_cie(illuminant_name): 
            self.__illuminant_name = illuminant_name.upper()
            self.__load_cie_illuminant__()
        else:
            raise CIEIlluminantError("The input illuminant name is not a valid CIE standard illuminant.")

    @property
    def normalised(self):
        return self.__normalised
    
    @normalised.setter
    def normalised(self, normalised):
        if isinstance(normalised, bool):
            self.__normalised = normalised
        else:
            raise ClassTypeError("The normalised parameter should be a valid bool type.")

    def __init__(self, cie_illuminant_name, normalised = False):
        self.illuminant_name = cie_illuminant_name
        if normalised:
            self.normalise_lambda_values()
        else:
            self.normalised = normalised

        
    def __load_cie_illuminant__(self):
        cie_illuminant_data = ld.load_cie_illuminant(self.illuminant_name)
        self.__update__(cie_illuminant_data["lambda_nm_range"], cie_illuminant_data["lambda_nm_interval"], cie_illuminant_data["lambda_values"])
    
    def normalise_lambda_values(self):
        '''
        Method to normalise the SPD data of the illuminant

        '''
        if self.__normalised:
            raise CIEIlluminantError("The CIE illuminant implemented is already normalised.")
        
        spd = self.lambda_values
        spd_normalised = list(lo.normalise_spectral_data(spd))
        self.lambda_values = spd_normalised
        self.normalised = True
    
    # theoretical WhitePoint
    def get_theoretical_white_point_XYZ(self, observer = 2):
        '''
        Method to get the theoretical illuminant WhitePoint in CIE XYZ coordinates.

        Parameter:
             observer           str, int    Valid CIE Observer. Default: 2.
                                Observer

        Returns:
            Xn, Yn, Zn          float       Theoretical WhitePoint XYZ.

        Note: Theoretical data are available only for CIE Illuminants: A, C, D50, D55, D65, D75
              Returns None for all remaining illuminants.

        CIE 015:2018. Table 9.1 and 9.2. Colorimetric data for CIE illuminants (p.58).
        https://cie.co.at/publications/colorimetry-4th-edition/

        '''

        valid_white_point = ["A", "C", "D50", "D55", "D65", "D75"] 
        if self.illuminant_name in valid_white_point:
            #obs = observer.observer if isinstance(observer, Observer) else observer
            WP = WhitePoint(self.illuminant_name, observer)
            return WP.coordinates
        return None, None, None

    def compute_white_point_XYZ(self, observer=2):
        '''
        Method to compute the illuminant WhitePoint in CIE XYZ coordinates.

        Note: Compute using the full SPD data (recomeended not to set the SPD into the visible range spectrum).

        Parameter:
             observer           str, int    Valid CIE Observer. Default: 2.
                                Observer

        Returns:
            Xn, Yn, Zn          float       Computed XYZ WhitePoint.

        '''

        # reflectance for the equal energy white
        spc = [100. for value in self.lambda_values] # reflectance [300,830] 5
        spd = self.lambda_values # [300,830] 5
        cmf = CMF(observer) # CMF [380,780], 5
        visible_nm_range = [400,700]
        visible_nm_interval = 10
        if self.nm_range==visible_nm_range and self.nm_interval==visible_nm_interval:
            cmf.set_cmf_into_visible_range_spectrum()

        x_cmf, y_cmf, z_cmf = [x.lambda_values for x in cmf.get_colour_matching_functions()]
        
        # common_range and interval
        common_nm_range = lo.find_common_range([self.nm_range, cmf.nm_range])
        common_nm_interval = cmf.nm_interval # 5nm
        
        # extract common range
        reflectance = lo.extract_nm_range(spc, self.nm_range, common_nm_interval, common_nm_range, common_nm_interval)
        spd = lo.extract_nm_range(spd, self.nm_range, self.nm_interval, common_nm_range, common_nm_interval)
        x_cmf = lo.extract_nm_range(x_cmf, cmf.nm_range, cmf.nm_interval, common_nm_range, common_nm_interval)
        y_cmf = lo.extract_nm_range(y_cmf, cmf.nm_range, cmf.nm_interval, common_nm_range, common_nm_interval)
        z_cmf = lo.extract_nm_range(z_cmf, cmf.nm_range, cmf.nm_interval, common_nm_range, common_nm_interval)
        # compute X,Y,Z
        Xn, Yn, Zn = csc.spectral_to_XYZ(reflectance, spd, x_cmf, y_cmf, z_cmf)
        return Xn, Yn, Zn

    def compute_white_point_xy(self, observer=2):
        '''
        Method to compute the illuminant WhitePoint in CIE xy coordinates.

        Parameter:
            observer        str, int    Valid CIE Observer. Default: 2.
                            Observer

        Returns:
            xn, yn          float       Computed x,y WhitePoint.

        '''

        Xn, Yn, Zn = self.compute_white_point_XYZ(observer)
        x, y, _ = csc.XYZ_to_xyY(Xn, Yn, Zn)
        return x, y 

    def compute_white_point_uv_1976(self, observer=2):
        '''
        Method to compute the illuminant WhitePoint in CIE u'v' coordinates.

        Parameter:
            observer        str, int    Valid CIE Observer. Default: 2.
                            Observer

        Returns:
            un_, vn_        float       Computed u'v' WhitePoint.

        '''

        Xn, Yn, Zn = self.compute_white_point_XYZ(observer)
        un_, vn_, _ = csc.XYZ_to_uvY(Xn, Yn, Zn)
        return un_, vn_

    def compute_white_point_uv_1960(self, observer=2):
        '''
        Method to compute the illuminant WhitePoint in CIE uv coordinates.

        Parameter:
            observer        str, int    Valid CIE Observer. Default: 2.
                            Observer

        Returns:
            un, vn          float       WhitePoint CIE u'v' coordinates.
        
        '''

        Xn, Yn, Zn = self.compute_white_point_XYZ(observer)
        un, vn  = cct.XYZ_to_uv_1960(Xn, Yn, Zn)
        return un, vn

    def compute_CCT(self, method="McCamy"):
        '''
        Method to compute the CCT (º K) from the x,y chromaticity coordinates.

        Methods implmented: "McCamy", "Hernandez", "Ohno".

        Parameter:
            method          str, int    Method. Default: "McCamy".
                            Observer

        Returns:
            cct_K           float       Computed CCT in ºK.
        
        '''
        
        method_implemented = ["McCamy", "Hernandez", "Ohno"]

        if method not in method_implemented:
            raise Exception("Method for the CCT computantion from xy not implemented. Valid methods: {method_implemented}.")

        Xn,Yn,Zn = self.compute_white_point_XYZ()
        x,y,_ = csc.XYZ_to_xyY(Xn,Yn,Zn)

        if method == "McCamy":
            cct_K = cct.xy_to_CCT_McCamy(x,y)
        elif method == "Hernandez": 
            cct_K = cct.xy_to_CCT_Hernandez(x,y)
        elif method == "Ohno":
            cct_K = cct.xy_to_CCT_Ohno(x,y)

        return cct_K

    def compute_Duv(self):
        '''
        Method to compute the Illuminant Duv

        Ohno, Yoshi. 2014. Practical Use and Calculation of CCT and Duv, LEUKOS, 10:1, 47-55 
        https://www.tandfonline.com/doi/abs/10.1080/15502724.2014.839020

        Returns:
            Duv           float       Computed Duv
        
        '''

        Xn,Yn,Zn = self.compute_white_point_XYZ()
        x, y, _ = csc.XYZ_to_xyY(Xn,Yn,Zn)
        u, v = cct.xy_to_uv_1960(x, y)
        Duv = cct.compute_Delta_uv(u,v)
        return Duv

    def plot(self, show_figure = True, save_figure = False, output_path = None):
        '''
        Method to create and display the SPD of the illuminant using Matplotlib.
        
        Parameters:
            show_figure    bool    If True, the plot is shown. Default: True.
            save_figure    bool    If True, the figure is saved at the output_path. Default: False.
            output_path    os      Path for the ouput figure. Default: None.
        
        '''   
        title = "Spectral Power Distribution of a CIE Illuminant"
        illuminant = {self.illuminant_name: (self.nm_range, self.nm_interval, self.lambda_values)}
        cpt.plot_illuminant(illuminant, self.normalised, show_figure, save_figure, output_path)

    def plot_xy_white_point(self, observer=2, show_figure = True, save_figure = False, output_path = None):
        '''
        Method to create and display the x,y WhitePoint into the CIE 1931 x,y Chromaticity Diagram using Matplotlib.
        
        Parameters:
            observer           str, int    Valid CIE Observer. Default: 2.
                                Observer
            show_figure    bool    If True, the plot is shown. Default: True.
            save_figure    bool    If True, the figure is saved at the output_path. Default: False.
            output_path    os      Path for the ouput figure. Default: None.
        
        '''   

        x, y = self.compute_white_point_xy(observer)

        obs = observer if isinstance(observer, int) else observer.observer
        short_name = f"WhitePoint ({self.illuminant_name}, {obs}º)" 
        sample = {short_name: (x,y)}
        cpt.plot_chromaticity_diagram(sample, show_figure, save_figure, output_path)    

    def __str__(self):
        return f"Illuminant object: CIE {self.illuminant_name} standard illuminant"


class IlluminantFromCCT(Spectral):
    ''' 
    IlluminantFromCCT class

    The IlluminantFromCCT class represents a illuminant witch SPD were computed from a valid correlated 
    colour temperature (specified in ºK)

    Parameters:
        cct_k                 float        CCT in ºK
        
    Attributes:
        subtype               str          "SPD Illuminant computed from CCT" 
        illuminant_name       str          Illuminant name
        normalised            bool         True for SPD normalised data.
        nm_range              list         lambda nm range [min, max]
        nm_interval           int          lambda nm interval
        lambda_values         list         SPD data

    Methods:
        .as_diagonal_array()
        .set_into_visible_range_spectrum(visible_nm_range, visible_nm_interval)
        .normalise_lambda_values()
        .compute_white_point_XYZ(observer)
        .compute_white_point_xy(observer)
        .compute_white_point_uv_1976(observer)
        .compute_white_point_uv_1960(observer)
        .compute_Duv()
        .plot(show_figure, save_figure, output_path, title)
        .plot_xy_white_point(observer, show_figure, save_figure, output_path)

    '''

    __subtype = "SPD Illuminant computed from CCT"
    __illuminant_name = None
    __cct_K = None
    __normalised = False

    @property
    def subtype(self):
        return self.__subtype

    @property
    def cct_K(self):
        return self.__cct_K
    
    @cct_K.setter
    def cct_K(self, cct_k):
        self.__cct_K = cct_k
        self.illuminant_name = f"{self.cct_K} ºK"

    @property
    def illuminant_name(self):
        return self.__illuminant_name
    
    @illuminant_name.setter
    def illuminant_name(self, illuminant_name):
        self.__illuminant_name = illuminant_name

    @property
    def normalised(self):
        return self.__normalised
    
    @normalised.setter
    def normalised(self, normalised):
        if isinstance(normalised, bool):
            self.__normalised = normalised
        else:
            raise ClassTypeError("The normalised parameter should be a valid bool type.")

    def __init__(self, cct_K):
        sc = SComponents()
        self.cct_K = cct_K
        
        if 4000 <= cct_K <= 25000:
            nm_range, nm_interval, spd = sc.CCT_to_SPD(cct_K) # CIE D illuminant [300,830] 5
            
        elif 1667 <= cct_K < 4000:
            # I am not sure of this method, I'm just trying 
            xD, yD = cct.compute_xy_from_CCT_cubic_spline_Kim(cct_K)
            M1 = (-1.3515-1.7703*xD+5.9114*yD)/(0.0241+0.2562*xD-0.7341*yD)
            M2 = (0.0300 -31.4424*xD+30.0717*yD)/(0.0241+0.2562*xD-0.7341*yD)
            S0, S1, S2 = sc.S0.lambda_values, sc.S1.lambda_values, sc.S2.lambda_values
            nm_range, nm_interval, spd = lo.compute_SPD_from_xy_and_M_coefficients(xD, yD, M1, M2, S0, S1, S2)
        
        else:
            raise CCTNotInValidRangeError("CCT out of range [4000-25000] ºK.")

        self.__update__(nm_range, nm_interval, spd)
        #self.illuminant_name = f"{self.cct_K} ºK"

    def normalise_lambda_values(self):
        '''
        Method to normalise the SPD data of the illuminant.

        '''

        if self.__normalised:
            raise Exception("The CCT illuminant implemented is already normalised.")
        
        spd = self.lambda_values
        spd_normalised = list(lo.normalise_spectral_data(spd))
        self.lambda_values = spd_normalised
        self.normalised = True

    def compute_white_point_XYZ(self, observer=2):
        '''
        Method to compute the illuminant WhitePoint in CIE XYZ coordinates.

        Parameter:
             observer           str, int    Valid CIE Observer. Default: 2.
                                Observer

        Returns:
            Xn, Yn, Zn          float       Computed XYZ WhitePoint.

        '''

        # reflectance for the equal energy white
        spc = [100. for value in self.lambda_values] # reflectance [300,830] 5
        spd = self.lambda_values # [300,830] 5
        cmf = CMF(observer) # CMF [380,780], 5
        x_cmf, y_cmf, z_cmf = [x.lambda_values for x in cmf.get_colour_matching_functions()]
        
        # common_range and interval
        common_nm_range = lo.find_common_range([self.nm_range, cmf.nm_range])
        common_nm_interval = cmf.nm_interval # 5nm
        
        # extract common range
        reflectance = lo.extract_nm_range(spc, self.nm_range, common_nm_interval, common_nm_range, common_nm_interval)
        spd = lo.extract_nm_range(spd, self.nm_range, self.nm_interval, common_nm_range, common_nm_interval)
        x_cmf = lo.extract_nm_range(x_cmf, cmf.nm_range, cmf.nm_interval, common_nm_range, common_nm_interval)
        y_cmf = lo.extract_nm_range(y_cmf, cmf.nm_range, cmf.nm_interval, common_nm_range, common_nm_interval)
        z_cmf = lo.extract_nm_range(z_cmf, cmf.nm_range, cmf.nm_interval, common_nm_range, common_nm_interval)
        # compute X,Y,Z
        Xn, Yn, Zn = csc.spectral_to_XYZ(reflectance, spd, x_cmf, y_cmf, z_cmf)
        #WP = UserWhitePoint(Xn, Yn, Zn, self.illuminant_name, observer) # circular import error
        return Xn, Yn, Zn #WP # UserWhitePoint

    def compute_white_point_xy(self, observer=2):
        '''
        Method to compute the illuminant WhitePoint in CIE xy coordinates.

        Parameter:
            observer        str, int    Valid CIE Observer. Default: 2.
                            Observer

        Returns:
            xn, yn          float       Computed x,y WhitePoint.

        '''

        Xn, Yn, Zn = self.compute_white_point_XYZ(observer)
        x, y, _ = csc.XYZ_to_xyY(Xn, Yn, Zn)
        return x,y 

    def compute_white_point_uv_1976(self, observer=2):
        '''
        Method to compute the illuminant WhitePoint in CIE u'v' coordinates.

        Parameter:
            observer        str, int    Valid CIE Observer. Default: 2.
                            Observer

        Returns:
            un_, vn_        float       Computed u',v' WhitePoint.

        '''

        Xn, Yn, Zn = self.compute_white_point_XYZ(observer)
        un_, vn_, _ = csc.XYZ_to_uvY(Xn, Yn, Zn)
        return un_, vn_

    def compute_white_point_uv_1960(self, observer=2):
        '''
        Method to compute the illuminant WhitePoint in CIE uv coordinates.

        Parameter:
            observer        str, int    Valid CIE Observer. Default: 2.
                            Observer

        Returns:
            un, vn          float        Computed u'v' WhitePoint.
        
        '''

        Xn, Yn, Zn = self.compute_white_point_XYZ(observer)
        un, vn  = cct.XYZ_to_uv_1960(Xn, Yn, Zn)
        return un, vn

    def compute_Duv(self,observer=2):
        '''
        Method to compute the illuminant Duv

        Ohno, Yoshi. 2014. Practical Use and Calculation of CCT and Duv, LEUKOS, 10:1, 47-55 
        https://www.tandfonline.com/doi/abs/10.1080/15502724.2014.839020

        Returns:
            Duv           float       Computed Duv
        
        '''

        Xn,Yn,Zn = self.compute_white_point_XYZ(observer)
        x, y, _ = csc.XYZ_to_xyY(Xn,Yn,Zn)
        u, v = cct.xy_to_uv_1960(x, y)
        Duv = cct.compute_Delta_uv(u,v)
        return Duv

    def plot(self, show_figure = True, save_figure = False, output_path = None):
        '''
        Method to create and display the SPD of the illuminant using Matplotlib.
        
        Parameters:
            show_figure    bool    If True, the plot is shown. Default: True.
            save_figure    bool    If True, the figure is saved at the output_path. Default: False.
            output_path    os      Path for the ouput figure. Default: None.
        
        '''   

        title = "SPD of the Illuminant computed from a CCT"
        illuminant = {self.illuminant_name: (self.nm_range, self.nm_interval, self.lambda_values)}
        cpt.plot_illuminant(illuminant, self.normalised, show_figure, save_figure, output_path, title)

    def plot_xy_white_point(self, observer=2, show_figure = True, save_figure = False, output_path = None):
        '''
        Method to create and display the x,y WhitePoint into the CIE 1931 x,y Chromaticity Diagram using Matplotlib.
        
        Parameters:
            observer           str, int    Valid CIE Observer. Default: 2.
                                Observer
            show_figure    bool    If True, the plot is shown. Default: True.
            save_figure    bool    If True, the figure is saved at the output_path. Default: False.
            output_path    os      Path for the ouput figure. Default: None.
        
        '''   

        x, y = self.compute_white_point_xy(observer)

        obs = observer if isinstance(observer, int) else observer.observer
        short_name = f"WhitePoint ({self.illuminant_name}, {obs}º)" 
        sample = {short_name: (x,y)}
        cpt.plot_chromaticity_diagram(sample, show_figure, save_figure, output_path)    

    def __str__(self):
        return f"IlluminantFromCCT object: CCT {self.cct_K} º K"

class MeasuredIlluminant(Spectral): 
    ''' 
    MeasuredIlluminant class.

    The MeasuredIlluminant class represents a illuminant witch SPD has been measured using specific 
    instrumental.

    Parameters:
        illuminant_name       str          Illuminant name or description.
        data                  dict         Measured data as dict. Default: None.
                                           Required keys: nm_range, nm_interval, lambda_values .
        path_file             os           CSV for Sekonic. JSON for any instrument. Default: None.
                                           Required keys: nm_range, nm_interval, lambda_values.
        metadata              dict         Instrument measurement information as dict. Default: {}.
        normalised            bool         If True, the SPD is normalised. Default: False.

    Atributes:
        subtype               str          "Measured SPD Illuminant".
        illuminant_name       str          Illuminant name.
        nm_range              list         lambda nm range [min, max].
        nm_interval           int          lambda nm interval.
        lambda_values         list         SPD data.
        normalised            bool         True for SPD normalised data.
        measured_data         dict         Illuminant data provided by the instrument.
        metadata              dict         Information about measurement conditions.

    Methods:
        .set_instrument_measurement_as_metadata(metadata)
        .as_diagonal_array()
        .set_into_visible_range_spectrum(visible_nm_range, visible_nm_interval)
        .normalise_lambda_values()
        .get_theoretical_white_point_XYZ(observer)
        .compute_white_point_XYZ(observer)
        .compute_white_point_xy(observer)
        .compute_white_point_uv_1976(observer)
        .compute_white_point_uv_1960(observer)
        .compute_CCT(method)
        .compute_Duv()
        .plot(show_figure, save_figure, output_path, title)
        .plot_xy_white_point(observer, show_figure, save_figure, output_path)

    '''

    __subtype = "Measured SPD Illuminant"
    __illuminant_name = None
    __measured_data = None
    __metadata = None
    __normalised = False

    @property
    def subtype(self):
        return self.__subtype

    @property
    def illuminant_name(self):
        return self.__illuminant_name
    
    @illuminant_name.setter
    def illuminant_name(self, illuminant_name):
        self.__illuminant_name = str(illuminant_name)

    @property
    def measured_data(self):
        return self.__measured_data

    @measured_data.setter
    def measured_data(self, measured_data):
        self.__measured_data = measured_data

    @property
    def metadata(self):
        return self.__metadata
    
    @metadata.setter
    def metadata(self, metadata):
        self.__metadata = metadata

    def set_instrument_measurement_as_metadata(self, metadata):
        self.metadata = metadata

    @property
    def normalised(self):
        return self.__normalised
    
    @normalised.setter
    def normalised(self, normalised):
        if isinstance(normalised, bool):
            self.__normalised = normalised
        else:
            raise ClassTypeError("The normalised parameter should be a valid bool type.")

    def __update_from_json__(self, path_json):
        self.measured_data = ld.load_spd_from_json(path_json)
        self.__update_from_dict__(self.measured_data)

    def __update_from_dict__(self, data_as_dict):
        self.measured_data = data_as_dict
        if ld.is_valid_spd_data_dict(data_as_dict):
            nm_range = data_as_dict["nm_range"]
            nm_interval = data_as_dict["nm_interval"]
            spd_lambda_values = data_as_dict["lambda_values"]
            self.__update__(nm_range, nm_interval, spd_lambda_values)
        else:
            raise DictLabelError("Error in the dict or file with measurement data: Incomplete data or wrong labels.")

    def __update_from_sekonic_csv__(self, path_csv_sekonic):
        self.measured_data = ld.load_metadata_sekonic_from_csv(path_csv_sekonic)
        nm_range = self.measured_data["nm_range"]
        spd_lambda_values = self.measured_data["lambda_values_5nm"]
        nm_interval = (nm_range[1]-nm_range[0])/(len(spd_lambda_values)-1)
        self.__update__(nm_range, nm_interval, spd_lambda_values)

    def __init__(self, illuminant_name, data = None, path_file = None, metadata = {}, normalised = False):
        self.illuminant_name = illuminant_name
        self.metadata = metadata
        # update
        if data!= None:
            self.__update_from_dict__(data)
        elif path_file!=None:
            # get extension
            file_extension = cop.get_file_extension(path_file)
            if file_extension=="csv":
                self.__update_from_sekonic_csv__(path_file)
            elif file_extension=="json":
                self.__update_from_json__(path_file)
            else:
                raise FileExtensionError("Type file not allowed: Only data from CSV or JSON files can be uploaded.")
        else:
            raise Exception("The class cannot be instantiated. Please check the input parameters.")

        self.normalised = normalised

    def normalise_lambda_values(self):
        '''
        Method to normalise the SPD data of the illuminant.

        '''

        if self.__normalised:
            raise Exception("The CCT illuminant implemented is already normalised.")
        
        spd = self.lambda_values
        spd_normalised = list(lo.normalise_spectral_data(spd))
        self.lambda_values = spd_normalised
        self.normalised = True

    def compute_white_point_XYZ(self, observer=2):
        '''
        Method to compute the illuminant WhitePoint in CIE XYZ coordinates.

        Parameter:
             observer           str, int    Valid CIE Observer. Default: 2.
                                Observer

        Returns:
            Xn, Yn, Zn          float       Computed XYZ WhitePoint.

        '''

        # reflectance for the equal energy white
        spc = [100. for value in self.lambda_values] # reflectance [300,830] 5
        spd = self.lambda_values # [300,830] 5
        cmf = CMF(observer) # CMF [380,780], 5
        x_cmf, y_cmf, z_cmf = [x.lambda_values for x in cmf.get_colour_matching_functions()]
        
        # common_range and interval
        common_nm_range = lo.find_common_range([self.nm_range, cmf.nm_range])
        common_nm_interval = cmf.nm_interval # 5nm
        
        # extract common range
        reflectance = lo.extract_nm_range(spc, self.nm_range, common_nm_interval, common_nm_range, common_nm_interval)
        spd = lo.extract_nm_range(spd, self.nm_range, self.nm_interval, common_nm_range, common_nm_interval)
        x_cmf = lo.extract_nm_range(x_cmf, cmf.nm_range, cmf.nm_interval, common_nm_range, common_nm_interval)
        y_cmf = lo.extract_nm_range(y_cmf, cmf.nm_range, cmf.nm_interval, common_nm_range, common_nm_interval)
        z_cmf = lo.extract_nm_range(z_cmf, cmf.nm_range, cmf.nm_interval, common_nm_range, common_nm_interval)
        # compute X,Y,Z
        Xn, Yn, Zn = csc.spectral_to_XYZ(reflectance, spd, x_cmf, y_cmf, z_cmf)
        #WP = UserWhitePoint(Xn, Yn, Zn, self.illuminant_name, observer) # circular import error
        return Xn, Yn, Zn #WP # UserWhitePoint

    def compute_white_point_xy(self, observer=2):
        '''
        Method to compute the illuminant WhitePoint in CIE xy coordinates.

        Parameter:
            observer        str, int    Valid CIE Observer. Default: 2.
                            Observer

        Returns:
            xn, yn          float       Computed x,y WhitePoint.

        '''

        Xn, Yn, Zn = self.compute_white_point_XYZ(observer)
        x, y, _ = csc.XYZ_to_xyY(Xn, Yn, Zn)
        return x,y 

    def compute_white_point_uv_1976(self, observer=2):
        '''
        Method to compute the illuminant WhitePoint in CIE u'v' coordinates.

        Parameter:
            observer        str, int    Valid CIE Observer. Default: 2.
                            Observer

        Returns:
            un_, vn_        float       Computed u'v' WhitePoint.

        '''

        Xn, Yn, Zn = self.compute_white_point_XYZ(observer)
        un_, vn_, _ = csc.XYZ_to_uvY(Xn, Yn, Zn)
        return un_, vn_

    def compute_white_point_uv_1960(self, observer=2):
        '''
        Method to compute the illuminant WhitePoint in CIE uv coordinates.

        Parameter:
            observer        str, int    Valid CIE Observer. Default: 2.
                            Observer

        Returns:
            un, vn          float       Computed u'v' WhitePoint.
        
        '''

        Xn, Yn, Zn = self.compute_white_point_XYZ(observer)
        un, vn  = cct.XYZ_to_uv_1960(Xn, Yn, Zn)
        return un, vn

    def compute_CCT(self, method="McCamy"):
        '''
        Method to compute the CCT (º K) from the x,y chromaticity coordinates.

        Methods implmented: "McCamy", "Hernandez", "Ohno".

        Parameter:
            method          str, int    Method. Default: "McCamy".
                            Observer

        Returns:
            cct_K           float       Computed CCT in ºK.
        
        '''
        
        method_implemented = ["McCamy", "Hernandez", "Ohno"]

        if method not in method_implemented:
            raise Exception("Method for the CCT computantion from xy not implemented. Valid methods: {method_implemented}.")

        Xn,Yn,Zn = self.compute_white_point_XYZ()
        x,y,_ = csc.XYZ_to_xyY(Xn,Yn,Zn)

        if method == "McCamy":
            cct_K = cct.xy_to_CCT_McCamy(x,y)
        elif method == "Hernandez": 
            cct_K = cct.xy_to_CCT_Hernandez(x,y)
        elif method == "Ohno":
            cct_K = cct.xy_to_CCT_Ohno(x,y)

        return cct_K

    def compute_Duv(self):
        '''
        Method to compute the Illuminant Duv

        Ohno, Yoshi. 2014. Practical Use and Calculation of CCT and Duv, LEUKOS, 10:1, 47-55 
        https://www.tandfonline.com/doi/abs/10.1080/15502724.2014.839020

        Returns:
            Duv           float       Computed Duv
        
        '''

        Xn,Yn,Zn = self.compute_white_point_XYZ()
        x, y, _ = csc.XYZ_to_xyY(Xn,Yn,Zn)
        u, v = cct.xy_to_uv_1960(x, y)
        Duv = cct.compute_Delta_uv(u,v)
        return Duv

    def plot_xy_white_point(self, observer=2, show_figure = True, save_figure = False, output_path = None):
        '''
        Method to create and display the x,y WhitePoint into the CIE 1931 x,y Chromaticity Diagram using Matplotlib.

        Parameters:
            observer           str, int    Valid CIE Observer. Default: 2.
                                Observer
            show_figure    bool    If True, the plot is shown. Default: True.
            save_figure    bool    If True, the figure is saved at the output_path. Default: False.
            output_path    os      Path for the ouput figure. Default: None.
        
        '''   

        x, y = self.compute_white_point_xy(observer)

        obs = observer if isinstance(observer, int) else observer.observer
        short_name = f"WhitePoint ({self.illuminant_name}, {obs}º)" 
        sample = {short_name: (x,y)}
        cpt.plot_chromaticity_diagram(sample, show_figure, save_figure, output_path)    

    def plot(self, show_figure = True, save_figure = False, output_path = None):
        '''
        Method to create and display the SPD of the illuminant using Matplotlib.
        
        Parameters:
            show_figure    bool    If True, the plot is shown. Default: True.
            save_figure    bool    If True, the figure is saved at the output_path. Default: False.
            output_path    os      Path for the ouput figure. Default: None.
        
        '''   

        title = "SPD of a Measured Illuminant"
        illuminant = {self.illuminant_name: (self.nm_range, self.nm_interval, self.lambda_values)}
        cpt.plot_illuminant(illuminant, self.normalised, show_figure, save_figure, output_path, title)

    def __str__(self):
        return f"MeasuredIlluminant object: Illuminant {self.illuminant_name}."

class SpectralColour(Spectral, CIE):
    ''' 
    SpectralColour class
    
    The SpectralColour class represents a colour sample defined by its spectral data referred to a CIE illuminant.

    Parameters:
        name_id               str                    description
        nm_range              list                   lambda range [min, max] in nm 
        nm_interval           int                    lambda interval in nm 
        lambda_values         list                   lambda values in the nm_range and nm_interval 
        illuminant            str, Illuminant        CIE Illuminant name or Illuminant instance
        observer              str, int, Observer     Instance Observer class / valid str or int

    Attributes:
        subtype               str                    "Spectral colour data referred to a CIE illuminant" 
        name_id               str                    Sample ID
        illuminant_name       str                    CIE Illuminant name
        observer              Observer               CIE Observer
        nm_range              list                   lambda nm range [min, max]
        nm_interval           int                    lambda nm interval
        lambda_values         list                   spectral data
        scaled                bool                   If True, spectral data in range (0,1)

    Methods:
        .as_diagonal_array()
        .scale_lambda_values()
        .to_XYZ(visible)
        .plot(show_figure, save_figure, output_path)

    '''

    __subtype = "Spectral colour data referred to a CIE illuminant"
    __name_id = None
    __illuminant = None # Illuminant / str
    __observer = None
    __scaled = False # Yo lo quitaria, para evitar confusion
    
    @property
    def subtype(self):
        return self.__subtype

    @subtype.setter
    def subtype(self, subtype):
        self.__subtype = subtype

    @property
    def name_id(self):
        return self.__name_id
    
    @name_id.setter
    def name_id(self, name_id):
        self.__name_id = name_id
    
    @property
    def illuminant(self):
        return self.__illuminant

    @illuminant.setter
    def illuminant(self, illuminant):
        if isinstance(illuminant, Illuminant):
            self.__illuminant = illuminant
        elif isinstance(illuminant, str):
            if ld.illuminant_is_cie(illuminant):
                self.__illuminant = Illuminant(illuminant)
            else:
                raise CIEIlluminantError("The input illuminant is not a valid CIE standard illuminant.")

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
    def scaled(self):
        return self.__scaled
    
    @scaled.setter
    def scaled(self, scaled):
        if isinstance(scaled,bool):
            self.__scaled = scaled

    def __init__(self, name_id, nm_range, nm_interval, lambda_values, illuminant="D65", observer=2):
        
        lambda_values = lo.scale_reflectance(lambda_values) # some instruments in range [0-1] --> scale [0-100]
        
        super().__update__(nm_range, nm_interval, lambda_values)        
        self.name_id = name_id
        self.illuminant = illuminant
        self.observer = observer
        
    def scale_lambda_values(self):
        '''
        Method to scale the spectral data into the range (0, 1).
        
        '''

        lambda_values = np.array(self.lambda_values)/100. # range [0,1]
        self.lambda_values = list(lambda_values) # update
        self.scaled = True

    def to_XYZ(self, visible = False):
        '''
        Method to obtain the CIE XYZ tristimulus values from spectral data.

        Parameter:
            visible    bool      If True, use only the visible spectrum data. Default: False
        
        Returns:
            XYZ        CIEXYZ    Computed tristimulus values as CIEXYZ object.

        '''    

        X, Y, Z = self.__to_XYZ_visible__() if visible else self.__to_XYZ__()
        #XYZ = CIEXYZ(self.name_id, X,Y,Z, self.illuminant.illuminant_name, self.observer)
        #return XYZ
        return X, Y, Z

    def __to_XYZ_visible__(self):
        visible_nm_range = [400, 700]
        visible_nm_interval = 10

        reflectance_nm_range = self.nm_range
        reflectance_nm_interval = self.nm_interval
        reflectance = self.lambda_values
        
        if lo.range_is_valid(reflectance_nm_range, reflectance_nm_interval, visible_nm_range, visible_nm_interval):
            reflectance_visible = lo.extract_nm_range(reflectance, reflectance_nm_range, reflectance_nm_interval, visible_nm_range, visible_nm_interval)
        
        cmf = CMF(self.observer)
        cmf.set_cmf_into_visible_range_spectrum(visible_nm_range, visible_nm_interval)
        cmf_x, cmf_y, cmf_z = cmf.get_colour_matching_functions()
        
        spd = self.illuminant.get_visible_lambda_values(self.illuminant.nm_range, self.illuminant.nm_interval, self.illuminant.lambda_values, visible_nm_range, visible_nm_interval)
                
        X, Y, Z = csc.spectral_to_XYZ(reflectance_visible, spd, cmf_x.lambda_values, cmf_y.lambda_values, cmf_z.lambda_values)
        
        return X, Y, Z

    def __to_XYZ__(self):
        spc = self.lambda_values  # reflectance [360,740], 10
        spd = self.illuminant.lambda_values # spd [300,780], [380,780], 5
        cmf = CMF(self.observer) # CMF [380,780], 5
        x_cmf, y_cmf, z_cmf = [x.lambda_values for x in cmf.get_colour_matching_functions()]
        # common_range and interval
        common_nm_range = lo.find_common_range([self.nm_range, self.illuminant.nm_range, cmf.nm_range])
        common_nm_interval = cmf.nm_interval # 5nm
        
        # reflectance interpolate data 5nm
        spc = self.get_lambda_values_interpolate(self.nm_range, self.nm_interval, spc, self.nm_range, common_nm_interval, method="Akima")
        
        # extract common range
        reflectance = lo.extract_nm_range(spc, self.nm_range, common_nm_interval, common_nm_range, common_nm_interval)
        spd = lo.extract_nm_range(spd, self.illuminant.nm_range, self.illuminant.nm_interval, common_nm_range, common_nm_interval)
        x_cmf = lo.extract_nm_range(x_cmf, cmf.nm_range, cmf.nm_interval, common_nm_range, common_nm_interval)
        y_cmf = lo.extract_nm_range(y_cmf, cmf.nm_range, cmf.nm_interval, common_nm_range, common_nm_interval)
        z_cmf = lo.extract_nm_range(z_cmf, cmf.nm_range, cmf.nm_interval, common_nm_range, common_nm_interval)
        # compute X,Y,Z
        X, Y, Z = csc.spectral_to_XYZ(reflectance, spd, x_cmf, y_cmf, z_cmf)
        return X, Y, Z

    def plot(self, show_figure = True, save_figure = False, output_path = None):
        '''
        Method to create and display the spectral data of a colour sample using Matplotlib.
        
        Parameters:
            show_figure    bool    If True, the plot is shown. Default: True.
            save_figure    bool    If True, the figure is saved at the output_path. Default: False.
            output_path    os      Path for the ouput figure. Default: None.
        
        '''   

        title = "Spectral Colour Data"
        sample = {self.name_id: (self.nm_range, self.nm_interval, self.lambda_values)}
        cpt.plot_spectral(sample, show_figure, save_figure, output_path, title)

    def __str__(self):
        return f"SpectralColour object: {self.name_id}"

class Reflectance(Spectral):
    ''' 
    Reflectance class
    
    The Reflectance class represents a colour sample defined by its spectral data measured by a spectrophotometer and referred to a given illuminant

    Parameters:
        name_id          str                    description
        nm_range         list [max, min]        lambda range in nm 
        nm_interval      int                    lambda interval in nm 
        lambda_values    list                   lambda values in the nm_range and nm_interval 
        illuminant       Illuminant, str        CIE Illuminant object or name CIE illuminant as str; Measured illuminant
                         MeasuredIlluminant         
        observer         Observer, str, int    Instance Observer class; valid str or int

    Attributes:
        subtype               str                    "Reflectance data of a colour sample" 
        name_id               str                    Sample ID
        metadata              dic                    Measurement information
        illuminant            Illuminant,            Illuminant
                              IlluminantFromCCT,
                              MeasuredIlluminant
        observer              Observer               CIE Observer
        nm_range              list                   lambda nm range [min, max]
        nm_interval           int                    lambda nm interval
        lambda_values         list                   spectral data
        scaled                bool                   True for spectral data in range (0,1)
        metadata              dict                   Measurement details as dict

    Methods:
        .as_diagonal_array()
        .scale_lambda_values()
        .to_XYZ(visible)
        .plot(show_figure, save_figure, output_path)

    '''

    __subtype = "Reflectance data of a colour sample"
    __name_id = None
    __metadata = None 
    __illuminant = None # Illuminant / str
    __observer = None
    __scaled = False
    
    @property
    def subtype(self):
        return self.__subtype
    
    @property
    def name_id(self):
        return self.__name_id
    
    @name_id.setter
    def name_id(self, name_id):
        self.__name_id = name_id

    @property
    def metadata(self):
        return self.__metadata
    
    @metadata.setter
    def metadata(self, metadata):
        self.__metadata = metadata

    def set_instrument_measurement_as_metadata(self, metadata):
        self.metadata = metadata

    @property
    def illuminant(self):
        return self.__illuminant

    @illuminant.setter
    def illuminant(self, illuminant):
        if isinstance(illuminant, str):
            if ld.illuminant_is_cie(illuminant):
                self.__illuminant = Illuminant(illuminant)
            else:
                raise CIEIlluminantError("The input illuminant is not a valid CIE standard illuminant.")
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
    def scaled(self):
        return self.__scaled
    
    @scaled.setter
    def scaled(self, scaled):
        if isinstance(scaled,bool):
            self.__scaled = scaled

    def __init__(self, name_id, nm_range, nm_interval, lambda_values, illuminant="D65", observer=2, metadata={}):
        super().__update__(nm_range, nm_interval, lambda_values)        
        self.name_id = name_id
        self.illuminant = illuminant
        self.observer = observer
        self.metadata = metadata
        
    def scale_lambda_values(self):
        '''
        Method to scale the reflectance data into the range [0-1]

        For some practical computations
        
        '''
        lambda_values = np.array(self.lambda_values)/100. # range [0,1]
        self.lambda_values = list(lambda_values) # update
        self.scaled = True
    
    def to_XYZ(self, visible = False):     
        '''
        Method to obtain the XYZ tristimulus values from reflectance data

        Parameter:
            visible    bool      If True, use only the visible spectrum data
        
        Returns:
            XYZ        float    Computed tristimulus values

        '''    

        X, Y, Z = self.__to_XYZ_visible__() if visible else self.__to_XYZ__()
        return X, Y, Z

    def __to_XYZ_visible__(self):
        visible_nm_range = [400, 700]
        visible_nm_interval = 10

        reflectance_nm_range = self.nm_range
        reflectance_nm_interval = self.nm_interval
        reflectance = self.lambda_values
        
        if lo.range_is_valid(reflectance_nm_range, reflectance_nm_interval, visible_nm_range, visible_nm_interval):
            reflectance_visible = lo.extract_nm_range(reflectance, reflectance_nm_range, reflectance_nm_interval, visible_nm_range, visible_nm_interval)
        
        cmf = CMF(self.observer)
        cmf.set_cmf_into_visible_range_spectrum(visible_nm_range, visible_nm_interval)
        cmf_x, cmf_y, cmf_z = cmf.get_colour_matching_functions()
        
        spd = self.illuminant.get_visible_lambda_values(self.illuminant.nm_range, self.illuminant.nm_interval, self.illuminant.lambda_values, visible_nm_range, visible_nm_interval)
                
        X, Y, Z = csc.spectral_to_XYZ(reflectance_visible, spd, cmf_x.lambda_values, cmf_y.lambda_values, cmf_z.lambda_values)
        
        return X, Y, Z

    def __to_XYZ__(self):
        spc = self.lambda_values  # reflectance [360,740], 10
        spd = self.illuminant.lambda_values # spd [300,780], [380,780], 5
        cmf = CMF(self.observer) # CMF [380,780], 5
        x_cmf, y_cmf, z_cmf = [x.lambda_values for x in cmf.get_colour_matching_functions()]
        # common_range and interval
        common_nm_range = lo.find_common_range([self.nm_range, self.illuminant.nm_range, cmf.nm_range])
        common_nm_interval = cmf.nm_interval # 5nm
        
        # reflectance interpolate data 5nm
        spc = self.get_lambda_values_interpolate(self.nm_range, self.nm_interval, spc, self.nm_range, common_nm_interval, method="Akima")
        
        # extract common range
        reflectance = lo.extract_nm_range(spc, self.nm_range, common_nm_interval, common_nm_range, common_nm_interval)
        spd = lo.extract_nm_range(spd, self.illuminant.nm_range, self.illuminant.nm_interval, common_nm_range, common_nm_interval)
        x_cmf = lo.extract_nm_range(x_cmf, cmf.nm_range, cmf.nm_interval, common_nm_range, common_nm_interval)
        y_cmf = lo.extract_nm_range(y_cmf, cmf.nm_range, cmf.nm_interval, common_nm_range, common_nm_interval)
        z_cmf = lo.extract_nm_range(z_cmf, cmf.nm_range, cmf.nm_interval, common_nm_range, common_nm_interval)
        # compute X,Y,Z
        X, Y, Z = csc.spectral_to_XYZ(reflectance, spd, x_cmf, y_cmf, z_cmf)
        return X, Y, Z

    def plot(self, show_figure = True, save_figure = False, output_path = None):
        '''
        Method to create and display the reflectance data of a colour sample.
        
        Parameters:
            show_figure    bool    If True, the plot is shown. Default: True.
            save_figure    bool    If True, the figure is saved at the output_path. Default: False.
            output_path    os      Path for the ouput figure. Default: None.
        
        '''   

        sample = {self.name_id: (self.nm_range, self.nm_interval, self.lambda_values)}
        cpt.plot_spectral(sample, show_figure, save_figure, output_path)

    def __str__(self):
        return f"Reflectance object: {self.name_id}"
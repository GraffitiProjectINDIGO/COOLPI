from matplotlib import pyplot as plt        
from matplotlib.patches import Circle, Rectangle
from matplotlib.pylab import hist
import numpy as np
import seaborn as sns

from coolpi.auxiliary.errors import PlotIlluminantError
import coolpi.colour.colour_space_conversion as csc
import coolpi.colour.lambda_operations as lo
import coolpi.image.raw_operations as rwo

def plot_spectral(samples, show_figure = True, save_figure = False, output_path = None, title = "Spectral Reflectance Data"):
    '''
    Function to plot the spectral data of a set of samples using matplotlib

    Parameters:
        samples        dict    samples data as dict
                               samples = {sample_id:[lambda_nm_range, lambda_nm_interval, lambda_values]}
        show_figure    bool    If True, the figure is shown. Default False.
        save_figure    bool    If True, the figure is saved at the output_path. Default False
        output_path    path    Path to save the figure. Default None
        title          str     Matplotlib title. Default "Spectral reflectance data"

    '''
    size_font_title = 12
    size_font_ticks = 10
    
    fig = plt.figure(figsize=(8,8))
    ax1 = fig.add_subplot(111)
    ax1.set_title(title, fontsize = size_font_title)

    max_lambda_value = 0 
    for (key,value) in samples.items():
        nm_ini = value[0][0]
        nm_end = value[0][1]
        nm_interval = value[1]
        wavelength = lo.create_wavelength_space(nm_ini, nm_end, nm_interval)
        lambda_values = np.array(value[2])
        max_lambda_value = max(lambda_values) if max(lambda_values)>max_lambda_value else max_lambda_value
        plt.plot(wavelength, lambda_values, label = key)

    ax1.set_ylim(0, max_lambda_value*1.05)
    ax1.set_xlim(nm_ini, nm_end)

    plt.xlabel("wavelength λ (nm)")
    plt.ylabel("reflectance factor")
    
    if len(samples.keys())<10:
        plt.legend(loc='best', shadow = True , fontsize = size_font_ticks) 

    if save_figure:
        plt.savefig(output_path, dpi = 300, transparent = False)   
            
    if show_figure:
        plt.show()
    
    plt.close()

def plot_illuminant(illuminants, normalised = False, show_figure = True, save_figure = False, output_path = None, title = "Spectral Power Distribution of the Illuminant"):
    '''
    Function to plot the SPD of a set of illuminants using matplotlib

    Parameters:
        illuminants    dict    illuminants data as dict (maximum 5 sample illuminants)
                               illuminants = {"name_illuminant": (nm_range, nm_interval, lambda_values)}
        normalised     bool    To set the ylabel as "relative spectral power". Default False
        show_figure    bool    If True, the figure is shown. Default False.
        save_figure    bool    If True, the figure is saved at the output_path. Default False
        output_path    path    Path to save the figure. Default None
        title          str     Matplotlib title. Default: "Spectral Power Distribution of Illuminant"

    '''

    if len(illuminants.keys())>5:
        raise PlotIlluminantError("Too many illuminants to plot: the maximun illuminants allowed to compare is 5")

    size_font_title = 12
    size_font_ticks = 10
    
    fig = plt.figure(figsize=(8,8))
    ax1 = fig.add_subplot(111)
    ax1.set_title(title, fontsize = size_font_title)
    
    max_lambda_value = 0 
    for key, value in illuminants.items():
        nm_ini = value[0][0]
        nm_end = value[0][1]
        nm_interval = value[1]
        wavelength = lo.create_wavelength_space(nm_ini, nm_end, nm_interval)
        lambda_values = np.array(value[2])
        max_lambda_value = max(lambda_values) if max(lambda_values)>max_lambda_value else max_lambda_value
        plt.plot(wavelength, lambda_values, label = key)

    ax1.set_ylim(0, max(lambda_values)*1.05)
    ax1.set_xlim(nm_ini, nm_end)

    if normalised:
        plt.ylabel("relative value")
    else:
        plt.ylabel("spectral power")
    plt.xlabel("wavelength λ (nm)")
    plt.legend(loc='best', shadow = True , fontsize = size_font_ticks) # best
    
    if save_figure:
        plt.savefig(output_path, dpi = 300, transparent = False)  # save before show / on the contrary, empty fig
    
    if show_figure:
        plt.show()

    plt.close()

def plot_cmf(cmf_range, cmf_interval, x_cmf, y_cmf, z_cmf, observer = 2, show_figure = True, save_figure = False, output_path = None):
    '''
    Function to plot the CMF using matplotlib

    Parameters:
        cmf_range       list    cmf lambda range
        cmf_interval    list    cmf lambda interval
        x_cmf           list    x-cmf lambda data
        y_cmf           list    y-cmf lambda data
        z_cmf           list    z-cmf lambda data
        observer        int     CIE standard observer (2 or 10). Default 2
        show_figure     bool    If True, the figure is shown. Default False.
        save_figure     bool    If True, the figure is saved at the output_path. Default False
        output_path     path    Path to save the figure. Default None

    '''

    opt2 = "CMFs for the 2º standard observer (CIE 1931)"
    opt10 = "CMFs for the 10º standard observer (CIE 1964)"

    title = opt2 if observer == 2 else opt10
    
    nm_ini, nm_end  = cmf_range[0], cmf_range[1]
    wavelength = lo.create_wavelength_space(nm_ini, nm_end, cmf_interval)

    size_font_title = 12
    size_font_ticks = 10

    fig = plt.figure(figsize=(8,8))
    ax1 = fig.add_subplot(111)
    ax1.set_title(title, fontsize = size_font_title)
    ax1.set_ylim(min([min(x_cmf), min(y_cmf), min(z_cmf)]), max([max(x_cmf), max(y_cmf), max(z_cmf)])*1.05)
    ax1.set_xlim(nm_ini, nm_end)
    plt.plot(wavelength, x_cmf, "r", label = "x_cmf")
    plt.plot(wavelength, y_cmf, "g", label = "y_cmf")
    plt.plot(wavelength, z_cmf, "b", label = "z_cmf")
    plt.xlabel("wavelength λ (nm)")
    plt.ylabel("spectral sensitivity")
    plt.legend(loc='best', shadow = True , fontsize = size_font_ticks) 

    if save_figure:
        plt.savefig(output_path, dpi = 300, transparent = False)   
            
    if show_figure:
        plt.show()

    plt.close()

def plot_s_components(s_range, s_interval, S0, S1, S2, show_figure = True, save_figure = False, output_path = None):
    '''
    Function to plot the S components using matplotlib

    Parameters:
        s_range       list    S components lambda range
        s_interval    list    S components lambda interval
        S0            list    S0 lambda data
        S1            list    S1 lambda data
        S2            list    S2 lambda data
        show_figure     bool    If True, the figure is shown. Default False.
        save_figure     bool    If True, the figure is saved at the output_path. Default False
        output_path     path    Path to save the figure. Default None

    '''

    title = "CIE S components for the SPD computation from the CCT"

    nm_ini, nm_end  = s_range[0], s_range[1]
    wavelength = lo.create_wavelength_space(nm_ini, nm_end, s_interval)

    size_font_title = 12
    size_font_ticks = 10
    
    fig = plt.figure(figsize=(8,8))
    ax1 = fig.add_subplot(111)
    ax1.set_title(title, fontsize = size_font_title)
    ax1.set_ylim(min([min(S0), min(S1), min(S2)]), max([max(S0), max(S1), max(S2)])*1.05)
    ax1.set_xlim(nm_ini, nm_end)
    plt.plot(wavelength, S0, "r", label = "S0")
    plt.plot(wavelength, S1, "g", label = "S1")
    plt.plot(wavelength, S2, "b", label = "S2")
    plt.xlabel("wavelength λ (nm)")
    plt.ylabel("spectral sensitivity")
    plt.legend(loc='best', shadow = True , fontsize = size_font_ticks) 

    if save_figure:
        plt.savefig(output_path, dpi = 300, transparent = False)   
            
    if show_figure:
        plt.show()
    
    plt.close()
    
def plot_rgbcmf(rgbcmf_range, rgbcmf_interval, r_cmf, g_cmf, b_cmf, observer = 2, show_figure = True, save_figure = False, output_path = None):
    '''
    Function to plot the RGB CMF using matplotlib

    Parameters:
        rgbcmf_range       list    rgb-cmf lambda range
        rgbcmf_interval    list    rgb-cmf lambda interval
        r_cmf              list    r-cmf lambda data
        g_cmf              list    g-cmf lambda data
        b_cmf              list    b-cmf lambda data
        observer           int     CIE standard observer (2 or 10). Default 2
        show_figure        bool    If True, the figure is shown. Default False.
        save_figure        bool    If True, the figure is saved at the output_path. Default False
        output_path        path    Path to save the figure. Default None
    '''

    opt2 = "RGB CMFs for the 2º standard observer (CIE 1931)"
    opt10 = "RGB CMFs for the 10º standard observer (CIE 1964)"


    title = opt2 if observer == 2 else opt10
    units_x = "wavelength λ (nm)" if observer == 2 else "wavelength λ (v/cm-1)"
    
    nm_ini, nm_end  = rgbcmf_range[0], rgbcmf_range[1]
    
    if observer==2:
        wavelength = lo.create_wavelength_space(nm_ini, nm_end, rgbcmf_interval)
    else:
        wavelength = lo.create_wavelength_space(nm_ini, nm_end, rgbcmf_interval)

    size_font_title = 12
    size_font_ticks = 10
    
    fig = plt.figure(figsize=(8,8))
    ax1 = fig.add_subplot(111)
    ax1.set_title(title, fontsize = size_font_title)
    ax1.set_ylim(min([min(r_cmf), min(g_cmf), min(b_cmf)]), max([max(r_cmf), max(g_cmf), max(b_cmf)])*1.05)
    ax1.set_xlim(nm_ini, nm_end) 
    plt.plot(wavelength, r_cmf, "r", label = "r_cmf")
    plt.plot(wavelength, g_cmf, "g", label = "b_cmf")
    plt.plot(wavelength, b_cmf, "b", label = "b_cmf")
    plt.xlabel(units_x)
    plt.ylabel("spectral sensitivity")
    plt.legend(loc='best', shadow = True , fontsize = size_font_ticks) 

    if save_figure:
        plt.savefig(output_path, dpi = 300, transparent = False)   
            
    if show_figure:
        plt.show()

    plt.close()

def plot_cfb(cfb_range, cfb_interval, xf_cmf, yf_cmf, zf_cmf, observer = 2, show_figure = True, save_figure = False, output_path = None):
    '''
    Function to plot the CFB using matplotlib

    Parameters:
        cfb_range       list    cfb lambda range
        cfb_interval    list    cfb lambda interval
        x_cfb           list    x-cfb lambda data
        y_cfb           list    y-cfb lambda data
        z_cfb           list    z-cfb lambda data
        observer        int     CIE standard observer (2 or 10). Default 2
        show_figure     bool    If True, the figure is shown. Default False.
        save_figure     bool    If True, the figure is saved at the output_path. Default False
        output_path     path    Path to save the figure. Default None

    ''' 

    opt2 = "CFB CMFs for the 2º standard observer (CIE 1931)"
    opt10 = "CFB CMFs for the 10º standard observer (CIE 1964)"

    title = opt2 if observer == 2 else opt10
    
    nm_ini, nm_end  = cfb_range[0], cfb_range[1]
    wavelength = lo.create_wavelength_space(nm_ini, nm_end, cfb_interval)

    size_font_title = 12
    size_font_ticks = 10

    fig = plt.figure(figsize=(8,8))
    ax1 = fig.add_subplot(111)
    ax1.set_title(title, fontsize = size_font_title)
    ax1.set_ylim(min([min(xf_cmf), min(yf_cmf), min(zf_cmf)]), max([max(xf_cmf), max(yf_cmf), max(zf_cmf)])*1.05)
    ax1.set_xlim(nm_ini, nm_end) 
    plt.plot(wavelength, xf_cmf, "r", label = "xf_cmf")
    plt.plot(wavelength, yf_cmf, "g", label = "yf_cmf")
    plt.plot(wavelength, zf_cmf, "b", label = "zf_cmf")
    plt.xlabel("wavelength λ (nm)")
    plt.ylabel("spectral sensitivity")
    plt.legend(loc='best', shadow = True , fontsize = size_font_ticks) 

    if save_figure:
        plt.savefig(output_path, dpi = 300, transparent = False)   
            
    if show_figure:
        plt.show()

    plt.close()

def plot_cielab(samples, show_figure = True, save_figure = False, output_path = None, title='CIELAB Diagram'):
    '''
    Function to plot the CIELAB diagram using matplotlib

    Parameters:
        samples         dict    CIELAB coordinates for the input samples as dict
                                samples = {name_id: (L, a, b)}
        show_figure     bool    If True, the figure is shown. Default False.
        save_figure     bool    If True, the figure is saved at the output_path. Default False
        output_path     path    Path to save the figure. Default None
        
    ''' 
    size_font_title = 12
    size_font_ticks = 10
    
    fig = plt.figure(figsize=(10,10))
    ax1 = fig.add_subplot(111)
    ax1.set_title(title, fontsize = size_font_title)
    plt.axis('off')
        
    for i in range(1,6):
        circle = Circle((0, 0), 20*i, facecolor='none', edgecolor="grey", linewidth = 1)
        ax1.add_patch(circle) 
    
    circle_border = Circle((0, 0), 120, facecolor='none', edgecolor="grey", linewidth = 0)
    ax1.add_patch(circle_border) 

    # new axis and labels
    plt.plot([-100,100], [0,0], c="black", lw = 2)
    plt.plot([0,0], [-100,100], c="black", lw = 2)
    
    text_kwargs = dict(ha='center', va='center', fontsize=9, color='black')
    ax1.text(108, 6, "0º", **text_kwargs)
    ax1.text(108, 0, "Red", **text_kwargs)
    ax1.text(108, -6, "+a*", **text_kwargs)
    
    ax1.text(-109, 6, "180º", **text_kwargs)
    ax1.text(-109, 0, "Green", **text_kwargs)
    ax1.text(-109, -6, "-a*", **text_kwargs)
    
    ax1.text(0, 116, "90º", **text_kwargs)
    ax1.text(0, 110, "Yellow", **text_kwargs)
    ax1.text(0, 104, "+b*", **text_kwargs)

    ax1.text(0, -104, "Blue", **text_kwargs)
    ax1.text(0, -110, "-b*", **text_kwargs)
    ax1.text(0, -116, "270º", **text_kwargs)

    for i in range(1,5):
        label_pos = f"+ {20*i}"
        label_neg = f"- {20*i}"
        ax1.text(-7.5, 20*i+2.5, label_pos, **text_kwargs)  
        ax1.text(20*i+6, 2.5, label_pos, **text_kwargs)   
        ax1.text(-(20*i+6), 2.5, label_neg, **text_kwargs) 
        ax1.text(-7.5, -(20*i+2.5), label_neg, **text_kwargs)  
        
    for key,value in samples.items():    
        #Xn, Yn, Zn = (95.04, 100.00, 108.88) # WP D65
        #r, g, b = csc.LAB_to_XYZ_to_RGB(value[0], value[1], value[2], Xn, Yn, Zn, "sRGB")
        #ax1.scatter(value[1], value[2], s=10, c = (r,g,b), label = key)
        #plt.plot([0, value[1]], [0, value[2]], c = (r,g,b), alpha=0.5)
        #ax1.text(value[1]+3, value[2], key, ha='center', va='center', fontsize=9, color=(r,g,b))
        ax1.scatter(value[1], value[2], s=10, c = "blue", label = key)
        plt.plot([0, value[1]], [0, value[2]], c = "blue", alpha=0.5)
        ax1.text(value[1]+5, value[2]+3, key, ha='center', va='center', fontsize=9, color="blue")
        
    plt.legend(loc='best', shadow = False ,fontsize = size_font_ticks)  # Improve

    if save_figure:
        plt.savefig(output_path, dpi = 300, transparent = False)   
            
    if show_figure:
        plt.show()

    plt.close()

def plot_chromaticity_diagram(samples, show_figure = True, save_figure = False, output_path = None):
    ''' 
    Function to plot a set of colour samples into the x,y Chromaticity diagram using Matplotlib.

    Parameters:
        samples         dict    xy coordinates for the input samples as dict.
                                samples = {"name_id": (x,y)}.
        show_figure     bool    If True, the figure is shown. Default False.
        save_figure     bool    If True, the figure is saved at the output_path. Default False.
        output_path     path    Path to save the figure. Default None.
    ''' 

    xyz_CIE1931_extended = {
        "Metadata": ["11.1 Table 1", "Chromaticity coordinates of the CIE1931 standar colorimetric observer (extended)", "pg.43-44"],
        "lambda_nm_interval": 5, "lambda_nm_range": [360, 830],
        "x": [0.175560, 0.175161, 0.174821, 0.174510, 0.174112, 0.174008, 0.173801, 0.173560, 0.173337, 0.173021, 0.172577, 0.172087, 0.171407,
        0.170301, 0.168878, 0.166895, 0.164412, 0.161105, 0.156641, 0.150985, 0.143960, 0.135503, 0.124118, 0.109594, 0.091294, 0.068706, 0.045391,
        0.023460, 0.008168, 0.003859, 0.013870, 0.038852, 0.074302, 0.114161, 0.154722, 0.192876, 0.229620, 0.265775, 0.301604, 0.337363, 0.373102,
        0.408736, 0.444062, 0.478775, 0.512486, 0.544787, 0.575151, 0.602933, 0.627037, 0.648233, 0.665764, 0.680079, 0.691504, 0.700606, 0.707918,
        0.714032, 0.719033, 0.723032, 0.725992, 0.728272, 0.729969, 0.731089, 0.731993, 0.732719, 0.733417, 0.734047, 0.734390, 0.734592, 0.734690,
        0.734690, 0.734690, 0.734548, 0.734690, 0.734690, 0.734690, 0.734690, 0.734690, 0.734690, 0.734690, 0.734690, 0.734690, 0.734690, 0.734690,
        0.734690, 0.734690, 0.734690, 0.734690, 0.734690, 0.734690, 0.734690, 0.734690, 0.734690, 0.734690, 0.734690, 0.734690],
        "y": [0.005294, 0.005256, 0.005221, 0.005182, 0.004964, 0.004981, 0.004915, 0.004923, 0.004797, 0.004775, 0.004799, 0.004833, 0.005102,
        0.005789, 0.006900, 0.008556, 0.010858, 0.013793, 0.017705, 0.022740, 0.029703, 0.039879, 0.057803, 0.086843, 0.132702, 0.200723, 0.294976,
        0.412703, 0.538423, 0.654823, 0.750186, 0.812016, 0.833803, 0.826207, 0.805864, 0.781629, 0.754329, 0.724324, 0.692308, 0.658848, 0.624451,
        0.589607, 0.554714, 0.520202, 0.486591, 0.454434, 0.424232, 0.396497, 0.372491, 0.351395, 0.334011, 0.319747, 0.308342, 0.299301, 0.292027,
        0.285929, 0.280935, 0.276948, 0.274008, 0.271728, 0.270031, 0.268911, 0.268007, 0.267281, 0.266583, 0.265953, 0.265610, 0.265408, 0.265310,
        0.265310, 0.265310, 0.265452, 0.265310, 0.265310, 0.265310, 0.265310, 0.265310, 0.265310, 0.265310, 0.265310, 0.265310, 0.265310, 0.265310,
        0.265310, 0.265310, 0.265310, 0.265310, 0.265310, 0.265310, 0.265310, 0.265310, 0.265310, 0.265310, 0.265310, 0.265310],
        "z": [0.819582, 0.819959, 0.820309, 0.820924, 0.821012, 0.821284, 0.821517, 0.821866, 0.822204, 0.822624, 0.823081, 0.823490, 0.823911,
        0.824222, 0.824549, 0.824731, 0.825102, 0.825654, 0.826274, 0.826337, 0.824618, 0.818079, 0.803563, 0.776004, 0.730571, 0.659633, 0.563837,
        0.453409, 0.341318, 0.235943, 0.149132, 0.091894, 0.059632, 0.039414, 0.025495, 0.016051, 0.009901, 0.006088, 0.003788, 0.002448, 0.001657,
        0.001224, 0.001023, 0.000923, 0.000779, 0.000616, 0.000571, 0.000472, 0.000372, 0.000226, 0.000174, 0.000154, 0.000093, 0.000055, 0.000040,
        0.000032, 0.000020, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
        0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000]
        }
    
    sRGBprimary = np.array([[0.6400, 0.3300],[0.3000, 0.6000],[0.1500, 0.0600],[0.6400, 0.3300]])

    XYZprimary = np.array([[1,0],[0,1],[0,0],[1,0]])

    x_boundary = xyz_CIE1931_extended["x"]
    y_boundary = xyz_CIE1931_extended["y"]
    xy_boundary = []

    for i in range(0,len(x_boundary)):
        xy_boundary.append([x_boundary[i],y_boundary[i]])

    # closed polygon
    xy_boundary.append([x_boundary[0],y_boundary[0]])
    xy_boundary = np.array(xy_boundary)

    # chromaticity diagram
    size_font_title = 12
    size_font_ticks = 10

    fig = plt.figure(figsize=(8,8))
    ax1 = fig.add_subplot(111)
    ax1.set_title('CIE 1931 x,y Chromaticity Diagram', fontsize = size_font_title)

    text_kwargs = dict(ha='center', va='center', fontsize=9, color='black')

    for key,value in samples.items():
        ax1.scatter(value[0],value[1], s=10, c="black", label = key)
        ax1.text(value[0]+.02,value[1]+.02, key, **text_kwargs)
    #ax1.scatter(sRGBprimary[:,0],sRGBprimary[:,1], s=4, c="red", label ="sRGB primary colours")
    #ax1.scatter(XYZprimary[:,0],XYZprimary[:,1], s=4, c="k", label ="CIE XYZ primary colours")
    #ax1.plot(sRGBprimary[:,0],sRGBprimary[:,1],"r:", label ="sRGB boundary")
    #ax1.plot(XYZprimary[:,0],XYZprimary[:,1],"k:", label ="CIE XYZ boundary")
    ax1.plot(xy_boundary[:,0],xy_boundary[:,1],"b-", label ="Visible spectrum boundary")
    #plt.axis([-0.05, 1.05, -0.05, 1.05])
    ax1.set_ylim(0, max(xyz_CIE1931_extended["y"]))
    ax1.set_xlim(0, max(xyz_CIE1931_extended["x"]))
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend(loc='best', shadow = True ,fontsize = size_font_ticks)  # Ver como usar

    if save_figure:
        #plt.tight_layout()
        plt.savefig(output_path, dpi = 300, transparent = False)
    
    if show_figure:
        plt.show()

    plt.close()

def plot_rgb_channel_histogram(rgb_array, show_figure = True, save_figure = False, output_path = None, title="RGB  Histogram"):
    '''
    Function to create and display the RGB channel Histogram using Matplotlib
    
    Parameters:
        rgb_array      np.array     RGB data
        show_figure    bool         If True, the figure is shown. Default: False.
        save_figure    bool         If True, the figure is saved at the output_path. Default: False
        output_path    path         Path to save the figure. Default: None
        title          str          Matplotlib title. Default: "RGB  Histogram"

    '''
    
    size_font_title = 6 # text size
    size_font_ticks = 6
    
    r,g,b = np.dsplit(rgb_array, 3) 
    #reshape
    r = np.reshape(r, (r.shape[0]*r.shape[1]))
    g = np.reshape(g, (g.shape[0]*g.shape[1]))
    b = np.reshape(b, (b.shape[0]*b.shape[1]))
    
    #print(r.shape, g.shape, b.shape)
    #print(np.amin(r), np.amax(r))
    #print(np.amin(g), np.amax(g))
    #print(np.amin(b), np.amax(g))

    amin = 0
    amax = rgb_array.max()

    fig = plt.figure(figsize=(6,4))
    ax1 = fig.add_subplot(111)
    
    plt.hist(r, bins = 250, color = "red", histtype = 'barstacked', density=True, edgecolor = "black", linewidth=0.1, alpha = 0.9, label = "R") # bins = 250, 
    plt.hist(g, bins = 250, color = "green", histtype = 'barstacked', density=True, edgecolor = "black", linewidth=0.1, alpha = 0.9, label = "G") # bins = 250, 
    plt.hist(b, bins = 250, color = "blue", histtype = 'barstacked', density=True, edgecolor = "black", linewidth=0.1, alpha = 0.9, label = "B") # bins = 250, 
    plt.xlim(amin, amax)
    plt.xticks(fontsize=size_font_ticks)
    plt.yticks(fontsize=size_font_ticks)
    plt.ylabel("frequency", fontsize = size_font_ticks)    
    plt.legend(loc='best', shadow = True ,fontsize = size_font_ticks)
    
    plt.suptitle(title, fontsize = size_font_title)

    if save_figure:
        plt.savefig(output_path, dpi = 300, transparent = False)
    
    if show_figure:
        plt.show()

    plt.close()

def plot_rgb_channel_histogram_split(rgb_array, show_figure = True, save_figure = False, output_path = None, title="RGB  Histogram"):
    '''
    Function to create and display the RGB channel Histogram (split per channel) using Matplotlib
    
    Parameters:
        rgb_array      np.array     RGB data
        show_figure    bool         If True, the figure is shown. Default: False.
        save_figure    bool         If True, the figure is saved at the output_path. Default: False
        output_path    path         Path to save the figure. Default: None
        title          str          Matplotlib title. Default: "RGB  Histogram"

    '''

    size_font_title = 6 # text size
    size_font_ticks = 6
    
    r,g,b = np.dsplit(rgb_array, 3) 
    #reshape
    r = np.reshape(r, (r.shape[0]*r.shape[1]))
    g = np.reshape(g, (g.shape[0]*g.shape[1]))
    b = np.reshape(b, (b.shape[0]*b.shape[1]))
    
    #print(r.shape, g.shape, b.shape)
    #print(np.amin(r), np.amax(r))
    #print(np.amin(g), np.amax(g))
    #print(np.amin(b), np.amax(g))
    
    amin = 0
    amax = rgb_array.max()
    
    plt.subplots(1,3, figsize = (8,2), sharey = True, dpi = 300)
    
    dict_data = {0: {"data":r, "label": "R", "color": "red"}, 1: {"data":g, "label": "G", "color": "green"}, 2: {"data":b, "label": "B", "color": "blue"}}
    
    for i in range(0,3):
        plt.subplot(1,3,(i+1))
        plt.hist(dict_data[i]["data"], bins = 250, color = dict_data[i]["color"], histtype = 'barstacked', density=True, edgecolor = "black", linewidth=0.1, alpha = 0.9, label = dict_data[i]["label"]) # bins = 250, 
        plt.xlim(amin, amax)
        plt.xticks(fontsize=size_font_ticks)
        plt.yticks(fontsize=size_font_ticks)
        plt.xlabel(dict_data[i]["label"], fontsize = size_font_ticks)
        plt.ylabel("frequency", fontsize = size_font_ticks)    
        plt.legend(loc='best', shadow = True ,fontsize = size_font_ticks)
    
    plt.suptitle(title, fontsize = size_font_title)

    if save_figure:
        plt.savefig(output_path, dpi = 300, transparent = False)
    
    if show_figure:
        plt.show()

    plt.close()


def plot_residuals(residuals, show_figure = True, save_figure = False, output_path = None):
    residual_label = "XYZ"
    fig, axis = plt.subplots(1,3, figsize=(24,6))
    fig.suptitle("Residuals CIE XYZ", fontsize = 14)
    colours = ["indigo", "navy", "slategrey"]
    for i in range(0,len(axis)):
        sns.histplot(x=residuals[:,i], color = colours[i], kde=True, ax = axis[i])
        axis[i].set(xlabel=f"{residual_label[i]}", ylabel="Frequency")
    
    if save_figure:
        #plt.tight_layout()
        plt.savefig(output_path, dpi = 300, transparent = False)
    
    if show_figure:
        plt.show()

    plt.close()

def plot_delta_e(AE, show_figure = True, save_figure = False, output_path = None):
    
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))

    sns.histplot(x=AE, color = "blue", kde=True, ax = axes[0])
    axes[0].set_title('CIE76 - Colour Differences (CIELAB units)', fontsize = 10, fontweight = "bold")
    axes[0].set_xlabel('CIE76')
    axes[0].set_ylabel('Frequency')
    axes[0].tick_params(labelsize = 7)

    axes[1].scatter(list(range(len(AE))), AE, color ="blue", edgecolors=(0, 0, 0), alpha = 0.4)
    axes[1].axhline(y = 4, linestyle = '--', color = 'red', lw=2) # threshold
    axes[1].set_title('CIE76 - Colour Differences (CIELAB units)', fontsize = 10, fontweight = "bold")
    axes[1].set_xlabel('Patch')
    axes[1].set_ylabel('CIE76')
    axes[1].tick_params(labelsize = 7)

    if save_figure:
        #plt.tight_layout()
        plt.savefig(output_path, dpi = 300, transparent = False)
    
    if show_figure:
        plt.show()

    plt.close()

def plot_rgb_data(r, g, b, title):
    
    size_font_title = 6 # text size
    size_font_ticks = 6
    
    r = np.array(r)
    g = np.array(g)
    b = np.array(b)
        
    amin = 0
    amax = rwo.compute_amax_channels(r,g,b)
    
    plt.figure(figsize = (6,6))#, sharey = True, dpi = 300)
    
    dict_data = {0: {"data":r, "label": "R", "color": "red"}, 1: {"data":g, "label": "G", "color": "green"}, 2: {"data":b, "label": "B", "color": "blue"}}
    
    for i in range(0,3):
        #plt.subplot(1,3,(i+1))
        plt.hist(dict_data[i]["data"], bins = r.shape[0], color = dict_data[i]["color"], histtype = 'barstacked', density=True, edgecolor = "black", linewidth=0.1, alpha = 0.9, label = dict_data[i]["label"]) # bins = 250, 
    
    plt.xlim(amin, amax)
    plt.xticks(fontsize=size_font_ticks)
    plt.yticks(fontsize=size_font_ticks)
    plt.xlabel(dict_data[i]["label"], fontsize = size_font_ticks)
    plt.ylabel("frequency", fontsize = size_font_ticks)    
    plt.legend(loc='best', shadow = True ,fontsize = size_font_ticks)
    plt.suptitle(title, fontsize = size_font_title)

    plt.show()

    plt.close()
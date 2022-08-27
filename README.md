# Coolpi

# Description

<div style="text-align: justify">
The Colour Operations Library for the Processing of Images (coolpi) is an open-source toolbox programmed in Python for the treatment of colorimetric
and spectral data. It includes classes, methods and functions developed and tested following the colorimetric standards 
published by the Commission Internationale de l'Éclairage [(CIE, 2018)](https://cie.co.at/publications/colorimetry-4th-edition/).

The coolpi package has been developed as part of the [INDIGO](https://projectindigo.eu/) project (In-ventory and 
DI-sseminate G-raffiti along the d-O-naukanal) carried out by the [Ludwig Boltzmann Institute](https://archpro.lbg.ac.at/) 
in close collaboration with the [GEO Department of TU Wien University](https://www.geo.tuwien.ac.at/).

The achievement of colour-accurate digital images is one of the primary research topics within the INDIGO project. 
Therefore, the coolpi package also includes specific procedures for digital image processing and colour correction, 
particularly from images in RAW format. 

Although the coolpi package has been designed mainly for Cultural Heritage documentation applications based on digital 
imaging techniques, we are confident that its applicability can be extended to any discipline where colour accurate 
registration is required.

</div>

# Modules

<div style="text-align: justify">

The coolpi library is structured in the following oriented objected programming (OOP) modules:

- Auxiliary: scripts with common operations for the coolpi modules.
- Colour: CIE, Colour and Spectral classes, with the basic colorimetric tools based on CIE formulation or additional published standards.
- Image: ColourChecker and Image classes with the methods and functions for image processing.

The coolpi auxilary module integrates functions that are used in the classes to carry out operations related to data loading and checking,
creation and display of colorimetric and spectral graphs, and so on. It also includes the errors module, with the exceptions associated with each of the classes. 

</div>

The recommended way to import the auxiliary modules is as follows:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Python 
>>> import coolpi.auxiliary.common_operations as cop
>>> import coolpi.auxiliary.load_data as ld
>>> import coolpi.auxiliary.export_data as ed
>>> import coolpi.auxiliary.plot as cpt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 <div style="text-align: justify">

The auxiliary functions are designed to support the coolpi library classes, they are not intended to be used independently by the user. 
However, they can be imported and used directly from Python if desired.*

The colour module is one of the pillars of the coolpi package, and is based on the colorimetric recommendations 
of the CIE [(CIE, 2018)](https://cie.co.at/publications/colorimetry-4th-edition/). This module includes the CIE], Colour and 
Spectral main classes, and the implementation of the basic tools for the colorimetric and spectral treatment of the data.

The acquisition of colour-accurate digital images is one of the primary research topics in the international graffiti project [INDIGO](https://projectindigo.eu/). 
Thus, the image module implemented in coolpi provides the ColourChecker and Image classes, with the methods and functions necessary 
to process and obtain accurate-colour data from digital images, especially in RAW format.

In addition, a graphical interface GUI has been designed that integrates the main functionalities of the coolpi library, 
especially designed for non-programmer users. 

</div>

# Installation

<div style="text-align: justify">
The coolpi package can be installed directly from [PyPi](https://pypi.org/) running the pip command 
on the system shell:</div>

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Python 
>>> pip install coolpi
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

<div style="text-align: justify">
The coolpi package is based on Python 3.9. It is therefore recommended not to work  with lower python versions, 
as the correct functioning of the library is not guaranteed.</div>


# Dependencies

<div style="text-align: justify">
For the proper operation of coolpi, the following packages must be installed together:

- Create plots and figures: [matplotlib 3.5.2](https://matplotlib.org/stable/index.html) 
- Scientific computing: [numpy 1.22.4](https://numpy.org/doc/1.22/reference/index.html)
- Computer vision: [opencv-python 4.6.0.66](https://pypi.org/project/opencv-python/)
- Data Analysis: [pandas 1.4.2](https://pandas.pydata.org/pandas-docs/version/1.4/index.html)
- Qt (GUI): [pyside6 6.3.0](https://pypi.org/project/PySide6/)
- RAW image processing: [rawpy 0.17.1](https://pypi.org/project/rawpy/)
- Scientific computing: [scipy 1.8.1](https://docs.scipy.org/doc/scipy/reference/index.html#scipy-api)
- Statistical data visualization: [seaborn 0.11.2](https://seaborn.pydata.org/tutorial.html)

The dependencies should have been installed automatically along with coolpi. Please check that everything is correct.

</div>

# Notebooks

<div style="text-align: justify">
A series of interactive [Jupyter Notebooks](https://jupyter.org) have been prepared. They include practical examples 
to help users become familiar with the classes, methods and functions implemented in the coolpi package. 

- 01 CIE objects
- 02a Colour objects
- 02b CSC - Colour Space Conversion
- 02c CSC - Data test (Ohta&Robertson 2005)
- 03a Spectral objects
- 03b CTT Calculations Test data (Fontecha et al. 2002)
- 04a Colour-difference
- 04b CIEDE2000 - Test data (Sharma et al., 2005)
- 05 ColourChecker objects
- 06 Image objects

Users can find the interative Jupyter Notebooks in the [notebook folder of the coolpi repository on GitHub]().

In order to use the iterative notebooks, [JupyterLab](https://jupyter.org/install), or its extension in the code editor used, 
must be installed beforehand.*

</div>

# GUI

<div style="text-align: justify">
A graphical user interface has been designed together with the coolpi package. The aim is to help especially non-programmers to use 
in an easy and practical way the functionalities implemented in the coolpi library. Efforts have been made to develop the graphical 
interface in a way that makes it intuitive and friendly to use. 

To run the coolpi-gui:</div>

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Python 
>>> from coolpi.gui.app import GUI
>>> gui = GUI()
>>> gui.run()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

<div style="text-align: justify">
The coolpi-gui includes the following tools:

- CSC: Colour Space Conversion
- CDE: Colour $\Delta E$
- CPT: Colour Plot Tool
- SPC: Spectral Colour
- SPD: Illuminant SPD
- CCI: ColourChecker Inspector
- RCIP: RAW Colour Image Processing
</div>

# Project links

<div style="text-align: justify">
- [INDIGO project](https://projectindigo.eu)
- [Ludwig Boltzmann Institut](https://archpro.lbg.ac.at)
- [GitHub](https://github.com/GraffitiProjectINDIGO/coolpi)
- [Source](https://github.com/GraffitiProjectINDIGO/coolpi/src"
- [Coolpi Documentation](https://github.com/GraffitiProjectINDIGO/coolpi/doc)
- [Jupyter Notebooks](https://github.com/GraffitiProjectINDIGO/coolpi/notebooks)
</div>

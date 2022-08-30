import json
import os
import sys
import webbrowser

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from coolpi.gui.config import Config

class AppView(QtWidgets.QMainWindow):

    def __init__(self, app,  parent = None):
        super().__init__()     
        self._app = app   
        self._set_initial_attributes()
        self._create_items()
        self._add_items()

    def _set_initial_attributes(self):
        self.setWindowTitle(Config.instance().data["main"]["title"])
        self.setGeometry(Config.instance().data["main"]["init_position"][0],Config.instance().data["main"]["init_position"][1],Config.instance().data["main"]["screen_size"][0],Config.instance().data["main"]["screen_size"][1])
        self.setMinimumSize(Config.instance().data["main"]["screen_size"][0], Config.instance().data["main"]["screen_size"][1])
    
    def _create_items(self):
        self._create_central_widget()
        self._create_layout()
        self._create_status_bar()
        self._create_logos()
        self._create_icons()
        self._create_actions()
        self._create_menu_bar()
        self._create_buttons()
        
    def _create_central_widget(self):
        self._central_widget = QtWidgets.QWidget(self)
        medium_gray = Config.instance().data["colour"]["rgb_medium_gray"]
        self._central_widget.setStyleSheet(f"background-color: {medium_gray};")
        self.setCentralWidget(self._central_widget)
    
    def _create_layout(self):
        self._grid_layout = QtWidgets.QGridLayout(self.centralWidget())
        self.setLayout = self._grid_layout

    def _create_status_bar(self):
        self.statusBar = QtWidgets.QStatusBar()
        colour_sb = Config.instance().data["colour"]["rgb_light_gray"]
        colour_font_sb = "white"
        self.statusBar.setStyleSheet(f"background-color: {colour_sb}; color: {colour_font_sb}")
        self.setStatusBar(self.statusBar)
        # init msg
        self.statusBar.showMessage(Config.instance().data["main"]["init_statusbar_message"])

    def _create_logos(self):
        self._coolpi_label = Logo("coolpi", os.path.join(*[Config.coolpi_dir, *Config.instance().data["logo"]["file_logo_coolpi"]]))
        self._lbi_label = Logo("LBI", os.path.join(*[Config.coolpi_dir, *Config.instance().data["logo"]["file_logo_LBI"]]))
        self._indigo_label = Logo("Indigo", os.path.join(*[Config.coolpi_dir, *Config.instance().data["logo"]["file_logo_indigo"]]))

    def _create_icons(self):
        self._cci_icon = QtGui.QIcon(os.path.join(*[Config.coolpi_dir, *Config.instance().data["icon"]["file_cci_icon"]]))
        self._cde_icon = QtGui.QIcon(os.path.join(*[Config.coolpi_dir, *Config.instance().data["icon"]["file_cde_icon"]]))        
        self._cpt_icon = QtGui.QIcon(os.path.join(*[Config.coolpi_dir, *Config.instance().data["icon"]["file_cpt_icon"]]))           
        self._csc_icon = QtGui.QIcon(os.path.join(*[Config.coolpi_dir, *Config.instance().data["icon"]["file_csc_icon"]]))
        #self._irgbe_icon = QtGui.QIcon(os.path.join(*Config.instance().data["icon"]["file_irgbe_icon"]))
        #self._lrm_icon = QtGui.QIcon(os.path.join(*Config.instance().data["icon"]["file_lrm_icon"]))
        self._quit_icon = QtGui.QIcon(os.path.join(*[Config.coolpi_dir, *Config.instance().data["icon"]["file_quit_icon"]]))
        self._rcip_icon = QtGui.QIcon(os.path.join(*[Config.coolpi_dir, *Config.instance().data["icon"]["file_rcip_icon"]]))     
        self._spc_icon = QtGui.QIcon(os.path.join(*[Config.coolpi_dir, *Config.instance().data["icon"]["file_spc_icon"]]))
        self._spd_icon = QtGui.QIcon(os.path.join(*[Config.coolpi_dir, *Config.instance().data["icon"]["file_spd_icon"]]))
        #self._wb_icon = QtGui.QIcon(os.path.join(*Config.instance().data["icon"]["file_wb_icon"]))
        
    def _create_actions(self):
        # csc - colour space conversion
        self._csc_action = QtGui.QAction(self._csc_icon, "&Colour Space Conversion")
        self._csc_action.setStatusTip("Open the Colour Space Conversion Tool")
        self._csc_action.setShortcut("Ctrl+C")
        # cde - colour deltae differences
        self._cde_action = QtGui.QAction(self._cde_icon, "Colour \u0394E &Differences")
        self._cde_action.setStatusTip("Open the Colour \u0394E differences Tool")
        self._cde_action.setShortcut("Ctrl+D")
        # cpt - plot
        self._cpt_action = QtGui.QAction(self._cpt_icon, "&Plot")
        self._cpt_action.setStatusTip("Open the Colour Plot Tool")
        self._cpt_action.setShortcut("Ctrl+P")
        # spc - spectral colour
        self._spc_action = QtGui.QAction(self._spc_icon , "&Spectral Colour")
        self._spc_action.setStatusTip("Open the Spectral Tool")
        self._spc_action.setShortcut("Ctrl+S")
        # spd - illuminant SPD
        self._spd_action = QtGui.QAction(self._spd_icon, "&Illuminant")
        self._spd_action.setStatusTip("Open the Illuminant SPD Inspector Tool")
        self._spd_action.setShortcut("Ctrl+I")
        # cci - colourchecker inspector
        self._cci_action = QtGui.QAction(self._cci_icon, "ColourChecker")
        self._cci_action.setStatusTip("Open the ColourChecker Inspector Tool")
        self._cci_action.setShortcut("Ctrl+T")   
        
        # crip - colour raw image processing
        self._rcip_action = QtGui.QAction(self._rcip_icon, "&RAW Image")
        self._rcip_action.setStatusTip("Open the RAW Colour Image Processing Tool")
        self._rcip_action.setShortcut("Ctrl+R")        
        # quit
        self._quit_action = QtGui.QAction(self._quit_icon , "&Quit")
        self._quit_action.setStatusTip("Quit the program")
        self._quit_action.setShortcut("Ctrl+Q")

    def _create_menu_bar(self):
        self.menuBar = QtWidgets.QMenuBar()
        self.setMenuBar(self.menuBar)
        self.menuBar.setNativeMenuBar(False)

        colour_menu = Config.instance().data["colour"]["rgb_dark_gray"]
        colour_font_menu = "white"
        self.menuBar.setStyleSheet(f"background-color: {colour_menu} ; color: {colour_font_menu}")
        
        self._menu_colour = QtWidgets.QMenu(" Colour", self)
        self._menu_colour.addAction(self._csc_action)   
        self._menu_colour.addAction(self._cde_action) 
        self._menu_colour.addSeparator() 
        self._menu_colour.addAction(self._cpt_action)  
        
        self._menu_spectral = QtWidgets.QMenu(" Spectral", self)
        self._menu_spectral.addAction(self._spc_action)
        self._menu_spectral.addSeparator()   
        self._menu_spectral.addAction(self._spd_action)  
        
        self._menu_colourchecker = QtWidgets.QMenu(" ColourChecker", self)
        self._menu_colourchecker.addAction(self._cci_action)  
        
        self._menu_image = QtWidgets.QMenu(" Image", self)
        self._menu_image.addAction(self._rcip_action)  
        
        self._menu_quit = QtWidgets.QMenu(" &Quit", self)
        self._menu_quit.addAction(self._quit_action)  
        
        menu_list = [self._menu_colour, self._menu_spectral, self._menu_colourchecker, self._menu_image, self._menu_quit] 
        for menu in menu_list:
            self.menuBar.addMenu(menu)

    def _create_buttons(self):
        colour_button = Config.instance().data["buttons"]["colour"]
        icon_button_size = QtCore.QSize(Config.instance().data["buttons"]["icon_size"], Config.instance().data["buttons"]["icon_size"])
        button_border_width = Config.instance().data["buttons"]["border_width"]
        button_border_colour = Config.instance().data["buttons"]["border_colour"]

        self._csc_button = QtWidgets.QPushButton(self._csc_icon, "")    
        self._csc_button.setStatusTip("Open the Colour Space Conversion Tool")
        self._cde_button = QtWidgets.QPushButton(self._cde_icon, "")
        self._cde_button.setStatusTip("Open the Colour \u0394E differences Tool")
        self._cpt_button = QtWidgets.QPushButton(self._cpt_icon, "")
        self._cpt_button.setStatusTip("Open the Colour Plot Tool")
        
        self._spc_button = QtWidgets.QPushButton(self._spc_icon, "")
        self._spc_button.setStatusTip("Open the Spectral Tools")
        self._spd_button = QtWidgets.QPushButton(self._spd_icon, "")
        self._spd_button.setStatusTip("Open the Illuminant SPD Inspector Tool")
        self._cci_button = QtWidgets.QPushButton(self._cci_icon, "")
        self._cci_button.setStatusTip("Open the ColourChecker Inspector Tool")
        
        self._rcip_button = QtWidgets.QPushButton(self._rcip_icon, "")    
        self._rcip_button.setStatusTip("Open the RAW Colour Image Processing Tool")   
        
        list_buttons = [self._csc_button, self._cde_button, self._cpt_button,
                        self._spc_button, self._spd_button, self._cci_button, 
                        self._rcip_button] 
        
        for button in list_buttons:
            button.setIconSize(icon_button_size)
            button.setStyleSheet(f"background-color: {colour_button}; border-width: {button_border_width}; border-color: {button_border_colour}")

    def _add_items(self):
        # colour
        self._grid_layout.addWidget(self._csc_button, 0, 0)
        self._grid_layout.addWidget(self._cde_button, 0, 1)
        self._grid_layout.addWidget(self._cpt_button, 0, 2)
        # spectral
        self._grid_layout.addWidget(self._spc_button, 1, 0)
        self._grid_layout.addWidget(self._spd_button, 1, 1)
        self._grid_layout.addWidget(self._cci_button, 1, 2)
        # image
        self._grid_layout.addWidget(self._rcip_button, 2, 1)#, 1, 3)
        self._grid_layout.addWidget(self._lbi_label, 2, 0, QtCore.Qt.AlignLeft)
        self._grid_layout.addWidget(self._indigo_label, 2, 2, QtCore.Qt.AlignCenter)

    # CSC - Colour Space Conversion
    def open_csc_view(self):
        self._csc = CSC(self)
        self._csc.setFocus()
        self._csc.setVisible(True)
        posx = self.pos().x() + Config.instance().data["main"]["screen_size"][0]
        posy = self.pos().y()
        self._csc.set_position(posx, posy)
        self._csc.show() 

    # CDE - Colour Differences
    def open_cde_view(self):
        self._cde = CDE(self)
        self._cde.setFocus()
        self._cde.setVisible(True)
        posx = self.pos().x() + Config.instance().data["main"]["screen_size"][0]
        posy = self.pos().y()
        self._cde.set_position(posx, posy)
        self._cde.show() 

   # CPT - Plot
    def open_cpt_view(self):        
        self._cpt = CPT(self)
        self._cpt.setFocus()
        self._cpt.setVisible(True)
        posx = self.pos().x() + Config.instance().data["main"]["screen_size"][0]
        posy = self.pos().y()
        self._cpt.set_position(posx, posy)
        self._cpt.show()

    # SPC - Spectral Colour
    def open_spc_view(self):
        self._spc = SPC(self)
        self._spc.setFocus()
        self._spc.setVisible(True)
        posx = self.pos().x() + Config.instance().data["main"]["screen_size"][0]
        posy = self.pos().y()
        self._spc.set_position(posx, posy)
        self._spc.show() 

    # SPD - Illuminant SPD
    def open_spd_view(self):
        self._spd = SPD(self)
        self._spd.setFocus()
        self._spd.setVisible(True)
        posx = self.pos().x() + Config.instance().data["main"]["screen_size"][0]
        posy = self.pos().y()
        self._spd.set_position(posx, posy)
        self._spd.show()

    # CCI - ColourChecker Inspector
    def open_cci_view(self):
        self._cci = CCI(self)
        self._cci.setFocus()
        self._cci.setVisible(True)
        posx = self.pos().x() + Config.instance().data["main"]["screen_size"][0]
        posy = self.pos().y()
        self._cci.set_position(posx, posy)
        self._cci.show()
    
    # RCIP - Raw Colour Image Processing
    def open_rcip_view(self):
        self._rcip = RCIP(self)
        self._rcip.setFocus()
        self._rcip.setVisible(True)
        posx = self.pos().x() + Config.instance().data["main"]["screen_size"][0]
        posy = self.pos().y()
        self._rcip.set_position(posx, posy)
        self._rcip.show()

    # Figure View
    def open_figure_zoom_view(self, window_title, path_image):
        self._figure = FigureView(window_title, path_image, self)
        self._figure.setFocus()
        self._figure.setVisible(True)
        posx = self.pos().x() + Config.instance().data["main"]["screen_size"][0]
        posy = self.pos().y()
        self._figure.set_position(posx, posy)
        self._figure.show()

    def open_html(self, url):
        self.statusBar.showMessage(f"Opening {url} at your browser")
        webbrowser.open(url)

    def mouseDoubleClickEvent(self, event):
        widget = self.childAt(event.pos())
        if widget is not None:
            if widget.objectName() == "LBI":
                self.open_html(Config.instance().data["logo"]["url_lbi"])
            elif widget.objectName() == "Indigo":
                self.open_html(Config.instance().data["logo"]["url_indigo"])

    # como conectar desde el controller
    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, "Window Close", "Are you sure you want to quit?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self._app.closeAllWindows()
            event.accept()
        else:
            event.ignore()
    
    def __quit__(self):   
        reply = QtWidgets.QMessageBox.question(self, "Window Close", "Are you sure you want to quit?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)        
        if reply == QtWidgets.QMessageBox.Yes:
            self._app.closeAllWindows()

# CSC - Colour Space Conversion

class CSC(QtWidgets.QWidget):

    def __init__(self, parent = None):
        super().__init__()
        self.setWindowTitle(Config.instance().data["csc"]["title"])
        self.setFixedSize(Config.instance().data["csc"]["screen_size"][0], Config.instance().data["csc"]["screen_size"][1])

        self.create_items()
        self.add_items()

    def set_position(self, posx, posy):
        self.move(posx,posy)

    def create_items(self):
        self.create_group_box()
        self.create_buttons()
        self.desactivate_export_button()
        self.create_coolpi_logo()

    def create_group_box(self):
        self._input_gb = InputGroupBox()
        self._xyz_gb = XYZGroupBox()
        self._xyY_gb = xyYGroupBox()
        self._lab_gb = LABGroupBox()
        self._lchab_gb = LCHabGroupBox()
        self._lchuv_gb = LCHuvGroupBox()
        self._luv_gb = LUVGroupBox()
        self._srgb_gb = sRGBGroupBox()
        self._srgb_gb.setMaximumWidth(140)

    def create_buttons(self):
        # properties
        colour_pink = Config.instance().data["colour"]["rgb_pink_colour"]
        colour_orange = Config.instance().data["colour"]["rgb_orange_colour"]
        colour_cyan = Config.instance().data["colour"]["rgb_cyan_colour"]
        # calculate
        self._calculate_button = QtWidgets.QPushButton()
        self._calculate_button.setText("Calculate")
        self._calculate_button.setStyleSheet(f"background-color: {colour_cyan}; color: white")
        # export
        self._export_button = QtWidgets.QPushButton()
        self._export_button.setText("Export")
        self._export_button.setStyleSheet(f"background-color: {colour_orange}; color: white")
        # clear
        self._clear_button = QtWidgets.QPushButton()
        self._clear_button.setText("Clear")     
        self._clear_button.setStyleSheet(f"background-color: {colour_pink}; color: white")

    def activate_export_button(self):
        self._export_button.setEnabled(True)

    def desactivate_export_button(self):
        self._export_button.setEnabled(False)

    def create_indigo_logo(self):
        file_logo_indigo = Config.instance().data["logo"]["file_logo_indigo"]
        path_logo_indigo = os.path.join(*[Config.coolpi_dir, *file_logo_indigo])
        self._indigo = Logo("Indigo", path_logo_indigo)

    def create_coolpi_logo(self):
        file_logo_coolpi = Config.instance().data["logo"]["file_logo_coolpi"]
        path_logo_coolpi = os.path.join(*[Config.coolpi_dir, *file_logo_coolpi])
        self._coolpi = Logo("coolpi", path_logo_coolpi)
        
    def create_coolpi_logo(self):
        file_logo_coolpi = Config.instance().data["logo"]["file_logo_coolpi"]
        path_logo_coolpi = os.path.join(*[Config.coolpi_dir, *file_logo_coolpi])
        self._coolpi = Logo("coolpi", path_logo_coolpi)

    def add_items(self):  
        self._grid_layout = QtWidgets.QGridLayout()
        self._grid_layout.addWidget(self._input_gb, 0, 0, 0, 1)
        self._grid_layout.addWidget(self._xyz_gb, 0, 1)
        self._grid_layout.addWidget(self._xyY_gb, 0, 2)
        self._grid_layout.addWidget(self._lab_gb, 0, 3)
        self._grid_layout.addWidget(self._srgb_gb, 0, 4)
        
        self._grid_layout.addWidget(self._lchab_gb, 1, 1)
        self._grid_layout.addWidget(self._lchuv_gb, 1, 2)
        self._grid_layout.addWidget(self._luv_gb, 1, 3)
        
        self._grid_layout.addWidget(self._calculate_button, 2, 0)
        self._grid_layout.addWidget(self._export_button, 2, 1)
        self._grid_layout.addWidget(self._clear_button, 2, 3)
        self._grid_layout.addWidget(self._coolpi, 2, 4, QtCore.Qt.AlignRight)

        self.setLayout(self._grid_layout)  
        
    def clear_labels(self):
        list_groups = [self._input_gb, self._xyz_gb, self._xyY_gb, self._lab_gb, self._lchab_gb, self._lchuv_gb, self._luv_gb, self._srgb_gb]
        for element in list_groups:
            element.clear_coordinates()
        self.desactivate_export_button()
        
    def get_pos_center(self):
        x_pos = int((self.pos().x() + self.frameGeometry().width())/2)
        y_pos = int((self.pos().y() + self.frameGeometry().height())/2)
        return x_pos, y_pos

    def show_warning_message(self, msg):
        warning = WarningMessageBox(self)
        x_pos, y_pos = self.get_pos_center()
        warning.setGeometry(x_pos, y_pos, Config.instance().data["main"]["message_screen_size"][0],Config.instance().data["main"]["message_screen_size"][1])
        warning.set_warning_message(msg)
        warning.exec() 
        
    def update_coordinates(self, new_coordinates):
        self._coordinates = new_coordinates
        for (key, value) in new_coordinates.items():
            if key =="CIE XYZ":
                self._xyz_gb.update_coordinates(value[0], value[1], value[2])
            if key =="CIE xyY":
                self._xyY_gb.update_coordinates(value[0], value[1], value[2])
            if key =="CIELAB":
               self._lab_gb.update_coordinates(value[0], value[1], value[2])
            if key =="CIE LCHab":
                self._lchab_gb.update_coordinates(value[0], value[1], value[2])
            if key =="CIE LCHuv":
                self._lchuv_gb.update_coordinates(value[0], value[1], value[2])
            if key =="CIELUV":
                self._luv_gb.update_coordinates(value[0], value[1], value[2])
            if key =="sRGB":
                self._srgb_gb.update_coordinates(value[0], value[1], value[2])

    def export_as_json(self):
        save_dialog = QtWidgets.QFileDialog()
        plot_default_dir = os.path.join(*[os.getcwd(), *Config.instance().data["dir_path"]["json_dir"]])
        save_path = save_dialog.getSaveFileName(self, "Save Current Coordinates", plot_default_dir, "Json files (*.json *.JSON)")
        path_file_json = save_path[0]  
        
        if path_file_json != "":  # avoid error press cancel button
            with open(path_file_json, 'w') as outfile:
                json.dump(self._coordinates, outfile, indent=4)
            self.show_export_message()
            #self.clear_labels()

    def show_export_message(self):
        export_message = SavedMessageBox("Coordinates exported successfully")
        x_pos, y_pos = self.get_pos_center()
        export_message.setGeometry(x_pos, y_pos, Config.instance().data["main"]["message_screen_size"][0],Config.instance().data["main"]["message_screen_size"][1])
        export_message.exec() # .show()

# CDE - Colour Differences

class CDE(QtWidgets.QWidget):

    def __init__(self, parent = None):
        super().__init__()
        self.setWindowTitle(Config.instance().data["cde"]["title"])
        self.setFixedSize(Config.instance().data["cde"]["screen_size"][0], Config.instance().data["cde"]["screen_size"][1])
    
        self.create_items()
        self.add_items()
    
    def set_position(self, posx, posy):
        self.move(posx,posy)
                
    def create_items(self):
        self.create_coolpi_logo()
        self.create_default_image()    
        self.create_group_box()
        self.create_buttons()

    def create_coolpi_logo(self):
        file_logo_coolpi = Config.instance().data["logo"]["file_logo_coolpi"]
        path_logo_coolpi = os.path.join(*[Config.coolpi_dir, *file_logo_coolpi])
        self._coolpi = Logo("coolpi", path_logo_coolpi)

    def create_default_image(self):
        file_default_image = Config.instance().data["plot"]["file_default_image"]
        path_default_image = os.path.join(*[Config.coolpi_dir, *file_default_image])

        self._cielab_image = QtGui.QPixmap(path_default_image)
        
        self._cielab_plot_label = QtWidgets.QLabel()
        self._cielab_plot_label.setMaximumSize(Config.instance().data["plot"]["plot_figure_size"][0], Config.instance().data["plot"]["plot_figure_size"][1])
        self._cielab_plot_label.setPixmap(self._cielab_image)
        self._cielab_plot_label.setScaledContents(True)
        
        self._srgb_image_1 = QtGui.QPixmap(path_default_image)
        self._srgb_image_2 = QtGui.QPixmap(path_default_image)

        self._srgb_plot1_label = QtWidgets.QLabel()
        self._srgb_plot1_label.setMaximumSize(Config.instance().data["plot"]["srgb_plot_size"], Config.instance().data["plot"]["srgb_plot_size"])
        self._srgb_plot1_label.setPixmap(self._srgb_image_1)
        self._srgb_plot1_label.setScaledContents(True)

        self._srgb_plot2_label = QtWidgets.QLabel()
        self._srgb_plot2_label.setMaximumSize(Config.instance().data["plot"]["srgb_plot_size"], Config.instance().data["plot"]["srgb_plot_size"])
        self._srgb_plot2_label.setPixmap(self._srgb_image_2)
        self._srgb_plot2_label.setScaledContents(True)

    def create_group_box(self):
        self._sample_1 = InputGroupBox()
        self._sample_1.setTitle("Colour Sample A")
        
        self._sample_2 = InputGroupBox()
        self._sample_2.setTitle("Colour Sample B")    
        
        self._cielab_diagram = QtWidgets.QGroupBox()
        self._cielab_diagram.setTitle("CIELAB Diagram")   
        self._cielab_form_layout = QtWidgets.QFormLayout()
        self._cielab_form_layout.addRow("", self._cielab_plot_label)
        self._cielab_diagram.setLayout(self._cielab_form_layout)
        
        self._srgb1 = QtWidgets.QGroupBox()
        self._srgb1.setTitle("Sample A")
        self._form_layout_srgb1 = QtWidgets.QFormLayout()
        self._form_layout_srgb1.addRow("", self._srgb_plot1_label)
        self._srgb1.setLayout(self._form_layout_srgb1)
        
        self._srgb2 = QtWidgets.QGroupBox()
        self._srgb2.setTitle("Sample B")
        self._form_layout_srgb2 = QtWidgets.QFormLayout()
        self._form_layout_srgb2.addRow("", self._srgb_plot2_label)   
        self._srgb2.setLayout(self._form_layout_srgb2)

        self._LAB1 = LABGroupBox()
        self._LAB1.setTitle("CIELAB A")   
         
        self._LAB2 = LABGroupBox()
        self._LAB2.setTitle("CIELAB B")   
        
        self._cie76_gb = QtWidgets.QGroupBox()
        self._cie76_gb.setTitle("\u0394Eab - CIE76")
        self._cie76_form = QtWidgets.QFormLayout()
        self._cie76 = QtWidgets.QLineEdit()
        self._cie76.setEnabled(False)
        self._cie76.setAlignment(QtCore.Qt.AlignCenter)
        self._cie76_form.addRow("", self._cie76)
        self._cie76_gb.setLayout(self._cie76_form)
        
        self._ciede2000_gb = QtWidgets.QGroupBox()
        self._ciede2000_gb.setTitle("\u0394E00 - CIEDE2000")
        self._ciede200_form = QtWidgets.QFormLayout()
        self._ciede2000 = QtWidgets.QLineEdit()
        self._ciede2000.setEnabled(False)
        self._ciede2000.setAlignment(QtCore.Qt.AlignCenter)
        self._ciede200_form.addRow("", self._ciede2000)
        self._ciede2000_gb.setLayout(self._ciede200_form)    

    def create_buttons(self):
        # properties
        colour_cyan = Config.instance().data["colour"]["rgb_cyan_colour"]
        colour_orange = Config.instance().data["colour"]["rgb_orange_colour"]
        colour_pink = Config.instance().data["colour"]["rgb_pink_colour"]
        size = QtCore.QSize(Config.instance().data["icon"]["icon_size"][0],Config.instance().data["icon"]["icon_size"][0])
        # calculate
        self._calculate_button = QtWidgets.QPushButton()
        self._calculate_button.setText("Calculate")
        self._calculate_button.setStyleSheet(f"background-color: {colour_cyan}; color: white")
        # zoom
        file_zoom_icon = Config.instance().data["icon"]["file_zoom_icon"]
        path_zoom_icon = os.path.join(*[Config.coolpi_dir, *file_zoom_icon])
        self._zoom_icon = QtGui.QIcon(path_zoom_icon)
        self._zoom_button = QtWidgets.QPushButton()
        self._zoom_button.setStyleSheet(f"background-color: {colour_orange}; color: white")
        self._zoom_button.setIcon(self._zoom_icon)
        self._zoom_button.setIconSize(size)
        self._zoom_button.setDisabled(True)
        # save
        file_save_icon = Config.instance().data["icon"]["file_save_icon"]
        path_save_icon = os.path.join(*[Config.coolpi_dir, *file_save_icon])
        self._save_button = SaveButton(path_save_icon, size, True)
        # clear
        self._clear_button = QtWidgets.QPushButton()
        self._clear_button.setText("Clear")
        self._clear_button.setStyleSheet(f"background-color: {colour_pink}; color: white")

    def activate_zoom_buttons(self):
        self._zoom_button.setDisabled(False)
        self._save_button.setDisabled(False)

    def desactivate_zoom_buttons(self):
        self._zoom_button.setDisabled(True)
        self._save_button.setDisabled(True)

    def add_items(self):  
        self._grid_layout = QtWidgets.QGridLayout()
        self._grid_layout.addWidget(self._sample_1, 0, 0, 2, 1)
        self._grid_layout.addWidget(self._sample_2, 2, 0, 2, 1)
        self._grid_layout.addWidget(self._cielab_diagram, 0, 1, 2, 3)
        self._grid_layout.addWidget(self._LAB1, 2, 1, 1, 2)
        self._grid_layout.addWidget(self._LAB2, 2, 3, 1, 2)
        self._grid_layout.addWidget(self._srgb1, 0, 4)
        self._grid_layout.addWidget(self._srgb2, 1, 4)
        self._grid_layout.addWidget(self._cie76_gb, 3, 1, 1, 2)
        self._grid_layout.addWidget(self._ciede2000_gb, 3, 3, 1, 2)        

        self._grid_layout.addWidget(self._calculate_button, 4, 0)
        self._grid_layout.addWidget(self._zoom_button, 4, 1)
        self._grid_layout.addWidget(self._save_button, 4, 2)
        self._grid_layout.addWidget(self._clear_button, 4, 3)
        # add logo
        #self._grid_layout.addWidget(self._indigo, 4, 4, QtCore.Qt.AlignRight)
        self._grid_layout.addWidget(self._coolpi, 4, 4, QtCore.Qt.AlignRight)

        self.setLayout(self._grid_layout)  

    def clear_labels(self):
        # groups
        list_groups = [self._sample_1, self._sample_2, self._LAB1, self._LAB2]
        for element in list_groups:
            element.clear_coordinates()
        # delta_e labels
        self._cie76.clear()
        self._ciede2000.clear()
        # default images
        self.update_rgb_figure(0,0,0, 0,0,0)
        file_default_image = Config.instance().data["plot"]["file_default_image"]
        path_default_image = os.path.join(*[Config.coolpi_dir, *file_default_image])
        self.update_cielab_plot(path_default_image)
        # desactivate buttons
        self.desactivate_zoom_buttons()
        
    def update_coordinates(self, new_coordinates):
        self._coordinates = new_coordinates # esto creo que no lo necesito
        for (key, value) in new_coordinates.items():
            if key =="CIELAB 1":
                self._LAB1.update_coordinates(value[0], value[1], value[2])
            if key =="CIELAB 2":
                self._LAB2.update_coordinates(value[0], value[1], value[2])

    def update_delta_values(self, cie76, ciede2000):
        self._cie76.setText(cie76)
        self._ciede2000.setText(ciede2000)

    def update_rgb_figure(self, r1,g1,b1, r2,g2,b2):
        self._srgb_image_1.fill(QtGui.QColor.fromRgb(r1, g1, b1))
        self._srgb_plot1_label.setPixmap(self._srgb_image_1)
        
        self._srgb_image_2.fill(QtGui.QColor.fromRgb(r2, g2, b2))
        self._srgb_plot2_label.setPixmap(self._srgb_image_2)

    def update_cielab_plot(self, path_figure):
        self._cielab_image = QtGui.QPixmap(path_figure)
        self._cielab_plot_label.setPixmap(self._cielab_image)

    def save_image(self):
        # save dialog
        save_dialog = QtWidgets.QFileDialog()
        plot_default_dir = os.path.join(*[os.getcwd(), *Config.instance().data["dir_path"]["plot_dir"]])
        save_path = save_dialog.getSaveFileName(self, "Save Current Plot", plot_default_dir, "Image files (*.png *.jpg)")
        path_file_png = save_path[0]
        if path_file_png != "": # avoid error press cancel button
            self._cielab_image.save(path_file_png)
            self.show_save_message()

    def get_pos_center(self):
        x_pos = int((self.pos().x() + self.frameGeometry().width())/2)
        y_pos = int((self.pos().y() + self.frameGeometry().height())/2)
        return x_pos, y_pos
    
    def show_warning_message(self, msg):
        warning = WarningMessageBox(self)
        x_pos, y_pos = self.get_pos_center()
        warning.setGeometry(x_pos, y_pos, Config.instance().data["main"]["message_screen_size"][0],Config.instance().data["main"]["message_screen_size"][1])
        warning.set_warning_message(msg)
        warning.exec() 
        
    def show_save_message(self):
        saved_message = SavedMessageBox("Figure saved successfully")
        x_pos, y_pos = self.get_pos_center()
        saved_message.setGeometry(x_pos, y_pos, Config.instance().data["main"]["message_screen_size"][0],Config.instance().data["main"]["message_screen_size"][1])
        saved_message.exec() # .show()

# SPC - Spectral Colour

class SPC(QtWidgets.QWidget):

    def __init__(self, parent = None):
        super().__init__()
        self.setWindowTitle(Config.instance().data["spc"]["title"])
        self.setFixedSize(Config.instance().data["spc"]["screen_size"][0], Config.instance().data["spc"]["screen_size"][1])

        self.create_items()
        self.add_items()

    def set_position(self, posx, posy):
        self.move(posx,posy)

    def create_items(self):
        self.create_coolpi_logo()
        self.create_buttons()
        self.desactivate_buttons()
        self.create_group_box()

    def create_coolpi_logo(self):
        file_logo_coolpi = Config.instance().data["logo"]["file_logo_coolpi"]
        path_logo_coolpi = os.path.join(*[Config.coolpi_dir, *file_logo_coolpi])
        self._coolpi = Logo("coolpi", path_logo_coolpi)

    def create_group_box(self):
        self._spc_input = SpectralGroupBox()
    
        self._xyz_gb = XYZGroupBox()
        self._xyY_gb = xyYGroupBox()
        self._lab_gb = LABGroupBox()

        self._spc_plot_gb = SpectralPlotGroupBox()
        self._srgb_gb = sRGBPlotGroupBox()
        self._srgb_gb.setMaximumWidth(140)

        self._coordinate_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._coordinate_splitter.addWidget(self._xyz_gb)
        self._coordinate_splitter.addWidget(self._xyY_gb)
        self._coordinate_splitter.addWidget(self._lab_gb)

        self._plot_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._plot_splitter.addWidget(self._spc_plot_gb)
        self._plot_splitter.addWidget(self._srgb_gb)

    def create_buttons(self):
        # properties
        colour_cyan = Config.instance().data["colour"]["rgb_cyan_colour"]
        colour_orange = Config.instance().data["colour"]["rgb_orange_colour"]
        colour_pink = Config.instance().data["colour"]["rgb_pink_colour"]
        size = QtCore.QSize(Config.instance().data["icon"]["icon_size"][0],Config.instance().data["icon"]["icon_size"][0])
        # load from JSON
        self._load_button = QtWidgets.QPushButton()
        self._load_button.setText("Load from JSON")
        self._load_button.setStyleSheet(f"background-color: {colour_cyan}; color: white")
        # zoom
        file_zoom_icon = Config.instance().data["icon"]["file_zoom_icon"]
        path_zoom_icon = os.path.join(*[Config.coolpi_dir, *file_zoom_icon])
        self._zoom_icon = QtGui.QIcon(path_zoom_icon)
        self._zoom_button = QtWidgets.QPushButton()
        self._zoom_button.setStyleSheet(f"background-color: {colour_orange}; color: white")
        self._zoom_button.setIcon(self._zoom_icon)
        self._zoom_button.setIconSize(size)
        # save
        file_save_icon = Config.instance().data["icon"]["file_save_icon"]
        path_save_icon = os.path.join(*[Config.coolpi_dir, *file_save_icon])
        self._save_button = SaveButton(path_save_icon, size, True)
        # clear
        self._clear_button = QtWidgets.QPushButton()
        self._clear_button.setText("Clear")
        self._clear_button.setStyleSheet(f"background-color: {colour_pink}; color: white")

    def desactivate_buttons(self):
        self._zoom_button.setEnabled(False)
        self._save_button.setEnabled(False)
        self._clear_button.setEnabled(False)

    def activate_save_zoom_buttons(self):
        self._zoom_button.setEnabled(True)
        self._save_button.setEnabled(True)
    
    def activate_clear_button(self):
        self._clear_button.setEnabled(True)

    def add_items(self):  
        self._grid_layout = QtWidgets.QGridLayout()
        self._grid_layout.addWidget(self._spc_input, 0, 0, 2, 1)
        self._grid_layout.addWidget(self._spc_plot_gb, 0, 1, 1, 3)
        self._grid_layout.addWidget(self._srgb_gb, 0, 4)
        self._grid_layout.addWidget(self._coordinate_splitter, 1, 1, 1, 4)
        self._grid_layout.addWidget(self._load_button, 2, 0)
        self._grid_layout.addWidget(self._zoom_button, 2, 1)
        self._grid_layout.addWidget(self._save_button, 2, 2)
        self._grid_layout.addWidget(self._clear_button, 2, 3)
        #self._grid_layout.addWidget(self._indigo, 2, 4, QtCore.Qt.AlignRight)
        self._grid_layout.addWidget(self._coolpi, 2, 4, QtCore.Qt.AlignRight)

        self.setLayout(self._grid_layout)  

    def load_from_json(self):
        keys = ["Sample_id", "Illuminant", "Observer", "nm_range", "nm_interval", "lambda_values"]
        load_dialog = QtWidgets.QFileDialog()
        json_default_dir = os.path.join(*[os.getcwd(), *Config.instance().data["dir_path"]["json_dir"]])
        load_path = load_dialog.getOpenFileName(self, "Load Spectral Sample", json_default_dir, "Json files (*.json *.JSON)")
        path_file_json = load_path[0]  
                
        if path_file_json != "":  # avoid error press cancel button
            with open(path_file_json, 'r') as json_file:
                json_data = json.load(json_file)
            # check json data
            omited_key = []
            for key in keys:
                if key not in json_data.keys():
                    omited_key.append(key)
                
            if omited_key!=[]:
                msg = f"Incomplete JSON spectral data: {omited_key}"
                self.show_warning_message(msg)
                self._json_spectral_data = None
            else:
                # check data
                self._json_spectral_data = json_data
        else:
            self._json_spectral_data = None

    def update_coordinates(self, new_coordinates):
        for (key, value) in new_coordinates.items():
            if key =="CIE XYZ":
                self._xyz_gb.update_coordinates(value[0], value[1], value[2])
            if key =="CIE xyY":
                self._xyY_gb.update_coordinates(value[0], value[1], value[2])
            if key =="CIELAB":
               self._lab_gb.update_coordinates(value[0], value[1], value[2])
            if key =="sRGB":
                self._srgb_gb.update_coordinates(value[0], value[1], value[2])

    def update_srgb_image(self, r, g, b):
        self._srgb_gb.update_figure(r, g, b)
    
    def clear_labels(self):
        # groups
        list_groups = [self._xyz_gb, self._xyY_gb, self._lab_gb, self._srgb_gb]
        for element in list_groups:
            element.clear_coordinates()
        # labels
        self._spc_input.clear_labels()
        # update figure
        self._srgb_gb.update_figure(0, 0, 0)
        file_default_image = Config.instance().data["plot"]["file_default_image"]
        path_default_image = os.path.join(*[Config.coolpi_dir, *file_default_image])
        self._spc_plot_gb.update_figure(path_default_image)
        # desactivate buttons
        self.desactivate_buttons()

    def get_pos_center(self):
        x_pos = int((self.pos().x() + self.frameGeometry().width())/2)
        y_pos = int((self.pos().y() + self.frameGeometry().height())/2)
        return x_pos, y_pos

    def save_image(self):
        save_dialog = QtWidgets.QFileDialog()
        plot_default_dir = os.path.join(*[os.getcwd(), *Config.instance().data["dir_path"]["plot_dir"]])
        save_path = save_dialog.getSaveFileName(self, "Save Spectral Plot", plot_default_dir, "Image files (*.png *.jpg)")
        path_file_png = save_path[0]
        if path_file_png != "": # avoid error press cancel button
            self._spc_plot_gb.save_figure(path_file_png)
            self.show_save_message()

    def show_save_message(self):
        saved_message = SavedMessageBox("Figure saved successfully")
        x_pos, y_pos = self.get_pos_center()
        saved_message.setGeometry(x_pos, y_pos, Config.instance().data["main"]["message_screen_size"][0],Config.instance().data["main"]["message_screen_size"][1])
        saved_message.exec() # .show()

    def show_warning_message(self, msg):
        warning = WarningMessageBox(self)
        x_pos, y_pos = self.get_pos_center()
        warning.setGeometry(x_pos, y_pos, Config.instance().data["main"]["message_screen_size"][0],Config.instance().data["main"]["message_screen_size"][1])
        warning.set_warning_message(msg)
        warning.exec() 

# CPT - Plot

class CPT(QtWidgets.QWidget):

    def __init__(self, parent = None):
        super().__init__()        
        self.setWindowTitle(Config.instance().data["cpt"]["title"])
        self.setFixedSize(Config.instance().data["cpt"]["screen_size"][0], Config.instance().data["cpt"]["screen_size"][1])
        
        self.create_items()
        self.add_items()

    def set_position(self, posx, posy):
        self.move(posx,posy)

    def create_items(self):
        #self.create_indigo_logo()
        self.create_coolpi_logo()
        self.create_group_box()
        self.create_buttons()

    def create_indigo_logo(self):
        file_logo_indigo = Config.instance().data["logo"]["file_logo_indigo"]
        path_logo_indigo = os.path.join(*[Config.coolpi_dir, *file_logo_indigo])
        self._indigo = Logo("Indigo", path_logo_indigo)

    def create_coolpi_logo(self):
        file_logo_coolpi = Config.instance().data["logo"]["file_logo_coolpi"]
        path_logo_coolpi = os.path.join(*[Config.coolpi_dir, *file_logo_coolpi])
        self._coolpi = Logo("coolpi", path_logo_coolpi)

    def create_group_box(self):
        self._input_gb = InputGroupBox()
        self._chromaticity_gb = ChromaticityDiagramGroupBox()
        self._cielab_gb = CielabPlotGroupBox()
        self._srgb_gb = sRGBPlotGroupBox()
        self._srgb_gb.setMaximumWidth(140)

    def update_coordinates(self, new_coordinates):
        for (key, value) in new_coordinates.items():
            if key =="CIE xyY":
                self._chromaticity_gb.update_coordinates(value[0], value[1], value[2])
            if key =="CIELAB":
               self._cielab_gb.update_coordinates(value[0], value[1], value[2])
            if key =="sRGB":
                self._srgb_gb.update_coordinates(value[0], value[1], value[2])
                
    def create_buttons(self):
        # properties
        colour_cyan = Config.instance().data["colour"]["rgb_cyan_colour"]
        colour_orange = Config.instance().data["colour"]["rgb_orange_colour"]
        size = QtCore.QSize(Config.instance().data["icon"]["icon_size"][0],Config.instance().data["icon"]["icon_size"][0])
        # plot
        self._plot_button = QtWidgets.QPushButton()
        self._plot_button.setText("Plot")
        
        self._plot_button.setStyleSheet(f"background-color: {colour_cyan}; color: white")
        # zoom
        file_zoom_icon = Config.instance().data["icon"]["file_zoom_icon"]
        path_zoom_icon = os.path.join(*[Config.coolpi_dir, *file_zoom_icon])
        self._zoom_icon = QtGui.QIcon(path_zoom_icon)

        self._zoom_button_cd = QtWidgets.QPushButton()
        self._zoom_button_cd.setStyleSheet(f"background-color: {colour_orange}; color: white")
        self._zoom_button_cd.setIcon(self._zoom_icon)
        self._zoom_button_cd.setIconSize(size)
        self._zoom_button_cd.setDisabled(True)

        self._zoom_button_cielab = QtWidgets.QPushButton()
        self._zoom_button_cielab.setStyleSheet(f"background-color: {colour_orange}; color: white")
        self._zoom_button_cielab.setIcon(self._zoom_icon)
        self._zoom_button_cielab.setIconSize(size)
        self._zoom_button_cielab.setDisabled(True)
        
        # save
        file_save_icon = Config.instance().data["icon"]["file_save_icon"]
        path_save_icon = os.path.join(*[Config.coolpi_dir, *file_save_icon])
        self._save_chromaticity_button = SaveButton(path_save_icon, size, True)
        self._save_cielab_button = SaveButton(path_save_icon, size, True)
        
        # group
        self._chromaticity_group_buttons = QtWidgets.QHBoxLayout()
        self._chromaticity_group_buttons.addWidget(self._zoom_button_cd)
        self._chromaticity_group_buttons.addWidget(self._save_chromaticity_button)

        self._cielab_group_buttons = QtWidgets.QHBoxLayout()
        self._cielab_group_buttons.addWidget(self._zoom_button_cielab)
        self._cielab_group_buttons.addWidget(self._save_cielab_button)

    def activate_zoom_buttons(self):
        self._zoom_button_cd.setDisabled(False)
        self._save_chromaticity_button.setDisabled(False)
        self._zoom_button_cielab.setDisabled(False)
        self._save_cielab_button.setDisabled(False)

    def add_items(self):
        self._grid_layout = QtWidgets.QGridLayout()
        self._grid_layout.addWidget(self._input_gb, 0, 0)#, 0, 1)
        self._grid_layout.addWidget(self._chromaticity_gb, 0, 1)# 0, 1)
        self._grid_layout.addWidget(self._cielab_gb, 0, 2)# 0, 1)
        self._grid_layout.addWidget(self._srgb_gb, 0, 3)# 0, 1)
        
        self._grid_layout.addWidget(self._plot_button, 1,0)
        self._grid_layout.addItem(self._chromaticity_group_buttons, 1, 1, QtCore.Qt.AlignRight)
        self._grid_layout.addItem(self._cielab_group_buttons, 1, 2, QtCore.Qt.AlignRight)
        #self._grid_layout.addWidget(self._indigo, 1, 3, QtCore.Qt.AlignRight)
        self._grid_layout.addWidget(self._coolpi, 1, 3, QtCore.Qt.AlignRight)
        
        self.setLayout(self._grid_layout)  

    def update_srgb_image(self, r, g, b):
        self._srgb_gb.update_figure(r, g, b)
    
    def update_default_srgb_image(self):
        self._srgb_gb.update_default_figure()
    
    def update_chromaticity_plot(self, path_figure):
        self._chromaticity_gb.update_figure(path_figure)

    def update_cielab_plot(self, path_figure):
        self._cielab_gb.update_figure(path_figure)

    def save_image(self, plot_name):
        # save dialog
        save_dialog = QtWidgets.QFileDialog()
        plot_default_dir = os.path.join(*[os.getcwd(), *Config.instance().data["dir_path"]["plot_dir"]])
        save_path = save_dialog.getSaveFileName(self, "Save Current Plot", plot_default_dir, "Image files (*.png *.jpg)")
        path_file_png = save_path[0]

        if path_file_png != "": # avoid error press cancel button
            if plot_name == "Chromaticity":
                self._chromaticity_gb.save_figure(path_file_png)
            elif plot_name == "Cielab":
                self._cielab_gb.save_figure(path_file_png)
            self.show_save_message()

    def get_pos_center(self):
        x_pos = int((self.pos().x() + self.frameGeometry().width())/2)
        y_pos = int((self.pos().y() + self.frameGeometry().height())/2)
        return x_pos, y_pos

    def show_save_message(self):
        saved_message = SavedMessageBox("Figure saved successfully")
        x_pos, y_pos = self.get_pos_center()
        saved_message.setGeometry(x_pos, y_pos, Config.instance().data["main"]["message_screen_size"][0],Config.instance().data["main"]["message_screen_size"][1])
        saved_message.exec() # .show()

    def show_warning_message(self, msg):
        warning = WarningMessageBox(self)
        x_pos, y_pos = self.get_pos_center()
        warning.setGeometry(x_pos, y_pos, Config.instance().data["main"]["message_screen_size"][0],Config.instance().data["main"]["message_screen_size"][1])
        warning.set_warning_message(msg)
        warning.exec() 

# SPD - Illuminant SPD Inspector

class SPD(QtWidgets.QWidget):

    def __init__(self, parent = None):
        super().__init__()
        self.setWindowTitle(Config.instance().data["spd"]["title"])
        self.setFixedSize(Config.instance().data["spd"]["screen_size"][0], Config.instance().data["spd"]["screen_size"][1])

        self.create_items()
        self.add_items()

    def set_position(self, posx, posy):
        self.move(posx,posy)

    def create_items(self):
        self.create_coolpi_logo()
        self.create_combo_box()
        self.create_buttons()
        self.desactivate_buttons()
        self.create_group_box()

    def create_coolpi_logo(self):
        file_logo_coolpi = Config.instance().data["logo"]["file_logo_coolpi"]
        path_logo_coolpi = os.path.join(*[Config.coolpi_dir, *file_logo_coolpi])
        self._coolpi = Logo("coolpi", path_logo_coolpi)
        
    def create_combo_box(self):
        self._observer_label = QtWidgets.QLabel("Observer")
        self._combo_observer = QtWidgets.QComboBox()
        self._combo_observer.addItems(Config.instance().data["spc"]["observers"])
        self._combo_observer.setCurrentText("2")
        self._combo_observer.setEnabled(True)
        self._observer_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._observer_splitter.addWidget(self._observer_label)
        self._observer_splitter.addWidget(self._combo_observer)

    def create_group_box(self):
        self._spd_input = InputIlluminantGroupBox()
        self._spd_input.setMaximumWidth(300)
        
        self._spd_data = SPDGroupBox()
        self._spd_data.setMaximumWidth(300)
        
        # Theoretical WhitePoint
        self._theoretical_label = QtWidgets.QLabel("Theoretical WhitePoint")
        self._xyz_t_gb = XYZGroupBox()
        self._xyY_t_gb = xyYGroupBox()
        self._theoretical_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._theoretical_splitter.addWidget(self._xyz_t_gb)
        self._theoretical_splitter.addWidget(self._xyY_t_gb)
        
        # Computed WhitePoint
        self._computed_label = QtWidgets.QLabel("Computed WhitePoint")
        self._xyz_c_gb = XYZGroupBox()
        self._xyY_c_gb = xyYGroupBox()
        self._computed_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._computed_splitter.addWidget(self._xyz_c_gb)
        self._computed_splitter.addWidget(self._xyY_c_gb)
        
        # Illuminant Plot
        self._spd_plot_gb = IlluminantPlotGroupBox() # Illuminant Plot

    def connect_radio_buttons(self):
        self._spd_input._cie_radio_button.toggled.connect(lambda: self.radio_button_checked(self._spd_input._cie_radio_button)) 
        self._spd_input._cct_radio_button.toggled.connect(lambda: self.radio_button_checked(self._spd_input._cct_radio_button))
        self._spd_input._user_radio_button.toggled.connect(lambda: self.radio_button_checked(self._spd_input._user_radio_button))

    def radio_button_checked(self, button):
        if button.text() == "CIE":
            self.clear_labels()
            self._spd_input._combo_illuminant.setEnabled(True)
            self._spd_input._cct_edit.setEnabled(False)
            self._spd_input._user_name_edit.setEnabled(False)
            self._spd_input.desactivate_load_button()
        elif button.text() == "CCT":
            self.clear_labels()
            self._spd_input._combo_illuminant.setCurrentText("D65") # default
            self._spd_input._combo_illuminant.setEnabled(False)
            self._spd_input._cct_edit.setEnabled(True)
            self._spd_input._user_name_edit.setEnabled(False)
            self._spd_input.desactivate_load_button()
        elif button.text() == "Measured":
            self.clear_labels()
            self._spd_input._combo_illuminant.setCurrentText("D65")
            self._spd_input._combo_illuminant.setEnabled(False)
            self._spd_input._cct_edit.setEnabled(False)
            self._spd_input.activate_load_button()
            self._spd_input._user_name_edit.setEnabled(True)
            
    def create_buttons(self):
        # properties
        colour_cyan = Config.instance().data["colour"]["rgb_cyan_colour"]
        colour_orange = Config.instance().data["colour"]["rgb_orange_colour"]
        colour_pink = Config.instance().data["colour"]["rgb_pink_colour"]

        size = QtCore.QSize(Config.instance().data["icon"]["icon_size"][0],Config.instance().data["icon"]["icon_size"][0])
        
        # plot
        self._plot_button = QtWidgets.QPushButton()
        self._plot_button.setText("Plot")
        self._plot_button.setStyleSheet(f"background-color: {colour_cyan}; color: white")
        self._plot_button.setEnabled(True) # default
        # zoom
        file_zoom_icon = Config.instance().data["icon"]["file_zoom_icon"]
        path_zoom_icon = os.path.join(*[Config.coolpi_dir, *file_zoom_icon])
        self._zoom_icon = QtGui.QIcon(path_zoom_icon)
        self._zoom_button = QtWidgets.QPushButton()
        self._zoom_button.setStyleSheet(f"background-color: {colour_orange}; color: white")
        self._zoom_button.setIcon(self._zoom_icon)
        self._zoom_button.setIconSize(size)
        # save
        file_save_icon = Config.instance().data["icon"]["file_save_icon"]
        path_save_icon = os.path.join(*[Config.coolpi_dir, *file_save_icon])
        self._save_button = SaveButton(path_save_icon, size, True)
        
        # clear
        self._clear_button = QtWidgets.QPushButton()
        self._clear_button.setText("Clear")
        self._clear_button.setStyleSheet(f"background-color: {colour_pink}; color: white")

    def desactivate_buttons(self):
        self._zoom_button.setEnabled(False)
        self._save_button.setEnabled(False)
        self._clear_button.setEnabled(False)

    def activate_save_zoom_buttons(self):
        self._zoom_button.setEnabled(True)
        self._save_button.setEnabled(True)
    
    def activate_clear_button(self):
        self._clear_button.setEnabled(True)

    def add_items(self):  
        self._grid_layout = QtWidgets.QGridLayout()
        self._grid_layout.addWidget(self._spd_input, 0, 0, 2, 1)
        self._grid_layout.addWidget(self._spd_data, 2, 0, 5, 1)
        self._grid_layout.addWidget(self._spd_plot_gb, 0, 1, 2, 4)    
        self._grid_layout.addWidget(self._observer_splitter, 2, 1, 1, 4)
        self._grid_layout.addWidget(self._theoretical_label, 3, 1, 1, 4)
        self._grid_layout.addWidget(self._theoretical_splitter, 4, 1, 1, 4)
        self._grid_layout.addWidget(self._computed_label, 5, 1, 1, 4)
        self._grid_layout.addWidget(self._computed_splitter, 6, 1, 1, 4)
        self._grid_layout.addWidget(self._plot_button, 7, 0)
        self._grid_layout.addWidget(self._zoom_button, 7, 1)
        self._grid_layout.addWidget(self._save_button, 7, 2)
        self._grid_layout.addWidget(self._clear_button, 7, 3)
        #self._grid_layout.addWidget(self._indigo, 7, 4, QtCore.Qt.AlignRight)
        self._grid_layout.addWidget(self._coolpi, 7, 4, QtCore.Qt.AlignRight)

        self.setLayout(self._grid_layout)  

    def update_coordinates(self, new_coordinates):
        for (key, value) in new_coordinates.items():
            if key == "theoretical":
                for (key2, value2) in value.items():
                    if key2 == "CIE XYZ":
                        self._xyz_t_gb.update_coordinates(value2[0], value2[1], value2[2])
                    if key2 =="CIE xyY":
                        self._xyY_t_gb.update_coordinates(value2[0], value2[1], value2[2])
            if key == "computed":
                for (key2, value2) in value.items():
                    if key2 == "CIE XYZ":
                        self._xyz_c_gb.update_coordinates(value2[0], value2[1], value2[2])
                    if key2 =="CIE xyY":
                        self._xyY_c_gb.update_coordinates(value2[0], value2[1], value2[2])

    def clear_labels(self):
        # default value
        self._combo_observer.setCurrentText("2")
        self._spd_data.clear_labels()
        self._spd_input.clear_labels()
        # default figure
        self._spd_plot_gb.update_figure(None)
        
        # groups
        list_groups = [self._xyz_t_gb, self._xyY_t_gb, self._xyz_c_gb, self._xyY_c_gb]
        for element in list_groups:
            element.clear_coordinates()

        # desactivate buttons
        self.desactivate_buttons()

    def get_pos_center(self):
        x_pos = int((self.pos().x() + self.frameGeometry().width())/2)
        y_pos = int((self.pos().y() + self.frameGeometry().height())/2)
        return x_pos, y_pos

    def save_image(self):
        save_dialog = QtWidgets.QFileDialog()
        plot_default_dir = os.path.join(*[os.getcwd(), *Config.instance().data["dir_path"]["plot_dir"]])
        save_path = save_dialog.getSaveFileName(self, "Save Spectral Plot", plot_default_dir, "Image files (*.png *.jpg)")
        path_file_png = save_path[0]
        if path_file_png != "": # avoid error press cancel button
            self._spd_plot_gb.save_figure(path_file_png)
            self.show_save_message()

    def show_save_message(self):
        saved_message = SavedMessageBox("Figure saved successfully")
        x_pos, y_pos = self.get_pos_center()
        saved_message.setGeometry(x_pos, y_pos, Config.instance().data["main"]["message_screen_size"][0],Config.instance().data["main"]["message_screen_size"][1])
        saved_message.exec() # .show()

    def show_warning_message(self, msg):
        warning = WarningMessageBox(self)
        x_pos, y_pos = self.get_pos_center()
        warning.setGeometry(x_pos, y_pos, Config.instance().data["main"]["message_screen_size"][0],Config.instance().data["main"]["message_screen_size"][1])
        warning.set_warning_message(msg)
        warning.exec() 

# CCI - ColourChecker Inspector

class CCI(QtWidgets.QWidget):

    def __init__(self, parent = None):
        super().__init__()
        self.setWindowTitle(Config.instance().data["cci"]["title"])
        self.setFixedSize(Config.instance().data["cci"]["screen_size"][0], Config.instance().data["cci"]["screen_size"][1])

        self.create_items()
        self.add_items()
        self.connect_radio_buttons()

    def set_position(self, posx, posy):
        self.move(posx,posy)
    
    def create_items(self):
        self.create_coolpi_logo()
        self.create_group_box()
        self.create_table()
        self.create_buttons()
        self.desactivate_buttons() # default

    def create_coolpi_logo(self):
        file_logo_coolpi = Config.instance().data["logo"]["file_logo_coolpi"]
        path_logo_coolpi = os.path.join(*[Config.coolpi_dir, *file_logo_coolpi])
        self._coolpi = Logo("coolpi", path_logo_coolpi)
        
    def create_group_box(self):
        self._colourchecker_gb = InputChartGroupBox()

        self._table_container_gb = QtWidgets.QGroupBox()
        self._table_container_gb.setTitle("Spectral data")

        self._xyz_gb = XYZGroupBox()
        self._xyY_gb = xyYGroupBox()
        self._lab_gb = LABGroupBox()
        self._srgb_gb = sRGBPlotGroupBox()
        self._srgb_gb.setMaximumWidth(120)
        self._spc_plot_gb = SpectralPlotGroupBox()
        
        self._coordinate_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._coordinate_splitter.addWidget(self._xyz_gb)
        self._coordinate_splitter.addWidget(self._xyY_gb)
        self._coordinate_splitter.addWidget(self._lab_gb)
        self._coordinate_splitter.addWidget(self._srgb_gb)

    def connect_radio_buttons(self):
        self._colourchecker_gb._chart_resources_radio_button.toggled.connect(lambda: self.radio_button_checked(self._colourchecker_gb._chart_resources_radio_button))        
        self._colourchecker_gb._chart_measured_radio_button.toggled.connect(lambda: self.radio_button_checked(self._colourchecker_gb._chart_measured_radio_button)) 
        
    def radio_button_checked(self, button):
        if button.text() == "From Resources":
            self.clear_labels()
            self._colourchecker_gb.deactivate_load_button()
            self._colourchecker_gb._combo_colourchecker.setDisabled(False)

        elif button.text() == "Measured":
            self.clear_labels()
            self._colourchecker_gb._combo_colourchecker.setDisabled(True)
            self._colourchecker_gb.activate_load_button()
    
    def create_table(self):
        self._spc_table = QtWidgets.QTableWidget()
        #self._spc_table.setEnabled(False) # read only

        self._spc_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self._spc_table.setSelectionMode(QtWidgets.QTableWidget.SingleSelection) # allowd only a one item
        self._spc_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows) # selected row

        self._table_qh = QtWidgets.QHBoxLayout()
        self._table_qh.addWidget(self._spc_table)
        self._table_container_gb.setLayout(self._table_qh)

    def fill_table(self, patches_dict):
        self._spc_table.clear()
        num_patches = len(patches_dict.keys())
        colum_labels = ["patch_id"]
 
        nm_range = [int(value) for value in self._colourchecker_gb._metadata_table.item(5,1).text().split(",")]
        nm_interval = int(self._colourchecker_gb._metadata_table.item(6,1).text())
        
        nm_range_label = [str(x) for x in range(nm_range[0], (nm_range[1] + nm_interval) ,nm_interval)]
        colum_labels.extend(nm_range_label)

        self._spc_table.setColumnCount(len(colum_labels))
        self._spc_table.setRowCount(num_patches)
        self._spc_table.setHorizontalHeaderLabels(colum_labels)

        r,g,b = Config.instance().data["cci"]["background_sample_id_colum"]

        row = 0
        for sample_id, lambda_values in patches_dict.items():
            sample_id_item = QtWidgets.QTableWidgetItem(sample_id)
            sample_id_item.setTextAlignment(QtCore.Qt.AlignHCenter)
            sample_id_item.setBackground(QtGui.QColor(r,g,b))
            self._spc_table.setItem(row, 0, sample_id_item)
            #self._spc_table.setItem(row, 0, QtWidgets.QTableWidgetItem(sample_id)) #.setTextAlignment(QtCore.Qt.AlignHCenter)) # setTextAlign not working
            for j in range(0, len(lambda_values)):
                spc_value = float(lambda_values[j])
                spc_value_item = QtWidgets.QTableWidgetItem(f"{spc_value:4.4f}")
                spc_value_item.setTextAlignment(QtCore.Qt.AlignHCenter)
                self._spc_table.setItem(row, j+1, spc_value_item)
                #self._spc_table.setItem(row, j+1, QtWidgets.QTableWidgetItem(f"{spc_value:4.4f}")) #.setTextAlignment(QtCore.Qt.AlignCenter)) #) # row, column, item
            row += 1

        self._spc_table.resizeColumnsToContents()
        self._spc_table.resizeRowsToContents() 

    def create_buttons(self):
        # properties
        size = QtCore.QSize(Config.instance().data["icon"]["icon_size"][0],Config.instance().data["icon"]["icon_size"][0])
        colour_orange = Config.instance().data["colour"]["rgb_orange_colour"]
        # zoom
        file_zoom_icon = Config.instance().data["icon"]["file_zoom_icon"]
        path_zoom_icon = os.path.join(*[Config.coolpi_dir, *file_zoom_icon])
        self._zoom_icon = QtGui.QIcon(path_zoom_icon)
        self._zoom_button= QtWidgets.QPushButton()
        self._zoom_button.setStyleSheet(f"background-color: {colour_orange}; color: white")
        self._zoom_button.setIcon(self._zoom_icon)
        self._zoom_button.setIconSize(size)
        # save
        file_save_icon = Config.instance().data["icon"]["file_save_icon"]
        path_save_icon = os.path.join(*[Config.coolpi_dir, *file_save_icon])
        self._save_button = SaveButton(path_save_icon, size, False)
        # group
        self._group_buttons = QtWidgets.QHBoxLayout()
        self._group_buttons.addWidget(self._zoom_button)
        self._group_buttons.addWidget(self._save_button)

    def desactivate_buttons(self):
        self._zoom_button.setDisabled(True)
        self._save_button.setDisabled(True)
    
    def activate_buttons(self):
        self._zoom_button.setDisabled(False)
        self._save_button.setDisabled(False)

    def add_items(self):
        self._grid_layout = QtWidgets.QGridLayout()
        self._grid_layout.addWidget(self._colourchecker_gb, 0, 0)#, 0, 1)
        self._grid_layout.addWidget(self._spc_plot_gb, 1, 0)#, 0, 1)
        self._grid_layout.addWidget(self._table_container_gb, 0, 2)
        self._grid_layout.addWidget(self._coordinate_splitter, 1, 2)
        self._grid_layout.addItem(self._group_buttons, 2, 0)
        # add indigo logo
        #self._grid_layout.addWidget(self._indigo, 2, 2, QtCore.Qt.AlignRight)
        self._grid_layout.addWidget(self._coolpi, 2, 2, QtCore.Qt.AlignRight)

        self.setLayout(self._grid_layout)  

    def save_image(self):
        # save dialog
        save_dialog = QtWidgets.QFileDialog()
        plot_default_dir = os.path.join(*[os.getcwd(), *Config.instance().data["dir_path"]["plot_dir"]])
        save_path = save_dialog.getSaveFileName(self, "Save Current Plot", plot_default_dir, "Image files (*.png *.jpg)")
        path_file_png = save_path[0]
        if path_file_png != "": # avoid error press cancel button
            self._spc_plot_gb.save_figure(path_file_png)
            self.show_save_message()

    def show_save_message(self):
        saved_message = SavedMessageBox("Figure saved successfully")
        x_pos, y_pos = self.get_pos_center()
        saved_message.setGeometry(x_pos, y_pos, Config.instance().data["main"]["message_screen_size"][0],Config.instance().data["main"]["message_screen_size"][1])
        saved_message.exec() # .show()

    def get_pos_center(self):
        x_pos = int((self.pos().x() + self.frameGeometry().width())/2)
        y_pos = int((self.pos().y() + self.frameGeometry().height())/2)
        return x_pos, y_pos

    def show_warning_message(self, msg):
        warning = WarningMessageBox(self)
        x_pos, y_pos = self.get_pos_center()
        warning.setGeometry(x_pos, y_pos, Config.instance().data["main"]["message_screen_size"][0],Config.instance().data["main"]["message_screen_size"][1])
        warning.set_warning_message(msg)
        warning.exec() 
    
    def update_label_checker_name(self, label_text):
        self._colourchecker_gb._chart_measured_name_edit.setText(str(label_text))

    def update_coordinates(self, new_coordinates):
        for (key, value) in new_coordinates.items():
            if key =="CIE XYZ":
                self._xyz_gb.update_coordinates(value[0], value[1], value[2])
            if key =="CIE xyY":
                self._xyY_gb.update_coordinates(value[0], value[1], value[2])
            if key =="CIELAB":
               self._lab_gb.update_coordinates(value[0], value[1], value[2])
            if key =="sRGB":
                self._srgb_gb.update_coordinates(value[0], value[1], value[2])

    def update_srgb_image(self, r, g, b):
        self._srgb_gb.update_figure(r, g, b)

    def load_from_json(self):        
        load_dialog = QtWidgets.QFileDialog()
        json_default_dir = os.path.join(*[os.getcwd(), *Config.instance().data["dir_path"]["json_dir"]])
        load_path = load_dialog.getOpenFileName(self, "Load ColourChecher Reflectance", json_default_dir, "Json files (*.json *.JSON)")
        path_file_json = load_path[0]
        
        keys = ["NameColorChart", "Instrument", "Measurement Date", "Illuminant", "Observer", "nm_range", "nm_interval"]
                
        if path_file_json != "":  # avoid error press cancel button
            with open(path_file_json, 'r') as json_file:
                json_data = json.load(json_file)
            # check json data
            omited_key = []
            for key in keys:
                if key not in json_data.keys():
                    omited_key.append(key)
                
            if omited_key!=[]:
                msg = f"Incomplete JSON reflectance data: {omited_key}"
                self.show_warning_message(msg)
                self._json_spectral_data = None
            else:
                # check data
                self._json_spectral_data = json_data
        else:
            self._json_spectral_data = None
        
    def clear_labels(self):
        self._colourchecker_gb.clear_labels()
        self._spc_table.clear()
        self._spc_plot_gb.update_figure(None)
        self._xyz_gb.clear_coordinates()
        self._xyY_gb.clear_coordinates()
        self._lab_gb.clear_coordinates()
        self._srgb_gb.clear_coordinates()
        self._srgb_gb.update_default_figure()

        index = self._colourchecker_gb._combo_colourchecker.findText("None") 
        self._colourchecker_gb._combo_colourchecker.setCurrentIndex(index)

# RCIP - RAW Colour Image Processing 

class RCIP(QtWidgets.QWidget):

    def __init__(self, parent = None):
        super().__init__()
        self.setWindowTitle(Config.instance().data["rcip"]["title"])
        self.setFixedSize(Config.instance().data["rcip"]["screen_size"][0], Config.instance().data["rcip"]["screen_size"][1])

        self.create_items()
        self.add_items()

    def set_position(self, posx, posy):
        self.move(posx,posy)

    def create_items(self):
        self.create_coolpi_logo()
        self.create_group_box()
        self.create_buttons()
        self.connect_radio_buttons()

    def create_coolpi_logo(self):
        file_logo_coolpi = Config.instance().data["logo"]["file_logo_coolpi"]
        path_logo_coolpi = os.path.join(*[Config.coolpi_dir, *file_logo_coolpi])
        self._coolpi = Logo("coolpi", path_logo_coolpi)
        
    def create_group_box(self):
        self._image_gp = ImageViewGroupBox()
        self._wb_gain_gb = WhiteBalanceFactorsGroupBox()
        self._rgb_to_xyz_gb = RGBToXYZMatrixGroupBox()
        self._path_gp = PathGroupBox()

    def deactivate_display_button(self):
        colour_grey = Config.instance().data["colour"]["rgb_very_light_grey"]
        self._plot_button.setStyleSheet(f"background-color: {colour_grey}; color: white")
        self._plot_button.setEnabled(False) # default

    def activate_display_button(self):
        colour_cyan = Config.instance().data["colour"]["rgb_cyan_colour"]
        self._plot_button.setStyleSheet(f"background-color: {colour_cyan}; color: white")
        self._plot_button.setEnabled(True) # default

    def deactivate_export_button(self):
        colour_grey = Config.instance().data["colour"]["rgb_very_light_grey"]
        self._export_button.setStyleSheet(f"background-color: {colour_grey}; color: white")
        self._export_button.setEnabled(False) # default

    def activate_export_button(self):
        colour_orange = Config.instance().data["colour"]["rgb_orange_colour"]
        self._export_button.setStyleSheet(f"background-color: {colour_orange}; color: white")
        self._export_button.setEnabled(True) # default

    def create_buttons(self):
        # properties
        colour_grey = Config.instance().data["colour"]["rgb_very_light_grey"]
        colour_cyan = Config.instance().data["colour"]["rgb_cyan_colour"]
        colour_orange = Config.instance().data["colour"]["rgb_orange_colour"]
        colour_pink = Config.instance().data["colour"]["rgb_pink_colour"]
        size = QtCore.QSize(Config.instance().data["icon"]["icon_size"][0],Config.instance().data["icon"]["icon_size"][0])
        
        # load image
        self._load_button = QtWidgets.QPushButton()
        self._load_button.setText("Load Image")
        self._load_button.setStyleSheet(f"background-color: {colour_cyan}; color: white")
        self._load_button.setEnabled(True) # default    

        # display
        self._plot_button = QtWidgets.QPushButton()
        self._plot_button.setText("Process Image")
        self._plot_button.setStyleSheet(f"background-color: {colour_grey}; color: white")
        self._plot_button.setEnabled(False) # default

        # export
        self._export_button = QtWidgets.QPushButton()
        self._export_button.setText("Export Image")
        self._export_button.setStyleSheet(f"background-color: {colour_grey}; color: white")
        self._export_button.setEnabled(False) # default

        # clear
        self._clear_button = QtWidgets.QPushButton()
        self._clear_button.setText("Clear")
        self._clear_button.setStyleSheet(f"background-color: {colour_pink}; color: white")
        self._load_button.setEnabled(True) # default    
    
    def connect_radio_buttons(self):
        self._rgb_to_xyz_gb._auto_radio_button.toggled.connect(lambda: self.radio_button_checked(self._rgb_to_xyz_gb._auto_radio_button)) 
        self._rgb_to_xyz_gb._computed_radio_button.toggled.connect(lambda: self.radio_button_checked(self._rgb_to_xyz_gb._computed_radio_button))
        self._wb_gain_gb._camera_radio_button.toggled.connect(lambda: self.radio_button_checked(self._wb_gain_gb._camera_radio_button))
        self._wb_gain_gb._daylight_radio_button.toggled.connect(lambda: self.radio_button_checked(self._wb_gain_gb._daylight_radio_button))
        self._wb_gain_gb._custom_radio_button.toggled.connect(lambda: self.radio_button_checked(self._wb_gain_gb._custom_radio_button))

        #self._wb_gain_gb._none_radio_button.isChecked()

    def radio_button_checked(self, button):
        if button.text() == "Auto":
            self._rgb_to_xyz_gb.desactivate_labels()
            self._rgb_to_xyz_gb.desactivate_load_button()
        elif button.text() == "Computed":
            self._rgb_to_xyz_gb.clear_labels()
            self._rgb_to_xyz_gb.activate_labels()
            self._rgb_to_xyz_gb.activate_load_button()

        elif button.text() == "Camera":
            self._wb_gain_gb.clear_labels()
            self._wb_gain_gb.desactivate_labels()
        
        elif button.text() == "Daylight":
            self._wb_gain_gb.clear_labels()
            self._wb_gain_gb.desactivate_labels()

        elif button.text() == "Custom":
            self._wb_gain_gb.clear_labels()
            self._wb_gain_gb.activate_labels()

    def add_items(self):
        self._grid_layout = QtWidgets.QGridLayout()
        self._grid_layout.addWidget(self._wb_gain_gb, 0, 0, 2, 1)
        self._grid_layout.addWidget(self._rgb_to_xyz_gb, 2, 0, 2, 1)

        self._grid_layout.addWidget(self._image_gp, 0, 1, 5, 4)
        self._grid_layout.addWidget(self._path_gp, 5, 1, 1, 4)

        # buttons
        self._grid_layout.addWidget(self._load_button, 6, 0)
        self._grid_layout.addWidget(self._plot_button, 6, 1)
        self._grid_layout.addWidget(self._export_button, 6, 2)
        self._grid_layout.addWidget(self._clear_button, 6, 3)
        # add logo
        #self._grid_layout.addWidget(self._indigo, 5, 4, QtCore.Qt.AlignRight)
        self._grid_layout.addWidget(self._coolpi, 6, 4, QtCore.Qt.AlignRight)
        self.setLayout(self._grid_layout)

    def clear_labels(self):   
        #self._output_image_gb.set_init_state()   
        self._image_gp.update_figure(None)
        self._rgb_to_xyz_gb.set_init_state()
        self._wb_gain_gb.set_init_state()
        #self._output_path_gp.set_init_state()
        self.deactivate_display_button()
        self.deactivate_export_button()

    def get_image_path(self):
        load_dialog = QtWidgets.QFileDialog()
        img_default_dir = os.path.join(*[os.getcwd(), *Config.instance().data["dir_path"]["img_dir"]])
        load_path = load_dialog.getOpenFileName(self, "Load RAW Image", img_default_dir, "IMG files (*.NEF *.nef .CR2 .cr2 .RAF .raf .X3F .x3f .DNG .dng)")
        path_file_img = load_path[0]  

        if path_file_img != "": 
            self._path_image_file = path_file_img
        else:
            self._path_image_file = None

    def get_export_image_path(self):
        save_dialog = QtWidgets.QFileDialog()
        img_default_dir = os.path.join(*[os.getcwd(), *Config.instance().data["dir_path"]["img_dir"]])
        save_path = save_dialog.getSaveFileName(self, "Export Image", img_default_dir, "IMG files (*.JPG *.jpg *.JPEG *.jpeg *.PNG *.png *.TIF *.tif)")
        path_file = save_path[0]  

        if path_file != "": # avoid error
            self._output_path_image_file = path_file
        else:
            self._output_path_image_file = None  

    def show_save_message(self, msg):
        saved_message = SavedMessageBox(msg)
        x_pos, y_pos = self.get_pos_center()
        saved_message.setGeometry(x_pos, y_pos, Config.instance().data["main"]["message_screen_size"][0],Config.instance().data["main"]["message_screen_size"][1])
        saved_message.exec() # .show()

    def get_pos_center(self):
        x_pos = int((self.pos().x() + self.frameGeometry().width())/2)
        y_pos = int((self.pos().y() + self.frameGeometry().height())/2)
        return x_pos, y_pos

    def show_warning_message(self, msg):
        warning = WarningMessageBox(self)
        x_pos, y_pos = self.get_pos_center()
        warning.setGeometry(x_pos, y_pos, Config.instance().data["main"]["message_screen_size"][0],Config.instance().data["main"]["message_screen_size"][1])
        warning.set_warning_message(msg)
        warning.exec() 

class PathGroupBox(QtWidgets.QGroupBox):    
    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("Path Image")
        
        self.create_labels()
        self.create_default_container()
        self.setLayout(self._container)
        self.set_init_state()

    def set_init_state(self):
        self.clear_labels()
        self._path_raw_edit.setEnabled(False)
        self._path_output_edit.setEnabled(False)
    
    def create_labels(self):
        self._path_raw_label = QtWidgets.QLabel("RAW Image: ")
        self._path_raw_edit = QtWidgets.QLineEdit()
        self._path_raw_edit.setAlignment(QtCore.Qt.AlignLeft)
        self._path_output_label = QtWidgets.QLabel("Output Image: ")
        self._path_output_edit = QtWidgets.QLineEdit()
        self._path_output_edit.setAlignment(QtCore.Qt.AlignLeft)

    def create_default_container(self):
        self._container = QtWidgets.QGridLayout()
        self._container.addWidget(self._path_raw_label, 0, 0)
        self._container.addWidget(self._path_raw_edit, 0, 1)
        self._container.addWidget(self._path_output_label, 1, 0)
        self._container.addWidget(self._path_output_edit, 1, 1)

    def clear_labels(self):
        self._path_raw_edit.clear()
        self._path_output_edit.clear()
        
    def update_raw_path_label(self, path_raw):
        self._path_raw_edit.setText(path_raw)

    def update_output_path_label(self, output_path):
        self._path_output_edit.setText(output_path)


class WhiteBalanceFactorsGroupBox(QtWidgets.QGroupBox):
    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("White Balance Multipliers")
    
        self.create_items()
        self.setLayout(self._container)
        self.set_init_state()

    def create_items(self):
        self.create_radio_buttons()
        self.create_apply_button()
        self.create_labels()
        self.create_default_container()
        
    def set_init_state(self):
        self.clear_labels()
        self._camera_radio_button.setChecked(True)
        self.desactivate_radio_buttons()
        self.desactivate_labels()

    def create_radio_buttons(self):
        self._camera_radio_button = QtWidgets.QRadioButton()
        self._camera_radio_button.setText("Camera")
        self._daylight_radio_button = QtWidgets.QRadioButton()
        self._daylight_radio_button.setText("Daylight")
        self._custom_radio_button = QtWidgets.QRadioButton()
        self._custom_radio_button.setText("Custom")

    def activate_radio_buttons(self):
        list_radio_buttons = [self._camera_radio_button, self._daylight_radio_button, self._custom_radio_button]
        for radio_button in list_radio_buttons:
            radio_button.setEnabled(True)

    def desactivate_radio_buttons(self):
        list_radio_buttons = [self._camera_radio_button, self._daylight_radio_button, self._custom_radio_button]
        for radio_button in list_radio_buttons:
            radio_button.setEnabled(False)

    def create_apply_button(self):
        colour_grey = Config.instance().data["colour"]["rgb_very_light_grey"]
        self._apply_wb_button = QtWidgets.QPushButton()
        self._apply_wb_button.setText("Apply WB")
        self._apply_wb_button.setStyleSheet(f"background-color: {colour_grey}; color: white")
        self._apply_wb_button.setEnabled(False) # default

    def deactivate_apply_wb_button(self):
        colour_grey = Config.instance().data["colour"]["rgb_very_light_grey"]
        self._apply_wb_button.setStyleSheet(f"background-color: {colour_grey}; color: white")
        self._apply_wb_button.setEnabled(False)

    def activate_apply_wb_button(self):
        colour_orange = Config.instance().data["colour"]["rgb_orange_colour"]
        self._apply_wb_button.setStyleSheet(f"background-color: {colour_orange}; color: white")
        self._apply_wb_button.setEnabled(True)

    def create_labels(self):
        self._wb_r_edit = QtWidgets.QLineEdit()
        self._wb_g_edit = QtWidgets.QLineEdit()
        self._wb_b_edit = QtWidgets.QLineEdit()
        
        list_label = [self._wb_r_edit, self._wb_g_edit, self._wb_b_edit]
        for item in list_label:
            item.setAlignment(QtCore.Qt.AlignCenter)

        self._wb_gain_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._wb_gain_splitter.addWidget(self._wb_r_edit)
        self._wb_gain_splitter.addWidget(QtWidgets.QLabel("-"))
        self._wb_gain_splitter.addWidget(self._wb_g_edit)
        self._wb_gain_splitter.addWidget(QtWidgets.QLabel("-"))
        self._wb_gain_splitter.addWidget(self._wb_b_edit)

    def get_wb_gain_factors(self):
        try:
            # rgbg
            wb_gain_factors = [float(self._wb_r_edit.text()), float(self._wb_g_edit.text()), float(self._wb_b_edit.text()), float(self._wb_g_edit.text())]
        except:
            wb_gain_factors = None
        
        return wb_gain_factors
    
    def clear_labels(self):
        list_labels = [self._wb_r_edit, self._wb_g_edit, self._wb_b_edit]
        for item in list_labels:
            item.clear()

    def activate_labels(self):
        list_labels = [self._wb_r_edit, self._wb_g_edit, self._wb_b_edit]
        for item in list_labels:
            item.setEnabled(True)
    
    def desactivate_labels(self):
        list_labels = [self._wb_r_edit, self._wb_g_edit, self._wb_b_edit]
        for item in list_labels:
            item.setEnabled(False)

    def create_default_container(self):
        self._container = QtWidgets.QVBoxLayout()
        self._container.addWidget(self._camera_radio_button)
        self._container.addWidget(self._daylight_radio_button)
        self._container.addWidget(self._custom_radio_button)
        self._container.addWidget(self._wb_gain_splitter)
        self._container.addWidget(self._apply_wb_button)

class RGBToXYZMatrixGroupBox(QtWidgets.QGroupBox):

    _path_file_csv = None # default, empty

    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("RGB to CIE XYZ matrix")
    
        self.create_radio_buttons()
        self.desactivate_radio_buttons()
        self.create_labels()
        self.desactivate_labels() # default
        self.create_buttons()
        self.create_default_container()
        self.setLayout(self._container)
        self.set_init_state()

    def set_init_state(self):
        self.clear_labels()
        self._auto_radio_button.setChecked(True) # default
        self.desactivate_radio_buttons()
        self.desactivate_labels()
        self.desactivate_load_button()

    def create_radio_buttons(self):
        self._auto_radio_button = QtWidgets.QRadioButton()
        self._auto_radio_button.setText("Auto") # camera_embedded
        self._computed_radio_button = QtWidgets.QRadioButton()
        self._computed_radio_button.setText("Computed")   

    def activate_radio_buttons(self):
        list_radio_buttons = [self._auto_radio_button, self._computed_radio_button]
        for radio_button in list_radio_buttons:
            radio_button.setEnabled(True)

    def desactivate_radio_buttons(self):
        list_radio_buttons = [self._auto_radio_button, self._computed_radio_button]
        for radio_button in list_radio_buttons:
            radio_button.setEnabled(False)

    def create_labels(self):
        self._a00 = QtWidgets.QLineEdit()
        self._a01 = QtWidgets.QLineEdit()
        self._a02 = QtWidgets.QLineEdit()
        self._a10 = QtWidgets.QLineEdit()
        self._a11 = QtWidgets.QLineEdit()
        self._a12 = QtWidgets.QLineEdit()
        self._a20 = QtWidgets.QLineEdit()
        self._a21 = QtWidgets.QLineEdit()
        self._a22 = QtWidgets.QLineEdit()

        list_label = [self._a00, self._a01, self._a02, self._a10, self._a11, self._a12, self._a20, self._a21, self._a22]
        for item in list_label:
            item.setAlignment(QtCore.Qt.AlignCenter)

        self._a0_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._a0_splitter.addWidget(self._a00)
        self._a0_splitter.addWidget(QtWidgets.QLabel("-"))
        self._a0_splitter.addWidget(self._a01)
        self._a0_splitter.addWidget(QtWidgets.QLabel("-"))
        self._a0_splitter.addWidget(self._a02)

        self._a1_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._a1_splitter.addWidget(self._a10)
        self._a1_splitter.addWidget(QtWidgets.QLabel("-"))
        self._a1_splitter.addWidget(self._a11)
        self._a1_splitter.addWidget(QtWidgets.QLabel("-"))
        self._a1_splitter.addWidget(self._a12)      

        self._a2_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._a2_splitter.addWidget(self._a20)
        self._a2_splitter.addWidget(QtWidgets.QLabel("-"))
        self._a2_splitter.addWidget(self._a21)
        self._a2_splitter.addWidget(QtWidgets.QLabel("-"))
        self._a2_splitter.addWidget(self._a22)

    def get_rgb_to_xyz_matrix(self):
        try:
            rgb_to_xyz = [[float(self._a00.text()), float(self._a01.text()), float(self._a02.text())], 
                          [float(self._a10.text()), float(self._a11.text()), float(self._a12.text())],
                          [float(self._a20.text()), float(self._a21.text()), float(self._a22.text())]]
        except:
            rgb_to_xyz = None
        
        return rgb_to_xyz

    def clear_labels(self):
        list_label = [self._a00, self._a01, self._a02, self._a10, self._a11, self._a12, self._a20, self._a21, self._a22]
        for item in list_label:
            item.clear()

    def activate_labels(self):
        list_label = [self._a00, self._a01, self._a02, self._a10, self._a11, self._a12, self._a20, self._a21, self._a22]
        for item in list_label:
            item.setEnabled(True)

    def desactivate_labels(self):
        list_label = [self._a00, self._a01, self._a02, self._a10, self._a11, self._a12, self._a20, self._a21, self._a22]
        for item in list_label:
            item.setEnabled(False)

    def update_matrix(self, rgb_xyz_array):
        self._a00.setText(str(f'{rgb_xyz_array[0][0]:2.3f}'))
        self._a01.setText(str(f'{rgb_xyz_array[0][1]:2.3f}'))
        self._a02.setText(str(f'{rgb_xyz_array[0][2]:2.3f}'))
        self._a10.setText(str(f'{rgb_xyz_array[1][0]:2.3f}'))
        self._a11.setText(str(f'{rgb_xyz_array[1][1]:2.3f}'))
        self._a12.setText(str(f'{rgb_xyz_array[1][2]:2.3f}'))
        self._a20.setText(str(f'{rgb_xyz_array[2][0]:2.3f}'))
        self._a21.setText(str(f'{rgb_xyz_array[2][1]:2.3f}'))
        self._a22.setText(str(f'{rgb_xyz_array[2][2]:2.3f}'))

    def update_matrix_(self, rgb_xyz_array):
        self._a00.setText(str(rgb_xyz_array[0][0]))
        self._a01.setText(str(rgb_xyz_array[0][1]))
        self._a02.setText(str(rgb_xyz_array[0][2]))
        self._a10.setText(str(rgb_xyz_array[1][0]))
        self._a11.setText(str(rgb_xyz_array[1][1]))
        self._a12.setText(str(rgb_xyz_array[1][2]))
        self._a20.setText(str(rgb_xyz_array[2][0]))
        self._a21.setText(str(rgb_xyz_array[2][1]))
        self._a22.setText(str(rgb_xyz_array[2][2]))

    def create_buttons(self):
        self._load_button = QtWidgets.QPushButton()
        self._load_button.setText("Load from CSV")
        self.desactivate_load_button()

    def activate_load_button(self):
        colour_orange = Config.instance().data["colour"]["rgb_orange_colour"]
        self._load_button.setStyleSheet(f"background-color: {colour_orange}; color: white") # default grey
        self._load_button.setEnabled(True) # default

    def desactivate_load_button(self):
        colour_grey = Config.instance().data["colour"]["rgb_very_light_grey"]
        self._load_button.setStyleSheet(f"background-color: {colour_grey}; color: white") 
        self._load_button.setEnabled(False) 

    def create_default_container(self):
        self._container = QtWidgets.QVBoxLayout()
        self._container.addWidget(self._auto_radio_button)
        self._container.addWidget(self._computed_radio_button)
        self._container.addWidget(self._a0_splitter)
        self._container.addWidget(self._a1_splitter)
        self._container.addWidget(self._a2_splitter)
        self._container.addWidget(self._load_button)
    
    def get_path_csv(self):
        load_dialog = QtWidgets.QFileDialog()
        json_default_dir = os.path.join(*[os.getcwd(), *Config.instance().data["dir_path"]["csv_dir"]])
        load_path = load_dialog.getOpenFileName(self, "Load to CIEXYZ matrix from CSV", json_default_dir, "CSV files (*.csv *.CSV)")
        path_file_csv = load_path[0]  

        if path_file_csv!= "":
            self.clear_labels()
            self._path_file_csv = path_file_csv

class ImageViewGroupBox(QtWidgets.QGroupBox):

    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("Image View")
        self.create_default_pixmap()
        self.create_default_container()
        self.setLayout(self._container)

    def create_default_pixmap(self):
        file_default_image = Config.instance().data["plot"]["file_default_image"]
        path_default_image = os.path.join(*[Config.coolpi_dir, *file_default_image])
        self._spc_image = QtGui.QPixmap(path_default_image)
        
    def create_default_container(self):
        self._spc_plot_label = QtWidgets.QLabel()
        self._spc_plot_label.setMaximumSize(Config.instance().data["plot"]["image_view_size"][0], Config.instance().data["plot"]["image_view_size"][1])
        self._spc_plot_label.setPixmap(self._spc_image)
        self._spc_plot_label.setScaledContents(True)

        self._container = QtWidgets.QHBoxLayout()
        self._container.addWidget(self._spc_plot_label)
    
    def update_figure(self, path_figure):
        QtGui.QImageReader.setAllocationLimit(0) # avoid error for images larger than 128 Mb
        if path_figure != None:
            self._spc_image = QtGui.QPixmap(path_figure)
            self._spc_image.scaledToHeight(Config.instance().data["plot"]["image_view_size"][0])
            self._spc_plot_label.setPixmap(self._spc_image)
            # scale
            
        else:
            self.create_default_pixmap()
            self._spc_plot_label.setPixmap(self._spc_image)

# Figure zoom view

class FigureView(QtWidgets.QWidget):

    def __init__(self, window_title, path_image, parent = None):
        super().__init__()   
        self.setFixedSize(Config.instance().data["zoom_plot"]["screen_size"][0], Config.instance().data["zoom_plot"]["screen_size"][1])
        self.setWindowTitle(window_title)

        self.create_items(path_image)
        self.add_items()

    def set_position(self, posx, posy):
        self.move(posx,posy)

    def create_items(self, path_image):
        self.create_layout()
        self.create_label(path_image)
        self.create_coolpi_logo()
        self.create_save_button()

    def create_layout(self):
        self._qv_layout = QtWidgets.QVBoxLayout()
        
    def create_label(self, path_image):
        self._image = QtGui.QPixmap(path_image)
        self._label = QtWidgets.QLabel()
        self._label.setFixedSize(Config.instance().data["zoom_plot"]["plot_zoom_size"][0], Config.instance().data["zoom_plot"]["plot_zoom_size"][1])
        self._label.setPixmap(self._image)
        self._label.setScaledContents(True)

    def create_coolpi_logo(self):
        file_logo_coolpi = Config.instance().data["logo"]["file_logo_coolpi"]
        path_logo_coolpi = os.path.join(*[Config.coolpi_dir, *file_logo_coolpi])
        self._coolpi = Logo("coolpi", path_logo_coolpi)
        
    def create_save_button(self):
        file_save_icon = Config.instance().data["icon"]["file_save_icon"]
        path_save_icon = os.path.join(*[Config.coolpi_dir, *file_save_icon])
        size = QtCore.QSize(Config.instance().data["icon"]["icon_size"][0],Config.instance().data["icon"]["icon_size"][0])
        self._save_button = SaveButton(path_save_icon, size, False)

    def add_items(self):
        self._qv_layout.addWidget(self._label)
        self._qv_layout.addWidget(self._save_button)
        #self._qv_layout.addWidget(self._indigo, 2, QtCore.Qt.AlignRight)
        self._qv_layout.addWidget(self._coolpi, 2, QtCore.Qt.AlignRight)
        self.setLayout(self._qv_layout)

    def save_image(self):
        save_dialog = QtWidgets.QFileDialog()
        plot_default_dir = os.path.join(*[os.getcwd(), *Config.instance().data["dir_path"]["plot_dir"]])
        save_path = save_dialog.getSaveFileName(self, "Save Current Plot", plot_default_dir, "Image files (*.png *.jpg)")
        path_file_png = save_path[0]
        if path_file_png != "": # avoid error press cancel button
            self._image.save(path_file_png)        
            self.show_save_message()

    def get_pos_center(self):
        x_pos = int((self.pos().x() + self.frameGeometry().width())/2)
        y_pos = int((self.pos().y() + self.frameGeometry().height())/2)
        return x_pos, y_pos

    def show_save_message(self):
        saved_message = SavedMessageBox("Figure saved successfully")
        x_pos, y_pos = self.get_pos_center()
        saved_message.setGeometry(x_pos, y_pos, Config.instance().data["main"]["message_screen_size"][0],Config.instance().data["main"]["message_screen_size"][1])
        saved_message.exec() # .show()

# Input GroupBox data

class InputGroupBox(QtWidgets.QGroupBox):
    
    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("Colour Sample")
        #self.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #E0E0E0, stop: 1 #FFFFFF)")

        self.create_combo_box()
        self.create_labels()
        self.create_input_form_layout()
        self.setLayout(self._input_form_layout)
        
    def create_combo_box(self):
        self._combo_colour_space = QtWidgets.QComboBox()
        self._combo_illuminant = QtWidgets.QComboBox()
        self._combo_observer = QtWidgets.QComboBox()

        colour_cyan = Config.instance().data["colour"]["rgb_cyan_colour"]
        self._combo_colour_space.setStyleSheet(f"selection-background-color: {colour_cyan}; selection-color: white;")
        self._combo_illuminant.setStyleSheet(f"selection-background-color: {colour_cyan}; selection-color: white;")
        self._combo_observer.setStyleSheet(f"selection-background-color: {colour_cyan}; selection-color: white;")
    
        # no es necesario recorrer la lista y add uno a uno los items        
        self._combo_illuminant.addItems(Config.instance().data["csc"]["cie_illuminants"])
        self._combo_illuminant.setCurrentText("D65")

        self._combo_observer.addItems(Config.instance().data["csc"]["observers"])
        self._combo_observer.setCurrentText("2")
        
        self._combo_colour_space.addItems(Config.instance().data["csc"]["colour_spaces"])
        self._combo_colour_space.setCurrentText("CIEXYZ")

    def create_labels(self):
        self._label_c1 = QtWidgets.QLabel()
        self._label_c1.setText(" X") # default
        self._label_c2 = QtWidgets.QLabel()
        self._label_c2.setText(" Y")
        self._label_c3 = QtWidgets.QLabel()
        self._label_c3.setText(" Z")
    
    def update_labels(self):
        colour_space = self._combo_colour_space.currentText()
        if colour_space == "CIE XYZ":
            self._label_c1.setText(" X")
            self._label_c2.setText(" Y")
            self._label_c3.setText(" Z")
        elif colour_space == "CIE xyY":
            self._label_c1.setText(" x")
            self._label_c2.setText(" y")
            self._label_c3.setText(" Y")
        elif colour_space == "CIELAB":
            self._label_c1.setText(" L")
            self._label_c2.setText(" a*")
            self._label_c3.setText(" b*")
        elif colour_space == "CIE LCHab":
            self._label_c1.setText(" L")
            self._label_c2.setText(" C")
            self._label_c3.setText(" Hab")
        elif colour_space == "CIE LCHuv":
            self._label_c1.setText(" L")
            self._label_c2.setText(" C")
            self._label_c3.setText(" Huv")
        elif colour_space == "CIELUV":
            self._label_c1.setText(" L")
            self._label_c2.setText(" U")
            self._label_c3.setText(" V")
            
    def create_input_form_layout(self):
        self._input_form_layout = QtWidgets.QFormLayout()
        self._input_form_layout.addRow("CIE Illuminant",self._combo_illuminant)
        self._input_form_layout.addRow("Observer", self._combo_observer)
        self._input_form_layout.addRow("Colour Space", self._combo_colour_space)
        
        self._sample_id = QtWidgets.QLineEdit()
        self._sample_id.setAlignment(QtCore.Qt.AlignCenter)
        self._input_form_layout.addRow("Sample ID", self._sample_id)
        self._c1 = QtWidgets.QLineEdit()
        self._c1.setAlignment(QtCore.Qt.AlignCenter)
        self._c2 = QtWidgets.QLineEdit()
        self._c2.setAlignment(QtCore.Qt.AlignCenter)
        self._c3 = QtWidgets.QLineEdit()
        self._c3.setAlignment(QtCore.Qt.AlignCenter)

        self._input_form_layout.addRow(self._label_c1, self._c1)
        self._input_form_layout.addRow(self._label_c2, self._c2)
        self._input_form_layout.addRow(self._label_c3, self._c3)

    def clear_coordinates(self):
        list_label = [self._sample_id , self._c1, self._c2, self._c3]
        for label in list_label:
            label.clear()

class SpectralGroupBox(QtWidgets.QGroupBox):

    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("Spectral Colour")
        
        self.create_combo_box()
        self.create_labels()
        self.create_init_table()
        self.create_grid()
        self.setLayout(self._spc_grid)

    def create_combo_box(self):
        self._combo_illuminant = QtWidgets.QComboBox()
        self._combo_observer = QtWidgets.QComboBox()

        colour_cyan = Config.instance().data["colour"]["rgb_cyan_colour"]
        self._combo_illuminant.setStyleSheet(f"selection-background-color: {colour_cyan}; selection-color: white;")
        self._combo_observer.setStyleSheet(f"selection-background-color: {colour_cyan}; selection-color: white;")
            
        self._combo_illuminant.addItems(Config.instance().data["spc"]["cie_illuminants"])
        self._combo_illuminant.setCurrentText("D65")

        self._combo_observer.addItems(Config.instance().data["spc"]["observers"])
        self._combo_observer.setCurrentText("2")

        self._combo_illuminant.setEnabled(False)
        self._combo_observer.setEnabled(False)

    def create_labels(self):
        self._cie_illuminant_label = QtWidgets.QLabel("CIE illuminant")
        self._cie_observer_label = QtWidgets.QLabel("Observer")
        self._sample_id_label = QtWidgets.QLabel("Sample ID")
        self._sample_id_edit = QtWidgets.QLineEdit()
        self._sample_id_edit.setAlignment(QtCore.Qt.AlignCenter)
        self._range_label = QtWidgets.QLabel("\u03BB range (nm)")
        self._min_range_edit = QtWidgets.QLineEdit()
        self._min_range_edit.setAlignment(QtCore.Qt.AlignCenter)
        self._max_range_edit = QtWidgets.QLineEdit()
        self._max_range_edit.setAlignment(QtCore.Qt.AlignCenter)

        self._range_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._range_splitter.addWidget(self._min_range_edit)
        self._range_splitter.addWidget(QtWidgets.QLabel("-"))
        self._range_splitter.addWidget(self._max_range_edit)

        self._interval_label = QtWidgets.QLabel("\u03BB interval (nm)")
        self._interval_edit = QtWidgets.QLineEdit()
        self._interval_edit.setAlignment(QtCore.Qt.AlignCenter)
    
        self._lambda_label = QtWidgets.QLabel("Spectral (\u03BB nm)")
    
        self._sample_id_edit.setEnabled(False)
        self._min_range_edit.setEnabled(False)
        self._max_range_edit.setEnabled(False)
        self._interval_edit.setEnabled(False)

    def create_init_table(self):
        self._lambda_table = QtWidgets.QTableWidget(2, 2)
        self._lambda_table.verticalHeader().setVisible(False)
        self._lambda_table.horizontalHeader().setVisible(False)
        self._header_table = self._lambda_table.horizontalHeader()
        self._header_table.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self._header_table.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.__fill_table_col_labels()

    def create_spc_table(self):
        nm_min = int(self._min_range_edit.text())
        nm_interval = int(self._interval_edit.text())        
        nm_max = int(self._max_range_edit.text()) + nm_interval
        row_labels = [x for x in range(nm_min, nm_max, nm_interval)]

        num_cols = Config.instance().data["spc"]["metadata_table_cols"] 
        num_rows = len(row_labels) + 1 
        
        self._lambda_table = QtWidgets.QTableWidget(num_rows, num_cols)
        self._lambda_table.verticalHeader().setVisible(False)
        self._lambda_table.horizontalHeader().setVisible(False)
        
        self._lambda_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        self._header_table = self._lambda_table.horizontalHeader()
        self._header_table.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self._header_table.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        self.__fill_table_col_labels()
        self.__fill_table_row_labels(row_labels)        
        self._lambda_table.setEnabled(False)
        
    def __fill_table_col_labels(self):
        col_labels = ["nm", "value"]
        r,g,b = Config.instance().data["spc"]["background_col_label"]
        for i in range(0,len(col_labels)):
            labelcol = QtWidgets.QTableWidgetItem(col_labels[i])
            labelcol.setTextAlignment(QtCore.Qt.AlignLeft)
            labelcol.setBackground(QtGui.QColor(r,g,b))
            self._lambda_table.setItem(0, i, labelcol)  
        self._lambda_table.resizeColumnsToContents()
        self._lambda_table.resizeRowsToContents() 

    def __fill_table_row_labels(self, row_labels):        
        r,g,b = Config.instance().data["spc"]["background_row_label"]
        for i in range(1, (len(row_labels)+1)):
            labelcol = QtWidgets.QTableWidgetItem(str(row_labels[i-1]))
            labelcol.setTextAlignment(QtCore.Qt.AlignLeft)
            labelcol.setBackground(QtGui.QColor(r,g,b))
            self._lambda_table.setItem(i, 0, labelcol)  
        self._lambda_table.resizeColumnsToContents()
        self._lambda_table.resizeRowsToContents() 

    def __fill_table_lambda_values(self, lambda_values):
        for i in range(1, (len(lambda_values)+1)):
            value = lambda_values[i-1] 
            labelcol = QtWidgets.QTableWidgetItem(f'{value:5.10f}')
            #labelcol = QtWidgets.QTableWidgetItem(str(lambda_values[i-1]))
            labelcol.setTextAlignment(QtCore.Qt.AlignLeft)
            self._lambda_table.setItem(i, 1, labelcol)  
            
    def update_label(self, label, data_label):
        if label == "sample_id":
            self._sample_id_edit.setText(str(data_label))
        if label == "illuminant":
            illuminant = data_label.upper()
            self._combo_illuminant.setCurrentText(illuminant)
        if label == "observer":
            observer = str(data_label)
            self._combo_observer.setCurrentText(observer)
        if label == "nm_range":
            nm_min = str(data_label[0])
            nm_max = str(data_label[1])
            self._min_range_edit.setText(nm_min)
            self._max_range_edit.setText(nm_max)
        if label == "nm_interval":
            nm_interval = str(data_label)
            self._interval_edit.setText(nm_interval)
            
    def update_table(self, lambda_values):
        self.create_spc_table()
        self.__fill_table_lambda_values(lambda_values)
        self._lambda_table.setEnabled(True)
        # add item
        self._spc_grid.addWidget(self._lambda_table, 5, 1)

    def clear_labels(self):
        self._sample_id_edit.clear()
        self._min_range_edit.clear()
        self._max_range_edit.clear()
        self._interval_edit.clear()
        self._lambda_table.clear()
        self.create_init_table()
        self._spc_grid.addWidget(self._lambda_table, 5, 1)

    def create_grid(self):
        self._spc_grid = QtWidgets.QGridLayout()
        self._spc_grid.addWidget(self._cie_illuminant_label, 0, 0)
        self._spc_grid.addWidget(self._combo_illuminant, 0, 1)
        self._spc_grid.addWidget(self._cie_observer_label, 1, 0)
        self._spc_grid.addWidget(self._combo_observer, 1, 1) 
        self._spc_grid.addWidget(self._sample_id_label, 2, 0)
        self._spc_grid.addWidget(self._sample_id_edit, 2, 1) 
        self._spc_grid.addWidget(self._range_label, 3, 0)
        self._spc_grid.addWidget(self._range_splitter, 3, 1)
        self._spc_grid.addWidget(self._interval_label, 4, 0)
        self._spc_grid.addWidget(self._interval_edit, 4, 1)
        self._spc_grid.addWidget(self._lambda_label, 5, 0)
        self._spc_grid.addWidget(self._lambda_table, 5, 1)

class InputIlluminantGroupBox(QtWidgets.QGroupBox):

    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("Input Illuminant")
        
        self.create_radio_buttons()
        self.create_buttons()
        self.create_combo_box()
        self.create_labels()
        self.create_grid()
        self.setLayout(self._spd_input_grid)

    def create_radio_buttons(self):
        self._cie_radio_button = QtWidgets.QRadioButton()
        self._cie_radio_button.setText("CIE")
        self._cie_radio_button.setChecked(True) # default
        self._cct_radio_button = QtWidgets.QRadioButton()
        self._cct_radio_button.setText("CCT")
        self._user_radio_button = QtWidgets.QRadioButton()
        self._user_radio_button.setText("Measured")
    
    def create_buttons(self):
        # load from CSV
        self._load_button = QtWidgets.QPushButton()
        self._load_button.setText("Select CSV/JSON")
        self.desactivate_load_button()

    def activate_load_button(self):
        colour_orange = Config.instance().data["colour"]["rgb_orange_colour"]
        self._load_button.setStyleSheet(f"background-color: {colour_orange}; color: white") # default grey
        self._load_button.setEnabled(True) # default

    def desactivate_load_button(self):
        colour_grey = Config.instance().data["colour"]["rgb_very_light_grey"]
        self._load_button.setStyleSheet(f"background-color: {colour_grey}; color: white") 
        self._load_button.setEnabled(False) 

    def create_combo_box(self):
        colour_cyan = Config.instance().data["colour"]["rgb_cyan_colour"]
        self._combo_illuminant = QtWidgets.QComboBox()
        self._combo_illuminant.setStyleSheet(f"selection-background-color: {colour_cyan}; selection-color: white;")
        self._combo_illuminant.addItems(Config.instance().data["spd"]["cie_illuminants"])
        self._combo_illuminant.setCurrentText("D65")
        self._combo_illuminant.setEnabled(True) # default

    def create_labels(self):
        self._cie_illuminant_label = QtWidgets.QLabel("CIE illuminant")
        self._cct_label = QtWidgets.QLabel("CCT (ºK)")
        self._cct_edit = QtWidgets.QLineEdit()
        self._cct_edit.setAlignment(QtCore.Qt.AlignCenter)
        self._cct_edit.setEnabled(False)

        self._user_name_label = QtWidgets.QLabel("Illuminant name")
        self._user_name_edit = QtWidgets.QLineEdit()
        self._user_name_edit.setAlignment(QtCore.Qt.AlignCenter)
        self._user_name_edit.setEnabled(False)
        self._user_path_label = QtWidgets.QLabel("Path CSV")
        self._user_path_edit = QtWidgets.QLineEdit()
        self._user_path_edit.setEnabled(False)

    def clear_labels(self):
        self._cct_edit.clear()
        self._user_name_edit.clear()
        self._user_path_edit.clear()

    def create_grid(self):
        self._spd_input_grid = QtWidgets.QGridLayout()
        self._spd_input_grid.addWidget(self._cie_radio_button, 0, 0, 1, 2)
        self._spd_input_grid.addWidget(self._cie_illuminant_label, 1, 0)
        self._spd_input_grid.addWidget(self._combo_illuminant, 1, 1)
        self._spd_input_grid.addWidget(self._cct_radio_button, 2, 0, 1, 2)
        self._spd_input_grid.addWidget(self._cct_label, 3, 0)
        self._spd_input_grid.addWidget(self._cct_edit, 3, 1)
        self._spd_input_grid.addWidget(self._user_radio_button, 4, 0, 1, 2)
        self._spd_input_grid.addWidget(self._user_name_label, 5, 0)
        self._spd_input_grid.addWidget(self._user_name_edit, 5, 1)
        self._spd_input_grid.addWidget(self._user_path_label, 6, 0)
        self._spd_input_grid.addWidget(self._user_path_edit, 6, 1)
        self._spd_input_grid.addWidget(self._load_button, 7, 0, 1, 2)

    def get_path_csv(self):
        load_dialog = QtWidgets.QFileDialog()
        spd_default_dir = os.path.join(*[os.getcwd(), *Config.instance().data["dir_path"]["spd_dir"]])
        load_path = load_dialog.getOpenFileName(self, "Load Illuminant from CSV or JSON", spd_default_dir, "CSV or JSON files (*.csv *.CSV *.json *.JSON)")
        path_file_csv = load_path[0]  

        if path_file_csv != "": 
            self._user_path_edit.setText(path_file_csv)

class SPDGroupBox(QtWidgets.QGroupBox):
    
    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("Spectral SPD data")
        
        self.create_labels()
        self.create_init_table()
        self.create_grid()
        self.setLayout(self._spd_grid)

    def create_labels(self):
        self._range_label = QtWidgets.QLabel("\u03BB range (nm)")
        self._min_range_edit = QtWidgets.QLineEdit()
        self._min_range_edit.setAlignment(QtCore.Qt.AlignCenter)
        self._max_range_edit = QtWidgets.QLineEdit()
        self._max_range_edit.setAlignment(QtCore.Qt.AlignCenter)

        self._range_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._range_splitter.addWidget(self._min_range_edit)
        self._range_splitter.addWidget(QtWidgets.QLabel("-"))
        self._range_splitter.addWidget(self._max_range_edit)

        self._interval_label = QtWidgets.QLabel("\u03BB interval (nm)")
        self._interval_edit = QtWidgets.QLineEdit()
        self._interval_edit.setAlignment(QtCore.Qt.AlignCenter)
    
        self._lambda_label = QtWidgets.QLabel("Spectral (\u03BB nm)")
        
        self._min_range_edit.setEnabled(False)
        self._max_range_edit.setEnabled(False)
        self._interval_edit.setEnabled(False)

    def create_init_table(self):
        self._lambda_table = QtWidgets.QTableWidget(2, 2)
        self._lambda_table.verticalHeader().setVisible(False)
        self._lambda_table.horizontalHeader().setVisible(False)
        self._header_table = self._lambda_table.horizontalHeader()
        self._header_table.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self._header_table.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.__fill_table_col_labels()

    def create_spd_table(self):
        nm_min = int(self._min_range_edit.text())
        nm_interval = int(self._interval_edit.text())        
        nm_max = int(self._max_range_edit.text()) + nm_interval
        row_labels = [x for x in range(nm_min, nm_max, nm_interval)]

        num_cols = Config.instance().data["spc"]["metadata_table_cols"] 
        num_rows = len(row_labels) + 1 
        
        self._lambda_table = QtWidgets.QTableWidget(num_rows, num_cols)
        self._lambda_table.verticalHeader().setVisible(False)
        self._lambda_table.horizontalHeader().setVisible(False)
        
        self._lambda_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        self._header_table = self._lambda_table.horizontalHeader()
        self._header_table.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self._header_table.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        self.__fill_table_col_labels()
        self.__fill_table_row_labels(row_labels)        
        self._lambda_table.setEnabled(False)
        
    def __fill_table_col_labels(self):
        col_labels = ["nm", "value"]
        r,g,b = Config.instance().data["spc"]["background_col_label"]
        for i in range(0,len(col_labels)):
            labelcol = QtWidgets.QTableWidgetItem(col_labels[i])
            labelcol.setTextAlignment(QtCore.Qt.AlignLeft)
            labelcol.setBackground(QtGui.QColor(r,g,b))
            self._lambda_table.setItem(0, i, labelcol)  
        self._lambda_table.resizeColumnsToContents()
        self._lambda_table.resizeRowsToContents() 

    def __fill_table_row_labels(self, row_labels):        
        r,g,b = Config.instance().data["spc"]["background_row_label"]
        for i in range(1, (len(row_labels)+1)):
            labelcol = QtWidgets.QTableWidgetItem(str(row_labels[i-1]))
            labelcol.setTextAlignment(QtCore.Qt.AlignLeft)
            labelcol.setBackground(QtGui.QColor(r,g,b))
            self._lambda_table.setItem(i, 0, labelcol)  
        self._lambda_table.resizeColumnsToContents()
        self._lambda_table.resizeRowsToContents() 

    def __fill_table_lambda_values(self, lambda_values):
        for i in range(1, (len(lambda_values)+1)):
            value = lambda_values[i-1] 
            labelcol = QtWidgets.QTableWidgetItem(f'{value:5.10f}')
            labelcol.setTextAlignment(QtCore.Qt.AlignLeft)
            self._lambda_table.setItem(i, 1, labelcol)  
            
    def update_label(self, label, data_label):
        if label == "nm_range":
            nm_min = str(data_label[0])
            nm_max = str(data_label[1])
            self._min_range_edit.setText(nm_min)
            self._max_range_edit.setText(nm_max)
        if label == "nm_interval":
            nm_interval = str(data_label)
            self._interval_edit.setText(nm_interval)
            
    def update_table(self, lambda_values):
        self.create_spd_table()
        self.__fill_table_lambda_values(lambda_values)
        self._lambda_table.setEnabled(True)
        # add item
        self._spd_grid.addWidget(self._lambda_table, 2, 1)

    def clear_labels(self):
        self._min_range_edit.clear()
        self._max_range_edit.clear()
        self._interval_edit.clear()
        self._lambda_table.clear()
        self.create_init_table()
        self._spd_grid.addWidget(self._lambda_table, 2, 1)

    def create_grid(self):
        self._spd_grid = QtWidgets.QGridLayout()
        self._spd_grid.addWidget(self._range_label, 0, 0)
        self._spd_grid.addWidget(self._range_splitter, 0, 1)
        self._spd_grid.addWidget(self._interval_label, 1, 0)
        self._spd_grid.addWidget(self._interval_edit, 1, 1)
        self._spd_grid.addWidget(self._lambda_label, 2, 0)
        self._spd_grid.addWidget(self._lambda_table, 2, 1)

class InputChartGroupBox(QtWidgets.QGroupBox):
    
    __colour_checker_implemented = Config.instance().data["cci"]["colourchecker_implemented"]
    
    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("ColourChecker")
        #self.setStyleSheet("background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #E0E0E0, stop: 1 #FFFFFF)")

        self.create_items()
        self.setLayout(self._input_layout)
    
    def create_items(self):
        self.create_combo_box()
        self.create_button()
        self.create_radio_buttons()
        self.create_labels()
        self.create_metadata()
        self.create_input_layout()

    def create_labels(self):
        self._chart_measured_name_edit = QtWidgets.QLineEdit()
        self._chart_measured_name_edit.setAlignment(QtCore.Qt.AlignCenter)
        self._chart_measured_name_edit.setEnabled(False)

    def create_combo_box(self):
        self._combo_colourchecker = QtWidgets.QComboBox()
        list_items = ["None"]
        list_items.extend([value for value in self.__colour_checker_implemented.values()])
        list_items = [value for value in self.__colour_checker_implemented.values()]
        self._combo_colourchecker.addItems(list_items)
        index = self._combo_colourchecker.findText("None") 
        self._combo_colourchecker.setCurrentIndex(index)
        
        colour_cyan = Config.instance().data["colour"]["rgb_cyan_colour"]
        self._combo_colourchecker.setStyleSheet(f"selection-background-color: {colour_cyan}; selection-color: white;")

    def create_button(self):
        # load from JSON
        self._load_button = QtWidgets.QPushButton()
        self._load_button.setText("Load from JSON")
        self.deactivate_load_button()
        
    def activate_load_button(self):
        colour_cyan = Config.instance().data["colour"]["rgb_cyan_colour"]
        self._load_button.setStyleSheet(f"background-color: {colour_cyan}; color: white")
        self._load_button.setDisabled(False)

    def deactivate_load_button(self):
        colour_grey = Config.instance().data["colour"]["rgb_very_light_grey"]
        self._load_button.setStyleSheet(f"background-color: {colour_grey}; color: white")
        self._load_button.setDisabled(True)    

    def create_radio_buttons(self):
        self._chart_resources_radio_button = QtWidgets.QRadioButton()
        self._chart_resources_radio_button.setText("From Resources")
        self._chart_resources_radio_button.setChecked(True) # default
        self._chart_measured_radio_button = QtWidgets.QRadioButton()
        self._chart_measured_radio_button.setText("Measured")

    def create_metadata(self): # table     
        num_cols = Config.instance().data["cci"]["metadata_table_cols"] 
        num_rows = Config.instance().data["cci"]["metadata_table_rows"] 
        self._metadata_table = QtWidgets.QTableWidget(num_rows, num_cols)
        self._metadata_table.verticalHeader().setVisible(False)
        self._metadata_table.horizontalHeader().setVisible(False)
        self._metadata_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        
        self._header_table = self._metadata_table.horizontalHeader()
        self._header_table.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self._header_table.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        
        self.__fill_table_col_labels() # default

    def __fill_table_col_labels(self):
        row_labels = ["Instrument", "Meas. Date", "Illuminant", "Observer", "Num. Patches", "\u03BB range (nm)", "\u03BB interval (nm)"]
        r,g,b = Config.instance().data["cci"]["background_metadata_label"]
        for i in range(0,len(row_labels)):
            labelcol = QtWidgets.QTableWidgetItem(row_labels[i])
            labelcol.setTextAlignment(QtCore.Qt.AlignLeft)
            labelcol.setBackground(QtGui.QColor(r,g,b))
            self._metadata_table.setItem(i, 0, labelcol)  
        self._metadata_table.resizeColumnsToContents()
        self._metadata_table.resizeRowsToContents() 
            
    def update_metadata(self, new_metadata):
        if self._combo_colourchecker.currentText() != "None":
            #self._metadata_table.clear()
            #self.__fill_table_col_labels()
            for key, value in new_metadata.items():
                labelrow = QtWidgets.QTableWidgetItem(str(value))
                #labelrow.setTextAlignment(QtCore.Qt.AlignHCenter)
                if "Instrument" in key:
                    self._metadata_table.setItem(0, 1, labelrow) 
                if "Date" in key:
                    labelrow.setText(f"{value[0][0]}/{value[0][1]}/{value[0][2]} - {value[1][0]}h {value[1][1]}m {value[1][2]}s")
                    self._metadata_table.setItem(1, 1, labelrow) 
                if "Illuminant" in key:
                    self._metadata_table.setItem(2, 1, labelrow) 
                if "Observer" in key:
                    self._metadata_table.setItem(3, 1, labelrow) 
                if "num" in key:
                    self._metadata_table.setItem(4, 1, labelrow) 
                if "range" in key:
                    self._metadata_table.setItem(5, 1, labelrow) 
                if "interval" in key:
                    self._metadata_table.setItem(6, 1, labelrow) 
            self._metadata_table.resizeColumnsToContents()
            self._metadata_table.resizeRowsToContents()

    def create_input_layout(self):
        self._input_layout = QtWidgets.QVBoxLayout()
        self._input_layout.addWidget(self._chart_resources_radio_button)
        self._input_layout.addWidget(self._combo_colourchecker)
        self._input_layout.addWidget(self._chart_measured_radio_button)
        self._input_layout.addWidget(self._chart_measured_name_edit)
        self._input_layout.addWidget(self._load_button)
        self._input_layout.addWidget(self._metadata_table)

    def clear_labels(self):
        self._chart_measured_name_edit.clear()
        self._metadata_table.clear()
        self.__fill_table_col_labels()

# CIE Colour Space GroupBox

class XYZGroupBox(QtWidgets.QGroupBox):
    
    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("CIE XYZ")
        self.create_XYZ_layout()
        self.setLayout(self._XYZ_form_layout)

    def create_XYZ_layout(self):
        self._XYZ_form_layout = QtWidgets.QFormLayout()

        self._X = QtWidgets.QLineEdit()
        self._X.setEnabled(False)
        self._X.setAlignment(QtCore.Qt.AlignCenter)
        self._Y = QtWidgets.QLineEdit()
        self._Y.setEnabled(False)
        self._Y.setAlignment(QtCore.Qt.AlignCenter)
        self._Z = QtWidgets.QLineEdit()
        self._Z.setEnabled(False)
        self._Z.setAlignment(QtCore.Qt.AlignCenter)

        self._XYZ_form_layout.addRow("X", self._X)
        self._XYZ_form_layout.addRow("Y", self._Y)
        self._XYZ_form_layout.addRow("Z", self._Z)

    def update_coordinates(self, X, Y, Z):
        self._X.setText(str(X))
        self._Y.setText(str(Y))
        self._Z.setText(str(Z))
    
    def clear_coordinates(self):
        list_label = [self._X, self._Y, self._Z]
        for label in list_label:
            label.clear()
    
class xyYGroupBox(QtWidgets.QGroupBox):
    
    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("CIE xyY")
        self.create_xyY_layout()
        self.setLayout(self._xyY_form_layout)

    def create_xyY_layout(self):
        self._xyY_form_layout = QtWidgets.QFormLayout()

        self._x = QtWidgets.QLineEdit()
        self._x.setEnabled(False)
        self._x.setAlignment(QtCore.Qt.AlignCenter)
        self._y = QtWidgets.QLineEdit()
        self._y.setEnabled(False)
        self._y.setAlignment(QtCore.Qt.AlignCenter)
        self._Y = QtWidgets.QLineEdit()
        self._Y.setEnabled(False)
        self._Y.setAlignment(QtCore.Qt.AlignCenter)

        self._xyY_form_layout.addRow("x", self._x)
        self._xyY_form_layout.addRow("y", self._y)
        self._xyY_form_layout.addRow("Y", self._Y)

    def update_coordinates(self, x, y, Y):
        self._x.setText(str(x))
        self._y.setText(str(y))
        self._Y.setText(str(Y))

    def clear_coordinates(self):
        list_label = [self._x, self._y, self._Y]
        for label in list_label:
            label.clear()
        
class LABGroupBox(QtWidgets.QGroupBox):
    
    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("CIELAB")
        self.create_LAB_layout()
        self.setLayout(self._LAB_form_layout) 

    def create_LAB_layout(self):
        self._LAB_form_layout = QtWidgets.QFormLayout()

        self._L = QtWidgets.QLineEdit()
        self._L.setEnabled(False)
        self._L.setAlignment(QtCore.Qt.AlignCenter)
        self._a = QtWidgets.QLineEdit()
        self._a.setEnabled(False)
        self._a.setAlignment(QtCore.Qt.AlignCenter)
        self._b = QtWidgets.QLineEdit()
        self._b.setEnabled(False)
        self._b.setAlignment(QtCore.Qt.AlignCenter)

        self._LAB_form_layout.addRow("L", self._L)
        self._LAB_form_layout.addRow("a*", self._a)
        self._LAB_form_layout.addRow("b*", self._b)

    def update_coordinates(self, L, a, b):
        self._L.setText(str(L))
        self._a.setText(str(a))
        self._b.setText(str(b))
    
    def clear_coordinates(self):
        list_label = [self._L, self._a, self._b]
        for label in list_label:
            label.clear()

class LCHabGroupBox(QtWidgets.QGroupBox):
    
    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("CIE LCHab")
        self.create_LCHab_layout()
        self.setLayout(self._LCHab_form_layout) 

    def create_LCHab_layout(self):
        self._LCHab_form_layout = QtWidgets.QFormLayout()

        self._L = QtWidgets.QLineEdit()
        self._L.setEnabled(False)
        self._L.setAlignment(QtCore.Qt.AlignCenter)
        self._C = QtWidgets.QLineEdit()
        self._C.setEnabled(False)
        self._C.setAlignment(QtCore.Qt.AlignCenter)
        self._Hab = QtWidgets.QLineEdit()
        self._Hab.setEnabled(False)
        self._Hab.setAlignment(QtCore.Qt.AlignCenter)

        self._LCHab_form_layout.addRow("L", self._L)
        self._LCHab_form_layout.addRow("C", self._C)
        self._LCHab_form_layout.addRow("Hab", self._Hab)

    def update_coordinates(self, L, C, Hab):
        self._L.setText(str(L))
        self._C.setText(str(C))
        self._Hab.setText(str(Hab))
    
    def clear_coordinates(self):
        list_label = [self._L, self._C, self._Hab]
        for label in list_label:
            label.clear()

class LCHuvGroupBox(QtWidgets.QGroupBox):
    
    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("CIE LCHuv")
        self.create_LCHuv_layout()
        self.setLayout(self._LCHuv_form_layout) 

    def create_LCHuv_layout(self):
        self._LCHuv_form_layout = QtWidgets.QFormLayout()

        self._L = QtWidgets.QLineEdit()
        self._L.setEnabled(False)
        self._L.setAlignment(QtCore.Qt.AlignCenter)
        self._C = QtWidgets.QLineEdit()
        self._C.setEnabled(False)
        self._C.setAlignment(QtCore.Qt.AlignCenter)
        self._Huv = QtWidgets.QLineEdit()
        self._Huv.setEnabled(False)
        self._Huv.setAlignment(QtCore.Qt.AlignCenter)

        self._LCHuv_form_layout.addRow("L", self._L)
        self._LCHuv_form_layout.addRow("C", self._C)
        self._LCHuv_form_layout.addRow("Huv", self._Huv)

    def update_coordinates(self, L, C, Huv):
        self._L.setText(str(L))
        self._C.setText(str(C))
        self._Huv.setText(str(Huv))
    
    def clear_coordinates(self):
        list_label = [self._L, self._C, self._Huv]
        for label in list_label:
            label.clear()

class LUVGroupBox(QtWidgets.QGroupBox):
    
    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("CIELUV")
        self.create_LUV_layout()
        self.setLayout(self._LUV_form_layout) 

    def create_LUV_layout(self):
        self._LUV_form_layout = QtWidgets.QFormLayout()

        self._L = QtWidgets.QLineEdit()
        self._L.setEnabled(False)
        self._L.setAlignment(QtCore.Qt.AlignCenter)
        self._U = QtWidgets.QLineEdit()
        self._U.setEnabled(False)
        self._U.setAlignment(QtCore.Qt.AlignCenter)
        self._V = QtWidgets.QLineEdit()
        self._V.setEnabled(False)
        self._V.setAlignment(QtCore.Qt.AlignCenter)

        self._LUV_form_layout.addRow("L", self._L)
        self._LUV_form_layout.addRow("U", self._U)
        self._LUV_form_layout.addRow("V", self._V)

    def update_coordinates(self, L, U, V):
        self._L.setText(str(L))
        self._U.setText(str(U))
        self._V.setText(str(V))
    
    def clear_coordinates(self):
        list_label = [self._L, self._U, self._V]
        for label in list_label:
            label.clear()

class sRGBGroupBox(QtWidgets.QGroupBox):
    
    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("sRGB")
        self.create_sRGB_layout()
        self.setLayout(self._sRGB_form_layout) 

    def create_sRGB_layout(self):
        self._sRGB_form_layout = QtWidgets.QFormLayout()

        self._sR = QtWidgets.QLineEdit()
        self._sR.setEnabled(False)
        self._sR.setAlignment(QtCore.Qt.AlignCenter)
        self._sG = QtWidgets.QLineEdit()
        self._sG.setEnabled(False)
        self._sG.setAlignment(QtCore.Qt.AlignCenter)
        self._sB = QtWidgets.QLineEdit()
        self._sB.setEnabled(False)
        self._sB.setAlignment(QtCore.Qt.AlignCenter)

        self._sRGB_form_layout.addRow("sR", self._sR)
        self._sRGB_form_layout.addRow("sG", self._sG)
        self._sRGB_form_layout.addRow("sB", self._sB)

    def update_coordinates(self, sR, sG, sB):
        self._sR.setText(str(sR))
        self._sG.setText(str(sG))
        self._sB.setText(str(sB))
    
    def clear_coordinates(self):
        self._sR.clear()
        self._sG.clear()
        self._sB.clear()

# Plot GoupBox

class ChromaticityDiagramGroupBox(QtWidgets.QGroupBox):

    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("CIE 1931 x,y Chromaticity Diagram")
        self.create_defaul_image()
        self.create_xy_plot_layout()
        self.setLayout(self._xy_plot_layout)
        
    def create_defaul_image(self):
        file_default_image = Config.instance().data["plot"]["file_default_image"]
        path_default_image = os.path.join(*[Config.coolpi_dir, *file_default_image])

        self._cd_image = QtGui.QPixmap(path_default_image)

        self._xy_plot_label = QtWidgets.QLabel()
        self._xy_plot_label.setMaximumSize(Config.instance().data["plot"]["plot_figure_size"][0], Config.instance().data["plot"]["plot_figure_size"][1])
        self._xy_plot_label.setPixmap(self._cd_image)
        self._xy_plot_label.setScaledContents(True)

    def create_xy_plot_layout(self):
        self._xy_plot_layout = QtWidgets.QFormLayout()
        self._xy_plot_layout.setFormAlignment(QtCore.Qt.AlignCenter) # fails
        # coordinates
        self._x = QtWidgets.QLineEdit()
        self._x.setEnabled(False)
        self._x.setAlignment(QtCore.Qt.AlignCenter)
        self._y = QtWidgets.QLineEdit()
        self._y.setEnabled(False)
        self._y.setAlignment(QtCore.Qt.AlignCenter)
        self._Y = QtWidgets.QLineEdit()
        self._Y.setEnabled(False)
        self._Y.setAlignment(QtCore.Qt.AlignCenter)
        self._xy_plot_layout.addRow("x", self._x)
        self._xy_plot_layout.addRow("y", self._y)
        self._xy_plot_layout.addRow("Y", self._Y)
        #plot
        self._xy_plot_layout.addRow("", self._xy_plot_label)

    def update_figure(self, path_image):
        self._cd_image = QtGui.QPixmap(path_image)
        self._xy_plot_label.setPixmap(self._cd_image) 

    def save_figure(self, path_out):
        self._cd_image.save(path_out)

    def update_coordinates(self, x, y, Y):
        self._x.setText(str(x))
        self._y.setText(str(y))
        self._Y.setText(str(Y))

class CielabPlotGroupBox(QtWidgets.QGroupBox):

    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("CIELAB Diagram")
        self.create_default_image()
        self.create_cielab_plot_layout()
        self.setLayout(self._cielab_plot_layout)
        
    def create_default_image(self):
        file_default_image = Config.instance().data["plot"]["file_default_image"]
        path_default_image = os.path.join(*[Config.coolpi_dir, *file_default_image])

        self._cielab_image = QtGui.QPixmap(path_default_image)
        
        self._cielab_plot_label = QtWidgets.QLabel()
        self._cielab_plot_label.setMaximumSize(Config.instance().data["plot"]["plot_figure_size"][0], Config.instance().data["plot"]["plot_figure_size"][1])
        self._cielab_plot_label.setPixmap(self._cielab_image)
        self._cielab_plot_label.setScaledContents(True)

    def create_cielab_plot_layout(self):
        self._cielab_plot_layout = QtWidgets.QFormLayout()
        # coordinates
        self._L = QtWidgets.QLineEdit()
        self._L.setEnabled(False)
        self._L.setAlignment(QtCore.Qt.AlignCenter)
        self._a = QtWidgets.QLineEdit()
        self._a.setEnabled(False)
        self._a.setAlignment(QtCore.Qt.AlignCenter)
        self._b = QtWidgets.QLineEdit()
        self._b.setEnabled(False)
        self._b.setAlignment(QtCore.Qt.AlignCenter)
        self._cielab_plot_layout.addRow("L", self._L)
        self._cielab_plot_layout.addRow("a*", self._a)
        self._cielab_plot_layout.addRow("b*", self._b)
        # plot
        self._cielab_plot_layout.addRow("", self._cielab_plot_label)
    
    def update_figure(self, path_figure):
        self._cielab_image = QtGui.QPixmap(path_figure)
        self._cielab_plot_label.setPixmap(self._cielab_image)
    
    def save_figure(self, path_out):
        self._cielab_image.save(path_out)

    def update_coordinates(self, L, a, b):
        self._L.setText(str(L))
        self._a.setText(str(a))
        self._b.setText(str(b))

class sRGBPlotGroupBox(QtWidgets.QGroupBox):

    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("sRGB Plot")
        self.create_default_image()
        self.create_srgb_plot_layout()
        self.setLayout(self._srgb_plot_layout)

    def load_default_image(self):
        file_default_image = Config.instance().data["plot"]["file_default_image"]
        path_default_image = os.path.join(*[Config.coolpi_dir, *file_default_image])
        self._srgb_image = QtGui.QPixmap(path_default_image)

    def create_default_image(self):
        self.load_default_image()
        self._srgb_plot_label = QtWidgets.QLabel()
        self._srgb_plot_label.setMaximumSize(Config.instance().data["plot"]["srgb_plot_size"], Config.instance().data["plot"]["srgb_plot_size"])
        self._srgb_plot_label.setPixmap(self._srgb_image)
        self._srgb_plot_label.setScaledContents(True)

    def create_srgb_plot_layout(self):
        self._srgb_plot_layout = QtWidgets.QFormLayout()
        # coordinates
        self._sR = QtWidgets.QLineEdit()
        self._sR.setEnabled(False)
        self._sR.setAlignment(QtCore.Qt.AlignCenter)
        self._sG = QtWidgets.QLineEdit()
        self._sG.setEnabled(False)
        self._sG.setAlignment(QtCore.Qt.AlignCenter)
        self._sB = QtWidgets.QLineEdit()
        self._sB.setEnabled(False)
        self._sB.setAlignment(QtCore.Qt.AlignCenter)
        self._srgb_plot_layout.addRow("sR", self._sR)
        self._srgb_plot_layout.addRow("sG", self._sG)
        self._srgb_plot_layout.addRow("sB", self._sB) 
        # plot 
        self._srgb_plot_layout.addRow("", self._srgb_plot_label)

    def update_figure(self, r, g, b):
        self._srgb_image.fill(QtGui.QColor.fromRgb(r, g, b))
        self._srgb_plot_label.setPixmap(self._srgb_image)
    
    def update_default_figure(self):
        self.load_default_image()
        self._srgb_plot_label.setPixmap(self._srgb_image)
    
    def update_coordinates(self, sR, sG, sB):
        self._sR.setText(str(sR))
        self._sG.setText(str(sG))
        self._sB.setText(str(sB))

    def clear_coordinates(self):
        self._sR.clear()
        self._sG.clear()
        self._sB.clear()

class SpectralPlotGroupBox(QtWidgets.QGroupBox):

    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("Spectral Plot")
        self.create_default_pixmap()
        self.create_default_container()
        self.setLayout(self._container)

    def create_default_pixmap(self):
        file_default_image = Config.instance().data["plot"]["file_default_image"]
        path_default_image = os.path.join(*[Config.coolpi_dir, *file_default_image])
        self._spc_image = QtGui.QPixmap(path_default_image)
        
    def create_default_container(self):
        self._spc_plot_label = QtWidgets.QLabel()
        self._spc_plot_label.setMaximumSize(Config.instance().data["plot"]["spectral_plot_size"][0], Config.instance().data["plot"]["spectral_plot_size"][1])
        self._spc_plot_label.setPixmap(self._spc_image)
        self._spc_plot_label.setScaledContents(True)

        self._container = QtWidgets.QHBoxLayout()
        self._container.addWidget(self._spc_plot_label)
    
    def update_figure(self, path_figure):
        if path_figure != None:
            self._spc_image = QtGui.QPixmap(path_figure)
            self._spc_plot_label.setPixmap(self._spc_image)
        else:
            self.create_default_pixmap()
            self._spc_plot_label.setPixmap(self._spc_image)

    def save_figure(self, path_out):
        self._spc_image.save(path_out)
             
class IlluminantPlotGroupBox(QtWidgets.QGroupBox):

    def __init__(self, parent = None):
        super().__init__()
        self.setTitle("Illuminant SPD Plot")
        self.create_default_pixmap()
        self.create_default_container()
        self.setLayout(self._container)

    def create_default_pixmap(self):
        file_default_image = Config.instance().data["plot"]["file_default_image"]
        path_default_image = os.path.join(*[Config.coolpi_dir, *file_default_image])
        self._spd_image = QtGui.QPixmap(path_default_image)
        
    def create_default_container(self):
        self._spd_plot_label = QtWidgets.QLabel()
        self._spd_plot_label.setMaximumSize(Config.instance().data["plot"]["spectral_plot_size"][0], Config.instance().data["plot"]["spectral_plot_size"][1])
        self._spd_plot_label.setPixmap(self._spd_image)
        self._spd_plot_label.setScaledContents(True)

        self._container = QtWidgets.QHBoxLayout()
        self._container.addWidget(self._spd_plot_label)
    
    def update_figure(self, path_figure):
        if path_figure != None:
            self._spd_image = QtGui.QPixmap(path_figure)
            self._spd_plot_label.setPixmap(self._spd_image)
        else:
            self.create_default_pixmap()
            self._spd_plot_label.setPixmap(self._spd_image)

    def save_figure(self, path_out):
        self._spd_image.save(path_out)

# Auxiliar classes

class Logo(QtWidgets.QLabel):
    def __init__(self, name_label, path_image, parent = None):
        super().__init__()
        self.setObjectName(name_label)
        logo_pixmap = QtGui.QPixmap(path_image)
        self.setPixmap(logo_pixmap)

class SaveButton(QtWidgets.QPushButton):
    def __init__(self, path_icon, size, disabled, parent = None):
        super().__init__()
        self._icon = QtGui.QIcon(path_icon)
        self.setIcon(self._icon)
        self.setIconSize(size)
        self.setDisabled(disabled)

        colour = Config.instance().data["colour"]["rgb_pink_colour"]
        self.setStyleSheet(f"background-color: {colour}; color: white")

# MessageBox

class SavedMessageBox(QtWidgets.QMessageBox):
    def __init__(self, msg, parent = None):
        super().__init__()  
        self.setIcon(QtWidgets.QMessageBox.Icon.Information)
        self.setText(msg)
        self._save_button = QtWidgets.QPushButton("Ok")
        self.addButton(self._save_button, QtWidgets.QMessageBox.ButtonRole.AcceptRole)

class WarningMessageBox(QtWidgets.QMessageBox):
    def __init__(self, parent = None):
        super().__init__()   
        self.setIcon(QtWidgets.QMessageBox.Icon.Warning)

    def set_warning_message(self, msg):
        self.setText(msg)
    
class QuestionMessageBox(QtWidgets.QMessageBox):
    def __init__(self, parent = None):
        super().__init__()   
        self.setIcon(QtWidgets.QMessageBox.Icon.Question)   
        
        self._cancel_button = QtWidgets.QPushButton("Cancel")
        self._save_button = QtWidgets.QPushButton("Ok")
        
        self.addButton(self._save_button, QtWidgets.QMessageBox.ButtonRole.AcceptRole)
        self.addButton(self._cancel_button, QtWidgets.QMessageBox.ButtonRole.AcceptRole)
        
    def set_question_message(self, msg):
        self.setText(msg)      
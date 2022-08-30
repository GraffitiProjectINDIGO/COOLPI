from functools import partial
import os

from coolpi.gui.config import Config

class Controller:

    def __init__(self, app, view, model):
        
        self._app = app
        self._view = view
        self._model = model
        self._connect_main_window_actions()

    def _connect_main_window_actions(self):
        # actions
        self._view._cci_action.triggered.connect(self.open_cci)
        self._view._cde_action.triggered.connect(self.open_cde)
        self._view._cpt_action.triggered.connect(self.open_cpt)                
        self._view._rcip_action.triggered.connect(self.open_rcip)
        self._view._csc_action.triggered.connect(self.open_csc)
        #self._view._irgbe_action.triggered.connect(self.open_irgbe)
        #self._view._lrm_action.triggered.connect(self.open_lrm)
        self._view._quit_action.triggered.connect(self.quit)
        self._view._spc_action.triggered.connect(self.open_spc)
        self._view._spd_action.triggered.connect(self.open_spd)
        #self._view._wb_action.triggered.connect(self.open_wb)
        # buttons
        self._view._cci_button.clicked.connect(self.open_cci)
        self._view._cde_button.clicked.connect(self.open_cde)                
        self._view._cpt_button.clicked.connect(self.open_cpt)
        self._view._csc_button.clicked.connect(self.open_csc)
        #self._view._irgbe_button.clicked.connect(self.open_irgbe)
        #self._view._lrm_button.clicked.connect(self.open_lrm)       
        self._view._rcip_button.clicked.connect(self.open_rcip) 
        self._view._spc_button.clicked.connect(self.open_spc)
        self._view._spd_button.clicked.connect(self.open_spd)
        #self._view._wb_button.clicked.connect(self.open_wb) 

    # CSC - Colour Space Conversion
    def open_csc(self):
        self.close_open_windows()
        self._view.open_csc_view()
        self._connect_csc_items()

    def _connect_csc_items(self):
        self._view._csc._input_gb._combo_colour_space.currentTextChanged.connect(self._view._csc._input_gb.update_labels)
        self._view._csc._calculate_button.clicked.connect(self.compute_csc)
        self._view._csc._clear_button.clicked.connect(partial(self.clear_labels, self._view._csc))
    
    def _connect_csc_export(self):
        self._view._csc.activate_export_button()
        self._view._csc._export_button.clicked.connect(self.save_csc_as_json)    

    def compute_csc(self):
        # get data
        data = self.get_data(self._view._csc, self._view._csc._input_gb)
        if data["coordinates"] != None:
            csc_coordinates = self._model.compute_colour_space_conversion(data["sample_id"], data["colour_space"], data["illuminant"], data["observer"] , data["coordinates"][0], data["coordinates"][1], data["coordinates"][2])
            #self._view._csc.update_coordinates(csc_coordinates)
            self.update_cordinates(self._view._csc, csc_coordinates)

            if "None" in csc_coordinates["sRGB"]:
                self._view._csc.show_warning_message("The sRGB colour conversion it's only implemented for D65")
            self._connect_csc_export()

    def save_csc_as_json(self):
        self._view._csc.export_as_json()
        #self.clear_csc_labels()

    # CDE - Colour Differences
    def open_cde(self):
        self.close_open_windows()
        self._view.open_cde_view()
        self._connect_cde_items()

    def _connect_cde_items(self):
        self._view._cde._sample_1._combo_colour_space.currentTextChanged.connect(self._view._cde._sample_1.update_labels)
        self._view._cde._sample_2._combo_colour_space.currentTextChanged.connect(self._view._cde._sample_2.update_labels)
        self._view._cde._calculate_button.clicked.connect(self.compute_cde)
        self._view._cde._clear_button.clicked.connect(partial(self.clear_labels, self._view._cde))

    def _connect_cde_zoom(self):
        self._view._cde.activate_zoom_buttons()
        self._view._cde._zoom_button.clicked.connect(self.plot_zoom_cielab)
        self._view._cde._save_button.clicked.connect(partial(self.save_plot, self._view._cde))
    
    def compute_cde(self):
        data_sample_1 = self.get_data(self._view._cde, self._view._cde._sample_1)
        if data_sample_1["coordinates"]!=None:
            data_sample_2 = self.get_data(self._view._cde, self._view._cde._sample_2)
            if data_sample_2["coordinates"] != None:
                coordinates, cie76, ciede2000 = self._model.compute_colour_difference(data_sample_1, data_sample_2)
                # update labels
                self.update_cordinates(self._view._cde, coordinates)
                self._view._cde.update_delta_values(cie76, ciede2000)
                # update sRGB
                r1, g1, b1 = coordinates["sRGB 1"]
                r2, g2, b2 = coordinates["sRGB 2"]
                self._view._cde.update_rgb_figure(r1, g1, b1, r2, g2, b2)
                # update CIELAB plot
                file_default_cielab = Config.instance().data["plot"]["file_default_cielab"]
                path_out_cielab = os.path.join(*[Config.instance().data["coolpi_dir"], *file_default_cielab])
                samples = {data_sample_1["sample_id"]: (float(coordinates["CIELAB 1"][0]), float(coordinates["CIELAB 1"][1]),float(coordinates["CIELAB 1"][2])), 
                    data_sample_2["sample_id"]: (float(coordinates["CIELAB 2"][0]), float(coordinates["CIELAB 2"][1]), float(coordinates["CIELAB 2"][2]))}
                # create figure
                self._model.save_cielab_diagram(samples, path_out_cielab)
                self._view._cde.update_cielab_plot(path_out_cielab)
                # activate and connect buttons
                self._connect_cde_zoom()
            
    # SPC - Spectral Colour
    def open_spc(self):
        self.close_open_windows()
        self._view.open_spc_view()
        self._connect_spc_load_button()

    def _connect_spc_load_button(self):
        self._view._spc._load_button.clicked.connect(self.load_spc_from_json)
    
    def _connect_spc_zoom(self):
        self._view._spc.activate_save_zoom_buttons()
        self._view._spc._zoom_button.clicked.connect(partial(self.plot_zoom_spectral, "Spectral Colour Plot"))
        self._view._spc._save_button.clicked.connect(partial(self.save_plot, self._view._spc))
    
    def _connect_spc_clear_button(self):
        self._view._spc.activate_clear_button()
        self._view._spc._clear_button.clicked.connect(partial(self.clear_labels, self._view._spc))

    def load_spc_from_json(self):
        # clear label first
        self.clear_labels(self._view._spc)
        # load json
        self._view._spc.load_from_json()
        json_data = self._view._spc._json_spectral_data

        if json_data is not None:
            full_update = True
            sample_id = json_data["Sample_id"]
            self._view._spc._spc_input.update_label("sample_id", sample_id)
            observer = json_data["Observer"]
            if self._model.check_spc_labels("observer", observer):
                self._view._spc._spc_input.update_label("observer", observer)
            else:
                full_update = False
                self._view._spc.show_warning_message(f"Incorrect CIE observer {observer}: CIE 2º or 10º standard observer")
                
            illuminant = json_data["Illuminant"]
            if self._model.check_spc_labels("illuminant", illuminant):
                self._view._spc._spc_input.update_label("illuminant", illuminant)
            else:
                full_update = False
                self._view._spc.show_warning_message(f"Incorrect CIE illuminant {illuminant}: CIE D50 or D65")

            nm_range = json_data["nm_range"]
            if self._model.check_spc_labels("nm_range", nm_range):
                self._view._spc._spc_input.update_label("nm_range", nm_range)
            else:
                full_update = False
                self._view._spc.show_warning_message(f"Incorrect \u03BB nm range {nm_range}: [min, max] nm")
    
            nm_interval = json_data["nm_interval"]
            if self._model.check_spc_labels("nm_interval", nm_interval):
                self._view._spc._spc_input.update_label("nm_interval", nm_interval)
            else:
                full_update = False
                self._view._spc.show_warning_message(f"Incorrect nm interval: {nm_interval} not float or int type")  
           
            lambda_values = json_data["lambda_values"]
            if self._model.check_lambda_values(nm_range, nm_interval, lambda_values):
                self._view._spc._spc_input.update_table(lambda_values)
            else:
                full_update = False
                self._view._spc.show_warning_message(f"Incomplete \u03BB spectral data")
        
            if full_update:
                # plot
                self.load_spc_figure()
            else:
                self._view._spc.show_warning_message(f"Incomplete update: Please review the JSON file")

    def load_spc_figure(self):
        json_data = self._view._spc._json_spectral_data
        img_out = Config.instance().data["plot"]["file_default_spectral"]
        path_img_out = os.path.join(*[Config.instance().data["coolpi_dir"], *img_out])
        # create
        spc_colour = self._model.create_spc_figure(json_data, path_img_out)
        # update figure
        self._view._spc._spc_plot_gb.update_figure(path_img_out)
        # colour transform
        coordinates = self._model.compute_colour_coordinates_from_spc(spc_colour)
        # update coordinates
        self._view._spc.update_coordinates(coordinates)
        # update sRGB image
        r, g, b = coordinates["sRGB"]
        self._view._spc.update_srgb_image(int(r), int(g), int(b))
        # activate and connect buttons
        self._connect_spc_zoom()
        self._connect_spc_clear_button()

    # CPT - Colour Plot
    def open_cpt(self):
        self.close_open_windows()
        self._view.open_cpt_view()
        self._connect_cpt_items()

    def _connect_cpt_items(self):
        self._view._cpt._input_gb._combo_colour_space.currentTextChanged.connect(self._view._cpt._input_gb.update_labels)
        self._view._cpt._plot_button.clicked.connect(self.plot_cpt_figures)
        # buttons
        self._view._cpt._zoom_button_cd.clicked.connect(self.plot_zoom_chromaticity)
        self._view._cpt._save_chromaticity_button.clicked.connect(partial(self.save_cpt_plot, "Chromaticity"))
        self._view._cpt._zoom_button_cielab.clicked.connect(self.plot_zoom_cielab)
        self._view._cpt._save_cielab_button.clicked.connect(partial(self.save_cpt_plot, "Cielab"))

    def plot_cpt_figures(self):
        data = self.get_data(self._view._cpt, self._view._cpt._input_gb)
        if data["coordinates"] != None:
            csc_coordinates = self._model.compute_colour_space_conversion(data["sample_id"], data["colour_space"], data["illuminant"], data["observer"] , data["coordinates"][0], data["coordinates"][1], data["coordinates"][2])
            self._view._cpt.update_coordinates(csc_coordinates)
            
            if "None" in csc_coordinates["sRGB"]:
                self._view._cpt.update_default_srgb_image()
                self._view._cpt.show_warning_message("The sRGB colour conversion it's only implemented for D65")
                
            else:
                r, g, b = csc_coordinates["sRGB"]
                self._view._cpt.update_srgb_image(int(r), int(g), int(b))
            
            # chromaticity / cielab
            file_default_chromaticity = Config.instance().data["plot"]["file_default_chromaticity"]
            path_out_chroma = os.path.join(*[Config.instance().data["coolpi_dir"], *file_default_chromaticity])
            file_default_cielab = Config.instance().data["plot"]["file_default_cielab"]
            path_out_cielab = os.path.join(*[Config.instance().data["coolpi_dir"], *file_default_cielab])
            
            self._model.create_chromaticity_and_cielab_plot(data["sample_id"], data["colour_space"], data["illuminant"], data["observer"], data["coordinates"][0], data["coordinates"][1], data["coordinates"][2], path_out_chroma, path_out_cielab)
            #update
            self._view._cpt.update_chromaticity_plot(path_out_chroma)
            self._view._cpt.update_cielab_plot(path_out_cielab)
            self._view._cpt.activate_zoom_buttons()

    def save_cpt_plot(self, plot_name):
        self._view._cpt.save_image(plot_name)

    # SPD - Illuminant SPD Inspector
    def open_spd(self):
        self.close_open_windows()
        self._view.open_spd_view()
        self._connect_spd_items()

    def _connect_spd_items(self):
        self._view._spd.connect_radio_buttons()    
        # buttons
        self._view._spd._plot_button.clicked.connect(self.plot_spd_illuminant)
        self._view._spd._spd_input._load_button.clicked.connect(self._view._spd._spd_input.get_path_csv)
        # combo box change
        self._view._spd._spd_input._combo_illuminant.currentTextChanged.connect(self._view._spd.clear_labels)
        self._view._spd._combo_observer.currentTextChanged.connect(self.spd_observer_change)
    
    def _connect_spd_zoom(self):
        self._view._spd.activate_save_zoom_buttons()
        self._view._spd._zoom_button.clicked.connect(partial(self.plot_zoom_illuminant, "Illuminant SPD Plot"))
        self._view._spd._save_button.clicked.connect(partial(self.save_plot, self._view._spd))
    
    def _connect_spd_clear_button(self):
        self._view._spd.activate_clear_button()
        self._view._spd._clear_button.clicked.connect(partial(self.clear_labels, self._view._spd))

    def plot_spd_illuminant(self):
        # default image
        img_out = Config.instance().data["plot"]["file_default_illuminant"]
        path_img_out = os.path.join(*[Config.instance().data["coolpi_dir"], *img_out])
        # get current plot
        if self._view._spd._spd_input._cie_radio_button.isChecked():
            illuminant_type = "CIE"
            illuminant_name = self._view._spd._spd_input._combo_illuminant.currentText()
            illuminant = self._model.create_spd_figure(illuminant_name, illuminant_type, path_img_out)
        
        elif self._view._spd._spd_input._cct_radio_button.isChecked():
            illuminant_type = "CCT"
            try:
                illuminant_name = float(self._view._spd._spd_input._cct_edit.text())
                illuminant = self._model.create_spd_figure(illuminant_name, illuminant_type, path_img_out)
            except:
                self._view._spd.show_warning_message("The input CCT is not in a valid numeric format")
                return 
        
        elif self._view._spd._spd_input._user_radio_button.isChecked():
            illuminant_type = "Measured"
            illuminant_name = self._view._spd._spd_input._user_name_edit.text()
            path_csv =  self._view._spd._spd_input._user_path_edit.text()
            if path_csv!="":
                if os.path.exists(path_csv):
                    if illuminant_name!="":
                        illuminant = self._model.create_spd_figure(illuminant_name, illuminant_type, path_img_out, path_csv)
                    else:
                        self._view._spd.show_warning_message("The input Illuminant name is empty")
                        return
                else:
                    self._view._spd.show_warning_message("The input CSV/JSON path is not in a valid path")
                    return
            else:
                self._view._spd.show_warning_message("Please, select a valid CSV/JSON")
                return

        nm_range = illuminant.nm_range
        nm_interval = illuminant.nm_interval
        spd = illuminant.lambda_values
        # update labels
        self._view._spd._spd_data.update_label("nm_range", nm_range)
        self._view._spd._spd_data.update_label("nm_interval", nm_interval)
        self._view._spd._spd_data.update_table(spd)
        # update figure
        self._view._spd._spd_plot_gb.update_figure(path_img_out)
        # get observer
        observer = int(self._view._spd._combo_observer.currentText())
        # get WhitePoint
        coordinates = self._model.get_spd_white_point(illuminant, observer, illuminant_type)
        # update coordinates
        self._view._spd.update_coordinates(coordinates)
        # activate and connect buttons
        self._connect_spd_zoom()
        self._connect_spd_clear_button()

    def spd_observer_change(self):
        # plot only if the data is ready
        if self._view._spd._spd_data._interval_edit.text()!="":
            self.plot_spd_illuminant()
            
    # CCI ColourChecker Inspector
    def open_cci(self):
        self.close_open_windows()
        self._view.open_cci_view()
        self._connect_cci_items()

    def _connect_cci_items(self):
        self._view._cci._colourchecker_gb._combo_colourchecker.currentTextChanged.connect(self.get_checker_data)
        self._view._cci._colourchecker_gb._load_button.clicked.connect(self.get_colour_chart_reflectance_from_json)
        self._view._cci._spc_table.itemDoubleClicked.connect(self.update_cci_items)
        self._view._cci._spc_table.itemSelectionChanged.connect(self.update_cci_items)

    def _connect_cci_buttons(self):
        self._view._cci._zoom_button.clicked.connect(partial(self.plot_zoom_spectral, "Spectral Reflectance Plot"))
        self._view._cci._save_button.clicked.connect(partial(self.save_plot, self._view._cci))

    def get_colour_chart_reflectance_from_json(self):
        # reset image
        self._view._cci._spc_plot_gb.update_figure(None)
        self._view._cci.desactivate_buttons()
        #clear selected item table
        self._view._cci._spc_table.clearSelection()
        self._view._cci.load_from_json()
        # get JSON path
        json_data = self._view._cci._json_spectral_data
        if json_data!=None:
            self._metadata = self._model.metadata_from_json(json_data)
            self._view._cci._colourchecker_gb.update_metadata(self._metadata)
            self._colourchecker_name = self._metadata["NameColorChart"] 
            # update colour checker name
            self._view._cci.update_label_checker_name(self._colourchecker_name)
            # update metadata
            self._data_patches = self._metadata["patches"]
            self._view._cci.fill_table(self._data_patches)

    def get_checker_data(self):
        # reset image
        self._view._cci._spc_plot_gb.update_figure(None)
        self._view._cci.desactivate_buttons()
        #clear selected item table
        self._view._cci._spc_table.clearSelection()
        # fill with current data
        self._colourchecker_name = self._view._cci._colourchecker_gb._combo_colourchecker.currentText()
        
        if self._colourchecker_name != "None":
            self._metadata = self._model.get_full_data_colourchecker(self._colourchecker_name)
            self._data_patches = self._metadata["patches"]
            # update metadata
            self._view._cci._colourchecker_gb.update_metadata(self._metadata)
            # update table
            self._view._cci.fill_table(self._data_patches)

    def get_current_patch(self):
        idx = self._view._cci._spc_table.selectionModel().selectedIndexes() # selection mode only one item
        row_selected = idx[0].row()
        patch_id = self._view._cci._spc_table.item(row_selected,0).text()
        return patch_id
    
    def save_current_spectral(self, patch_id, path_img_out):
        self._model.plot_reflectance_patche(patch_id, path_img_out)   

    def compute_XYZ_from_reflectance(self, patch_id):
        coordinates = self._model.patch_spectral_to_XYZ(patch_id)
        return coordinates

    def update_spectral_plot(self, path_img_out):
        self._view._cci._spc_plot_gb.update_figure(path_img_out)
        
    def update_cci_items(self):
        current_patch = self.get_current_patch()
        img_out = Config.instance().data["plot"]["file_default_spectral"]
        path_img_out = os.path.join(*[Config.instance().data["coolpi_dir"], *img_out])
        self.save_current_spectral(current_patch, path_img_out)
        self.update_spectral_plot(path_img_out)
        #active buttons
        self._view._cci.activate_buttons() 
        #update coordinates
        coordinates = self.compute_XYZ_from_reflectance(current_patch)
        self.update_cordinates(self._view._cci, coordinates)
        # update sRGB image
        r, g, b = coordinates["sRGB"]
        self._view._cci.update_srgb_image(int(r), int(g), int(b))
        # connect buttons
        self._connect_cci_buttons()

    # RCIP - RAW Colour Image Processing
    def open_rcip(self):
        self.close_open_windows()
        self._view.open_rcip_view()
        self._connect_rcip_items()

    def _connect_rcip_items(self):
        self._view._rcip._load_button.clicked.connect(self.display_init_raw_image)
        self._view._rcip._plot_button.clicked.connect(self.compute_colour_corrected_image)
        self._view._rcip._export_button.clicked.connect(self.export_colour_corrected_image)
        self._view._rcip._clear_button.clicked.connect(self._view._rcip.clear_labels)
        #rgb to xyz from csv
        self._view._rcip._rgb_to_xyz_gb._load_button.clicked.connect(self.update_rgb_to_xyz_matrix)
        self._view._rcip._wb_gain_gb._apply_wb_button.clicked.connect(self.apply_white_balance_to_raw_image)
        # display

    def display_init_raw_image(self):
        self._view._rcip.clear_labels()
        self._view._rcip.get_image_path()
        path_raw = self._view._rcip._path_image_file

        if path_raw is not None:
            # create the RawImage object
            self._model.create_raw_image(path_raw)
            # save default raw image
            path_default = os.path.join(*[Config.instance().data["coolpi_dir"], *Config.instance().data["rcip"]["default_raw_image"]])
            self._model.save_raw_image(path_default, data="raw", bits=8)
            self.update_processed_image(path_default) # update into Image View
            self._view._rcip.activate_display_button()
            # activate RGB_To_XYZ and WB
            self._view._rcip._rgb_to_xyz_gb.activate_radio_buttons()
            self._view._rcip._wb_gain_gb.activate_radio_buttons()
            self._view._rcip._wb_gain_gb.activate_apply_wb_button()
            # update label
            self._view._rcip._path_gp.update_raw_path_label(path_raw)
    
    def apply_white_balance_to_raw_image(self):
        wb_multipliers = self.get_wb_multipliers()
        if wb_multipliers!=None:
            self._model.compute_white_balanced_raw_image(wb_multipliers)
            # save default
            path_default = os.path.join(*[Config.instance().data["coolpi_dir"], *Config.instance().data["rcip"]["default_wb_image"]])
            self._model.save_raw_image(path_default, data="wb", bits=8)
            self.update_processed_image(path_default) # update into Image View

    def compute_colour_corrected_image(self):
        RGB_to_XYZ = self.get_rgb_to_xyz_matrix()
        if RGB_to_XYZ!= None:
            wb_multipliers = self.get_wb_multipliers()
            if wb_multipliers!=None:
                self._model.compute_colour_corrected_raw_image(wb_multipliers, RGB_to_XYZ)
                # save default
                path_default = os.path.join(*[Config.instance().data["coolpi_dir"], *Config.instance().data["rcip"]["default_colour_corrected"]])
                self._model.save_raw_image(path_default, data="sRGB", bits=8)
                self.update_processed_image(path_default) # update into Image View  
                self._view._rcip.activate_export_button()
    
    def export_colour_corrected_image(self):
        # get path
        self._view._rcip.get_export_image_path()
        output_path = self._view._rcip._output_path_image_file
        if output_path is not None:
            #export 
            output_bits = self._model.get_output_bits_from_extension(output_path)
            self._model.save_raw_image(output_path, data="sRGB", bits=output_bits)
            self._view._rcip.show_save_message(f"Processed image {output_path} saved successfully")
            # update label
            self._view._rcip._path_gp.update_output_path_label(output_path)

    def update_rgb_to_xyz_matrix(self):
        # select csv
        self._view._rcip._rgb_to_xyz_gb.get_path_csv()
        path_csv = self._view._rcip._rgb_to_xyz_gb._path_file_csv
        if path_csv is not None:
            # load data
            rgb_to_xyz_array = self._model.load_matrix_coefficients_from_csv(path_csv)
            if rgb_to_xyz_array is not None: 
                # update
                self._view._rcip._rgb_to_xyz_gb.update_matrix(rgb_to_xyz_array)
            else:
                self._view._rcip.show_warning_message("Unsopported CSV file format. Please, review")
        else:
            self._view._rcip.show_warning_message("The input CSV path is empty. Please, select a valid CSV file")

    def update_processed_image(self, path_img):
        self._view._rcip._image_gp.update_figure(path_img)

    def get_wb_multipliers(self):
        if self._view._rcip._wb_gain_gb._camera_radio_button.isChecked():
            wb_multipliers = "camera" # wb_gain_factors = raw_image.raw_attributes["camera_whitebalance"]
        elif self._view._rcip._wb_gain_gb._daylight_radio_button.isChecked():
            wb_multipliers = "daylight" # wb_gain_factors = raw_image.raw_attributes["daylight_whitebalance"]
        elif self._view._rcip._wb_gain_gb._custom_radio_button.isChecked():
            wb_multipliers = self._view._rcip._wb_gain_gb.get_wb_gain_factors()
            if wb_multipliers is None:
                self._view._rcip.show_warning_message("The Custom white balance multipliers are empty or not in a valid numeric format. Please, review")
                return
        return wb_multipliers

    def get_rgb_to_xyz_matrix(self):
        if self._view._rcip._rgb_to_xyz_gb._auto_radio_button.isChecked():
            rgb_to_xyz_matrix = "camera"
        elif self._view._rcip._rgb_to_xyz_gb._computed_radio_button.isChecked():     
            rgb_to_xyz_matrix = self._view._rcip._rgb_to_xyz_gb.get_rgb_to_xyz_matrix()
            if rgb_to_xyz_matrix is None:
                self._view._rcip.show_warning_message("The Computed RGB To XYZ matrix is empty, imcomplete or not in a valid float format. Please, review")
                return
        return rgb_to_xyz_matrix

    def get_rcip_process_raw_image(self):
        # get the path
        path_raw_image = self._view._rcip._input_image_gb._path_image_file
        # get metadata
        metadata = {} # Not implemented yet. EXIF

        if path_raw_image is not None:


            # WhiteBalance
            if self._view._rcip._wb_gain_gb._none_radio_button.isChecked():
                whitebalance = None # wb_gain_factors = [1.0, 1.0, 1.0, 1.0]
            elif self._view._rcip._wb_gain_gb._camera_radio_button.isChecked():
                whitebalance = "camera" # wb_gain_factors = raw_image.raw_attributes["camera_whitebalance"]
            elif self._view._rcip._wb_gain_gb._daylight_radio_button.isChecked():
                whitebalance = "daylight" # wb_gain_factors = raw_image.raw_attributes["daylight_whitebalance"]
            elif self._view._rcip._wb_gain_gb._custom_radio_button.isChecked():
                whitebalance = self._view._rcip._wb_gain_gb.get_wb_gain_factors()
                if whitebalance is None:
                    self._view._rcip.show_warning_message("The Custom WhiteBalance gain factors are empty or not in a valid numeric format. Please, review")
                    return
            
            # compute raw image
            # output_path
            # name_img
            name_img, _ = self._view._rcip._input_image_gb._name_image_edit.text().split(".")
            # get_name_out
            #name_out = self._view._rcip._output_image_gb._name_out_image_edit.text()
            # update
            #self._view._rcip._output_image_gb.update_name_image(name_out)       
            # compute
            path_jpg, path_tiff = self._model.compute_raw_image(metadata, path_raw_image, whitebalance, rgb_to_xyz_matrix, "prueba")#name_out)
            # process image
            
            # update
            self.update_processed_image(path_jpg)
            # update_labels
            self._view._rcip._output_path_gp.update_labels(path_jpg, path_tiff)
            # activate export buton
            self._view._rcip.activate_export_button()
        else:
            self._view._rcip.show_warning_message("The input image is empty. Please, select a image first")
            
    # Zoom Figure
    def _connect_figure_save_button(self):
        self._view._figure._save_button.clicked.connect(partial(self.save_plot, self._view._figure))

    def plot_zoom_chromaticity(self):
        self.close_open_figure_window()
        window_title = "Chromaticity Diagram" 
        file_default_chromaticity = Config.instance().data["plot"]["file_default_chromaticity"]
        path_out_chroma = os.path.join(*[Config.instance().data["coolpi_dir"], *file_default_chromaticity])
        self._view.open_figure_zoom_view(window_title, path_out_chroma)
        self._connect_figure_save_button()

    def plot_zoom_cielab(self):
        self.close_open_figure_window()
        window_title = "CIELAB Diagram" 
        file_default_cielab = Config.instance().data["plot"]["file_default_cielab"]
        path_out_cielab = os.path.join(*[Config.instance().data["coolpi_dir"], *file_default_cielab])
        self._view.open_figure_zoom_view(window_title, path_out_cielab)
        self._connect_figure_save_button()

    def plot_zoom_spectral(self, window_title):
        self.close_open_figure_window()
        file_default_spc = Config.instance().data["plot"]["file_default_spectral"]
        path_out_spc = os.path.join(*[Config.instance().data["coolpi_dir"], *file_default_spc])
        self._view.open_figure_zoom_view(window_title, path_out_spc)
        self._view._figure._label.setFixedSize(Config.instance().data["zoom_spectral_plot"]["plot_zoom_size"][0], Config.instance().data["zoom_spectral_plot"]["plot_zoom_size"][1])
        self._view._figure.setFixedSize(Config.instance().data["zoom_spectral_plot"]["screen_size"][0], Config.instance().data["zoom_spectral_plot"]["screen_size"][1])
        self._connect_figure_save_button()

    def plot_zoom_illuminant(self, window_title):
        self.close_open_figure_window()
        file_default_spd = Config.instance().data["plot"]["file_default_illuminant"]
        path_out_spd = os.path.join(*[Config.instance().data["coolpi_dir"], *file_default_spd])
        self._view.open_figure_zoom_view(window_title, path_out_spd)
        self._view._figure._label.setFixedSize(Config.instance().data["zoom_spectral_plot"]["plot_zoom_size"][0], Config.instance().data["zoom_spectral_plot"]["plot_zoom_size"][1])
        self._view._figure.setFixedSize(Config.instance().data["zoom_spectral_plot"]["screen_size"][0], Config.instance().data["zoom_spectral_plot"]["screen_size"][1])
        self._connect_figure_save_button()

    # common functions
    def get_data(self, view, view_item):
        data = {}
        data["sample_id"] = view_item._sample_id.text()
        data["colour_space"] = view_item._combo_colour_space.currentText()
        data["illuminant"]  = view_item._combo_illuminant.currentText()
        data["observer"] = int(view_item._combo_observer.currentText())
        # coordinates
        c1 = view_item._c1.text()
        c2 = view_item._c2.text()
        c3 = view_item._c3.text()
        
        if c1 == "" or c2 == "" or c3 == "":
            view.show_warning_message("The input coordinates are empty")
            data["coordinates"] = None
        else:
            try:
                data["coordinates"] = [float(c1), float(c2), float(c3)]
            except:
                data["coordinates"] = None
                view.show_warning_message("The input coordinates are not in a valid numeric format")
        return data

    def update_cordinates(self, view_item, coordinates):
        view_item.update_coordinates(coordinates)

    def clear_labels(self, view_item):
        view_item.clear_labels()

    def save_plot(self, view_item):
        view_item.save_image()

    # Close
    def close_open_windows(self):
        windows_to_close = ["_csc","_cde", "_cpt", "_spc", "_spd", "_cci", "_irgbe", "_lrm", "_rcip"]
        current_items = self._view.__dict__

        for window in windows_to_close:
            if window in current_items:
                item =  current_items[window]
                item.close()

    def close_open_figure_window(self):
        window_to_close = "_figure"
        current_items = self._view.__dict__

        if window_to_close in current_items:
            item =  current_items[window_to_close]
            item.close()

    # Quit
    def quit(self):
        self._view._app.closeAllWindows()
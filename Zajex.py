# -*- coding: utf-8 -*-
"""
Created on 29.01.2024

@author: Zajicek
@author: Vopalensky
"""
import sys
from argparse import ArgumentParser
from queue import Queue

from PyQt5.QtGui import QIcon, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QFileDialog, QDialog
from PyQt5.uic import loadUiType

from tomography import TomographyManagerThread, TomographyManagerWidget
from ui_elements_classes import *
from ui_elements import icon_app, icon_rotate_cw, icon_rotate_ccw, icon_load, icon_save
from utils import *

Ui_MainWindow, QMainWindow = loadUiType('./ui_elements/QtUI/MainWindow.ui')


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, args):
        super(Main, self).__init__()
        self.setupUi(self)
        self.palettes = {'dark': DarkPalette(), 'light': LightPalette()}
        self.setWindowIcon(QIcon(icon_app))
        self.parameters = Parameters()
        self.action_connection()

        if args.shape is not None:
            self.parameters.width, self.parameters.height = args.shape
        self.palette = 'dark'
        app.setPalette(self.palettes['dark'], None)

        self.curr_image = None
        self.last_image_id = None
        self.images = {}
        self.last_action_ = None

        self.loading_queue = Queue()
        self.loading_thread = ImageLoaderThread(self, image_queue=self.loading_queue)
        self.loading_thread.start()

        self.saving_queue = Queue()
        self.saving_thread = ImageSaverThread(self, image_queue=self.saving_queue, images=self.images)
        self.saving_thread.start()

        self.dm_window = None
        self.dm_thread = TomographyManagerThread(self)
        self.dm_thread.new_message.connect(self._new_message)

        input_handling_functions = self._input_handling_functions()
        for signal in input_handling_functions.keys():
            signal.connect(input_handling_functions[signal])

        self.models = {key: QStandardItemModel() for key in ['a', 'b', 'c', 'd']}
        self.list_views = {key: getattr(self, f"lw_{key}") for key in ['a', 'b', 'c', 'd']}
        self.combo_boxes = {key: getattr(self, f"cb_images_{key}") for key in ['a', 'b', 'c', 'd']}
        for key in ['a', 'b', 'c', 'd']:
            getattr(self, f"cb_images_{key}").setView(DragNDropListView())
            getattr(self, f"cb_images_{key}").activated.connect(self._cb_images_handler)
            getattr(self, f"cb_images_{key}").remove_items.connect(self.remove_items_from_model)
            getattr(self, f"tb_load_{key}").clicked.connect(self._pb_load_handler)
            getattr(self, f"tb_load_{key}").setIcon(QIcon(icon_load))
            getattr(self, f"cb_save_{key}").save_signal.connect(self._cb_save_handler)
            getattr(self, f"slider_{key}").valueChanged.connect(self._slider_handler)
            getattr(self, f"lw_{key}").doubleClicked.connect(self._lw_handler)
            getattr(self, f"lw_{key}").remove_items.connect(self.remove_items_from_model)
            getattr(self, f"lw_{key}").delete_items.connect(self.delete_items)
            getattr(self, f"canvas_{key}").selection_changed.connect(self._selection_changed)
            getattr(self, f"canvas_{key}").pixel_selected.connect(self.plot_histogram)

            self.list_views[key].setModel(self.models[key])
            self.combo_boxes[key].setModel(self.models[key])
            getattr(self, f"lw_{key}").set_move_mode("move")

        self.sliders = {key: getattr(self, f"slider_{key}") for key in ['a', 'b', 'c', 'd']}
        self.spin_boxes = {
            "lower": self.dsb_lower,
            "upper": self.dsb_upper,
            "rows_from": self.sb_rows_from,
            "rows_to": self.sb_rows_to,
            "columns_from": self.sb_columns_from,
            "columns_to": self.sb_columns_to,
        }
        self.collapsible_widgets = [self.gb_intensity, self.gb_zoom, self.gb_parameters, self.gb_histogram,
                                    self.gb_rot_mir, self.gb_a, self.gb_b, self.gb_c, self.gb_d, ]
        self._init_gui_values()
        self.id_gen = id_generator()
        self.console_widget.get_locals()['images'] = self.images
        self.console_widget.get_locals()['app'] = self

    def _init_gui_values(self):
        for cmap in cmaps_list:
            self.cb_colormaps.addItem(cmap)

        for f in supportedSaveFormats:
            for key in ['a', 'b', 'c', 'd']:
                getattr(self, f"cb_save_{key}").addItem(QIcon(icon_save), f"[{f}]")
            self.cb_save_current.addItem(f"Save current image [{f}]")

        for r in limits_dict.values():
            self.cb_auto_range.addItem(r)

        for i in rotation_list:
            self.cb_rotation.addItem(i)

        self.pb_rotate_cw.setIcon(QIcon(icon_rotate_cw))
        self.pb_rotate_ccw.setIcon(QIcon(icon_rotate_ccw))

        for s in self.sliders:
            if s not in ['upper', "lower"]:
                self.sliders[s].setRange(0, 0)

    def _input_handling_functions(self):
        return {
            # Figure settings
            # - Intensity values
            self.cb_colormaps.currentIndexChanged: self._cb_colormaps_handler,
            self.range_slider.lowerValueChanged: self.dsb_lower.setValue,
            self.range_slider.upperValueChanged: self.dsb_upper.setValue,
            self.dsb_upper.valueChanged: self._dsb_limits_handler,
            self.dsb_lower.valueChanged: self._dsb_limits_handler,
            self.cb_auto_range.currentIndexChanged: self._cb_auto_range_handler,
            self.cb_from_zoom.stateChanged: self._cb_from_zoom_handler,
            self.pb_apply_all_range.clicked: self._pb_apply_all_handler,
            # - Zoomed Area
            self.sb_rows_from.editingFinished: self._sb_rows_handler,
            self.sb_rows_to.editingFinished: self._sb_rows_handler,
            self.sb_columns_from.editingFinished: self._sb_columns_handler,
            self.sb_columns_to.editingFinished: self._sb_columns_handler,
            self.pb_unzoom.clicked: self._un_zoom,
            self.pb_apply_all_zoom.clicked: self._pb_apply_all_handler,
            # - Histogram
            self.slider_bins.valueChanged: self._slider_bins_handler,
            # - Rotation and Mirror
            self.cb_rotation.currentIndexChanged: self._rotation_handler,
            self.pb_rotate_ccw.clicked: self._rotation_handler,
            self.pb_rotate_cw.clicked: self._rotation_handler,
            self.cb_mirror_ud.stateChanged: self._mirror_handler,
            self.cb_mirror_lr.stateChanged: self._mirror_handler,
            self.pb_apply_all_rot.clicked: self._pb_apply_all_handler,
            # - Save Current
            self.cb_save_current.save_signal: self._cb_save_handler,

            # Other
            self.loading_thread.image_loaded: lambda _args: self._image_loader_handler(*_args),
            self.loading_thread.last_image: self._last_image_handler,
            self.saving_thread.image_saved: self._image_saver_handler,
            self.saving_thread.delete_signal: self._remove_handler,
            self.le_operation.return_pressed: self._le_operation_handler,
        }

    def action_connection(self):
        self.aSetInputParams.triggered.connect(self._set_input_parameters)
        self.aSwitchTheme.triggered.connect(self.switch_theme)
        self.a_Settings.triggered.connect(self._show_settings)
        self.a_Batch_Processing.triggered.connect(self._batch_processing)
        self.a_Load_Images.triggered.connect(self._a_load_images_handler)
        self.a_Save_Image.triggered.connect(self._a_save_image_handler)
        self.a_Tomography.triggered.connect(self._tomography_handler)

    def _set_input_parameters(self):
        dialog = FileInfoDialog(self, self.parameters, ftype="bin")
        if dialog.exec_() == QDialog.Accepted:
            self.parameters.width = dialog.result["width"]
            self.parameters.height = dialog.result["height"]
            self.parameters.dtype = dialog.result["dtype"]

    def _show_settings(self):
        dialog = SettingsDialog(self, self.parameters, ftype="bin")
        if dialog.exec_() == QDialog.Accepted:
            self.parameters.width = dialog.result["width"]
            self.parameters.height = dialog.result["height"]
            self.parameters.dtype = dialog.result["dtype"]
            self.parameters.show_axes = dialog.result["show_axes"]
            self.parameters.ratio = dialog.result["ratio"]

    def _batch_processing(self):
        dialog = BatchDialog(self, self.parameters)
        if dialog.exec_() == QDialog.Accepted:
            pass

    def switch_theme(self):
        if self.palette == 'dark':
            self.palette = 'light'
            app.setPalette(self.palettes['light'], None)
        elif self.palette == 'light':
            self.palette = 'dark'
            app.setPalette(self.palettes['dark'], None)

    def remove_items_from_model(self, im_ids):
        """
        Move image with im_id to slot
        :param im_ids: list of ids of image to move
        """
        old_slot = self.images[im_ids[0]].slot
        model = self.models[old_slot]

        for im_id in im_ids:
            for row in range(model.rowCount()):
                item = model.item(row, 0)
                if item.data(Qt.UserRole, ) == im_id:
                    model.removeRow(row)
                    break

        self.sliders[old_slot].blockSignals(True)
        self.sliders[old_slot].setMaximum(model.rowCount() - 1)
        self.sliders[old_slot].blockSignals(False)

    def delete_items(self, im_ids):
        for im_id in im_ids:
            self.images.pop(im_id)

    def _cb_colormaps_handler(self):
        self.parameters.cmap = self.cb_colormaps.currentText()
        self.canvas_a.redraw()
        self.plot_histogram()

    def _dsb_limits_handler(self):
        value = self.sender().value()
        side = self.sender().objectName().split('_')[-1]
        r_slider = self.range_slider
        glimits = r_slider.lowerValue(), r_slider.upperValue()
        letter = "a"

        self.last_action_ = "m"
        if self.curr_image is None:
            return

        if glimits[0] <= value <= glimits[1]:
            r_slider.blockSignals(True)
            if side == "lower":
                self.curr_image.vmin = value
                getattr(self, f"canvas_{letter}").set_vmin(value)
                # if letter in self.windows: self.windows[letter].set_vmin(value)
                r_slider.setLowerValue(value)
            else:
                self.curr_image.vmax = value
                getattr(self, f"canvas_{letter}").set_vmax(value)
                # if letter in self.windows: self.windows[letter].set_vmax(value)
                r_slider.setUpperValue(value)
            r_slider.blockSignals(False)
        else:
            if side == "lower":
                self.dsb_lower.setValue(glimits[0])
            else:
                self.dsb_upper.setValue(glimits[1])

    def _cb_auto_range_handler(self):
        if self.curr_image is None:
            return
        self.last_action_ = "a"
        if self.parameters.from_zoom:
            arr = arr_from_zoom(self.curr_image.array, (self.curr_image.x_lim, self.curr_image.y_lim))
        else:
            arr = self.curr_image.array

        idx = self.cb_auto_range.currentIndex()
        self.curr_image.vmin, self.curr_image.vmax = limits_func(arr, idx)
        self.range_slider.setRange(self.curr_image.vmin, self.curr_image.vmax)
        self.canvas_a.redraw()
        self.plot_histogram()

    def _cb_from_zoom_handler(self):
        self.parameters.from_zoom = self.cb_from_zoom.isChecked()
        self.show_image(self.curr_image.id_)

    def _pb_apply_all_handler(self):
        pb = self.sender().objectName().split('_')[-1]
        if pb == "zoom":
            for img in self.images:
                self.images[img].x_lim = self.curr_image.x_lim
                self.images[img].y_lim = self.curr_image.y_lim
        if pb == 'range':
            for img in self.images.values():
                if self.last_action_ == "m":
                    img.vmax = self.curr_image.vmax
                    img.vmin = self.curr_image.vmin
                elif self.last_action_ == "a":
                    img.vmin, img.vmax = limits_func(img.array, self.cb_auto_range.currentIndex())
                else:
                    pass
        if pb == 'rot':
            for img in self.images:
                self.images[img].rotation = self.curr_image.rotation
                self.images[img].mirror_UD = self.curr_image.mirror_UD
                self.images[img].mirror_LR = self.curr_image.mirror_LR

    def _sb_rows_handler(self):
        self.curr_image.y_lim = (self.sb_rows_to.value(), self.sb_rows_from.value())
        self.canvas_a.redraw()

    def _sb_columns_handler(self):
        self.curr_image.x_lim = (self.sb_columns_from.value(), self.sb_columns_to.value())
        self.canvas_a.redraw()

    def _un_zoom(self):
        if self.curr_image is None:
            return
        arr = self.curr_image.array
        self.curr_image.x_lim = (0, arr.shape[1])
        self.curr_image.y_lim = (arr.shape[0], 0)
        self.canvas_a.redraw()
        self.plot_histogram()
        self._init_image_info_values()

    def _slider_bins_handler(self, event):
        self.parameters.num_bins = event
        self.plot_histogram()

    def _rotation_handler(self):
        if self.curr_image is None:
            return
        sender = self.sender().objectName()
        if "pb" in sender:
            pb = sender.split("_")[-1]
            if pb == "cw":
                self.cb_rotation.setCurrentIndex((self.cb_rotation.currentIndex() + 1) % 4)
            elif pb == "ccw":
                self.cb_rotation.setCurrentIndex((self.cb_rotation.currentIndex() - 1) % 4)
        else:
            old_rotation = self.curr_image.rotation
            index = self.cb_rotation.currentIndex()
            self.curr_image.array = np.rot90(self.curr_image.array, (index - old_rotation) % 4)
            self.curr_image.rotation = index
            self.canvas_a.redraw()

    def _mirror_handler(self, event):
        sender = self.sender().objectName().split("_")[-1]
        if sender == "ud":
            self.curr_image.array = np.flipud(self.curr_image.array)
            if event == 0:
                self.curr_image.mirror_UD = False
            elif event == 2:
                self.curr_image.mirror_UD = True
        elif sender == "lr":
            self.curr_image.array = np.fliplr(self.curr_image.array)
            if event == 0:
                self.curr_image.mirror_LR = False
            elif event == 2:
                self.curr_image.mirror_LR = True
        self.canvas_a.redraw()

    def _cb_images_handler(self, event):
        group = self.sender().objectName().split('_')[-1]
        self.sliders[group].blockSignals(True)
        self.sliders[group].setValue(event)
        im_id = self.combo_boxes[group].itemData(event, Qt.UserRole)
        self.show_image(im_id)
        self.sliders[group].blockSignals(False)

    def _pb_load_handler(self):
        group = self.sender().objectName().split("_")[-1]
        self._load_images(group)

    def _load_images(self, group):
        filenames, filter_ = QFileDialog.getOpenFileNames(self, "Load images...",
                                                          self.parameters.last_dir, lFileTypeString,
                                                          initialFilter="All files (*.*)")
        if not filenames:
            return
        self.parameters.last_dir = filenames[0][:filenames[0].rfind("/")]
        self.open_files(filenames, group)

    def _a_save_image_handler(self):
        dialog = SaveImagesDialog(self, self.models, self.saving_queue)
        if dialog.exec_():
            self.saving_thread.wake()

            if dialog.result is None:
                return
            models = dialog.result
            for model in ["a", "b", "c", "d"]:
                model_new = models[model]
                self.models[model] = model_new
                self.list_views[model].setModel(model_new)
                self.combo_boxes[model].setModel(model_new)

    def open_files(self, filepaths: list, group: str):
        for filepath in filepaths:
            valid = False
            while not valid:
                valid = validate_input(filepath, self.parameters)
                if valid is None or valid:
                    break
                dialog = FileInfoDialog(self, self.parameters, ftype=filepath.split(".")[-1])
                if dialog.exec_() == QDialog.Accepted:
                    self.parameters.width = dialog.result["width"]
                    self.parameters.height = dialog.result["height"]
                    self.parameters.dtype = dialog.result["dtype"]
                    self.parameters.header = dialog.result["header"]
                else:
                    valid = None
                    break
            if valid is None:
                self.log(f"File \"{filepath}\" could not be loaded.", LogTypes.Error)
            else:
                self.loading_queue.put((filepath, self.parameters, group))

        self.statusbar.start_progress(self.loading_queue.qsize())
        self.loading_thread.wake()

    def save_image(self, arr_im_id, ftype, kwargs):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save images", "",
                                                   save_formats_strings[ftype], )
        if file_path != "":
            self.saving_queue.put((arr_im_id, ftype, file_path, kwargs))

    def _cb_save_handler(self):
        if self.curr_image is None:
            return
        combo = self.sender().objectName().split("_")[-1]
        ftype = self.sender().currentText().split("[")[-1][:3]

        if ftype in ["jpg", "png"]:
            kwargs = {"dtype": "uint8"}
        else:
            kwargs = {"dtype": "uint16"}

        # if ftype == 'raw':
        #     kwargs['header'] = header

        if combo == "current":
            self.save_image(self.curr_image.id_, ftype, kwargs)
        else:
            file_path = QFileDialog.getExistingDirectory(self, f"Save images from {combo}", "")
            if file_path != "":
                combo = self.combo_boxes[combo]
                for i in range(combo.count()):
                    im_id = combo.get_custom_item(i).data(Qt.UserRole, )
                    self.saving_queue.put((im_id, ftype, file_path, kwargs))
                self._save_images()

    def _save_images(self):
        self.statusbar.start_progress(self.saving_queue.qsize())
        self.saving_thread.wake()

    def _slider_handler(self, event):
        group = self.sender().objectName().split("_")[-1]
        self.combo_boxes[group].blockSignals(True)
        self.combo_boxes[group].setCurrentIndex(event)
        im_id = self.combo_boxes[group].get_custom_item(event).data(Qt.UserRole, )
        self.show_image(im_id)
        self.combo_boxes[group].blockSignals(False)

    def _le_operation_handler(self):
        from scipy.fftpack import fft2, ifft2
        text = self.le_operation.text()
        combo = self.combo_boxes['d']
        slider = self.sliders['d']
        fp_a, fp_b, fp_c, fp_d = "", "", "", ""

        for slot in ["a", "b", "c", "d"]:
            if self.combo_boxes[slot].count() > 0:
                locals()[f"im_{slot}"] = self.images[self.combo_boxes[slot].get_current_item().data(Qt.UserRole, )]
                locals()[slot] = locals()[slot.upper()] = locals()[f"im_{slot}"].array
                locals()[f"fp_{slot}"] = locals()[f"im_{slot}"].filepath

        try:
            image = eval(str(text))
        except Exception as e:
            self.log(f"Operation failed. It was not possible to perform the required calculation.\n{e}", LogTypes.Error)
            return

        tooltip = text.replace("a", "\t").replace("b", '\n').replace("c", '\r')
        tooltip = tooltip.replace("\t", f"[{fp_a.split('/')[-1]}]").replace("\n", f"[{fp_b.split('/')[-1]}]")
        tooltip = tooltip.replace("\r", f"[{fp_c.split('/')[-1]}]") + "/" + text

        im_id = next(self.id_gen)
        self.images[im_id] = ImageObject(image, image.min(), image.max(), (0, image.shape[1]),
                                         (image.shape[0], 0), im_id, "d", tooltip)
        item = create_item(self.images[im_id], im_id)
        self.models["d"].insertRow(0, item)

        slider.setMaximum(combo.count() - 1)
        slider.blockSignals(True)
        slider.setValue(0)
        slider.blockSignals(False)
        combo.setCurrentIndex(0)
        self.show_image(im_id)

    def _image_loader_handler(self, arr, filepath, slot, id_=-1):
        if arr is not None:
            if id_ == -1:
                im_id = next(self.id_gen)
                name = filepath.split("/")[0]
                self.sender().worker_tabs[name].current_id = im_id
            else:
                im_id = id_
            self.sliders[slot].blockSignals(True)
            self.combo_boxes[slot].blockSignals(True)
            img = ImageObject(arr, arr.min(), arr.max(), (0, arr.shape[1]), (arr.shape[0], 0), im_id, slot, filepath)
            self.images[im_id] = img
            self.last_image_id = im_id

            item = create_item(img, im_id)
            self.models[slot].insertRow(0, item)

            self.log(f"File \"{filepath}\" loaded with ID: {im_id} in slot: {slot.upper()}.", LogTypes.Log)
            self.sliders[slot].setMaximum(self.combo_boxes[slot].count() - 1)
            self.sliders[slot].blockSignals(False)
            self.combo_boxes[slot].blockSignals(False)

        else:
            self.log(f"File \"{filepath}\" could not be loaded.", LogTypes.Error)
        self.statusbar.add_progress()

    def _last_image_handler(self, *args):
        self.show_image(self.last_image_id)

    def _image_saver_handler(self, file):
        self.log(f"Saved \"{file}\"")
        self.statusbar.add_progress()

    def _remove_handler(self, im_id):
        if im_id not in self.images.keys():
            return
        if im_id == self.canvas_a.image.id_:
            self.canvas_a.reset_canvas()
            self.canvas_histogram.reset_canvas()
        self.images.pop(im_id)

    def _init_image_info_values(self):
        if self.curr_image is None:
            return
        for sb in self.spin_boxes.values():
            sb.blockSignals(True)
        self.range_slider.setRange(self.curr_image.vmin, self.curr_image.vmax)

        self.spin_boxes['rows_from'].setRange(0, self.curr_image.y_lim[0])
        self.spin_boxes['rows_from'].setValue(self.curr_image.y_lim[1])
        self.spin_boxes['rows_to'].setRange(0, self.curr_image.y_lim[0])
        self.spin_boxes['rows_to'].setValue(self.curr_image.y_lim[0])
        self.spin_boxes['columns_from'].setRange(0, self.curr_image.x_lim[1])
        self.spin_boxes['columns_from'].setValue(self.curr_image.x_lim[0])
        self.spin_boxes['columns_to'].setRange(0, self.curr_image.x_lim[1])
        self.spin_boxes['columns_to'].setValue(self.curr_image.x_lim[1])

        self.l_im_mean.setText(str(self.curr_image.array.mean()))
        self.l_im_sigma.setText(str(self.curr_image.array.std()))
        arr_zoom = arr_from_zoom(self.curr_image.array, (self.curr_image.x_lim, self.curr_image.y_lim))
        self.l_range_mean.setText(str(arr_zoom.mean()))
        self.l_range_sigma.setText(str(arr_zoom.std()))

        for sb in self.spin_boxes.values():
            sb.blockSignals(False)

    def _selection_changed(self, limits):
        self.canvas_a.set_camera_range(limits)
        # if l in self.windows: self.windows[l].set_camera_range(limits)
        (x_min, x_max), (y_max, y_min) = limits
        self.curr_image.x_lim, self.curr_image.y_lim = (int(x_min), int(x_max)), (int(y_max), int(y_min))
        if self.parameters.from_zoom:
            arr = arr_from_zoom(self.curr_image.array, (self.curr_image.x_lim, self.curr_image.y_lim))
            self.curr_image.vmin = arr.min()
            self.curr_image.vmax = arr.max()
        self._init_image_info_values()
        self.plot_histogram()

    def _lw_handler(self, event):
        group = self.sender().objectName().split('_')[-1]
        self.sliders[group].blockSignals(True)
        self.sliders[group].setValue(event.row())
        im_id = self.list_views[group].get_custom_item(event).data(Qt.UserRole, )
        self.show_image(im_id)
        self.sliders[group].blockSignals(False)

    def _a_load_images_handler(self, event):
        dialog = LoadImagesDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            group = dialog.result
            self._load_images(group)

    def _tomography_handler(self):
        self.dm_thread.start()
        self.dm_window = TomographyManagerWidget(None, self)
        self.dm_thread.worker_initialized.connect(lambda args: self.dm_window.worker_initialized(*args))
        self.dm_window.new_image.connect(lambda args: self._image_loader_handler(*args))
        self.dm_window.new_image.connect(self._last_image_handler)
        self.dm_window.show()

    def _new_message(self, message):
        """
        Handle new message from DetectorManagerThread
        :param message: message to log
        """
        if self.dm_window is not None:
            try:
                self.dm_window.new_message(*message)
            except Exception as e:
                self.log(e, LogTypes.Error)
        else:
            self.log(*message)

    def plot_histogram(self, value=None):
        self.parameters.num_bins = self.slider_bins.value()
        if len(self.images) == 0:
            return
        self.canvas_histogram.plot_histogram(self.curr_image, self.parameters, value)

    def show_image(self, im_id):
        image = self.images[im_id]
        self.curr_image = image
        self.cb_auto_range.setCurrentIndex(0)

        if self.parameters.from_zoom:
            arr = arr_from_zoom(self.curr_image.array, (self.curr_image.x_lim, self.curr_image.y_lim))
            self.curr_image.vmin = arr.min()
            self.curr_image.vmax = arr.max()
        self.canvas_a.show_image(image)
        self.plot_histogram()
        self._init_image_info_values()

    def log(self, text, log_type=LogTypes.Log):
        if log_type == LogTypes.Log:
            text = f"<font color='green'>{text}</font>"
        elif log_type == LogTypes.Warning:
            text = f"<font color='yellow'>Warning: {text}</font>"
        elif log_type == LogTypes.Error:
            text = f"<font color='red'>{text}</font>"
        self.log_widget.append(text)

    def resizeEvent(self, event):
        self.gb_fig_settings.setFixedWidth(int(event.size().width() / 6))
        self.dockWidget.setFixedWidth(int(event.size().width() / 6))
        for el in self.collapsible_widgets:
            el.set_content_layout()
        super().resizeEvent(event)

    def closeEvent(self, event):
        self.loading_thread.requestInterruption()
        self.loading_thread.wake()
        self.saving_thread.requestInterruption()
        self.saving_thread.wake()
        if self.dm_thread.isRunning():
            self.dm_thread.wake()
            self.dm_thread.wait()
        event.accept()
        app.exit(0)


if __name__ == '__main__':
    parser = ArgumentParser(
        prog="Zajex",
        description='',
        epilog="")
    parser.add_argument("-s", "--shape", nargs=2, type=int, metavar=("width", "height"),
                        help="Shape of input images")
    cmd_args = parser.parse_args()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    main = Main(cmd_args)

    main.show()
    app.exec_()

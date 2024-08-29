# -*- coding: utf-8 -*-
"""
Created on 29.01.2024

@author: Zajicek
@author: Vopalensky
"""
import sys
from argparse import ArgumentParser
from queue import Queue

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QFileDialog, QDialog, QAction
from PyQt5.uic import loadUiType

from ui_elements_classes import *
try:
    from detectors import DetectorManager
    detectors_available = True
except ImportError as e:
    print(e)
    DetectorManager = None
    detectors_available = False
from utils.ImageLoaderThread import ImageLoaderThread
from utils.ImageSaverThread import ImageSaverThread
from utils.global_vars import *
from utils.utils import *

Ui_MainWindow, QMainWindow = loadUiType('./ui_elements/MainWindow.ui')
icon_path = './ui_elements/icon_64x.png'
icon_rotate_cw_path = './ui_elements/arrow_rotate_cw.png'
icon_rotate_ccw_path = './ui_elements/arrow_rotate_ccw.png'


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, args):
        super(Main, self).__init__()
        self.setupUi(self)
        self.palettes = {'dark': DarkPalette(), 'light': LightPalette()}
        self.setWindowIcon(QIcon(icon_path))
        self.parameters = Parameters()
        self.dm_thread = None
        if detectors_available:
            self.a_Detector_Manager = QAction("Detector Manager", self)
            self.menuTools.addAction(self.a_Detector_Manager)
            self.a_Detector_Manager.triggered.connect(self._detector_manager)
            self.dm_queue = Queue()
            self.dm_thread = DetectorManager(self, self.dm_queue)
            self.dm_thread.message_received.connect(lambda x: self.log(x, LogTypes.Log))
            self.dm_thread.frame_received.connect(self._image_loader_handler)
            self.dm_thread.start()
            self.dm_window = None
        self.action_connection()

        if args.shape is not None:
            self.parameters.width, self.parameters.height = args.shape
        self.palette = 'dark'
        app.setPalette(self.palettes['dark'], None)

        self.curr_image = None
        self.last_image_id = None
        self.images = {}

        self.loading_queue = Queue()
        self.loading_thread = ImageLoaderThread(self, image_queue=self.loading_queue)
        self.loading_thread.start()

        self.saving_queue = Queue()
        self.saving_thread = ImageSaverThread(self, image_queue=self.saving_queue, images=self.images)
        self.saving_thread.start()

        input_handling_functions = self._input_handling_functions()
        for signal in input_handling_functions.keys():
            signal.connect(input_handling_functions[signal])

        self.combo_boxes = {
            "a": self.cb_images_a,
            "b": self.cb_images_b,
            "c": self.cb_images_c,
            "d": self.cb_images_d,
        }
        self.list_views = {
            "a": self.lw_a,
            "b": self.lw_b,
            "c": self.lw_c,
            "d": self.lw_d,
        }
        self.sliders = {
            "a": self.slider_a,
            "b": self.slider_b,
            "c": self.slider_c,
            "d": self.slider_d,
            "lower": self.slider_lower,
            "upper": self.slider_upper
        }
        self.spin_boxes = {
            "lower": self.dsb_lower,
            "upper": self.dsb_upper,
            "rows_from": self.sb_rows_from,
            "rows_to": self.sb_rows_to,
            "columns_from": self.sb_columns_from,
            "columns_to": self.sb_columns_to,
        }
        self.models = {
            "a": QStandardItemModel(),
            "b": QStandardItemModel(),
            "c": QStandardItemModel(),
            "d": QStandardItemModel()
        }
        for model in self.models.keys():
            self.combo_boxes[model].set_custom_model(self.models[model])
            self.list_views[model].set_custom_model(self.models[model])

        self.collapsible_widgets = [self.gb_intensity, self.gb_zoom, self.gb_parameters, self.gb_histogram,
                                    self.gb_rot_mir, self.gb_a, self.gb_b, self.gb_c, self.gb_d,]
        self._init_gui_values()
        self.id_gen = id_generator()
        self.console_widget.get_locals()['images'] = self.images
        self.console_widget.get_locals()['app'] = self

    def _init_gui_values(self):
        for cmap in cmaps_list:
            self.cb_colormaps.addItem(cmap)

        for f in supportedSaveFormats:
            self.cb_save_a.addItem(f"Save all in A [{f}]")
            self.cb_save_b.addItem(f"Save all in B [{f}]")
            self.cb_save_c.addItem(f"Save all in C [{f}]")
            self.cb_save_d.addItem(f"Save all calculated [{f}]")
            self.cb_save_current.addItem(f"Save current image [{f}]")

        for r in limits_dict.values():
            self.cb_auto_range.addItem(r)

        for i in rotation_list:
            self.cb_rotation.addItem(i)

        self.pb_rotate_cw.setIcon(QIcon(icon_rotate_cw_path))
        self.pb_rotate_ccw.setIcon(QIcon(icon_rotate_ccw_path))

        for s in self.sliders:
            if s not in ['upper', "lower"]:
                self.sliders[s].setRange(0, 0)

    def _input_handling_functions(self):
        return {
            # Figure settings
            # - Intensity values
            self.cb_colormaps.currentIndexChanged: self._cb_colormaps_handler,
            self.slider_lower.sliderReleased: self._slider_limits_handler,
            self.slider_upper.sliderReleased: self._slider_limits_handler,
            self.dsb_upper.editingFinished: self._dsb_limits_handler,
            self.dsb_lower.editingFinished: self._dsb_limits_handler,
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

            # Assets
            # - A
            self.cb_images_a.activated: self._cb_images_handler,
            self.cb_images_a.item_changed: self._item_changed,
            self.pb_load_a.clicked: self._pb_load_handler,
            self.cb_save_a.save_signal: self._cb_save_handler,
            self.slider_a.valueChanged: self._slider_handler,
            # - B
            self.cb_images_b.activated: self._cb_images_handler,
            self.cb_images_b.item_changed: self._item_changed,
            self.pb_load_b.clicked: self._pb_load_handler,
            self.cb_save_b.save_signal: self._cb_save_handler,
            self.slider_b.valueChanged: self._slider_handler,
            # - C
            self.cb_images_c.activated: self._cb_images_handler,
            self.cb_images_c.item_changed: self._item_changed,
            self.pb_load_c.clicked: self._pb_load_handler,
            self.cb_save_c.save_signal: self._cb_save_handler,
            self.slider_c.valueChanged: self._slider_handler,
            # - Operation
            self.cb_images_d.activated: self._cb_images_handler,
            self.cb_images_d.item_changed: self._item_changed,
            self.le_operation.returnPressed: self._le_operation_handler,
            self.cb_save_d.save_signal: self._cb_save_handler,
            self.slider_d.valueChanged: self._slider_handler,

            # Other
            self.loading_thread.image_loaded: self._image_loader_handler,
            self.loading_thread.last_image: self._last_image_handler,
            self.saving_thread.image_saved: self._image_saver_handler,
            self.saving_thread.delete_signal: self._remove_handler,
            self.canvas_main.selection_changed: self._selection_changed,
            self.canvas_main.pixel_selected: self.plot_histogram,

            # List Views
            self.lw_a.doubleClicked: self._lw_handler,
            self.lw_b.doubleClicked: self._lw_handler,
            self.lw_c.doubleClicked: self._lw_handler,
            self.lw_d.doubleClicked: self._lw_handler,

            self.lw_a.itemChanged: self._item_changed,
            self.lw_b.itemChanged: self._item_changed,
            self.lw_c.itemChanged: self._item_changed,
            self.lw_d.itemChanged: self._item_changed,
        }

    def action_connection(self):
        self.aSetInputParams.triggered.connect(self._set_input_parameters)
        self.aSwitchTheme.triggered.connect(self.switch_theme)
        self.a_Settings.triggered.connect(self._show_settings)
        self.a_Batch_Processing.triggered.connect(self._batch_processing)
        self.a_Load_Images.triggered.connect(self._a_load_images_handler)
        self.a_Save_Image.triggered.connect(self._a_save_image_handler)

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

    def _cb_colormaps_handler(self):
        self.parameters.cmap = self.cb_colormaps.currentText()
        self.canvas_main.redraw()
        self.plot_histogram()

    def _slider_limits_handler(self):
        if self.curr_image is None:
            return
        arr = self.curr_image.array
        if self.parameters.from_zoom:
            arr = self._arr_from_zoom()
        arr_diff = arr.max() - arr.min()
        slider = self.sender().objectName().split('_')[-1]
        value = self.sender().value()

        if slider == "upper":
            if value <= self.sliders["lower"].value():
                self.sender().setValue(self.sliders["lower"].value() + 1)
                return
            self.curr_image.vmax = value * arr_diff / 100 + arr.min()
        elif slider == "lower":
            if value >= self.sliders["upper"].value():
                self.sender().setValue(self.sliders["upper"].value() - 1)
                return
            self.curr_image.vmin = value * arr_diff / 100 + arr.min()

        self.spin_boxes[slider].blockSignals(True)
        self.spin_boxes[slider].setValue(value * arr_diff / 100)
        self.spin_boxes[slider].blockSignals(False)
        self.canvas_main.redraw()
        self.plot_histogram()

    def _dsb_limits_handler(self):
        value = self.sender().value()
        spin_box = self.sender().objectName().split('_')[-1]
        if self.curr_image is None:
            return
        arr = self.curr_image.array
        if self.parameters.from_zoom:
            arr = self._arr_from_zoom()
        if spin_box == "upper":
            self.curr_image.vmax = value
        elif spin_box == 'lower':
            self.curr_image.vmin = value
        self.sliders[spin_box].blockSignals(True)
        self.sliders[spin_box].setValue(int(100 * value / (arr.max() - arr.min())))
        self.sliders[spin_box].blockSignals(False)
        self.canvas_main.redraw()
        self.plot_histogram()

    def _cb_auto_range_handler(self):
        if self.curr_image is None:
            return

        if self.parameters.from_zoom:
            arr = self._arr_from_zoom()
        else:
            arr = self.curr_image.array

        idx = self.cb_auto_range.currentIndex()
        self.curr_image.vmin, self.curr_image.vmax = limits(arr, idx)

        for el in [self.sliders['upper'], self.sliders['lower'], self.dsb_lower, self.dsb_upper]:
            el.blockSignals(True)
        arr_diff = self.curr_image.array.max() - self.curr_image.array.min()
        self.sliders['lower'].setValue(int(100 * self.curr_image.vmin / arr_diff))
        self.sliders['upper'].setValue(int(100 * self.curr_image.vmax / arr_diff))
        self.dsb_lower.setValue(self.curr_image.vmin)
        self.dsb_upper.setValue(self.curr_image.vmax)
        for el in [self.sliders['upper'], self.sliders['lower'], self.dsb_lower, self.dsb_upper]:
            el.blockSignals(False)
        self.canvas_main.redraw()
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
            for img in self.images:
                self.images[img].vmax = self.curr_image.vmax
                self.images[img].vmin = self.curr_image.vmin
        if pb == 'rot':
            for img in self.images:
                self.images[img].rotation = self.curr_image.rotation
                self.images[img].mirror_UD = self.curr_image.mirror_UD
                self.images[img].mirror_LR = self.curr_image.mirror_LR

    def _sb_rows_handler(self):
        self.curr_image.y_lim = (self.sb_rows_to.value(), self.sb_rows_from.value())
        self.canvas_main.redraw()

    def _sb_columns_handler(self):
        self.curr_image.x_lim = (self.sb_columns_from.value(), self.sb_columns_to.value())
        self.canvas_main.redraw()

    def _un_zoom(self):
        if self.curr_image is None:
            return
        arr = self.curr_image.array
        self.curr_image.x_lim = (0, arr.shape[1])
        self.curr_image.y_lim = (arr.shape[0], 0)
        self.canvas_main.redraw()
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
            self.canvas_main.redraw()

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
        self.canvas_main.redraw()

    def _cb_images_handler(self, event):
        group = self.sender().objectName().split('_')[-1]
        self.sliders[group].blockSignals(True)
        self.sliders[group].setValue(event)
        im_id = self.combo_boxes[group].get_custom_item(event).data(Qt.UserRole, )
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
                self.list_views[model].set_custom_model(model_new)
                self.combo_boxes[model].set_custom_model(model_new)

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
                else:
                    valid = None
                    break
            if valid is None:
                self.log(f"File \"{filepath}\" could not be loaded.", LogTypes.Error)
            else:
                self.loading_queue.put((filepath, self.parameters, group))

        self.statusbar.start_progress(self.loading_queue.qsize())
        self.loading_thread.wake()

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
            file_path, _ = QFileDialog.getSaveFileName(self, "Save images", "",
                                                       save_formats_strings[ftype], )
            if file_path != "":
                arr = self.curr_image.array
                name = file_path.split("/")[-1][:-4]
                file_path = "/".join(file_path.split("/")[:-1])
                get_save_image(ftype)(arr, name, file_path, **kwargs)
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
        text = self.le_operation.text()
        combo = self.combo_boxes['d']
        slider = self.sliders['d']
        fp_a, fp_b, fp_c = "", "", ""

        if self.combo_boxes['a'].count() > 0:
            im_a = self.images[self.combo_boxes['a'].get_current_item().data(Qt.UserRole, )]
            a = im_a.array
            fp_a = im_a.filepath
        if self.combo_boxes['b'].count() > 0:
            im_b = self.images[self.combo_boxes['b'].get_current_item().data(Qt.UserRole, )]
            b = im_b.array
            fp_b = im_b.filepath
        if self.combo_boxes['c'].count() > 0:
            im_c = self.images[self.combo_boxes['c'].get_current_item().data(Qt.UserRole, )]
            c = im_c.array
            fp_c = im_c.filepath

        try:
            image = eval(str(text))
        except Exception as e:
            self.log(f"Operation failed. It was not possible to perform the required calculation.\n{e}", LogTypes.Error)
            return

        tooltip = text.replace("a", "\t").replace("b", '\n').replace("c", '\r')
        tooltip = tooltip.replace("\t", f"[{fp_a.split('/')[-1]}]").replace("\n", f"[{fp_b.split('/')[-1]}]")
        tooltip = tooltip.replace("\r", f"[{fp_c.split('/')[-1]}]")

        item = QStandardItem()
        item.setText(text)
        item.setToolTip(tooltip)
        im_id = next(self.id_gen)
        item.setData(im_id, Qt.UserRole)
        combo.add_item(item)

        self.images[im_id] = ImageObject(image, image.min(), image.max(), (0, image.shape[1]),
                                         (image.shape[0], 0), im_id, tooltip)

        slider.setMaximum(combo.count() - 1)
        slider.blockSignals(True)
        slider.setValue(0)
        slider.blockSignals(False)
        self.show_image(im_id)

    def _image_loader_handler(self, event):
        arr, filepath, slot = event
        if arr is not None:
            self.sliders[slot].blockSignals(True)
            self.combo_boxes[slot].blockSignals(True)
            im_id = next(self.id_gen)
            img = ImageObject(arr, arr.min(), arr.max(), (0, arr.shape[1]), (arr.shape[0], 0), im_id, filepath)
            self.images[im_id] = img
            self.last_image_id = im_id

            item = QStandardItem()
            item.setText(filepath.split("/")[-1])
            item.setToolTip(filepath)
            item.setData(im_id, Qt.UserRole)
            self.models[slot].appendRow(item)

            self.log(f"File \"{filepath}\" loaded with ID: {im_id} in slot: {slot.upper()}.", LogTypes.Log)
            self.sliders[slot].setMaximum(self.combo_boxes[slot].count() - 1)
            self.sliders[slot].blockSignals(False)
            self.combo_boxes[slot].blockSignals(False)

        else:
            self.log(f"File \"{filepath}\" could not be loaded.", LogTypes.Error)
        self.statusbar.add_progress()

    def _last_image_handler(self):
        self.show_image(self.last_image_id)

    def _image_saver_handler(self, file):
        self.log(f"Saved \"{file}\"")
        self.statusbar.add_progress()

    def _remove_handler(self, im_id):
        if im_id == self.canvas_main.image.id_:
            self.canvas_main.reset_canvas()
            self.canvas_histogram.reset_canvas()
        self.images[im_id] = None

    def _item_changed(self):
        slot = self.sender().objectName().split("_")[-1]
        self.sliders[slot].blockSignals(True)
        maximum = self.combo_boxes[slot].count() - 1 if self.combo_boxes[slot].count() - 1 > 0 else 0
        self.sliders[slot].setMaximum(maximum)
        self.sliders[slot].setValue(0)
        self.sliders[slot].blockSignals(False)

    def _init_image_info_values(self):
        if self.curr_image is None:
            return
        for sb in self.spin_boxes.values():
            sb.blockSignals(True)
        for sl in [self.sliders['upper'], self.sliders['lower']]:
            sl.blockSignals(True)

        self.spin_boxes['lower'].setValue(self.curr_image.vmin)
        self.spin_boxes['upper'].setValue(self.curr_image.vmax)
        self.sliders['lower'].setValue(0)
        self.sliders['upper'].setValue(100)

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
        self.l_range_mean.setText(str(self._arr_from_zoom().mean()))
        self.l_range_sigma.setText(str(self._arr_from_zoom().std()))

        for sb in self.spin_boxes.values():
            sb.blockSignals(False)
        for sl in [self.sliders['upper'], self.sliders['lower']]:
            sl.blockSignals(False)

    def _selection_changed(self):
        if self.parameters.from_zoom:
            arr = self._arr_from_zoom()
            self.curr_image.vmin = arr.min()
            self.curr_image.vmax = arr.max()
        self._init_image_info_values()
        self.canvas_main.redraw()
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

    def _detector_manager(self):
        self.dm_window = DetectorManagerWidget(None, self.dm_thread, self.dm_queue)
        self.dm_window.show()

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
            arr = self._arr_from_zoom()
            self.curr_image.vmin = arr.min()
            self.curr_image.vmax = arr.max()
        self.canvas_main.show_image(image)
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

    def _arr_from_zoom(self):
        return self.curr_image.array[self.curr_image.y_lim[1]:self.curr_image.y_lim[0],
                                     self.curr_image.x_lim[0]:self.curr_image.x_lim[1]]

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
        if self.dm_thread:
            self.dm_thread.requestInterruption()
            self.dm_thread.wake()
        event.accept()
        app.exit(0)


if __name__ == '__main__':
    parser = ArgumentParser(
        prog="Vopex 3.0",
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

import os
import json
import subprocess
import webbrowser
import shotgrid_utils
from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class PlayblastUI(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(PlayblastUI, self).__init__(parent)
        self.setWindowTitle("Playblast Settings")
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.load_render_settings()
        self.load_ffmpeg_path()

    def create_widgets(self):
        self.camera_label = QtWidgets.QLabel("Camera:")
        self.camera_combo = QtWidgets.QComboBox()

        self.viewport_label = QtWidgets.QLabel("Viewport:")
        self.viewport_combo = QtWidgets.QComboBox()
        
        self.renderer_label = QtWidgets.QLabel("Renderer:")
        self.renderer_combo = QtWidgets.QComboBox()

        self.width_label = QtWidgets.QLabel("Width:")
        self.width_spin = QtWidgets.QSpinBox()
        self.width_spin.setRange(1, 10000)

        self.height_label = QtWidgets.QLabel("Height:")
        self.height_spin = QtWidgets.QSpinBox()
        self.height_spin.setRange(1, 10000)

        self.ffmpeg_label = QtWidgets.QLabel("FFmpeg Path:")
        self.ffmpeg_line_edit = QtWidgets.QLineEdit()
        self.browse_button = QtWidgets.QPushButton("Browse")

        self.warning_label = QtWidgets.QLabel(
            "Warning: Disable film and resolution gates manually."
        )
        self.warning_label.setStyleSheet("color: red;")

        self.submit_button = QtWidgets.QPushButton("Submit")
        self.cancel_button = QtWidgets.QPushButton("Cancel")

        self.load_viewports()
        self.load_renderers()

    def create_layouts(self):
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow(self.viewport_label, self.viewport_combo)
        form_layout.addRow(self.renderer_label, self.renderer_combo)
        form_layout.addRow(self.camera_label, self.camera_combo)
        form_layout.addRow(self.width_label, self.width_spin)
        form_layout.addRow(self.height_label, self.height_spin)
        form_layout.addRow(self.ffmpeg_label, self.ffmpeg_line_edit)
        form_layout.addRow(self.browse_button)
        form_layout.addRow(self.warning_label)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.submit_button.clicked.connect(self.on_submit)
        self.cancel_button.clicked.connect(self.reject)
        self.browse_button.clicked.connect(self.browse_ffmpeg_path)
        self.ffmpeg_line_edit.textChanged.connect(self.save_ffmpeg_path)
        self.viewport_combo.currentIndexChanged.connect(self.update_camera_list)
        self.renderer_combo.currentIndexChanged.connect(self.update_render_settings)

    def load_viewports(self):
        self.viewport_combo.clear()
        viewports = cmds.getPanel(type="modelPanel")
        for viewport in viewports:
            camera = cmds.modelPanel(viewport, query=True, camera=True)
            self.viewport_combo.addItem(f"{viewport} ({camera})")
        
        active_viewport = cmds.getPanel(withFocus=True)
        if active_viewport in viewports:
            index = self.viewport_combo.findText(active_viewport, QtCore.Qt.MatchStartsWith)
            if index >= 0:
                self.viewport_combo.setCurrentIndex(index)
        
        self.update_camera_list()

    def load_renderers(self):
        self.renderer_combo.clear()
        viewport_renderers = ['vp2Renderer', 'hwRender', 'vrayRE']  # Add or remove renderers as needed
        for renderer in viewport_renderers:
            self.renderer_combo.addItem(renderer)
        
        # Set default to 'vp2Renderer' (Viewport 2.0)
        default_index = self.renderer_combo.findText('vp2Renderer')
        if default_index >= 0:
            self.renderer_combo.setCurrentIndex(default_index)

    def update_camera_list(self):
        self.camera_combo.clear()
        selected_viewport = self.viewport_combo.currentText().split(' (')[0]
        try:
            camera = cmds.modelPanel(selected_viewport, query=True, camera=True)
            if camera:
                self.camera_combo.addItem(camera)
            
            # Add all cameras in the scene as options
            all_cameras = cmds.listCameras()
            for cam in all_cameras:
                if cam != camera:
                    self.camera_combo.addItem(cam)
        except:
            cmds.warning(f"Failed to query camera for viewport {selected_viewport}")

    def update_render_settings(self):
        # This method might not be necessary for viewport renderers
        pass

    def load_render_settings(self):
        render_width = cmds.getAttr("defaultResolution.width")
        render_height = cmds.getAttr("defaultResolution.height")
        self.width_spin.setValue(render_width)
        self.height_spin.setValue(render_height)

    def load_ffmpeg_path(self):
        config_path = self.get_config_path()
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                ffmpeg_path = config.get('ffmpeg_path', '')
                self.ffmpeg_line_edit.setText(ffmpeg_path)

    def browse_ffmpeg_path(self):
        ffmpeg_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select FFmpeg Executable")
        if ffmpeg_path:
            self.ffmpeg_line_edit.setText(ffmpeg_path)

    def save_ffmpeg_path(self):
        ffmpeg_path = self.ffmpeg_line_edit.text()
        if os.path.exists(ffmpeg_path) and os.path.isfile(ffmpeg_path):
            config_path = self.get_config_path()
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump({'ffmpeg_path': ffmpeg_path}, f)

    def get_config_path(self):
        user_dir = os.path.expanduser("~")
        config_path = os.path.join(user_dir, '.prttm', 'AnimationPublisher', 'AnimationPublisher.json')
        return config_path

    def on_submit(self):
        reply = QtWidgets.QMessageBox.warning(
            self,
            "Warning",
            "Disable film and resolution gates manually. Do you want to proceed?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )

        if reply == QtWidgets.QMessageBox.Yes:
            self.export_image_sequence()
            self.accept()
        else:
            self.reject()

    def export_image_sequence(self):
        file_path = cmds.file(query=True, sceneName=True)
        
        if not file_path:
            cmds.error("Please save your scene before running the script.")
            return

        file_dir = os.path.dirname(file_path)
        base_name = os.path.basename(file_path)
        name, ext = os.path.splitext(base_name)

        output_dir = file_dir.replace('/tasks/', '/outputs/')
        output_dir = os.path.join(output_dir, name, 'playblast')
        frames_dir = os.path.join(output_dir, 'frames')
        output_dir = os.path.normpath(output_dir)
        frames_dir = os.path.normpath(frames_dir)
        if not os.path.exists(frames_dir):
            os.makedirs(frames_dir)

        output_pattern = os.path.join(frames_dir, name)
        output_pattern = os.path.normpath(output_pattern)

        print("Output Directory: {}".format(output_dir))
        print("Output File Pattern: {}".format(output_pattern))

        selected_viewport = self.viewport_combo.currentText().split(' (')[0]
        selected_renderer = self.renderer_combo.currentText()
        current_camera = self.camera_combo.currentText()

        if not current_camera:
            cmds.error("No camera selected. Please select a valid camera.")
            return

        print("Using Camera: {}".format(current_camera))

        if not cmds.objExists(current_camera):
            cmds.error(f"Camera '{current_camera}' does not exist in the scene.")
            return

        try:
            camera_shape = cmds.listRelatives(current_camera, shapes=True, type="camera")[0]
        except:
            cmds.error(f"Failed to get camera shape for '{current_camera}'. Please ensure it's a valid camera.")
            return

        start_frame = cmds.playbackOptions(query=True, minTime=True)
        end_frame = cmds.playbackOptions(query=True, maxTime=True)

        render_width = self.width_spin.value()
        render_height = self.height_spin.value()

        # Set up the viewport for playblast
        try:
            cmds.modelEditor(selected_viewport, edit=True, displayAppearance='smoothShaded', camera=current_camera)
            
            # Set the viewport renderer
            cmds.modelEditor(selected_viewport, edit=True, rendererName=selected_renderer)
            
            # Additional settings for specific renderers
            if selected_renderer == 'vp2Renderer':
                cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 1)
                cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", 1)
            elif selected_renderer == 'vrayRE':
                # Add any specific V-Ray RT settings here if needed
                pass
        except Exception as e:
            cmds.warning(f"Failed to set up viewport {selected_viewport}: {str(e)}. Using default viewport settings.")

        # Perform the playblast
        try:
            cmds.playblast(
                filename=output_pattern,
                format='image',
                startTime=start_frame,
                endTime=end_frame,
                sequenceTime=0,
                clearCache=1,
                viewer=0,
                showOrnaments=0,
                fp=4,
                percent=100,
                compression='jpg',
                quality=100,
                widthHeight=[render_width, render_height],
                offScreen=True,
                framePadding=4
            )
        except Exception as e:
            cmds.error(f"Playblast failed: {str(e)}")
            return

        self.convert_to_mp4(output_dir, frames_dir, name, ext)

    def convert_to_mp4(self, output_dir, frames_dir, base_name, ext):
        ffmpeg_path = self.ffmpeg_line_edit.text()
        if not os.path.exists(ffmpeg_path) or not os.path.isfile(ffmpeg_path):
            cmds.error("Invalid FFmpeg path.")
            return

        frame_rate = self.get_frame_rate()
        if frame_rate <= 0:
            cmds.error("Invalid frame rate.")
            return

        mp4_output_path = os.path.join(output_dir, base_name + ".mp4")

        if os.path.exists(mp4_output_path):
            reply = QtWidgets.QMessageBox.question(
                self,
                "File Exists",
                f"The file {mp4_output_path} already exists. Do you want to overwrite it?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            )
            if reply == QtWidgets.QMessageBox.No:
                return
            else:
                os.remove(mp4_output_path)

        first_frame = self.get_first_frame_number(frames_dir, base_name)
        if first_frame is None:
            cmds.error("No frames found in the specified directory.")
            return

        ffmpeg_command = [
            ffmpeg_path,
            '-framerate', str(frame_rate),
            '-start_number', str(first_frame),
            '-i', os.path.join(frames_dir, base_name + ".%04d.jpg"),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            mp4_output_path
        ]

        print("FFmpeg Command: {}".format(" ".join(ffmpeg_command)))
        try:
            subprocess.run(ffmpeg_command, check=True)
            self.open_mp4(mp4_output_path)
            self.upload_to_shotgrid(base_name + ext, proxy=mp4_output_path)
        except subprocess.CalledProcessError as e:
            cmds.error("FFmpeg failed with error: {}".format(e))

    def get_frame_rate(self):
        time_unit = cmds.currentUnit(query=True, time=True)
        frame_rates = {
            'game': 15.0,
            'film': 24.0,
            'pal': 25.0,
            'ntsc': 30.0,
            'show': 48.0,
            'palf': 50.0,
            'ntscf': 60.0,
        }
        return frame_rates.get(time_unit, 0.0)

    def get_first_frame_number(self, frames_dir, base_name):
        files = os.listdir(frames_dir)
        frames = sorted([int(f.split('.')[-2]) for f in files if f.startswith(base_name) and f.endswith('.jpg')])
        return frames[0] if frames else None

    def open_mp4(self, mp4_path):
        webbrowser.open(mp4_path)

    def upload_to_shotgrid(self, short_name, proxy):
        # Use shotgrid_utils to upload the version with proxy path
        shotgrid_utils.update_version(short_name, proxy=proxy)
        print("uploading")

# Example usage
if __name__ == "__main__":
    try:
        playblast_ui.close()  # Close the window if it exists
        playblast_ui.deleteLater()
    except:
        pass

    playblast_ui = PlayblastUI()
    playblast_ui.show()
    shotgrid_utils.update_version(short)
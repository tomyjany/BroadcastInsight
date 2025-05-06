import cv2
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QFrame,
    QApplication,
    QSizePolicy,
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, pyqtSignal, Qt


class VideoPlayer(QWidget):
    frame_changed = pyqtSignal(int)  # Signal to notify when the frame changes

    def __init__(self, video_path, scene_slider, scene_cuts):
        super().__init__()
        self.video_path = video_path
        self.layout = QVBoxLayout()

        # Video display area (with minimum size set to ensure visibility)
        self.video_label = QLabel("Loading video...")
        self.video_label.setMinimumSize(
            640, 360
        )  # Ensure a reasonable size for video and border
        self.video_label.setAlignment(
            Qt.AlignCenter
        )  # Center the video within the window
        self.layout.addWidget(self.video_label)
        self.setLayout(self.layout)

        # Enable resizing of the video label
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.cap = cv2.VideoCapture(video_path)
        self.frame_count = int(
            self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        )  # Total frames in the video
        self.fps = self.cap.get(
            cv2.CAP_PROP_FPS
        )  # Get the video's frames per second (FPS)
        self.slider = scene_slider  # Link the slider to the video player
        self.scene_cuts = scene_cuts  # Store the scene cuts
        self.overlay_timer = QTimer(self)  # Timer to control the scene change highlight

        self.slider.setMaximum(
            self.frame_count
        )  # Set the slider range based on total frames

        # Timer for updating frames (using the video’s native frame rate)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(
            int(1000 / self.fps)
        )  # Set the timer interval based on the FPS

        # Connect the slider movement to the video seeking functionality
        self.slider.valueChanged.connect(self.seek_frame)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Convert frame to RGB format
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Resize the frame to fit the QLabel dimensions
            label_width = self.video_label.width()
            label_height = self.video_label.height()
            frame_rgb = cv2.resize(
                frame_rgb, (label_width, label_height), interpolation=cv2.INTER_AREA
            )

            # Convert the image to QImage for display in PyQt
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # Display the frame on QLabel
            self.video_label.setPixmap(QPixmap.fromImage(q_image))

            # Update the slider to the current frame
            current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            self.slider.blockSignals(
                True
            )  # Prevent slider from emitting valueChanged signal
            self.slider.setValue(current_frame)
            self.slider.blockSignals(False)

            # Emit signal that the frame has changed
            self.frame_changed.emit(current_frame)

            # Check if the current frame is a scene cut and highlight
            for cut in self.scene_cuts:
                if (
                    abs(int(current_frame) - int(cut)) <= 2
                ):  # Allow tolerance of 2 frames
                    self.show_scene_cut_overlay()
                    break  # Exit loop after finding a match

        else:
            self.timer.stop()  # Stop the timer when the video ends

    def seek_frame(self, frame_number):
        # Jump to the selected frame in the video
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        self.update_frame()  # Update the video display to the selected frame

    def show_scene_cut_overlay(self):
        # Add a border or visual cue for a brief moment
        self.video_label.setStyleSheet(
            "border: 5px solid red;"
        )  # Red border to highlight the scene change

        # Set a timer to remove the border after 0.5 seconds (for actual scene cuts, otherwise stays visible)
        self.overlay_timer.singleShot(500, self.remove_scene_cut_overlay)

    def remove_scene_cut_overlay(self):
        # Remove the visual cue (border)
        self.video_label.setStyleSheet("")  # Reset to no border

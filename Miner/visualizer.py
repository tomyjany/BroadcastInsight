import sys
import json
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QListWidget,
    QTextEdit,
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import cv2


class SceneVisualizer(QMainWindow):
    def __init__(self, video_path: str, json_path: str):
        super().__init__()
        self.video_path = video_path
        self.json_path = json_path
        self.scenes = self.load_json()
        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")

        self.init_ui()

    def load_json(self):
        with open(self.json_path, "r") as f:
            return json.load(f)

    def init_ui(self):
        self.setWindowTitle("Scene Visualizer")
        self.setGeometry(100, 100, 1200, 800)

        # Main layout
        main_layout = QHBoxLayout()

        # Scene list
        self.scene_list = QListWidget()
        self.scene_list.addItems(
            [f"Scene {scene['scene_info']['id']}" for scene in self.scenes]
        )
        self.scene_list.currentRowChanged.connect(self.display_scene)
        main_layout.addWidget(self.scene_list, 2)

        # Scene display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.image_label, 5)

        # Metadata display
        self.metadata_display = QTextEdit()
        self.metadata_display.setReadOnly(True)
        main_layout.addWidget(self.metadata_display, 3)

        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def display_scene(self, index):
        if index < 0 or index >= len(self.scenes):
            return

        scene = self.scenes[index]
        frame_number = scene["scene_info"]["frame_number"]

        # Extract frame from video
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.cap.read()
        if not ret:
            self.image_label.setText("Failed to load frame.")
            return

        # Convert frame to QPixmap
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = frame_rgb.shape
        bytes_per_line = channel * width
        q_image = QImage(
            frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888
        )
        pixmap = QPixmap.fromImage(q_image)

        # Display frame
        self.image_label.setPixmap(
            pixmap.scaled(
                self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )

        # Display metadata with improved formatting
        metadata = f"""
        <b>Scene ID:</b> {scene['scene_info']['id']}<br>
        <b>Frame Number:</b> {scene['scene_info']['frame_number']}<br>
        <b>Begin Time:</b> {scene['scene_info']['begin_time']} ms<br>
        <b>End Time:</b> {scene['scene_info']['end_time']} ms<br><br>
        <b>OCR Text:</b><br>{scene['ocr_text']}<br><br>
        <b>Detected People:</b><br>
        {self.format_detected_people(scene['detected_people'])}<br>
        <b>TV Logo:</b> {scene['tv_logo']}
        """
        self.metadata_display.setHtml(metadata.strip())

    def format_detected_people(self, people):
        if not people:
            return "None"
        return "<br>".join(
            [
                f"- {p['person']} (Age: {p['age']}, Gender: {p['gender']})"
                for p in people
            ]
        )

    def closeEvent(self, event):
        self.cap.release()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    video_path = (
        "path_to_video.mp4"  # Replace with the actual video path
    )
    json_path = "path_to_json.json"  # Replace with the actual JSON path
    visualizer = SceneVisualizer(video_path, json_path)
    visualizer.show()
    sys.exit(app.exec_())

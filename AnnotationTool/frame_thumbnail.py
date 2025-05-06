from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QImage


class FrameThumbnail(QLabel):
    clicked = pyqtSignal(int)  # Signal emitted when frame is clicked

    def __init__(self, frame_num, frame_image):
        super().__init__()
        self.frame_num = frame_num
        self.setPixmap(self.convert_to_pixmap(frame_image))
        self.setFrameShape(QLabel.Box)
        self.setAlignment(Qt.AlignCenter)

    def convert_to_pixmap(self, frame_image):
        """Convert the frame (OpenCV) image to QPixmap."""
        h, w, ch = frame_image.shape
        bytes_per_line = ch * w
        q_image = QImage(frame_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(q_image).scaled(120, 90, Qt.KeepAspectRatio)

    def mousePressEvent(self, event):
        """Emit the clicked signal with the frame number when clicked."""
        self.clicked.emit(self.frame_num)

    def mark_as_cut(self, color: str):
        """Highlight the frame to indicate it's marked as a scene cut."""
        # self.setStyleSheet("border: 3px solid red;")
        print("poustim marker ", color)
        if color == "start":
            self.setStyleSheet("border: 10px solid green;")
            print("NASTAVENO NA ZELENOU")
        if color == "end":
            self.setStyleSheet("border: 10px solid red;")
            print("NASTAVENO NA CERVENOU")

    def unmark_as_cut(self):
        """Remove the highlight from the frame."""
        self.setStyleSheet("border: none;")

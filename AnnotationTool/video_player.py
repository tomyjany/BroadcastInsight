from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
import cv2

class VideoPlayer(QWidget):
    frame_changed = pyqtSignal(int)  # Signal to notify when the frame changes

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.layout = QVBoxLayout()

        # Video display area
        self.video_label = QLabel("Loading video...")
        self.video_label.setMinimumSize(640, 360)
        self.layout.addWidget(self.video_label)
        self.setLayout(self.layout)

        # Video capture
        self.cap = cv2.VideoCapture(video_path)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        print("FPS: ", self.fps)

        # Timer for playback
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)  # Only used during playback

        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.fixed_fps = 25.015  # fixed fps for testing

    def update_frame(self):
        """Called during video playback to update the current frame."""
        ret, frame = self.cap.read()
        if ret:
            self.display_frame(frame)  # Use the resized frame for display
            current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            self.frame_changed.emit(current_frame)

        # Use the fixed FPS instead of the original video FPS for consistent playback
        self.timer.setInterval(int(1000 / self.fixed_fps))

    def seek_frame(self, frame_num):
        """Seek to the specified frame using the fixed FPS."""
        if self.fixed_fps > 0:
            time_in_ms = (
                frame_num / self.fixed_fps
            ) * 1000  # Frame number to milliseconds

            # Seek to the calculated time
            self.cap.set(cv2.CAP_PROP_POS_MSEC, time_in_ms)

            ret, frame = self.cap.read()
            if ret:
                self.display_frame(frame)  # Use the resized frame for display
                self.frame_changed.emit(frame_num)

    def display_frame(self, frame):
        """Helper function to convert and display a video frame at a lower resolution."""
        # Get current frame number and timestamp to track changes
        current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        current_time = self.cap.get(cv2.CAP_PROP_POS_MSEC)
        print(f"Displaying frame {current_frame}, timestamp: {current_time} ms")

        # Resize the frame to a lower resolution (e.g., 50% of original)
        scale_factor = 0.5  # Adjust this factor as needed
        frame_resized = cv2.resize(
            frame, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA
        )

        # Convert the resized frame to RGB and display
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Display the QImage in the QLabel
        self.video_label.setPixmap(QPixmap.fromImage(q_image))

    def get_frame_at(self, frame_num):
        """Retrieve the frame at the specified frame number."""
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return True, frame_rgb
        return False, None

    def get_timestamp_ms(self, frame_num):
        """Get the timestamp in milliseconds for the given frame number."""
        return int((frame_num / self.fps) * 1000)

    def get_current_frame(self):
        """Get the current frame number."""
        return int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

    def play_video(self):
        """Start playing the video."""
        self.timer.start(int(1000 / self.fps))

    def pause_video(self):
        """Pause the video."""
        self.timer.stop()

    def resizeEvent(self, event):
        """Handle window resize events to ensure the video is stretched properly."""
        if hasattr(self, "video_label") and self.video_label.pixmap() is not None:
            # Ensure the video label resizes with the window
            self.video_label.setPixmap(
                self.video_label.pixmap().scaled(
                    self.video_label.size(),  # Use QLabel's size for stretching
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )

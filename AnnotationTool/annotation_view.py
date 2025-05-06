from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QPushButton,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
)
from PyQt5.QtCore import Qt
from AnnotationTool.video_player import VideoPlayer
from AnnotationTool.frame_thumbnail import FrameThumbnail
from AnnotationTool.cut_manager import CutManager

from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence, QFont


class AnnotationView(QWidget):
    def __init__(self, video_path):
        super().__init__()
        self.mark_begin = True
        self.setWindowTitle("Video Annotation Tool")
        self.video_path = video_path
        self.cut_manager = CutManager()

        # Set up larger UI elements
        self.setup_ui_scaling()

        # Main layout
        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)  # Add more spacing between widgets

        # Video player widget
        self.video_player = VideoPlayer(video_path)
        self.video_player.frame_changed.connect(
            self.on_frame_change
        )  # Connect video frame updates to frame viewer
        self.layout.addWidget(self.video_player)

        # Frame thumbnails layout (for displaying multiple frames)
        self.frame_viewer_layout = QHBoxLayout()
        self.frame_viewer_layout.setSpacing(8)  # Add spacing between thumbnails
        self.layout.addLayout(self.frame_viewer_layout)

        self.segment_button_layout = QHBoxLayout()

        self.previous_segment_button = QPushButton("Previous Segment")
        self.next_segment_button = QPushButton("Next Segment")

        # Apply styling to the segment buttons
        self.previous_segment_button.setFont(self.button_font)
        self.next_segment_button.setFont(self.button_font)
        self.previous_segment_button.setMinimumHeight(40)
        self.next_segment_button.setMinimumHeight(40)

        self.segment_button_layout.addWidget(self.previous_segment_button)
        self.segment_button_layout.addWidget(self.next_segment_button)
        self.previous_segment_button.clicked.connect(self.previous_segment)
        self.next_segment_button.clicked.connect(self.next_segment)

        self.layout.addLayout(self.segment_button_layout)

        # Slider for video navigation
        self.video_slider = QSlider(Qt.Horizontal)
        self.video_slider.setMaximum(self.video_player.frame_count - 1)
        self.video_slider.valueChanged.connect(self.slider_moved)
        self.layout.addWidget(self.video_slider)

        # Button layout for play/pause and frame-by-frame navigation
        self.button_layout = QHBoxLayout()
        self.frame_cache = {}

        # Play/Pause button
        self.play_button = QPushButton("Play")
        self.play_button.setFont(self.button_font)
        self.play_button.setMinimumHeight(40)
        self.play_button.clicked.connect(self.toggle_playback)
        self.button_layout.addWidget(self.play_button)

        # Frame backward button (1 frame)
        self.backward_one_button = QPushButton("<< 1 frame")
        self.backward_one_button.setFont(self.button_font)
        self.backward_one_button.setMinimumHeight(40)
        self.backward_one_button.clicked.connect(self.step_backward_one)
        self.button_layout.addWidget(self.backward_one_button)

        # Frame forward button (1 frame)
        self.forward_one_button = QPushButton("1 frame >>")
        self.forward_one_button.setFont(self.button_font)
        self.forward_one_button.setMinimumHeight(40)
        self.forward_one_button.clicked.connect(self.step_forward_one)
        self.button_layout.addWidget(self.forward_one_button)

        # Frame backward button (10 frames)
        self.backward_button = QPushButton("<< 10 frames")
        self.backward_button.setFont(self.button_font)
        self.backward_button.setMinimumHeight(40)
        self.backward_button.clicked.connect(self.step_backward)
        self.button_layout.addWidget(self.backward_button)

        # Frame forward button (10 frames)
        self.forward_button = QPushButton("10 frames >>")
        self.forward_button.setFont(self.button_font)
        self.forward_button.setMinimumHeight(40)
        self.forward_button.clicked.connect(self.step_forward)
        self.button_layout.addWidget(self.forward_button)

        self.layout.addLayout(self.button_layout)

        # Marking list to display all saved cuts
        self.marking_list = QListWidget()
        self.marking_list.setFont(self.list_font)
        self.marking_list.itemClicked.connect(
            self.on_marking_clicked
        )  # Seek to marking on click
        self.layout.addWidget(self.marking_list)

        # Delete button to remove selected markings
        self.delete_button = QPushButton("Delete Selected Marking")
        self.delete_button.setFont(self.button_font)
        self.delete_button.setMinimumHeight(40)
        self.delete_button.clicked.connect(self.delete_selected_marking)
        self.layout.addWidget(self.delete_button)

        # Buttons for saving annotations
        self.save_button = QPushButton("Save Annotations")
        self.save_button.setFont(self.button_font)
        self.save_button.setMinimumHeight(40)
        self.save_button.clicked.connect(self.save_annotations)
        self.layout.addWidget(self.save_button)

        # Initialize UI
        self.setLayout(self.layout)
        self.display_frames_around(0)  # Display initial set of frames
        self.is_playing = False
        self.current_frame = 0  # Track the current frame

        # Button for loading annotations
        self.load_button = QPushButton("Load Annotations")
        self.load_button.setFont(self.button_font)
        self.load_button.setMinimumHeight(40)
        self.load_button.clicked.connect(self.load_annotations)
        self.layout.addWidget(self.load_button)

        self.setup_shortcuts()

    def setup_ui_scaling(self):
        """Set up larger UI elements for better visibility"""
        # Create larger fonts
        self.app_font = QFont()
        self.app_font.setPointSize(12)
        self.setFont(self.app_font)

        self.button_font = QFont()
        self.button_font.setPointSize(12)
        self.button_font.setBold(True)

        self.list_font = QFont()
        self.list_font.setPointSize(12)

        # Set application-wide stylesheet for common elements
        self.setStyleSheet("""
            QPushButton {
                padding: 8px;
                min-height: 30px;
            }
            QSlider {
                min-height: 30px;
            }
            QSlider::groove:horizontal {
                height: 8px;
            }
            QSlider::handle:horizontal {
                width: 18px;
                margin: -5px 0;
            }
            QListWidget {
                font-size: 12pt;
            }
            QListWidget::item {
                padding: 5px;
                min-height: 25px;
            }
        """)

    def setup_shortcuts(self):
        play_shortcut = QShortcut(QKeySequence("Space"), self)
        play_shortcut.activated.connect(self.play_button.click)

        forward_one_shortcut = QShortcut(QKeySequence("h"), self)
        forward_one_shortcut.activated.connect(self.backward_one_button.click)
        backward_one_shortcut = QShortcut(QKeySequence("l"), self)
        backward_one_shortcut.activated.connect(self.forward_one_button.click)

        forward_shortcut = QShortcut(QKeySequence("shift+h"), self)
        forward_shortcut.activated.connect(self.backward_button.click)
        backward_shortcut = QShortcut(QKeySequence("shift+l"), self)
        backward_shortcut.activated.connect(self.forward_button.click)

        previous_segment_shortcut = QShortcut(QKeySequence("ctrl+h"), self)
        previous_segment_shortcut.activated.connect(self.previous_segment)
        next_segment_shortcut = QShortcut(QKeySequence("ctrl+l"), self)
        next_segment_shortcut.activated.connect(self.next_segment)

    def next_segment(self):
        def find_next_segment():
            if self.cut_manager.cuts:
                for cut in self.cut_manager.cuts:
                    if cut["start"] > self.current_frame:
                        return cut["start"]
                return self.current_frame

        self.on_frame_change(find_next_segment())

    def previous_segment(self):
        def find_previous_segment():
            if self.cut_manager.cuts:
                for cut in self.cut_manager.cuts[::-1]:
                    if cut["start"] < self.current_frame:
                        return cut["start"]
            return self.current_frame

        self.on_frame_change(find_previous_segment())

    def display_frames_around(self, current_frame):
        """Display frames around the given frame number with caching."""
        self.clear_frame_viewer()

        # Define the range of frames to display (from -5 to +5)
        frame_range = range(
            max(0, current_frame - 10),
            min(self.video_player.frame_count, current_frame + 10),
        )

        for frame_num in frame_range:
            # Check if the frame is cached
            if frame_num in self.frame_cache:
                # If cached, retrieve it from memory
                frame = self.frame_cache[frame_num]
            else:
                # If not cached, load the frame and cache it
                success, frame = self.video_player.get_frame_at(frame_num)
                if success:
                    self.frame_cache[frame_num] = frame  # Cache the loaded frame

            # If frame is available, create a thumbnail widget
            if frame.any():
                frame_thumb = FrameThumbnail(frame_num, frame)
                frame_thumb.clicked.connect(self.toggle_cut)
                self.frame_viewer_layout.addWidget(frame_thumb)

        # Ensure that marked frames are visually updated
        self.update_frame_marks()

    def clear_frame_cache(self):
        """Optional: Clear the frame cache if needed."""
        self.frame_cache.clear()

    def slider_moved(self, frame_num):
        """Update the main video player and surrounding frames when the slider is moved."""
        self.current_frame = frame_num  # Update the current frame
        self.video_player.seek_frame(frame_num)
        self.display_frames_around(frame_num)  # Update thumbnails around the new frame

    def toggle_cut(self, frame_num):
        """Mark or unmark the frame as a scene cut."""
        color = self.cut_manager.is_cut(frame_num)

        if color == "start":
            self.cut_manager.remove_cut(frame_num)
            self.mark_begin = True
        elif color == "end":
            self.cut_manager.remove_cut(frame_num)
            self.mark_begin = False
        else:
            if self.mark_begin:
                self.start_cache = frame_num
                self.start_time_cache = self.video_player.get_timestamp_ms(frame_num)
                self.mark_begin = False
            else:
                self.end_cache = frame_num
                self.end_time_cache = self.video_player.get_timestamp_ms(frame_num)
                self.cut_manager.add_cut(
                    self.start_cache,
                    self.end_cache,
                    self.start_time_cache,
                    self.end_time_cache,
                )
                (
                    self.start_cache,
                    self.end_cache,
                    self.start_time_cache,
                    self.end_time_cache,
                ) = (None, None, None, None)

                self.mark_begin = True
                self.update_frame_marks()  # Update the frame marks after toggling
                self.update_marking_list()  # Update the list of saved markings

    def update_frame_marks(self):
        """Update the visual indication of marked frames."""
        for i in range(self.frame_viewer_layout.count()):
            frame_thumb = self.frame_viewer_layout.itemAt(i).widget()
            color = self.cut_manager.is_cut(frame_thumb.frame_num)
            if color == "start":
                frame_thumb.mark_as_cut(color)
            elif color == "end":
                frame_thumb.mark_as_cut(color)
            else:
                frame_thumb.unmark_as_cut()

    def update_marking_list(self):
        """Update the QListWidget to show all saved cuts."""
        self.marking_list.clear()
        self.cut_manager.cuts.sort(key=lambda d: d["start"])
        for cut in self.cut_manager.cuts:
            frame_start = cut["start"]
            frame_end = cut["end"]
            frame_time_start = cut["time_start"]
            frame_time_end = cut["time_end"]
            list_item = QListWidgetItem(
                f"start: {frame_start}, Time: {frame_time_start} ms"
            )
            list_item.setFont(self.list_font)
            list_item.setData(
                Qt.UserRole, frame_start
            )  # Store the frame number in the item
            self.marking_list.addItem(list_item)

    def save_annotations(self):
        """Save the annotations to a JSON file."""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Annotations", "", "JSON Files (*.json)"
        )
        if file_name:
            self.cut_manager.save_cuts_to_file(file_name)

    def clear_frame_viewer(self):
        """Clear the frame viewer layout."""
        while self.frame_viewer_layout.count():
            child = self.frame_viewer_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def toggle_playback(self):
        """Toggle play/pause for the video."""
        if self.is_playing:
            self.video_player.pause_video()
            self.play_button.setText("Play")
            # Save the current frame after pausing
            self.current_frame = self.video_player.get_current_frame()
            self.display_frames_around(self.current_frame)
        else:
            self.video_player.play_video()
            self.play_button.setText("Pause")
        self.is_playing = not self.is_playing

    def step_backward_one(self):
        """Step backward by 1 frame."""
        self.current_frame = max(0, self.current_frame - 1)
        self.video_slider.setValue(self.current_frame)
        self.slider_moved(self.current_frame)

    def step_forward_one(self):
        """Step forward by 1 frame."""
        self.current_frame = min(
            self.video_player.frame_count - 1, self.current_frame + 1
        )
        self.video_slider.setValue(self.current_frame)
        self.slider_moved(self.current_frame)

    def step_backward(self):
        """Step backward by 10 frames."""
        self.current_frame = max(0, self.current_frame - 10)
        self.video_slider.setValue(self.current_frame)
        self.slider_moved(self.current_frame)

    def step_forward(self):
        """Step forward by 10 frames."""
        self.current_frame = min(
            self.video_player.frame_count - 1, self.current_frame + 10
        )
        self.video_slider.setValue(self.current_frame)
        self.slider_moved(self.current_frame)

    def on_frame_change(self, frame_num):
        """Update slider and frame viewer when video frame changes."""
        self.current_frame = frame_num  # Sync with the video frame
        self.video_slider.setValue(frame_num)
        self.display_frames_around(
            frame_num
        )  # Update thumbnails when the frame changes

    def on_marking_clicked(self, item):
        """Seek to the frame number associated with the clicked marking."""
        frame_num = item.data(Qt.UserRole)
        self.video_slider.setValue(frame_num)
        self.slider_moved(frame_num)

    def delete_selected_marking(self):
        """Delete the currently selected marking from the list and update the cut manager."""
        selected_item = self.marking_list.currentItem()

        if selected_item:
            frame_num = selected_item.data(Qt.UserRole)
            self.cut_manager.remove_cut(
                frame_num
            )  # Remove the cut from the cut manager
            self.update_marking_list()  # Update the marking list
            self.update_frame_marks()  # Update frame marks in the thumbnails

    def load_annotations(self):
        """Load the annotations from a JSON file."""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Load Annotations", "", "JSON Files (*.json)"
        )
        self.cut_manager.load_cuts_from_file(file_name)
        self.update_marking_list()  # Refresh the marking list
        self.update_frame_marks()  # Update frame marks in the thumbnails

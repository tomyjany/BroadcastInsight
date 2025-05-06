from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGridLayout,
    QScrollArea,
    QCheckBox,
    QSizePolicy,
)
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PeopleFinder.photo_downloader.interface import get_downloader
from PeopleFinder.People.Photo import get_cropped_faces_from_images, Photo
from PeopleFinder.People.Person import Person
from PeopleFinder.GUI.DownloadThread import DownloadThread
from PeopleFinder.GUI.CropFacesThread import CropFacesThread
from PIL import Image
import io


class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    shift_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.checkbox = None
        self.photo = None

    def mousePressEvent(self, event):
        if event.modifiers() == Qt.ShiftModifier:
            print("shift plus click pressed")
            self.shift_clicked.emit()
        else:
            self.clicked.emit()

    def set_checkbox(self, checkbox):
        self.checkbox = checkbox

    def set_photo(self, photo):
        self.photo = photo


class PeopleFinderView(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.person = None

    def initUI(self):
        self.setWindowTitle("People Finder")
        self.layout = QVBoxLayout()

        # Input fields
        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        self.number_label = QLabel("Number of Pictures:")
        self.number_input = QLineEdit()
        self.temp_person = None

        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download_photos)

        self.embed_button = QPushButton("Embed Person")
        self.embed_button.clicked.connect(self.embed_person)

        self.sort_button = QPushButton("Sort Photos")
        self.sort_button.clicked.connect(self.sort_photos)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.name_label)
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(self.number_label)
        input_layout.addWidget(self.number_input)
        input_layout.addWidget(self.download_button)
        input_layout.addWidget(self.embed_button)
        input_layout.addWidget(self.sort_button)

        self.layout.addLayout(input_layout)

        # Scroll area for images
        self.scroll_area = QScrollArea()
        self.scroll_area_widget = QWidget()
        self.scroll_area_layout = QGridLayout()
        self.scroll_area_widget.setLayout(self.scroll_area_layout)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.scroll_area.setWidgetResizable(True)

        # Add this to the initUI method
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.progress_bar)

        self.layout.addWidget(self.scroll_area)
        self.setLayout(self.layout)

    def download_photos(self):
        name = self.name_input.text()
        number = int(self.number_input.text())
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat(f"Downloading {number} photos...")

        self.download_thread = DownloadThread(name, number)
        self.download_thread.progress.connect(self.progress_bar.setValue)
        self.download_thread.result.connect(self.display_photos)
        self.download_thread.start()

    def on_photo_clicked(self, label):
        if label.checkbox:
            label.checkbox.setChecked(not label.checkbox.isChecked())

    def on_photo_shift_clicked(self, label):
        print("Shift clicked")
        if label.checkbox:
            label.checkbox.setChecked(True)
            index = self.scroll_area_layout.indexOf(label)
            for i in range(index):
                print("Checking box")
                widget = self.scroll_area_layout.itemAt(i).widget()
                if isinstance(widget, ClickableLabel) and widget.checkbox:
                    widget.checkbox.setChecked(True)

    @pyqtSlot(list)
    def display_photos(self, images):
        self.progress_bar.setValue(0)
        number_of_images = len(images)
        self.progress_bar.setFormat(f"Detecting faces in {number_of_images} photos...")

        self.crop_faces_thread = CropFacesThread(images)
        self.crop_faces_thread.progress.connect(self.progress_bar.setValue)
        self.crop_faces_thread.result.connect(self.show_faces)
        self.crop_faces_thread.start()

    @pyqtSlot(list)
    def show_faces(self, faces):
        for i, face in enumerate(faces):
            image_data = io.BytesIO()
            face.cropped.save(image_data, format="PNG")
            pixmap = QPixmap()
            pixmap.loadFromData(image_data.getvalue())

            label = ClickableLabel()
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            label.setScaledContents(False)  # Ensure aspect ratio is maintained
            label.setMinimumSize(
                100, 100
            )  # Set a minimum size to maintain aspect ratio

            # Adjust the pixmap size to maintain aspect ratio
            original_size = pixmap.size()
            scaled_size = original_size.scaled(200, 200, Qt.KeepAspectRatio)
            label.setPixmap(
                pixmap.scaled(scaled_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

            checkbox = QCheckBox()
            label.set_checkbox(checkbox)
            label.set_photo(face)
            label.clicked.connect(lambda lbl=label: self.on_photo_clicked(lbl))
            label.shift_clicked.connect(
                lambda lbl=label: self.on_photo_shift_clicked(lbl)
            )

            self.scroll_area_layout.addWidget(label, i // 3, (i % 3) * 2)
            self.scroll_area_layout.addWidget(checkbox, i // 3, (i % 3) * 2 + 1)

    def embed_temp_person(self):
        name = self.name_input.text()
        self.temp_person = Person(name)

        for i in range(self.scroll_area_layout.count()):
            widget = self.scroll_area_layout.itemAt(i).widget()
            if isinstance(widget, ClickableLabel):
                self.temp_person.add_photo(widget.photo)

    def embed_person(self):
        name = self.name_input.text()
        self.person = Person(name)

        for i in range(self.scroll_area_layout.count()):
            widget = self.scroll_area_layout.itemAt(i).widget()
            if isinstance(widget, ClickableLabel) and widget.checkbox.isChecked():
                self.person.add_photo(widget.photo)

        self.person.save_person()

    def sort_photos(self):
        self.embed_temp_person()
        if self.temp_person:
            self.temp_person.sort_photos()
            self.redisplay_photos(temp=True)

    def redisplay_photos(self, temp=False):
        for i in reversed(range(self.scroll_area_layout.count())):
            widget = self.scroll_area_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for i, photo in enumerate(
            self.person.photos if not temp else self.temp_person.photos
        ):
            image_data = io.BytesIO()
            photo.cropped.save(image_data, format="PNG")
            pixmap = QPixmap()
            pixmap.loadFromData(image_data.getvalue())

            label = ClickableLabel()
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            label.setScaledContents(False)  # Ensure aspect ratio is maintained
            label.setMinimumSize(
                100, 100
            )  # Set a minimum size to maintain aspect ratio

            # Adjust the pixmap size to maintain aspect ratio
            original_size = pixmap.size()
            scaled_size = original_size.scaled(200, 200, Qt.KeepAspectRatio)
            label.setPixmap(
                pixmap.scaled(scaled_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

            checkbox = QCheckBox()
            label.set_checkbox(checkbox)
            label.set_photo(photo)
            label.clicked.connect(lambda lbl=label: self.on_photo_clicked(lbl))
            label.shift_clicked.connect(
                lambda lbl=label: self.on_photo_shift_clicked(lbl)
            )

            self.scroll_area_layout.addWidget(label, i // 3, (i % 3) * 2)
            self.scroll_area_layout.addWidget(checkbox, i // 3, (i % 3) * 2 + 1)

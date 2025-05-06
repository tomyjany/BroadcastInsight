from PyQt5.QtCore import QThread, pyqtSignal
from PeopleFinder.People.Photo import get_cropped_faces_from_single_image
from insightface.app.face_analysis import FaceAnalysis


class CropFacesThread(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(list)

    def __init__(self, images):
        super().__init__()
        self.images = images
        self.fa = FaceAnalysis()
        self.fa.prepare(ctx_id=0)

    def run(self):
        faces = []
        for i, image in enumerate(self.images):
            faces.extend(get_cropped_faces_from_single_image(image, self.fa))
            self.progress.emit(int((i + 1) / len(self.images) * 100))
        self.result.emit(faces)

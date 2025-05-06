from PIL import Image
import warnings

warnings.filterwarnings("ignore", category=FutureWarning, message=r".*rcond.*")

from insightface.app.face_analysis import FaceAnalysis
import cv2
import numpy as np
from typing import List
from insightface.model_zoo import SCRFD


class Photo:
    def __init__(self, image: Image.Image, cropped: Image.Image, encoding):
        self.image = image
        self.id = None
        self.cropped = cropped
        self.path = None
        self.score = 0
        self.encoding = encoding
        self.age = None

    def set_age(self, age: int):
        self.age = age

    def set_gender(self, gender):
        self.gender = gender

    def set_id(self, id: int):
        self.id = id

    def set_path(self, path: str):
        self.path = path

    def show(self):
        self.image.show()

    def get_metadata(self):
        """Returns metadata of the photo"""
        return {
            "path": self.path,
            "id": self.id,
        }


def get_cropped_faces_from_single_image(
    image: Image.Image, fa: FaceAnalysis
) -> List[Photo]:
    # fa = fa if fa is not None else FaceAnalysis()
    # fa.prepare(ctx_id=0, det_size=(640,640))
    if fa is None:
        fa = FaceAnalysis()

        fa.prepare(ctx_id=0, det_size=(640, 640))

    try:
        faces = fa.get(np.array(image))
    except ValueError as e:
        print(f"Error getting faces: {e}")
        print(np.array(image).shape)
        return []
    # iterates over faces and creates cropped photos of type Photo
    # and resizes the image to 100x100
    photos = []
    for face in faces:
        bbox = face["bbox"]
        # print("AGE: ", face['age'])
        x1, y1, x2, y2 = bbox
        # cropped = image.crop((x1, y1, x2, y2))
        # relative to height
        size_of_add_on = int(image.height * 0.1)  # For example, 10% of the image height
        cropped = image.crop(
            (
                max(0, x1 - size_of_add_on),
                max(0, y1 - size_of_add_on),
                min(image.width, x2 + size_of_add_on),
                min(image.height, y2 + size_of_add_on),
            )
        )
        thumbnail = cropped.copy()
        thumbnail.thumbnail((100, 100))
        # cropped.thumbnail((100, 100))
        encoding = face["embedding"]
        photo = Photo(cropped=thumbnail, image=cropped.copy(), encoding=encoding)
        photo.set_age(face["age"])
        photo.set_gender(face.sex)
        photos.append(photo)
    return photos


def get_cropped_faces_from_images(
    images: List[Image.Image], fa: FaceAnalysis
) -> List[Photo]:
    fa = fa if fa is not None else FaceAnalysis()
    fa.prepare(ctx_id=0, det_size=(640, 640))
    faces = []
    for image in images:
        faces.extend(get_cropped_faces_from_single_image(image, fa))
    return faces


def test_get_cropped_faces():
    path = "PeopleFinder/People/example_people.jpg"
    image = Image.open(path)
    detector = SCRFD("models/det_10g.onnx")
    detector.prepare(ctx_id=0)
    faces = get_cropped_faces_from_single_image(image, None)  # , detector)
    for face in faces:

        face.show()


if __name__ == "__main__":
    # test_get_cropped_faces()
    # get_cropped_faces(Image.open("PeopleFinder/People/example_people.jpg"))
    test_get_cropped_faces()

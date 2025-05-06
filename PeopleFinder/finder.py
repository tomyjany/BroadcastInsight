from insightface.app.face_analysis import FaceAnalysis
from PeopleFinder.People.Photo import get_cropped_faces_from_single_image, Photo
from PeopleFinder.People.Person import Person, find_top_3_people
from PIL import Image
from typing import List
import pickle
import os
import json
from tools.config_mapper import cfg


def load_people_from_database(database_path: str) -> List[Person]:
    """
    Load all saved people from the database directory.

    Args:
        database_path: Path to the directory where people data is stored.

    Returns:
        List[Person]: A list of Person objects loaded from the database.
    """
    people = []

    # Iterate through all JSON files in the database directory
    for file_name in os.listdir(database_path):
        if file_name.endswith(".json"):
            json_path = os.path.join(database_path, file_name)
            with open(json_path, "r", encoding="utf-8") as f:
                person_data = json.load(f)

            # Create a Person object
            person = Person(name_czech=person_data["name_czech"])

            # Load encodings from the corresponding .pkl file
            pkl_path = os.path.join(database_path, person_data["encodings_path"])
            if os.path.exists(pkl_path):
                with open(pkl_path, "rb") as f:
                    encodings = pickle.load(f)
            else:
                encodings = []

            # Load photos and associate them with the person
            for photo_metadata in person_data["photos"]:
                photo_path = os.path.join(
                    database_path, photo_metadata["path"] + ".jpg"
                )
                if os.path.exists(photo_path):
                    photo = Photo(
                        cropped=None,  # Placeholder, as cropped is not needed here
                        image=None,
                        encoding=None,  # Placeholder, as encoding will be set below
                    )
                    # Match encoding by ID
                    for encoding in encodings:
                        if encoding["id"] == photo_metadata["id"]:
                            photo.encoding = encoding["encoding"]
                            photo.set_id(photo_metadata["id"])
                            break
                    person.photos.append(photo)

            people.append(person)

    return people


class PeopleFinder:
    def __init__(self, database_path: str = cfg.PEOPLE_DB_PATH):
        self.database_path = database_path
        self.people = load_people_from_database(database_path)
        self.fa = FaceAnalysis()
        self.fa.prepare(ctx_id=0)

        pass

    def find_people(self, image: Image.Image) -> List[Person]:
        faces = get_cropped_faces_from_single_image(image, self.fa)
        people = []
        for face in faces:
            top_people = find_top_3_people(self.people, face.encoding)
            if top_people[0]["sim"] != 0:
                top_people[0]["age"] = face.age
                top_people[0]["gender"] = face.gender
                people.append(top_people[0])
            else:
                people.append(
                    {
                        "person": "Unknown",
                        "sim": 0,
                        "age": face.age,
                        "gender": face.gender,
                    }
                )
        return people


def test_on_test_image():
    # path = "PeopleFinder/test_image_babis_and_trump.jpg"
    path = "PeopleFinder/zelezny.jpg"
    image = Image.open(path)
    pf = PeopleFinder()
    people = pf.find_people(image)
    print(people)

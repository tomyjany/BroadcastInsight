from PeopleFinder.People.Photo import Photo
import os
import pickle
import json
from unidecode import unidecode
import numpy as np


class Person:
    def __init__(self, name_czech):
        self.name_czech = name_czech
        self.name_simple = create_name_simple(name_czech)
        self.id_iter = 0
        self.photos = []

    def add_photo(self, photo):
        photo.set_id(self.id_iter)
        photo.set_path(self.name_simple + str(self.id_iter) + ".jpg")
        self.id_iter += 1
        self.photos.append(photo)

    def sort_photos(self):
        """uses np.dot(xv, xt) / (np.linalg.norm(xv) * np.linalg.norm(xt)) between encodings
        applies all combinations between photos and each photo keeps score that is a sum of all scores
        then sorts the photos by score
        returns the sorted list of coressponding photos
        """
        for photo in self.photos:
            for photo2 in self.photos:
                if photo != photo2:
                    photo.score += np.dot(photo.encoding, photo2.encoding) / (
                        np.linalg.norm(photo.encoding) * np.linalg.norm(photo2.encoding)
                    )
        self.photos.sort(key=lambda x: x.score, reverse=True)

    def save_person(self):
        """Will create dict of photo metadata in dict and save it as json"""
        dict = {
            "name_czech": self.name_czech,
            "name_simple": self.name_simple,
            "encodings_path": self.name_simple + ".pkl",
            "photos": [],
        }
        encodings = []

        for photo in self.photos:
            dict["photos"].append(photo.get_metadata())

            encodings.append({"encoding": photo.encoding, "id": photo.id})
            with open("PeopleFinder/People/database/" + photo.path + ".jpg", "wb") as f:
                photo.image.save(f, format="JPEG")
        pkl_path = "PeopleFinder/People/database/" + self.name_simple + ".pkl"
        if not os.path.exists(pkl_path):
            with open(pkl_path, "wb") as f:
                pickle.dump(encodings, f)
        json_path = "PeopleFinder/People/database/" + self.name_simple + ".json"
        if not os.path.exists(json_path):
            with open(json_path, "w") as f:
                print(dict)
                json.dump(dict, f)

    def compare_with_person(self, unkonwn_embedding):
        sims = []
        for photo in self.photos:

            sims.append(
                {
                    "sim": float(compare_faces(photo.encoding, unkonwn_embedding)),
                    "person": self.name_simple,
                }
            )
        return sims


def find_top_3_people(people, unknown_embedding):
    """Finds top 3 people with highest similarity to the unknown embedding

    Args:
        people (List[Person]): List of Person objects
        unknown_embedding (InsightEmbedding): Embedding of the unknown photo

    Returns:
        List[Dict[str, Union[str, float]]]: List of dictionaries containing the name of the person and the similarity score
    """
    sims = []
    for person in people:
        sims.extend(person.compare_with_person(unknown_embedding))
    sims.sort(key=lambda x: x["sim"], reverse=True)
    return sims[:3]


def compare_faces(
    database_emb, unknown_emb
):  # Adjust this threshold according to your usecase.
    """Cossine similarity between two embeddings

    Args:
        database_emb (InsightEmbedding): embedding of one of the original annotated photos
        unknown_emb (InsightEmbedding): embedding of the unknown photo

    Returns:
        np.float: similarity between the two embeddings
    """
    similarity = np.dot(database_emb, unknown_emb) / (
        np.linalg.norm(database_emb) * np.linalg.norm(unknown_emb)
    )
    if similarity < 0.5:
        similarity = 0
    return similarity


def create_name_simple(name_czech):
    name_ascii = unidecode(name_czech)
    name_ascii = name_ascii.lower().replace(" ", "_")
    return name_ascii


def test_person_save():
    """Tests saving person"""
    from PIL import Image
    from PeopleFinder.People.Photo import Photo, get_cropped_faces_from_images

    photos = get_cropped_faces_from_images(
        [Image.open("PeopleFinder/People/example_people.jpg")], None
    )
    person = Person("Petr Novák")
    for photo in photos:
        person.add_photo(photo)

    person.save_person()


if __name__ == "__main__":
    test_person_save()

import unittest
from unittest.mock import MagicMock
from PeopleFinder.People.Person import Person, find_top_3_people


class TestFindTop3People(unittest.TestCase):
    def setUp(self):
        # Create mock embeddings
        self.unknown_embedding = [0.1, 0.2, 0.3, 0.4]

        # Create mock people
        self.person1 = Person(name_czech="Person 1")
        self.person1.compare_with_person = MagicMock(
            return_value=[
                {"name": "Person 1", "sim": 0.9},
                {"name": "Person 1", "sim": 0.85},
            ]
        )

        self.person2 = Person(name_czech="Person 2")
        self.person2.compare_with_person = MagicMock(
            return_value=[
                {"name": "Person 2", "sim": 0.8},
                {"name": "Person 2", "sim": 0.75},
            ]
        )

        self.person3 = Person(name_czech="Person 3")
        self.person3.compare_with_person = MagicMock(
            return_value=[
                {"name": "Person 3", "sim": 0.7},
                {"name": "Person 3", "sim": 0.65},
            ]
        )

        self.people = [self.person1, self.person2, self.person3]

    def test_find_top_3_people(self):
        # Call the function
        top_3 = find_top_3_people(self.people, self.unknown_embedding)

        # Assert the results
        self.assertEqual(len(top_3), 3)
        self.assertEqual(top_3[0]["name"], "Person 1")
        self.assertEqual(top_3[0]["sim"], 0.9)
        self.assertEqual(top_3[1]["name"], "Person 1")
        self.assertEqual(top_3[1]["sim"], 0.85)
        self.assertEqual(top_3[2]["name"], "Person 2")
        self.assertEqual(top_3[2]["sim"], 0.8)

    def test_find_top_3_people_with_fewer_results(self):
        # Modify one person to return fewer results
        self.person3.compare_with_person = MagicMock(
            return_value=[{"name": "Person 3", "sim": 0.7}]
        )

        # Call the function
        top_3 = find_top_3_people(self.people, self.unknown_embedding)

        # Assert the results
        self.assertEqual(len(top_3), 3)
        self.assertEqual(top_3[0]["name"], "Person 1")
        self.assertEqual(top_3[0]["sim"], 0.9)
        self.assertEqual(top_3[1]["name"], "Person 1")
        self.assertEqual(top_3[1]["sim"], 0.85)
        self.assertEqual(top_3[2]["name"], "Person 2")
        self.assertEqual(top_3[2]["sim"], 0.8)


if __name__ == "__main__":
    unittest.main()

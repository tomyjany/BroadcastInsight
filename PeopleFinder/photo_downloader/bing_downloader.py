from PeopleFinder.photo_downloader.interface import PhotoGetterInterface
from dotenv import load_dotenv
from PIL import Image
import os
import requests
from io import BytesIO
from typing import List


load_dotenv(override=True)


class BingPhotoGetter(PhotoGetterInterface):
    def get_photo(
        self, query_person_name: str, number_of_pictures=10
    ) -> List[Image.Image]:
        """Will use bing to download picture of the person"""

        search_url = "https://api.bing.microsoft.com/v7.0/images/search"
        headers = {
            "Ocp-Apim-Subscription-Key": os.environ["BING_SEARCH_V7_SUBSCRIPTION_KEY"]
        }
        params = {
            "q": query_person_name,
            "count": number_of_pictures,
            "imageType": "photo",
        }
        response = requests.get(search_url, headers=headers, params=params)
        print(response)
        response.raise_for_status()
        data = response.json().get("value", [])
        print(data)
        if not data:
            return None
        # image_url = data[0]["contentUrl"]
        # img_response = requests.get(image_url)
        # img_response.raise_for_status()

        images = []
        for img in data:
            img_response = requests.get(img["contentUrl"])
            try:
                img_response.raise_for_status()
                images.append(Image.open(BytesIO(img_response.content)))
            except Exception as e:
                print(f"Error downloading image: {e}")
        print(len(images))
        return images


def test_bing_photo_getter():
    from matplotlib import pyplot as plt

    bing_photo_getter = BingPhotoGetter()
    photos = bing_photo_getter.get_photo("Bill Gates")
    for photo in photos:
        assert photo is not None
        assert isinstance(photo, Image.Image)
        photo.show()


if __name__ == "__main__":
    test_bing_photo_getter()

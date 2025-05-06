from PyQt5.QtCore import QThread, pyqtSignal
import os
import requests
from PIL import Image
from io import BytesIO


class DownloadThread(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(list)

    def __init__(self, query_person_name, number_of_pictures):
        super().__init__()
        self.query_person_name = query_person_name
        self.number_of_pictures = number_of_pictures

    def run(self):
        search_url = "https://api.bing.microsoft.com/v7.0/images/search"
        headers = {
            "Ocp-Apim-Subscription-Key": os.environ["BING_SEARCH_V7_SUBSCRIPTION_KEY"]
        }
        params = {
            "q": self.query_person_name,
            "count": self.number_of_pictures,
            "imageType": "photo",
        }
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json().get("value", [])
        if not data:
            self.result.emit([])
            return

        images = []
        for i, img in enumerate(data):
            img_response = requests.get(img["contentUrl"])
            try:
                img_response.raise_for_status()
                images.append(Image.open(BytesIO(img_response.content)))
                self.progress.emit(int((i + 1) / len(data) * 100))
            except Exception as e:
                print(f"Error downloading image: {e}")
        self.result.emit(images)

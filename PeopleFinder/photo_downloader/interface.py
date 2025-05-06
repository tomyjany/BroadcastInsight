from abc import ABC, abstractmethod
from typing import List
from PIL import Image


class PhotoGetterInterface(ABC):
    @abstractmethod
    def get_photo(
        self, query_person_name: str, number_of_pictures=10
    ) -> List[Image.Image]:
        """Will use some interface like bing or google search to download picture of the person"""
        pass


def get_downloader(downloader_name: str) -> PhotoGetterInterface:
    if downloader_name == "bing":
        from PeopleFinder.photo_downloader.bing_downloader import BingPhotoGetter

        return BingPhotoGetter()
    elif downloader_name == "google":
        raise NotImplementedError("Google downloader is not implemented yet")
    else:
        raise ValueError("Unknown downloader name")

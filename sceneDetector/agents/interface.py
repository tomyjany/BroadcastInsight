from abc import ABC, abstractmethod
from typing import List
import json


class SceneDetectorI(ABC):
    def __init__(self):
        self.cuts = []  # List of dictionaries to store frame and timestamp
        self.bcuts = []  # List of

    @abstractmethod
    def detect_shot(self, file_path_to_video: str) -> List[str]:
        """
        Detects the shot cuts in the given video file and returns a list of timestamps.

        :param file_path_to_video: Path to the video file.
        :return: List of timestamps indicating the cuts between scenes.
        """
        pass

    @abstractmethod
    def detect_shot_with_timestamps(self, file_path_to_video: str) -> List[dict]:
        """
        Detects the shot cuts in the given video file and returns a list of dictionaries.

        :param file_path_to_video: Path to the video file.
        :return: List of frames and timestamps indicating the cuts between scenes.
        """
        pass

    @abstractmethod
    def detect_shot_with_bondaries(self, file_path_to_video: str):
        """
        Detects the shot cuts with the interval included.
        That is because some methods also include the timing for each cut and are detecting it.

        This method will be redundand for pyscenedetect, but is needed for transnet and other more advanced libraries.
        """
        pass

    def save_cuts_to_file(self, file_name):
        cuts_data = {"cuts": self.cuts}
        with open(file_name, "w") as f:
            json.dump(cuts_data, f, indent=4)

    def save_boundary_cuts_to_file(self, file_name):
        cuts_data = {"cuts": self.bcuts}
        with open(file_name, "w") as f:
            json.dump(cuts_data, f, indent=4)


libraries = ["scenedetect", "transnet", "autoshot", "ffprobe"]


def get_libraries() -> List[str]:
    return libraries


# Factory Method


def get_scene_detector(library_name: str) -> SceneDetectorI:
    if library_name not in libraries:
        raise ValueError(f"Library {library_name} not supported.")
    if library_name == "scenedetect":
        from sceneDetector.agents.SceneDetectImpl import SceneDetectImpl

        return SceneDetectImpl()
    if library_name == "transnet":
        from sceneDetector.agents.transnet import TransNetImpl

        return TransNetImpl()
    if library_name == "autoshot":
        from sceneDetector.agents.autoshot import Autoshot

        return Autoshot()

    if library_name == "ffprobe":
        from sceneDetector.agents.ffprobe import Ffprobe

        return Ffprobe()


def get_scene_detector_by_number(scene_number: int) -> SceneDetectorI:
    selected_library = libraries[scene_number]
    return get_scene_detector(selected_library)

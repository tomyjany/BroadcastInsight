from sceneDetector.agents.interface import SceneDetectorI
import cv2
import numpy as np
import sys
import os

sys.path.append(os.path.relpath("Autoshot"))
from Autoshot.infer import get_shot_boundary_frames


class Autoshot(SceneDetectorI):
    def __init__(self):
        self.scene_list = None
        self.fps = None

    def detect_shot(self, file_path_to_video):
        self.cuts = get_shot_boundary_frames(file_path_to_video)
        return self.cuts

    def get_fps(self, file_path_to_video):
        if not self.fps:
            video = cv2.VideoCapture(file_path_to_video)
            self.fps = video.get(cv2.CAP_PROP_FPS)

    def detect_shot_with_timestamps(self, file_path_to_video):
        return NotImplementedError

    def detect_shot_with_timestamps(self, file_path_to_video: str):
        self.get_fps(file_path_to_video)
        self.cuts = [
            {"frame": int(scene[0]), "timestamp": int((scene[0] / self.fps) * 1000)}
            for scene in self.scene_list
        ]
        # print(self.cuts)
        return self.cuts

    def detect_shot_with_bondaries(self, file_path_to_video):
        cuts = self.detect_shot(file_path_to_video)
        self.get_fps(file_path_to_video)

        self.bcuts = []
        for cut in cuts:
            self.bcuts.append(
                {
                    "start": cut,
                    "end": cut + 1,
                    "time_start": (cut / self.fps) * 1000,
                    "time_end": (cut + 1 / self.fps) * 1000,
                }
            )
        print(self.bcuts)
        return self.bcuts

import os
import cv2
import sys
import numpy as np
from sceneDetector.agents.interface import SceneDetectorI
from TransNetV2.inference.transnetv2 import TransNetV2
from tools.config_mapper import cfg


class TransNetImpl(SceneDetectorI):
    def __init__(self):
        super().__init__()
        self.scene_list = None
        self.fps = None
        self.model = TransNetV2(model_dir=cfg.TRANSNET_MODEL_DIR)

    def _detect_scenes_if_needed(self, file_path_to_video):
        if not self.scene_list:
            video_frames, single_frame_predictions, all_frame_predictions = (
                self.model.predict_video(file_path_to_video)
            )
            self.scene_list = self.model.predictions_to_scenes(single_frame_predictions)
            print("SCENELIST ", self.scene_list)

    def detect_shot(self, file_path_to_video):
        self._detect_scenes_if_needed(file_path_to_video)
        return [str(scene[0]) for scene in self.scene_list]

    def get_fps(self, file_path_to_video):
        if not self.fps:
            video = cv2.VideoCapture(file_path_to_video)
            self.fps = video.get(cv2.CAP_PROP_FPS)

    def detect_shot_with_timestamps(self, file_path_to_video: str):
        self._detect_scenes_if_needed(file_path_to_video)
        self.get_fps(file_path_to_video)
        self.cuts = [
            {"frame": int(scene[0]), "timestamp": int((scene[0] / self.fps) * 1000)}
            for scene in self.scene_list
        ]
        # print(self.cuts)
        return self.cuts

    def detect_shot_with_bondaries(self, file_path_to_video):
        self._detect_scenes_if_needed(file_path_to_video)
        self.get_fps(file_path_to_video)
        first = int(self.scene_list[0][1])
        self.bcuts = []
        for scene in self.scene_list[1::]:
            self.bcuts.append(
                {
                    "start": first,
                    "end": int(scene[0]),
                    "time_start": (first / self.fps) * 1000,
                    "time_end": (int(scene[0]) / self.fps) * 1000,
                }
            )
            first = int(scene[1])
        print(self.bcuts)
        return self.bcuts


if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

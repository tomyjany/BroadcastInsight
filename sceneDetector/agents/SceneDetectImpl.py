from typing import List
import cv2
from scenedetect import open_video, SceneManager, ContentDetector
from sceneDetector.agents.interface import SceneDetectorI
from tools.config_mapper import cfg


class SceneDetectImpl(SceneDetectorI):
    def __init__(self):
        super().__init__()  # Initialize the parent class
        self.scene_list = None  # Store detected scenes for reuse
        self.fps = None  # Store video FPS

    def _detect_scenes_if_needed(self, video):
        """Helper method to detect scenes if they haven't been detected yet."""
        if self.scene_list is None:
            scene_manager = SceneManager()
            scene_manager.add_detector(
                ContentDetector(
                    threshold=cfg.PYSCENE_THRESHOLD,
                    min_scene_len=cfg.PYSCENE_MIN_SCENE_LEN,
                )
            )
            video.seek(0)  # Seek to the start if needed
            scene_manager.detect_scenes(video)
            self.scene_list = scene_manager.get_scene_list()

    def detect_shot(self, file_path_to_video: str) -> List[str]:
        """Detects the cuts in the video and returns timestamps as strings."""
        video = open_video(file_path_to_video)
        self._detect_scenes_if_needed(video)  # Detect scenes if not already done

        # Convert frame numbers to strings (timestamps as placeholders, for example)
        return [
            str(scene[0].get_frames()) for scene in self.scene_list
        ]  # Return as string list

    # def detect_shot_with_bondaries(self, file_path_to_video):
    #     shots = self.detect_shot(file_path_to_video)
    #     self.bcuts = [
    #         {
    #             "begin": int(shot) - 1,
    #             "end": int(shot),
    #             "timestamp": int((shot / self.fps) * 1000),
    #         }
    #         for shot in shots
    #     ]
    def get_fps(self, file_path_to_video):
        if not self.fps:
            video = cv2.VideoCapture(file_path_to_video)
            self.fps = video.get(cv2.CAP_PROP_FPS)

    def detect_shot_with_bondaries(self, file_path_to_video):
        cuts = self.detect_shot(file_path_to_video)
        self.get_fps(file_path_to_video)
        # self.get_fps(file_path_to_video)

        self.bcuts = []
        for cut in cuts:
            self.bcuts.append(
                {
                    "start": int(cut),
                    "end": int(cut) + 1,
                    "time_start": (int(cut) / self.fps) * 1000,
                    "time_end": (int(cut) + 1 / self.fps) * 1000,
                }
            )
        return self.bcuts

    def detect_shot_with_timestamps(self, file_path_to_video: str) -> List[dict]:
        """Returns cuts with both frame numbers and timestamps in milliseconds."""
        video = open_video(file_path_to_video)
        self.get_fps(file_path_to_video)

        if self.fps is None:  # Cache the FPS to avoid redundant get_fps() calls
            # self.fps = video.get(cv2.CAP_PROP_FPS)
            self.fps = video.frame_rate

        self._detect_scenes_if_needed(video)  # Detect scenes if not already done

        # Save cuts as dictionaries with frame and timestamp (in milliseconds)
        self.cuts = [
            {
                "frame": scene[0].get_frames(),
                "timestamp": int(
                    (scene[0].get_frames() / self.fps) * 1000
                ),  # Calculate timestamp in milliseconds
            }
            for scene in self.scene_list
        ]

        return self.cuts  # Return the list of dictionaries

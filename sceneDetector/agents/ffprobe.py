from sceneDetector.agents.interface import SceneDetectorI
import subprocess
import json
import cv2
import logging
import subprocess
import cv2
import sys
import os
from tools.config_mapper import cfg

sys.path.append(os.path.relpath("shot_benchmarks"))
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
# from shot_benchmarks.detectors.ffprobe_shots import extract_shots_with_ffprobe


class Ffprobe(SceneDetectorI):
    def __init__(self):
        self.fps = None
        self.cuts = []
        self.bcuts = []

    def detect_shot(self, file_path_to_video):
        return extract_shots_with_ffprobe(file_path_to_video)

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
        return self.bcuts


def get_ffprobe_version():
    """
    Retrieves the major version number of the installed ffprobe.

    Returns:
        int: Major version number of ffprobe.
    """
    try:
        result = subprocess.run(
            ["ffprobe", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        version_line = result.stdout.split("\n")[0]
        version_number = version_line.split()[2]
        major_version = int(version_number.split(".")[0])
        return major_version
    except (IndexError, ValueError, subprocess.CalledProcessError) as e:
        raise RuntimeError(f"Error determining ffprobe version: {e}")


def extract_shots_with_ffprobe(src_video, threshold=0.1):
    """
    Detects scene changes and returns the corresponding frame numbers.

    Args:
        src_video (str): Path to the source video file.
        threshold (float): Scene change detection threshold.

    Returns:
        List[int]: A list of frame numbers where scene changes occur.
    """
    ffprobe_major_version = get_ffprobe_version()
    logging.info(f"Detected ffprobe version: {ffprobe_major_version}")

    if ffprobe_major_version > 5:
        logging.warning("Using ffprobe version v6 for scene detection.")
        return extract_shots_with_ffprobe_v6(src_video, threshold)
    else:
        logging.warning("Using ffprobe version v7 for scene detection.")
        return extract_shots_with_ffprobe_v7(src_video, threshold)


def extract_shots_with_ffprobe_v6(src_video, threshold=0.1):
    """
    Uses ffprobe (version < 7.0) to detect scene changes using coded_picture_number.

    Args:
        src_video (str): Path to the source video file.
        threshold (float): Scene change detection threshold.

    Returns:
        List[int]: A list of frame numbers where scene changes occur.
    """
    cmd = [
        "ffprobe",
        "-show_frames",
        "-of",
        "json",
        "-f",
        "lavfi",
        f"movie={src_video},select=gt(scene\\,{threshold})",
    ]
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
    )
    output = json.loads(result.stdout)

    boundaries = []
    for frame in output.get("frames", []):
        frame_number = int(frame.get("coded_picture_number", 0))
        boundaries.append(frame_number)

    return boundaries


def extract_shots_with_ffprobe_v7(src_video, threshold=0.1):
    """
    Uses ffprobe (version >= 7.0) to detect scene changes using pkt_pts_time.

    Args:
        src_video (str): Path to the source video file.
        threshold (float): Scene change detection threshold.

    Returns:
        List[int]: A list of frame numbers where scene changes occur.
    """
    fps = get_video_fps(src_video)
    if fps is None:
        raise RuntimeError("Unable to determine FPS for the video.")

    cmd = [
        "ffprobe",
        "-show_frames",
        "-of",
        "json",
        "-f",
        "lavfi",
        f"movie={src_video},select=gt(scene\\,{threshold})",
    ]
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
    )
    output = json.loads(result.stdout)

    boundaries = []
    for frame in output.get("frames", []):
        pkt_pts_time = float(frame.get("pkt_pts_time", 0))
        frame_number = int(round(pkt_pts_time * fps))
        boundaries.append(frame_number)

    return boundaries


def get_video_fps(video_path):
    """
    Determines the frames per second (FPS) of the given video.

    Args:
        video_path (str): Path to the video file.

    Returns:
        float: Frames per second of the video, or None if it cannot be determined.
    """
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    video.release()
    return fps if fps > 0 else None

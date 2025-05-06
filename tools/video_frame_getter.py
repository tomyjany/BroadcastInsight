from typing import List, Tuple
from PIL import Image
import cv2


class VideoFrameGetter:
    """This class will return an iterator that yields a tuple containing:
    - PIL Image of the middle frame
    - Metadata about the scene (start frame, end frame, start time, end time in milliseconds)

    Example usage:
        video = VideoFrameGetter("path_to_video.mp4", cuts)
        for frame, metadata in video:
            frame.show()
            print(metadata)
    """

    def __init__(self, path_to_video: str, cuts: List[dict]):
        self.path_to_video = path_to_video
        self.cuts = self._calculate_intervals(cuts)
        self.cap = cv2.VideoCapture(path_to_video)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video file: {path_to_video}")
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

    def _calculate_intervals(self, cuts: List[dict]) -> List[dict]:
        intervals = []
        previous_end = 0  # Start from the first frame
        previous_time_end = 0  # Start from time 0 ms
        for cut in cuts:
            start_frame = previous_end
            end_frame = cut["start"]
            start_time = previous_time_end
            end_time = cut["time_start"]
            intervals.append(
                {
                    "start_frame": start_frame,
                    "end_frame": end_frame,
                    "start_time": start_time,
                    "end_time": end_time,
                }
            )
            previous_end = cut["end"]
            previous_time_end = cut["time_end"]
        return intervals

    def __iter__(self):
        return self

    def __next__(self) -> Tuple[Image.Image, dict]:
        if not self.cuts:
            self.cap.release()
            raise StopIteration

        cut = self.cuts.pop(0)
        middle_frame = int((cut["start_frame"] + cut["end_frame"]) / 2)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
        ret, frame = self.cap.read()

        if not ret:
            raise ValueError(f"Failed to read frame at position {middle_frame}")

        # Convert the frame to a PIL Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame_rgb), cut

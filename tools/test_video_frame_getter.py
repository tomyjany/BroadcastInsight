import json
from matplotlib import pyplot as plt
from PIL import Image
from video_frame_getter import VideoFrameGetter
import cv2


def test_video_frame_getter(video_path: str, cuts_file: str):
    # Load cuts from the JSON file
    with open(cuts_file, "r") as f:
        data = json.load(f)
    cuts = data["cuts"]

    # Initialize VideoFrameGetter
    video_frame_getter = VideoFrameGetter(video_path, cuts)

    # Open video with OpenCV for boundary frames
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    for frame, metadata in video_frame_getter:
        start_frame = metadata["start_frame"]
        end_frame = metadata["end_frame"]

        # Get left boundary frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        ret, left_frame = cap.read()
        if not ret:
            raise ValueError(f"Failed to read frame at position {start_frame}")
        left_frame_rgb = cv2.cvtColor(left_frame, cv2.COLOR_BGR2RGB)

        # Get right boundary frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, end_frame)
        ret, right_frame = cap.read()
        if not ret:
            raise ValueError(f"Failed to read frame at position {end_frame}")
        right_frame_rgb = cv2.cvtColor(right_frame, cv2.COLOR_BGR2RGB)

        # Plot the frames and metadata
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        axes[0].imshow(left_frame_rgb)
        axes[0].set_title(f"Left Boundary (Frame {start_frame})")
        axes[0].axis("off")

        axes[1].imshow(frame)
        axes[1].set_title(f"Middle Frame\n{metadata}")
        axes[1].axis("off")

        axes[2].imshow(right_frame_rgb)
        axes[2].set_title(f"Right Boundary (Frame {end_frame})")
        axes[2].axis("off")

        plt.show()

    cap.release()


# Example usage
test_video_frame_getter(
    "video.mp4", "video-label.json"
)

import os
import cv2
import argparse


def create_output_folder(video_path, output_dir):
    """Create a folder named after the original video in the output directory."""
    # Get the base name of the video (without extension)
    base_name = os.path.splitext(os.path.basename(video_path))[0]

    # Create the folder path
    folder_path = os.path.join(output_dir, base_name)
    os.makedirs(folder_path, exist_ok=True)

    return folder_path, base_name


def cut_video(video_path, output_dir):
    """Cut the video into 1-minute parts and save them in a folder named after the video."""
    # Open the video using OpenCV
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)  # Frames per second
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Total number of frames
    video_length_seconds = total_frames / fps  # Total video length in seconds

    part_duration_seconds = 120
    part_frames = int(fps * part_duration_seconds)

    # Create the output folder named after the video
    output_folder, base_name = create_output_folder(video_path, output_dir)

    part_number = 1
    frame_counter = 0

    while frame_counter < total_frames:
        # Create the output file name for the current part
        output_file = os.path.join(output_folder, f"{base_name}_part_{part_number}.mp4")

        # Video writer for the output part
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video_writer = cv2.VideoWriter(
            output_file,
            fourcc,
            fps,
            (
                int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            ),
        )

        # Write the frames for the current part
        for _ in range(part_frames):
            ret, frame = cap.read()
            if not ret:
                break  # End of video
            video_writer.write(frame)
            frame_counter += 1

        video_writer.release()  # Release the writer after finishing the part
        part_number += 1

    cap.release()
    print(f"Video cut into {part_number - 1} parts and saved to {output_folder}.")


def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Cut video into 1-minute parts.")
    parser.add_argument("video_path", type=str, help="Path to the input video.")
    parser.add_argument(
        "output_dir", type=str, help="Directory to save the output video parts."
    )

    args = parser.parse_args()

    # Run the video cutting function
    cut_video(args.video_path, args.output_dir)


if __name__ == "__main__":
    main()

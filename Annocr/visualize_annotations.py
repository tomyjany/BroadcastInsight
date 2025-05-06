import sys
import cv2
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def load_annotations(annotation_path):
    try:
        with open(annotation_path, "r", encoding="utf-8") as file:
            annotations = file.readlines()
    except FileNotFoundError:
        # if not found, will load different file
        print(f"Error: Unable to load annotations at {annotation_path}")
        annotations = []

    return annotations


def visualize_annotations(image_path):
    # Derive the annotation path from the image path
    annotation_path = os.path.splitext(image_path)[0] + ".boxes"

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Unable to load image at {image_path}")
        return

    # Convert the image from BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Load annotations
    annotations = load_annotations(annotation_path)

    # Create a figure and axis
    fig, ax = plt.subplots(1)

    # Display the image
    ax.imshow(image)

    # Iterate over each annotation
    for annotation in annotations:
        parts = annotation.split()
        label = parts[0]
        text = " ".join(parts[1:-4])
        x, y, w, h = map(float, parts[-4:])

        # Create a rectangle patch
        rect = patches.Rectangle(
            (x, y), w, h, linewidth=2, edgecolor="g", facecolor="none"
        )
        ax.add_patch(rect)

        # Add the text label
        plt.text(
            x,
            y - 10,
            text,
            fontsize=10,
            color="g",
            bbox=dict(facecolor="white", alpha=0.5),
        )

    # Show the plot
    plt.show()
    # Example usage


def visualize_annotations_in_directory(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(directory_path, filename)
            annotation_path = os.path.splitext(image_path)[0] + ".boxes"
            if os.path.exists(annotation_path):
                visualize_annotations(image_path)
        # if filename.endswith(".jpg") or filename.endswith(".png"):
        #     image_path = os.path.join(directory_path, filename)
        #     visualize_annotations(image_path)


if __name__ == "__main__":
    # visualize_annotations('ocr_dat')
    visualize_annotations_in_directory("ocr_data/data")

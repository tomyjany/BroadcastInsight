import os
from PIL import Image

import matplotlib.pyplot as plt


def get_image_info(image_path):
    with Image.open(image_path) as img:
        image_size = img.size
        file_size = os.path.getsize(image_path)
        file_format = img.format
    return image_size, file_size, file_format


def visualize_image_info(image_info):
    formats = [info["format"] for info in image_info]
    sizes = [info["file_size"] for info in image_info]
    dimensions = [info["image_size"] for info in image_info]

    plt.figure(figsize=(10, 6))

    plt.subplot(1, 3, 1)
    plt.hist(formats, bins=len(set(formats)), edgecolor="black")
    plt.title("Image Formats")
    plt.xlabel("Format")
    plt.ylabel("Count")

    plt.subplot(1, 3, 2)
    plt.hist(sizes, bins=10, edgecolor="black")
    plt.title("File Sizes")
    plt.xlabel("Size (bytes)")
    plt.ylabel("Count")

    plt.subplot(1, 3, 3)
    width, height = zip(*dimensions)
    plt.scatter(width, height)
    plt.title("Image Dimensions")
    plt.xlabel("Width (pixels)")
    plt.ylabel("Height (pixels)")

    plt.tight_layout()
    plt.show()

    def count_box_files(directory):
        box_count = 0
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(".boxes"):
                    box_count += 1
        print(f"Number of '.box' files: {box_count}")

    count_box_files(directory)


def main(directory):
    image_info = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                image_path = os.path.join(root, file)
                image_size, file_size, file_format = get_image_info(image_path)
                image_info.append(
                    {
                        "image_size": image_size,
                        "file_size": file_size,
                        "format": file_format,
                    }
                )

    visualize_image_info(image_info)


if __name__ == "__main__":
    directory = ""
    main(directory)

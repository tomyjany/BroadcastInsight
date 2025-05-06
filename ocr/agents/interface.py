import os
import json
import cv2
from abc import ABC, abstractmethod
from typing import List, Dict, Union, Tuple
from PIL import Image


class OCRInterface(ABC):
    @abstractmethod
    def ocr_raw(self, image: Image.Image) -> str:
        """will return any text that is default to library, will be mainly used for debugging"""
        pass

    def _load_image(self, image_path):
        return cv2.imread(image_path)

    def ocr_raw_from_path(self, image_path):
        image = self._load_image(image_path)
        return self.ocr_raw(image)
    def safe_raw_ocr_from_path(self, image_path, output_name):
        text = self.ocr_raw_from_path(image_path)
        with open(output_name, "w+", encoding="utf-8") as f:
            f.write(text)



    def save_text(self, text, file_path):
        with open(file_path, "w") as f:
            f.write(text)

    @abstractmethod
    def visualize_ocr(self, image):
        """This will return image with bounding boxes and text"""
        pass

    @abstractmethod
    def structured_text(self, image):
        pass

    @abstractmethod
    def get_ocr_as_bboxes(
        self, image
    ) -> List[Dict[str, Union[str, Tuple[int, int, int, int]]]]:
        """
        This method performs OCR on the given image and returns the bounding boxes and text.

        Args:
            image: The image to perform OCR on.

        Returns:
            List[Dict[str, Union[str, Tuple[int, int, int, int]]]]: A list of dictionaries where each dictionary contains:
                - 'text': The recognized text (str).
                - 'coordinates': A tuple of four integers representing the bounding box (x, y, width, height).
        """
        pass

    def safe_ocr_as_bboxes(self, image, output_file):
        results = self.get_ocr_as_bboxes(image)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        return results

    def safe_ocr_as_bboxes_on_directory(
        self, directory: str, output_file: str, maximum_images=70
    ) -> None:
        """
        This function processes all images in the specified directory that have corresponding annotation files.
        It performs OCR on each image, compares the results with the annotations, and saves the combined results
        in the specified output file.

        Args:
            directory: The directory containing the images and annotations.
            output_file: The file to save the OCR results.

        The output JSON file will have the following structure:
        [
            {
                "file": "image_filename.jpg",
                "annotation": [
                    {
                        "tag": "T1",
                        "text": "Annotated text",
                        "coordinates": (x, y, w, h)
                    },
                    ...
                ],
                "ocr_result": [
                    {
                        "text": "Recognized text",
                        "coordinates": (x, y, w, h)
                    },
                    ...
                ]
            },
            ...
        ]
        """
        results = []
        ite = 0
        for file in os.listdir(directory):
            if file.endswith(".jpg"):
                image_path = os.path.join(directory, file)
                bbox_path = image_path.replace(".jpg", ".boxes")
                if not os.path.exists(bbox_path):
                    continue

                print(f"processing {file} {(ite + 1) * 100 / len(os.listdir(directory)):.2f}")
                ite += 1

                annotations = load_annotation(bbox_path)
                ocr_results = self.get_ocr_as_bboxes(image_path)
                result = {
                    "file": file,
                    "annotation": annotations,
                    "ocr_result": ocr_results,
                }
                results.append(result)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
            print("saved to file: ", output_file)
        return

    def structured_text_from_path(self, image_path):
        image = self._load_image(image_path)
        return self.structured_text(image)

    def visualize_ocr_from_path(self, image_path):
        image = self._load_image(image_path)
        self.visualize_ocr(image)

    def ocr_from_bbox(self, image_path):
        """
        This will return the text from the bounding box
        The image_path is the path to the image.
        Note that path to the annotation with bounding box should be the same as the image_path but with .boxes extension
        """
        image = self._load_image(image_path)
        bbox_path = image_path.replace(".jpg", ".boxes")

        results = []

        with open(bbox_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 6:
                    tag = parts[0]
                    text = " ".join(parts[1:-4])
                    x, y, w, h = map(int, map(float, parts[-4:]))
                    roi = image[y : y + h, x : x + w]
                    ocr_text = self.ocr_raw(roi).replace("\n", "")
                    results.append(
                        {
                            "tag": tag,
                            "text": text,
                            "ocr_text": ocr_text,
                            "coordinates": (x, y, w, h),
                        }
                    )

        return results

    def ocr_from_bbox_on_directory(self, directory, output_file):
        """
        This will return the text from the bounding box
        The image_path is the path to the image.
        Note that path to the annotation with bounding box should be the same as the image_path but with .boxes extension
        """
        results = []
        ite = 0
        for file in os.listdir(directory):
            if file.endswith(".boxes"):
                ite += 1
                print(f"processing {file} {((ite + 1) * 100 / 70):.2f}")
                bbox_path = os.path.join(directory, file)
                image_path = bbox_path.replace(".boxes", ".jpg")
                if os.path.exists(image_path):
                    image = self._load_image(image_path)

                    with open(bbox_path, "r", encoding="utf-8") as f:
                        for line in f:
                            parts = line.strip().split()
                            if len(parts) >= 6:
                                tag = parts[0]
                                text = " ".join(parts[1:-4])
                                x, y, w, h = map(int, map(float, parts[-4:]))

                                # Validate bounding box
                                height, width, _ = image.shape
                                if x < 0 or y < 0 or x + w > width or y + h > height:
                                    print(f"Invalid bounding box: {(x, y, w, h)}")
                                    continue

                                roi = image[y : y + h, x : x + w]

                                # Convert ROI to PIL image and pass to ocr_raw
                                ocr_text = self.ocr_raw(roi).replace("\n", "")

                                results.append(
                                    {
                                        "tag": tag,
                                        "text": text,
                                        "ocr_text": ocr_text,
                                        "coordinates": (x, y, w, h),
                                    }
                                )
        # Save results to JSON file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        return results


def load_annotation(
    annotation_path: str,
) -> List[Dict[str, Union[str, Tuple[int, int, int, int]]]]:
    """
    This method loads the annotation from the given path.

    Args:
        annotation_path: The path to the annotation file.

    Returns:
        List[Dict[str, Union[str, Tuple[int, int, int, int]]]]: A list of dictionaries where each dictionary contains:
            - 'tag': The tag associated with the annotation (str).
            - 'text': The annotated text (str).
            - 'coordinates': A tuple of four integers representing the bounding box (x, y, width, height).
    """
    results = []
    with open(annotation_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 6:
                tag = parts[0]
                text = " ".join(parts[1:-4])
                x, y, w, h = map(int, map(float, parts[-4:]))
                data = {"tag": tag, "text": text, "coordinates": (x, y, w, h)}
                results.append(data)
    return results


libraries = ["tesseract", "easyocr", "paddleocr"]


# Factory method
def get_ocr_agent(agent_name):
    if agent_name == "tesseract":
        from ocr.agents.tesseractI import TesseractI

        return TesseractI()
    elif agent_name == "easyocr":
        from ocr.agents.easyocrI import EasyOCRInterface

        return EasyOCRInterface()
    elif agent_name == "paddleocr":
        from ocr.agents.paddleI import PaddleOCRInterface

        return PaddleOCRInterface()
    else:
        raise ValueError("Invalid agent name")

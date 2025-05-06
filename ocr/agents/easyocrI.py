import easyocr
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import List, Dict, Union, Tuple
import matplotlib.pyplot as plt
import cv2
from ocr.agents.interface import OCRInterface
from PIL import Image
from tools.config_mapper import cfg


class EasyOCRInterface(OCRInterface):
    def __init__(self,lang=cfg.EASY_LANG,gpu=cfg.EASY_GPU, detect_network=cfg.EASY_DETECTION_MODEL, recog_network = cfg.EASY_RECOGNITION_MODEL
):
        self.reader = easyocr.Reader(
            [lang], gpu=gpu, detect_network=detect_network, recog_network =recog_network
        )  # Initialize EasyOCR with Czech language support
        self.name = f"EASY_OCR_lang:{lang}_gpu:_{gpu}_detection:{detect_network}_recognition:_{recog_network}.json"

    def _load_image(self, image_path):
        return cv2.imread(image_path)

    def __str__(self):
        return self.name

    # def ocr_raw(self, image: Image.Image):
    #     # result = self.reader.readtext(np.array(image))
    #     print("inference zacala")
    #     result = self.reader.recognize_direct(image)
    #     print("inference hotova")
    #     text = " ".join([res[1] for res in result])
    #     return text

    def ocr_raw(self, image: Image.Image):
        # result = self.reader.readtext(np.array(image))
        result = self.reader.readtext(image)
        print("inference hotova")
        text = " ".join([res[1] for res in result])
        return text

    def save_text(self, text, file_path):
        with open(file_path, "w") as f:
            f.write(text)

    def visualize_ocr(self, image):
        result = self.reader.readtext(image)

        # Convert image to RGB if needed. Assume image is a numpy array.
        # If the image has 3 channels in BGR, convert to RGB.
        if image.ndim == 3 and image.shape[2] == 3:
            image_rgb = image[..., ::-1]
        else:
            image_rgb = image

        fig, ax = plt.subplots(1)
        ax.imshow(image_rgb)

        for bbox, text, prob in result:
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))
            # Calculate width and height for rectangle
            width = bottom_right[0] - top_left[0]
            height = bottom_right[1] - top_left[1]

            # Create a rectangle patch
            rect = patches.Rectangle(
                top_left,
                width,
                height,
                linewidth=2,
                edgecolor="green",
                facecolor="none",
            )
            ax.add_patch(rect)

            # Place the text above the rectangle
            ax.text(
                top_left[0],
                max(top_left[1] - 10, 0),
                text,
                fontsize=12,
                color="green",
                backgroundcolor="white",
                verticalalignment="bottom",
            )

        plt.axis("off")
        plt.show()

    def structured_text(self, image):
        result = self.reader.readtext(image, detail=1, paragraph=True)
        structured_data = []
        for bbox, text, prob in result:
            structured_data.append({"bbox": bbox, "text": text, "probability": prob})
        return structured_data

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
        result = self.reader.readtext(image)
        bboxes = []
        for bbox, text, prob in result:
            (top_left, top_right, bottom_right, bottom_left) = bbox
            x, y = map(int, top_left)
            w, h = map(
                int, (bottom_right[0] - top_left[0], bottom_right[1] - top_left[1])
            )
            bboxes.append({"text": text, "coordinates": (x, y, w, h)})
        return bboxes
    @staticmethod
    def get_all_configs():
        """Returns a list of EasyOCRInterface instances with permutations of recognition and detection models."""
        # recognition_models = ["latin_g1", "latin_g2"]
        # detection_models = ["craft", "dbnet18"]
        # configs = [
        #     EasyOCRInterface(
        #         lang=cfg.EASY_LANG,
        #         gpu=cfg.EASY_GPU,
        #         detect_network=detect,
        #         recog_network=recog,
        #     )
        #     for recog in recognition_models
        #     for detect in detection_models
               # ]
        configs = []
        configs.append(EasyOCRInterface(lang=cfg.EASY_LANG, gpu=cfg.EASY_GPU, recog_network="latin_g1", detect_network="craft"))
        # configs.append(EasyOCRInterface(lang=cfg.EASY_LANG, gpu=cfg.EASY_GPU, recog_network="latin_g1", detect_network="dbnet18"))
        configs.append(EasyOCRInterface(lang=cfg.EASY_LANG, gpu=cfg.EASY_GPU, recog_network="latin_g2", detect_network="craft"))
        # configs.append(EasyOCRInterface(lang=cfg.EASY_LANG, gpu=cfg.EASY_GPU, recog_network="latin_g2", detect_network="dbnet18"))
        return configs



        

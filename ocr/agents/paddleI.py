import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import List, Dict, Union, Tuple
import cv2
from ocr.agents.interface import OCRInterface
from PIL import Image
import importlib.util

# Check if paddleocr is available
PADDLE_AVAILABLE = importlib.util.find_spec("paddleocr") is not None
PADDLE_IMPORT_ERROR = None

try:
    if PADDLE_AVAILABLE:
        from paddleocr import PaddleOCR
except ImportError as e:
    PADDLE_AVAILABLE = False
    PADDLE_IMPORT_ERROR = str(e)

# Try to import config_mapper - use empty defaults if not available
try:
    from tools.config_mapper import cfg
    PADDLE_LANG = getattr(cfg, 'PADDLE_LANG', 'en')
    PADDLE_GPU = getattr(cfg, 'PADDLE_GPU', False)
except ImportError:
    # Default configuration if config mapper is not available
    class DummyConfig:
        PADDLE_LANG = 'en'
        PADDLE_GPU = False
    cfg = DummyConfig()


class PaddleOCRInterface(OCRInterface):
    def __init__(self, Paddle_ocr_version="PP-OCRv4", lang=cfg.PADDLE_LANG):
        if not PADDLE_AVAILABLE:
            error_msg = f"PaddleOCR is not available. Error: {PADDLE_IMPORT_ERROR or 'Module not found'}\n"
            error_msg += "Please install PaddleOCR and its dependencies with: pip install paddleocr paddlepaddle"
            raise ImportError(error_msg)
            
        self.paddle_ocr = PaddleOCR(
            use_angle_cls=True, 
            lang=lang,
            use_gpu=cfg.PADDLE_GPU,
            ocr_version=Paddle_ocr_version
        )  # Initialize PaddleOCR with language support
        self.name = Paddle_ocr_version

    def __str__(self):
        return f"{self.name}.json"
    def _load_image(self, image_path):
        return cv2.imread(image_path)

    def ocr_raw(self, image: Image.Image):
        # Convert PIL image to numpy array if needed
        if isinstance(image, Image.Image):
            image = np.array(image)
            
        result = self.paddle_ocr.ocr(image, cls=True)
        # Flatten the result if it's not empty
        if result and len(result) > 0 and result[0]:
            text = " ".join([line[1][0] for line in result[0]])
            return text
        return ""

    def visualize_ocr(self, image):
        result = self.paddle_ocr.ocr(image, cls=True)
        
        # Convert image to RGB if needed
        if image.ndim == 3 and image.shape[2] == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image

        fig, ax = plt.subplots(1)
        ax.imshow(image_rgb)

        # Check if result is not empty
        if result and len(result) > 0 and result[0]:
            for line in result[0]:
                bbox = line[0]
                text, prob = line[1]
                
                # Convert points to integers
                top_left = (int(bbox[0][0]), int(bbox[0][1]))
                bottom_right = (int(bbox[2][0]), int(bbox[2][1]))
                
                # Calculate width and height for rectangle
                width = bottom_right[0] - top_left[0]
                height = bottom_right[1] - top_left[1]

                # Create a rectangle patch
                rect = patches.Rectangle(
                    top_left,
                    width,
                    height,
                    linewidth=2,
                    edgecolor="blue",
                    facecolor="none",
                )
                ax.add_patch(rect)

                # Place the text above the rectangle
                ax.text(
                    top_left[0],
                    max(top_left[1] - 10, 0),
                    text,
                    fontsize=12,
                    color="blue",
                    backgroundcolor="white",
                    verticalalignment="bottom",
                )

        plt.axis("off")
        plt.show()

    def structured_text(self, image):
        result = self.paddle_ocr.ocr(image, cls=True)
        structured_data = []
        
        # Check if result is not empty
        if result and len(result) > 0 and result[0]:
            for line in result[0]:
                bbox = line[0]
                text, prob = line[1]
                structured_data.append({
                    "bbox": bbox,
                    "text": text,
                    "probability": prob
                })
                
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
        result = self.paddle_ocr.ocr(image, cls=True)
        bboxes = []
        
        # Check if result is not empty
        if result and len(result) > 0 and result[0]:
            for line in result[0]:
                bbox = line[0]
                text, _ = line[1]
                
                # Calculate x, y, width, height from the four corner points
                x = int(min(point[0] for point in bbox))
                y = int(min(point[1] for point in bbox))
                max_x = int(max(point[0] for point in bbox))
                max_y = int(max(point[1] for point in bbox))
                w = max_x - x
                h = max_y - y
                
                bboxes.append({"text": text, "coordinates": (x, y, w, h)})
                
        return bboxes
    @staticmethod
    def get_all_configs():
        """
            Returns all versions of PaddleOCR for cs lang. 
            1 PP-OCRv4,
            2 PP-OCRv3,
            3 PP-OCRv2,
            4 PP-OCR,
        """
        ocr_version = [
            "PP-OCRv4",
            "PP-OCRv3",
            "PP-OCRv2",
            "PP-OCR",
        ]

        return [PaddleOCRInterface(Paddle_ocr_version=version, lang="cs") for version in ocr_version]

            

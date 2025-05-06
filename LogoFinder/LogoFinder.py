from ultralytics import YOLO
from matplotlib import pyplot as plt
import logging
from PIL import Image
from pathlib import Path
from typing import Any, Dict, List, Union
import numpy as np
from tools.config_mapper import cfg


class LogoFinder:
    def __init__(self, model_name=cfg.YOLO_MODEL_PATH):
        self.model = YOLO(model_name)
        logging.getLogger("ultralytics").setLevel(logging.ERROR)

    def find_logo(
        self, image: Union[str, Path, int, Image.Image, list, tuple, np.ndarray]
    ) -> str:
        result = self.model(image)
        if result and result[0].boxes:
            # Assuming the class names are stored in result[0].names and boxes.cls contains class indices
            class_index = int(result[0].boxes.cls[0])
            return result[0].names[class_index]
        return ""

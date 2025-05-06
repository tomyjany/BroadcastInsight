from ocr.agents.interface import OCRInterface
from matplotlib.patches import Rectangle  # noqa: F401
from typing import List, Dict, Union, Tuple
import matplotlib.pyplot as plt
import pytesseract
import cv2
from tools.config_mapper import cfg


class TesseractI(OCRInterface):
    def __init__(self):

        self.custom_config = f"--oem {cfg.TESS_OEM} --psm {cfg.TESS_PSM} -l {cfg.TESS_LANG}"
        print("running tesseract with config: ", self.custom_config)

    def _load_image(self, image_path):

        return cv2.imread(image_path)

        """OPtimized for czech language"""

    def ocr_raw(self, image):
        # custom_config = r"--oem 3 --psm 6 -l ces"
        return pytesseract.image_to_string(image, config=self.custom_config)

    def save_text(self, text, file_path):
        with open(file_path, "w") as f:
            f.write(text)

    def visualize_ocr(self, image):
        data = pytesseract.image_to_data(
            image, config=r"--oem 3 --psm 6 -l ces", output_type=pytesseract.Output.DICT
        )
        n_boxes = len(data["level"])
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        for i in range(n_boxes):
            if int(data["conf"][i]) > 0:  # Filter out low-confidence results
                (x, y, w, h) = (
                    data["left"][i],
                    data["top"][i],
                    data["width"][i],
                    data["height"][i],
                )
                plt.gca().add_patch(
                    Rectangle(
                        (x, y), w, h, edgecolor="green", facecolor="none", linewidth=2
                    )
                )
                plt.text(
                    x,
                    y - 10,
                    data["text"][i],
                    fontsize=12,
                    color="green",
                    bbox=dict(facecolor="white", alpha=0.5),
                )
        plt.axis("off")
        plt.show()

    def get_ocr_as_bboxes(self, image):
        # return super().get_ocr_as_bboxes(image)
        # data = pytesseract.image_to_data(
        #     image,
        #     config=r"--oem 3 --psm 6 -l ces -c tessedit_char_blacklist=/\"$%\\\'()*+9;<=>X[]wx|£«»ĎňŤť—“„",
        #     output_type=pytesseract.Output.DICT,
        # )
        data = pytesseract.image_to_data(image, config=self.custom_config, output_type=pytesseract.Output.DICT)
        n_boxes = len(data["level"])
        results = []
        for i in range(n_boxes):
            if int(data["conf"][i]) > 0:
                (x, y, w, h) = (
                    data["left"][i],
                    data["top"][i],
                    data["width"][i],
                    data["height"][i],
                )
                results.append({"text": data["text"][i], "coordinates": (x, y, w, h)})
        return results

    def structured_text(self, image):
        """This will use HOCR or ALTO XML format, can provide labeled and structured text regions similar to your example."""
        custom_config = r"--oem 3 --psm 6 -l ces hocr"
        hocr = pytesseract.image_to_pdf_or_hocr(
            image, config=custom_config, extension="hocr"
        )
        return hocr.decode("utf-8")
    def get_all_tesseract_configs(self):
        # return [
        #     {
        #         "name":f"dataset_tesseract_oem_{i}_psm_{j}.json",
        #         "config":f"--oem {i} --psm {j} -l {cfg.TESS_LANG}"
        #     } for i in range(4) for j in range(14)

        # ] 

        oem0 =  [
            {
                "name" : f"dataset_tesseract_oem_0_psm_{j}.json",
                "config" :f"--oem 0 --psm {j} -l cesLEGACY"
            } for j in range(14)

        ]
        oem1 = [
            {
                "name" : f"dataset_tesseract_oem_1_psm_{j}.json",
                "config" :f"--oem 1 --psm {j} -l ces"
            } for j in range(14)

        ]

        oem2 = [
            {
                "name" : f"dataset_tesseract_oem_2_psm_{j}.json",
                "config" :f"--oem 2 --psm {j} -l cesLEGACY"
            } for j in range(14)

        ]
        return oem0 + oem1 + oem2







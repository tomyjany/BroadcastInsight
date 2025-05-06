from LogoFinder.LogoFinder import LogoFinder
from ocr.agents.interface import get_ocr_agent
from PeopleFinder.finder import PeopleFinder
from sceneDetector.agents.interface import get_scene_detector
from tools.video_frame_getter import VideoFrameGetter
import time
import logging
from tools.config_mapper import cfg

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


class Miner:
    def __init__(
        self,
        ocr_method="tesseract",
        scene_detect_method="scenedetect",
        people_database_path=cfg.PEOPLE_DB_PATH,
        yolo_model_path=cfg.YOLO_MODEL_PATH,
    ):
        self.scene_detector = get_scene_detector(scene_detect_method)
        logging.info("Scene detector intialized")
        self.ocr = get_ocr_agent(ocr_method)
        logging.info("OCR intialized")
        self.people_finder = PeopleFinder(database_path=people_database_path)
        logging.info("PeopleFinder initialized")
        self.logo_finder = LogoFinder(model_name=yolo_model_path)
        logging.info("LogoFinder intialized")

        pass

    def __call__(self, path_to_video):
        # Detecting scenes
        logging.info("Detecting scenes...")
        cuts = self.scene_detector.detect_shot_with_bondaries(path_to_video)
        frame_getter = VideoFrameGetter(path_to_video, cuts)
        found_people = []
        logos = []

        result = []

        total_time_ocr = 0
        total_time_logo = 0
        total_time_people = 0

        ids = 0

        logging.info("Extracting: OCR, People, Logos...")
        for frame, scene_metadata in frame_getter:
            # Detecting logos
            logo_start = time.time()
            logo = self.logo_finder.find_logo(frame)
            total_time_logo += time.time() - logo_start
            ocr_text_start = time.time()
            ocr_text = self.ocr.ocr_raw(frame)
            total_time_ocr += time.time() - ocr_text_start
            logos.append(logo)
            total_time_people_start = time.time()
            people = self.people_finder.find_people(frame)
            total_time_people += time.time() - total_time_people_start
            found_people.extend(people)
            scene = {
                "scene_info": {
                    "id": ids,
                    "frame_number": int(
                        (scene_metadata["start_frame"] + scene_metadata["end_frame"])
                        / 2
                    ),
                    "begin_time": scene_metadata["start_time"],
                    "end_time": scene_metadata["end_time"],
                },
                "ocr_text": ocr_text,
                "detected_people": people,
                "tv_logo": logo,
            }
            result.append(scene)
            ids += 1

        logging.info(f"Found logos: {logos}")
        logging.info(f"Found people:{found_people}")
        logging.info(f"Total time spent on OCR:{total_time_ocr}")
        logging.info(f"Total time spent on logo detection:{total_time_logo}")
        logging.info(f"Total time spent on people detection:{total_time_people}")
        # writes result to file
        return result

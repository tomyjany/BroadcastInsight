import warnings
import os
from Miner.Miner import Miner
import tempfile
from tools.config_mapper import repeat

import logging
from typing import List, Dict, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)


async def run_inference(
    scene_detect_method: str,
    ocr_method: str,
    people_database_path: str,
    yolo_model_path,
    file,
) -> Tuple[List[Dict], str]:
    try:
        repeat()
        if file is not None:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file_path = os.path.join(temp_dir, file.filename)

                # Save the uploaded file to the temporary directory
                with open(temp_file_path, "wb") as temp_file:
                    content = await file.read()
                    temp_file.write(content)
                    logging.info(f"File saved to {temp_file_path}")

                agent = Miner(
                    scene_detect_method=scene_detect_method,
                    ocr_method=ocr_method,
                    people_database_path=people_database_path,
                    yolo_model_path=yolo_model_path,
                )
                results = agent(temp_file_path)

                return results

    except Exception as e:
        raise ValueError(f"Inference error: {str(e)}")

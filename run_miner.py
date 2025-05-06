import argparse
import requests
import json
from tools.config_mapper import cfg


def main():
    parser = argparse.ArgumentParser(description="Run News Video Miner via API")
    parser.add_argument(
        "--video",
        type=str,
        default="testvideo.mp4",
        help="Path to the video file",
    )
    parser.add_argument(
        "--ocr_method", type=str, default="tesseract", help="OCR method to use"
    )
    parser.add_argument(
        "--scene_detect_method",
        type=str,
        default="transnet",
        help="Scene detection method to use",
    )
    parser.add_argument(
        "--people_database_path",
        type=str,
        default=cfg.PEOPLE_DB_PATH,
        help="Path to the people database",
    )
    parser.add_argument(
        "--yolo_model_path",
        type=str,
        default=cfg.YOLO_MODEL_PATH,
        help="Path to the YOLO model",
    )
    parser.add_argument(
        "--output", type=str, default="output.json", help="Path to save the output JSON"
    )
    parser.add_argument(
        "--api_url",
        type=str,
        default="http://localhost:8000/api/v1/NewsVideoMiner/inference",
        help="API endpoint URL",
    )
    args = parser.parse_args()

    # Prepare the request payload
    files = {"file": open(args.video, "rb")}
    data = {
        "ocr_method": args.ocr_method,
        "scene_detect_method": args.scene_detect_method,
        "people_database_path": args.people_database_path,
        "yolo_model_path": args.yolo_model_path,
    }

    # Call the API
    try:
        response = requests.post(args.api_url, files=files, data=data)
        response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx
        results = response.json()

        # Save results to output file
        with open(args.output, "w") as f:
            json.dump(results, f, indent=4)
        print(f"Results saved to {args.output}")
    except requests.exceptions.RequestException as e:
        print(f"Error during API call: {e}")


if __name__ == "__main__":
    main()

from Miner.Miner import Miner
import time
import gc
import json


def test_Miner():
    # fastest possible
    miner = Miner()  # init with default values
    time_start = time.time()
    result = miner("video.mp4")
    # save json
    with open("video.json", "w") as f:
        json.dump(result, f, indent=4)
    total_time1 = time.time() - time_start
    print("TOTAL TIME ", total_time1)


def test_Miner_ffprobe():
    # fastest possible
    miner = Miner(scene_detect_method="ffprobe")  # init with default values
    time_start = time.time()
    result = miner("video.mp4")
    # save json
    with open("video.json", "w") as f:
        json.dump(result, f, indent=4)
    total_time1 = time.time() - time_start
    print("TOTAL TIME ", total_time1)


def test_Miner_autoshot():
    # fastest possible
    miner = Miner(scene_detect_method="autoshot")  # init with default values
    time_start = time.time()
    result = miner("video.mp4")
    # save json
    with open("video.json", "w") as f:
        json.dump(result, f, indent=4)
    total_time1 = time.time() - time_start
    print("TOTAL TIME ", total_time1)


def test_Miner():
    # fastest possible
    miner = Miner(scene_detect_method="ffprobe")  # init with default values
    time_start = time.time()
    result = miner("video.mp4")
    # save json
    with open("video.json", "w") as f:
        json.dump(result, f, indent=4)
    total_time1 = time.time() - time_start
    print("TOTAL TIME ", total_time1)


def test_Miner_transnet_easyocr():
    # harder models, better accuracy
    miner = Miner(
        ocr_method="easyocr", scene_detect_method="transnet"
    )  # , num_workers=20) # init with default values
    time_start = time.time()
    result = miner("video.mp4")
    # save json
    with open(
        "video.json", "w"
    ) as f:
        json.dump(result, f, indent=4)
    total_time1 = time.time() - time_start
    print("TOTAL TIME ", total_time1)

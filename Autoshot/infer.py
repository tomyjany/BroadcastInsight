import os
import numpy as np
import torch
from tools.config_mapper import cfg
from utils import (
    get_frames,
    get_batches,
)  # Import get_frames and get_batches from utils

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def get_shot_boundary_frames(path_to_video):
    # Import the TransNetV2Supernet model
    from supernet_flattransf_3_8_8_8_13_12_0_16_60 import TransNetV2Supernet

    # Initialize the model
    model = TransNetV2Supernet().eval()

    # Check device
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Load pretrained weights
    # pretrained_path = "Autoshot/ckpt_0_200_0.pth"  # Adjust the path to your weights
    pretrained_path = cfg.AUTOSHOT_MODEL_PATH  # Adjust the path to your weights
    if os.path.exists(pretrained_path):
        print("Loading pretrained weights from %s" % pretrained_path)
        model_dict = model.state_dict()
        pretrained_dict = torch.load(pretrained_path, map_location=device)
        pretrained_dict = {
            k: v for k, v in pretrained_dict["net"].items() if k in model_dict
        }
        model_dict.update(pretrained_dict)
        model.load_state_dict(model_dict)
    else:
        raise Exception("Error: Cannot find pretrained model at %s" % pretrained_path)

    if device == "cuda":
        model = model.to(device)
    model.eval()

    # Define predict function
    def predict(batch):
        batch = torch.from_numpy(batch.transpose((3, 0, 1, 2))[np.newaxis, ...]) * 1.0
        batch = batch.to(device)
        with torch.no_grad():
            one_hot = model(batch)
            if isinstance(one_hot, tuple):
                # print(len(one_hot))
                # input(
                one_hot = one_hot[0]
                # print(one_hot)
            return torch.sigmoid(one_hot[0])

    # Get frames from video
    frames = get_frames(path_to_video)

    # Initialize list to store predictions
    predictions = []

    # Process frames in batches using the get_batches function from utils
    logging.info("Processing frames in batches")
    n_frames = len(frames)
    batch_size = 100  # This is the batch size used in get_batches
    total_batches = (
        n_frames + 50 - 1
    ) // 50  # Calculate total batches based on step size (50)
    ite = 0
    for batch in get_batches(frames):
        ite += 1
        if ite % 10 == 0:
            logging.info(
                f"Processed {ite}/{total_batches} batches {ite*100/total_batches}%"
            )
        one_hot = predict(batch)
        one_hot = one_hot.detach().cpu().numpy()
        # We take the middle 50 frames (from index 25 to 75)
        predictions.append(one_hot[25:75])

    # Concatenate predictions and ensure the length matches number of frames
    predictions = np.concatenate(predictions, axis=0)[: len(frames)]

    # Determine shot boundaries based on threshold
    # Use the threshold from your evaluation (e.g., 0.296)
    # threshold = 0.296
    threshold = cfg.AUTOSHOT_THRESHOLD
    shot_boundaries = (predictions > threshold).astype(np.uint8)

    # Get the indices of frames that are shot boundaries
    boundary_frames = np.where(shot_boundaries == 1)[0]

    # Return the list of frame indices
    return boundary_frames.tolist()



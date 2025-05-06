from tools.dtw_wer import wer
import json
from tabulate import tabulate

import os, pathlib, PyQt5
_qt = pathlib.Path(PyQt5.__file__).parent / 'Qt5'
os.environ['LD_LIBRARY_PATH']       = str(_qt / 'lib') + ':' + os.environ.get('LD_LIBRARY_PATH', '')
os.environ['QT_PLUGIN_PATH']        = str(_qt / 'plugins')
os.environ.pop('QT_QPA_PLATFORM_PLUGIN_PATH', None)   # throw away stale overrides

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import numpy as np
import os




# def visualize_ocr_results(results_dir, data_path, json_file_filter="DB"):
#     """
#     Visualize OCR results by drawing bounding boxes and detected text on images.
#     
#     Args:
#         results_dir: Path to the directory containing OCR results.
#         data_path: Path to the directory containing the original images.
#         json_file_filter: Filter for specific annotations in JSON files.
#     """
#     import os
#     import json
#     from matplotlib import pyplot as plt
#     from PIL import Image, ImageDraw, ImageFont
#
#     # Prompt user to select an agent
#     agents = [agent for agent in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, agent))]
#     print("Available agents:")
#     for idx, agent in enumerate(agents, start=1):
#         print(f"{idx}. {agent}")
#     agent_choice = int(input("Select an agent by number: ")) - 1
#     agent_name = agents[agent_choice]
#
#     # Prompt user to select a JSON file
#     json_dir = os.path.join(results_dir, agent_name, "dataset_full")
#     json_files = [file for file in os.listdir(json_dir) if file.endswith(".json")]
#     print("\nAvailable JSON files:")
#     for idx, json_file in enumerate(json_files, start=1):
#         print(f"{idx}. {json_file}")
#     json_choice = int(input("Select a JSON file by number: ")) - 1
#     json_file = json_files[json_choice]
#
#     # Load and visualize the selected JSON file
#     with open(os.path.join(json_dir, json_file), "r", encoding="utf-8") as f:
#         results = json.load(f)
#
#     print(f"\nVisualizing results from JSON: {json_file}")
#     for record in results:
#         image_file = record["file"]
#         if json_file_filter not in image_file:
#             continue
#
#         image_path = os.path.join(data_path, image_file)
#         if not os.path.exists(image_path):
#             print(f"Image not found: {image_path}")
#             continue
#
#         image = Image.open(image_path).convert("RGB")
#         draw = ImageDraw.Draw(image)
#
#         # Load a font with better Unicode support
#         try:
#             font = ImageFont.truetype("DejaVuSans-Bold.ttf", size=15)
#         except IOError:
#             font = ImageFont.load_default()
#
#         # Draw bounding boxes first
#         for ocr_result in record["ocr_result"]:
#             if "coordinates" in ocr_result:
#                 x, y, w, h = ocr_result["coordinates"]
#                 draw.rectangle([x, y, x + w, y + h], outline="green", width=3)
#
#         # Track used vertical space to avoid text overlap
#         used_vertical_space = set()
#
#         # Draw text over bounding boxes
#         for ocr_result in record["ocr_result"]:
#             if "coordinates" in ocr_result and "text" in ocr_result:
#                 x, y, w, h = ocr_result["coordinates"]
#                 text = ocr_result["text"]
#
#                 # Print OCR result to the command line
#                 print(f"File: {image_file}, Text: {text}, Coordinates: {x, y, w, h}")
#
#                 # Calculate text size
#                 text_bbox = font.getbbox(text)
#                 text_width = text_bbox[2] - text_bbox[0]
#                 text_height = text_bbox[3] - text_bbox[1]
#
#                 # Adjust text position to avoid overlap and ensure visibility
#                 text_x = max(0, x)
#                 text_y = max(0, y - text_height - 5)
#                 while text_y in used_vertical_space:
#                     text_y += text_height + 5
#                 used_vertical_space.add(text_y)
#
#                 # Ensure text is visible even if it extends outside the image
#                 if text_x + text_width > image.width:
#                     text_x = image.width - text_width - 5
#                 if text_y + text_height > image.height:
#                     text_y = image.height - text_height - 5
#
#                 # Add a semi-transparent background for text
#                 draw.rectangle(
#                     [text_x, text_y, text_x + text_width + 5, text_y + text_height + 5],
#                     fill="black",
#                     outline=None,
#                 )
#
#                 # Put text
#                 draw.text((text_x + 2, text_y + 2), text, fill="white", font=font)
#
#         # Display the image with JSON file info
#         plt.imshow(image)
#         plt.title(f"Visualization for {image_file} (JSON: {json_file})")
#         plt.axis("off")
#         plt.show()


def visualize_ocr_results(results_dir, data_path,json_file_filter="DB"): #json_file_filter="DB160330-Scene-017-02.jpg"):
    """
    Visualize OCR results by drawing bounding boxes and detected text on images.
    
    Args:
        results_dir: Path to the directory containing OCR results.
        data_path: Path to the directory containing the original images.
        json_file_filter: Filter for specific annotations in JSON files.
    """
    import os
    import json
    from matplotlib import pyplot as plt
    from PIL import Image, ImageDraw, ImageFont

    # Prompt user to select an agent
    agents = [agent for agent in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, agent))]
    print("Available agents:")
    for idx, agent in enumerate(agents, start=1):
        print(f"{idx}. {agent}")
    agent_choice = int(input("Select an agent by number: ")) - 1
    agent_name = agents[agent_choice]

    # Prompt user to select a JSON file
    json_dir = os.path.join(results_dir, agent_name, "dataset_full")
    json_files = [file for file in os.listdir(json_dir) if file.endswith(".json")]
    print("\nAvailable JSON files:")
    for idx, json_file in enumerate(json_files, start=1):
        print(f"{idx}. {json_file}")
    json_choice = int(input("Select a JSON file by number: ")) - 1
    json_file = json_files[json_choice]

    # Load and visualize the selected JSON file
    with open(os.path.join(json_dir, json_file), "r", encoding="utf-8") as f:
        results = json.load(f)

    print(f"\nVisualizing results from JSON: {json_file}")
    for record in results:
        image_file = record["file"]
        if json_file_filter not in image_file:
            continue

        image_path = os.path.join(data_path, image_file)
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            continue

        image = Image.open(image_path).convert("RGB")

        # Load a font with better Unicode support
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", size=12)
        except IOError:
            font = ImageFont.load_default()

        # Plot annotations only
        annotation_image = image.copy()
        annotation_draw = ImageDraw.Draw(annotation_image)
        used_vertical_space = set()
        for annotation in record.get("annotation", []):
            if "coordinates" in annotation and "text" in annotation:
                x, y, w, h = annotation["coordinates"]
                text = annotation["text"]

                # Draw bounding box
                annotation_draw.rectangle([x, y, x + w, y + h], outline="green", width=3)
                # combined_draw.rectangle([x, y, x + w, y + h], outline="red", width=3)

                # Calculate text size and adjust position
                text_bbox = font.getbbox(text)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                text_x = max(0, x)
                text_y = max(0, y - text_height - 5)
                while text_y in used_vertical_space:
                    text_y += text_height + 5
                used_vertical_space.add(text_y)

                # Ensure text is visible even if it extends outside the image
                if text_x + text_width > annotation_image.width:
                    text_x = annotation_image.width - text_width - 5
                if text_y + text_height > annotation_image.height:
                    text_y = annotation_image.height - text_height - 5

                # Add a semi-transparent background for text
                annotation_draw.rectangle(
                    [text_x, text_y, text_x + text_width + 5, text_y + text_height + 5],
                    fill="black",
                    outline=None,
                )

                # Put text
                annotation_draw.text((text_x + 2, text_y + 2), text, fill="white", font=font)
        plt.imshow(annotation_image)
        plt.title(f"Annotations for {image_file}")
        plt.axis("off")
        plt.show()

        # Plot OCR results only
        result_image = image.copy()
        result_draw = ImageDraw.Draw(result_image)
        used_vertical_space = set()
        for ocr_result in record["ocr_result"]:
            if "coordinates" in ocr_result and "text" in ocr_result:
                x, y, w, h = ocr_result["coordinates"]
                text = ocr_result["text"]

                # Print OCR result to the command line
                print(f"File: {image_file}, Text: {text}, Coordinates: {x, y, w, h}")

                # Draw bounding box
                try: 
                    result_draw.rectangle([x, y, x + w, y + h], outline="red", width=3)
                except Exception as e:
                    print("Error during drawing boudnary box", str(e))


                # Calculate text size and adjust position
                text_bbox = font.getbbox(text)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                text_x = max(0, x)
                text_y = max(0, y - text_height - 5)
                while text_y in used_vertical_space:
                    text_y += text_height + 5
                used_vertical_space.add(text_y)

                # Ensure text is visible even if it extends outside the image
                if text_x + text_width > result_image.width:
                    text_x = result_image.width - text_width - 5
                if text_y + text_height > result_image.height:
                    text_y = result_image.height - text_height - 5

                # Add a semi-transparent background for text
                # result_draw.rectangle(
                #     [text_x, text_y, text_x + text_width + 5, text_y + text_height + 5],
                #     fill="black",
                #     outline=None,
                # )

                # Put text
                # result_draw.text((text_x + 2, text_y + 2), text, fill="white", font=font)
        plt.imshow(result_image)
        plt.title(f"OCR Results for {image_file}")
        plt.axis("off")
        plt.show()

        # Plot combined annotations and OCR results
        combined_image = image.copy()
        combined_draw = ImageDraw.Draw(combined_image)
        for annotation in record.get("annotation", []):
            if "coordinates" in annotation:
                x, y, w, h = annotation["coordinates"]
                combined_draw.rectangle([x, y, x + w, y + h], outline="green", width=3)
        for ocr_result in record["ocr_result"]:
            if "coordinates" in ocr_result and "text" in ocr_result:
                x, y, w, h = ocr_result["coordinates"]
                text = ocr_result["text"]

                # Draw bounding box
                combined_draw.rectangle([x, y, x + w, y + h], outline="red", width=3)

                # Calculate text size and adjust position
                text_bbox = font.getbbox(text)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                text_x = max(0, x)
                text_y = max(0, y - text_height - 5)
                # while text_y in used_vertical_space:
                #     text_y += text_height + 5
                used_vertical_space.add(text_y)

                if text_x + text_width > annotation_image.width:
                    text_x = annotation_image.width - text_width - 5
                if text_y + text_height > annotation_image.height:
                    text_y = annotation_image.height - text_height - 5


                # Add a semi-transparent background for text
                # combined_draw.rectangle(
                #     [text_x, text_y, text_x + text_width + 5, text_y + text_height + 5],
                #     fill="black",
                #     outline=None,
                # )
                #
                # # Put text
                # combined_draw.text((text_x + 2, text_y + 2), text, fill="white", font=font)

                combined_draw.rectangle(
                    [text_x, text_y, text_x + text_width + 5, text_y + text_height + 5],
                    fill="black",
                    outline=None,
                )

                # Put text
                combined_draw.text((text_x + 2, text_y + 2), text, fill="white", font=font)
        plt.imshow(combined_image)
        plt.title(f"Annotations and OCR Results for {image_file}")
        plt.axis("off")
        plt.show()


def evaluate_ocr_dtw_wer_only(json_file, ignore_special_characters=False):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_S = 0
    total_D = 0
    total_I = 0
    total_N = 0

    for record in data:
        text = list(record["text"])
        ocr_text = list(record["ocr_text"])
        if ignore_special_characters:
            text = [char for char in text if char not in special_characters]
            ocr_text = [char for char in ocr_text if char not in special_characters]

        S, D, I, N = wer(text, ocr_text)
        total_S += S
        total_D += D
        total_I += I
        total_N += N

    CER = ((total_S + total_D + total_I) / total_N) * 100 if total_N > 0 else 0
    CAcc = 100 - CER

    print(f"No. of characters in the reference: {total_N}")
    print(f"No. of substitutions: {total_S}")
    print(f"No. of deletions: {total_D}")
    print(f"No. of insertions: {total_I}")
    print(f"Character Error Rate: {CER:.1f}%")
    print(f"Character Accuracy: {CAcc:.1f}%")
    return {
        "total_N":total_N,
        "total_S":total_S,
        "total_D":total_D,
        "total_I":total_I,
        "CER":CER,
        "CAcc":CAcc,
    }


def evaluate_mpocr_text_only(
    mpocr_json_file, ocr_results_file, ignore_special_characters=False
):
    """
    Evaluate OCR results using DTW-based WER on MPOCR dataset format.
    Only compares text content, completely ignoring bounding boxes.

    Args:
        mpocr_json_file: Path to the ground truth annotations in MPOCR format
        ocr_results_file: Path to OCR results in JSON format
        ignore_special_characters: Whether to ignore special characters in the comparison
    """
    # Load ground truth annotations
    with open(mpocr_json_file, "r", encoding="utf-8") as f:
        mpocr_data = json.load(f)

    # Load OCR results
    with open(ocr_results_file, "r", encoding="utf-8") as f:
        ocr_results = json.load(f)

    total_S = 0
    total_D = 0
    total_I = 0
    total_N = 0

    # Create a mapping from image_id to annotations
    img_to_anns = {}

    # Build img_to_anns mapping
    if "imgToAnns" in mpocr_data:
        img_to_anns = mpocr_data["imgToAnns"]
    elif "anns" in mpocr_data:
        for ann_id, ann in mpocr_data["anns"].items():
            image_id = ann["image_id"]
            if image_id not in img_to_anns:
                img_to_anns[image_id] = []
            img_to_anns[image_id].append(ann_id)

    # Process each file in the OCR results
    for item in ocr_results:
        if "file" not in item or not item["ocr_result"]:
            continue

        file_name = item["file"]
        image_id = file_name.split(".")[0]  # Remove file extension

        # Skip if this image doesn't have annotations
        if image_id not in img_to_anns:
            continue

        # Collect all text from this image's annotations
        all_gt_text = ""
        for ann_id in img_to_anns[image_id]:
            ann = mpocr_data["anns"][ann_id]
            all_gt_text += ann["utf8_string"] + " "

        # Collect all text from OCR results
        all_ocr_text = ""
        for ocr_box in item["ocr_result"]:
            all_ocr_text += ocr_box["text"] + " "

        # Filter special characters if requested
        if ignore_special_characters:
            all_gt_text = "".join(
                [char for char in all_gt_text if char not in special_characters]
            )
            all_ocr_text = "".join(
                [char for char in all_ocr_text if char not in special_characters]
            )

        # Skip empty text comparisons
        if not all_gt_text or not all_ocr_text:
            continue

        # Convert to character lists for WER calculation - each character is a separate item
        # gt_chars = [c for c in all_gt_text]
        # ocr_chars = [c for c in all_ocr_text]

        # Calculate WER metrics
        S, D, I, N = wer(all_gt_text.split(), all_ocr_text.split())
        print(all_gt_text)
        print("*" * 10)
        print(all_ocr_text)
        print("*" * 10)
        print("S: ", S, " D ", D, " I ", I, " N ", N)
        input()

        total_S += S
        total_D += D
        total_I += I
        total_N += N

    # Calculate final metrics
    CER = ((total_S + total_D + total_I) / total_N) * 100 if total_N > 0 else 0
    # Cap CER at 100%
    CER = min(CER, 100.0)
    CAcc = 100 - CER

    print(f"No. of characters in the reference: {total_N}")
    print(f"No. of substitutions: {total_S}")
    print(f"No. of deletions: {total_D}")
    print(f"No. of insertions: {total_I}")
    print(f"Character Error Rate: {CER:.1f}%")
    print(f"Character Accuracy: {CAcc:.1f}%")

    return {
        "CER": CER,
        "CAcc": CAcc,
        "total_S": total_S,
        "total_D": total_D,
        "total_I": total_I,
        "total_N": total_N,
    }


def get_iou_score(bbox1, bbox2):
    x1, y1, w1, h1 = bbox1
    x2, y2, w2, h2 = bbox2

    xA = max(x1, x2)
    yA = max(y1, y2)
    xB = min(x1 + w1, x2 + w2)
    yB = min(y1 + h1, y2 + h2)

    interArea = max(0, xB - xA) * max(0, yB - yA)

    box1Area = w1 * h1
    box2Area = w2 * h2

    iou = interArea / float(box1Area + box2Area - interArea)
    return iou


# def assign_bboxes(annotation, ocr_bboxes):
#     assigned_bboxes = []
#     print("*" * 10)
#
#     # Add an index to each OCR bounding box
#     indexed_ocr_bboxes = [{"index": idx, **ocr_bbox} for idx, ocr_bbox in enumerate(ocr_bboxes)]
#
#     for bbox in annotation:
#         sum_iou = 0
#         boxxes_that_intersect = []
#         for ocr_bbox in indexed_ocr_bboxes:
#             iou = get_iou_score(ocr_bbox["coordinates"], bbox["coordinates"])
#             if iou > 0.1:
#                 sum_iou += iou
#                 print(f"IOU: {iou}, text: {ocr_bbox['text']}")
#                 boxxes_that_intersect.append(ocr_bbox)
#         print("Sum IOU", sum_iou)
#         result = {
#             "tag": bbox["tag"],
#             "text": bbox["text"],
#             "assigned_bboxes": boxxes_that_intersect,
#             "sum_iou": sum_iou,  # type: ignore
#         }
#         assigned_bboxes.append(result)
#
#     print("*" * 10)
#     return assigned_bboxes

def assign_bboxes(annotation, ocr_bboxes):
    assigned_bboxes = []
    print("*" * 10)

    # Add an index to each OCR bounding box
    indexed_ocr_bboxes = [{"index": idx, **ocr_bbox} for idx, ocr_bbox in enumerate(ocr_bboxes)]

    for bbox in annotation:
        sum_iou = 0
        boxxes_that_intersect = []
        for ocr_bbox in indexed_ocr_bboxes:
            iou = get_iou_score(ocr_bbox["coordinates"], bbox["coordinates"])
            if iou > 0.1:
                sum_iou += iou
                print(f"IOU: {iou}, text: {ocr_bbox['text']}")
                boxxes_that_intersect.append(ocr_bbox)
        print("Sum IOU", sum_iou)
        result = {
            "tag": bbox["tag"],
            "text": bbox["text"],  # Keep the original "text" key for compatibility
            "bbox_data": bbox,  # Add a new key to store the entire bbox object
            "assigned_bboxes": boxxes_that_intersect,
            "sum_iou": sum_iou,  # type: ignore
        }
        assigned_bboxes.append(result)

    print("*" * 10)
    return assigned_bboxes


# def run_on_json(json_path, debug=False, ignore_special_characters=False):
#     with open(json_path, "r", encoding="utf-8") as f:
#         data = json.load(f)
#     total_S = 0
#     total_D = 0
#     total_I = 0
#     total_N = 0
#     detection_accuracy = 0
#     total_boxes = 0
#     print("data size",len(data))
#     for record in data:
#         try:
#             assigned_boxes = assign_bboxes(record["annotation"], record["ocr_result"])
#         except TypeError as e:
#             continue
#         for assigned_box in assigned_boxes:
#             total_boxes += 1
#             if assigned_box["sum_iou"] > IOU_THRESHOLD:
#                 detection_accuracy += 1
#             joined_text = " ".join(
#                 [box["text"] for box in assigned_box["assigned_bboxes"]]
#             )
#             if ignore_special_characters:
#                 assigned_box_text = "".join(
#                     [
#                         char
#                         for char in assigned_box["text"]
#                         if char not in special_characters
#                     ]
#                 )
#                 joined_text = "".join(
#                     [char for char in joined_text if char not in special_characters]
#                 )
#             else:
#                 assigned_box_text = assigned_box["text"]
#             S, D, I, N = wer(assigned_box_text, joined_text)
#             total_S += S
#             total_D += D
#             total_I += I
#             total_N += N
#
#             if debug:
#                 print(joined_text)
#                 print(assigned_box["sum_iou"])
#                 print(assigned_box["text"])
#                 print(tabulate(assigned_box["assigned_bboxes"], headers="keys"))
#                 table_data = [
#                     [joined_text, assigned_box["sum_iou"], assigned_box["text"]]
#                 ]
#                 headers = ["Joined Text", "Sum IOU", "Original Text"]
#
#                 # Print the table
#                 print(tabulate(table_data, headers=headers, tablefmt="grid"))
#                 input()
#
#
#         # print(assigned_boxes)
#         # input()
#     CER = ((total_S + total_D + total_I) / total_N) * 100 if total_N > 0 else 0
#     CAcc = 100 - CER
#
#     print(f"No. of characters in the reference: {total_N}")
#     print(f"No. of substitutions: {total_S}")
#     print(f"No. of deletions: {total_D}")
#     print(f"No. of insertions: {total_I}")
#     print(f"Character Error Rate: {CER:.1f}%")
#     print(f"Character Accuracy: {CAcc:.1f}%")
#     return{
#         "No. of characters in the reference:": total_N,
#         "No. of substitutions:": total_S,
#         "No. of deletions:": total_D,
#         "No. of insertions:": total_I,
#         "Character Error Rate:": CER,
#         "Character Accuracy:": CAcc,
#     }


    # print("detection accuracy: ", detection_accuracy / total_boxes * 100)


def run_on_json(json_path, debug=False, ignore_special_characters=False):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    total_S = 0
    total_D = 0
    total_I = 0
    total_N = 0
    detection_accuracy = 0
    total_boxes = 0
    print("data size", len(data))
    
    for record in data:
        try:
            assigned_boxes = assign_bboxes(record["annotation"], record["ocr_result"])
        except TypeError as e:
            print(f"Error in assigning boxes: {e}")
            continue

        # Track annotations that are linked
        linked_annotations = set()

        # Group OCR text by annotation tag
        annotation_to_ocr_text = {}
        for assigned_box in assigned_boxes:
            total_boxes += 1
            if assigned_box["sum_iou"] > IOU_THRESHOLD:
                detection_accuracy += 1

            joined_text = " ".join(
                [box["text"] for box in assigned_box["assigned_bboxes"]]
            )
            if ignore_special_characters:
                joined_text = "".join(
                    [char for char in joined_text if char not in special_characters]
                )

            tag = assigned_box["bbox_data"]["tag"]
            if tag not in annotation_to_ocr_text:
                annotation_to_ocr_text[tag] = joined_text
            else:
                annotation_to_ocr_text[tag] += " " + joined_text

            # Mark annotation as linked
            linked_annotations.add(tag)

        # Evaluate each annotation
        for annotation in record["annotation"]:
            tag = annotation["tag"]
            annotation_text = annotation["text"]
            if ignore_special_characters:
                annotation_text = "".join(
                    [char for char in annotation_text if char not in special_characters]
                )

            if tag in annotation_to_ocr_text:
                # Linked annotation
                ocr_text = annotation_to_ocr_text[tag]
                S, D, I, N = wer(annotation_text, ocr_text)
                total_S += S
                total_D += D
                total_I += I
                total_N += N
            else:
                # Unlinked annotation
                print(f"Unlinked annotation: {annotation}")
                total_D += len(annotation_text)  # Count as deletions
                total_N += len(annotation_text)  # Add to total reference length

    CER = ((total_S + total_D + total_I) / total_N) * 100 if total_N > 0 else 0
    CAcc = 100 - CER

    print(f"No. of characters in the reference: {total_N}")
    print(f"No. of substitutions: {total_S}")
    print(f"No. of deletions: {total_D}")
    print(f"No. of insertions: {total_I}")
    print(f"Character Error Rate: {CER:.1f}%")
    print(f"Character Accuracy: {CAcc:.1f}%")
    return {
        "No. of characters in the reference:": total_N,
        "No. of substitutions:": total_S,
        "No. of deletions:": total_D,
        "No. of insertions:": total_I,
        "Character Error Rate:": CER,
        "Character Accuracy:": CAcc,
    }
def get_known_characters_from_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    known_characters = set()
    for record in data:
        for annotation in record["annotation"]:
            for char in annotation["text"]:
                known_characters.add(char)
    return known_characters


def test_assign_boxes():
    """Test the assign_bboxes function"""
    annotation = [
        {"tag": "1", "text": "hello", "coordinates": (10, 10, 100, 50)},
        {"tag": "2", "text": "world", "coordinates": (150, 150, 100, 50)},
    ]
    ocr_bboxes = [
        {"text": "hello", "coordinates": (10, 10, 100, 50)},
        {"text": "world", "coordinates": (150, 150, 100, 50)},
    ]
    assigned_bboxes = assign_bboxes(annotation, ocr_bboxes)
    print(assigned_bboxes)


def filter_out_apriori_bad_bboxes_from_json(json_path):
    """This method will take into account known alpabet and will autmatically remove those boundary boxes that containt only letters outside this alphabet"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    known_characters = get_known_characters_from_json(json_path)
    for record in data:
        record["ocr_result"] = [
            ocr_result
            for ocr_result in record["ocr_result"]
            if any(char in known_characters for char in ocr_result["text"])
        ]
    with open("filtered_original.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_unknown_characters_found_by_ocr(json_path, known_characters):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    unknown_characters = set()
    for record in data:
        for ocr_result in record["ocr_result"]:
            for char in ocr_result["text"]:
                if char not in known_characters:
                    unknown_characters.add(char)
    return unknown_characters


special_characters = list(
    {
        "£",
        ">",
        "|",
        "=",
        "%",
        "“",
        "*",
        "]",
        "x",
        "[",
        "ť",
        "9",
        "Ť",
        "Ď",
        "ň",
        "»",
        '"',
        "w",
        "$",
        "+",
        "—",
        ")",
        "X",
        "«",
        "'",
        "(",
        ";",
        "„",
        "<",
        "#",
        "@",
        "/",
        "|",
        "\\",
        "!",
        "©",
        ",",
        ".",
    }
)
# set of known characters (characters that are in the annotations)
known_characters = set(
    [
        " ",
        "!",
        "#",
        ",",
        "-",
        ".",
        "/",
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        ":",
        "?",
        "@",
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "Y",
        "Z",
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "r",
        "s",
        "t",
        "u",
        "v",
        "y",
        "z",
        "©",
        "Á",
        "É",
        "Í",
        "Ú",
        "Ý",
        "á",
        "é",
        "í",
        "ú",
        "ý",
        "Č",
        "č",
        "ď",
        "Ě",
        "ě",
        "Ň",
        "Ř",
        "ř",
        "Š",
        "š",
        "Ů",
        "ů",
        "Ž",
        "ž",
    ]
)


def run_on_mpocr_json_with_transformed_ocr(
    mpocr_json_file,
    tesseract_results_file,
    debug=False,
    ignore_special_characters=False,
    iou_threshold=0.1,
):
    """
    Evaluate OCR results in the tesseract format against annotations in MPOCR format.
    """
    # Load ground truth annotations
    with open(mpocr_json_file, "r", encoding="utf-8") as f:
        mpocr_data = json.load(f)

    # Load OCR results
    with open(tesseract_results_file, "r", encoding="utf-8") as f:
        tesseract_results = json.load(f)

    total_S = 0
    total_D = 0
    total_I = 0
    total_N = 0
    detection_accuracy = 0
    total_boxes = 0

    # Create a mapping from image_id to annotations
    img_to_anns = {}

    # Build img_to_anns mapping
    if "imgToAnns" in mpocr_data:
        img_to_anns = mpocr_data["imgToAnns"]
    elif "anns" in mpocr_data:
        for ann_id, ann in mpocr_data["anns"].items():
            image_id = ann["image_id"]
            if image_id not in img_to_anns:
                img_to_anns[image_id] = []
            img_to_anns[image_id].append(ann_id)

    # Process each file in the OCR results
    for item in tesseract_results:
        if "file" not in item or not item["ocr_result"]:
            continue

        file_name = item["file"]
        image_id = file_name.split(".")[0]  # Remove file extension

        # Skip if this image doesn't have annotations
        if image_id not in img_to_anns:
            continue

        # Get ground truth bounding boxes and text
        gt_boxes = []
        for ann_id in img_to_anns[image_id]:
            ann = mpocr_data["anns"][ann_id]
            bbox = ann["bbox"]

            # Handle different bbox formats
            if len(bbox) == 4:
                if bbox[2] > bbox[0] and bbox[3] > bbox[1]:
                    # It's [x1, y1, x2, y2] format
                    x = bbox[0]
                    y = bbox[1]
                    w = bbox[2] - bbox[0]
                    h = bbox[3] - bbox[1]
                else:
                    # It's already [x, y, w, h] format
                    x = bbox[0]
                    y = bbox[1]
                    w = bbox[2]
                    h = bbox[3]

                gt_boxes.append(
                    {
                        "tag": ann_id,
                        "text": ann["utf8_string"],
                        "coordinates": (x, y, w, h),
                    }
                )

        # Skip if no valid gt boxes
        if not gt_boxes:
            continue

        # Convert OCR results
        ocr_boxes = []
        for ocr_box in item["ocr_result"]:
            if "coordinates" in ocr_box and len(ocr_box["coordinates"]) == 4:
                x, y, w, h = ocr_box["coordinates"]
                ocr_boxes.append({"text": ocr_box["text"], "coordinates": (x, y, w, h)})

        # Skip if no valid OCR boxes
        if not ocr_boxes:
            continue

        # Assign OCR boxes to ground truth boxes
        assigned_boxes = assign_bboxes(gt_boxes, ocr_boxes)

        # Calculate metrics with better error handling
        for assigned_box in assigned_boxes:
            total_boxes += 1

            # Check for valid detection based on IoU
            if assigned_box["sum_iou"] > iou_threshold:
                detection_accuracy += 1

                # Only calculate text metrics for detected boxes
                joined_text = " ".join(
                    [box["text"] for box in assigned_box["assigned_bboxes"]]
                )

                # Normalize text for comparison
                if ignore_special_characters:
                    assigned_box_text = "".join(
                        [
                            char
                            for char in assigned_box["text"]
                            if char not in special_characters
                        ]
                    )
                    joined_text = "".join(
                        [char for char in joined_text if char not in special_characters]
                    )
                else:
                    assigned_box_text = assigned_box["text"]

                # Skip empty text comparisons
                if not assigned_box_text or not joined_text:
                    continue

                # Calculate WER metrics
                S, D, I, N = wer(assigned_box_text, joined_text)

                # Cap errors at length of reference text
                max_errors = len(assigned_box_text)
                S = min(S, max_errors)
                D = min(D, max_errors)
                I = min(I, max_errors)

                total_S += S
                total_D += D
                total_I += I
                total_N += N

                if debug:
                    print(f"File: {file_name}, Annotation: {assigned_box['tag']}")
                    print(f"Ground truth: {assigned_box_text}")
                    print(f"OCR result: {joined_text}")
                    print(f"Sum IOU: {assigned_box['sum_iou']}")
                    print(f"S: {S}, D: {D}, I: {I}, N: {N}")
                    print("-" * 50)

    # Calculate final metrics
    CER = ((total_S + total_D + total_I) / total_N) * 100 if total_N > 0 else 0
    # Cap CER at 100%
    CER = min(CER, 100.0)
    CAcc = 100 - CER
    detection_acc = detection_accuracy / total_boxes * 100 if total_boxes > 0 else 0

    print(f"No. of characters in the reference: {total_N}")
    print(f"No. of substitutions: {total_S}")
    print(f"No. of deletions: {total_D}")
    print(f"No. of insertions: {total_I}")
    print(f"Character Error Rate: {CER:.1f}%")
    print(f"Character Accuracy: {CAcc:.1f}%")
    print(f"Detection Accuracy: {detection_acc:.1f}%")

    return {
        "CER": CER,
        "CAcc": CAcc,
        "detection_accuracy": detection_acc,
        "total_S": total_S,
        "total_D": total_D,
        "total_I": total_I,
        "total_N": total_N,
        "total_boxes": total_boxes,
        "detected_boxes": detection_accuracy,
    }

tesseract_eval_paths = [
    "dataset_tesseract_oem_0_psm_11.json",
    "dataset_tesseract_oem_0_psm_12.json",
    "dataset_tesseract_oem_0_psm_13.json",
    "dataset_tesseract_oem_0_psm_1.json",
    "dataset_tesseract_oem_0_psm_3.json",
    "dataset_tesseract_oem_0_psm_4.json",
    "dataset_tesseract_oem_0_psm_5.json",
    "dataset_tesseract_oem_0_psm_6.json",
    "dataset_tesseract_oem_0_psm_9.json",
    "dataset_tesseract_oem_1_psm_10.json",
    "dataset_tesseract_oem_1_psm_11.json",
    "dataset_tesseract_oem_1_psm_12.json",
    "dataset_tesseract_oem_1_psm_13.json",
    "dataset_tesseract_oem_1_psm_1.json",
    "dataset_tesseract_oem_1_psm_3.json",
    "dataset_tesseract_oem_1_psm_4.json",
    "dataset_tesseract_oem_1_psm_5.json",
    "dataset_tesseract_oem_1_psm_6.json",
    "dataset_tesseract_oem_1_psm_7.json",
    "dataset_tesseract_oem_1_psm_8.json",
    "dataset_tesseract_oem_1_psm_9.json"
    ]

wer_only_tesseract = [
  "wer_only_dataset_tesseract_oem_0_psm_11.json",
  "wer_only_dataset_tesseract_oem_0_psm_12.json",
  "wer_only_dataset_tesseract_oem_0_psm_13.json",
  "wer_only_dataset_tesseract_oem_0_psm_1.json",
  "wer_only_dataset_tesseract_oem_0_psm_3.json",
  "wer_only_dataset_tesseract_oem_0_psm_4.json",
  "wer_only_dataset_tesseract_oem_0_psm_5.json",
  "wer_only_dataset_tesseract_oem_0_psm_6.json",
  "wer_only_dataset_tesseract_oem_0_psm_7.json",
  "wer_only_dataset_tesseract_oem_0_psm_8.json",
  "wer_only_dataset_tesseract_oem_0_psm_9.json",
  "wer_only_dataset_tesseract_oem_1_psm_10.json",
  "wer_only_dataset_tesseract_oem_1_psm_11.json",
  "wer_only_dataset_tesseract_oem_1_psm_12.json",
  "wer_only_dataset_tesseract_oem_1_psm_13.json",
  "wer_only_dataset_tesseract_oem_1_psm_1.json",
  "wer_only_dataset_tesseract_oem_1_psm_3.json",
  "wer_only_dataset_tesseract_oem_1_psm_4.json",
  "wer_only_dataset_tesseract_oem_1_psm_5.json",
  "wer_only_dataset_tesseract_oem_1_psm_6.json",
  "wer_only_dataset_tesseract_oem_1_psm_7.json",
  "wer_only_dataset_tesseract_oem_1_psm_8.json",
  "wer_only_dataset_tesseract_oem_1_psm_9.json",
]

def eval_dir(dir_path, agent_dir="agent"):
    """
    Evaluate all JSON files in a directory and save the results to a single JSON file.
    """
    import json
    import os

    if not os.path.isdir(dir_path):
        raise ValueError("dir_path should be a directory")

    # Create an empty list to store results
    results = []

    # Loop through each file in the directory
    evaluation_dir = os.path.join("results", "evaluation", agent_dir, "dataset_full")
    os.makedirs(evaluation_dir, exist_ok=True)
    for filename in os.listdir(dir_path):
        print("Evaluating file:", filename)
        if filename.endswith(".json"):
            result = run_on_json(os.path.join(dir_path, filename))
            output_file = os.path.join(evaluation_dir, filename)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4)
            print(f"Saved evaluation for {filename} to {output_file}")

    # Save the results to a single JSON file
    # with open(output_name, "w", encoding="utf-8") as f:
    #     json.dump(results, f, indent=4)

def eval_bulk_paths(paths):
    """
    Evaluate multiple JSON files and save the results to a single JSON file.
    """
    import json

    if not isinstance(paths, list):
        raise ValueError("paths should be a list of JSON file paths")

    # Create an empty list to store results
    results = []

    # Loop through each path, evaluate, and append the result to the list
    for path in paths:
        result = run_on_json("ocr_data/"+path)
        result["file"] = path  # Add the file name to the result
        results.append(result)

    # Save the results to a single JSON file
    with open("combined_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

def eval_bulk_paths_dtw_wer_only(paths):
    """
    Evaluate multiple JSON files and save the results to a single JSON file.
    """
    import json

    if not isinstance(paths, list):
        raise ValueError("paths should be a list of JSON file paths")

    # Create an empty list to store results
    results = []

    # Loop through each path, evaluate, and append the result to the list
    for path in paths:
        result = evaluate_ocr_dtw_wer_only("ocr_data/"+path)
        result["file"] = path  # Add the file name to the result
        results.append(result)

    # Save the results to a single JSON file
    with open("tesseract_dtw_wer_onlycombined_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
def eval_bulk_directory_dtw_wer_only(directory_path):
    """
    Evaluate all JSON files in a directory and save the results to a single JSON file.
    """
    import json
    import os

    if not os.path.isdir(directory_path):
        raise ValueError("directory_path should be a directory")

    # Create an empty list to store results
    results = []

    # Loop through each file in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            result = evaluate_ocr_dtw_wer_only(os.path.join(directory_path, filename))
            result["file"] = filename  # Add the file name to the result
            results.append(result)

    # Save the results to a single JSON file
    with open("combined_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

def eval_results_directory_dtw_wer_only(results_dir):
    """
    Evaluate all JSON files in the results directory (wer_only) and save the evaluations.
    """
    import os
    import json

    for agent_dir in os.listdir(results_dir):
        agent_path = os.path.join(results_dir, agent_dir, "wer_only")
        if not os.path.isdir(agent_path):
            continue

        evaluation_dir = os.path.join("results", "evaluation", agent_dir, "wer_only")
        os.makedirs(evaluation_dir, exist_ok=True)

        for filename in os.listdir(agent_path):
            if filename.endswith(".json"):
                result = evaluate_ocr_dtw_wer_only(os.path.join(agent_path, filename))
                output_file = os.path.join(evaluation_dir, filename)
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=4)
                print(f"Saved evaluation for {filename} to {output_file}")


def eval_results_directory_full(results_dir):
    """
    Evaluate all JSON files in the results directory (dataset_full) and save the evaluations.
    """
    import os
    import json

    for agent_dir in os.listdir(results_dir):
        agent_path = os.path.join(results_dir, agent_dir, "dataset_full")
        if not os.path.isdir(agent_path):
            continue

        evaluation_dir = os.path.join("results", "evaluation", agent_dir, "dataset_full")
        os.makedirs(evaluation_dir, exist_ok=True)

        for filename in os.listdir(agent_path):
            if filename.endswith(".json"):
                result = run_on_json(os.path.join(agent_path, filename))
                output_file = os.path.join(evaluation_dir, filename)
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=4)
                print(f"Saved evaluation for {filename} to {output_file}")

def evaluate_ocr_dtw_iou(json_file):
    """
    Evaluate OCR results by calculating average, min, and max IoU across the dataset.
    """
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_iou = 0
    total_boxes = 0
    min_iou = float("inf")
    max_iou = float("-inf")

    for record in data:
        try:
            assigned_boxes = assign_bboxes(record["annotation"], record["ocr_result"])
        except TypeError:
            continu

        for assigned_box in assigned_boxes:
            iou = assigned_box["sum_iou"]
            print("THIS IOU", iou)
            total_iou += iou
            total_boxes += 1
            min_iou = min(min_iou, iou)
            max_iou = max(max_iou, iou)
            if iou > 1:
                # plots the image
                print("Max iou is", max_iou)
                print("origin file: ", record["file"])
                print("configuration ", json_file)
                print("assigned box text: ", assigned_box["text"])

                if record["file"] == "DB160330-Scene-017-02.jpg":
                    input()
    if max_iou >1:
        print("Total IOU ", total_iou)
        print("Total boxes ", total_boxes)
        print("Average Iou", total_iou / total_boxes)




    avg_iou = total_iou / total_boxes if total_boxes > 0 else 0

    print(f"Average IoU: {avg_iou:.4f}")
    print(f"Minimum IoU: {min_iou:.4f}")
    print(f"Maximum IoU: {max_iou:.4f}")

    return {
        "average_iou": avg_iou,
        "min_iou": min_iou,
        "max_iou": max_iou,
        "total_boxes": total_boxes,
    }

def eval_results_directory_iou(results_dir, save=True):
    """
    Evaluate all JSON files in the results directory (dataset_full) for IoU and save the evaluations.
    """
    import os
    import json

    for agent_dir in os.listdir(results_dir):
        agent_path = os.path.join(results_dir, agent_dir, "dataset_full")
        print("Agent Dir Path", agent_path)
        if not os.path.isdir(agent_path):
            continue

        evaluation_dir = os.path.join("results", "evaluation", agent_dir, "iou")
        os.makedirs(evaluation_dir, exist_ok=True)
        for filename in os.listdir(agent_path):
            if filename.endswith(".json"):
                result = evaluate_ocr_dtw_iou(os.path.join(agent_path, filename))
                if save:
                    output_file = os.path.join(evaluation_dir, filename)

                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(result, f, indent=4)
                    print(f"Saved IoU evaluation for {filename} to {output_file}")
IOU_THRESHOLD = 0.95


def compare_ocr_results(json_file_1, json_file_2):
    """
    Compare two OCR result JSON files by evaluating their IoU metrics and printing the differences.
    
    Args:
        json_file_1: Path to the first OCR result JSON file.
        json_file_2: Path to the second OCR result JSON file.
    """
    import json

    # Load the two JSON files
    with open(json_file_1, "r", encoding="utf-8") as f1, open(json_file_2, "r", encoding="utf-8") as f2:
        data_1 = json.load(f1)
        data_2 = json.load(f2)

    # Ensure both files have the same number of records
    if len(data_1) != len(data_2):
        print("The two JSON files have different numbers of records. Comparison may not be accurate.")
        return

    print(f"Comparing results from {json_file_1} and {json_file_2}:\n")

    max_average_iou_difference = 0
    max_average_iou_difference_file = ""
    method_with_bigger_average = ""
    # Iterate through the records and compare metrics
    for record_1, record_2 in zip(data_1, data_2):
        file_1 = record_1["file"]
        file_2 = record_2["file"]

        # Ensure the files being compared are the same
        if file_1 != file_2:
            print(f"Mismatch in file names: {file_1} vs {file_2}. Skipping comparison for this record.")
            continue

        # Evaluate IoU metrics for both records
        result_1 = evaluate_ocr_dtw_iou_single(record_1)
        result_2 = evaluate_ocr_dtw_iou_single(record_2)
        average_iou_difference = abs(result_1["average_iou"] - result_2["average_iou"])
        if average_iou_difference > max_average_iou_difference:
            max_average_iou_difference = average_iou_difference
            max_average_iou_difference_file = file_1
            if result_1["average_iou"] > result_2["average_iou"]:
                method_with_bigger_average = json_file_1
            else:
                method_with_bigger_average = json_file_2

        # Print the differences
        print(f"File: {file_1}")
        print(f"  Average IoU Difference: {result_1['average_iou'] - result_2['average_iou']:.4f}")
        print(f"  Min IoU Difference: {result_1['min_iou'] - result_2['min_iou']:.4f}")
        print(f"  Max IoU Difference: {result_1['max_iou'] - result_2['max_iou']:.4f}")
        print(f"  Total Boxes Difference: {result_1['total_boxes'] - result_2['total_boxes']}\n")
    print(f"Maximum average IoU difference: {max_average_iou_difference:.4f} for file {max_average_iou_difference_file}")
    print("Method with bigger average IoU: ", method_with_bigger_average)


def evaluate_ocr_dtw_iou_single(record):
    """
    Evaluate a single OCR record by calculating average, min, and max IoU.
    
    Args:
        record: A single OCR record containing annotations and OCR results.
    
    Returns:
        A dictionary with IoU metrics.
    """
    total_iou = 0
    total_boxes = 0
    min_iou = float("inf")
    max_iou = float("-inf")

    try:
        assigned_boxes = assign_bboxes(record["annotation"], record["ocr_result"])
    except TypeError:
        return {
            "average_iou": 0,
            "min_iou": 0,
            "max_iou": 0,
            "total_boxes": 0,
        }

    for assigned_box in assigned_boxes:
        iou = assigned_box["sum_iou"]
        total_iou += iou
        total_boxes += 1
        min_iou = min(min_iou, iou)
        max_iou = max(max_iou, iou)

    avg_iou = total_iou / total_boxes if total_boxes > 0 else 0

    return {
        "average_iou": avg_iou,
        "min_iou": min_iou,
        "max_iou": max_iou,
        "total_boxes": total_boxes,
    }

if __name__ == "__main__":
    # Use defined functions to evaluate data

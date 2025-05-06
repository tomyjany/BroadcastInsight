from evaluate_ocr import assign_bboxes
import json

# def evaluate_ocr_dtw_iou(json_file):
#     """
#     Evaluate OCR results by calculating average, min, and max IoU across the dataset.
#     Also tracks the number of OCR boundary boxes not linked to any annotation.
#     """
#     with open(json_file, "r", encoding="utf-8") as f:
#         data = json.load(f)
#
#     total_iou = 0
#     total_boxes = 0
#     min_iou = float("inf")
#     max_iou = float("-inf")
#     unlinked_boxes_count = 0  # Counter for unlinked OCR boxes
#     linked_boxes_count = 0
#     all_boxes =0
#
#     for record in data:
#         try:
#             assigned_boxes = assign_bboxes(record["annotation"], record["ocr_result"])
#         except TypeError:
#             continue
#
#         linked_boxes = set()  # Track linked OCR box indices
#         for assigned_box in assigned_boxes:
#             iou = assigned_box["sum_iou"]
#             total_iou += iou
#             total_boxes += 1
#             min_iou = min(min_iou, iou)
#             max_iou = max(max_iou, iou)
#
#             # Track linked OCR boxes
#             for linked_box in assigned_box["assigned_bboxes"]:
#                 linked_boxes.add(linked_box["index"])
#
#         # Count unlinked OCR boxes
#         all_ocr_indices = {i for i in range(len(record["ocr_result"]))}
#         unlinked_boxes = all_ocr_indices - linked_boxes
#         unlinked_boxes_count += len(unlinked_boxes)
#         linked_boxes_count += len(linked_boxes)
#         all_boxes += len(record["ocr_result"])
#
#         # Debugging output for IoU > 1
#         if max_iou > 1:
#             print("Max IoU is", max_iou)
#             print("Origin file:", record["file"])
#             print("Configuration:", json_file)
#             print("Assigned box text:", assigned_box["text"])
#             # if record["file"] == "DB160330-Scene-017-02.jpg":
#             #     input()
#
#     if max_iou > 1:
#         print("Total IoU:", total_iou)
#         print("Total boxes:", total_boxes)
#         print("Average IoU:", total_iou / total_boxes)
#
#     avg_iou = total_iou / total_boxes if total_boxes > 0 else 0
#
#     print(f"Average IoU: {avg_iou:.4f}")
#     print(f"Minimum IoU: {min_iou:.4f}")
#     print(f"Maximum IoU: {max_iou:.4f}")
#     print(f"Unlinked OCR Boxes: {unlinked_boxes_count}")
#     print(f"linked OCR Boxes: {linked_boxes_count}")
#
#     # Calculate precision, recall, and F1 score
#     precision = linked_boxes_count / (linked_boxes_count + unlinked_boxes_count) if (linked_boxes_count + unlinked_boxes_count) > 0 else 0
#     recall = linked_boxes_count / all_boxes if all_boxes > 0 else 0
#     f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
#
#     return {
#         "average_iou": avg_iou,
#         "min_iou": min_iou,
#         "max_iou": max_iou,
#         "all_boxes": all_boxes,
#         "unlinked_boxes": unlinked_boxes_count,
#         "linked_boxes": linked_boxes_count,
#         "total_boxes": total_boxes,
#         "precision": precision,
#         "recall": recall,
#         "f1_score": f1_score,
#     }

def evaluate_ocr_dtw_iou(json_file):
    """
    Evaluate OCR results by calculating average, min, and max IoU across the dataset.
    Also incorporates weighted false positives and false negatives based on bounding box area.
    """
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_iou = 0
    total_boxes = 0
    min_iou = float("inf")
    max_iou = float("-inf")
    linked_area = 0  # Total area of linked OCR boxes
    weighted_false_positive_area = 0  # Total area of unlinked OCR boxes
    weighted_false_negative_area = 0  # Total area of unlinked annotation boxes

    for record in data:
        try:
            assigned_boxes = assign_bboxes(record["annotation"], record["ocr_result"])
        except TypeError:
            continue

        linked_boxes = set()  # Track linked OCR box indices
        for assigned_box in assigned_boxes:
            iou = assigned_box["sum_iou"]
            total_iou += iou
            total_boxes += 1
            min_iou = min(min_iou, iou)
            max_iou = max(max_iou, iou)

            # Calculate linked area
            for linked_box in assigned_box["assigned_bboxes"]:
                linked_boxes.add(linked_box["index"])
                bbox_area = linked_box["coordinates"][2] * linked_box["coordinates"][3]  # width * height
                linked_area += bbox_area

            # Calculate false negatives (annotation boxes not linked to any OCR box)
            if not assigned_box["assigned_bboxes"]:
                if "coordinates" in assigned_box.get("bbox_data", {}):
                    bbox_area = assigned_box["bbox_data"]["coordinates"][2] * assigned_box["bbox_data"]["coordinates"][3]
                    weighted_false_negative_area += bbox_area
                else:
                    print(f"Skipping assigned_box['bbox_data']: {assigned_box.get('bbox_data')} (invalid structure)")

        # Calculate false positives (unlinked OCR boxes)
        all_ocr_indices = {i for i in range(len(record["ocr_result"]))}
        unlinked_boxes = all_ocr_indices - linked_boxes
        for idx in unlinked_boxes:
            bbox = record["ocr_result"][idx]
            bbox_area = bbox["coordinates"][2] * bbox["coordinates"][3]  # width * height
            weighted_false_positive_area += bbox_area

    avg_iou = total_iou / total_boxes if total_boxes > 0 else 0

    # Calculate precision, recall, and F1 score
    precision = linked_area / (linked_area + weighted_false_positive_area) if (linked_area + weighted_false_positive_area) > 0 else 0
    recall = linked_area / (linked_area + weighted_false_negative_area) if (linked_area + weighted_false_negative_area) > 0 else 0
    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    print(f"Average IoU: {avg_iou:.4f}")
    print(f"Minimum IoU: {min_iou:.4f}")
    print(f"Maximum IoU: {max_iou:.4f}")
    print(f"Weighted False Positive Area: {weighted_false_positive_area:.4f}")
    print(f"Weighted False Negative Area: {weighted_false_negative_area:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1_score:.4f}")

    return {
        "average_iou": avg_iou,
        "min_iou": min_iou,
        "max_iou": max_iou,
        "linked_area": linked_area,
        "weighted_false_positive_area": weighted_false_positive_area,
        "weighted_false_negative_area": weighted_false_negative_area,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
    }
def eval_results_directory_iou(results_dir, save=True):
    """
    Evaluate all JSON files in the results directory (dataset_full) for IoU and save the evaluations.
    Also tracks the number of OCR boundary boxes not linked to any annotation.
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
if __name__ == "__main__":
    # Example usage
    results_dir = "results"
    eval_results_directory_iou(results_dir)
    # evaluate_ocr_dtw_iou("results/tesseract/dataset_full/BA180101-Scene-424-02.json")
"""
### Metrics for Evaluating OCR Results

1. **Intersection over Union (IoU)**:
   - **Definition**: Measures the overlap between OCR-detected bounding boxes and ground truth annotations.
   - **Metrics**:
     - **Average IoU**: Mean IoU across all linked bounding boxes.
     - **Minimum IoU**: Smallest IoU value among linked bounding boxes.
     - **Maximum IoU**: Largest IoU value among linked bounding boxes.

2. **Linked Area**:
   - **Definition**: Total area of OCR bounding boxes correctly linked to annotations.
   - **Purpose**: Quantifies the size of correctly detected OCR regions.

3. **Weighted False Positive Area**:
   - **Definition**: Total area of OCR bounding boxes not linked to any annotation.
   - **Purpose**: Penalizes larger false positives more heavily.

4. **Weighted False Negative Area**:
   - **Definition**: Total area of annotation bounding boxes not linked to any OCR box.
   - **Purpose**: Penalizes larger missed annotations more heavily.

5. **Precision**:
   - **Formula**:  
     \[
     \text{Precision} = \frac{\text{Linked Area}}{\text{Linked Area} + \text{Weighted False Positive Area}}
     \]
   - **Purpose**: Measures the accuracy of OCR detections.

6. **Recall**:
   - **Formula**:  
     \[
     \text{Recall} = \frac{\text{Linked Area}}{\text{Linked Area} + \text{Weighted False Negative Area}}
     \]
   - **Purpose**: Measures the completeness of OCR detections.

7. **F1 Score**:
   - **Formula**:  
     \[
     \text{F1 Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}
     \]
   - **Purpose**: Balances precision and recall into a single metric.

---

### Summary of Purpose
These metrics provide a comprehensive evaluation of OCR performance by assessing the quality of bounding box alignment (IoU), penalizing detection errors based on their size (weighted areas), and balancing accuracy and completeness (precision, recall, F1 score).

"""

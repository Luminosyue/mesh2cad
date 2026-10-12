from __future__ import annotations


def bidirectional_qa(source_metrics: dict, candidate_metrics: dict) -> dict:
    return {
        "local_chamfer": candidate_metrics.get("chamfer"),
        "local_hausdorff": candidate_metrics.get("hausdorff"),
        "source_candidate_occupancy_iou": candidate_metrics.get("occupancy_iou"),
        "source_candidate_occupancy_precision": candidate_metrics.get("occupancy_precision"),
        "source_candidate_occupancy_recall": candidate_metrics.get("occupancy_recall"),
        "false_positive_occupancy_ratio": candidate_metrics.get("false_positive_occupancy_ratio"),
        "false_negative_occupancy_ratio": candidate_metrics.get("false_negative_occupancy_ratio"),
        "void_preservation_ratio": candidate_metrics.get("void_preservation_ratio"),
        "section_occupancy_iou_mean": candidate_metrics.get("section_occupancy_iou_mean"),
        "section_occupancy_iou_p10": candidate_metrics.get("section_occupancy_iou_p10"),
        "section_false_positive_mean": candidate_metrics.get("section_false_positive_mean"),
    }

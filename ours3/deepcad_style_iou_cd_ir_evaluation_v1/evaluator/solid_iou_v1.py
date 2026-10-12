"""Solid/BRep IoU protocol using CadQuery/OCC booleans."""
from __future__ import annotations


def _shape(obj):
    if hasattr(obj, "val"):
        obj = obj.val()
    if obj is None or not hasattr(obj, "isValid") or not obj.isValid():
        raise ValueError("invalid BRep shape")
    if obj.Volume() <= 0:
        raise ValueError("empty or zero-volume BRep")
    return obj


def solid_iou(pred, gt):
    p, g = _shape(pred), _shape(gt)
    inter = p.intersect(g)
    union = p.fuse(g)
    if not inter.isValid() or not union.isValid():
        raise ValueError("boolean result invalid")
    inter_v, union_v = float(inter.Volume()), float(union.Volume())
    if union_v <= 0:
        raise ValueError("union has zero volume")
    return {"intersection_volume": inter_v, "union_volume": union_v, "iou": inter_v / union_v}

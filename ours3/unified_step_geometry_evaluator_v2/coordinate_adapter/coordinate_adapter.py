"""Frozen official CAD-Recode STEP -> dataset canonical coordinate adapter."""
import numpy as np
import cadquery as cq
from OCP.gp import gp_Pnt, gp_Trsf, gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform

CAD_RECODE_TO_CANONICAL_SCALE = 1.0 / 200.0
CAD_RECODE_TO_CANONICAL_TRANSLATION = np.array([0.5, 0.5, 0.5], dtype=float)

def transform_point(point):
    p = np.asarray(point, dtype=float)
    return p * CAD_RECODE_TO_CANONICAL_SCALE + CAD_RECODE_TO_CANONICAL_TRANSLATION

def identity_shape(shape):
    return shape

def cad_recode_shape_to_canonical(shape):
    # OCC uniform scale + translation preserves the STEP topology more robustly
    # than CadQuery's general GTransform for trimmed surfaces.
    t = gp_Trsf()
    t.SetScale(gp_Pnt(0, 0, 0), CAD_RECODE_TO_CANONICAL_SCALE)
    t.SetTranslationPart(gp_Vec(*CAD_RECODE_TO_CANONICAL_TRANSLATION.tolist()))
    return cq.Shape.cast(BRepBuilderAPI_Transform(shape.wrapped, t, True).Shape())

def adapt_shape(shape, source_frame):
    if source_frame == 'DATASET_CANONICAL':
        return identity_shape(shape)
    if source_frame == 'OFFICIAL_CENTERED_CUBE2':
        return cad_recode_shape_to_canonical(shape)
    raise ValueError(f'unknown source frame: {source_frame}')

import numpy as np
import torch
from .anchor_features import object_anchor, AnchorMLP
def test_object_frame_not_curve_frame():
    curves=np.array([[[0,0,0],[2,4,6]], [[8,0,0],[10,4,6]]],np.float32)
    x=object_anchor(curves,np.zeros(3),np.array([10,10,10],np.float32))
    assert np.allclose(x[0],[-.4,-.3,-.2,.2,.4,.6])
    assert np.allclose(x[1],[.4,-.3,-.2,.2,.4,.6])
def test_fusion_shape():
    out=AnchorMLP()(torch.zeros(3,256),torch.zeros(3,6)); assert out.shape==(3,256)

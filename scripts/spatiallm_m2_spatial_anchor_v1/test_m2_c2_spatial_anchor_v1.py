import torch
from torch import nn
from .m2_c2_spatial_anchor_v1 import M2C2SpatialAnchorV1
class Adapter(nn.Module):
 def forward(self,x,m):return x,m
def test_c2_not_owned_and_shapes_preserved():
 m=M2C2SpatialAnchorV1(Adapter()); x=torch.randn(2,4,256); a=torch.randn(2,4,6); mask=torch.ones(2,4,dtype=torch.bool); out,got=m(x,a,mask)
 assert out.shape==(2,4,256) and got.equal(mask) and not m.trainable_parameter_groups()['c2']

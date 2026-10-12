#!/usr/bin/env python3
import torch
from torch import nn
from .m2_c2_spatial_anchor_v1 import M2C2SpatialAnchorV1
class Adapter(nn.Module):
 def forward(self,x,m): return x,m
def main():
 model=M2C2SpatialAnchorV1(Adapter()); out,mask=model(torch.randn(2,4,256),torch.randn(2,4,6),torch.ones(2,4,dtype=torch.bool))
 assert tuple(out.shape)==(2,4,256) and mask.all() and model.trainable_parameter_groups()['c2']==[]
 print('M2_C2_SPATIAL_ANCHOR_V1_CONTRACT=PASS')
if __name__=='__main__':main()

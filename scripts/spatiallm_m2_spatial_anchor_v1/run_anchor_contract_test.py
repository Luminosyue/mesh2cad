#!/usr/bin/env python3
import numpy as np
import torch
from .anchor_features import object_anchor, AnchorMLP
def main():
 curves=np.array([[[0,0,0],[2,4,6]],[[8,0,0],[10,4,6]]],np.float32)
 anchors=object_anchor(curves,np.zeros(3),np.array([10,10,10],np.float32))
 expected=np.array([[-.4,-.3,-.2,.2,.4,.6],[.4,-.3,-.2,.2,.4,.6]],np.float32)
 if not np.allclose(anchors,expected): raise RuntimeError(f'anchor mismatch: {anchors}')
 out=AnchorMLP()(torch.zeros(2,256),torch.from_numpy(anchors))
 if tuple(out.shape)!=(2,256): raise RuntimeError(f'fused shape {tuple(out.shape)}')
 print('M2_C2_ANCHOR_CONTRACT=PASS')
if __name__=='__main__': main()

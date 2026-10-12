"""Run the original P1 encoder on the exported tire curves, without training."""
from pathlib import Path
import sys
import numpy as np
import torch

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path.insert(0,str(ROOT/'scripts'))
from curve_encoder_baseline_v1.models import build_model

data_dir=Path(__file__).resolve().parent
checkpoint=ROOT/'ours3/curve_encoder_baseline_v1/runs/P1_frozen_v1/best.pt'
z=np.load(data_dir/'encoder_input_p1.npz')
x=torch.from_numpy(z['feats'])
assert x.ndim==3 and x.shape[1:]==(32,6)
model=build_model('pointnet',('xyz','tangent'))
state=torch.load(checkpoint,map_location='cpu',weights_only=False)
model.load_state_dict(state['model'],strict=True)
model.eval()
torch.set_num_threads(2)
with torch.inference_mode():
    output=model(x)
tokens=output['token'].cpu().numpy()
expected=np.load(data_dir/'p1_curve_tokens.npy')
np.testing.assert_allclose(tokens,expected,rtol=1e-5,atol=1e-6)
print('input',tuple(x.shape),'tokens',tokens.shape,'all finite',bool(np.isfinite(tokens).all()))

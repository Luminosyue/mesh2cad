import os,sys
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); EXP=ROOT/'ours3/airplane_fullseq_14bit_ir_v1'
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'SpatialLM'),str(EXP)]
os.environ['CAD_SECOND_STREAM']='curve_tokens'; os.environ['CAD_USE_SEPARATE_EDGE_TOKENS']='1'
os.environ['CURVE_TOKEN_REGISTRY']=str(EXP/'curve_registry.jsonl'); os.environ['REQUIRE_CURVE_TOKEN_REGISTRY']='1'
os.environ['CURVE_TOKEN_ROOT']=str(ROOT/'ours3/exact9998_curve_tokens_c2_v1'); os.environ['C2_CHECKPOINT_PATH']=str(ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt')
os.environ['CUDA_VISIBLE_DEVICES']='7'
from spatiallm_curve_token_v1 import curve_token_injector
curve_token_injector.install()
from spatiallm.tuner.trainer import run_exp
sys.argv=[sys.argv[0],str(EXP/'part000_overfit.yaml')]
raise SystemExit(run_exp())

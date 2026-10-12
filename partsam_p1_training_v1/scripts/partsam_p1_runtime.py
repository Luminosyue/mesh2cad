"""Isolated PartSAM registration; leaves original P1/DeepCAD source files intact."""
from pathlib import Path
import os,sys,json
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OUT=ROOT/'partsam_p1_training_v1'
sys.path[:0]=[str(ROOT),str(ROOT/'scripts'),str(ROOT/'SpatialLM')]

def install():
    os.environ.update(CAD_SECOND_STREAM='curve_tokens',CAD_USE_SEPARATE_EDGE_TOKENS='1',
        CURVE_TOKEN_REGISTRY=str(OUT/'CURVE_TOKEN_REGISTRY.jsonl'),REQUIRE_CURVE_TOKEN_REGISTRY='1',DISABLE_VERSION_CHECK='1')
    os.environ.setdefault('P1_LAMBDA_OP','1.0')
    from spatiallm_curve_token_v1 import curve_token_injector as ci
    ci._DATASET_BY_PACK_DIR['PartSAM']='partsam'
    ci.install()
    import p1_operation_loss_runtime as op
    # Only the in-process registry root is changed, before registry loading.
    op.EXP=OUT;op.REG.clear()
    for split in ('TRAIN','VAL','TEST'):
        path=OUT/'masks'/f'{split}_OPERATION_TOKEN_MASK_REGISTRY.jsonl'
        if path.exists():
            for line in path.read_text().splitlines():
                row=json.loads(line);op.REG[row['response_sha256']]=row
    return op.install()

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: python3 partsam_p1_runtime.py config.yaml')
    config=Path(sys.argv[1]).resolve()
    if not config.is_file():raise SystemExit(f'Config does not exist: {config}')
    sys.argv[1]=str(config)
    install()
    from spatiallm.tuner.trainer import run_exp
    os.chdir(ROOT/'SpatialLM');run_exp()

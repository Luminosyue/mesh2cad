import os,sys
from pathlib import Path
ROOT=Path("/data/home/cuiyuehan/project/mesh2cad");EXP=ROOT/"ours3/p1v2_size_placement_overfit32_v1"
sys.path[:0]=[str(EXP),str(ROOT),str(ROOT/"scripts"),str(ROOT/"ours3/m2_exact9998_corrected_m2_train_v1/launch"),str(ROOT/"SpatialLM")]
os.environ["P1V2_CONFIG_OVERRIDE"]=sys.argv[1]
import corrected_m2_runtime_audit;corrected_m2_runtime_audit.install()
import p2_size_loss_runtime;p2_size_loss_runtime.install()
from spatiallm_curve_token_v1.train_curve_token_spatiallm import main
sys.argv=[sys.argv[0],sys.argv[1]]
raise SystemExit(main())

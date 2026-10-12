import sys
sys.path.insert(0, '/data/home/cuiyuehan/project/mesh2cad/CADFit')
from run_pipeline import process_single_stl

process_single_stl(
    stl_path='/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/input_stl/PART_023.stl',
    folder_name='/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw',
    max_iterations=1,
    keep_history=True,
)

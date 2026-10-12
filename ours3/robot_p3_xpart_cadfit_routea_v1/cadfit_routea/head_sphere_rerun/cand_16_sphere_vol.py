import cadquery as cq
import math

result = cq.Workplane('XY').sphere(0.81146294)
cq.exporters.export(result, r'/data/home/cuiyuehan/project/mesh2cad/ours3/robot_p3_xpart_cadfit_routea_v1/cadfit_routea/head_sphere_rerun/cand_16_sphere_vol.stl')
print('OK')

import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.74356, 0.57011, 0.1041), normal=(-0.79752, 0.6033, -0.0002), xDir=(0.6033, 0.79752, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.03219, 0.12387)
loop_1 = loop_1.lineTo(0.09734, 0.12959)
loop_1 = loop_1.lineTo(0.15474, 0.1419)
loop_1 = loop_1.lineTo(0.16494, 0.14469)
loop_1 = loop_1.lineTo(0.18901, 0.15365)
loop_1 = loop_1.lineTo(0.20641, 0.16876)
loop_1 = loop_1.lineTo(0.22521, 0.1882)
loop_1 = loop_1.lineTo(0.24402, 0.20564)
loop_1 = loop_1.lineTo(0.26053, 0.22717)
loop_1 = loop_1.lineTo(0.16454, 0.14549)
loop_1 = loop_1.lineTo(0.0348, 0.12425)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_25_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_25_interval_1.stl')
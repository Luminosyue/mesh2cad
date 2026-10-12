import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.55672, -0.57258, -0.03362), normal=(0.51752, -0.85527, -0.02629), xDir=(-0.85556, -0.5177, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.46233, 0.20869)
loop_1 = loop_1.lineTo(0.47096, 0.18884)
loop_1 = loop_1.lineTo(0.47362, 0.15212)
loop_1 = loop_1.lineTo(0.47399, 0.10399)
loop_1 = loop_1.lineTo(0.48299, 0.00408)
loop_1 = loop_1.threePointArc((0.48607, -0.01956), (0.48876, -0.04037))
loop_1 = loop_1.lineTo(0.49183, -0.08849)
loop_1 = loop_1.lineTo(0.49899, -0.13661)
loop_1 = loop_1.lineTo(0.4626, 0.20516)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_9_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_9_interval_1.stl')
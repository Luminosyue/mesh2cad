import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.50909, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.81789, -0.29618)
loop_1 = loop_1.lineTo(-0.81748, -0.32295)
loop_1 = loop_1.threePointArc((-0.81592, -0.34937), (-0.81459, -0.37675))
loop_1 = loop_1.threePointArc((-0.81447, -0.39164), (-0.81411, -0.40577))
loop_1 = loop_1.lineTo(-0.81335, -0.42666)
loop_1 = loop_1.threePointArc((-0.81353, -0.45253), (-0.81326, -0.4772))
loop_1 = loop_1.lineTo(-0.80573, -0.51741)
loop_1 = loop_1.lineTo(-0.80331, -0.52836)
loop_1 = loop_1.lineTo(-0.81789, -0.5292)
loop_1 = loop_1.lineTo(-0.81789, -0.29634)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_59_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_59_interval_0.stl')
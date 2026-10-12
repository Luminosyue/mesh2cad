import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.49091, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.81794, 0.14482)
loop_1 = loop_1.threePointArc((-0.80997, 0.1206), (-0.80222, 0.0952))
loop_1 = loop_1.threePointArc((-0.78764, 0.068), (-0.77312, 0.04244))
loop_1 = loop_1.lineTo(-0.7475, 0.00954)
loop_1 = loop_1.lineTo(-0.73395, -0.00823)
loop_1 = loop_1.lineTo(-0.74663, -0.06017)
loop_1 = loop_1.threePointArc((-0.7522, -0.06217), (-0.75728, -0.06425))
loop_1 = loop_1.lineTo(-0.77491, -0.07262)
loop_1 = loop_1.lineTo(-0.79854, -0.09234)
loop_1 = loop_1.lineTo(-0.81559, -0.11225)
loop_1 = loop_1.lineTo(-0.81789, -0.13103)
loop_1 = loop_1.lineTo(-0.81789, 0.14463)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_56_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_56_interval_1.stl')
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.3589, -0.77311, 0.01882), normal=(0.5598, -0.82863, 0.00049), xDir=(-0.82863, -0.5598, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.39612, 0.14775)
loop_1 = loop_1.threePointArc((-0.39591, 0.12531), (-0.39523, 0.10378))
loop_1 = loop_1.threePointArc((-0.39357, 0.07951), (-0.39219, 0.05949))
loop_1 = loop_1.threePointArc((-0.39282, 0.03136), (-0.3931, 0.00777))
loop_1 = loop_1.threePointArc((-0.39254, -0.0315), (-0.39306, -0.06869))
loop_1 = loop_1.lineTo(-0.39428, -0.08494)
loop_1 = loop_1.lineTo(-0.37271, -0.12955)
loop_1 = loop_1.lineTo(-0.31718, -0.14794)
loop_1 = loop_1.lineTo(-0.39669, -0.14794)
loop_1 = loop_1.lineTo(-0.39618, 0.14421)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_15_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_15_interval_0.stl')
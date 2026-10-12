import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.18653, -0.09013, 0.36162), normal=(0.06723, 0.02988, 0.99729), xDir=(0.0, 0.99955, -0.02995))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.18085, -0.23775)
loop_1 = loop_1.lineTo(0.18128, -0.45788)
loop_1 = loop_1.lineTo(-0.00194, -0.3853)
loop_1 = loop_1.lineTo(-0.00202, -0.36794)
loop_1 = loop_1.threePointArc((0.0055, -0.36153), (0.0117, -0.35699))
loop_1 = loop_1.threePointArc((0.01948, -0.35074), (0.02535, -0.34625))
loop_1 = loop_1.lineTo(0.05633, -0.32462)
loop_1 = loop_1.threePointArc((0.06827, -0.31665), (0.07677, -0.31074))
loop_1 = loop_1.threePointArc((0.08667, -0.30432), (0.09393, -0.29935))
loop_1 = loop_1.lineTo(0.11232, -0.28435)
loop_1 = loop_1.threePointArc((0.11887, -0.27921), (0.12584, -0.27405))
loop_1 = loop_1.lineTo(0.13659, -0.26496)
loop_1 = loop_1.threePointArc((0.1466, -0.25821), (0.15367, -0.2534))
loop_1 = loop_1.lineTo(0.16879, -0.24566)
loop_1 = loop_1.lineTo(0.18085, -0.23775)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.23)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_5_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_5_interval_1.stl')
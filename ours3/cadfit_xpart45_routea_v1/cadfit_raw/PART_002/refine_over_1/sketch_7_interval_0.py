import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.26, 0.008, 0.07767), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.30688, -0.42823)
loop_1 = loop_1.lineTo(-0.30688, -0.73233)
loop_1 = loop_1.lineTo(-0.15791, -0.73233)
loop_1 = loop_1.lineTo(-0.12399, -0.75171)
loop_1 = loop_1.threePointArc((-0.10147, -0.76262), (-0.08327, -0.77105))
loop_1 = loop_1.threePointArc((-0.04797, -0.78577), (-0.0172, -0.79921))
loop_1 = loop_1.lineTo(-0.15954, -0.73122)
loop_1 = loop_1.lineTo(-0.17035, -0.72039)
loop_1 = loop_1.lineTo(-0.19364, -0.68983)
loop_1 = loop_1.lineTo(-0.21762, -0.65112)
loop_1 = loop_1.lineTo(-0.2315, -0.63134)
loop_1 = loop_1.lineTo(-0.24175, -0.61781)
loop_1 = loop_1.lineTo(-0.26835, -0.58226)
loop_1 = loop_1.lineTo(-0.28548, -0.54007)
loop_1 = loop_1.lineTo(-0.29376, -0.50305)
loop_1 = loop_1.lineTo(-0.29827, -0.46603)
loop_1 = loop_1.threePointArc((-0.30207, -0.44469), (-0.3049, -0.42901))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.61)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_7_interval_0.stl')
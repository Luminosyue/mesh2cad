import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.73755, 0.58058, 0.03503), normal=(0.95468, -0.29759, 0.00451), xDir=(-0.29759, -0.95469, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.54807, -0.1325)
loop_1 = loop_1.lineTo(0.52263, 0.1893)
loop_1 = loop_1.lineTo(0.52443, 0.16568)
loop_1 = loop_1.lineTo(0.52666, 0.11015)
loop_1 = loop_1.threePointArc((0.52747, 0.08592), (0.52857, 0.06585))
loop_1 = loop_1.threePointArc((0.53079, 0.04174), (0.53247, 0.02043))
loop_1 = loop_1.lineTo(0.53359, 0.00163)
loop_1 = loop_1.threePointArc((0.5341, -0.01648), (0.53374, -0.03172))
loop_1 = loop_1.lineTo(0.53195, -0.04997)
loop_1 = loop_1.lineTo(0.52957, -0.06309)
loop_1 = loop_1.lineTo(0.52871, -0.08598)
loop_1 = loop_1.lineTo(0.53401, -0.10323)
loop_1 = loop_1.lineTo(0.54374, -0.12267)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.67)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_5_interval_0.stl')
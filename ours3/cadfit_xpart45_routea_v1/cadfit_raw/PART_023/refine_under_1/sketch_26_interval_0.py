import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.69857, -0.77763, -0.073), normal=(0.91096, 0.4125, -4e-05), xDir=(0.4125, -0.91096, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.07536, 0.72101)
loop_1 = loop_1.lineTo(0.0938, 0.72047)
loop_1 = loop_1.lineTo(0.11782, 0.7151)
loop_1 = loop_1.lineTo(0.13716, 0.69649)
loop_1 = loop_1.lineTo(0.14522, 0.684)
loop_1 = loop_1.lineTo(0.14783, 0.65772)
loop_1 = loop_1.lineTo(0.13716, 0.6381)
loop_1 = loop_1.lineTo(0.12407, 0.6246)
loop_1 = loop_1.lineTo(0.09325, 0.61511)
loop_1 = loop_1.lineTo(0.08318, 0.61814)
loop_1 = loop_1.lineTo(0.06561, 0.61964)
loop_1 = loop_1.lineTo(0.05408, 0.62605)
loop_1 = loop_1.lineTo(0.03864, 0.64525)
loop_1 = loop_1.lineTo(0.03183, 0.65942)
loop_1 = loop_1.lineTo(0.03284, 0.68384)
loop_1 = loop_1.lineTo(0.04866, 0.70986)
loop_1 = loop_1.threePointArc((0.06474, 0.71765), (0.07374, 0.72049))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_26_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_26_interval_0.stl')
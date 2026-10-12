import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.01992, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.96821, 0.01836)
loop_1 = loop_1.threePointArc((0.96606, 0.00804), (0.9621, -0.00219))
loop_1 = loop_1.lineTo(0.94337, -0.01436)
loop_1 = loop_1.threePointArc((0.92044, -0.01803), (0.89707, -0.01987))
loop_1 = loop_1.lineTo(0.82737, -0.02512)
loop_1 = loop_1.threePointArc((0.71699, -0.03427), (0.61176, -0.044))
loop_1 = loop_1.threePointArc((0.5214, -0.04948), (0.42793, -0.054))
loop_1 = loop_1.lineTo(0.21607, -0.06589)
loop_1 = loop_1.lineTo(0.03434, -0.07719)
loop_1 = loop_1.lineTo(0.00569, -0.0799)
loop_1 = loop_1.lineTo(0.97, -0.07782)
loop_1 = loop_1.lineTo(0.96925, 0.01834)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.53)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_65_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_65_interval_0.stl')
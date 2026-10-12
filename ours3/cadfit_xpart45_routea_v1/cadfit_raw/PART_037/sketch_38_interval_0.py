import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.01), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.0871, 0.58888)
loop_1 = loop_1.threePointArc((-0.08691, 0.58316), (-0.08658, 0.57768))
loop_1 = loop_1.lineTo(-0.08248, 0.56535)
loop_1 = loop_1.lineTo(-0.06765, 0.54753)
loop_1 = loop_1.lineTo(-0.0524, 0.5412)
loop_1 = loop_1.threePointArc((-0.04545, 0.54115), (-0.03878, 0.54126))
loop_1 = loop_1.lineTo(-0.00691, 0.56195)
loop_1 = loop_1.lineTo(0.00366, 0.58946)
loop_1 = loop_1.lineTo(0.00569, 0.60281)
loop_1 = loop_1.lineTo(0.00255, 0.6156)
loop_1 = loop_1.threePointArc((-0.00735, 0.62529), (-0.0106, 0.62878))
loop_1 = loop_1.threePointArc((-0.01638, 0.63172), (-0.02115, 0.63382))
loop_1 = loop_1.threePointArc((-0.0311, 0.63659), (-0.03621, 0.63717))
loop_1 = loop_1.threePointArc((-0.04434, 0.6369), (-0.049, 0.63602))
loop_1 = loop_1.lineTo(-0.06273, 0.63037)
loop_1 = loop_1.lineTo(-0.07692, 0.61572)
loop_1 = loop_1.lineTo(-0.0871, 0.58888)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_38_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_38_interval_0.stl')
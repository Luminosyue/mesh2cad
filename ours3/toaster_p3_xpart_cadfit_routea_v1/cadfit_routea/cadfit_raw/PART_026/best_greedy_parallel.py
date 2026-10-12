import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.99, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.00964, 0.03414)
loop_1 = loop_1.lineTo(0.02835, 0.0222)
loop_1 = loop_1.lineTo(0.03864, -0.00608)
loop_1 = loop_1.threePointArc((0.03336, -0.02007), (0.02992, -0.02481))
loop_1 = loop_1.threePointArc((0.02204, -0.03059), (0.01853, -0.03312))
loop_1 = loop_1.lineTo(-0.00987, -0.03422)
loop_1 = loop_1.lineTo(-0.02705, -0.02402)
loop_1 = loop_1.threePointArc((-0.0343, -0.01894), (-0.03774, -0.01679))
loop_1 = loop_1.threePointArc((-0.04598, -0.01845), (-0.05369, -0.0204))
loop_1 = loop_1.threePointArc((-0.06124, -0.02034), (-0.06591, -0.01961))
loop_1 = loop_1.lineTo(-0.06567, -0.00578)
loop_1 = loop_1.threePointArc((-0.05329, -0.00381), (-0.05043, -0.00423))
loop_1 = loop_1.lineTo(-0.03757, -0.00539)
loop_1 = loop_1.threePointArc((-0.03024, 0.00851), (-0.02891, 0.01328))
loop_1 = loop_1.threePointArc((-0.02149, 0.0252), (-0.01866, 0.02787))
loop_1 = loop_1.threePointArc((-0.00929, 0.03298), (-0.00778, 0.03338))
loop_1 = loop_1.lineTo(0.00964, 0.03414)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.98)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/toaster_p3_xpart_cadfit_routea_v1/cadfit_routea/cadfit_raw/PART_026/sketch_26_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/toaster_p3_xpart_cadfit_routea_v1/cadfit_routea/cadfit_raw/PART_026/sketch_26_interval_0.stl')
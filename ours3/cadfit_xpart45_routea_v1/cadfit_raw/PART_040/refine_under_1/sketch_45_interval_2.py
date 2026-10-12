import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.1323, -0.38898, -0.0081), normal=(0.8591, -0.51181, -0.00051), xDir=(-0.51181, -0.8591, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.16071, 0.09333)
loop_1 = loop_1.threePointArc((-0.1617, 0.0852), (-0.16283, 0.07673))
loop_1 = loop_1.threePointArc((-0.16263, 0.05213), (-0.16289, 0.03636))
loop_1 = loop_1.threePointArc((-0.16317, 0.01416), (-0.16377, -0.00645))
loop_1 = loop_1.lineTo(-0.16409, -0.02709)
loop_1 = loop_1.lineTo(-0.16359, -0.03976)
loop_1 = loop_1.lineTo(-0.16396, -0.06437)
loop_1 = loop_1.lineTo(-0.16443, -0.07504)
loop_1 = loop_1.lineTo(-0.1641, -0.09784)
loop_1 = loop_1.lineTo(-0.16343, -0.10862)
loop_1 = loop_1.threePointArc((-0.16256, -0.11567), (-0.16174, -0.12301))
loop_1 = loop_1.lineTo(-0.15846, 0.09676)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.36)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_45_interval_2.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_45_interval_2.stl')
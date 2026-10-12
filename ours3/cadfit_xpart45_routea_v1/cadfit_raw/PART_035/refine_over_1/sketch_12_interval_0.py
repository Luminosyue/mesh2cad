import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.51828, 0.11466, -0.00272), normal=(-0.64804, 0.76146, 0.0152), xDir=(0.76154, 0.64811, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.23464, -0.15333)
loop_1 = loop_1.lineTo(-0.23369, 0.11471)
loop_1 = loop_1.lineTo(-0.2339, 0.10385)
loop_1 = loop_1.threePointArc((-0.23492, 0.08793), (-0.2362, 0.07453))
loop_1 = loop_1.threePointArc((-0.23772, 0.05836), (-0.23963, 0.04483))
loop_1 = loop_1.lineTo(-0.24149, 0.02886)
loop_1 = loop_1.threePointArc((-0.2438, 0.00791), (-0.24625, -0.01055))
loop_1 = loop_1.threePointArc((-0.24695, -0.02338), (-0.24771, -0.03343))
loop_1 = loop_1.threePointArc((-0.24701, -0.04618), (-0.24671, -0.05631))
loop_1 = loop_1.lineTo(-0.24392, -0.08464)
loop_1 = loop_1.lineTo(-0.23643, -0.15012)
loop_1 = loop_1.lineTo(-0.23461, -0.16173)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.35)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_12_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_12_interval_0.stl')
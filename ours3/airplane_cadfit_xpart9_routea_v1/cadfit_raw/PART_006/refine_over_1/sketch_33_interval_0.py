import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.80962, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.74634, 0.08815)
loop_1 = loop_1.lineTo(-0.74599, 0.01492)
loop_1 = loop_1.lineTo(-0.59364, 0.01524)
loop_1 = loop_1.threePointArc((-0.61164, 0.01983), (-0.63013, 0.0249))
loop_1 = loop_1.lineTo(-0.66338, 0.03406)
loop_1 = loop_1.threePointArc((-0.67295, 0.03717), (-0.68204, 0.0399))
loop_1 = loop_1.threePointArc((-0.69151, 0.04403), (-0.70058, 0.04756))
loop_1 = loop_1.threePointArc((-0.71247, 0.05582), (-0.72156, 0.06258))
loop_1 = loop_1.lineTo(-0.7506, 0.14157)
loop_1 = loop_1.lineTo(-0.75724, 0.08959)
loop_1 = loop_1.lineTo(-0.74651, 0.08818)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.54)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_33_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_33_interval_0.stl')
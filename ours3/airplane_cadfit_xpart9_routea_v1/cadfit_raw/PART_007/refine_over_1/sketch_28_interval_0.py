import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.78229, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.90806, -0.06393)
loop_1 = loop_1.threePointArc((0.89847, -0.07256), (0.89528, -0.07633))
loop_1 = loop_1.threePointArc((0.88848, -0.08185), (0.88144, -0.0873))
loop_1 = loop_1.lineTo(0.86044, -0.09595)
loop_1 = loop_1.threePointArc((0.85016, -0.09699), (0.84054, -0.09844))
loop_1 = loop_1.threePointArc((0.82771, -0.09884), (0.81561, -0.09965))
loop_1 = loop_1.threePointArc((0.80201, -0.09996), (0.78804, -0.09996))
loop_1 = loop_1.threePointArc((0.77038, -0.10049), (0.75217, -0.10042))
loop_1 = loop_1.threePointArc((0.73737, -0.10076), (0.72216, -0.10071))
loop_1 = loop_1.threePointArc((0.707, -0.10086), (0.69142, -0.10057))
loop_1 = loop_1.threePointArc((0.67369, -0.10069), (0.65542, -0.10049))
loop_1 = loop_1.lineTo(0.9049, -0.11254)
loop_1 = loop_1.lineTo(0.90805, -0.06412)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.43)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_28_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_28_interval_0.stl')
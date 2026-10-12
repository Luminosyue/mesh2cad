import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.04301, 0.2608, -0.03774), normal=(0.1889, 0.58283, 0.79033), xDir=(0.95128, -0.30832, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.70548, -0.61061)
loop_1 = loop_1.lineTo(-0.45729, -0.5356)
loop_1 = loop_1.lineTo(-0.4694, -0.54038)
loop_1 = loop_1.threePointArc((-0.49918, -0.55127), (-0.53048, -0.56179))
loop_1 = loop_1.threePointArc((-0.55004, -0.56843), (-0.56698, -0.57436))
loop_1 = loop_1.threePointArc((-0.58543, -0.58052), (-0.60052, -0.58612))
loop_1 = loop_1.threePointArc((-0.61689, -0.59302), (-0.63183, -0.59911))
loop_1 = loop_1.threePointArc((-0.64969, -0.60468), (-0.66612, -0.60956))
loop_1 = loop_1.lineTo(-0.70255, -0.61168)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_0_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_0_interval_1.stl')
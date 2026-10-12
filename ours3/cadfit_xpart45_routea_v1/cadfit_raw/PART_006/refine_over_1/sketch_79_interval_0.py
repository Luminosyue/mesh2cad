import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.52271), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.00748, 0.99605)
loop_1 = loop_1.threePointArc((0.01389, 0.99578), (0.02053, 0.99505))
loop_1 = loop_1.threePointArc((0.03591, 0.99282), (0.05047, 0.99127))
loop_1 = loop_1.lineTo(0.07195, 0.98846)
loop_1 = loop_1.threePointArc((0.0945, 0.98336), (0.11758, 0.97768))
loop_1 = loop_1.lineTo(0.18922, 0.96)
loop_1 = loop_1.threePointArc((0.23621, 0.94671), (0.28476, 0.93259))
loop_1 = loop_1.lineTo(0.33209, 0.91553)
loop_1 = loop_1.lineTo(0.3858, 0.89128)
loop_1 = loop_1.lineTo(0.38941, 0.99614)
loop_1 = loop_1.lineTo(0.00778, 0.99614)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_79_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_79_interval_0.stl')
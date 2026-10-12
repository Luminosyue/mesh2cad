import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.10001, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.06808, 0.83967)
loop_1 = loop_1.threePointArc((0.06918, 0.83036), (0.07074, 0.82149))
loop_1 = loop_1.lineTo(0.07161, 0.81115)
loop_1 = loop_1.lineTo(0.07803, 0.79113)
loop_1 = loop_1.lineTo(0.08794, 0.77054)
loop_1 = loop_1.lineTo(0.09801, 0.75641)
loop_1 = loop_1.threePointArc((0.10096, 0.74437), (0.1007, 0.73783))
loop_1 = loop_1.threePointArc((0.10021, 0.72798), (0.10049, 0.72637))
loop_1 = loop_1.lineTo(0.10296, 0.71009)
loop_1 = loop_1.lineTo(0.10217, 0.68957)
loop_1 = loop_1.lineTo(0.1001, 0.66956)
loop_1 = loop_1.lineTo(0.08837, 0.64964)
loop_1 = loop_1.lineTo(0.07649, 0.63935)
loop_1 = loop_1.lineTo(0.06051, 0.61468)
loop_1 = loop_1.lineTo(0.06051, 0.83984)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_34_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_34_interval_0.stl')
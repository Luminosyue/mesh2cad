import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.5118, 0.10705, -0.00287), normal=(-0.64804, 0.76146, 0.0152), xDir=(0.76154, 0.64811, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.24185, 0.02568)
loop_1 = loop_1.threePointArc((-0.2438, 0.00791), (-0.24625, -0.01055))
loop_1 = loop_1.lineTo(-0.24743, -0.0385)
loop_1 = loop_1.lineTo(-0.24689, -0.04866)
loop_1 = loop_1.lineTo(-0.24627, -0.06075)
loop_1 = loop_1.lineTo(-0.24405, -0.08355)
loop_1 = loop_1.lineTo(-0.23679, -0.14782)
loop_1 = loop_1.lineTo(-0.23461, -0.16173)
loop_1 = loop_1.lineTo(-0.23526, 0.04297)
loop_1 = loop_1.lineTo(-0.23371, -0.16759)
loop_1 = loop_1.lineTo(-0.23463, 0.0914)
loop_1 = loop_1.lineTo(-0.23771, 0.05809)
loop_1 = loop_1.lineTo(-0.24082, 0.03521)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.36)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_0_interval_0.stl')
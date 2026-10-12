import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.36898, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.94007, -0.09316)
loop_1 = loop_1.lineTo(-0.47123, -0.09628)
loop_1 = loop_1.threePointArc((-0.33657, -0.09111), (-0.20767, -0.08443))
loop_1 = loop_1.lineTo(-0.06623, -0.07602)
loop_1 = loop_1.lineTo(-0.00065, -0.07188)
loop_1 = loop_1.lineTo(-0.94, -0.07448)
loop_1 = loop_1.lineTo(-0.94, -0.09255)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.68)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_62_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_62_interval_0.stl')
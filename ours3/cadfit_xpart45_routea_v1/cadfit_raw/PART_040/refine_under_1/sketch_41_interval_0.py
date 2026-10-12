import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43934, -0.07338, 0.23363), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.39058, 0.18183)
loop_1 = loop_1.lineTo(-0.40996, 0.16921)
loop_1 = loop_1.lineTo(-0.42941, 0.17056)
loop_1 = loop_1.lineTo(-0.44605, 0.18472)
loop_1 = loop_1.lineTo(-0.44916, 0.20528)
loop_1 = loop_1.lineTo(-0.42816, 0.22254)
loop_1 = loop_1.lineTo(-0.41277, 0.22334)
loop_1 = loop_1.lineTo(-0.39499, 0.21304)
loop_1 = loop_1.lineTo(-0.39058, 0.18183)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_41_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_41_interval_0.stl')
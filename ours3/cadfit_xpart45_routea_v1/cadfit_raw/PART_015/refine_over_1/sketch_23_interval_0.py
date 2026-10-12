import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.45356, -0.75944, -0.0287), normal=(0.65793, 0.75308, -0.00279), xDir=(0.75308, -0.65793, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.1346, -0.23505)
loop_1 = loop_1.lineTo(-0.12154, -0.23598)
loop_1 = loop_1.lineTo(-0.05551, -0.23583)
loop_1 = loop_1.lineTo(-0.09034, -0.25978)
loop_1 = loop_1.lineTo(-0.11644, -0.27746)
loop_1 = loop_1.lineTo(-0.13471, -0.2801)
loop_1 = loop_1.lineTo(-0.13461, -0.23613)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.74)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_23_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_23_interval_0.stl')
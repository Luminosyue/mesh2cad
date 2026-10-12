import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.92797, -0.08705, -0.1616), normal=(0.99926, -0.00418, -0.0382), xDir=(-0.00418, -0.99999, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.08859, -0.09254)
loop_1 = loop_1.lineTo(-0.12989, -0.12815)
loop_1 = loop_1.lineTo(-0.07099, -0.12815)
loop_1 = loop_1.lineTo(-0.07085, -0.11317)
loop_1 = loop_1.lineTo(-0.08808, -0.09314)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_17_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_17_interval_1.stl')
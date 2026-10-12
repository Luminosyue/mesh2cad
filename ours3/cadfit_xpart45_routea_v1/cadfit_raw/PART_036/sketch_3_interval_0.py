import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.17406, -0.19089, -0.15472), normal=(-0.02357, 0.65303, -0.75696), xDir=(0.99935, 0.03607, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.78803, -0.25933)
loop_1 = loop_1.threePointArc((0.7938, -0.26373), (0.79979, -0.26832))
loop_1 = loop_1.lineTo(0.8215, -0.30454)
loop_1 = loop_1.threePointArc((0.82336, -0.31327), (0.82516, -0.32164))
loop_1 = loop_1.lineTo(0.82406, -0.34831)
loop_1 = loop_1.lineTo(0.80851, -0.37284)
loop_1 = loop_1.lineTo(0.78805, -0.37832)
loop_1 = loop_1.lineTo(0.77478, -0.36233)
loop_1 = loop_1.lineTo(0.76811, -0.34692)
loop_1 = loop_1.lineTo(0.76451, -0.32887)
loop_1 = loop_1.threePointArc((0.76409, -0.31643), (0.76361, -0.30588))
loop_1 = loop_1.lineTo(0.7664, -0.29498)
loop_1 = loop_1.threePointArc((0.76718, -0.2882), (0.76783, -0.28265))
loop_1 = loop_1.lineTo(0.78803, -0.25933)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.25)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_3_interval_0.stl')
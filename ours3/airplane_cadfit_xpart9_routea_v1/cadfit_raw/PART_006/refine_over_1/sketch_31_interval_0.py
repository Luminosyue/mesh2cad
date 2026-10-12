import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.78949, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.74366, 0.08537)
loop_1 = loop_1.lineTo(-0.7435, 0.01492)
loop_1 = loop_1.lineTo(-0.68342, 0.01508)
loop_1 = loop_1.threePointArc((-0.69267, 0.01936), (-0.70155, 0.02332))
loop_1 = loop_1.lineTo(-0.71529, 0.03521)
loop_1 = loop_1.lineTo(-0.72673, 0.04733)
loop_1 = loop_1.threePointArc((-0.73334, 0.05754), (-0.73981, 0.06725))
loop_1 = loop_1.threePointArc((-0.74119, 0.07319), (-0.74232, 0.07933))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.52)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_31_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_31_interval_0.stl')
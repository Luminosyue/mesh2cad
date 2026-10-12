import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.36898, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.93848, -0.11202)
loop_1 = loop_1.threePointArc((-0.92316, -0.11358), (-0.90839, -0.11407))
loop_1 = loop_1.threePointArc((-0.89381, -0.11346), (-0.88085, -0.11228))
loop_1 = loop_1.lineTo(-0.84028, -0.11149)
loop_1 = loop_1.lineTo(-0.64223, -0.10451)
loop_1 = loop_1.threePointArc((-0.62169, -0.10389), (-0.60294, -0.10253))
loop_1 = loop_1.lineTo(-0.2264, -0.0856)
loop_1 = loop_1.threePointArc((-0.20776, -0.08426), (-0.18934, -0.08378))
loop_1 = loop_1.lineTo(-0.02968, -0.07387)
loop_1 = loop_1.lineTo(-0.00119, -0.07188)
loop_1 = loop_1.lineTo(-0.89918, -0.0727)
loop_1 = loop_1.lineTo(-0.33225, -0.0852)
loop_1 = loop_1.lineTo(-0.45311, -0.08689)
loop_1 = loop_1.lineTo(-0.94, -0.09324)
loop_1 = loop_1.lineTo(-0.93998, -0.11168)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.69)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_63_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_63_interval_0.stl')
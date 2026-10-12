import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.06905), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.2405, -0.54098)
loop_1 = loop_1.lineTo(-0.2073, -0.62765)
loop_1 = loop_1.lineTo(-0.17423, -0.70403)
loop_1 = loop_1.lineTo(-0.17826, -0.68667)
loop_1 = loop_1.lineTo(-0.184, -0.67663)
loop_1 = loop_1.lineTo(-0.18904, -0.65636)
loop_1 = loop_1.lineTo(-0.1967, -0.63615)
loop_1 = loop_1.lineTo(-0.20438, -0.61785)
loop_1 = loop_1.threePointArc((-0.20844, -0.59943), (-0.21146, -0.5832))
loop_1 = loop_1.threePointArc((-0.2179, -0.55645), (-0.22118, -0.53617))
loop_1 = loop_1.lineTo(-0.22376, -0.51542)
loop_1 = loop_1.lineTo(-0.24045, -0.54085)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_42_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_42_interval_0.stl')
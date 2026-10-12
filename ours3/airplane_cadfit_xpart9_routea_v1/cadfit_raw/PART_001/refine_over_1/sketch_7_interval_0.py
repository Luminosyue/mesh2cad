import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.40086, -0.33817, 0.12248), normal=(5e-05, -0.71751, 0.69654), xDir=(-1.0, -8e-05, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.57073, 0.06043)
loop_1 = loop_1.lineTo(-0.9859, 0.05999)
loop_1 = loop_1.threePointArc((-0.94038, 0.05784), (-0.89726, 0.05645))
loop_1 = loop_1.threePointArc((-0.83064, 0.05422), (-0.76971, 0.05292))
loop_1 = loop_1.lineTo(-0.73018, 0.05154)
loop_1 = loop_1.lineTo(-0.71586, 0.05119)
loop_1 = loop_1.threePointArc((-0.691, 0.05038), (-0.66514, 0.04896))
loop_1 = loop_1.lineTo(-0.63539, 0.04857)
loop_1 = loop_1.lineTo(-0.60356, 0.04801)
loop_1 = loop_1.threePointArc((-0.58335, 0.04791), (-0.56556, 0.04661))
loop_1 = loop_1.lineTo(-0.54445, 0.04708)
loop_1 = loop_1.lineTo(-0.57073, 0.06043)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_7_interval_0.stl')
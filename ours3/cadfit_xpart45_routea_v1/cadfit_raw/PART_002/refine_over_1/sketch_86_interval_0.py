import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.7708), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.39631, -0.0054)
loop_1 = loop_1.lineTo(-0.39576, -0.26)
loop_1 = loop_1.lineTo(-0.35707, -0.25982)
loop_1 = loop_1.lineTo(-0.36023, -0.2493)
loop_1 = loop_1.threePointArc((-0.36216, -0.24102), (-0.36446, -0.23336))
loop_1 = loop_1.lineTo(-0.37047, -0.21189)
loop_1 = loop_1.lineTo(-0.3779, -0.17341)
loop_1 = loop_1.lineTo(-0.38378, -0.13731)
loop_1 = loop_1.threePointArc((-0.38598, -0.11971), (-0.38833, -0.10303))
loop_1 = loop_1.threePointArc((-0.3896, -0.08977), (-0.39056, -0.07612))
loop_1 = loop_1.lineTo(-0.39381, -0.03833)
loop_1 = loop_1.threePointArc((-0.39505, -0.02153), (-0.39631, -0.00558))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.73)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_86_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_86_interval_0.stl')
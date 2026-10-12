import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.5578, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.82141, 0.09912)
loop_1 = loop_1.lineTo(-0.79451, 0.043)
loop_1 = loop_1.threePointArc((-0.78354, 0.02815), (-0.77255, 0.01448))
loop_1 = loop_1.lineTo(-0.75452, -0.00853)
loop_1 = loop_1.lineTo(-0.74518, -0.05666)
loop_1 = loop_1.lineTo(-0.782, -0.07811)
loop_1 = loop_1.lineTo(-0.81948, -0.11238)
loop_1 = loop_1.threePointArc((-0.82035, -0.11952), (-0.82138, -0.12676))
loop_1 = loop_1.lineTo(-0.82146, 0.09894)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_77_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_77_interval_0.stl')
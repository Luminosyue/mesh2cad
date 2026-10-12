import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.55896, 0.06532, -0.51654), normal=(-0.79983, -0.01226, 0.6001), xDir=(-0.01533, 0.99988, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.31606, -0.37954)
loop_1 = loop_1.lineTo(-0.58801, -0.3928)
loop_1 = loop_1.lineTo(-0.59933, -0.392)
loop_1 = loop_1.lineTo(-0.24423, -0.29064)
loop_1 = loop_1.lineTo(-0.26431, -0.32883)
loop_1 = loop_1.lineTo(-0.27314, -0.34105)
loop_1 = loop_1.threePointArc((-0.28536, -0.35345), (-0.29702, -0.36541))
loop_1 = loop_1.lineTo(-0.31606, -0.37954)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_24_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_24_interval_0.stl')
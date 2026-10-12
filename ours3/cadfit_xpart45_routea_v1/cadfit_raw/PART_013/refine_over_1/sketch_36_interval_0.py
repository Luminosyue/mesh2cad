import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.05396, -0.02065, -0.18457), normal=(0.00848, -0.04584, 0.99891), xDir=(-0.0, 0.99895, 0.04584))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.81837, 0.52762)
loop_1 = loop_1.lineTo(-0.82374, 0.51562)
loop_1 = loop_1.lineTo(-0.9558, 0.12945)
loop_1 = loop_1.lineTo(-0.95728, 0.15392)
loop_1 = loop_1.lineTo(-0.95508, 0.17346)
loop_1 = loop_1.lineTo(-0.94939, 0.20637)
loop_1 = loop_1.lineTo(-0.94218, 0.23899)
loop_1 = loop_1.lineTo(-0.93252, 0.2742)
loop_1 = loop_1.lineTo(-0.92328, 0.30306)
loop_1 = loop_1.threePointArc((-0.90926, 0.34093), (-0.89818, 0.37188))
loop_1 = loop_1.lineTo(-0.88157, 0.41181)
loop_1 = loop_1.lineTo(-0.86629, 0.44466)
loop_1 = loop_1.lineTo(-0.84767, 0.48035)
loop_1 = loop_1.lineTo(-0.83381, 0.50397)
loop_1 = loop_1.lineTo(-0.82054, 0.5244)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.49)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_36_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_36_interval_0.stl')
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.37919, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.37821, 0.8)
loop_1 = loop_1.lineTo(0.26494, 0.79911)
loop_1 = loop_1.lineTo(0.27718, 0.78151)
loop_1 = loop_1.lineTo(0.31606, 0.77444)
loop_1 = loop_1.lineTo(0.34685, 0.76559)
loop_1 = loop_1.threePointArc((0.3605, 0.74031), (0.36608, 0.72234))
loop_1 = loop_1.lineTo(0.37117, 0.5868)
loop_1 = loop_1.threePointArc((0.37487, 0.43987), (0.37526, 0.28765))
loop_1 = loop_1.threePointArc((0.37666, 0.10024), (0.37616, -0.0941))
loop_1 = loop_1.lineTo(0.37786, -0.35734)
loop_1 = loop_1.lineTo(0.37821, 0.79914)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.51)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_24_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_24_interval_0.stl')
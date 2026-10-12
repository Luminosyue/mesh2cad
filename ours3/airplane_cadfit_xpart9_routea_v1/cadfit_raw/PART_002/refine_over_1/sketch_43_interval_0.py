import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.17039, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.16551, 0.22429)
loop_1 = loop_1.threePointArc((-0.12753, 0.21114), (-0.09081, 0.19928))
loop_1 = loop_1.lineTo(-0.07398, 0.19503)
loop_1 = loop_1.lineTo(-0.07398, 0.20539)
loop_1 = loop_1.lineTo(-0.10455, 0.20577)
loop_1 = loop_1.lineTo(0.25965, 0.34448)
loop_1 = loop_1.threePointArc((0.19737, 0.33976), (0.13796, 0.33485))
loop_1 = loop_1.threePointArc((0.12328, 0.33426), (0.10836, 0.33402))
loop_1 = loop_1.threePointArc((0.06849, 0.32878), (0.03159, 0.31879))
loop_1 = loop_1.threePointArc((0.01958, 0.31468), (0.00901, 0.30937))
loop_1 = loop_1.threePointArc((-0.02975, 0.29618), (-0.07093, 0.28685))
loop_1 = loop_1.threePointArc((-0.09204, 0.28224), (-0.11182, 0.27732))
loop_1 = loop_1.threePointArc((-0.12648, 0.27256), (-0.14003, 0.26755))
loop_1 = loop_1.threePointArc((-0.15407, 0.26237), (-0.16703, 0.25623))
loop_1 = loop_1.lineTo(-0.20351, 0.24389)
loop_1 = loop_1.lineTo(-0.21507, 0.23362)
loop_1 = loop_1.threePointArc((-0.19574, 0.22997), (-0.17297, 0.22613))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_43_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_43_interval_0.stl')
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.77303), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.37724, 0.05221)
loop_1 = loop_1.lineTo(-0.37657, -0.26)
loop_1 = loop_1.lineTo(-0.3502, -0.2598)
loop_1 = loop_1.threePointArc((-0.35265, -0.24592), (-0.35464, -0.23158))
loop_1 = loop_1.threePointArc((-0.35678, -0.21891), (-0.35924, -0.20704))
loop_1 = loop_1.threePointArc((-0.3631, -0.18396), (-0.36672, -0.16009))
loop_1 = loop_1.threePointArc((-0.36944, -0.14474), (-0.37169, -0.12889))
loop_1 = loop_1.lineTo(-0.37389, -0.09834)
loop_1 = loop_1.lineTo(-0.37616, -0.06302)
loop_1 = loop_1.lineTo(-0.37689, -0.0187)
loop_1 = loop_1.threePointArc((-0.3769, 0.00656), (-0.37716, 0.0306))
loop_1 = loop_1.threePointArc((-0.37707, 0.04162), (-0.37723, 0.05199))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.75)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_97_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_97_interval_0.stl')
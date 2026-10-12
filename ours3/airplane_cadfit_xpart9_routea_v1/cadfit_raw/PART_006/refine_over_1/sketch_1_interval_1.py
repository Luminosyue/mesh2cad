import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.82448, 0.34587, -0.12469), normal=(0.97878, 0.18685, -0.08409), xDir=(0.18752, -0.98226, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.13848, 0.00464)
loop_1 = loop_1.lineTo(-0.26834, 0.03079)
loop_1 = loop_1.lineTo(-0.25034, 0.03378)
loop_1 = loop_1.lineTo(-0.23065, 0.03588)
loop_1 = loop_1.threePointArc((-0.20844, 0.037), (-0.18912, 0.03745))
loop_1 = loop_1.lineTo(-0.16783, 0.03688)
loop_1 = loop_1.threePointArc((-0.13936, 0.03435), (-0.11387, 0.03152))
loop_1 = loop_1.lineTo(-0.05733, 0.0248)
loop_1 = loop_1.threePointArc((-0.03893, 0.02249), (-0.025, 0.02115))
loop_1 = loop_1.threePointArc((0.01264, 0.01647), (0.04536, 0.01327))
loop_1 = loop_1.threePointArc((0.09336, 0.0085), (0.13575, 0.0049))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_1_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_1_interval_1.stl')
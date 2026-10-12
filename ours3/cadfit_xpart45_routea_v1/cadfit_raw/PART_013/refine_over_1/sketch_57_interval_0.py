import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.23028), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.99247, 0.13018)
loop_1 = loop_1.lineTo(-0.98939, 0.14416)
loop_1 = loop_1.threePointArc((-0.98497, 0.15755), (-0.98097, 0.17029))
loop_1 = loop_1.threePointArc((-0.97768, 0.18179), (-0.97409, 0.19353))
loop_1 = loop_1.threePointArc((-0.96612, 0.21707), (-0.95752, 0.24128))
loop_1 = loop_1.threePointArc((-0.95002, 0.26426), (-0.9417, 0.28783))
loop_1 = loop_1.threePointArc((-0.93034, 0.32134), (-0.91727, 0.35558))
loop_1 = loop_1.threePointArc((-0.91267, 0.36858), (-0.90762, 0.3818))
loop_1 = loop_1.lineTo(-0.90248, 0.39443)
loop_1 = loop_1.threePointArc((-0.90798, 0.38352), (-0.91276, 0.37301))
loop_1 = loop_1.lineTo(-0.92441, 0.34771)
loop_1 = loop_1.lineTo(-0.93949, 0.3105)
loop_1 = loop_1.threePointArc((-0.95152, 0.277), (-0.96436, 0.24242))
loop_1 = loop_1.lineTo(-0.97432, 0.21014)
loop_1 = loop_1.lineTo(-0.98287, 0.17778)
loop_1 = loop_1.lineTo(-0.98988, 0.14521)
loop_1 = loop_1.lineTo(-0.99244, 0.13036)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.5)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_57_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_57_interval_0.stl')
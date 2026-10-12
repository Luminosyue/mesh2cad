import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.03108, -0.07617, 0.82), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.32123, 0.24616)
loop_1 = loop_1.lineTo(-0.33067, 0.21892)
loop_1 = loop_1.lineTo(-0.39123, 0.21892)
loop_1 = loop_1.lineTo(-0.39123, -0.02884)
loop_1 = loop_1.threePointArc((-0.38698, -0.00529), (-0.38416, 0.00921))
loop_1 = loop_1.lineTo(-0.37564, 0.05134)
loop_1 = loop_1.lineTo(-0.36767, 0.09092)
loop_1 = loop_1.threePointArc((-0.35952, 0.12731), (-0.35085, 0.1624))
loop_1 = loop_1.threePointArc((-0.33724, 0.20008), (-0.32539, 0.2339))
loop_1 = loop_1.lineTo(-0.32123, 0.24616)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.6)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_39_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_39_interval_0.stl')
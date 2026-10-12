import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.98555, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.23973, -0.10238)
loop_1 = loop_1.lineTo(-0.23936, -0.16608)
loop_1 = loop_1.lineTo(-0.00674, -0.16567)
loop_1 = loop_1.lineTo(-0.03065, -0.15972)
loop_1 = loop_1.threePointArc((-0.04875, -0.15434), (-0.06604, -0.14956))
loop_1 = loop_1.threePointArc((-0.08652, -0.14342), (-0.10613, -0.13797))
loop_1 = loop_1.threePointArc((-0.12568, -0.13264), (-0.14576, -0.1268))
loop_1 = loop_1.threePointArc((-0.16144, -0.12159), (-0.17644, -0.117))
loop_1 = loop_1.lineTo(-0.2073, -0.10642)
loop_1 = loop_1.threePointArc((-0.22328, -0.10149), (-0.23968, -0.09617))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.96)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_56_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_56_interval_0.stl')
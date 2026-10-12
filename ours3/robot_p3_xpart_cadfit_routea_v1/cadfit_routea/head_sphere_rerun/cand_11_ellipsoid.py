import cadquery as cq
import math

rx, ry, rz = 0.95000000, 0.87136633, 0.70003941
wp = cq.Workplane('XZ')
wp = wp.moveTo(0, -rz)
wp = wp.ellipseArc(rx, rz, -90, 90)
wp = wp.close()
result = wp.revolve(360, (0, 0, 0), (0, 1, 0))
cq.exporters.export(result, r'/data/home/cuiyuehan/project/mesh2cad/ours3/robot_p3_xpart_cadfit_routea_v1/cadfit_routea/head_sphere_rerun/cand_11_ellipsoid.stl')
print('OK')

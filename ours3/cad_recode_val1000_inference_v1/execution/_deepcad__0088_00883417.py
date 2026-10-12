import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-36))
w1=cq.Workplane('XY',origin=(0,0,-33))
r=w0.sketch().push([(-52,-62.5)]).rect(68,75).reset().face(w0.sketch().segment((7,65),(10,65)).arc((57,21),(84,79)).segment((84,80)).segment((83,80)).arc((73,91),(60,98)).segment((60,100)).segment((48,100)).segment((48,98)).arc((35,95),(23,88)).segment((15,85)).segment((16,80)).segment((12,80)).close().assemble()).push([(50,59)]).circle(24,mode='s').finalize().extrude(73).union(w0.sketch().push([(-52,-62)]).circle(34).push([(-52,-62.5)]).rect(42,29,mode='s').finalize().extrude(73)).union(w1.sketch().arc((53,21),(87,60),(53,99)).close().assemble().finalize().extrude(50))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0088_00883417.step')

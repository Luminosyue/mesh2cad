import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,21))
r=w0.sketch().segment((-47,-100),(47,-100)).segment((47,-60)).segment((47,-18)).segment((47,100)).segment((-47,100)).segment((-47,60)).segment((-47,18)).close().assemble().reset().face(w0.sketch().segment((-47,-14),(-47,14)).arc((-48,0),(-47,-14)).assemble(),mode='s').reset().face(w0.sketch().arc((-47,-56),(0,-70),(47,-56)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-47,56),(47,56)).segment((47,59)).arc((44,60),(47,61)).segment((47,70)).arc((0,84),(-47,70)).close().assemble(),mode='s').reset().face(w0.sketch().arc((47,-14),(48,0),(47,14)).close().assemble(),mode='s').finalize().extrude(-42)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0031_00314830.step')

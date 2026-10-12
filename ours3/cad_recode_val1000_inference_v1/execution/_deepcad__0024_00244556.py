import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,37))
r=w0.sketch().segment((-100,-45),(-90,-45)).segment((-90,-35)).segment((-24,-35)).segment((-24,20)).segment((35,20)).segment((35,-35)).segment((100,-35)).segment((100,40)).segment((53,40)).segment((53,62)).segment((-90,63)).segment((-90,54)).segment((-100,54)).close().assemble().reset().face(w0.sketch().segment((-2,-63),(95,-62)).segment((95,-54)).segment((-2,-54)).close().assemble()).finalize().extrude(-75).union(w0.sketch().segment((-97,62),(-73,62)).segment((-73,-62)).segment((-46,-62)).segment((-46,62)).segment((97,62)).arc((0,62),(-97,62)).assemble().finalize().extrude(-59))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0024_00244556.step')

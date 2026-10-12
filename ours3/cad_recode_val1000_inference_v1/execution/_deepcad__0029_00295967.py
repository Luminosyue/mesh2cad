import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,96))
r=w0.sketch().segment((-47,44),(-17,20)).segment((-15,20)).segment((-46,43)).close().assemble().finalize().extrude(-200).union(w0.sketch().segment((-34,31),(-21,22)).segment((-20,24)).segment((-33,33)).close().assemble().finalize().extrude(-175)).union(w1.sketch().segment((-46,42),(-45,42)).arc((-45,41),(-44,41)).segment((-44,40)).segment((-43,40)).segment((-43,39)).segment((-44,39)).segment((-44,38)).segment((-45,38)).segment((-45,41)).close().assemble().finalize().extrude(-183))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0029_00295967.step')

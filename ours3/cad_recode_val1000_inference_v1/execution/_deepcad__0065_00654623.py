import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,12))
w1=cq.Workplane('ZX',origin=(0,8,0))
r=w0.sketch().segment((-95,-100),(1,-100)).segment((1,-33)).segment((-15,8)).segment((-35,8)).segment((-35,14)).segment((-54,8)).segment((-64,8)).segment((-64,2)).segment((-95,2)).close().assemble().finalize().extrude(-95).union(w0.sketch().segment((-81,-70),(-55,-95)).segment((70,35)).segment((44,60)).segment((29,45)).arc((24,51),(18,55)).segment((18,82)).segment((-15,82)).segment((-15,55)).arc((-20,51),(-25,45)).segment((-15,51)).segment((-15,34)).segment((-47,34)).segment((-47,-31)).segment((-46,-31)).segment((-46,-58)).segment((-47,-58)).segment((-47,-68)).segment((-80,-68)).close().assemble().finalize().extrude(15)).union(w0.sketch().segment((-47,-12),(-11,-45)).segment((55,31)).segment((6,70)).segment((-47,7)).close().assemble().reset().face(w0.sketch().segment((-48,91),(-47,91)).segment((-47,92)).segment((-45,92)).segment((-45,91)).segment((-33,91)).segment((-33,97)).segment((-48,97)).close().assemble()).push([(85,16)]).circle(9).finalize().extrude(71)).union(w1.workplane(offset=-108/2).moveTo(-43,-47).box(80,96,108))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0065_00654623.step')

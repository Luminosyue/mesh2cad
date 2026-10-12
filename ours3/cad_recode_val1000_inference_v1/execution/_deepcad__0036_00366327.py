import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,0,0))
r=w0.sketch().segment((-67,-100),(-41,-100)).segment((-41,-89)).segment((-22,-89)).segment((-22,20)).segment((-67,20)).segment((-67,-19)).segment((-51,-19)).segment((-51,-48)).segment((-67,-48)).close().assemble().finalize().extrude(-45).union(w0.workplane(offset=-45/2).moveTo(-58.5,26).box(17,14,45)).union(w0.sketch().segment((-45,2),(-44,2)).segment((-44,-33)).segment((-19,-33)).arc((-10,-34),(-1,-33)).segment((56,-33)).segment((56,-30)).segment((67,-30)).segment((67,11)).segment((36,11)).segment((36,55)).segment((67,55)).segment((67,100)).segment((27,100)).segment((27,99)).arc((32,96),(36,92)).segment((36,100)).segment((-44,100)).segment((-44,2)).arc((-45,3),(-45,4)).close().assemble().finalize().extrude(44))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0036_00366327.step')

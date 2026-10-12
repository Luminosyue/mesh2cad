import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-73,0))
r=w0.sketch().arc((16,-40),(20,-37),(24,-36)).arc((-19,38),(16,-40)).assemble().finalize().extrude(34).union(w0.sketch().arc((-21,-37),(-16,-39),(-11,-41)).arc((1,-43),(13,-41)).arc((14,-39),(16,-39)).arc((42,-7),(30,31)).arc((26,34),(22,36)).arc((20,37),(18,39)).arc((-39,17),(-21,-37)).assemble().finalize().extrude(200)).union(w1.sketch().arc((-23,-36),(-19,-38),(-15,-40)).arc((-18,-38),(-23,-36)).assemble().finalize().extrude(122))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0058_00585517.step')

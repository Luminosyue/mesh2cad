import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-38,0))
r=w0.sketch().arc((33,61),(-45,-49),(59,36)).arc((1,1),(33,61)).assemble().finalize().extrude(40).union(w0.sketch().arc((-69,-9),(-67,18),(-58,42)).arc((-68,18),(-69,-9)).assemble().reset().face(w0.sketch().arc((-9,68),(17,67),(40,56)).arc((18,67),(-9,68)).assemble()).finalize().extrude(176)).union(w1.sketch().arc((-49,-50),(-10,-70),(29,-64)).arc((26,-37),(51,-49)).arc((68,-17),(68,17)).arc((65,21),(63,26)).arc((57,39),(48,49)).arc((15,32),(-19,47)).arc((-24,45),(-29,42)).arc((6,-50),(-49,-50)).assemble().finalize().extrude(114))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0043_00430015.step')

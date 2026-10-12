import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-28,0))
w1=cq.Workplane('ZX',origin=(0,-25,0))
r=w0.sketch().segment((-98,29),(-61,11)).segment((-96,-19)).arc((-89,-44),(-74,-66)).arc((-55,-50),(-38,-69)).segment((-38,-71)).segment((-61,-71)).arc((-69,-69),(-75,-65)).arc((-81,-55),(-87,-45)).arc((-91,-37),(-94,-29)).arc((-95,-28),(-96,-27)).arc((-95,-28),(-93,-30)).close().assemble().reset().face(w0.sketch().segment((-96,24),(-1,-30)).segment((29,-30)).segment((29,-4)).segment((94,-4)).segment((94,2)).segment((29,2)).segment((29,11)).segment((-71,62)).segment((-71,70)).segment((-79,58)).segment((-79,57)).close().assemble()).finalize().extrude(56).union(w1.sketch().arc((-96,17),(-60,-18),(-61,-68)).arc((89,44),(-96,17)).assemble().push([(1,10)]).circle(25,mode='s').finalize().extrude(50))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0089_00894171.step')

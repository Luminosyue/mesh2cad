import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
w1=cq.Workplane('ZX',origin=(0,96,0))
r=w0.sketch().arc((-8,-34),(8,-36),(-8,-32)).arc((-7,-33),(-8,-34)).assemble().finalize().extrude(-162).union(w0.sketch().segment((-4,42),(1,30)).arc((4,30),(7,29)).segment((8,39)).close().assemble().reset().face(w0.sketch().arc((8,-29),(8,-30),(9,-30)).segment((8,-29)).close().assemble()).finalize().extrude(-16)).union(w1.workplane(offset=-196/2).moveTo(-1,-33).cylinder(196,8))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0053_00533110.step')

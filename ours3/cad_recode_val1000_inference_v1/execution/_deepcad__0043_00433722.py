import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(53,0,0))
w1=cq.Workplane('XY',origin=(0,0,-28))
r=w0.sketch().segment((-98,-28),(-62,-28)).segment((-62,-15)).segment((-35,-15)).segment((-35,-28)).segment((17,-28)).segment((17,-22)).arc((27,-13),(33,-2)).segment((17,-10)).segment((17,31)).arc((-1,24),(-14,10)).segment((-35,28)).segment((-35,31)).segment((-42,31)).segment((-43,31)).segment((-44,31)).segment((-98,31)).close().assemble().reset().face(w0.sketch().segment((-98,-31),(-97,-31)).arc((-96,-30),(-95,-30)).segment((-95,-28)).segment((-98,-28)).close().assemble()).finalize().extrude(-73).union(w0.sketch().segment((-100,-12),(-95,-12)).segment((-95,-30)).segment((-57,-30)).segment((-57,-12)).segment((-52,-12)).segment((-52,-7)).segment((-57,-7)).segment((-57,1)).arc((-44,27),(-72,26)).segment((-95,26)).segment((-95,-7)).segment((-100,-7)).close().assemble().push([(2.5,1)]).rect(61,52).finalize().extrude(2)).union(w0.workplane(offset=-84/2).moveTo(98.5,1).box(3,48,84)).union(w1.sketch().arc((-52,-41),(-18,-99),(1,-35)).arc((18,-35),(38,-36)).arc((20,16),(14,49)).arc((13,23),(18,-1)).arc((-1,-1),(-15,-12)).arc((-47,22),(-41,-24)).arc((-48,-31),(-52,-41)).assemble().finalize().extrude(-2))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0043_00433722.step')

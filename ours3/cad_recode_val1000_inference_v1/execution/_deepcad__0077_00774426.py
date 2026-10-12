import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,45))
r=w0.sketch().segment((-42,20),(-29,-10)).segment((-29,-2)).segment((-18,-2)).segment((-27,36)).arc((-33,28),(-42,20)).assemble().reset().face(w0.sketch().segment((-26,-26),(-24,-28)).segment((27,19)).segment((14,30)).segment((14,22)).segment((3,22)).segment((12,1)).segment((-2,1)).segment((-2,-2)).segment((-1,-2)).close().assemble()).finalize().extrude(-200).union(w0.sketch().segment((-57,-42),(-53,-53)).segment((-45,-48)).arc((-47,-40),(-45,-32)).close().assemble().reset().face(w0.sketch().arc((-42,-30),(-39,-25),(-35,-20)).segment((-39,-15)).segment((-21,0)).segment((-19,-2)).segment((26,17)).segment((23,24)).segment((12,29)).arc((14,44),(30,40)).segment((47,44)).segment((56,47)).arc((32,53),(10,52)).segment((10,46)).segment((-8,48)).segment((-25,-10)).segment((-24,-10)).arc((-27,-14),(-30,-18)).close().assemble()).finalize().extrude(-99)).union(w1.sketch().arc((-58,-27),(-57,-38),(-54,-50)).arc((-51,-46),(-48,-43)).arc((-51,-35),(-46,-30)).arc((-52,-29),(-58,-27)).assemble().finalize().extrude(-137))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0077_00774426.step')

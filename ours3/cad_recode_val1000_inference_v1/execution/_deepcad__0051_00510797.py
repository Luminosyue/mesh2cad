import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(3,0,0))
r=w0.sketch().segment((-100,19),(-97,19)).segment((-97,6)).segment((-84,6)).segment((-84,19)).segment((-65,19)).arc((-82,30),(-100,19)).assemble().reset().face(w0.sketch().segment((-90,6),(-65,-31)).segment((-65,-26)).segment((-53,-26)).segment((-53,-46)).segment((-54,-46)).segment((-33,-66)).segment((-27,-66)).segment((-27,-68)).segment((-12,-66)).segment((-12,-63)).segment((17,-39)).segment((17,-28)).segment((39,-23)).segment((39,-20)).segment((52,-16)).segment((49,-10)).segment((39,-14)).segment((39,-13)).segment((37,-13)).segment((30,6)).segment((52,6)).segment((52,13)).segment((88,13)).segment((88,24)).arc((99,46),(75,58)).segment((73,69)).segment((31,55)).segment((33,44)).segment((63,50)).segment((63,32)).segment((20,32)).segment((20,24)).segment((8,20)).segment((10,11)).segment((-4,5)).segment((-4,2)).segment((-65,2)).segment((-65,6)).close().assemble()).push([(-21,-43)]).circle(11,mode='s').finalize().extrude(-6)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0051_00510797.step')

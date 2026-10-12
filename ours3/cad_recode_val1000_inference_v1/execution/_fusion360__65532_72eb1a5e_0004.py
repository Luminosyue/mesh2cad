import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
w1=cq.Workplane('XY',origin=(0,0,8))
r=w0.sketch().segment((-34,-4),(-20,-28)).segment((35,3)).segment((21,28)).close().assemble().finalize().extrude(43).union(w0.sketch().segment((-25,20),(16,31)).segment((-17,31)).close().assemble().reset().face(w0.sketch().segment((-24,-21),(-19,-21)).segment((-19,-31)).segment((14,-31)).segment((36,0)).segment((22,13)).close().assemble()).finalize().extrude(200)).union(w1.sketch().arc((-36,0),(-33,-6),(-29,-11)).arc((-31,-6),(-31,-1)).arc((-33,0),(-36,0)).assemble().finalize().extrude(87))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__65532_72eb1a5e_0004.step')

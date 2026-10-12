import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,17))
r=w0.sketch().segment((-100,-20),(-29,-20)).segment((-70,-2)).segment((-60,20)).segment((-100,20)).close().assemble().reset().face(w0.sketch().segment((-42,-20),(100,-20)).segment((100,20)).segment((60,20)).segment((70,0)).segment((60,-2)).segment((61,14)).segment((54,14)).segment((54,2)).segment((53,2)).segment((53,14)).segment((47,14)).segment((47,20)).segment((-22,20)).segment((-22,19)).segment((-20,19)).segment((-20,17)).segment((-16,17)).segment((-16,19)).segment((-13,19)).segment((-13,17)).segment((-9,17)).segment((-9,14)).segment((-13,14)).segment((-13,12)).segment((-16,12)).segment((-16,10)).segment((-19,10)).segment((-19,12)).segment((-22,12)).segment((-22,10)).segment((-25,10)).segment((-25,12)).segment((-29,12)).segment((-29,19)).segment((-100,19)).close().assemble()).finalize().extrude(-35)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0079_00797643.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(2,0,0))
r=w0.sketch().segment((-100,-18),(-97,-22)).segment((-88,-16)).segment((-94,-14)).close().assemble().reset().face(w0.sketch().segment((-96,12),(-53,13)).segment((-53,15)).segment((-14,16)).segment((-14,15)).segment((-4,17)).segment((-3,12)).segment((56,12)).segment((56,16)).segment((98,16)).segment((98,12)).segment((100,12)).segment((98,15)).segment((98,22)).segment((56,22)).segment((56,18)).segment((-38,19)).segment((-38,17)).segment((-96,16)).close().assemble()).reset().face(w0.sketch().segment((-72,-22),(-24,-21)).segment((-24,-18)).segment((-72,-17)).close().assemble()).push([(37,-19.5)]).rect(122,5).finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0016_00160943.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,11))
r=w0.sketch().segment((-98,17),(-97,15)).segment((-97,17)).close().assemble().reset().face(w0.sketch().segment((-97,-15),(-90,-20)).segment((-81,-10)).segment((-81,-22)).segment((83,-21)).segment((82,-16)).segment((93,-16)).segment((93,-15)).segment((63,-8)).segment((73,11)).segment((100,0)).segment((100,16)).segment((93,20)).segment((93,21)).segment((90,21)).segment((82,10)).segment((82,22)).segment((-47,21)).segment((-47,16)).segment((-27,10)).segment((-37,-10)).segment((-69,8)).segment((-69,-10)).segment((-82,-10)).segment((-82,10)).segment((-97,17)).assemble()).reset().face(w0.sketch().segment((-47,-16),(-11,-16)).segment((-47,-10)).close().assemble()).finalize().extrude(-22)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0068_00682327.step')

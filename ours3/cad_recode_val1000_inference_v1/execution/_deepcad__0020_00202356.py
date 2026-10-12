import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-10))
r=w0.sketch().segment((-100,-100),(100,-100)).segment((100,100)).segment((23,100)).segment((95,51)).segment((65,10)).segment((95,10)).segment((95,-17)).segment((47,-17)).segment((47,0)).segment((15,-27)).segment((15,-71)).segment((-6,-71)).segment((-6,-29)).segment((-29,-54)).segment((-100,-10)).close().assemble().reset().face(w0.sketch().segment((-100,10),(-34,10)).segment((-100,62)).close().assemble()).reset().face(w0.sketch().segment((-49,100),(10,51)).segment((-6,71)).segment((-6,100)).close().assemble()).reset().face(w0.sketch().segment((23,-17),(47,-17)).segment((47,10)).segment((23,10)).close().assemble()).finalize().extrude(20)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0020_00202356.step')

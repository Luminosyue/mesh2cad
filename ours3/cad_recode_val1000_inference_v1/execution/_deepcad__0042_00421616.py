import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-83))
r=w0.sketch().segment((-100,-67),(-33,-67)).segment((-33,-33)).segment((100,-33)).segment((100,33)).segment((-33,33)).segment((-33,67)).segment((-100,67)).close().assemble().finalize().extrude(166).union(w0.sketch().segment((-100,-67),(-53,-67)).arc((-15,-24),(45,-34)).segment((45,33)).segment((-100,33)).close().assemble().reset().face(w0.sketch().arc((-89,58),(-86,62),(-83,67)).segment((-89,67)).close().assemble()).reset().face(w0.sketch().segment((-73,67),(-33,67)).segment((-33,33)).segment((45,33)).segment((45,13)).arc((48,22),(50,31)).arc((39,32),(30,37)).arc((-19,38),(-73,67)).assemble()).finalize().extrude(166))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0042_00421616.step')

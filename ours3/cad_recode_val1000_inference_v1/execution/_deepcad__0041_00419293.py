import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-87,0))
r=w0.sketch().segment((-100,-100),(100,-100)).segment((100,-78)).segment((99,-78)).segment((99,-76)).segment((100,-76)).segment((100,0)).segment((-100,-62)).close().assemble().reset().face(w0.sketch().segment((-100,-34),(-6,93)).segment((-6,100)).segment((-100,100)).close().assemble()).finalize().extrude(200).union(w1.sketch().segment((17,46),(17,76)).arc((32,24),(82,4)).arc((76,16),(80,29)).arc((55,42),(38,65)).segment((38,46)).close().assemble().finalize().extrude(176))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0041_00419293.step')

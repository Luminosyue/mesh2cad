import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-2))
r=w0.sketch().segment((-16,8),(-8,8)).segment((-8,96)).segment((-16,96)).segment((-16,36)).arc((-14,35),(-16,34)).close().assemble().reset().face(w0.sketch().segment((8,-100),(16,-100)).segment((16,-24)).segment((8,-24)).segment((8,-50)).arc((9,-52),(8,-54)).close().assemble()).reset().face(w0.sketch().segment((8,-10),(16,-10)).segment((16,27)).segment((13,27)).segment((13,29)).segment((16,29)).segment((16,96)).segment((8,96)).close().assemble()).finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0045_00452848.step')

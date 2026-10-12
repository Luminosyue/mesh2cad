import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-8))
r=w0.sketch().segment((-100,-58),(-48,-58)).segment((-48,-57)).segment((-100,-29)).close().assemble().reset().face(w0.sketch().segment((-100,-29),(-48,-56)).segment((-48,-22)).segment((-28,-22)).segment((-28,-58)).segment((16,-58)).segment((16,-32)).segment((41,-32)).segment((41,-58)).segment((100,-58)).segment((100,58)).segment((41,58)).segment((41,32)).segment((48,32)).segment((48,-6)).segment((41,-6)).segment((41,-19)).segment((16,-19)).segment((16,-6)).segment((14,-6)).segment((14,32)).segment((16,32)).segment((16,58)).segment((-100,58)).close().assemble()).reset().face(w0.sketch().segment((-32,20),(-28,-19)).segment((-5,-16)).segment((-9,22)).close().assemble()).finalize().extrude(16)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0028_00285881.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-9))
r=w0.sketch().segment((-100,-69),(-69,-69)).segment((-69,-28)).segment((-36,-28)).segment((-36,-69)).segment((16,-69)).segment((16,-68)).segment((100,-69)).segment((100,69)).segment((69,69)).segment((69,41)).segment((90,41)).segment((90,0)).segment((69,0)).segment((69,0)).segment((39,0)).segment((39,-13)).segment((16,-13)).segment((16,0)).segment((-22,0)).segment((-22,0)).segment((-23,0)).segment((-23,-13)).segment((-36,-13)).segment((-36,-23)).segment((-69,-23)).segment((-69,0)).segment((-90,0)).segment((-90,16)).segment((-69,16)).segment((-69,52)).segment((23,52)).segment((23,69)).segment((-100,69)).segment((-100,0)).segment((-100,-16)).close().assemble().reset().face(w0.sketch().segment((-69,21),(-69,41)).arc((-70,31),(-69,21)).assemble()).finalize().extrude(18)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0005_00050880.step')

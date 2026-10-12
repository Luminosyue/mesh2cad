import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(4,0,0))
r=w0.sketch().segment((-27,-97),(-18,-97)).segment((-18,-100)).segment((27,-100)).segment((27,-29)).segment((27,93)).segment((18,93)).segment((18,88)).segment((1,88)).segment((1,100)).segment((-20,100)).segment((-20,88)).segment((-27,88)).segment((-27,7)).arc((-21,1),(-22,-7)).arc((-21,-10),(-20,-12)).segment((-20,-57)).segment((-18,-57)).segment((-18,-12)).arc((-16,-10),(-15,-7)).arc((-11,-10),(-7,-12)).segment((-7,-17)).segment((7,-17)).segment((7,-12)).arc((11,-10),(15,-7)).segment((20,-7)).segment((20,-12)).arc((21,-10),(22,-7)).segment((27,-7)).segment((27,58)).segment((18,58)).segment((18,34)).segment((-7,34)).segment((-7,58)).segment((-18,58)).segment((-18,55)).arc((-21,56),(-27,58)).segment((-27,7)).arc((-21,1),(-18,-7)).segment((-18,-12)).arc((-21,-10),(-27,-7)).close().assemble().reset().face(w0.sketch().segment((-27,17),(-20,17)).segment((-20,20)).arc((-21,21),(-22,23)).arc((-24,21),(-27,17)).assemble()).finalize().extrude(-8)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0088_00888470.step')

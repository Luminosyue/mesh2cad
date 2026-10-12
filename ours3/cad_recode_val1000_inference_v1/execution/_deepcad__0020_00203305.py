import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,9))
r=w0.sketch().segment((-40,-88),(-34,-88)).segment((-34,-100)).segment((-30,-100)).arc((-15,-69),(0,-100)).segment((39,-100)).segment((39,-94)).segment((40,-94)).segment((40,-57)).segment((39,-57)).segment((39,63)).segment((40,63)).segment((40,100)).segment((9,100)).segment((16,79)).segment((-1,79)).segment((-1,69)).segment((17,69)).segment((-1,29)).segment((-1,17)).segment((-10,17)).segment((-16,1)).segment((-39,8)).segment((-34,22)).segment((-34,30)).segment((-40,30)).close().assemble().reset().face(w0.sketch().segment((-40,52),(-25,90)).segment((-4,82)).segment((-4,89)).segment((-21,89)).segment((-21,92)).segment((-40,92)).close().assemble()).finalize().extrude(-18)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0020_00203305.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-56,0))
w1=cq.Workplane('XY',origin=(0,0,29))
r=w0.sketch().segment((-29,-13),(-27,-13)).segment((-27,-53)).segment((-16,-53)).segment((-16,-98)).segment((19,-98)).segment((19,-53)).segment((27,-53)).segment((27,-13)).segment((29,-13)).segment((29,49)).segment((27,49)).segment((27,90)).segment((19,90)).segment((19,92)).segment((-16,92)).segment((-16,90)).segment((-27,90)).segment((-27,49)).segment((-29,49)).close().assemble().finalize().extrude(-7).union(w1.sketch().segment((-100,-56),(-93,-56)).segment((-93,56)).segment((-45,56)).arc((-30,55),(-15,56)).segment((0,56)).arc((-1,55),(-4,56)).segment((0,56)).segment((0,63)).segment((-4,63)).arc((-1,64),(0,63)).segment((84,63)).segment((84,56)).segment((93,56)).segment((93,-56)).segment((100,-56)).segment((100,63)).segment((-100,63)).close().assemble().finalize().extrude(-58))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0098_00986230.step')

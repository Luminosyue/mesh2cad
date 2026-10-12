import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-4))
r=w0.sketch().segment((-100,0),(-87,-13)).segment((-76,-13)).segment((-76,-10)).segment((-60,-13)).segment((-28,-13)).segment((-28,-11)).segment((-27,-11)).segment((-27,-13)).segment((82,-13)).segment((100,-1)).segment((97,4)).segment((97,10)).segment((93,10)).segment((93,13)).segment((42,13)).segment((42,11)).segment((-28,11)).segment((-28,10)).segment((-29,10)).segment((-29,12)).segment((-45,13)).segment((-45,11)).segment((-68,11)).segment((-68,10)).segment((-69,10)).segment((-69,11)).segment((-98,11)).segment((-98,1)).close().assemble().finalize().extrude(8)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0030_00304094.step')

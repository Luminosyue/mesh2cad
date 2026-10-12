import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,2,0))
r=w0.sketch().segment((-4,34),(-3,34)).segment((-3,-100)).segment((3,-100)).segment((3,34)).segment((4,34)).segment((4,56)).segment((3,56)).segment((3,100)).segment((-3,100)).segment((-3,56)).segment((-4,56)).close().assemble().finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0081_00819413.step')

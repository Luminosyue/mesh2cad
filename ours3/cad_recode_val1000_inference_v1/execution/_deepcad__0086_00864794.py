import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-96))
w1=cq.Workplane('YZ',origin=(-90,0,0))
r=w0.sketch().segment((-95,-39),(-90,-41)).arc((-90,-35),(-90,-28)).close().assemble().finalize().extrude(181).union(w0.sketch().segment((90,-42),(100,-42)).segment((100,-30)).arc((95,-27),(90,-27)).close().assemble().finalize().extrude(194)).union(w1.sketch().arc((-39,-96),(-32,-92),(-27,-85)).arc((-33,-84),(-39,-82)).close().assemble().finalize().extrude(-10))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0086_00864794.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-11,0,0))
r=w0.sketch().segment((-100,-15),(-46,-16)).segment((-46,-15)).segment((86,-16)).segment((86,-13)).segment((100,0)).segment((83,12)).segment((82,12)).segment((29,13)).arc((27,13),(25,12)).segment((-100,15)).close().assemble().finalize().extrude(22)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0013_00137059.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-4,0,0))
r=w0.sketch().segment((-100,0),(-96,-13)).segment((-40,-12)).segment((100,-12)).segment((100,12)).segment((-40,12)).segment((-40,0)).close().assemble().finalize().extrude(8)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0024_00243914.step')

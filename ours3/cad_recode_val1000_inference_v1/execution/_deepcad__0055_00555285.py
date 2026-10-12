import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(6,0,0))
r=w0.sketch().segment((-100,-6),(-14,-6)).segment((-14,-7)).segment((-11,-6)).segment((100,-6)).segment((100,6)).segment((14,6)).segment((14,7)).segment((11,6)).segment((-100,6)).close().assemble().finalize().extrude(-12)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0055_00555285.step')

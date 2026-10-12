import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(7,0,0))
r=w0.sketch().segment((-10,-100),(10,-100)).segment((10,100)).segment((-10,100)).segment((-10,-39)).segment((4,-39)).segment((4,-41)).segment((-10,-41)).close().assemble().finalize().extrude(-14)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__132461_14abd2d0_0005.step')

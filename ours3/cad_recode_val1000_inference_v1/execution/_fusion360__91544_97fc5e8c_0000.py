import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(20,0,0))
r=w0.sketch().segment((-100,-20),(-83,-20)).segment((-83,-10)).segment((-51,-10)).segment((-51,-20)).segment((-27,-20)).arc((-28,-18),(-29,-16)).segment((-14,-16)).segment((-14,-20)).segment((100,-20)).segment((100,20)).segment((-100,20)).close().assemble().finalize().extrude(-40)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__91544_97fc5e8c_0000.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(8,0,0))
r=w0.sketch().segment((-9,15),(-8,15)).segment((-8,-93)).segment((-7,-93)).segment((-7,15)).segment((-6,15)).segment((-6,100)).segment((-8,100)).segment((-8,35)).segment((-9,35)).close().assemble().finalize().extrude(-16).union(w0.sketch().segment((-10,-36),(-3,-100)).segment((8,-98)).segment((2,-49)).arc((8,-41),(8,-31)).segment((10,-10)).segment((3,-9)).segment((3,13)).segment((7,13)).segment((7,85)).segment((-7,85)).segment((-7,31)).segment((-3,31)).segment((-3,29)).segment((-7,29)).segment((-7,-34)).arc((-8,-35),(-10,-36)).assemble().finalize().extrude(-1))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0082_00829935.step')

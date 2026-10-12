import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(4,0,0))
r=w0.sketch().segment((-6,97),(-4,-51)).segment((-4,-58)).segment((-3,-58)).segment((-4,-97)).segment((2,-100)).segment((6,-93)).segment((4,-93)).segment((4,-84)).segment((5,-84)).segment((4,-26)).segment((4,97)).segment((2,97)).segment((2,100)).close().assemble().finalize().extrude(-8)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0062_00623998.step')

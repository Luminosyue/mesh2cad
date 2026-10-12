import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,1))
r=w0.sketch().segment((-5,-97),(-2,-100)).segment((5,-98)).segment((5,92)).segment((-5,100)).close().assemble().finalize().extrude(-2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0095_00953901.step')

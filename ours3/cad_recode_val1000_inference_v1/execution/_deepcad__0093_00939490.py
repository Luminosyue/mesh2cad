import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,5))
r=w0.sketch().segment((-9,-95),(2,-95)).segment((2,-100)).segment((9,-100)).segment((9,100)).segment((2,100)).segment((2,95)).segment((-9,95)).close().assemble().finalize().extrude(-10)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0093_00939490.step')

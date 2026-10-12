import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,1))
r=w0.sketch().segment((-11,-67),(-8,-67)).segment((-8,-74)).segment((-10,-74)).segment((-10,-87)).segment((-8,-87)).segment((-8,-100)).segment((11,-98)).segment((11,-33)).segment((11,16)).segment((11,100)).segment((-11,98)).segment((-11,44)).segment((-9,44)).segment((-9,16)).segment((-11,16)).close().assemble().finalize().extrude(-2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0097_00979069.step')

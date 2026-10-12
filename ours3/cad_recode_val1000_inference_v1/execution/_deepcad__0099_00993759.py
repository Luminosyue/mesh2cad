import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,62,0))
r=w0.sketch().segment((-63,-100),(63,-100)).segment((63,100)).segment((-63,100)).segment((-63,66)).segment((-62,66)).segment((-62,64)).segment((-63,64)).close().assemble().push([(60,-10)]).circle(3,mode='s').finalize().extrude(-125).union(w0.sketch().segment((-62,-100),(62,-100)).segment((62,100)).segment((-43,100)).arc((-48,85),(-62,76)).close().assemble().push([(0,-1)]).circle(63,mode='s').finalize().extrude(-120))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0099_00993759.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,33,0))
r=w0.sketch().segment((-100,-100),(100,-100)).segment((100,-33)).segment((33,-33)).segment((33,3)).segment((24,3)).segment((24,-29)).segment((-24,-29)).segment((-24,-33)).segment((-33,-33)).segment((-33,-56)).segment((-38,-56)).segment((-38,-33)).segment((-100,-33)).close().assemble().reset().face(w0.sketch().segment((-100,-8),(-38,38)).segment((-38,41)).segment((-33,41)).segment((-33,100)).segment((-100,100)).close().assemble()).finalize().extrude(-66).union(w0.sketch().segment((-97,-48),(-53,-48)).segment((-53,-100)).segment((33,-100)).segment((33,-48)).segment((63,-48)).segment((63,-33)).segment((33,-33)).segment((33,34)).segment((-53,34)).segment((-53,-33)).segment((-97,-33)).close().assemble().finalize().extrude(-67))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0042_00425268.step')

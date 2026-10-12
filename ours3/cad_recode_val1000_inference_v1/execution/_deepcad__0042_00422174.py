import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-20,0))
r=w0.sketch().segment((-100,-15),(28,-15)).segment((28,-13)).segment((29,-13)).segment((29,-15)).segment((100,-15)).segment((100,15)).segment((60,15)).segment((60,-2)).segment((20,-2)).segment((20,15)).segment((-100,15)).close().assemble().push([(-66,-10)]).circle(8,mode='s').finalize().extrude(39).union(w0.sketch().segment((-96,-15),(25,-15)).segment((25,-2)).segment((-65,-2)).segment((-65,15)).segment((-71,15)).segment((-71,-2)).segment((-96,-2)).close().assemble().finalize().extrude(40))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0042_00422174.step')

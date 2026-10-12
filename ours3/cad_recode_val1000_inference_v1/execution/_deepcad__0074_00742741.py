import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-84,0))
r=w0.sketch().segment((-91,-100),(46,-100)).segment((91,-62)).segment((91,49)).segment((35,100)).segment((-91,100)).close().assemble().push([(39,3)]).circle(54,mode='s').finalize().extrude(168)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0074_00742741.step')

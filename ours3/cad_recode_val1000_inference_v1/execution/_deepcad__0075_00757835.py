import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-67,0))
r=w0.sketch().arc((-67,-45),(-12,-60),(19,-100)).segment((67,-100)).segment((67,90)).segment((43,90)).segment((43,100)).segment((-67,100)).close().assemble().push([(-12,35)]).circle(57,mode='s').finalize().extrude(67).union(w0.sketch().segment((-67,-100),(57,-100)).segment((57,-33)).segment((49,-33)).segment((49,-34)).segment((47,-34)).segment((47,-33)).segment((-67,-33)).close().assemble().finalize().extrude(134))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0075_00757835.step')

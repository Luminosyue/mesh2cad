import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-53,0))
r=w0.sketch().segment((-100,55),(-46,-51)).segment((1,-26)).arc((72,-28),(41,38)).segment((41,56)).segment((-97,56)).segment((-97,57)).close().assemble().push([(34,-1)]).circle(23,mode='s').finalize().extrude(100).union(w0.sketch().segment((-75,4),(-64,-20)).segment((-64,-16)).segment((-22,-14)).arc((-47,27),(-4,19)).segment((-2,19)).segment((-2,20)).segment((-2,21)).segment((-2,22)).segment((-2,23)).segment((-3,23)).segment((-4,25)).segment((-10,23)).segment((-10,22)).segment((-10,21)).segment((-10,20)).segment((-10,19)).segment((-11,19)).segment((-11,18)).segment((-12,19)).segment((-13,19)).segment((-40,35)).close().assemble().push([(34,-1)]).rect(132,110).circle(14,mode='s').finalize().extrude(106))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0043_00439632.step')

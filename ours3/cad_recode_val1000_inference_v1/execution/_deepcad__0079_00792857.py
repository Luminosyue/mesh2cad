import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-1,0))
r=w0.sketch().segment((-15,-56),(5,-100)).segment((15,-87)).segment((15,-74)).segment((1,-74)).segment((1,-41)).segment((12,-41)).segment((12,-61)).segment((15,-60)).segment((15,-43)).segment((12,-43)).segment((12,-2)).segment((15,10)).segment((15,19)).segment((14,19)).segment((14,42)).segment((15,42)).segment((15,74)).segment((6,100)).segment((-5,74)).segment((-5,73)).arc((-14,50),(-5,27)).segment((-5,19)).segment((-14,19)).segment((-14,-19)).segment((-5,-19)).segment((-5,-20)).segment((1,-20)).segment((1,-19)).segment((5,-19)).segment((5,-27)).segment((1,-27)).segment((1,-41)).segment((-10,-41)).segment((-10,-20)).segment((-14,-20)).segment((-14,-2)).segment((-10,-2)).segment((-10,-19)).segment((-15,-19)).close().assemble().finalize().extrude(2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0079_00792857.step')

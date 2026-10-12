import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-67,-100),(-33,-100)).arc((-16,-41),(33,-7)).segment((33,100)).segment((-67,100)).close().assemble().finalize().extrude(196).union(w0.sketch().segment((-67,-100),(67,-100)).segment((67,-50)).segment((33,-50)).segment((33,50)).segment((67,50)).segment((67,100)).segment((-67,100)).segment((-67,50)).segment((-33,50)).segment((-33,-50)).segment((-67,-50)).close().assemble().finalize().extrude(200))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0062_00624069.step')

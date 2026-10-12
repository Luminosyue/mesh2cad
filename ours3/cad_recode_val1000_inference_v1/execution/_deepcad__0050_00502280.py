import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,2,0))
r=w0.sketch().segment((-15,-98),(10,-100)).segment((15,-100)).segment((15,38)).segment((14,38)).segment((14,42)).segment((15,42)).segment((15,100)).segment((-15,100)).segment((-15,33)).arc((-13,32),(-15,31)).segment((-15,7)).arc((-13,0),(-15,-7)).segment((-15,-27)).segment((-13,-27)).segment((-13,-33)).segment((-15,-33)).close().assemble().finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0050_00502280.step')

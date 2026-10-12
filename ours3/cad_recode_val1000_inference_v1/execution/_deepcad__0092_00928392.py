import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-84))
r=w0.sketch().segment((-100,-99),(100,-99)).segment((100,99)).segment((-68,99)).arc((-81,87),(-94,99)).segment((-100,99)).close().assemble().push([(26,0)]).circle(38,mode='s').finalize().extrude(168)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0092_00928392.step')

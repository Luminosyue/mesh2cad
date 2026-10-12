import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-8,0))
w1=cq.Workplane('XY',origin=(0,0,94))
r=w0.sketch().segment((-100,-2),(-95,-2)).segment((-95,-7)).segment((-74,-7)).segment((-74,-8)).segment((-21,-8)).segment((-21,-7)).segment((96,-8)).segment((96,2)).segment((97,2)).segment((97,8)).segment((9,8)).segment((9,2)).segment((-21,2)).segment((-21,8)).segment((-95,8)).segment((-95,2)).segment((-100,2)).close().assemble().push([(0,0)]).rect(148,14,mode='s').finalize().extrude(16).union(w1.workplane(offset=-105/2).box(14,14,105))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0044_00440355.step')

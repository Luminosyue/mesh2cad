import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-8,0))
w1=cq.Workplane('XY',origin=(0,0,30))
r=w0.sketch().segment((-100,4),(-92,4)).segment((-92,6)).segment((-43,6)).segment((-43,4)).segment((-14,4)).segment((-14,12)).segment((-100,12)).close().assemble().finalize().extrude(3).union(w0.sketch().push([(11.5,-5)]).rect(153,16).push([(11.5,-5.5)]).rect(11,13,mode='s').finalize().extrude(15)).union(w1.sketch().segment((-13,-6),(-10,-6)).arc((-5,-7),(0,-6)).segment((3,-6)).segment((3,6)).segment((0,6)).arc((-5,8),(-10,6)).segment((-13,6)).close().assemble().finalize().extrude(-105))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0070_00708928.step')

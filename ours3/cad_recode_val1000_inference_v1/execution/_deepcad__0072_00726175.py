import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-83,0))
w1=cq.Workplane('ZX',origin=(0,-69,0))
r=w0.sketch().segment((-21,59),(-1,94)).segment((-11,94)).segment((-11,99)).arc((-16,97),(-21,94)).segment((-1,94)).close().assemble().finalize().extrude(45).union(w0.sketch().segment((-35,-11),(-14,-79)).segment((-14,-94)).segment((-8,-94)).segment((-5,-100)).segment((10,-100)).segment((35,-95)).segment((35,26)).segment((29,26)).segment((29,76)).segment((35,76)).segment((35,94)).segment((29,94)).segment((29,100)).segment((-10,100)).segment((-10,94)).segment((10,94)).segment((10,76)).segment((-10,76)).segment((-10,69)).segment((-21,69)).arc((-25,45),(-19,21)).segment((-19,15)).segment((-34,15)).arc((-30,5),(-23,-4)).close().assemble().push([(32,-59)]).rect(4,60).finalize().extrude(150)).union(w1.sketch().arc((-34,-11),(-12,-3),(-1,-20)).arc((-10,3),(-34,-11)).assemble().push([(-19,5)]).circle(1,mode='s').finalize().extrude(153))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0072_00726175.step')

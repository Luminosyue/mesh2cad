import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,0))
r=w0.sketch().segment((-100,-44),(-68,-50)).segment((-61,-25)).segment((-32,-25)).segment((-32,-48)).segment((-7,-51)).segment((-4,-25)).segment((14,-25)).segment((14,-40)).segment((20,-40)).segment((20,-46)).segment((30,-46)).segment((30,-40)).segment((49,-40)).segment((49,-39)).segment((62,-49)).segment((75,-29)).segment((51,-14)).segment((51,-13)).segment((100,-13)).segment((100,8)).segment((51,8)).segment((51,16)).segment((30,16)).segment((30,17)).segment((20,17)).segment((20,16)).segment((4,16)).segment((4,15)).segment((10,15)).segment((10,-13)).segment((4,-13)).segment((4,-14)).segment((-19,-14)).segment((-19,13)).segment((-46,15)).segment((-46,14)).segment((-39,14)).segment((-39,-5)).segment((-92,1)).close().assemble().push([(-51,49.5)]).rect(46,1).push([(54,49.5)]).rect(46,1).finalize().extrude(0)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0030_00301691.step')

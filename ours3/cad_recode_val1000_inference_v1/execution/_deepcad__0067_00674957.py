import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,12))
r=w0.sketch().segment((-37,-67),(-35,-67)).segment((-35,-93)).segment((-23,-93)).segment((-23,-97)).segment((-1,-97)).segment((-1,-93)).segment((35,-93)).segment((35,-67)).segment((37,-67)).segment((37,-42)).segment((35,-42)).segment((35,-41)).arc((31,-37),(28,-32)).segment((28,-31)).arc((31,-26),(35,-21)).segment((35,10)).segment((35,11)).segment((37,11)).segment((37,36)).segment((35,36)).segment((35,62)).segment((-35,62)).segment((-35,36)).segment((-35,11)).segment((-35,10)).segment((-37,10)).segment((-37,-15)).segment((-35,-15)).segment((-35,-42)).segment((-37,-42)).close().assemble().push([(-10,-17)]).circle(17,mode='s').push([(-19,82)]).rect(32,28).finalize().extrude(-25).union(w0.sketch().segment((-37,-23),(-11,-23)).segment((-11,-100)).segment((4,-100)).segment((4,-23)).segment((26,-23)).segment((26,100)).segment((-37,100)).close().assemble().push([(4,-61)]).circle(22,mode='s').finalize().extrude(2))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0067_00674957.step')

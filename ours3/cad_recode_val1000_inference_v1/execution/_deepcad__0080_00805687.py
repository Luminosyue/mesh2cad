import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,12))
r=w0.sketch().segment((-100,-87),(-96,-87)).segment((-100,-86)).close().assemble().reset().face(w0.sketch().segment((-88,-87),(95,-87)).arc((72,-55),(32,-48)).segment((32,-53)).segment((28,-53)).arc((-21,-60),(-23,-12)).segment((-24,-1)).segment((-49,3)).segment((-31,-51)).segment((-77,-39)).arc((-79,-50),(-82,-61)).segment((-73,-61)).segment((-73,-82)).segment((-88,-82)).close().assemble()).reset().face(w0.sketch().segment((-22,31),(1,8)).segment((27,40)).segment((-3,82)).segment((-13,64)).arc((-15,61),(-15,58)).segment((-22,50)).close().assemble()).finalize().extrude(-24).union(w0.sketch().segment((32,-7),(41,-20)).arc((40,-36),(56,-35)).segment((64,-40)).segment((66,-37)).segment((57,-32)).arc((58,-14),(42,-15)).segment((34,-10)).close().assemble().finalize().extrude(-19))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0080_00805687.step')

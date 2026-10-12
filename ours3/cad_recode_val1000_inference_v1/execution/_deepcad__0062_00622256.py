import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,17,0))
r=w0.sketch().segment((-50,-95),(-40,-95)).segment((-40,-100)).segment((-25,-100)).segment((-25,-17)).segment((-5,-17)).segment((-5,-10)).segment((31,-7)).segment((21,46)).segment((12,44)).segment((12,38)).arc((19,26),(12,15)).segment((12,9)).segment((-5,9)).segment((-5,8)).segment((-40,8)).segment((-40,3)).segment((-50,3)).close().assemble().push([(48,80)]).rect(4,40).finalize().extrude(-34).union(w0.sketch().segment((-50,-64),(-25,-74)).segment((-25,8)).segment((-29,9)).segment((-30,4)).segment((-50,4)).close().assemble().reset().face(w0.sketch().segment((13,33),(44,33)).segment((44,25)).segment((50,25)).segment((50,91)).segment((13,91)).close().assemble()).finalize().extrude(-31))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0062_00622256.step')

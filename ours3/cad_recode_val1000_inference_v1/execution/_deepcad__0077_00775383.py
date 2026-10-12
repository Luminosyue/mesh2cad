import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,1,0))
r=w0.sketch().segment((-33,40),(-29,40)).segment((-29,12)).segment((-31,12)).segment((-29,-1)).segment((-30,-1)).segment((-30,-14)).segment((-27,-14)).segment((-27,-38)).segment((-30,-38)).segment((-30,-51)).segment((-29,-51)).segment((-29,-100)).segment((28,-100)).segment((28,-51)).segment((31,-51)).segment((31,-38)).segment((28,-38)).segment((28,-14)).segment((25,-14)).segment((25,12)).segment((33,12)).segment((33,40)).segment((33,73)).segment((28,73)).segment((28,100)).segment((10,100)).segment((10,96)).segment((-29,96)).segment((-29,73)).segment((-33,73)).close().assemble().push([(1,-43)]).circle(6,mode='s').finalize().extrude(-2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0077_00775383.step')

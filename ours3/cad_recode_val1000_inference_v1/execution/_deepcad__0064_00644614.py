import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-39,0))
w1=cq.Workplane('ZX',origin=(0,-38,0))
r=w0.sketch().segment((-30,2),(-24,-10)).arc((-23,-12),(-22,-14)).segment((-16,-26)).segment((-11,-24)).arc((13,-31),(30,-13)).segment((30,-12)).arc((31,-11),(31,-10)).segment((30,-9)).segment((30,-8)).segment((31,-8)).arc((31,-6),(30,-4)).segment((30,1)).segment((24,1)).arc((10,15),(-10,15)).segment((-10,14)).arc((-11,12),(-11,10)).close().assemble().finalize().extrude(10).union(w1.sketch().segment((-100,-51),(-34,-51)).arc((-28,-46),(-22,-43)).arc((-24,-11),(-4,14)).arc((14,32),(39,39)).arc((37,45),(34,51)).segment((-100,51)).close().assemble().reset().face(w1.sketch().segment((-9,-51),(100,-51)).segment((100,51)).segment((54,51)).arc((53,46),(51,42)).arc((51,39),(50,37)).arc((47,38),(44,39)).arc((40,39),(37,41)).arc((35,-28),(-9,-51)).assemble()).finalize().extrude(77))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0064_00644614.step')

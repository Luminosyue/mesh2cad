import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-15))
w1=cq.Workplane('XY',origin=(0,0,8))
r=w0.sketch().segment((-51,-65),(26,-65)).segment((26,-9)).segment((58,-9)).segment((58,-3)).segment((100,-3)).segment((100,55)).segment((46,55)).segment((46,36)).segment((1,36)).segment((1,26)).segment((-51,26)).close().assemble().push([(13,-14)]).circle(14,mode='s').finalize().extrude(15).union(w0.sketch().segment((-100,-68),(-65,-68)).arc((-48,-42),(-22,-68)).segment((15,-68)).segment((15,-62)).segment((58,-62)).segment((58,3)).segment((54,3)).segment((54,-9)).segment((37,-9)).segment((37,-10)).segment((15,-10)).segment((15,26)).segment((-100,26)).close().assemble().finalize().extrude(30)).union(w1.sketch().arc((1,26),(23,29),(38,13)).arc((24,68),(1,26)).assemble().finalize().extrude(-10))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0012_00120949.step')

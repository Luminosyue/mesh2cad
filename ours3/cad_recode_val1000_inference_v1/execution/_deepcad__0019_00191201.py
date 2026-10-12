import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-10))
r=w0.sketch().segment((-100,-15),(-25,-14)).segment((-74,-14)).segment((-74,4)).segment((-68,4)).arc((-63,-4),(-56,-9)).segment((-56,-14)).segment((-29,-14)).segment((-29,-15)).segment((-26,-15)).segment((-26,-14)).segment((100,-14)).segment((100,15)).segment((-45,14)).segment((-3,14)).segment((-41,14)).segment((-41,-9)).arc((-48,-4),(-53,4)).segment((-56,4)).segment((-56,-9)).segment((-68,-9)).segment((-68,4)).segment((-74,4)).segment((-74,14)).segment((-100,14)).close().assemble().push([(48,0)]).circle(10,mode='s').reset().face(w0.sketch().segment((57,-14),(67,-14)).segment((67,-13)).arc((63,-13),(67,-12)).segment((67,-11)).arc((68,-9),(67,-7)).segment((67,4)).segment((57,4)).segment((57,-7)).arc((56,-9),(57,-11)).close().assemble(),mode='s').finalize().extrude(20)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0019_00191201.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,5))
r=w0.sketch().segment((-100,-38),(-52,-38)).arc((-56,-32),(-57,-25)).segment((-78,-23)).segment((-75,15)).segment((-54,13)).arc((-46,21),(-36,26)).segment((-36,38)).segment((-100,38)).close().assemble().reset().face(w0.sketch().segment((-35,-38),(7,-38)).segment((7,-27)).segment((14,-27)).segment((14,-6)).segment((48,-16)).segment((44,-38)).segment((100,-38)).segment((100,38)).segment((23,38)).segment((23,30)).segment((-7,38)).segment((-35,38)).segment((-35,26)).arc((-31,21),(-28,15)).segment((-7,13)).segment((-10,-15)).segment((-32,-13)).arc((-32,-25),(-35,-38)).assemble()).push([(61,12)]).circle(14,mode='s').finalize().extrude(-10)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0067_00676583.step')

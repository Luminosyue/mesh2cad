import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,8))
r=w0.sketch().segment((-40,-100),(40,-100)).segment((40,24)).segment((40,100)).segment((-40,100)).segment((-40,56)).arc((-35,51),(-40,46)).segment((-40,3)).segment((-28,3)).segment((-28,29)).segment((-13,29)).segment((-13,35)).segment((-10,35)).segment((-10,29)).segment((10,29)).segment((10,3)).segment((17,3)).segment((17,-13)).segment((10,-13)).segment((10,-19)).segment((-10,-19)).segment((-10,-25)).segment((-13,-25)).segment((-13,-19)).segment((-28,-19)).segment((-28,-13)).segment((-40,-13)).close().assemble().reset().face(w0.sketch().segment((-40,56),(17,56)).segment((17,35)).segment((10,35)).segment((10,38)).arc((-13,73),(-40,42)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-40,-100),(40,-100)).segment((40,-42)).arc((0,-85),(-40,-42)).close().assemble()).finalize().extrude(-16)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0095_00955711.step')

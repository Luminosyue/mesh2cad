import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-25))
r=w0.sketch().segment((-100,-25),(-50,-25)).segment((-50,25)).segment((-94,25)).segment((-94,22)).segment((-100,22)).close().assemble().reset().face(w0.sketch().segment((50,-25),(59,-25)).segment((59,-22)).segment((63,-22)).segment((63,-25)).segment((94,-25)).segment((94,-22)).segment((100,-22)).segment((100,22)).segment((94,22)).segment((94,25)).segment((50,25)).close().assemble()).finalize().extrude(50)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0041_00419914.step')

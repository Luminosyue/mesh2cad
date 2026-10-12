import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-13))
r=w0.sketch().segment((-100,-100),(-48,-100)).segment((-78,-54)).segment((-10,-15)).arc((-12,21),(17,44)).segment((17,56)).segment((27,56)).segment((27,44)).arc((45,36),(46,16)).segment((78,-27)).segment((17,-76)).segment((17,-100)).segment((100,-100)).segment((100,100)).segment((-100,100)).close().assemble().reset().face(w0.sketch().segment((-100,-100),(-99,-100)).segment((-100,-99)).close().assemble()).reset().face(w0.sketch().segment((-100,-69),(-99,-69)).segment((-100,-68)).close().assemble()).reset().face(w0.sketch().segment((-100,69),(-99,68)).segment((-99,69)).close().assemble()).reset().face(w0.sketch().segment((-88,100),(-87,99)).segment((-87,100)).close().assemble()).reset().face(w0.sketch().segment((-48,100),(-47,99)).segment((-47,100)).close().assemble()).finalize().extrude(26)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0003_00037492.step')

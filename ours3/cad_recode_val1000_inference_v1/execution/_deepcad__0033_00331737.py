import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-70,0))
r=w0.sketch().segment((-92,-100),(92,-100)).segment((92,100)).segment((-92,100)).segment((-92,58)).segment((-87,58)).segment((-87,54)).segment((-92,54)).close().assemble().push([(25,79)]).circle(17,mode='s').finalize().extrude(140)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0033_00331737.step')

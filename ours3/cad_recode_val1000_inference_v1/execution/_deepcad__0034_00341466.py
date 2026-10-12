import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-25))
r=w0.sketch().segment((-67,-100),(67,-100)).segment((67,-18)).segment((14,-36)).segment((14,27)).segment((-22,27)).segment((-22,36)).segment((67,36)).segment((67,100)).segment((-67,100)).close().assemble().push([(-52,-70)]).circle(15,mode='s').finalize().extrude(50).union(w0.sketch().segment((-67,-46),(-25,-46)).arc((-46,0),(-25,46)).segment((-67,46)).close().assemble().reset().face(w0.sketch().segment((25,-46),(67,-46)).segment((67,46)).segment((25,46)).arc((46,0),(25,-46)).assemble()).finalize().extrude(50))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0034_00341466.step')

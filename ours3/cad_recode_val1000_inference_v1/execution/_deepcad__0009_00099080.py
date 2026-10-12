import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-5))
r=w0.sketch().segment((-48,61),(-47,61)).segment((-47,-94)).segment((-39,-94)).segment((-42,-98)).segment((-37,-100)).segment((-34,-94)).segment((-28,-94)).segment((-28,-70)).segment((-20,-70)).segment((-20,-86)).segment((-7,-86)).segment((-7,-100)).segment((47,-100)).segment((47,-70)).segment((48,-70)).segment((48,-62)).segment((47,-62)).segment((47,61)).segment((48,61)).segment((48,78)).segment((40,78)).segment((43,97)).segment((37,98)).segment((34,78)).segment((28,78)).segment((28,100)).segment((-37,100)).segment((-37,78)).segment((-47,78)).segment((-47,61)).close().assemble().reset().face(w0.sketch().segment((-37,12),(-11,1)).segment((-20,-36)).segment((20,-36)).segment((20,-2)).segment((37,49)).segment((-20,69)).close().assemble(),mode='s').finalize().extrude(10)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0009_00099080.step')

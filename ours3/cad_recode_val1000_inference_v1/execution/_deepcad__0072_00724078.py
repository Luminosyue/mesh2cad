import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,65))
w1=cq.Workplane('XY',origin=(0,0,57))
r=w0.sketch().segment((-100,29),(-51,29)).segment((-82,9)).segment((-79,5)).segment((-40,29)).segment((-20,29)).segment((-20,8)).segment((85,8)).segment((85,-9)).segment((86,-9)).segment((85,-7)).segment((85,-71)).segment((-19,-71)).segment((-19,-86)).segment((100,-86)).segment((100,2)).segment((90,2)).segment((90,22)).segment((22,45)).segment((22,46)).segment((20,46)).segment((-57,72)).segment((-62,58)).segment((-100,58)).close().assemble().finalize().extrude(-130).union(w0.sketch().segment((-100,8),(-82,8)).arc((-62,29),(-33,35)).segment((-33,63)).segment((-93,84)).segment((-100,70)).close().assemble().reset().face(w0.sketch().segment((-33,59),(-29,56)).segment((-29,63)).segment((-33,63)).close().assemble(),mode='s').finalize().extrude(-56)).union(w1.sketch().segment((-79,8),(-34,8)).arc((-26,25),(-10,37)).segment((-10,56)).segment((-79,56)).close().assemble().finalize().extrude(-123))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0072_00724078.step')

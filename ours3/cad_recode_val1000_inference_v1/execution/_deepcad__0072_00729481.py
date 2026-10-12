import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-21))
r=w0.sketch().segment((-100,0),(-99,-4)).segment((-70,-5)).arc((-64,-7),(-58,-6)).segment((100,-6)).segment((89,7)).segment((-59,6)).arc((-65,7),(-70,6)).segment((-96,6)).segment((-96,1)).close().assemble().finalize().extrude(1).union(w0.sketch().arc((59,-2),(60,-2),(60,-3)).arc((62,3),(59,-2)).assemble().finalize().extrude(39)).union(w0.sketch().segment((-68,-2),(-64,-2)).segment((-64,2)).segment((-68,2)).arc((-67,0),(-68,-2)).assemble().finalize().extrude(40))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0072_00729481.step')

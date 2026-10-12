import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-2,0))
w1=cq.Workplane('XY',origin=(0,0,-7))
r=w0.sketch().segment((-100,-4),(-96,-4)).arc((-80,-5),(-64,-4)).segment((-57,-4)).segment((-57,4)).arc((-53,3),(-48,4)).segment((-48,-4)).segment((-47,-4)).segment((-47,4)).arc((-46,6),(-46,8)).arc((-48,9),(-48,10)).segment((-48,9)).arc((-53,10),(-57,9)).segment((-57,10)).segment((-64,10)).arc((-80,10),(-96,4)).segment((-100,4)).close().assemble().finalize().extrude(-4).union(w0.sketch().segment((-27,29),(24,4)).segment((87,4)).segment((87,7)).segment((100,7)).segment((90,12)).segment((90,11)).segment((87,11)).segment((87,13)).segment((67,13)).segment((67,16)).segment((23,15)).segment((23,13)).segment((-2,13)).segment((-2,6)).segment((-26,32)).close().assemble().finalize().extrude(4)).union(w1.sketch().segment((-38,-6),(-18,-6)).arc((-17,-5),(-16,-6)).segment((29,-6)).arc((33,-1),(38,-2)).arc((33,4),(32,11)).arc((30,10),(29,8)).segment((29,0)).segment((26,0)).segment((26,8)).arc((25,8),(24,7)).segment((24,5)).segment((22,5)).segment((22,7)).arc((21,7),(20,8)).segment((20,5)).segment((-16,5)).segment((-16,0)).segment((-19,0)).segment((-19,6)).segment((-38,6)).close().assemble().finalize().extrude(-13))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0059_00597424.step')

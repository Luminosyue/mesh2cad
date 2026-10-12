import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-19))
w1=cq.Workplane('XY',origin=(0,0,-22))
r=w0.sketch().arc((42,-8),(43,-7),(42,-6)).close().assemble().finalize().extrude(-70).union(w0.sketch().segment((-57,-11),(-56,-13)).arc((-59,-54),(-27,-78)).segment((-26,-80)).segment((-23,-79)).arc((-1,-66),(17,-47)).segment((19,-46)).segment((18,-44)).arc((21,-39),(23,-33)).segment((43,-33)).segment((43,-9)).segment((23,-9)).arc((18,-1),(11,5)).segment((10,7)).segment((7,6)).arc((-16,10),(-39,1)).segment((-42,0)).segment((-42,-1)).arc((-49,-6),(-55,-10)).close().assemble().push([(-20,-38)]).circle(2,mode='s').finalize().extrude(-3)).union(w0.sketch().segment((44,37),(58,31)).segment((58,33)).segment((44,40)).close().assemble().finalize().extrude(108)).union(w1.sketch().arc((-27,56),(-49,10),(-16,-28)).arc((14,-68),(37,-25)).arc((32,-26),(27,-26)).arc((18,-30),(10,-26)).arc((11,-19),(10,-12)).arc((18,-10),(27,-13)).arc((29,-13),(31,-14)).arc((32,-11),(33,-9)).arc((14,19),(38,41)).arc((12,60),(-20,59)).arc((-23,58),(-25,57)).segment((-27,57)).close().assemble().finalize().extrude(3))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0015_00157564.step')

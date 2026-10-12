import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(68,0,0))
r=w0.sketch().segment((-85,-92),(100,-92)).segment((100,92)).segment((-85,92)).segment((-85,40)).arc((-100,0),(-85,-38)).close().assemble().push([(27,0)]).circle(30,mode='s').finalize().extrude(-136).union(w0.sketch().segment((-99,-12),(-57,-12)).segment((-57,-44)).segment((57,-44)).segment((57,-12)).segment((99,-12)).segment((99,12)).segment((57,12)).segment((57,44)).segment((-57,44)).segment((-57,12)).segment((-99,12)).close().assemble().finalize().extrude(-91))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0085_00851422.step')

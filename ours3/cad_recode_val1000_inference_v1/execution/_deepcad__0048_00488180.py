import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-37,0,0))
r=w0.sketch().segment((-50,-100),(29,-100)).segment((29,-98)).segment((-10,-98)).segment((-10,-56)).segment((29,-56)).segment((29,-52)).segment((50,-52)).segment((50,77)).segment((-50,77)).segment((-50,40)).segment((-29,40)).segment((-29,20)).segment((-50,20)).close().assemble().push([(5,14)]).circle(20,mode='s').finalize().extrude(25).union(w0.sketch().segment((-50,75),(50,75)).segment((50,100)).segment((-38,100)).segment((-38,92)).segment((-50,92)).close().assemble().finalize().extrude(75))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0048_00488180.step')

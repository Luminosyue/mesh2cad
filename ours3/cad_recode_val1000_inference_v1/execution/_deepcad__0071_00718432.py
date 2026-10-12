import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,57,0))
r=w0.sketch().arc((-85,-83),(-48,-100),(-10,-87)).arc((-18,-38),(7,4)).segment((7,33)).segment((85,33)).segment((85,100)).segment((-85,100)).segment((-85,3)).arc((-80,-1),(-85,-4)).close().assemble().push([(-48,46)]).circle(6,mode='s').reset().face(w0.sketch().arc((-85,-78),(-83,-60),(-85,-42)).close().assemble(),mode='s').reset().face(w0.sketch().arc((10,100),(15,96),(19,92)).segment((19,100)).close().assemble()).reset().face(w0.sketch().arc((41,75),(66,60),(85,36)).segment((85,100)).close().assemble()).finalize().extrude(-113).union(w0.sketch().arc((-73,-89),(-32,-51),(7,-10)).arc((-58,-16),(-73,-89)).assemble().finalize().extrude(-104))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0071_00718432.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-50,0,0))
r=w0.sketch().segment((-93,-38),(6,-38)).segment((6,-31)).segment((47,-31)).segment((47,-29)).segment((100,-29)).segment((100,-4)).segment((83,-4)).segment((94,28)).segment((42,38)).segment((30,10)).segment((79,10)).segment((79,-15)).segment((22,-15)).segment((22,10)).segment((29,10)).segment((29,28)).segment((14,28)).segment((14,38)).segment((11,38)).segment((11,28)).segment((-25,34)).segment((-28,10)).segment((-8,10)).segment((-8,-15)).segment((-2,-15)).segment((-2,-21)).segment((-49,-21)).segment((-49,-8)).segment((-93,-8)).close().assemble().reset().face(w0.sketch().segment((-93,14),(-49,14)).segment((-49,15)).segment((-83,15)).segment((-83,38)).segment((-93,38)).close().assemble()).finalize().extrude(6).union(w0.sketch().segment((-100,-38),(-94,-38)).segment((-94,38)).segment((-100,38)).segment((-100,28)).segment((-99,28)).segment((-99,26)).segment((-100,26)).close().assemble().finalize().extrude(100))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0066_00660206.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-18))
w1=cq.Workplane('XY',origin=(0,0,-18))
r=w0.sketch().segment((-100,-100),(-88,-100)).segment((-100,-88)).close().assemble().reset().face(w0.sketch().segment((-100,-79),(-54,10)).arc((-61,14),(-67,19)).segment((36,61)).segment((67,-24)).segment((-46,-66)).arc((-42,-83),(-36,-100)).segment((79,-100)).segment((79,-90)).segment((83,-89)).segment((81,-84)).segment((79,-84)).segment((79,-82)).segment((100,-17)).segment((79,-11)).segment((79,100)).segment((-79,100)).segment((-79,90)).segment((-83,89)).segment((-81,84)).segment((-79,84)).segment((-79,82)).segment((-100,66)).close().assemble()).reset().face(w0.sketch().segment((74,92),(84,86)).segment((84,92)).close().assemble()).finalize().extrude(36).union(w1.sketch().arc((62,29),(63,31),(62,33)).close().assemble().finalize().extrude(23))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0037_00372205.step')

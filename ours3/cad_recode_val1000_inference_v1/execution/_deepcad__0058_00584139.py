import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,3,0))
r=w0.sketch().segment((-100,17),(-92,-18)).segment((-83,-17)).close().assemble().reset().face(w0.sketch().segment((-91,-17),(-48,-17)).segment((-48,-13)).segment((-42,-13)).segment((-42,-17)).segment((100,-17)).segment((100,17)).segment((-8,17)).segment((-8,13)).segment((-14,13)).segment((-14,17)).segment((-34,17)).segment((-33,16)).segment((-37,14)).segment((-38,17)).segment((-68,17)).segment((-68,13)).segment((-74,13)).segment((-74,17)).close().assemble()).finalize().extrude(-6)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0058_00584139.step')

import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,5))
r=w0.sketch().segment((-10,-97),(-7,-97)).segment((-7,-100)).segment((9,-100)).segment((9,-97)).segment((10,-97)).segment((10,-67)).segment((-10,-66)).close().assemble().reset().face(w0.sketch().segment((-10,-48),(10,-50)).segment((10,97)).segment((9,97)).segment((9,100)).segment((-7,100)).segment((-7,97)).segment((-10,97)).close().assemble()).finalize().extrude(-10)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0068_00689798.step')

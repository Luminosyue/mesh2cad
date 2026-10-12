import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-13))
r=w0.sketch().segment((-33,-100),(33,-100)).segment((33,100)).segment((-6,100)).segment((32,65)).segment((11,41)).segment((11,21)).segment((1,21)).segment((-1,17)).segment((-6,21)).segment((-19,21)).segment((-19,31)).segment((-33,31)).segment((-33,-54)).segment((-27,-54)).segment((-27,-60)).segment((-33,-60)).close().assemble().finalize().extrude(26)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0081_00819903.step')

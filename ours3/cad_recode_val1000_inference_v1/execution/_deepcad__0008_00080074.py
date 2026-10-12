import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-3))
r=w0.sketch().segment((-23,-92),(-17,-92)).segment((-17,-97)).segment((-10,-97)).segment((-10,-92)).segment((-7,-92)).segment((-7,-96)).segment((20,-100)).segment((23,-68)).segment((23,-67)).segment((23,-66)).segment((23,-65)).segment((23,-50)).segment((17,-50)).segment((17,-13)).segment((23,-13)).segment((23,14)).segment((15,14)).segment((23,74)).segment((23,95)).segment((17,95)).segment((17,100)).segment((-17,100)).segment((-17,95)).segment((-23,95)).segment((-23,37)).segment((-17,37)).segment((-17,33)).segment((-23,33)).segment((-23,-33)).segment((-17,-33)).segment((-17,-38)).segment((-23,-38)).close().assemble().finalize().extrude(6)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0008_00080074.step')

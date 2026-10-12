import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,31))
r=w0.sketch().arc((-63,-22),(-41,-22),(-58,-33)).arc((-32,-59),(5,-66)).arc((10,-66),(14,-65)).arc((37,56),(-63,-22)).assemble().finalize().extrude(-200).union(w0.sketch().arc((-58,-33),(-19,-30),(-5,-67)).arc((36,55),(-58,-33)).assemble().finalize().extrude(-116)).union(w1.sketch().arc((-63,22),(54,-39),(-54,39)).arc((-60,32),(-63,22)).assemble().finalize().extrude(-116))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0039_00396092.step')

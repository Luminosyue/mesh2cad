import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,86,0))
r=w0.sketch().arc((-96,-29),(46,89),(1,-100)).arc((35,-72),(48,-32)).arc((50,38),(-14,54)).arc((-74,40),(-96,-29)).assemble().finalize().extrude(-172).union(w0.sketch().arc((-96,-29),(16,38),(56,-83)).arc((31,94),(-96,-29)).assemble().finalize().extrude(-103))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0035_00351536.step')

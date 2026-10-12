import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,56))
r=w0.sketch().arc((-66,0),(58,-31),(-24,58)).arc((-55,34),(-66,0)).assemble().finalize().extrude(-143).union(w1.sketch().arc((-62,21),(56,-34),(-58,30)).arc((-58,25),(-62,21)).assemble().finalize().extrude(-156))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0067_00674807.step')

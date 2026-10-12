import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-16))
r=w0.sketch().arc((-83,8),(-84,10),(-82,10)).arc((-76,12),(-70,10)).arc((-63,1),(-69,-9)).arc((-70,-10),(-71,-11)).arc((-73,-12),(-75,-12)).arc((-88,-19),(-75,-12)).arc((-69,-10),(-65,-6)).arc((-59,19),(-83,8)).assemble().push([(75,0)]).circle(25).circle(12,mode='s').finalize().extrude(32)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0042_00426778.step')

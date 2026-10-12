import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,4,0))
r=w0.sketch().segment((-100,-5),(-92,-5)).segment((-92,-67)).segment((-68,-67)).segment((-75,-58)).segment((-45,-35)).segment((-45,-50)).segment((-38,-50)).segment((-38,-53)).segment((-24,-53)).segment((-24,-50)).segment((-16,-50)).segment((-16,-40)).segment((-6,-59)).segment((-38,-78)).segment((-38,-63)).segment((-45,-63)).segment((-45,-67)).segment((-75,-67)).segment((-75,-63)).segment((-92,-63)).segment((-92,-5)).segment((-61,-5)).segment((-61,13)).segment((-24,32)).segment((-24,17)).segment((-16,17)).segment((-16,27)).segment((-6,19)).segment((-38,-5)).segment((11,-5)).segment((11,5)).segment((29,5)).segment((29,-67)).segment((56,-67)).segment((56,-20)).segment((100,-20)).segment((100,59)).segment((56,59)).segment((56,67)).segment((29,67)).segment((29,39)).segment((11,39)).segment((11,67)).segment((-100,67)).close().assemble().push([(-44,58)]).rect(36,18).finalize().extrude(-7)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__41733_1ec9b00c_0013.step')

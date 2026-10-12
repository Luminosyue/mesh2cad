import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,2,0))
r=w0.sketch().segment((-100,-15),(-93,-17)).segment((-96,-39)).segment((-68,-44)).segment((-66,-39)).segment((-64,-40)).segment((-62,-43)).segment((-59,-45)).segment((-58,-44)).segment((-34,-48)).segment((-33,-44)).segment((-34,-44)).segment((-34,-33)).segment((-24,-16)).segment((-15,-16)).segment((-15,-10)).segment((-19,-10)).segment((-19,-9)).segment((-20,-9)).segment((-19,-10)).segment((-19,-15)).segment((-24,-15)).segment((-24,-16)).segment((-23,-16)).segment((-23,-17)).segment((-70,-10)).segment((-70,-9)).segment((-73,-9)).segment((-73,35)).segment((-78,35)).segment((-75,45)).segment((-94,51)).segment((-99,35)).segment((-96,35)).segment((-96,24)).segment((-98,24)).segment((-98,-9)).segment((-93,-9)).close().assemble().push([(12,-27)]).circle(24).circle(16,mode='s').reset().face(w0.sketch().segment((74,-36),(80,-39)).arc((83,-38),(84,-40)).segment((96,-42)).segment((100,-25)).segment((79,-16)).close().assemble()).finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0012_00121185.step')

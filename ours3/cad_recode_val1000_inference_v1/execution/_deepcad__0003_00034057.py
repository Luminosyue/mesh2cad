import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-30,0,0))
r=w0.sketch().segment((-100,-49),(-31,-49)).segment((-31,-12)).segment((14,-24)).segment((14,-49)).segment((100,-49)).segment((100,48)).segment((89,48)).segment((89,53)).segment((14,53)).segment((14,34)).segment((-31,45)).segment((-31,53)).segment((-100,53)).close().assemble().push([(-65.5,2)]).rect(69,38,mode='s').finalize().extrude(41).union(w0.sketch().segment((-94,-53),(-18,-53)).segment((-18,-52)).segment((-16,-52)).segment((-16,-53)).segment((96,-53)).segment((96,-29)).segment((-94,-29)).close().assemble().finalize().extrude(60))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0003_00034057.step')

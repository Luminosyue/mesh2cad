import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,23))
w1=cq.Workplane('ZX',origin=(0,33,0))
r=w0.sketch().push([(-46,-72.5)]).rect(14,55).push([(46,-72.5)]).rect(14,55).finalize().extrude(-73).union(w0.sketch().segment((-51,-33),(-30,-72)).segment((-29,-72)).arc((12,-98),(47,-65)).segment((51,-63)).segment((30,-24)).segment((29,-24)).arc((-12,-1),(-47,-33)).close().assemble().finalize().extrude(-30)).union(w0.sketch().segment((-25,54),(-18,54)).segment((-18,33)).segment((21,33)).segment((21,54)).segment((27,54)).segment((27,84)).segment((21,84)).segment((21,100)).segment((-18,100)).segment((-18,84)).segment((-25,84)).close().assemble().finalize().extrude(21)).union(w1.sketch().arc((23,18),(49,5),(24,20)).segment((24,18)).close().assemble().finalize().extrude(30))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0061_00610334.step')

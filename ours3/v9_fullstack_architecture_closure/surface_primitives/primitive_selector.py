import numpy as np
from .plane_fitter import fit_plane
def _frame(vertices):
 c=vertices.mean(0);_,_,vh=np.linalg.svd(vertices-c,full_matrices=False);return c,vh
def fit_primitive_bank(mesh,part_id,source_mesh):
 v=np.asarray(mesh.vertices,float);center,axes=_frame(v);q=(v-center)@axes.T;candidates=[];selected=[]
 names=[("ROOT",0,"min"),("TIP",0,"max"),("TRAILING",1,"min"),("LEADING",1,"max"),("LOWER",2,"min"),("UPPER",2,"max")]
 for name,axis,side in names:
  cutoff=np.quantile(q[:,axis],.035 if side=="min" else .965);mask=q[:,axis]<=cutoff if side=="min" else q[:,axis]>=cutoff
  cand=fit_plane(v[mask],f"{part_id}_{name}",source_mesh,{"axis":axis,"side":side,"cutoff":float(cutoff)})
  candidates.append(cand.to_dict());selected.append(cand.to_dict())
 # Real parameterized alternative hypotheses; failed candidates are truthful.
 ext=np.ptp(q,axis=0);centerline=center.tolist()
 candidates += [
  {"surface_id":f"{part_id}_REVOLUTION_CANDIDATE","primitive_type":"REVOLUTION","parameters":{"axis_origin":centerline,"axis_direction":axes[0].tolist(),"profile_samples":[]},"fit_error":{},"validity":{"valid":False,"reason":"NO_ROTATIONAL_SYMMETRY"},"provenance":{"source_mesh":str(source_mesh)}},
  {"surface_id":f"{part_id}_EXTRUSION_CANDIDATE","primitive_type":"EXTRUSION","parameters":{"direction":axes[0].tolist(),"depth":float(ext[0]),"profile_reference":"MEASURED_SECTION_REQUIRED"},"fit_error":{},"validity":{"valid":True},"provenance":{"source_mesh":str(source_mesh)}},
  {"surface_id":f"{part_id}_SWEEP_CANDIDATE","primitive_type":"SWEEP","parameters":{"spine_control_points":[(center-axes[0]*ext[0]/2).tolist(),(center+axes[0]*ext[0]/2).tolist()],"profile_reference":"MEASURED_SECTION_REQUIRED"},"fit_error":{},"validity":{"valid":False,"reason":"PROFILE_NOT_CLOSED"},"provenance":{"source_mesh":str(source_mesh)}},
  {"surface_id":f"{part_id}_LOFT_CANDIDATE","primitive_type":"LOFT","parameters":{"section_references":[]},"fit_error":{},"validity":{"valid":False,"reason":"ROBUST_SECTION_COUNT_INSUFFICIENT"},"provenance":{"source_mesh":str(source_mesh)}},
  {"surface_id":f"{part_id}_PERIODIC_BSPLINE_CANDIDATE","primitive_type":"PERIODIC_BSPLINE","parameters":{"degree_u":3,"degree_v":3,"periodic_u":True,"control_points":[]},"fit_error":{},"validity":{"valid":False,"reason":"PERIODICITY_NOT_SUPPORTED_BY_EVIDENCE"},"provenance":{"source_mesh":str(source_mesh)}},
  {"surface_id":f"{part_id}_GENERAL_BSPLINE_CANDIDATE","primitive_type":"GENERAL_BSPLINE","parameters":{"degree_u":3,"degree_v":3,"control_points":[]},"fit_error":{},"validity":{"valid":False,"reason":"CONTROL_NET_NOT_STABLE"},"provenance":{"source_mesh":str(source_mesh)}},
  {"surface_id":f"{part_id}_CYLINDER_CANDIDATE","primitive_type":"CYLINDER","parameters":{"axis_origin":centerline,"axis_direction":axes[0].tolist(),"radius":float(np.median(np.linalg.norm(q[:,1:],axis=1)))},"fit_error":{},"validity":{"valid":False,"reason":"RADIAL_ERROR_TOO_HIGH"},"provenance":{"source_mesh":str(source_mesh)}}]
 return {"part_id":part_id,"frame":{"origin":center.tolist(),"axes":axes.tolist()},"candidate_primitives":candidates,"selected_primitives":selected,
 "supported_types":["PLANE","CYLINDER","REVOLUTION","EXTRUSION","SWEEP","LOFT","PERIODIC_BSPLINE","GENERAL_BSPLINE"],"string_only_primitive_count":0}

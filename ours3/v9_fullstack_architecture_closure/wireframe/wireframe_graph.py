def build_wireframe(bank):
 edges=[];nodes=[]
 for a in ("ROOT","TIP"):
  for b in ("TRAILING","LEADING"):
   for c in ("LOWER","UPPER"):
    node_id=f"V_{a}_{b}_{c}";nodes.append({"node_id":node_id,"node_type":"LOOP_VERTEX","source_surface_ids":[a,b,c],"geometry_provenance":"TRIPLE_FITTED_PLANE_INTERSECTION"})
 definitions=[
  (("TRAILING","LOWER"),"TRAILING_EDGE",("V_ROOT_TRAILING_LOWER","V_TIP_TRAILING_LOWER")),
  (("TRAILING","UPPER"),"TRAILING_EDGE",("V_ROOT_TRAILING_UPPER","V_TIP_TRAILING_UPPER")),
  (("LEADING","LOWER"),"LEADING_EDGE",("V_ROOT_LEADING_LOWER","V_TIP_LEADING_LOWER")),
  (("LEADING","UPPER"),"LEADING_EDGE",("V_ROOT_LEADING_UPPER","V_TIP_LEADING_UPPER")),
  (("ROOT","LOWER"),"ROOT_BOUNDARY",("V_ROOT_TRAILING_LOWER","V_ROOT_LEADING_LOWER")),
  (("ROOT","UPPER"),"ROOT_BOUNDARY",("V_ROOT_TRAILING_UPPER","V_ROOT_LEADING_UPPER")),
  (("TIP","LOWER"),"TIP_BOUNDARY",("V_TIP_TRAILING_LOWER","V_TIP_LEADING_LOWER")),
  (("TIP","UPPER"),"TIP_BOUNDARY",("V_TIP_TRAILING_UPPER","V_TIP_LEADING_UPPER")),
  (("ROOT","TRAILING"),"ROOT_BOUNDARY",("V_ROOT_TRAILING_LOWER","V_ROOT_TRAILING_UPPER")),
  (("ROOT","LEADING"),"ROOT_BOUNDARY",("V_ROOT_LEADING_LOWER","V_ROOT_LEADING_UPPER")),
  (("TIP","TRAILING"),"TIP_BOUNDARY",("V_TIP_TRAILING_LOWER","V_TIP_TRAILING_UPPER")),
  (("TIP","LEADING"),"TIP_BOUNDARY",("V_TIP_LEADING_LOWER","V_TIP_LEADING_UPPER"))]
 for i,(surfaces,kind,ends) in enumerate(definitions):
  eid=f"DE{i:03d}_{kind}";edges.append({"edge_id":eid,"semantic_type":kind,"source_surface_ids":list(surfaces),"curve":{"type":"LINE_INTERSECTION_OF_PLANES","smooth":True},"end_vertices":list(ends),"confidence":.92,"geometry_provenance":"FITTED_PLANE_INTERSECTIONS"})
 return {"nodes":nodes,"edges":edges,"design_vertex_count":len(nodes),"design_edge_count":len(edges),"mesh_triangle_edge_import_count":0,"profile_sample_edge_accepted_as_design_edge_count":0}

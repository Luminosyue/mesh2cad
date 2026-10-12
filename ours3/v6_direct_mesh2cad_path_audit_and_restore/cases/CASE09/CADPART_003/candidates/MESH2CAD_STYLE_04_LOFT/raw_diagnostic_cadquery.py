import cadquery as cq

# Define mesh profile
profile = cq.Workplane('XY').box(mesh_bounds[1]-mesh_bounds[0], mesh_bounds[3]-mesh_bounds[2], 0.01)

# Loft profile
lofted = profile.loft(mesh_bounds[5]-mesh_bounds[4])

# Return lofted shape
lofted
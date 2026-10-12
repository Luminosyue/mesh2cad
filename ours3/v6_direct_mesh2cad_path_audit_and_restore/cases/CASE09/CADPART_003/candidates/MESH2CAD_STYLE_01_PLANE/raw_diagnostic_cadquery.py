import cadquery as cq

# Extract mesh bounds and create plane
mesh_bounds = [min(v[0] for v in vertices), max(v[0] for v in vertices),
               min(v[1] for v in vertices), max(v[1] for v in vertices),
               min(v[2] for v in vertices), max(v[2] for v in vertices)]

# Create plane from bounds
plane = cq.Workplane('XY').box(mesh_bounds[1]-mesh_bounds[0], mesh_bounds[3]-mesh_bounds[2], mesh_bounds[5]-mesh_bounds[4])

# Apply mesh topology constraints
plane = plane.moveTo(mesh_bounds[0], mesh_bounds[1], mesh_bounds[4])

# Return plane
plane
import cadquery as cq

# Define a 2D profile
profile = cq.Workplane('XY').moveTo(0, 0, 0).lineTo(0.05, 0, 0).lineTo(0.05, 0.05, 0).close()

# Extrude along a vector
extruded_surface = cq.Workplane('XY').extrude(profile, vector=(0, 0, 0.1))

# Apply smoothing
smoothed_surface = extruded_surface.smooth()

# Return the constructed shape
smoothed_surface
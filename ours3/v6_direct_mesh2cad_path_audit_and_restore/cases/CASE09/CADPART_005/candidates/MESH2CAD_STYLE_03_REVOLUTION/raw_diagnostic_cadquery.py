import cadquery as cq

# Define a 2D profile
profile = cq.Workplane('XY').moveTo(0, 0, 0).lineTo(0.05, 0, 0).lineTo(0.05, 0.05, 0).close()

# Revolve around an axis
revolved_surface = cq.Workplane('XY').revolve(profile, axis=(0, 0, 0.1))

# Apply smoothing
smoothed_surface = revolved_surface.smooth()

# Return the constructed shape
smoothed_surface
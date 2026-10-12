import cadquery as cq

# Define two cross-section profiles
profile1 = cq.Workplane('XY').moveTo(0, 0, 0).lineTo(0.05, 0, 0).lineTo(0.05, 0.05, 0).close()
profile2 = cq.Workplane('XY').moveTo(0, 0, 0.1).lineTo(0.05, 0, 0.1).lineTo(0.05, 0.05, 0.1).close()

# Loft between profiles
lofted_surface = cq.Workplane('XY').loft([profile1, profile2])

# Apply smoothing
smoothed_surface = lofted_surface.smooth()

# Return the constructed shape
smoothed_surface
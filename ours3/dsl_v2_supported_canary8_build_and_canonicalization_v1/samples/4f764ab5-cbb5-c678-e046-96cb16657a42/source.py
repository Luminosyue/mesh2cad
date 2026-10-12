import cadquery as cq
import math
max_dim = 100
shaft_diameter = 20.0
collar_width = 30.0
outer_diameter = 50.0
key_width = 6.0
key_depth = 4.0
undercut_depth = 2.0
undercut_length = 5.0
chamfer_size = 0.5
mount_hole_dia = 4.0
mount_hole_circle_radius = 20.0
inner_radius = shaft_diameter / 2.0
outer_radius = outer_diameter / 2.0
# Create 2D profile for revolve
profile = (
    cq.Workplane("XZ")
    .moveTo(inner_radius, 0)
    .lineTo(outer_radius, 0)
    .lineTo(outer_radius, collar_width - undercut_length)
    .lineTo(outer_radius - undercut_depth, collar_width - undercut_length)
    .lineTo(outer_radius - undercut_depth, collar_width)
    .lineTo(inner_radius, collar_width)
    .close()
)
# Revolve profile around Z axis to create collar
collar = profile.revolve(360)
# Create keyway cut
keyway = (
    cq.Workplane("YZ")
    .center(inner_radius - key_depth / 2.0, collar_width / 2.0)
    .rect(key_depth, key_width)
    .extrude(collar_width + 2.0)
)
# Subtract keyway
collar = collar.cut(keyway)
# Undercut cylinder to remove material from outer face
undercut_cyl = (
    cq.Workplane("XY")
    .circle(outer_radius - undercut_depth)
    .extrude(undercut_length)
    .translate((0, 0, collar_width - undercut_length))
)
collar = collar.cut(undercut_cyl)
# Add mounting holes around circumference
for i in range(4):
    angle = i * math.pi / 2.0
    x = mount_hole_circle_radius * math.cos(angle)
    y = mount_hole_circle_radius * math.sin(angle)
    hole = (
        cq.Workplane("XY")
        .center(x, y)
        .circle(mount_hole_dia / 2.0)
        .extrude(collar_width + 2.0)
    )
    collar = collar.cut(hole)
# Apply chamfer to outer cylindrical edges
result = collar.edges("|Z").chamfer(chamfer_size)

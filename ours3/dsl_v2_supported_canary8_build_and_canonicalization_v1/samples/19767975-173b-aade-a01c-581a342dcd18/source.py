import cadquery as cq

# Parameters
plate_width = 80.0
plate_depth = 60.0
plate_thickness = 4.0
plate_chamfer = 0.5
rib_height = 2.0
rib_width = 10.0
rib_depth = 30.0
socket_width = 30.0
socket_depth = 20.0
socket_height = 6.0
socket_cyl_dia = 8.0
side_cut_width = 6.0
side_cut_depth = 12.0
side_cut_offset = 12.0

# Base plate
base_plate = (
    cq.Workplane("XY")
    .rect(plate_width, plate_depth)
    .extrude(plate_thickness)
)

# Top rib (adds material on top)
rib = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(rib_width, rib_depth)
    .extrude(rib_height)
    .translate((0, 0, plate_thickness))
)

# Socket cavity (rectangular pocket with central cylinder and side cutouts)
socket_pocket = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(socket_width, socket_depth)
    .extrude(-socket_height)
)

cyl_cut = (
    cq.Workplane("XY")
    .center(0, 0)
    .circle(socket_cyl_dia / 2)
    .extrude(-socket_height)
)

side_cut_1 = (
    cq.Workplane("XY")
    .center(-socket_width/2 + side_cut_offset, 0)
    .rect(side_cut_width, side_cut_depth)
    .extrude(-socket_height)
)

side_cut_2 = (
    cq.Workplane("XY")
    .center(socket_width/2 - side_cut_offset, 0)
    .rect(side_cut_width, side_cut_depth)
    .extrude(-socket_height)
)

# Combine all cut features
socket_cut = socket_pocket.union(cyl_cut).union(side_cut_1).union(side_cut_2)

# Apply cuts to plate
plate_with_socket = base_plate.cut(socket_cut)

# Add rib
plate_with_rib = plate_with_socket.union(rib)

# Apply chamfer to front edges (positive Y direction)
result = (
    plate_with_rib
    .edges("<Y and |Z")
    .chamfer(plate_chamfer)
)

#!/usr/bin/env python3
import sys
import cadquery as cq

for value in sys.argv[1:]:
    shape = cq.importers.importStep(value).val()
    box = shape.BoundingBox()
    print(value, [box.xmin, box.xmax, box.ymin, box.ymax, box.zmin, box.zmax], shape.Volume())

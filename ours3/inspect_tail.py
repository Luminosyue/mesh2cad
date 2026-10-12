from pathlib import Path

from v13_transform_restore_and_xcaf_assembly.assembly.assembly_quality_audit import (
    count_pcurves_and_trimmed_faces,
    shared_occ_edge_count,
)
from v13_transform_restore_and_xcaf_assembly.assembly.xcaf_assembly_builder import load_step_shape
from v13_transform_restore_and_xcaf_assembly.assembly.placement_validator import shape_counts

path = Path(
    "/data/home/cuiyuehan/project/mesh2cad/ours3/v12_full_cad_part_router/"
    "cases/CASE09/parts/CADPART_005/selected/generated.step"
)
shape = load_step_shape(path)
print("TYPE", shape.ShapeType())
print("COUNTS", shape_counts(shape))
print("OPEN", shared_occ_edge_count(shape), count_pcurves_and_trimmed_faces(shape))

from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDocStd import TDocStd_Document
from OCP.TDF import TDF_LabelSequence
from OCP.XCAFApp import XCAFApp_Application
from OCP.XCAFDoc import XCAFDoc_DocumentTool

reader = STEPCAFControl_Reader()
print("CAF_READ", reader.ReadFile(str(path)) == IFSelect_RetDone)
doc = TDocStd_Document(TCollection_ExtendedString("I"))
app = XCAFApp_Application.GetApplication_s()
app.NewDocument(TCollection_ExtendedString("I"), doc)
app.InitDocument(doc)
print("CAF_TRANSFER", reader.Transfer(doc))
tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
roots = TDF_LabelSequence()
tool.GetFreeShapes(roots)
for i in range(1, roots.Length() + 1):
    caf_shape = tool.GetShape_s(roots.Value(i))
    print("CAF", caf_shape.ShapeType(), shape_counts(caf_shape), shared_occ_edge_count(caf_shape), count_pcurves_and_trimmed_faces(caf_shape))

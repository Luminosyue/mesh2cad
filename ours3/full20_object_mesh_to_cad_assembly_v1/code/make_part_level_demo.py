import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
EXP = ROOT / 'ours3/full20_object_mesh_to_cad_assembly_v1'
OBJ = 'aroma_stainless_steel_milk_frother_2_cup'
FREE = EXP / 'model_v1/generated' / OBJ / 'free_320'
OBJ_DIR = EXP / 'objects' / OBJ
OUT = EXP / 'paper_demo/MILK_FROTHER_PART_LEVEL_DEMO.png'

sys.path.insert(0, str(EXP / 'code'))
import pipeline as pipe


def font(size):
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)


def render_meshes(meshes, center, extent, colors, output, opacity=None, size=(760, 560)):
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray, vtk_to_numpy

    ren = vtk.vtkRenderer()
    ren.SetBackground(0.965, 0.975, 0.985)
    for i, (m, color) in enumerate(zip(meshes, colors)):
        xyz = (np.asarray(m.vertices) - center) / extent
        poly = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        points.SetData(numpy_to_vtk(xyz, deep=True))
        poly.SetPoints(points)
        cells = vtk.vtkCellArray()
        packed = np.c_[np.full(len(m.faces), 3), m.faces].ravel().astype(np.int64)
        cells.SetCells(len(m.faces), numpy_to_vtkIdTypeArray(packed, deep=True))
        poly.SetPolys(cells)
        normals = vtk.vtkPolyDataNormals()
        normals.SetInputData(poly)
        normals.SetFeatureAngle(55)
        normals.SplittingOn()
        normals.Update()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(normals.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        prop = actor.GetProperty()
        prop.SetColor(*color)
        prop.SetAmbient(0.28)
        prop.SetDiffuse(0.72)
        prop.SetSpecular(0.25)
        prop.SetSpecularPower(28)
        prop.EdgeVisibilityOff()
        if opacity is not None:
            prop.SetOpacity(opacity[i] if isinstance(opacity, (list, tuple)) else opacity)
        ren.AddActor(actor)

    camera = ren.GetActiveCamera()
    camera.ParallelProjectionOn()
    camera.SetPosition(2.5, 1.8, -2.8)
    camera.SetViewUp(0, 0, -1)
    camera.SetFocalPoint(0, 0, 0)
    ren.ResetCamera()
    camera.Zoom(1.05)
    ren.ResetCameraClippingRange()
    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.SetSize(*size)
    win.SetMultiSamples(4)
    win.AddRenderer(ren)
    win.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(win)
    capture.Update()
    arr = vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars()).reshape(size[1], size[0], 3)
    Image.fromarray(arr[::-1].copy()).save(output)
    win.Finalize()


def main():
    gate = json.loads((FREE / 'OBJECT_GATE.json').read_text())
    frame = json.loads((OBJ_DIR / 'OBJECT_FRAME.json').read_text())
    center = np.array(frame['center'], dtype=float)
    extent = 1.0 / float(frame['scale'])
    rows = list(csv.DictReader((OBJ_DIR / 'PART_MANIFEST.csv').open()))
    work = FREE / 'part_level_renders'
    work.mkdir(exist_ok=True)
    cad_meshes = []
    input_meshes = []
    for row in rows:
        pid = row['PART_ID']
        input_mesh = pipe.mesh(row['PART_MESH_PATH'])
        import cadquery as cq
        shape = cq.importers.importStep(str(FREE / 'parts' / pid / 'part.step')).val()
        cad_mesh = pipe.shapemesh(shape)
        input_meshes.append(input_mesh)
        cad_meshes.append(cad_mesh)
        render_meshes([input_mesh], center, extent, [(0.56, 0.63, 0.70)], work / f'{pid}_input.png')
        render_meshes([cad_mesh], center, extent, [(0.18, 0.48, 0.72)], work / f'{pid}_cad.png')
        render_meshes([input_mesh, cad_mesh], center, extent, [(0.92, 0.35, 0.20), (0.18, 0.55, 0.82)], work / f'{pid}_overlay.png', [0.28, 0.82])

    assembly_path = work / 'assembly.png'
    render_meshes(cad_meshes, center, extent, [(0.18, 0.48, 0.72)] * len(cad_meshes), assembly_path, size=(1550, 620))

    cell_w, cell_h = 430, 315
    margin_l, margin_t = 185, 170
    gap_x, gap_y = 22, 22
    assembly_h = 430
    canvas_w = margin_l + len(rows) * (cell_w + gap_x) + 24
    canvas_h = margin_t + 3 * (cell_h + gap_y) + assembly_h + 90
    canvas = Image.new('RGB', (canvas_w, canvas_h), 'white')
    draw = ImageDraw.Draw(canvas)
    title = font(34)
    subtitle = font(19)
    label = font(20)
    small = font(17)
    draw.text((margin_l, 22), 'Milk Frother | Full-sequence Mesh-to-CAD', font=title, fill='#142c3d')
    draw.text((margin_l, 72), 'P1 model-generated | q14 + Compact IR V3 | empty-target greedy | no GT prefix | natural EOS', font=subtitle, fill='#35586c')
    draw.text((margin_l, 104), f"free exact {gate['free_exact_n']}/{gate['required_parts']} | CAD/BRep {gate['cad_pass_n']}/{gate['required_parts']} | original object coordinates | no ICP", font=subtitle, fill='#35586c')
    row_names = ['Input mesh', 'Generated CAD', 'Overlay']
    for ri, name in enumerate(row_names):
        y = margin_t + ri * (cell_h + gap_y)
        draw.text((20, y + cell_h // 2 - 12), name, font=label, fill='#203746')
    for ci, row in enumerate(rows):
        x = margin_l + ci * (cell_w + gap_x)
        pid = row['PART_ID']
        draw.text((x + 8, margin_t - 34), pid, font=label, fill='#17384d')
        for ri, suffix in enumerate(['input', 'cad', 'overlay']):
            y = margin_t + ri * (cell_h + gap_y)
            im = Image.open(work / f'{pid}_{suffix}.png').convert('RGB')
            im.thumbnail((cell_w, cell_h), Image.Resampling.LANCZOS)
            canvas.paste(im, (x + (cell_w - im.width) // 2, y + (cell_h - im.height) // 2))
    ay = margin_t + 3 * (cell_h + gap_y) + 4
    draw.text((20, ay + assembly_h // 2 - 12), 'Complete\nCAD assembly', font=label, fill='#203746')
    im = Image.open(assembly_path).convert('RGB')
    im.thumbnail((canvas_w - margin_l - 24, assembly_h), Image.Resampling.LANCZOS)
    canvas.paste(im, (margin_l + (canvas_w - margin_l - 24 - im.width) // 2, ay + (assembly_h - im.height) // 2))
    metrics = gate['metrics']
    fy = canvas_h - 56
    draw.text((margin_l, fy), f"Measured mesh-vs-CAD: CD {metrics['CD']:.6f} | surface IoU64 {metrics['IOU']:.6f} | volume error {metrics['VOLUME_ERROR']:.2%} | texture reconstruction out of scope", font=small, fill='#35586c')
    OUT.parent.mkdir(exist_ok=True)
    canvas.save(OUT, quality=95)
    print(OUT)


if __name__ == '__main__':
    main()

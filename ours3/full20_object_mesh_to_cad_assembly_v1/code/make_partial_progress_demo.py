import csv
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
EXP = ROOT / 'ours3/full20_object_mesh_to_cad_assembly_v1'
ITEMS = [
    ('speaker_big', 'free_320', 'Speaker Big'),
    ('android_figure_orange', 'free_640', 'Android Figure'),
    ('cube', 'free_640', 'Cube'),
    ('baby_car', 'free_640', 'Baby Car'),
    ('dvd_player', 'free_80', 'DVD Player'),
]
OUT = EXP / 'paper_demo/PARTIAL_FREE_GENERATED_PROGRESS.png'
sys.path.insert(0, str(EXP / 'code'))
import pipeline as pipe


def fnt(n):
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', n)


def render(meshes, center, extent, colors, path, size=(760, 420)):
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray, vtk_to_numpy
    ren = vtk.vtkRenderer()
    ren.SetBackground(0.965, 0.975, 0.985)
    for m, color in zip(meshes, colors):
        xyz = (np.asarray(m.vertices) - center) / extent
        poly = vtk.vtkPolyData(); points = vtk.vtkPoints(); points.SetData(numpy_to_vtk(xyz, deep=True)); poly.SetPoints(points)
        cells = vtk.vtkCellArray(); packed = np.c_[np.full(len(m.faces), 3), m.faces].ravel().astype(np.int64); cells.SetCells(len(m.faces), numpy_to_vtkIdTypeArray(packed, deep=True)); poly.SetPolys(cells)
        normals = vtk.vtkPolyDataNormals(); normals.SetInputData(poly); normals.SetFeatureAngle(55); normals.SplittingOn(); normals.Update()
        mapper = vtk.vtkPolyDataMapper(); mapper.SetInputConnection(normals.GetOutputPort())
        actor = vtk.vtkActor(); actor.SetMapper(mapper); prop = actor.GetProperty(); prop.SetColor(*color); prop.SetAmbient(.28); prop.SetDiffuse(.72); prop.SetSpecular(.25); prop.SetSpecularPower(28); prop.EdgeVisibilityOff(); ren.AddActor(actor)
    cam = ren.GetActiveCamera(); cam.ParallelProjectionOn(); cam.SetPosition(2.5, 1.8, -2.8); cam.SetViewUp(0, 0, -1); cam.SetFocalPoint(0, 0, 0); ren.ResetCamera(); cam.Zoom(1.05); ren.ResetCameraClippingRange()
    win = vtk.vtkRenderWindow(); win.SetOffScreenRendering(1); win.SetSize(*size); win.SetMultiSamples(4); win.AddRenderer(ren); win.Render()
    cap = vtk.vtkWindowToImageFilter(); cap.SetInput(win); cap.Update(); arr = vtk_to_numpy(cap.GetOutput().GetPointData().GetScalars()).reshape(size[1], size[0], 3); Image.fromarray(arr[::-1].copy()).save(path); win.Finalize()


def main():
    tiles = []
    tmp = EXP / 'paper_demo/partial_progress_renders'; tmp.mkdir(exist_ok=True)
    for obj, free_name, pretty in ITEMS:
        free = EXP / 'model_v1/generated' / obj / free_name
        gate = json.loads((free / 'OBJECT_GATE.json').read_text())
        obj_dir = EXP / 'objects' / obj
        frame = json.loads((obj_dir / 'OBJECT_FRAME.json').read_text()); center = np.array(frame['center'], dtype=float); extent = 1.0 / float(frame['scale'])
        rows = {r['PART_ID']: r for r in csv.DictReader((obj_dir / 'PART_MANIFEST.csv').open())}
        pids = sorted([p.name for p in (free / 'parts').glob('PART_*') if (p / 'part.step').exists()])
        inputs = [pipe.mesh(rows[pid]['PART_MESH_PATH']) for pid in pids]
        import cadquery as cq
        cads = [pipe.shapemesh(cq.importers.importStep(str(free / 'parts' / pid / 'part.step')).val()) for pid in pids]
        ip = tmp / f'{obj}_input.png'; cp = tmp / f'{obj}_cad.png'
        render(inputs, center, extent, [(0.56, .63, .70)] * len(inputs), ip); render(cads, center, extent, [(0.18, .48, .72)] * len(cads), cp)
        tiles.append((pretty, gate, ip, cp, len(pids)))

    cols, card_w, card_h, gap = 2, 760, 500, 28
    width = cols * card_w + (cols + 1) * gap; rows_n = (len(tiles) + cols - 1) // cols
    canvas = Image.new('RGB', (width, 170 + rows_n * (card_h + gap) + 70), 'white'); d = ImageDraw.Draw(canvas)
    d.text((gap, 22), 'Latest P1 Free-generation Progress', font=fnt(34), fill='#142c3d')
    d.text((gap, 72), 'Model-generated Compact IR V3 parts | empty-target greedy | no GT prefix | natural EOS', font=fnt(19), fill='#35586c')
    d.text((gap, 106), 'Partial objects are shown for progress only; full CAD assembly remains pending until every required part passes.', font=fnt(18), fill='#8a4d32')
    for i, (pretty, gate, ip, cp, n) in enumerate(tiles):
        x = gap + (i % cols) * (card_w + gap); y = 160 + (i // cols) * (card_h + gap)
        d.text((x, y), f'{pretty}  |  free exact {gate.get("free_exact_n", 0)}/{gate.get("required_parts", "?")}  |  assembly PENDING', font=fnt(22), fill='#17384d')
        for j, src in enumerate([ip, cp]):
            im = Image.open(src).convert('RGB'); im.thumbnail((card_w // 2 - 8, 375), Image.Resampling.LANCZOS); px = x + j * (card_w // 2) + (card_w // 2 - im.width) // 2; py = y + 45 + (375 - im.height) // 2; canvas.paste(im, (px, py))
        d.text((x + 40, y + 425), 'Input part meshes' if True else '', font=fnt(17), fill='#35586c')
        d.text((x + card_w // 2 + 40, y + 425), 'Generated CAD parts', font=fnt(17), fill='#35586c')
    d.text((gap, canvas.height - 42), 'These previews do not count as FULL_MODEL_ASSEMBLY_PASS. Texture reconstruction is out of scope.', font=fnt(17), fill='#35586c')
    OUT.parent.mkdir(exist_ok=True); canvas.save(OUT, quality=95); print(OUT)


if __name__ == '__main__':
    main()

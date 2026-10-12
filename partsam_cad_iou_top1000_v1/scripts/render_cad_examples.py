"""Render actual CAD reconstruction surfaces from evaluated PartSAM cases."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
import vtk


ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1')
DEST = ROOT / 'plots' / 'cad_renders'
CASES = [
    ('002e462c8bfa4267a9c9f038c7966f3b_part_003', 'High fidelity'),
    ('ed24b6e27921449f935509d9f3da043f_part_009', 'Threshold pass'),
    ('dd76ce99626246889beeb477d6ad2c17_part_011', 'Below threshold'),
    ('f121301624174b179ca4d50158797b03_part_014', 'Poor fit'),
]
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def render(case_id: str) -> Image.Image:
    case_dir = ROOT / 'candidates' / case_id
    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(case_dir / 'reconstructed.stl'))
    reader.Update()
    mesh = reader.GetOutput()
    if mesh.GetNumberOfPolys() == 0:
        raise ValueError(f'Empty reconstructed STL: {case_id}')

    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(reader.GetOutputPort())
    normals.ConsistencyOn()
    normals.SplittingOff()
    normals.Update()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    mapper.ScalarVisibilityOff()
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.16, 0.48, 0.72)
    actor.GetProperty().SetAmbient(0.2)
    actor.GetProperty().SetDiffuse(0.75)
    actor.GetProperty().SetSpecular(0.24)
    actor.GetProperty().SetSpecularPower(22)
    actor.GetProperty().SetInterpolationToPhong()

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.985, 0.99, 0.995)
    renderer.AddActor(actor)
    bounds = mesh.GetBounds()
    center = tuple((bounds[2*i] + bounds[2*i+1]) / 2 for i in range(3))
    extent = max(bounds[2*i+1] - bounds[2*i] for i in range(3))
    camera = renderer.GetActiveCamera()
    camera.SetFocalPoint(*center)
    camera.SetPosition(center[0] + 1.4*extent, center[1] - 1.6*extent, center[2] + 1.2*extent)
    camera.SetViewUp(0, 0, 1)
    camera.ParallelProjectionOn()
    renderer.ResetCamera()
    camera.Zoom(1.12)

    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(1000, 700)
    window.SetMultiSamples(4)
    window.AddRenderer(renderer)
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.ReadFrontBufferOff()
    capture.Update()
    out = DEST / f'{case_id}.png'
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(out))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()
    print(case_id, mesh.GetNumberOfPolys(), out, flush=True)
    return Image.open(out).convert('RGB')


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    canvas = Image.new('RGB', (2000, 1520), '#f3f5f7')
    draw = ImageDraw.Draw(canvas)
    label_font = ImageFont.truetype(FONT, 27)
    small_font = ImageFont.truetype(FONT, 18)
    for index, (case_id, label) in enumerate(CASES):
        image = render(case_id)
        metrics = json.loads((ROOT / 'candidates' / case_id / 'metrics.json').read_text())
        x = index % 2 * 1000
        y = index // 2 * 760
        canvas.paste(image, (x, y + 60))
        draw.rectangle((x, y, x + 999, y + 59), fill='#ffffff')
        draw.text((x + 25, y + 7), f'{label}  |  IoU128 {metrics["iou128"]:.4f}', font=label_font, fill='#222b33')
        draw.text((x + 25, y + 39), case_id, font=small_font, fill='#68747e')
    out = DEST / 'cad_surface_comparison.png'
    canvas.save(out, optimize=True)
    print('COMPARISON', out, flush=True)


if __name__ == '__main__':
    main()

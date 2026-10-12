#!/usr/bin/env python3
"""Render overall + per-part previews for BUILD_A_ROBOT Qwen3-VL MAC v3."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pyvista as pv
import trimesh
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/build_a_robot_pipeline_a_qwen3vl_mac_v3")
OUT = ROOT / "artifacts" / "shaded_3d"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
CAD_ORANGE = "#d95f02"
FACET_GRAY = "#8b98a8"
SOURCE_GRAY = "#c5c9ce"
MAC_TEAL = "#2c7fb8"
OVERLAY_CAD = "#e6550d"

VIEWS = {
    "iso_front_left": (-1.25, -1.65, 1.15),
    "iso_front_right": (1.35, -1.55, 1.05),
    "high_orbit": (-0.55, -1.15, 2.15),
    "side": (1.85, 0.05, 0.35),
}


def font(size: int) -> ImageFont.ImageFont:
    return ImageFont.truetype(FONT, size) if Path(FONT).is_file() else ImageFont.load_default()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def load_mesh(path: Path) -> trimesh.Trimesh | None:
    if not path.is_file():
        return None
    mesh = trimesh.load(path, force="mesh", process=False)
    if mesh is None or len(getattr(mesh, "faces", [])) == 0:
        return None
    return mesh


def to_poly(mesh: trimesh.Trimesh, face_limit: int = 90000) -> pv.PolyData:
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(faces) > face_limit:
        faces = faces[np.linspace(0, len(faces) - 1, face_limit, dtype=np.int64)]
    encoded = np.column_stack((np.full(len(faces), 3, dtype=np.int64), faces)).ravel()
    poly = pv.PolyData(vertices, encoded)
    try:
        poly = poly.compute_normals(
            cell_normals=False,
            point_normals=True,
            split_vertices=False,
            consistent_normals=True,
            auto_orient_normals=False,
        )
    except Exception:
        pass
    return poly


def bounds_of(meshes: list[trimesh.Trimesh]) -> np.ndarray:
    pts = np.vstack([np.asarray(m.vertices) for m in meshes if m is not None and len(m.vertices)])
    return np.vstack((pts.min(axis=0), pts.max(axis=0)))


def camera_from_bounds(bounds: np.ndarray, direction: tuple[float, float, float], scale_factor: float = 0.62):
    bounds = np.asarray(bounds, dtype=float)
    center = bounds.mean(axis=0)
    diag = max(float(np.linalg.norm(bounds[1] - bounds[0])), 1e-6)
    direction = np.asarray(direction, dtype=float)
    direction = direction / np.linalg.norm(direction)
    up = (0.0, 0.0, 1.0) if abs(direction[2]) < 0.95 else (0.0, 1.0, 0.0)
    return [tuple(center + direction * diag * 3.2), tuple(center), up], diag * scale_factor


def render_items(
    items: list[tuple[pv.PolyData, str, float]],
    bounds: np.ndarray,
    path: Path,
    direction: tuple[float, float, float],
    window: tuple[int, int] = (1100, 900),
) -> None:
    plotter = pv.Plotter(off_screen=True, window_size=window)
    plotter.set_background("#f4f6f8")
    for poly, color, opacity in items:
        plotter.add_mesh(
            poly,
            color=color,
            opacity=opacity,
            smooth_shading=True,
            show_edges=False,
            ambient=0.30,
            diffuse=0.68,
            specular=0.18,
            specular_power=22,
        )
    camera, scale = camera_from_bounds(bounds, direction)
    plotter.camera.parallel_projection = True
    plotter.camera_position = camera
    plotter.camera.parallel_scale = scale
    try:
        plotter.enable_anti_aliasing("fxaa")
        plotter.add_light(pv.Light(position=(4, -5, 7), focal_point=camera[1], color="white", intensity=0.85))
        plotter.add_light(pv.Light(position=(-4, 3, 2), focal_point=camera[1], color="#dbe7f5", intensity=0.35))
    except Exception:
        pass
    plotter.reset_camera_clipping_range()
    path.parent.mkdir(parents=True, exist_ok=True)
    plotter.screenshot(str(path))
    plotter.close()


def caption(image: Image.Image, title: str, subtitle: str = "") -> Image.Image:
    image = image.convert("RGB")
    pad = 72 if subtitle else 54
    canvas = Image.new("RGB", (image.width, image.height + pad), "#f4f6f8")
    canvas.paste(image, (0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, image.height, image.width, image.height + pad), fill="#ffffff")
    draw.line((0, image.height, image.width, image.height), fill="#d7dbe0", width=1)
    draw.text((18, image.height + 10), title, font=font(22), fill=(28, 36, 46))
    if subtitle:
        draw.text((18, image.height + 40), subtitle, font=font(15), fill=(90, 98, 108))
    return canvas


def hstack(images: list[Image.Image], path: Path, gap: int = 10) -> None:
    height = max(im.height for im in images)
    width = sum(im.width for im in images) + gap * (len(images) - 1)
    canvas = Image.new("RGB", (width, height), "#f4f6f8")
    x = 0
    for im in images:
        canvas.paste(im, (x, (height - im.height) // 2))
        x += im.width + gap
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, dpi=(160, 160))


def grid(images: list[Image.Image], cols: int, path: Path, gap: int = 8) -> None:
    rows = (len(images) + cols - 1) // cols
    cell_w = max(im.width for im in images)
    cell_h = max(im.height for im in images)
    canvas = Image.new("RGB", (cols * cell_w + gap * (cols - 1), rows * cell_h + gap * (rows - 1)), "#f4f6f8")
    for i, im in enumerate(images):
        r, c = divmod(i, cols)
        canvas.paste(im, (c * (cell_w + gap), r * (cell_h + gap)))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, dpi=(150, 150))


def metric(qa: dict, key: str, digits: int = 3) -> str:
    value = qa.get(key)
    if value is None:
        return "—"
    return f"{float(value):.{digits}f}"


def load_components() -> list[dict]:
    selected_rows = {}
    matrix = ROOT / "artifacts" / "candidate_matrix.csv"
    with matrix.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("selected") == "True":
                selected_rows[row["component_id"]] = row
    parts: list[dict] = []
    for component_dir in sorted((ROOT / "03_components").glob("P3_COMPONENT_*")):
        cid = component_dir.name
        selected = load_json(component_dir / "11_selected" / "selected_manifest.json")
        mac_qa = load_json(component_dir / "08_qa" / "MAC_CANDIDATE_01" / "qa.json")
        v6_qa = load_json(component_dir / "08_qa" / "CURRENT_V6_PROFILE_LOFT" / "qa.json")
        source = load_mesh(component_dir / "01_prepare" / "source_part.obj")
        mac = load_mesh(component_dir / "08_qa" / "MAC_CANDIDATE_01" / "MAC_CANDIDATE_01.stl")
        v6 = load_mesh(component_dir / "08_qa" / "CURRENT_V6_PROFILE_LOFT" / "CURRENT_V6_PROFILE_LOFT.stl")
        native = bool(selected.get("cad_native"))
        backend = str(selected.get("selected_backend") or selected_rows.get(cid, {}).get("backend") or "")
        cad_mesh = mac if native and mac is not None else (v6 if native else source)
        cad_label = "MAC CAD" if mac is not None else ("CURRENT_V6 loft" if v6 is not None else "no CAD mesh")
        parts.append(
            {
                "id": cid,
                "short": cid.replace("P3_COMPONENT_", ""),
                "native": native,
                "backend": backend,
                "source": source,
                "mac": mac,
                "v6": v6,
                "cad": cad_mesh,
                "selected": source if not native else cad_mesh,
                "mac_qa": mac_qa,
                "v6_qa": v6_qa,
                "cad_label": cad_label,
            }
        )
    return parts


def write_html(parts: list[dict]) -> None:
    native = [p["short"] for p in parts if p["native"]]
    html = f"""<!doctype html>
<html lang="zh">
<head>
  <meta charset="utf-8"/>
  <title>BUILD_A_ROBOT Qwen3-VL MAC v3 preview</title>
  <style>
    body {{ font-family: sans-serif; margin: 0; background: #f4f6f8; color: #222; }}
    header {{ padding: 16px 20px; background: #fff; border-bottom: 1px solid #ddd; }}
    main {{ padding: 16px 20px 40px; max-width: 1280px; margin: 0 auto; }}
    img {{ width: 100%; border: 1px solid #d7dbe0; background: #fff; }}
    .grid {{ display: grid; gap: 16px; }}
    .two {{ grid-template-columns: 1fr; }}
    @media (min-width: 900px) {{ .two {{ grid-template-columns: 1fr 1fr; }} }}
    canvas {{ width: 100%; height: 640px; display: block; background: #e8edf2; border: 1px solid #d7dbe0; }}
    p {{ color: #444; }}
  </style>
</head>
<body>
  <header>
    <h1>BUILD_A_ROBOT Qwen3-VL + MAC v3</h1>
    <p>橙色 = CAD-native（{"、".join(native) or "无"}）· 灰蓝 = faceted fallback。下面可拖动旋转。</p>
  </header>
  <main>
    <h2>可旋转 3D</h2>
    <canvas id="view"></canvas>
    <h2>整体效果</h2>
    <div class="grid two">
      <img src="final_cad_iso_front_left_captioned.png" alt="source vs mixed"/>
      <img src="final_cad_iso_front_right.png" alt="mixed opposite"/>
      <img src="final_cad_high_orbit.png" alt="high orbit"/>
      <img src="final_cad_native_only_captioned.png" alt="CAD native only"/>
    </div>
    <h2>各零件</h2>
    <div class="grid two">
      <img src="parts_grid_selected.png" alt="selected parts"/>
      <img src="parts_grid_mac.png" alt="MAC CAD"/>
    </div>
  </main>
  <script type="importmap">
  {{ "imports": {{
      "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
      "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
  }}}}
  </script>
  <script type="module">
    import * as THREE from "three";
    import {{ GLTFLoader }} from "three/addons/loaders/GLTFLoader.js";
    import {{ OrbitControls }} from "three/addons/controls/OrbitControls.js";
    const canvas = document.getElementById("view");
    const renderer = new THREE.WebGLRenderer({{ canvas, antialias: true }});
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xe8edf2);
    const camera = new THREE.PerspectiveCamera(42, 2, 0.01, 50);
    camera.position.set(-2.2, -2.6, 1.5);
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    scene.add(new THREE.AmbientLight(0xffffff, 0.7));
    const key = new THREE.DirectionalLight(0xffffff, 1.05);
    key.position.set(-2, -3, 4);
    scene.add(key);
    scene.add(new THREE.HemisphereLight(0xdde6ff, 0x8a8f96, 0.55));
    function resize() {{
      const w = canvas.clientWidth, h = canvas.clientHeight;
      renderer.setSize(w, h, false);
      camera.aspect = w / Math.max(h, 1);
      camera.updateProjectionMatrix();
    }}
    window.addEventListener("resize", resize);
    new GLTFLoader().load("./robot_mixed_cad.glb", (gltf) => {{
      scene.add(gltf.scene);
      const box = new THREE.Box3().setFromObject(gltf.scene);
      const c = box.getCenter(new THREE.Vector3());
      controls.target.copy(c);
      camera.lookAt(c);
      resize();
    }});
    function tick() {{
      controls.update();
      renderer.render(scene, camera);
      requestAnimationFrame(tick);
    }}
    tick();
  </script>
</body>
</html>
"""
    (OUT / "preview.html").write_text(html, encoding="utf-8")


def export_glb(parts: list[dict]) -> None:
    scene = trimesh.Scene()
    for part in parts:
        mesh = part["selected"]
        if mesh is None:
            continue
        colored = mesh.copy()
        rgba = [217, 95, 2, 255] if part["native"] else [139, 152, 168, 255]
        colored.visual.face_colors = np.tile(rgba, (len(colored.faces), 1))
        scene.add_geometry(colored, node_name=part["id"])
    scene.export(OUT / "robot_mixed_cad.glb")


def main() -> None:
    pv.OFF_SCREEN = True
    OUT.mkdir(parents=True, exist_ok=True)
    parts = load_components()
    source_meshes = [p["source"] for p in parts if p["source"] is not None]
    selected_meshes = [p["selected"] for p in parts if p["selected"] is not None]
    native_meshes = [p["cad"] for p in parts if p["native"] and p["cad"] is not None]
    global_bounds = bounds_of(source_meshes + selected_meshes)

    source_items = [(to_poly(m), SOURCE_GRAY, 1.0) for m in source_meshes]
    mixed_items = [
        (to_poly(p["selected"]), CAD_ORANGE if p["native"] else FACET_GRAY, 1.0)
        for p in parts
        if p["selected"] is not None
    ]
    native_items = [(to_poly(m), CAD_ORANGE, 1.0) for m in native_meshes]

    for name, direction in VIEWS.items():
        render_items(source_items, global_bounds, OUT / f"_src_{name}.png", direction)
        render_items(mixed_items, global_bounds, OUT / f"_mix_{name}.png", direction)
        if native_items:
            render_items(native_items, global_bounds, OUT / f"_nat_{name}.png", direction)

    src_left = caption(Image.open(OUT / "_src_iso_front_left.png"), "source mesh", "9 P3 parts, original OBJ")
    mix_left = caption(
        Image.open(OUT / "_mix_iso_front_left.png"),
        "selected mixed CAD",
        "orange = CAD-native · gray = faceted fallback",
    )
    hstack([src_left, mix_left], OUT / "final_cad_iso_front_left_captioned.png")
    Image.open(OUT / "_mix_iso_front_right.png").save(OUT / "final_cad_iso_front_right.png")
    Image.open(OUT / "_mix_high_orbit.png").save(OUT / "final_cad_high_orbit.png")
    Image.open(OUT / "_mix_side.png").save(OUT / "final_cad_side.png")
    native_cap = caption(
        Image.open(OUT / "_nat_iso_front_left.png") if native_items else Image.open(OUT / "_mix_iso_front_left.png"),
        "CAD-native only",
        "P3 006 + 008 MAC loft passed hard gate" if len(native_meshes) == 2 else "CAD-native subset",
    )
    native_cap.save(OUT / "final_cad_native_only_captioned.png")
    hstack(
        [
            caption(Image.open(OUT / "_src_high_orbit.png"), "source"),
            caption(Image.open(OUT / "_mix_high_orbit.png"), "mixed selected"),
            caption(Image.open(OUT / "_nat_high_orbit.png") if native_items else Image.open(OUT / "_mix_high_orbit.png"), "CAD-native"),
        ],
        OUT / "overview_source_vs_mixed_vs_native.png",
    )

    part_selected: list[Image.Image] = []
    part_mac: list[Image.Image] = []
    for part in parts:
        source = part["source"]
        cad = part["mac"] if part["mac"] is not None else part["v6"]
        local = [m for m in (source, cad) if m is not None]
        bounds = bounds_of(local) if local else global_bounds
        sheet_dir = OUT / "parts"
        sheet_dir.mkdir(parents=True, exist_ok=True)
        src_png = sheet_dir / f"{part['id']}_source.png"
        cad_png = sheet_dir / f"{part['id']}_cad.png"
        over_png = sheet_dir / f"{part['id']}_overlay.png"
        sel_png = sheet_dir / f"{part['id']}_selected.png"
        render_items([(to_poly(source), SOURCE_GRAY, 1.0)], bounds, src_png, VIEWS["iso_front_left"], (720, 620))
        if cad is not None:
            render_items([(to_poly(cad), MAC_TEAL if part["mac"] is not None else CAD_ORANGE, 1.0)], bounds, cad_png, VIEWS["iso_front_left"], (720, 620))
            render_items(
                [(to_poly(source), SOURCE_GRAY, 0.42), (to_poly(cad), OVERLAY_CAD, 0.82)],
                bounds,
                over_png,
                VIEWS["iso_front_left"],
                (720, 620),
            )
        else:
            placeholder = Image.new("RGB", (720, 620), "#eef1f4")
            draw = ImageDraw.Draw(placeholder)
            draw.text((360, 310), "NO MAC CAD", font=font(36), fill="#626b77", anchor="mm")
            placeholder.save(cad_png)
            placeholder.save(over_png)
        sel_color = CAD_ORANGE if part["native"] else FACET_GRAY
        render_items([(to_poly(part["selected"]), sel_color, 1.0)], bounds, sel_png, VIEWS["iso_front_left"], (720, 620))
        qa = part["mac_qa"] if part["mac"] is not None else part["v6_qa"]
        cad_sub = (
            f"{part['cad_label']}  cov {metric(qa, 'coverage', 3)}  "
            f"chamfer {metric(qa, 'chamfer', 4)}  Hausdorff {metric(qa, 'hausdorff', 3)}"
        )
        src_im = caption(Image.open(src_png), f"{part['id']}  source", "prepare/source_part.obj")
        cad_im = caption(Image.open(cad_png), f"{part['id']}  {part['cad_label']}", cad_sub)
        over_im = caption(
            Image.open(over_png),
            f"{part['id']}  overlay",
            f"selected {part['backend']}  {'CAD-native' if part['native'] else 'faceted fallback'}",
        )
        hstack([src_im, cad_im, over_im], sheet_dir / f"preview_{part['id']}_source_mac_overlay.png")
        part_selected.append(caption(Image.open(sel_png), f"{part['short']}  {part['backend']}", "CAD-native" if part["native"] else "faceted"))
        part_mac.append(cad_im.resize((720, 680), Image.Resampling.LANCZOS))

    grid(part_selected, 3, OUT / "parts_grid_selected.png")
    grid(part_mac, 3, OUT / "parts_grid_mac.png")
    export_glb(parts)
    write_html(parts)
    manifest = {
        "output_dir": str(OUT),
        "cad_native": [p["id"] for p in parts if p["native"]],
        "faceted": [p["id"] for p in parts if not p["native"]],
        "files": sorted(path.name for path in OUT.iterdir() if path.is_file()),
        "part_sheets": [f"parts/preview_{p['id']}_source_mac_overlay.png" for p in parts],
    }
    (OUT / "render_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "native": manifest["cad_native"], "out": str(OUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

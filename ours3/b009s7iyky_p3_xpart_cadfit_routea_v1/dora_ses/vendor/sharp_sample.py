# Adapted from Dora official sharp_sample.py (Seed3D/Dora, Apache 2.0).
# Adds salient edge NPZ export for CAD-edge prior adapter workflow.
import argparse
import gc
import json
import math
import os

import bpy
import bmesh
import fpsample
import numpy as np
import trimesh
from pysdf import SDF
from tqdm import tqdm


def save_vertices_as_ply_trimesh(vertices, filepath):
    cloud = trimesh.PointCloud(vertices)
    cloud.export(filepath)


def process_mesh(
    mesh_path,
    point_number,
    ply_output_path,
    npz_output_path,
    edge_output_path,
    sharpness_threshold,
):
    bpy.ops.wm.obj_import(filepath=mesh_path)
    obj = bpy.context.selected_objects[0]

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_mode(type="EDGE")
    bpy.ops.mesh.edges_select_sharp(sharpness=sharpness_threshold)
    bpy.ops.object.mode_set(mode="OBJECT")

    bm = bmesh.new()
    bm.from_mesh(obj.data)

    sharp_edges = [edge for edge in bm.edges if edge.select]

    sharp_edges_vertices = []
    link_normal1 = []
    link_normal2 = []
    sharp_edges_angle = []
    vertices_set = set()
    for edge in sharp_edges:
        vertices_set.update(edge.verts[:])
        sharp_edges_vertices.append([edge.verts[0].index, edge.verts[1].index])

        normal1 = edge.link_faces[0].normal
        normal2 = edge.link_faces[1].normal
        link_normal1.append(normal1)
        link_normal2.append(normal2)

        if normal1.length == 0.0 or normal2.length == 0.0:
            sharp_edges_angle.append(0.0)
        else:
            sharp_edges_angle.append(math.degrees(normal1.angle(normal2)))

    vertices = []
    vertices_index = []
    vertices_normal = []

    for vertice in vertices_set:
        vertices.append(vertice.co)
        vertices_index.append(vertice.index)
        vertices_normal.append(vertice.normal)

    vertices = np.array(vertices)
    vertices_index = np.array(vertices_index)
    vertices_normal = np.array(vertices_normal)

    sharp_edges_count = np.array(len(sharp_edges))
    sharp_edges_angle_array = np.array(sharp_edges_angle)
    sharp_edges_vertices_array = np.array(sharp_edges_vertices)

    if sharp_edges_count > 0:
        sharp_edge_link_normal = np.array(np.concatenate([link_normal1, link_normal2], axis=1))
        nan_mask = np.isnan(sharp_edge_link_normal)
        sharp_edge_link_normal = np.where(nan_mask, 0, sharp_edge_link_normal)

        nan_mask = np.isnan(vertices_normal)
        vertices_normal = np.where(nan_mask, 0, vertices_normal)

    if sharp_edges_count > 0:
        np.savez(
            edge_output_path,
            edge_vertex_indices=sharp_edges_vertices_array.astype(np.int32),
            edge_dihedral_deg=sharp_edges_angle_array.astype(np.float32),
            sharp_vertex_indices=vertices_index.astype(np.int32),
        )

        mesh = trimesh.load(mesh_path, process=False)
        num_target_sharp_vertices = point_number // 2
        sharp_edge_length = sharp_edges_count
        sharp_edges_vertices_pair = sharp_edges_vertices_array
        sharp_vertices_pair = mesh.vertices[sharp_edges_vertices_pair]
        epsilon = 1e-4
        edge_normal = 0.5 * sharp_edge_link_normal[:, :3] + 0.5 * sharp_edge_link_normal[:, 3:]
        norms = np.linalg.norm(edge_normal, axis=1, keepdims=True)
        norms = np.where(norms > epsilon, norms, epsilon)
        edge_normal = edge_normal / norms
        known_vertices = vertices
        known_vertices_normal = vertices_normal
        known_vertices = np.concatenate([known_vertices, known_vertices_normal], axis=1)

        num_known_vertices = known_vertices.shape[0]
        if num_known_vertices < num_target_sharp_vertices:
            num_new_vertices = num_target_sharp_vertices - num_known_vertices
            if num_new_vertices >= sharp_edge_length:
                num_new_vertices_per_pair = num_new_vertices // sharp_edge_length
                new_vertices = np.zeros((sharp_edge_length, num_new_vertices_per_pair, 6))

                start_vertex = sharp_vertices_pair[:, 0]
                end_vertex = sharp_vertices_pair[:, 1]
                for j in range(1, num_new_vertices_per_pair + 1):
                    t = j / float(num_new_vertices_per_pair + 1)
                    new_vertices[:, j - 1, :3] = (1 - t) * start_vertex + t * end_vertex
                    new_vertices[:, j - 1, 3:] = edge_normal
                new_vertices = new_vertices.reshape(-1, 6)

                remaining_vertices = num_new_vertices % sharp_edge_length
                if remaining_vertices > 0:
                    rng = np.random.default_rng()
                    ind = rng.choice(sharp_edge_length, remaining_vertices, replace=False)
                    new_vertices_remain = np.zeros((remaining_vertices, 6))
                    start_vertex = sharp_vertices_pair[ind, 0]
                    end_vertex = sharp_vertices_pair[ind, 1]
                    t = np.random.rand(remaining_vertices).reshape(-1, 1)
                    new_vertices_remain[:, :3] = (1 - t) * start_vertex + t * end_vertex

                    edge_normal = 0.5 * sharp_edge_link_normal[ind, :3] + 0.5 * sharp_edge_link_normal[ind, 3:]
                    edge_normal = edge_normal / np.linalg.norm(edge_normal, axis=1, keepdims=True)
                    new_vertices_remain[:, 3:] = edge_normal

                    new_vertices = np.concatenate([new_vertices, new_vertices_remain], axis=0)
            else:
                remaining_vertices = num_new_vertices % sharp_edge_length
                if remaining_vertices > 0:
                    rng = np.random.default_rng()
                    ind = rng.choice(sharp_edge_length, remaining_vertices, replace=False)
                    new_vertices_remain = np.zeros((remaining_vertices, 6))
                    start_vertex = sharp_vertices_pair[ind, 0]
                    end_vertex = sharp_vertices_pair[ind, 1]
                    t = np.random.rand(remaining_vertices).reshape(-1, 1)
                    new_vertices_remain[:, :3] = (1 - t) * start_vertex + t * end_vertex

                    edge_normal = 0.5 * sharp_edge_link_normal[ind, :3] + 0.5 * sharp_edge_link_normal[ind, 3:]
                    edge_normal = edge_normal / np.linalg.norm(edge_normal, axis=1, keepdims=True)
                    new_vertices_remain[:, 3:] = edge_normal

                    new_vertices = new_vertices_remain

            target_vertices = np.concatenate([new_vertices, known_vertices], axis=0)
        else:
            target_vertices = known_vertices

        sharp_surface = target_vertices
        sharp_surface_points = sharp_surface[:, :3]

        sharp_near_surface_points = [
            sharp_surface_points + np.random.normal(scale=0.001, size=(len(sharp_surface_points), 3)),
            sharp_surface_points + np.random.normal(scale=0.005, size=(len(sharp_surface_points), 3)),
            sharp_surface_points + np.random.normal(scale=0.007, size=(len(sharp_surface_points), 3)),
            sharp_surface_points + np.random.normal(scale=0.01, size=(len(sharp_surface_points), 3)),
        ]
        sharp_near_surface_points = np.concatenate(sharp_near_surface_points)

        f = SDF(mesh.vertices, mesh.faces)
        sharp_sdf = f(sharp_near_surface_points).reshape(-1, 1)
        sharp_near_surface = np.concatenate([sharp_near_surface_points, sharp_sdf], axis=1)

        coarse_surface_points, faces = mesh.sample(200000, return_index=True)
        normals = mesh.face_normals[faces]
        coarse_surface = np.concatenate([coarse_surface_points, normals], axis=1)

        coarse_near_surface_points = [
            coarse_surface_points + np.random.normal(scale=0.001, size=(len(coarse_surface_points), 3)),
            coarse_surface_points + np.random.normal(scale=0.005, size=(len(coarse_surface_points), 3)),
        ]
        coarse_near_surface_points = np.concatenate(coarse_near_surface_points)
        space_points = np.random.uniform(-1.05, 1.05, (200000, 3))
        rand_points = np.concatenate([coarse_near_surface_points, space_points], axis=0)
        coarse_sdf = f(rand_points).reshape(-1, 1)
        rand_points = np.concatenate([rand_points, coarse_sdf], axis=1)

        coarse_surface_points, faces = mesh.sample(200000, return_index=True)
        normals = mesh.face_normals[faces]
        coarse_surface = np.concatenate([coarse_surface_points, normals], axis=1)

        fps_coarse_surface_list = []
        for _ in range(1):
            kdline_fps_samples_idx = fpsample.bucket_fps_kdline_sampling(
                coarse_surface_points, num_target_sharp_vertices, h=5
            )
            fps_coarse_surface = coarse_surface[kdline_fps_samples_idx].reshape(-1, 1, 6)
            fps_coarse_surface_list.append(fps_coarse_surface)
        fps_coarse_surface = np.concatenate(fps_coarse_surface_list, axis=1)

        fps_sharp_surface_list = []
        if sharp_surface.shape[0] > num_target_sharp_vertices:
            for _ in range(1):
                kdline_fps_samples_idx = fpsample.bucket_fps_kdline_sampling(
                    sharp_surface_points, num_target_sharp_vertices, h=5
                )
                fps_sharp_surface = sharp_surface[kdline_fps_samples_idx].reshape(-1, 1, 6)
                fps_sharp_surface_list.append(fps_sharp_surface)
            fps_sharp_surface = np.concatenate(fps_sharp_surface_list, axis=1)
        else:
            fps_sharp_surface = sharp_surface[:, None]

        sharp_surface[np.isinf(sharp_surface)] = 1
        sharp_surface[np.isnan(sharp_surface)] = 1
        fps_coarse_surface[np.isinf(fps_coarse_surface)] = 1
        fps_coarse_surface[np.isnan(fps_coarse_surface)] = 1
        np.savez(
            npz_output_path,
            fps_sharp_surface=fps_sharp_surface.astype(np.float32),
            sharp_near_surface=sharp_near_surface.astype(np.float32),
            fps_coarse_surface=fps_coarse_surface.astype(np.float32),
            rand_points=rand_points.astype(np.float32),
        )
        save_vertices_as_ply_trimesh(sharp_surface[:, :3], ply_output_path)
    else:
        print(f"{mesh_path} no sharp edges!")

    bm.free()
    bpy.data.objects.remove(obj, do_unlink=True)
    gc.collect()


def main(json_file_path, angle_threshold, point_number, sharp_point_path, sample_path, edge_path) -> None:
    with open(json_file_path, "r", encoding="utf-8") as handle:
        meshes_paths = json.load(handle)

    sharpness_threshold = math.radians(angle_threshold)

    for mesh_path in tqdm(meshes_paths, desc="Processing meshes"):
        part_dir = os.path.basename(mesh_path).replace(".obj", "")
        ply_output_path = f"{sharp_point_path}/{part_dir}/salient_points.ply"
        npz_output_path = f"{sample_path}/{part_dir}/dora_samples.npz"
        edge_output_path = f"{edge_path}/{part_dir}/salient_edges.npz"
        os.makedirs(f"{sharp_point_path}/{part_dir}", exist_ok=True)
        os.makedirs(f"{sample_path}/{part_dir}", exist_ok=True)
        os.makedirs(f"{edge_path}/{part_dir}", exist_ok=True)
        if (
            os.path.exists(ply_output_path)
            and os.path.exists(npz_output_path)
            and os.path.exists(edge_output_path)
        ):
            continue
        try:
            process_mesh(
                mesh_path,
                point_number,
                ply_output_path,
                npz_output_path,
                edge_output_path,
                sharpness_threshold,
            )
            gc.collect()
        except Exception as exc:
            print(f"ERROR: in processing path: {mesh_path}. Error: {exc}")
            gc.collect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json_file_path", type=str, help="JSON list of normalized mesh paths")
    parser.add_argument("--angle_threshold", type=int, help="Dihedral angle threshold in degrees")
    parser.add_argument("--point_number", type=int, help="Number of points to sample")
    parser.add_argument("--sharp_point_path", type=str, help="Directory for sharp point PLY files")
    parser.add_argument("--sample_path", type=str, help="Directory for official Dora NPZ samples")
    parser.add_argument("--edge_path", type=str, help="Directory for salient edge NPZ files")
    args, _extras = parser.parse_known_args()
    main(
        args.json_file_path,
        args.angle_threshold,
        args.point_number,
        args.sharp_point_path,
        args.sample_path,
        args.edge_path,
    )

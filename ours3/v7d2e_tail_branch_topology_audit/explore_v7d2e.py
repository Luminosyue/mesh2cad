#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
from collections import defaultdict, deque
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
V7A = ROOT / 'v7a_profile_recovery'
V7D2B = ROOT / 'v7d2b_versioned_chain_evidence_repair'
OUT = ROOT / 'v7d2e_tail_branch_topology_audit'


def load(path):
    return json.loads(Path(path).read_text())


def own_graph(segments, snap):
    segments = np.asarray(segments, float)
    points = segments.reshape((-1, 3))
    parent = list(range(len(points)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[b] = a

    for a, b in cKDTree(points).query_pairs(float(snap)):
        union(a, b)
    groups = defaultdict(list)
    for i in range(len(points)):
        groups[find(i)].append(i)
    nodes, p2n = [], {}
    for members in groups.values():
        nodes.append(points[members].mean(axis=0))
        for i in members:
            p2n[i] = len(nodes) - 1
    adj = {i: set() for i in range(len(nodes))}
    edges = []
    seen = set()
    for i in range(len(segments)):
        a, b = p2n[2 * i], p2n[2 * i + 1]
        key = tuple(sorted((a, b)))
        if a == b or key in seen:
            continue
        seen.add(key)
        adj[a].add(b)
        adj[b].add(a)
        edges.append((a, b))
    rem, comps = set(adj), []
    while rem:
        start = min(rem)
        q, comp = deque([start]), set()
        while q:
            x = q.popleft()
            if x in comp:
                continue
            comp.add(x)
            q.extend(adj[x] - comp)
        rem -= comp
        comps.append(comp)
    return np.asarray(nodes), edges, adj, comps


def ordered_component(adj, comp):
    ends = sorted(n for n in comp if len(adj[n] & comp) == 1)
    if len(ends) == 2 and all(len(adj[n] & comp) <= 2 for n in comp):
        out, prev, cur = [ends[0]], None, ends[0]
        while cur != ends[1]:
            choices = sorted((adj[cur] & comp) - ({prev} if prev is not None else set()))
            if len(choices) != 1:
                return 'AMBIGUOUS', []
            nxt = choices[0]
            if nxt in out:
                return 'AMBIGUOUS', []
            out.append(nxt)
            prev, cur = cur, nxt
        return 'OPEN_CHAIN', out
    if len(comp) >= 3 and all(len(adj[n] & comp) == 2 for n in comp):
        start, out, prev, cur = min(comp), [min(comp)], None, min(comp)
        while True:
            choices = sorted((adj[cur] & comp) - ({prev} if prev is not None else set()))
            if not choices:
                return 'AMBIGUOUS', []
            nxt = choices[0]
            if nxt == start:
                return ('CLOSED_LOOP', out) if len(out) == len(comp) else ('AMBIGUOUS', [])
            if nxt in out:
                return 'AMBIGUOUS', []
            out.append(nxt)
            prev, cur = cur, nxt
    return 'AMBIGUOUS', []


def resample(points, count=64, closed=False):
    p = np.asarray(points, float)
    if closed:
        p = np.vstack([p, p[0]])
    if len(p) < 2:
        return np.repeat(p[:1], count, axis=0)
    seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
    cum = np.r_[0.0, np.cumsum(seg)]
    if cum[-1] <= 1e-12:
        return np.repeat(p[:1], count, axis=0)
    q = np.linspace(0, cum[-1], count)
    return np.column_stack([np.interp(q, cum, p[:, j]) for j in range(3)])


def section(mesh, profile, station_id, station_t):
    mod_path = V7A / 'geometry/section_intersection.py'
    spec = importlib.util.spec_from_file_location('section_intersection', mod_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    diag = float(np.linalg.norm(mesh.extents))
    result = mod.triangle_plane_segments(
        mesh, profile['plane_origin'], profile['plane_normal'], max(1e-9, diag * 1e-9)
    )
    nodes, edges, adj, comps = own_graph(result.segments, profile['snap_tolerance'])
    records = []
    origin = np.asarray(profile['plane_origin'], float)
    bu, bv = np.asarray(profile['basis_u'], float), np.asarray(profile['basis_v'], float)
    for i, comp in enumerate(comps):
        kind, order = ordered_component(adj, comp)
        pts = nodes[order] if order else nodes[sorted(comp)]
        closed = kind == 'CLOSED_LOOP'
        rp = resample(pts, 64, closed)
        local = np.column_stack(((rp - origin) @ bu, (rp - origin) @ bv))
        arc = float(np.linalg.norm(np.diff(np.vstack([pts, pts[0]]) if closed else pts, axis=0), axis=1).sum()) if len(pts) > 1 else 0.0
        principal = np.linalg.svd(rp - rp.mean(0), full_matrices=False)[2][0]
        records.append({
            'station_id': station_id, 'station_t': float(station_t), 'component_id': f'COMP_{i:03d}',
            'topology': kind, 'points': pts.tolist(), 'resampled': rp.tolist(),
            'local': local.tolist(), 'centroid': rp.mean(0).tolist(), 'arc_length': arc,
            'principal': principal.tolist(), 'node_count': len(comp),
            'node_ids': sorted(int(x) for x in comp),
            'edge_ids': [j for j, (a, b) in enumerate(edges) if a in comp and b in comp],
        })
    return {
        'station_id': station_id, 'station_t': float(station_t),
        'raw_segments': int(len(result.segments)), 'node_count': int(len(nodes)),
        'edge_count': int(len(edges)), 'component_count': len(records),
        'intersection_segments': np.asarray(result.segments, float).tolist(),
        'nodes': nodes.tolist(),
        'edges': [{'edge_id': f'E{i:04d}', 'node_a': int(a), 'node_b': int(b)} for i, (a, b) in enumerate(edges)],
        'components': records,
    }


def component_distance(a, b, diag):
    pa, pb = np.asarray(a['resampled']), np.asarray(b['resampled'])
    ca, cb = np.asarray(a['centroid']), np.asarray(b['centroid'])
    la, lb = np.asarray(a['local']), np.asarray(b['local'])
    # Translation-invariant whole-chain shape plus physical continuity. No seam curvature.
    na = pa - ca
    nb = pb - cb
    shape = min(np.mean(np.linalg.norm(na - nb, axis=1)), np.mean(np.linalg.norm(na - nb[::-1], axis=1))) / diag
    centroid = np.linalg.norm(ca - cb) / diag
    length = abs(a['arc_length'] - b['arc_length']) / max(a['arc_length'], b['arc_length'], 1e-12)
    principal = 1.0 - abs(float(np.dot(a['principal'], b['principal'])))
    side = abs(float(np.mean(la[:, 0]) - np.mean(lb[:, 0]))) / diag
    tangent = min(np.linalg.norm((pa[1] - pa[0]) / max(np.linalg.norm(pa[1] - pa[0]), 1e-12) - (pb[1] - pb[0]) / max(np.linalg.norm(pb[1] - pb[0]), 1e-12)),
                  np.linalg.norm((pa[1] - pa[0]) / max(np.linalg.norm(pa[1] - pa[0]), 1e-12) + (pb[-2] - pb[-1]) / max(np.linalg.norm(pb[-2] - pb[-1]), 1e-12)))
    total = 2.0 * shape + centroid + 0.4 * side + 0.35 * length + 0.25 * principal + 0.15 * tangent
    return {'total': float(total), 'shape': float(shape), 'centroid': float(centroid), 'side': float(side), 'length': float(length), 'principal': float(principal), 'tangent': float(tangent)}


def main():
    ga = load(V7A / '03_geometry_analyzer/CADPART_005/geometry_analysis.json')
    mesh = trimesh.load(ga['source_mesh'], force='mesh', process=False)
    profiles = {p['station_id']: p for p in ga['profiles']}
    sections = {}
    for i in range(4, 10):
        sid = f'S{i:02d}'
        sections[sid] = section(mesh, profiles[sid], sid, profiles[sid]['actual_t'])
    diag = float(np.linalg.norm(mesh.extents))
    # Adaptive samples in the permitted S05-S07 interval. Seven samples derive only from gap subdivision.
    p5, p7 = profiles['S05'], profiles['S07']
    t5, t7 = float(p5['actual_t']), float(p7['actual_t'])
    adaptive = {}
    for j, t in enumerate(np.linspace(t5, t7, 9)[1:-1], 1):
        sid = f'A{j:02d}'
        origin = np.asarray(ga['axis']['origin']) + (t - 0.5) * (mesh.bounds[1, 0] - mesh.bounds[0, 0]) * np.asarray(ga['axis']['direction'])
        # Match the exact parameter convention from original plane origins by interpolation.
        alpha = (t - t5) / (t7 - t5)
        origin = (1 - alpha) * np.asarray(p5['plane_origin']) + alpha * np.asarray(p7['plane_origin'])
        profile = dict(p5)
        profile['plane_origin'] = origin.tolist()
        adaptive[sid] = section(mesh, profile, sid, t)
    # Pairwise correspondence costs.
    edge_costs = []
    sequence = list(sections.values())
    for aa, bb in zip(sequence, sequence[1:]):
        for a in aa['components']:
            for b in bb['components']:
                cost = component_distance(a, b, diag)
                edge_costs.append({'from': f"{aa['station_id']}/{a['component_id']}", 'to': f"{bb['station_id']}/{b['component_id']}", **cost})
    # Current track component nearest by centroid/shape.
    tr = load(V7D2B / '03_geometry_analyzer/CADPART_005/versioned_measured_chain_evidence.json')['tracks']['TRACK_0']
    current = {}
    for item in tr:
        sid = item['station_id']
        if sid in sections:
            pseudo = {'resampled': item['resampled_points_3d'], 'centroid': item['centroid'], 'local': item['resampled_points_local'], 'arc_length': item['arc_length'], 'principal': item['principal_direction']}
            scores = [(component_distance(pseudo, c, diag)['total'], c['component_id']) for c in sections[sid]['components']]
            current[sid] = min(scores)[1]
    out = {'mesh_diag': diag, 'profiles': {k: {x: profiles[k][x] for x in ['status','actual_t','raw_segment_count','raw_path_count','open_path_count','closed_path_count']} for k in profiles if 'S04' <= k <= 'S09'}, 'sections': sections, 'adaptive': adaptive, 'edge_costs': edge_costs, 'current': current}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'explore.json').write_text(json.dumps(out, indent=2) + '\n')
    print('CURRENT', current)
    for sid, s in {**sections, **adaptive}.items():
        print(sid, 'seg', s['raw_segments'], 'components', [(c['component_id'], c['topology'], round(c['arc_length'], 6), [round(x, 5) for x in c['centroid']]) for c in s['components']])
    print('NEAREST EDGES')
    for a, b in zip(sequence, sequence[1:]):
        e = sorted([x for x in edge_costs if x['from'].startswith(a['station_id'] + '/') and x['to'].startswith(b['station_id'] + '/')], key=lambda x: x['total'])[:5]
        print(a['station_id'], b['station_id'], [(x['from'].split('/')[1], x['to'].split('/')[1], round(x['total'], 4)) for x in e])


if __name__ == '__main__':
    main()

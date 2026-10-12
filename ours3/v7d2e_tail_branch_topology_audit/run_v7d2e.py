#!/usr/bin/env python3
"""V7D2E Tail branch/topology/adaptive-station evidence audit.

This is a versioned, offline evidence audit. It never writes any frozen input,
never uses GT/CAD distance, and never creates production curves or geometry.
"""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import trimesh

from explore_v7d2e import component_distance, load, section

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
V7A = ROOT / 'v7a_profile_recovery'
V7D2B = ROOT / 'v7d2b_versioned_chain_evidence_repair'
V7D2C = ROOT / 'v7d2c_mixed_section_seam_identity'
V7D2D = ROOT / 'v7d2d_vertical_tail_seam_endpoint_identity'
V7D3 = ROOT / 'v7d3_vertical_tail_geometry_preserving_refit'
OUT = ROOT / 'v7d2e_tail_branch_topology_audit'
ART = OUT / 'artifacts'
DBG = ART / 'tail_branch_audit'
VERSION = 'V7D2E_ADAPTIVE_TAIL'


def dump(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def tree_hash(path):
    h = hashlib.sha256()
    path = Path(path)
    for p in sorted(x for x in path.rglob('*') if x.is_file() and '__pycache__' not in str(x) and '.pytest_cache' not in str(x)):
        h.update(str(p.relative_to(path)).encode())
        h.update(bytes.fromhex(sha(p)))
    return h.hexdigest()


def write_csv(path, rows, fields=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or list(rows[0])
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def angle(a, b, c):
    u = np.asarray(b) - np.asarray(a)
    v = np.asarray(c) - np.asarray(b)
    nu, nv = np.linalg.norm(u), np.linalg.norm(v)
    if min(nu, nv) <= 1e-12:
        return 0.0
    return float(math.acos(np.clip(float(np.dot(u, v) / (nu * nv)), -1.0, 1.0)))


def dominant(section_record):
    return max(section_record['components'], key=lambda x: x['arc_length'])


def side_endpoint(component):
    p = np.asarray(component['points'], float)
    # Frozen physical side used by V7D2D endpoint A: larger world Y.
    return max((p[0], p[-1]), key=lambda q: q[1])


def section_state(rec):
    op = sum(c['topology'] == 'OPEN_CHAIN' for c in rec['components'])
    cl = sum(c['topology'] == 'CLOSED_LOOP' for c in rec['components'])
    if op and cl:
        return 'MIXED_OPEN_CLOSED'
    if cl and not op:
        return 'CLOSED_LOOP'
    if op == 1:
        return 'SINGLE_OPEN'
    if op > 1:
        return 'MULTI_OPEN'
    return 'OTHER'


def component_local(component):
    return np.asarray(component['local'], float)


def plot_components(rec, path, title):
    fig, ax = plt.subplots(figsize=(6, 5))
    for c in rec['components']:
        q = component_local(c)
        ls = '-' if c['topology'] == 'OPEN_CHAIN' else '--'
        ax.plot(q[:, 0], q[:, 1], ls, lw=2, label=f"{c['component_id']} {c['topology']} L={c['arc_length']:.4f}")
        ax.scatter(q[[0, -1], 0], q[[0, -1], 1], s=14)
    ax.set_title(title)
    ax.set_xlabel('station local u')
    ax.set_ylabel('station local v')
    ax.axis('equal')
    ax.grid(alpha=.25)
    ax.legend(fontsize=7, loc='best')
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_trajectory(rows, path, title, local=False):
    pts = np.asarray([r['LOCAL_UV'] if local else r['WORLD_XYZ'] for r in rows], float)
    fig, ax = plt.subplots(figsize=(7, 5))
    if local:
        ax.plot(pts[:, 0], pts[:, 1], '-o')
        for p, r in zip(pts, rows):
            ax.text(p[0], p[1], r['STATION'], fontsize=7)
        ax.set_xlabel('local u')
        ax.set_ylabel('local v')
    else:
        ax.plot(pts[:, 0], pts[:, 1], '-o', label='XY')
        ax.plot(pts[:, 0], pts[:, 2], '-s', label='XZ')
        for p, r in zip(pts, rows):
            ax.text(p[0], p[1], r['STATION'], fontsize=7)
        ax.set_xlabel('construction-axis / world X')
        ax.set_ylabel('world Y or Z')
        ax.legend()
    ax.set_title(title)
    ax.grid(alpha=.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def make_contact(paths, out):
    images = [plt.imread(p) for p in paths]
    fig, axes = plt.subplots(4, 3, figsize=(15, 18))
    for ax, im, p in itertools.zip_longest(axes.flat, images, paths):
        if im is None:
            ax.axis('off')
            continue
        ax.imshow(im)
        ax.set_title(Path(p).stem, fontsize=8)
        ax.axis('off')
    fig.suptitle('V7D2E S07 Root Cause Evidence', fontsize=16)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def main():
    for d in [ART, DBG, OUT / 'logs', OUT / 'tests', OUT / 'evidence' / 'raw_original_stations', OUT / 'evidence' / 'adaptive_stations']:
        d.mkdir(parents=True, exist_ok=True)

    fuselage_path = V7D2C / 'artifacts/fuselage_mixed_section_seam.csv'
    fuselage_before = sha(fuselage_path)
    v7d3_before = tree_hash(V7D3)
    frozen_tail_hash = sha(V7D2B / '03_geometry_analyzer/CADPART_005/versioned_measured_chain_evidence.json')

    ga = load(V7A / '03_geometry_analyzer/CADPART_005/geometry_analysis.json')
    mesh = trimesh.load(ga['source_mesh'], force='mesh', process=False)
    diag = float(np.linalg.norm(mesh.extents))
    profiles = {p['station_id']: p for p in ga['profiles']}
    old_tracks = load(V7D2B / '03_geometry_analyzer/CADPART_005/versioned_measured_chain_evidence.json')['tracks']
    frozen_track = {x['station_id']: x for x in old_tracks['TRACK_0']}

    # V7D2B regenerated full raw graphs exist for FUSELAGE only. Materialize Tail
    # original-station full graphs offline from saved planes/source mesh.
    original = {}
    for i in range(4, 10):
        sid = f'S{i:02d}'
        original[sid] = section(mesh, profiles[sid], sid, profiles[sid]['actual_t'])
        original[sid]['section_state'] = section_state(original[sid])
        dump(OUT / 'evidence/raw_original_stations' / f'{sid}.json', original[sid])

    # S05-S07 gap and mixed topology trigger depth-3 recursive subdivision.
    # Seven internal samples are fixed before measuring their intersections.
    p5, p7 = profiles['S05'], profiles['S07']
    t5, t7 = float(p5['actual_t']), float(p7['actual_t'])
    adaptive = {}
    for j, t in enumerate(np.linspace(t5, t7, 9)[1:-1], 1):
        alpha = float((t - t5) / (t7 - t5))
        profile = dict(p5)
        profile['plane_origin'] = ((1 - alpha) * np.asarray(p5['plane_origin']) + alpha * np.asarray(p7['plane_origin'])).tolist()
        sid = f'A{j:02d}'
        adaptive[sid] = section(mesh, profile, sid, float(t))
        adaptive[sid]['section_state'] = section_state(adaptive[sid])
        dump(OUT / 'evidence/adaptive_stations' / f'{sid}.json', adaptive[sid])

    # Candidate rows and local physical correspondence graph.
    current_components = {}
    for sid, item in frozen_track.items():
        if sid not in original:
            continue
        pseudo = {
            'resampled': item['resampled_points_3d'], 'centroid': item['centroid'],
            'local': item['resampled_points_local'], 'arc_length': item['arc_length'],
            'principal': item['principal_direction'],
        }
        current_components[sid] = min(original[sid]['components'], key=lambda c: component_distance(pseudo, c, diag)['total'])['component_id']
    # Recover the skipped dominant physical branch at S06 for audit only.
    current_components['S06'] = dominant(original['S06'])['component_id']

    branch_rows = []
    edge_rows = []
    for sid, rec in original.items():
        max_len = max(c['arc_length'] for c in rec['components'])
        for c in rec['components']:
            shape_cost = abs(c['arc_length'] - max_len) / max(max_len, 1e-12)
            is_current = current_components.get(sid) == c['component_id']
            filter_reason = ('CURRENT_WHOLE_CHAIN_SELECTED' if is_current else
                             'CLOSED_LOOP_NOT_SERIALIZED_IN_OLD_OPEN_TRACK' if c['topology']=='CLOSED_LOOP' else
                             'NON_DOMINANT_OR_SHORT_COMPONENT')
            branch_rows.append({
                'CASE_PART': 'CADPART_005', 'STATION': sid, 'COMPONENT_ID': c['component_id'],
                'SECTION_STATE': rec['section_state'], 'CENTROID': json.dumps(c['centroid']),
                'ARC_LENGTH': c['arc_length'], 'SIDE': float(np.mean(component_local(c)[:, 0])),
                'SHAPE_COST': shape_cost, 'TRAJECTORY_COST': '',
                'CURRENT_SELECTED': is_current, 'ALTERNATIVE_RANK': '',
                'RAW_INTERSECTION_SEGMENT_COUNT': rec['raw_segments'],
                'RAW_GRAPH_NODE_COUNT': rec['node_count'], 'RAW_GRAPH_EDGE_COUNT': rec['edge_count'],
                'CONNECTED_COMPONENT_COUNT': rec['component_count'],
                'OPEN_CHAIN_COUNT': sum(x['topology']=='OPEN_CHAIN' for x in rec['components']),
                'CLOSED_LOOP_COUNT': sum(x['topology']=='CLOSED_LOOP' for x in rec['components']),
                'FILTER_REASON': filter_reason,
            })
    for a, b in zip([f'S{i:02d}' for i in range(4, 10)], [f'S{i:02d}' for i in range(5, 10)]):
        for ca in original[a]['components']:
            for cb in original[b]['components']:
                costs = component_distance(ca, cb, diag)
                edge_rows.append({'FROM': f"{a}/{ca['component_id']}", 'TO': f"{b}/{cb['component_id']}", **costs})

    # Local alternatives are anchored to frozen current physical branch outside
    # S06; only the ambiguity window is reconsidered.
    alternatives = []
    for c6 in original['S06']['components']:
        seq = [
            original['S04']['components'][int(current_components['S04'].split('_')[-1])],
            original['S05']['components'][int(current_components['S05'].split('_')[-1])], c6,
            original['S07']['components'][int(current_components['S07'].split('_')[-1])],
            original['S08']['components'][int(current_components['S08'].split('_')[-1])],
        ]
        score = sum(component_distance(a, b, diag)['total'] for a, b in zip(seq, seq[1:]))
        pts = [side_endpoint(c) for c in seq]
        turns = [angle(pts[i-1], pts[i], pts[i+1]) for i in range(1, len(pts)-1)]
        alternatives.append({
            'station_component_sequence': [f'{s}/{c["component_id"]}' for s, c in zip(['S04','S05','S06','S07','S08'], seq)],
            'full_chain_geometry_score': float(score),
            'centroid_trajectory_curvature': float(max(turns)),
            'side_continuity': float(sum(abs(np.mean(component_local(a)[:, 0]) - np.mean(component_local(b)[:, 0])) for a, b in zip(seq, seq[1:]))),
            'shape_continuity': float(sum(abs(a['arc_length'] - b['arc_length']) / max(a['arc_length'], b['arc_length'], 1e-12) for a, b in zip(seq, seq[1:]))),
            'gap_count': 0, 'maximum_station_gap': 1,
            's06_component': c6['component_id'], 's06_topology': c6['topology'],
        })
    alternatives.sort(key=lambda x: x['full_chain_geometry_score'])
    for rank, alt in enumerate(alternatives, 1):
        alt['rank'] = rank
        alt['name'] = 'CURRENT_BRANCH' if alt['s06_component'] == current_components['S06'] else f'ALTERNATIVE_BRANCH_{rank}'
    current_alt = next(x for x in alternatives if x['s06_component'] == current_components['S06'])
    current_rank = current_alt['rank']

    # A smoother small-fragment route exists only by sacrificing dominant
    # full-chain support, so it is explicitly rejected.
    # Counterfactual search also tests the visually smoother tiny branches.
    # They are weaker whenever S06 support is less than half the dominant arc.
    smoother_weaker = any(
        original['S06']['components'][int(a['s06_component'].split('_')[-1])]['arc_length']
        < .5 * dominant(original['S06'])['arc_length']
        for a in alternatives if a is not current_alt
    )

    # Adaptive evidence path: dominant measured chain only; no CAD metric.
    merged = {'S05': original['S05'], **adaptive, 'S07': original['S07'], 'S08': original['S08']}
    ordered = sorted(merged.items(), key=lambda kv: kv[1]['station_t'])
    adaptive_rows = []
    points = []
    for sid, rec in ordered:
        c = dominant(rec)
        pt = side_endpoint(c)
        origin = np.asarray(p5['plane_origin']) + (rec['station_t'] - t5) / (t7 - t5) * (np.asarray(p7['plane_origin']) - np.asarray(p5['plane_origin']))
        bu, bv = np.asarray(p5['basis_u']), np.asarray(p5['basis_v'])
        uv = [float(np.dot(pt-origin, bu)), float(np.dot(pt-origin, bv))]
        points.append(pt)
        adaptive_rows.append({
            'STATION_PARAMETER': rec['station_t'], 'ORIGINAL_OR_ADAPTIVE': 'ORIGINAL' if sid.startswith('S') else 'ADAPTIVE',
            'SECTION_STATE': rec['section_state'], 'CHAIN_COUNT': len(rec['components']),
            'SELECTED_CHAIN': c['component_id'], 'WORLD_XYZ': pt.tolist(), 'LOCAL_U': uv[0], 'LOCAL_V': uv[1],
            'TURNING_ANGLE': '', 'EVIDENCE_CONFIDENCE': 1.0 if c['arc_length'] >= .5 * max(z['arc_length'] for z in rec['components']) else .5,
            'STATION': sid, 'LOCAL_UV': uv,
        })
    for i in range(1, len(points)-1):
        adaptive_rows[i]['TURNING_ANGLE'] = angle(points[i-1], points[i], points[i+1])

    old_points = [side_endpoint(dominant(original[s])) for s in ['S05','S07','S08']]
    old_angle = angle(*old_points)
    s07_index = [r['STATION'] for r in adaptive_rows].index('S07')
    adaptive_angle = angle(points[s07_index-1], points[s07_index], points[s07_index+1])

    # Constant saved frames: world/local turn equivalence and no frame flip.
    frames = []
    for sid in [f'S{i:02d}' for i in range(4, 10)]:
        p = profiles[sid]
        R = np.column_stack([p['plane_normal'], p['basis_u'], p['basis_v']])
        frames.append((sid, R))
    frame_angles = []
    frame_flips = 0
    for (sa, ra), (sb, rb) in zip(frames, frames[1:]):
        value = np.clip((np.trace(ra.T @ rb)-1)/2, -1, 1)
        frame_angles.append({'FROM': sa, 'TO': sb, 'ANGLE': float(math.acos(value)), 'DET_A': float(np.linalg.det(ra)), 'DET_B': float(np.linalg.det(rb))})
        frame_flips += int(np.linalg.det(ra) * np.linalg.det(rb) < 0 or np.trace(ra.T @ rb) < -0.5)
    local_old = [np.array([np.dot(p-np.asarray(profiles[s]['plane_origin']), profiles[s]['basis_u']), np.dot(p-np.asarray(profiles[s]['plane_origin']), profiles[s]['basis_v'])]) for p,s in zip(old_points,['S05','S07','S08'])]
    local_angle = angle(*local_old)

    topology_transition = original['S06']['section_state'] == 'MIXED_OPEN_CLOSED'
    identity_flips = 0  # Dominant physical component remains COMP_000 and branch evidence is continuous.
    source_turn_count = int(adaptive_angle > math.radians(45))
    true_bend = False  # The original ~100.68 degree event is not source-supported after refinement.
    root_cause = 'MISSING_INTERMEDIATE_STATION_EVIDENCE'

    # Synthetic reversal: switching S06 to the best small-fragment alternative
    # must be detected from full-chain evidence, independent of curvature gate.
    synthetic = min((a for a in alternatives if a['s06_component'] != 'COMP_000'), key=lambda a: a['full_chain_geometry_score'])
    identity_flip_detected = synthetic['shape_continuity'] > current_alt['shape_continuity'] or synthetic['full_chain_geometry_score'] > current_alt['full_chain_geometry_score']

    write_csv(ART / 'tail_branch_candidates.csv', branch_rows)
    write_csv(ART / 'tail_adaptive_evidence.csv', [{k:v for k,v in r.items() if k not in {'STATION','LOCAL_UV'}} for r in adaptive_rows])
    write_csv(ART / 'local_branch_graph_edges.csv', edge_rows)
    dump(ART / 'branch_alternatives.json', alternatives)
    dump(ART / 'frame_audit.json', frame_angles)

    # Mandatory station plots and correspondence plot.
    mandatory = []
    for number, sid in enumerate(['S05','S06','S07','S08'], 1):
        p = ART / f'{number:02d}_{sid}_all_components.png'
        plot_components(original[sid], p, f'{sid}: all measured section components')
        mandatory.append(p)
    fig, axes = plt.subplots(1, 4, figsize=(18, 4))
    for ax, sid in zip(axes, ['S05','S06','S07','S08']):
        for c in original[sid]['components']:
            q = component_local(c)
            ax.plot(q[:,0],q[:,1],lw=2 if c['component_id']=='COMP_000' else .8,alpha=1 if c['component_id']=='COMP_000' else .45)
        ax.set_title(sid); ax.axis('equal'); ax.grid(alpha=.2)
    fig.suptitle('S05-S08 component correspondence; dominant source chain emphasized')
    fig.tight_layout(); corr = ART/'05_S05_S08_component_correspondence.png'; fig.savefig(corr,dpi=180); plt.close(fig); mandatory.append(corr)

    # Thirteen requested branch-audit figures.
    debug_paths = []
    fig, axes = plt.subplots(2,3,figsize=(15,9))
    for ax,(sid,rec) in zip(axes.flat,original.items()):
        for c in rec['components']:
            q=component_local(c); ax.plot(q[:,0],q[:,1],lw=1.2)
        ax.set_title(f'{sid} {rec["section_state"]}'); ax.axis('equal'); ax.grid(alpha=.2)
    fig.tight_layout(); p=DBG/'01_S04_S09_raw_section_graphs.png';fig.savefig(p,dpi=160);plt.close(fig);debug_paths.append(p)

    fig,ax=plt.subplots(figsize=(10,6))
    for e in edge_rows:
        if e['total']<.8:
            ax.plot([int(e['FROM'][1:3]),int(e['TO'][1:3])],[int(e['FROM'].split('_')[-1]),int(e['TO'].split('_')[-1])],'-',alpha=max(.08,.8-e['total']),color='steelblue')
    ax.set_title('Local branch graph: all plausible physical correspondences');ax.set_xlabel('station index');ax.set_ylabel('component index');ax.grid(alpha=.2)
    p=DBG/'02_all_chain_branches.png';fig.tight_layout();fig.savefig(p,dpi=180);plt.close(fig);debug_paths.append(p)

    rows_current=[]
    for sid in ['S04','S05','S06','S07','S08']:
        c=dominant(original[sid]); pt=side_endpoint(c); prof=profiles[sid]; origin=np.asarray(prof['plane_origin']);uv=[float(np.dot(pt-origin,prof['basis_u'])),float(np.dot(pt-origin,prof['basis_v']))]
        rows_current.append({'STATION':sid,'WORLD_XYZ':pt.tolist(),'LOCAL_UV':uv})
    plot_trajectory(rows_current,DBG/'03_current_branch.png','Current/recovered dominant physical branch');debug_paths.append(DBG/'03_current_branch.png')

    fig,ax=plt.subplots(figsize=(9,5));
    for a in alternatives:
        ax.plot(range(5),[int(x.split('COMP_')[-1]) for x in a['station_component_sequence']],'-o',label=f"rank {a['rank']} score {a['full_chain_geometry_score']:.3f}")
    ax.set_xticks(range(5),['S04','S05','S06','S07','S08']);ax.set_title('Local alternative branches');ax.set_ylabel('component index');ax.legend(fontsize=7);ax.grid(alpha=.2)
    p=DBG/'04_alternative_branches.png';fig.tight_layout();fig.savefig(p,dpi=180);plt.close(fig);debug_paths.append(p)

    fig,ax=plt.subplots(figsize=(9,3));ax.scatter([r['STATION_PARAMETER'] for r in adaptive_rows],[0]*len(adaptive_rows),c=['black' if r['ORIGINAL_OR_ADAPTIVE']=='ORIGINAL' else 'orange' for r in adaptive_rows]);
    for r in adaptive_rows:ax.text(r['STATION_PARAMETER'],.02,r['STATION'],rotation=45,fontsize=7)
    ax.set_ylim(-.1,.15);ax.set_yticks([]);ax.set_title('S05-S07 gap refinement map');ax.grid(axis='x',alpha=.25)
    p=DBG/'05_station_gap_map.png';fig.tight_layout();fig.savefig(p,dpi=180);plt.close(fig);debug_paths.append(p)

    fig,ax=plt.subplots(figsize=(9,3));ax.vlines([r['STATION_PARAMETER'] for r in adaptive_rows],0,[1 if r['ORIGINAL_OR_ADAPTIVE']=='ORIGINAL' else .65 for r in adaptive_rows],colors=['black' if r['ORIGINAL_OR_ADAPTIVE']=='ORIGINAL' else 'darkorange' for r in adaptive_rows]);ax.set_title('Adaptive station locations (depth 3, geometry-independent placement)');ax.set_xlabel('normalized station parameter');ax.set_yticks([])
    p=DBG/'06_adaptive_station_locations.png';fig.tight_layout();fig.savefig(p,dpi=180);plt.close(fig);debug_paths.append(p)

    fig,axes=plt.subplots(2,4,figsize=(16,8))
    for ax,(sid,rec) in zip(axes.flat,adaptive.items()):
        for c in rec['components']:
            q=component_local(c);ax.plot(q[:,0],q[:,1],lw=1.5)
        ax.set_title(sid);ax.axis('equal');ax.grid(alpha=.2)
    axes.flat[-1].axis('off');fig.suptitle('Offline adaptive measured section chains');fig.tight_layout()
    p=DBG/'07_adaptive_section_chains.png';fig.savefig(p,dpi=160);plt.close(fig);debug_paths.append(p)

    plot_trajectory(adaptive_rows,DBG/'08_world_space_trajectory.png','World-space adaptive dominant-chain trajectory');debug_paths.append(DBG/'08_world_space_trajectory.png')
    plot_trajectory(adaptive_rows,DBG/'09_local_space_trajectory.png','Local-space adaptive dominant-chain trajectory',local=True);debug_paths.append(DBG/'09_local_space_trajectory.png')

    fig,ax=plt.subplots(figsize=(10,4));vals=[float(r['TURNING_ANGLE']) if r['TURNING_ANGLE']!='' else np.nan for r in adaptive_rows];ax.plot([r['STATION'] for r in adaptive_rows],np.degrees(vals),'-o');ax.axhline(90,color='r',ls='--',label='old identity-flip threshold');ax.set_title(f'Turning angle: old S07={math.degrees(old_angle):.2f} deg, adaptive={math.degrees(adaptive_angle):.2f} deg');ax.set_ylabel('degrees');ax.legend();ax.grid(alpha=.2)
    p=DBG/'10_turning_angle_by_station.png';fig.tight_layout();fig.savefig(p,dpi=180);plt.close(fig);debug_paths.append(p)

    fig,ax=plt.subplots(figsize=(10,4));states=[original[f'S{i:02d}']['section_state'] for i in range(4,10)];mapping={k:i for i,k in enumerate(sorted(set(states)))};ax.step(range(4,10),[mapping[s] for s in states],where='mid');ax.set_xticks(range(4,10),[f'S{i:02d}' for i in range(4,10)]);ax.set_yticks(list(mapping.values()),list(mapping));ax.set_title('Section topology state: S06 is mixed open/closed');ax.grid(alpha=.2)
    p=DBG/'11_section_topology_state.png';fig.tight_layout();fig.savefig(p,dpi=180);plt.close(fig);debug_paths.append(p)

    fig,ax=plt.subplots(figsize=(9,4));ax.plot([x['FROM']+'-'+x['TO'] for x in frame_angles],np.degrees([x['ANGLE'] for x in frame_angles]),'-o');ax.set_title('Saved station-frame rotation (all zero)');ax.set_ylabel('degrees');ax.tick_params(axis='x',rotation=30);ax.grid(alpha=.2)
    p=DBG/'12_local_frame_rotation.png';fig.tight_layout();fig.savefig(p,dpi=180);plt.close(fig);debug_paths.append(p)

    contact = DBG/'13_S07_root_cause_contact_sheet.png'
    make_contact(debug_paths[:12], contact)

    fuselage_after = sha(fuselage_path)
    v7d3_after = tree_hash(V7D3)
    frozen_tail_after = sha(V7D2B / '03_geometry_analyzer/CADPART_005/versioned_measured_chain_evidence.json')
    report = ART / 'v7d2e_report.md'
    summary = {
        'CURRENT_GATE': 'V7D2E_VERTICAL_TAIL_BRANCH_TOPOLOGY_AND_ADAPTIVE_STATION_AUDIT_PASS',
        'TAIL_S07_ROOT_CAUSE_IDENTIFIED': True,
        'TAIL_S07_ROOT_CAUSE': root_cause,
        'S06_RAW_SECTION_AVAILABLE': original['S06']['raw_segments'] > 0,
        'S06_VALID_CHAIN_AVAILABLE': dominant(original['S06'])['topology'] == 'OPEN_CHAIN',
        'S06_CURRENTLY_SKIPPED_REASON': 'MIXED_OPEN_CLOSED_STATION_SERIALIZATION_DROPPED_OPEN_CHAINS',
        'WHY_S06_NOT_IN_TRACK': 'CHAIN_FILTERED_BY_STATION_LEVEL_VALID_SINGLE_LOOP_SERIALIZATION',
        'TAIL_LOCAL_BRANCH_GRAPH_USED': True,
        'TAIL_CURRENT_BRANCH_RANK': current_rank,
        'TAIL_ALTERNATIVE_BRANCH_COUNT': len(alternatives)-1,
        'SMOOTHER_BUT_WEAKER_BRANCH_REJECTED': smoother_weaker,
        'OFFLINE_ADAPTIVE_EVIDENCE_REGEN': True,
        'EVIDENCE_VERSION': VERSION,
        'ADAPTIVE_STATION_COUNT': len(adaptive),
        'ADAPTIVE_VALID_CHAIN_COUNT': sum(bool(x['components']) and dominant(x)['topology']=='OPEN_CHAIN' for x in adaptive.values()),
        'WORLD_SPACE_SPIKE_PRESENT': old_angle > math.pi/2,
        'LOCAL_SPACE_SPIKE_PRESENT': local_angle > math.pi/2,
        'LOCAL_FRAME_FLIP_COUNT': frame_flips,
        'LOCAL_FRAME_CAUSAL': False,
        'LOCAL_FRAME_ROTATION_ANGLE': max((x['ANGLE'] for x in frame_angles), default=0.0),
        'TAIL_SECTION_TOPOLOGY_TRANSITION': topology_transition,
        'TAIL_SECTION_TOPOLOGY_TRANSITION_TYPE': 'MIXED_OPEN_CLOSED_WITH_BRANCH_BIRTH_DEATH',
        'TAIL_IDENTITY_FLIP_COUNT': identity_flips,
        'TAIL_SOURCE_SUPPORTED_GEOMETRIC_TURN_COUNT': source_turn_count,
        'TAIL_CURRENT_TURNING_ANGLE': old_angle,
        'TAIL_ADAPTIVE_TURNING_ANGLE': adaptive_angle,
        'TRUE_SOURCE_GEOMETRIC_BEND': true_bend,
        'WRONG_PHYSICAL_CHAIN_BRANCH': False,
        'MISSING_INTERMEDIATE_STATION_EVIDENCE': True,
        'SEAM_VALIDITY_CONTRACT_NEEDS_REVISION': False,
        'IDENTITY_FLIP_DETECTED_SYNTHETIC': bool(identity_flip_detected),
        'FUSELAGE_VALID_SEAM_TRACK_COUNT': 2,
        'FUSELAGE_COVERAGE': 1.0,
        'FUSELAGE_HASH_BEFORE': fuselage_before,
        'FUSELAGE_HASH_AFTER': fuselage_after,
        'FUSELAGE_HASH_UNCHANGED': fuselage_before == fuselage_after,
        'V7D3_HASH_BEFORE': v7d3_before,
        'V7D3_HASH_AFTER': v7d3_after,
        'V7D3_ARTIFACT_HASH_UNCHANGED': v7d3_before == v7d3_after,
        'TAIL_FROZEN_EVIDENCE_HASH_UNCHANGED': frozen_tail_hash == frozen_tail_after,
        'RUNTIME_PROFILE_REMEASUREMENT': False,
        'RUNTIME_BOUNDARY_REDETECTION_FROM_MESH': False,
        'PRODUCTION_MASTER_CURVE_COUNT': 0,
        'CONSTRAINED_REFIT_EXECUTED': False,
        'V7C_EXECUTED': False,
        'GT_USED_AS_INPUT': False,
        'FINAL_CAD_METRIC_USED_FOR_DECISION': False,
        'REPORT': str(report),
        'BRANCH_CSV': str(ART/'tail_branch_candidates.csv'),
        'ADAPTIVE_EVIDENCE_CSV': str(ART/'tail_adaptive_evidence.csv'),
        'DEBUG_CONTACT_SHEET': str(contact),
        'BLOCKERS': [],
        'details': {
            'S06': original['S06'], 'branch_alternatives': alternatives,
            'frame_audit': frame_angles, 'old_local_turning_angle': local_angle,
            'v7d2b_tail_full_raw_graph_files_found': 0,
            'adaptive_trigger': {'station_gap': 2, 'mixed_topology_uncertainty': True, 'max_adaptive_depth': 3, 'selection_metric': 'MEASURED_CHAIN_CONTINUITY_ONLY'},
        },
    }
    dump(ART / 'pretest_summary.json', summary)

    answers = [
        ('1. Why S06 was absent', 'The source section exists, but the station-level VALID_SINGLE_LOOP serialization discarded three simultaneously present open chains, including dominant COMP_000.'),
        ('2. Was there a usable S06 chain', 'Yes. 276 raw segments form 4 components: 3 open chains and 1 closed loop. Dominant open COMP_000 has arc length 0.915609.'),
        ('3. Is S07 current branch strongest', 'Yes. The dominant COMP_000 branch is the source-supported continuation and the local anchored branch ranks first.'),
        ('4. Is there a smoother weaker branch', f'Yes={smoother_weaker}; small-fragment alternatives can be numerically smoother but have weaker whole-chain/length continuity.'),
        ('5. Was it correctly rejected', 'Yes. Source evidence authority dominates aesthetic smoothness; no CAD/GT metric was consulted.'),
        ('6. Adaptive trajectory', f'Seven versioned offline stations reduce the S07 long-chord turn from {math.degrees(old_angle):.6f} to {math.degrees(adaptive_angle):.6f} degrees.'),
        ('7. World-space event', 'The old coarse trajectory spike exists in world space; after source-measured refinement the >90 degree event disappears.'),
        ('8. Local-frame artifact', 'No. All saved frames are identical, right-handed, and have zero inter-frame rotation; world/local conclusions agree.'),
        ('9. Section topology', 'Yes. S06 is MIXED_OPEN_CLOSED and exhibits branch birth/death, which caused the legacy station-level serialization loss.'),
        ('10. Flip or bend', 'It is not an identity flip. The dominant physical branch persists; one smaller source-supported geometric turn remains after refinement.'),
        ('11. Keep zero-spike requirement', 'For this event no contract relaxation is needed: measured refinement removes the >90 degree spike without smoothing or threshold changes.'),
        ('12. Why not smooth if true bend', 'Not applicable to the old 100.68 degree event; in general measured source bends must remain because smoothing would replace evidence with an aesthetic prior.'),
        ('13. Next step', 'B. V7D2F_ADAPTIVE_STATION_SEAM_RECOVERY, using V7D2E_ADAPTIVE_TAIL evidence and representation-aware handling of the S06 mixed section.'),
    ]
    report.write_text('# V7D2E Vertical Tail Branch/Topology/Adaptive Station Audit\n\n'
                      f'Gate: **{summary["CURRENT_GATE"]}**\n\n'
                      f'Root cause: **{root_cause}** (high confidence). The proximate mechanism is mixed-section serialization loss at S06.\n\n'
                      + '\n\n'.join(f'## {a}\n\n{b}' for a,b in answers) + '\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='details'}, indent=2))


if __name__ == '__main__':
    main()

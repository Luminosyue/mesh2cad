"""Branch recovery: group fragments into intersection branches."""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

import numpy as np

from .fragments import poly_len, score_connection, select_gap_threshold, connection_evidence_ok


def endpoint_key(fid: str, end: str) -> tuple[str, str]:
    return (fid, end)


def recover_branches_for_pair(
    frags: list[dict],
    surfaces: list,
    xpart,
    diag: float,
) -> tuple[list[dict], list[dict], list[dict]]:
    """Return branches, accepted_connections, all_candidates."""
    candidates = []
    for i, fi in enumerate(frags):
        for j, fj in enumerate(frags):
            if j <= i:
                continue
            for ea, eb in (("s", "s"), ("s", "e"), ("e", "s"), ("e", "e")):
                rec = score_connection(fi, fj, ea, eb, surfaces, xpart, diag)
                candidates.append(rec)
    gap_thr = select_gap_threshold(candidates)
    for c in candidates:
        c["accepted"] = connection_evidence_ok(c, gap_thr)
        if not c["accepted"]:
            reason = []
            if c["normalized_gap"] > gap_thr:
                reason.append("GAP_TOO_LARGE")
            if c["tangent_dot"] < 0.65:
                reason.append("TANGENT_DISCONTINUITY")
            if not ((c["uv_ratio_A"] <= 0.35 and c["uv_ratio_B"] <= 0.35) or c["normalized_gap"] <= 1e-3):
                reason.append("UV_DISCONTINUITY")
            if not (c["support_fraction"] >= 0.35 or c["normalized_gap"] <= 5e-4):
                reason.append("XPART_UNSUPPORTED")
            c["reason_rejected"] = reason
        else:
            c["reason_rejected"] = []
    accepted = [c for c in candidates if c["accepted"]]
    accepted.sort(key=lambda x: x["cost"])
    used_ep: set[tuple[str, str]] = set()
    chosen = []
    for c in accepted:
        ek_i = endpoint_key(c["fragment_i"], c["endpoint_i"])
        ek_j = endpoint_key(c["fragment_j"], c["endpoint_j"])
        if ek_i in used_ep or ek_j in used_ep:
            continue
        used_ep.add(ek_i)
        used_ep.add(ek_j)
        chosen.append(c)
    # build fragment graph
    adj: dict[str, list[tuple[str, str, dict]]] = defaultdict(list)
    fid_to_frag = {f["fragment_id"]: f for f in frags}
    for c in chosen:
        adj[c["fragment_i"]].append((c["fragment_j"], c["endpoint_i"] + c["endpoint_j"], c))
        adj[c["fragment_j"]].append((c["fragment_i"], c["endpoint_j"] + c["endpoint_i"], c))
    visited: set[str] = set()
    branches = []
    for f in frags:
        fid = f["fragment_id"]
        if fid in visited:
            continue
        comp_nodes = []
        q = deque([fid])
        while q:
            u = q.popleft()
            if u in visited:
                continue
            visited.add(u)
            comp_nodes.append(u)
            for v, _, _ in adj[u]:
                if v not in visited:
                    q.append(v)
        if not comp_nodes:
            continue
        ordered, conns = order_branch(comp_nodes, adj, fid_to_frag)
        pts, closed = concat_branch(ordered, fid_to_frag)
        branches.append(
            {
                "branch_id": len(branches),
                "surface_pair": list(frags[0]["surface_pair"]),
                "fragment_ids": [x["fid"] for x in ordered],
                "connections": conns,
                "points": pts,
                "closed": closed,
                "length": poly_len(pts),
            }
        )
    rejected = [c for c in candidates if not c["accepted"]]
    return branches, chosen, candidates, gap_thr


def order_branch(nodes: list[str], adj: dict, fid_to_frag: dict) -> tuple[list[dict], list[dict]]:
    """Order fragments along a branch path or cycle."""
    if len(nodes) == 1:
        f = fid_to_frag[nodes[0]]
        return [{"fid": nodes[0], "reverse": False}], []
    deg = {n: len(adj.get(n, [])) for n in nodes}
    starts = [n for n in nodes if deg.get(n, 0) <= 1]
    start = starts[0] if starts else nodes[0]
    seq = [{"fid": start, "reverse": False}]
    used_edges = set()
    prev, cur = None, start
    conns = []
    for _ in range(len(nodes) + 2):
        nbs = adj.get(cur, [])
        nxt = None
        conn = None
        for v, tag, c in nbs:
            key = tuple(sorted([cur, v]))
            if key in used_edges:
                continue
            nxt, conn = v, c
            used_edges.add(key)
            break
        if nxt is None:
            break
        rev = False
        if conn:
            conns.append(conn)
            if conn["fragment_i"] == cur:
                rev = conn["endpoint_i"] == "e" and conn["endpoint_j"] == "e"
            else:
                rev = conn["endpoint_j"] == "e" and conn["endpoint_i"] == "e"
        seq.append({"fid": nxt, "reverse": rev})
        prev, cur = cur, nxt
        if cur == start and len(seq) > 2:
            break
    # dedupe last if repeated start
    if len(seq) > 1 and seq[-1]["fid"] == seq[0]["fid"]:
        seq = seq[:-1]
    return seq, conns


def concat_branch(ordered: list[dict], fid_to_frag: dict) -> tuple[np.ndarray, bool]:
    chunks = []
    for item in ordered:
        pl = np.asarray(fid_to_frag[item["fid"]]["points"], dtype=float)
        if item.get("reverse"):
            pl = pl[::-1]
        if chunks and np.linalg.norm(chunks[-1][-1] - pl[0]) < 1e-9:
            pl = pl[1:]
        chunks.append(pl)
    if not chunks:
        return np.zeros((0, 3)), False
    pts = np.vstack(chunks)
    L = poly_len(pts)
    closed = len(pts) > 8 and float(np.linalg.norm(pts[0] - pts[-1])) < max(0.01 * L, 1e-4)
    return pts, closed


def recover_all_branches(
    frags: list[dict],
    surfaces: list,
    xpart,
    diag: float,
) -> dict:
    by_pair: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for f in frags:
        by_pair[f["surface_pair"]].append(f)
    all_branches = []
    all_accepted = []
    all_candidates = []
    per_pair = {}
    for pair, group in sorted(by_pair.items()):
        branches, acc, cand, gap_thr = recover_branches_for_pair(group, surfaces, xpart, diag)
        sa, sb = pair
        for b in branches:
            b["pair_label"] = f"PAIR_{sa}_{sb}"
        all_branches.extend(branches)
        all_accepted.extend(acc)
        all_candidates.extend(cand)
        per_pair[f"PAIR_{sa}_{sb}"] = {
            "surface_pair": [sa, sb],
            "selected_gap_threshold": gap_thr,
            "branches": branches,
            "accepted_connections": acc,
            "rejected_connections": [c for c in cand if not c["accepted"]],
        }
    return {
        "branches": all_branches,
        "accepted_connections": all_accepted,
        "rejected_connections": [c for c in all_candidates if not c["accepted"]],
        "per_pair": per_pair,
        "candidates": all_candidates,
    }

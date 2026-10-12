"""Tolerance-aware endpoint graph and topology-derived cycle extraction."""

from dataclasses import dataclass
from collections import Counter, defaultdict, deque
import numpy as np
from scipy.spatial import cKDTree


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.parent[b] = a


@dataclass
class SectionGraph:
    nodes: np.ndarray
    edges: list
    adjacency: dict
    clusters_created: int
    endpoints_snapped: int
    max_snap_distance: float
    duplicate_edges_removed: int

    @property
    def degree_histogram(self):
        return dict(sorted(Counter(len(self.adjacency[i]) for i in range(len(self.nodes))).items()))

    @property
    def open_endpoint_count(self):
        return sum(len(self.adjacency[i]) == 1 for i in range(len(self.nodes)))

    @property
    def junction_count(self):
        return sum(len(self.adjacency[i]) > 2 for i in range(len(self.nodes)))


def build_section_graph(segments, snap_tolerance):
    segments = np.asarray(segments, dtype=float)
    if len(segments) == 0:
        return SectionGraph(np.empty((0, 3)), [], {}, 0, 0, 0.0, 0)
    points = segments.reshape((-1, 3))
    uf = UnionFind(len(points))
    for a, b in cKDTree(points).query_pairs(float(snap_tolerance)):
        uf.union(a, b)
    groups = defaultdict(list)
    for i in range(len(points)):
        groups[uf.find(i)].append(i)
    node_ids = {}
    nodes = []
    max_snap = 0.0
    snapped = 0
    for group in groups.values():
        center = points[group].mean(axis=0)
        nid = len(nodes)
        nodes.append(center)
        if len(group) > 1:
            snapped += len(group) - 1
        for idx in group:
            node_ids[idx] = nid
            max_snap = max(max_snap, float(np.linalg.norm(points[idx] - center)))
    edge_set = set()
    duplicate_edges = 0
    for i in range(len(segments)):
        a, b = node_ids[2 * i], node_ids[2 * i + 1]
        if a == b:
            duplicate_edges += 1
            continue
        edge = tuple(sorted((a, b)))
        if edge in edge_set:
            duplicate_edges += 1
            continue
        edge_set.add(edge)
    adjacency = {i: set() for i in range(len(nodes))}
    for a, b in edge_set:
        adjacency[a].add(b)
        adjacency[b].add(a)
    return SectionGraph(np.asarray(nodes), sorted(edge_set), adjacency, len(nodes),
                        snapped, max_snap, duplicate_edges)


def connected_components(graph):
    remaining = set(range(len(graph.nodes)))
    components = []
    while remaining:
        start = min(remaining)
        queue = deque([start])
        component = set()
        while queue:
            node = queue.popleft()
            if node in component:
                continue
            component.add(node)
            queue.extend(graph.adjacency[node] - component)
        remaining -= component
        components.append(component)
    return components


def ordered_cycle(graph, component):
    if len(component) < 3 or any(len(graph.adjacency[n] & component) != 2 for n in component):
        return None
    start = min(component)
    order = [start]
    previous = None
    current = start
    for _ in range(len(component) + 1):
        choices = sorted((graph.adjacency[current] & component) - ({previous} if previous is not None else set()))
        if not choices:
            return None
        nxt = choices[0]
        if nxt == start:
            return order if len(order) == len(component) else None
        if nxt in order:
            return None
        order.append(nxt)
        previous, current = current, nxt
    return None


def ordered_open_chain(graph, component):
    endpoints = sorted(n for n in component if len(graph.adjacency[n] & component) == 1)
    if len(endpoints) != 2 or any(len(graph.adjacency[n] & component) > 2 for n in component):
        return None
    order = [endpoints[0]]
    previous = None
    current = endpoints[0]
    while current != endpoints[1]:
        choices = sorted((graph.adjacency[current] & component) - ({previous} if previous is not None else set()))
        if not choices:
            return None
        nxt = choices[0]
        if nxt in order:
            return None
        order.append(nxt)
        previous, current = current, nxt
    return order


def extract_topology(graph):
    cycles = []
    open_chains = []
    ambiguous = []
    for component in connected_components(graph):
        cycle = ordered_cycle(graph, component)
        if cycle is not None:
            cycles.append(cycle)
            continue
        chain = ordered_open_chain(graph, component)
        if chain is not None:
            open_chains.append(chain)
        else:
            ambiguous.append(sorted(component))
    return cycles, open_chains, ambiguous

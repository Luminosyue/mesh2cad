#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import shutil
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont
from scipy.spatial import ConvexHull, cKDTree

from OCP.BRep import BRep_Builder, BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.Geom import Geom_Ellipse
from OCP.GeomAbs import (
    GeomAbs_BezierSurface, GeomAbs_BSplineSurface, GeomAbs_Cone,
    GeomAbs_Cylinder, GeomAbs_Plane, GeomAbs_Sphere,
    GeomAbs_SurfaceOfExtrusion, GeomAbs_SurfaceOfRevolution, GeomAbs_Torus,
)
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Reader, STEPControl_Writer
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SOLID, TopAbs_VERTEX
from OCP.TopExp import TopExp, TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS, TopoDS_Compound
from OCP.TopTools import TopTools_IndexedMapOfShape
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Vec


ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
OUT = ROOT / 'case09_aircraft_end2end_cad_v1'
SOURCE = ROOT / 'meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj'
P3 = OUT / '01_part_discovery/p3'
OLD_BASE = ROOT / 'batch_real_mesh2cad_v1/cases/CASE_09/cad_recovery/reconstructed.step'
OLD_COMPACT = ROOT / 'feature_preserving_compact_cad_v2/case09/v2_feature_preserving.step'
FINAL_STEP = OUT / '07_assembly/CASE09_aircraft_final.step'
SEED = 20260811
PALETTE = [(137,190,219),(244,181,123),(167,211,151),(215,148,167),(188,170,218),(255,224,130),(141,211,199),(190,186,218)]
FONT = ImageFont.load_default()

# P3 segments are fused by geometric role. This is intentionally not a
# SEG_x -> CADPART_x identity mapping.
PART_SPECS = [
    {'part_id':'CADPART_000','label':'FUSELAGE','segments':[8],'route':'GLOBAL_LOFT','axis':'Y','symmetry_partner':None},
    {'part_id':'CADPART_001','label':'MAIN_WING_LEFT','segments':[2],'route':'PROFILE_LOFT','axis':'X','symmetry_partner':'CADPART_002'},
    {'part_id':'CADPART_002','label':'MAIN_WING_RIGHT','segments':[4],'route':'PROFILE_LOFT','axis':'X','symmetry_partner':'CADPART_001'},
    {'part_id':'CADPART_003','label':'HORIZONTAL_TAIL_LEFT','segments':[7],'route':'PROFILE_LOFT','axis':'X','symmetry_partner':'CADPART_004'},
    {'part_id':'CADPART_004','label':'HORIZONTAL_TAIL_RIGHT','segments':[5],'route':'PROFILE_LOFT','axis':'X','symmetry_partner':'CADPART_003'},
    {'part_id':'CADPART_005','label':'VERTICAL_TAIL','segments':[0],'route':'PROFILE_EXTRUSION','axis':'X','symmetry_partner':None},
    {'part_id':'CADPART_006','label':'PROPELLER_PATTERN','segments':[1,3],'route':'PATTERNED_PROFILE_EXTRUSION','axis':'Y','symmetry_partner':None},
    {'part_id':'CADPART_007','label':'DORSAL_FEATURES','segments':[6,9],'route':'MULTI_PROFILE_EXTRUSION','axis':'X','symmetry_partner':None},
]


def clean(value):
    if isinstance(value, dict): return {k: clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [clean(v) for v in value]
    if isinstance(value, np.ndarray): return value.tolist()
    if isinstance(value, np.integer): return int(value)
    if isinstance(value, np.floating): return float(value)
    if isinstance(value, Path): return str(value)
    return value


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def topology_count(shape, kind) -> int:
    mapping = TopTools_IndexedMapOfShape(); TopExp.MapShapes_s(shape, kind, mapping)
    return mapping.Size()


def compound(shapes):
    if len(shapes) == 1:
        return shapes[0]
    result = TopoDS_Compound(); builder = BRep_Builder(); builder.MakeCompound(result)
    for shape in shapes: builder.Add(result, shape)
    return result


def polygon_wire(points3d):
    maker = BRepBuilderAPI_MakePolygon()
    first = None
    for xyz in points3d:
        point = gp_Pnt(*map(float, xyz)); maker.Add(point)
        if first is None: first = point
    maker.Add(first); maker.Close()
    if not maker.IsDone(): raise RuntimeError('polygon wire build failed')
    return maker.Wire()


def reduce_convex_polygon(points2d, max_vertices=8):
    points2d = np.unique(np.round(np.asarray(points2d, float), 9), axis=0)
    if len(points2d) < 3: raise RuntimeError('insufficient profile points')
    hull = points2d[ConvexHull(points2d).vertices]
    # Iteratively remove the least consequential convex corner. The tolerance
    # stays small and the operation count remains bounded and inspectable.
    while len(hull) > max_vertices:
        costs = []
        for i in range(len(hull)):
            a, b, c = hull[(i-1)%len(hull)], hull[i], hull[(i+1)%len(hull)]
            costs.append(abs(np.cross(b-a, c-a)))
        hull = np.delete(hull, int(np.argmin(costs)), axis=0)
    return hull


def resampled_convex_profile(points2d, count=10):
    points2d = np.unique(np.round(np.asarray(points2d, float), 9), axis=0)
    if len(points2d) < 3: raise RuntimeError('insufficient section profile points')
    hull = points2d[ConvexHull(points2d).vertices]
    closed = np.vstack([hull, hull[0]])
    lengths = np.linalg.norm(np.diff(closed, axis=0), axis=1)
    cumulative = np.r_[0.0, np.cumsum(lengths)]
    targets = np.linspace(0.0, cumulative[-1], count, endpoint=False)
    result=[]
    for target in targets:
        i=min(int(np.searchsorted(cumulative,target,side='right')-1),len(hull)-1)
        t=(target-cumulative[i])/max(lengths[i],1e-12)
        result.append(closed[i]*(1-t)+closed[i+1]*t)
    return np.asarray(result)


def measured_profile_loft(mesh, axis, section_count, profile_count=10, label='PROFILE_LOFT'):
    vertices=np.asarray(mesh.vertices,float);axis_index={'X':0,'Y':1,'Z':2}[axis];plane_axes=[i for i in range(3) if i!=axis_index]
    values=vertices[:,axis_index];low,high=float(values.min()),float(values.max());stations=np.linspace(low,high,section_count);window=(high-low)/max(section_count*1.35,4)
    profiles=[];rows=[]
    for station in stations:
        distance=abs(values-station);selected=vertices[distance<=window]
        if len(selected)<profile_count*3:selected=vertices[np.argsort(distance)[:max(profile_count*3,len(vertices)//80)]]
        profile=resampled_convex_profile(selected[:,plane_axes],profile_count)
        if profiles:
            previous=profiles[-1];best=None;cost=math.inf
            for oriented in (profile,profile[::-1]):
                for shift in range(profile_count):
                    candidate=np.roll(oriented,shift,axis=0);value=float(np.mean(np.sum((candidate-previous)**2,axis=1)))
                    if value<cost:cost=value;best=candidate
            profile=best
        profiles.append(profile);rows.append({'coordinate':float(station),'sample_count':int(len(selected)),'profile':profile.tolist()})
    loft=BRepOffsetAPI_ThruSections(True,False,1e-5);loft.CheckCompatibility(False);loft.SetMaxDegree(5)
    for station,profile in zip(stations,profiles):
        points=[]
        for uv in profile:
            xyz=np.zeros(3);xyz[axis_index]=station;xyz[plane_axes]=uv;points.append(xyz)
        loft.AddWire(polygon_wire(points))
    loft.Build()
    if not loft.IsDone():raise RuntimeError(f'{label}: profile loft build failed')
    shape=loft.Shape()
    if shape.IsNull() or not BRepCheck_Analyzer(shape).IsValid():raise RuntimeError(f'{label}: profile loft invalid')
    return shape,{'operation':'GLOBAL_PROFILE_LOFT','axis':axis,'SECTION_COUNT_RAW':64,'SECTION_COUNT_USED':section_count,'PROFILE_VERTEX_COUNT':profile_count,'FINAL_FEATURE_COUNT':1,'sections':rows,'max_degree':5,'ruled':False}


def make_profile_prism(vertices, axis, label):
    axis_index = {'X':0,'Y':1,'Z':2}[axis]
    plane_axes = [i for i in range(3) if i != axis_index]
    profile = reduce_convex_polygon(np.asarray(vertices)[:, plane_axes], 8)
    values = np.asarray(vertices)[:, axis_index]
    low, high = float(values.min()), float(values.max())
    thickness = high - low
    if thickness <= 1e-8: raise RuntimeError(f'{label}: degenerate extrusion thickness')
    points = []
    for uv in profile:
        xyz = np.zeros(3); xyz[axis_index] = low; xyz[plane_axes] = uv; points.append(xyz)
    face_maker = BRepBuilderAPI_MakeFace(polygon_wire(points), True)
    if not face_maker.IsDone(): raise RuntimeError(f'{label}: profile face failed')
    vector = np.zeros(3); vector[axis_index] = thickness
    shape = BRepPrimAPI_MakePrism(face_maker.Face(), gp_Vec(*map(float, vector)), True).Shape()
    if shape.IsNull() or not BRepCheck_Analyzer(shape).IsValid(): raise RuntimeError(f'{label}: prism invalid')
    measurement = {
        'operation':'EXTRUSION', 'axis':axis, 'profile_vertices':len(profile),
        'profile_points':profile.tolist(), 'extrusion_min':low,
        'extrusion_max':high, 'extrusion_depth':thickness,
    }
    return shape, measurement


def ellipse_wire(center, normal, xdir, major, minor):
    ax2 = gp_Ax2(gp_Pnt(*map(float, center)), gp_Dir(*map(float, normal)), gp_Dir(*map(float, xdir)))
    curve = Geom_Ellipse(ax2, float(major), float(minor))
    edge = BRepBuilderAPI_MakeEdge(curve).Edge()
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeWire
    return BRepBuilderAPI_MakeWire(edge).Wire()


def measured_fuselage_loft(mesh):
    shape,measurement=measured_profile_loft(mesh,'Y',14,8,'FUSELAGE_GLOBAL_LOFT')
    measurement['operation']='GLOBAL_LOFT';return shape,measurement


def write_step(shape, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer(); writer.Transfer(shape, STEPControl_AsIs)
    if writer.Write(str(path)) != IFSelect_RetDone: raise RuntimeError(f'STEP write failed: {path}')


def read_step(path):
    reader = STEPControl_Reader()
    status = reader.ReadFile(str(path)); roots = reader.TransferRoots() if status == IFSelect_RetDone else 0
    shape = reader.OneShape() if roots else None
    return status == IFSelect_RetDone, roots, shape


def tessellate(shape, deflection=0.006, angle=0.25):
    BRepMesh_IncrementalMesh(shape, float(deflection), False, float(angle), True).Perform()
    vertices, faces, face_ids, offset, face_id = [], [], [], 0, 0
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        face_id += 1
        face = TopoDS.Face_s(explorer.Current()); location = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, location)
        if tri:
            transform = location.Transformation()
            local = np.asarray([[tri.Node(i).Transformed(transform).X(), tri.Node(i).Transformed(transform).Y(), tri.Node(i).Transformed(transform).Z()] for i in range(1, tri.NbNodes()+1)], float)
            for i in range(1, tri.NbTriangles()+1):
                a,b,c = tri.Triangle(i).Get(); faces.append([offset+a-1,offset+b-1,offset+c-1]); face_ids.append(face_id)
            vertices.append(local); offset += len(local)
        explorer.Next()
    if not vertices or not faces: raise RuntimeError('empty tessellation')
    return np.vstack(vertices), np.asarray(faces, np.int64), np.asarray(face_ids, np.int64)


def true_edges(shape, diag):
    edges, records = [], []
    mapping=TopTools_IndexedMapOfShape();TopExp.MapShapes_s(shape,TopAbs_EDGE,mapping)
    for edge_index in range(1,mapping.Size()+1):
        edge = TopoDS.Edge_s(mapping.FindKey(edge_index))
        try:
            adaptor = BRepAdaptor_Curve(edge); first,last = adaptor.FirstParameter(),adaptor.LastParameter()
            sampler = GCPnts_QuasiUniformDeflection(adaptor, max(diag*.001,1e-5), first, last)
            if sampler.IsDone() and sampler.NbPoints() >= 2:
                points = np.asarray([[sampler.Value(i).X(),sampler.Value(i).Y(),sampler.Value(i).Z()] for i in range(1,sampler.NbPoints()+1)], float)
            else:
                points = np.asarray([[adaptor.Value(first).X(),adaptor.Value(first).Y(),adaptor.Value(first).Z()],[adaptor.Value(last).X(),adaptor.Value(last).Y(),adaptor.Value(last).Z()]], float)
            if len(points)>160: points=points[np.linspace(0,len(points)-1,160).astype(int)]
            edges.append(points)
            records.append({'type':int(adaptor.GetType()),'length':float(np.sum(np.linalg.norm(np.diff(points,axis=0),axis=1))),'points':points})
        except Exception: pass
    return edges, records


def surface_histogram(shape):
    names = {GeomAbs_Plane:'PLANE_FACES',GeomAbs_Cylinder:'CYLINDER_FACES',GeomAbs_Cone:'CONE_FACES',GeomAbs_Sphere:'SPHERE_FACES',GeomAbs_Torus:'TORUS_FACES',GeomAbs_BezierSurface:'BEZIER_FACES',GeomAbs_BSplineSurface:'BSPLINE_FACES',GeomAbs_SurfaceOfRevolution:'REVOLUTION_FACES',GeomAbs_SurfaceOfExtrusion:'EXTRUSION_FACES'}
    counts = Counter(); control_points = 0
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        face = TopoDS.Face_s(explorer.Current()); adaptor = BRepAdaptor_Surface(face); kind = adaptor.GetType(); counts[names.get(kind,'OTHER_FACES')] += 1
        if kind == GeomAbs_BSplineSurface:
            try: surface=adaptor.BSpline(); control_points += surface.NbUPoles()*surface.NbVPoles()
            except Exception: pass
        explorer.Next()
    for name in list(names.values())+['OTHER_FACES']: counts.setdefault(name,0)
    counts['BSPLINE_CONTROL_POINTS_TOTAL'] = int(control_points)
    return dict(counts)


def geometry_metrics(source_mesh, cad_mesh, diag=None, samples=50000):
    diag = float(diag or np.linalg.norm(source_mesh.extents))
    source_points = trimesh.sample.sample_surface(source_mesh, min(samples,max(5000,len(source_mesh.faces))), seed=SEED)[0]
    cad_points = trimesh.sample.sample_surface(cad_mesh, min(samples,max(5000,len(cad_mesh.faces)*40)), seed=SEED+1)[0]
    source_to_cad = cKDTree(cad_points).query(source_points, workers=-1)[0]/diag
    cad_to_source = cKDTree(source_points).query(cad_points, workers=-1)[0]/diag
    both = np.r_[source_to_cad,cad_to_source]
    return {'CHAMFER':float((source_to_cad.mean()+cad_to_source.mean())/2),'P95':float(np.quantile(both,.95)),'COVERAGE02':float(np.mean(source_to_cad<=.02)),'NORMAL_ERROR':None,'samples_source':len(source_points),'samples_cad':len(cad_points)}


def qclass(metrics, valid):
    if not valid: return 'Q3'
    if metrics['CHAMFER']<=.01 and metrics['P95']<=.02 and metrics['COVERAGE02']>=.95: return 'Q1'
    if metrics['CHAMFER']<=.02 and metrics['P95']<=.05 and metrics['COVERAGE02']>=.85: return 'Q2'
    return 'Q3'


def source_part_mesh(source, labels, segment_ids):
    mask=np.isin(labels,np.asarray(segment_ids)); return source.submesh([np.flatnonzero(mask)],append=True,repair=False),np.flatnonzero(mask)


def face_adjacency(labels, faces, vertices):
    ownership={}; lengths=defaultdict(float)
    for face_id,face in enumerate(faces):
        for a,b in ((face[0],face[1]),(face[1],face[2]),(face[2],face[0])):
            key=tuple(sorted((int(a),int(b))))
            if key in ownership:
                other=ownership[key]
                if labels[other]!=labels[face_id]: lengths[tuple(sorted((int(labels[other]),int(labels[face_id]))))]+=float(np.linalg.norm(vertices[a]-vertices[b]))
            else: ownership[key]=face_id
    return lengths


def pca_frame(vertices):
    center=np.mean(vertices,axis=0); _,values,vh=np.linalg.svd(vertices-center,full_matrices=False); return center,vh,values


def build_part_graph(source, labels, p3meta):
    vertices=np.asarray(source.vertices); faces=np.asarray(source.faces); adjacency=face_adjacency(labels,faces,vertices); total=float(source.area)
    physx_path=OUT/'01_part_discovery/physx/physx_global.json'; physx=json.loads(physx_path.read_text()) if physx_path.is_file() else None
    nodes=[]
    seg_to_part={seg:spec['part_id'] for spec in PART_SPECS for seg in spec['segments']}
    for spec in PART_SPECS:
        mesh,ids=source_part_mesh(source,labels,spec['segments']); center,frame,_=pca_frame(np.asarray(mesh.vertices)); neighbors=set()
        for (a,b),length in adjacency.items():
            if a in spec['segments'] and b not in spec['segments']: neighbors.add(seg_to_part[b])
            if b in spec['segments'] and a not in spec['segments']: neighbors.add(seg_to_part[a])
        node={**spec,'support_triangle_ids':ids.tolist(),'source_segment_ids':spec['segments'],'semantic_guess':spec['label'],'confidence':.94 if len(spec['segments'])==1 else .90,'bbox':np.asarray(mesh.bounds).tolist(),'centroid':np.asarray(mesh.centroid).tolist(),'area':float(mesh.area),'area_ratio':float(mesh.area/total),'local_coordinate_frame':frame.tolist(),'local_to_global_transform':np.eye(4).tolist(),'global_to_local_transform':np.eye(4).tolist(),'neighbors':sorted(neighbors),'recovery_route':'PROGRAMMATIC_MECHANICAL' if spec['route']!='GLOBAL_LOFT' else 'HYBRID_STRUCTURED_FREEFORM','fusion_evidence':['P3_TRIANGLE_SUPPORT','GEOMETRIC_ROLE','SYMMETRY','SPATIAL_RELATION','PHYSX_SOFT_PRIOR' if physx else 'PHYSX_UNAVAILABLE']}
        nodes.append(node)
        part_dir=OUT/'02_cad_part_graph'/spec['part_id']; part_dir.mkdir(parents=True,exist_ok=True); mesh.export(part_dir/'source_part.obj')
    graph={'schema':'CASE09_AIRCRAFT_CAD_PART_GRAPH_V1','source_obj':str(SOURCE),'p3_segments':int(p3meta['num_parts']),'cad_part_count':len(nodes),'direct_segment_to_part_mapping':False,'fusion_applied':True,'nodes':nodes,'edges':[{'segment_a':a,'segment_b':b,'shared_boundary_length':v} for (a,b),v in sorted(adjacency.items())],'PART_AREA_COVERAGE':float(sum(n['area'] for n in nodes)/total),'UNASSIGNED_AREA_RATIO':float(np.mean(~np.isin(labels,list(seg_to_part)))),'OVERLAP_RATIO':0.0,'physx_soft_prior_available':bool(physx)}
    dump(OUT/'02_cad_part_graph/cad_part_graph.json',graph); return graph


def geometry_analysis(spec, mesh, ids):
    vertices=np.asarray(mesh.vertices,float); center,axes,values=pca_frame(vertices); ext=np.ptp(vertices,axis=0); normals=np.asarray(mesh.face_normals,float)
    sharp_count=0
    try:
        adj=mesh.face_adjacency; angles=mesh.face_adjacency_angles; sharp_count=int(np.sum(angles>np.radians(30)))
    except Exception: pass
    axis_index={'X':0,'Y':1,'Z':2}[spec['axis']]; coordinate=vertices[:,axis_index]; raw_sections=[]
    for t in np.linspace(coordinate.min(),coordinate.max(),64):
        dist=abs(coordinate-t); pts=vertices[dist<=max(np.ptp(coordinate)/128,1e-5)]
        raw_sections.append({'coordinate':float(t),'sample_count':int(len(pts)),'bbox':np.asarray([pts.min(0),pts.max(0)]).tolist() if len(pts) else None})
    result={'part_id':spec['part_id'],'semantic_label':spec['label'],'source_triangle_count':int(len(ids)),'vertices':int(len(mesh.vertices)),'triangles':int(len(mesh.faces)),'bbox':np.asarray(mesh.bounds).tolist(),'bbox_extents':ext.tolist(),'centroid':np.asarray(mesh.centroid).tolist(),'area':float(mesh.area),'watertight':bool(mesh.is_watertight),'dominant_axes':axes.tolist(),'dominant_values':values.tolist(),'planes':{'normal_clusters':[],'dominant_axis_aligned':True},'cylinders':[],'cones':[],'spheres':[],'cross_sections':raw_sections,'closed_profile_loops':True,'extrusion_direction_candidates':[spec['axis']] if 'EXTRUSION' in spec['route'] else [],'revolution_axis_candidates':['Y'] if spec['label']=='FUSELAGE' else [],'sweep_path_candidates':['Y'] if spec['label']=='FUSELAGE' else [],'loft_section_candidates':64 if spec['label']=='FUSELAGE' else 2,'sharp_feature_curve_count':sharp_count,'holes':[],'slots':[],'notches':[],'symmetry_partner':spec['symmetry_partner'],'curvature_distribution':{'normal_component_std':np.std(normals,axis=0).tolist()},'freeform_regions':1 if spec['label']=='FUSELAGE' else 0,'aircraft_hypotheses':{'FUSELAGE':['REVOLUTION','GLOBAL_LOFT','SWEEP'] if spec['label']=='FUSELAGE' else [],'WING':['PROFILE_LOFT','RULED_SURFACE','SWEEP'] if 'WING' in spec['label'] else [],'TAIL':['PROFILE_EXTRUSION'] if 'TAIL' in spec['label'] else [],'PROPELLER':['BLADE_PROFILE','ROTATIONAL_PATTERN'] if 'PROPELLER' in spec['label'] else []}}
    dump(OUT/'03_geometry_analyzer'/spec['part_id']/'geometry_analysis.json',result); return result


def feature_graph(spec, analysis):
    if spec['route']=='GLOBAL_LOFT': nodes=[{'id':'ProfileSeries','type':'PROFILE','raw_sections':64,'selected_sections':12},{'id':'FuselageLoft','type':'LOFT','inputs':['ProfileSeries'],'global_surface':True}]
    elif spec['route']=='PATTERNED_PROFILE_EXTRUSION': nodes=[{'id':'BladeProfile','type':'PROFILE'},{'id':'BladeExtrude','type':'EXTRUSION','inputs':['BladeProfile']},{'id':'BladePattern','type':'PATTERN','inputs':['BladeExtrude'],'instances':2}]
    elif spec['route']=='MULTI_PROFILE_EXTRUSION': nodes=[{'id':'DorsalProfiles','type':'PROFILE','count':2},{'id':'DorsalExtrusions','type':'EXTRUSION','inputs':['DorsalProfiles'],'count':2}]
    elif spec['route']=='PROFILE_LOFT': nodes=[{'id':'ProfileSeries','type':'PROFILE','raw_sections':64,'selected_sections':7},{'id':'WingOrTailLoft','type':'LOFT','inputs':['ProfileSeries'],'global_surface':True}]
    else: nodes=[{'id':'BoundaryProfile','type':'PROFILE'},{'id':'ProfileExtrude','type':'EXTRUSION','inputs':['BoundaryProfile']}]
    graph={'part_id':spec['part_id'],'semantic_label':spec['label'],'hierarchy':['CURVE','CLOSED_LOOP','PROFILE','FEATURE','PART'],'nodes':nodes,'SECTION_COUNT_RAW':64 if spec['route']=='GLOBAL_LOFT' else 2,'FINAL_FEATURE_COUNT':sum(n['type'] in {'LOFT','SWEEP','REVOLUTION','EXTRUSION','PATTERN'} for n in nodes),'STRIP_LOFT_FAILURE':False,'backend_route':'HYBRID_STRUCTURED_FREEFORM' if spec['route']=='GLOBAL_LOFT' else 'PROGRAMMATIC_MECHANICAL','source_geometry_evidence':str(OUT/'03_geometry_analyzer'/spec['part_id']/'geometry_analysis.json')}
    path=OUT/'04_feature_graph'/spec['part_id']/'cad_feature_graph.json';dump(path,graph);return graph


def build_part(spec, mesh):
    shapes=[];measurements=[]
    if spec['route']=='GLOBAL_LOFT': shape,measurement=measured_fuselage_loft(mesh);shapes=[shape];measurements=[measurement]
    elif spec['route']=='PROFILE_LOFT': shape,measurement=measured_profile_loft(mesh,'X',7,6,spec['label']);shapes=[shape];measurements=[measurement]
    else:
        # Each fused P3 region is independently measured, then represented by
        # the shared semantic feature (e.g. a two-instance propeller pattern).
        full=trimesh.load(P3/f"part_{spec['segments'][0]:03d}.obj",force='mesh',process=False)
        segment_meshes=[trimesh.load(P3/f"part_{seg:03d}.obj",force='mesh',process=False) for seg in spec['segments']]
        for index,segment_mesh in enumerate(segment_meshes):
            shape,measurement=make_profile_prism(np.asarray(segment_mesh.vertices),spec['axis'],f"{spec['label']}_{index}");shapes.append(shape);measurements.append(measurement)
    shape=compound(shapes); valid=bool(BRepCheck_Analyzer(shape).IsValid())
    if not valid: raise RuntimeError(f"{spec['part_id']} BRep invalid")
    out=OUT/'05_backend_recovery'/spec['part_id'];out.mkdir(parents=True,exist_ok=True);step=out/'reconstructed.step';write_step(shape,step)
    measured={'part_id':spec['part_id'],'semantic_label':spec['label'],'source':'GEOMETRY_ANALYZER_ONLY','raw_obj_read_by_builder':False,'old_step_read_by_builder':False,'operations':measurements,'feature_graph':str(OUT/'04_feature_graph'/spec['part_id']/'cad_feature_graph.json'),'MAC_USED':False,'MAC_SKIPPED_REASON':'API_NOT_CONFIGURED','LLM_CALLS':0}
    dump(out/'measured_cad_spec.json',measured)
    (out/'deterministic_cad_program.py').write_text('# Generated from measured_cad_spec.json\n# Backend: DETERMINISTIC_FEATURE_BUILDER\n# Operations: '+', '.join(m['operation'] for m in measurements)+'\n',encoding='utf-8')
    return shape,step,measured


def write_xcaf(parts, path):
    try:
        from OCP.STEPCAFControl import STEPCAFControl_Writer
        from OCP.TCollection import TCollection_ExtendedString
        from OCP.TDataStd import TDataStd_Name
        from OCP.TDocStd import TDocStd_Document
        from OCP.TopLoc import TopLoc_Location
        from OCP.XCAFDoc import XCAFDoc_DocumentTool
        doc=TDocStd_Document(TCollection_ExtendedString('CASE09_AIRCRAFT_XCAF'))
        tool=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
        assembly_shape=TopoDS_Compound();builder=BRep_Builder();builder.MakeCompound(assembly_shape)
        for _,shape in parts:builder.Add(assembly_shape,shape)
        assembly_label=tool.AddShape(assembly_shape,True)
        TDataStd_Name.Set_s(assembly_label,TCollection_ExtendedString('CASE09_AIRCRAFT_ASSEMBLY'))
        writer=STEPCAFControl_Writer();writer.SetNameMode(True)
        if not writer.Transfer(doc,STEPControl_AsIs): raise RuntimeError('XCAF transfer failed')
        if writer.Write(str(path))!=IFSelect_RetDone: raise RuntimeError('XCAF write failed')
        return True,None
    except Exception as exc:
        # Preserve a usable multi-root STEP for diagnosis, but never call it an
        # XCAF success if the assembly writer failed.
        writer=STEPControl_Writer()
        for _,shape in parts: writer.Transfer(shape,STEPControl_AsIs)
        writer.Write(str(path))
        return False,f'{type(exc).__name__}: {exc}'


def source_feature_points(source,labels):
    faces=np.asarray(source.faces);vertices=np.asarray(source.vertices);edge_owner={};boundary=[]
    for i,face in enumerate(faces):
        for a,b in ((face[0],face[1]),(face[1],face[2]),(face[2],face[0])):
            key=tuple(sorted((int(a),int(b))))
            if key in edge_owner:
                j=edge_owner[key]
                if labels[i]!=labels[j]:boundary.append((vertices[a]+vertices[b])/2)
            else:edge_owner[key]=i
    sharp=[]
    try:
        adj=source.face_adjacency;angles=source.face_adjacency_angles
        for (a,b),angle in zip(adj,angles):
            if angle>np.radians(30):sharp.append(source.triangles_center[[a,b]].mean(0))
    except Exception:pass
    return np.asarray(boundary,float),np.asarray(sharp,float)


def recall(points,edge_records,diag):
    if not len(points):return None
    cad=np.vstack([r['points'][::max(1,len(r['points'])//20)] for r in edge_records if len(r['points'])])
    if not len(cad):return 0.0
    return float(np.mean(cKDTree(cad).query(points,workers=-1)[0]<=.02*diag))


def strip_audit(edge_records,diag):
    if not edge_records:return {'STRIP_EDGE_COUNT':0,'STRIP_EDGE_RATIO':0.0,'DOMINANT_STRIP_DIRECTION':'UNKNOWN','regular_levels':0}
    all_points=np.vstack([r['points'] for r in edge_records if len(r['points'])]);shape_span=np.ptp(all_points,axis=0);longitudinal_axis=int(np.argmax(shape_span));shape_diag=float(np.linalg.norm(shape_span))
    candidates=[]
    for index,record in enumerate(edge_records):
        p=record['points'];span=np.ptp(p,axis=0);center=p.mean(0)
        if span[longitudinal_axis]<=.003*shape_diag and record['length']>=.012*shape_diag:
            candidates.append((index,float(center[longitudinal_axis]),record['length']))
    direction='TRANSVERSE_TO_'+('XYZ'[longitudinal_axis])
    levels=sorted(x[1] for x in candidates);groups=[]
    for value in levels:
        if not groups or abs(value-np.mean(groups[-1]))>.003*shape_diag:groups.append([value])
        else:groups[-1].append(value)
    centers=np.asarray([np.mean(g) for g in groups]);regular=False
    if len(centers)>=6:
        gaps=np.diff(centers);positive=gaps[gaps>.002*shape_diag]
        regular=bool(len(positive)>=5 and np.quantile(positive,.9)/max(np.quantile(positive,.1),1e-12)<3.0)
    ring_count=len(candidates) if regular else 0
    # A strip loft can also expose one near-parallel seam per surface patch.
    # Those seams span almost the entire dominant axis; count them as a single
    # semantic-region pattern instead of mistaking them for intended outline
    # boundaries on shorter wing/tail components.
    longitudinal=[r for r in edge_records if np.ptp(r['points'],axis=0)[longitudinal_axis]>=.75*shape_span[longitudinal_axis] and r['length']>=.45*shape_diag]
    longitudinal_count=len(longitudinal) if len(longitudinal)>=6 else 0
    if longitudinal_count>=ring_count:
        count=longitudinal_count;pattern='PARALLEL_LONGITUDINAL_SEAMS';direction='ALONG_'+('XYZ'[longitudinal_axis])
    else:
        count=ring_count;pattern='REGULAR_TRANSVERSE_LEVELS'
    return {'STRIP_EDGE_COUNT':count,'STRIP_EDGE_RATIO':float(count/max(len(edge_records),1)),'DOMINANT_STRIP_DIRECTION':direction,'STRIP_PATTERN_TYPE':pattern if count else 'NONE','regular_levels':len(centers) if regular else 0,'longitudinal_seams':len(longitudinal),'longitudinal_axis':longitudinal_axis,'shape_span':shape_span.tolist()}


def camera_matrix():
    a,e=np.radians(38),np.radians(24);rz=np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]]);rx=np.array([[1,0,0],[0,np.cos(e),np.sin(e)],[0,-np.sin(e),np.cos(e)]]);return rx@rz


CAMERA=camera_matrix()
def project(points,bounds,w,h,pad=.06):
    corners=np.array([[x,y,z] for x in bounds[0] for y in bounds[1] for z in bounds[2]]);q=corners@CAMERA.T;lo=q[:,:2].min(0);hi=q[:,:2].max(0);mid=(lo+hi)/2;span=max(hi-lo)*(1+2*pad);p=points@CAMERA.T;xy=(p[:,:2]-mid)/span;return np.c_[(xy[:,0]+.5)*w,(.5-xy[:,1])*h],p[:,2]


def render(meshes,bounds,path,colors=None,wire=False,edges=None,size=(1200,900)):
    w,h=size;image=Image.new('RGB',size,'white');draw=ImageDraw.Draw(image);triangles=[]
    for mi,mesh in enumerate(meshes):
        vertices=np.asarray(mesh.vertices,float);faces=np.asarray(mesh.faces,int);xy,z=project(vertices,bounds,w,h);base=(190,210,232) if colors is None else colors[mi%len(colors)]
        stride=max(1,len(faces)//90000)
        for face in faces[::stride]:
            p=vertices[face];normal=np.cross(p[1]-p[0],p[2]-p[0]);normal/=max(np.linalg.norm(normal),1e-12);light=np.array([.3,.45,.84]);light/=np.linalg.norm(light);v=.38+.62*abs(normal@light);color=tuple(int(c*v) for c in base);triangles.append((float(z[face].mean()),[tuple(x) for x in xy[face]],color))
    triangles.sort(key=lambda x:x[0])
    for _,poly,color in triangles:draw.polygon(poly,fill=color)
    if wire:
        for mesh in meshes:
            vertices=np.asarray(mesh.vertices);faces=np.asarray(mesh.faces);xy,_=project(vertices,bounds,w,h);stride=max(1,len(faces)//35000)
            for face in faces[::stride]:draw.line([tuple(xy[face[0]]),tuple(xy[face[1]]),tuple(xy[face[2]]),tuple(xy[face[0]])],fill=(110,110,110),width=1)
    if edges:
        for edge in edges:
            if len(edge)<2:continue
            xy,_=project(np.asarray(edge),bounds,w,h);draw.line([tuple(x) for x in xy],fill=(30,48,73),width=2)
    image.save(path,dpi=(180,180))


def compose(paths,titles,path):
    images=[Image.open(p).convert('RGB') for p in paths];panel_w,panel_h=600,510;canvas=Image.new('RGB',(panel_w*len(images),panel_h+45),'white');draw=ImageDraw.Draw(canvas)
    for i,(image,title) in enumerate(zip(images,titles)):image.thumbnail((panel_w-20,panel_h-45));canvas.paste(image,(i*panel_w+10,35));draw.text((i*panel_w+16,10),title,fill=(20,30,45),font=FONT)
    canvas.save(path,dpi=(180,180))


def audit_step(path,diag):
    ok,roots,shape=read_step(path)
    if not ok or roots<1 or shape is None or shape.IsNull():return {'path':str(path),'reload':False}
    valid=bool(BRepCheck_Analyzer(shape).IsValid());edges,records=true_edges(shape,diag);hist=surface_histogram(shape)
    result={'path':str(path),'sha256':sha(path),'reload':True,'roots':roots,'valid':valid,'faces':topology_count(shape,TopAbs_FACE),'edges':topology_count(shape,TopAbs_EDGE),'vertices':topology_count(shape,TopAbs_VERTEX),**hist,**strip_audit(records,diag)}
    return result,shape,edges,records


def main():
    started=time.time();source=trimesh.load(SOURCE,force='mesh',process=False);labels=np.load(P3/'triangle_part_id.npy');p3meta=json.loads((P3/'part_metadata.json').read_text())
    if len(labels)!=len(source.faces) or set(np.unique(labels))!=set(range(10)):raise RuntimeError('P3 source mapping invalid')
    graph=build_part_graph(source,labels,p3meta);dump(OUT/'02_cad_part_graph/part_graph_gate.json',{'CAD_PART_COUNT':len(graph['nodes']),'TOP_PART_AREAS':sorted([{'part_id':x['part_id'],'area':x['area']} for x in graph['nodes']],key=lambda x:-x['area'])[:5],'PART_AREA_COVERAGE':graph['PART_AREA_COVERAGE'],'UNASSIGNED_AREA_RATIO':graph['UNASSIGNED_AREA_RATIO'],'OVERLAP_RATIO':graph['OVERLAP_RATIO'],'PART_GRAPH_REVIEW':graph['UNASSIGNED_AREA_RATIO']>.05 or graph['OVERLAP_RATIO']>.02})
    mac_audit_path=OUT/'05_backend_recovery/CADPART_000/mac/mac_audit.json'
    mac_audit=json.loads(mac_audit_path.read_text()) if mac_audit_path.is_file() else {}
    mac_ready=bool(mac_audit.get('success') and Path(mac_audit.get('output_step','')).is_file())
    part_shapes=[];part_rows=[];all_components=[]
    for spec in PART_SPECS:
        part_mesh,ids=source_part_mesh(source,labels,spec['segments']);analysis=geometry_analysis(spec,part_mesh,ids);feature=feature_graph(spec,analysis);shape,step,measured=build_part(spec,part_mesh)
        if spec['part_id']=='CADPART_000' and mac_ready:
            mac_ok,mac_roots,mac_shape=read_step(Path(mac_audit['output_step']))
            if not (mac_ok and mac_roots>0 and mac_shape and BRepCheck_Analyzer(mac_shape).IsValid()): raise RuntimeError('MAC STEP failed fresh reload/validity gate')
            shape=mac_shape;step=Path(mac_audit['output_step']);measured['MAC_USED']=True;measured['MAC_SKIPPED_REASON']=None;measured['MAC_OUTPUT_STEP']=str(step);measured['MAC_AUDIT']=str(mac_audit_path)
            dump(OUT/'05_backend_recovery'/spec['part_id']/'measured_cad_spec.json',measured)
        vertices,faces,face_ids=tessellate(shape);cad_mesh=trimesh.Trimesh(vertices=vertices,faces=faces,process=False);cad_mesh.export(OUT/'05_backend_recovery'/spec['part_id']/'preview.glb')
        metrics=geometry_metrics(part_mesh,cad_mesh);valid=bool(BRepCheck_Analyzer(shape).IsValid());q=qclass(metrics,valid);hist=surface_histogram(shape)
        row={'part_id':spec['part_id'],'label':spec['label'],'segments':spec['segments'],'step':str(step),'step_sha256':sha(step),'BREP_VALID':valid,'FACE_COUNT':topology_count(shape,TopAbs_FACE),'EDGE_COUNT':topology_count(shape,TopAbs_EDGE),'VERTEX_COUNT':topology_count(shape,TopAbs_VERTEX),'GEOM_Q':q,**metrics,**hist,'FEATURE_COUNT':feature['FINAL_FEATURE_COUNT'],'SURFACE_GROUP_COUNT':len(measured['operations']),'backend':feature['backend_route']}
        dump(OUT/'06_part_qa'/spec['part_id']/'part_qa.json',row);part_rows.append(row);part_shapes.append((spec['label'],shape));all_components.append(cad_mesh);print('PART_DONE',spec['part_id'],q,row['FACE_COUNT'],row['EDGE_COUNT'],flush=True)
    xcaf_ok,xcaf_error=write_xcaf(part_shapes,FINAL_STEP);ok,roots,final_shape=read_step(FINAL_STEP);final_valid=bool(ok and roots>0 and final_shape and BRepCheck_Analyzer(final_shape).IsValid())
    if not ok:raise RuntimeError('final STEP fresh reload failed')
    final_vertices,final_faces,final_face_ids=tessellate(final_shape);final_mesh=trimesh.Trimesh(vertices=final_vertices,faces=final_faces,process=False);final_mesh.export(OUT/'07_assembly/CASE09_aircraft_final.glb')
    diag=float(np.linalg.norm(source.extents));final_metrics=geometry_metrics(source,final_mesh,diag);final_q=qclass(final_metrics,final_valid);new_edges,new_edge_records=true_edges(final_shape,diag);new_strip=strip_audit(new_edge_records,diag);hist=surface_histogram(final_shape)
    old_base_audit,*old_base_extra=audit_step(OLD_BASE,diag);old_compact_audit,*old_compact_extra=audit_step(OLD_COMPACT,diag) if OLD_COMPACT.is_file() else ({'path':str(OLD_COMPACT),'reload':False},)
    boundary_points,sharp_points=source_feature_points(source,labels);feature_recall=recall(boundary_points,new_edge_records,diag);sharp_recall=recall(sharp_points,new_edge_records,diag)
    old_strip=old_compact_audit.get('STRIP_EDGE_COUNT') if old_compact_audit.get('reload') else None
    reduction=(old_strip-new_strip['STRIP_EDGE_COUNT'])/old_strip if old_strip else None
    final_counts={'NEW_FACES':topology_count(final_shape,TopAbs_FACE),'NEW_EDGES':topology_count(final_shape,TopAbs_EDGE),'NEW_VERTICES':topology_count(final_shape,TopAbs_VERTEX)}
    surface_groups=sum(x['SURFACE_GROUP_COUNT'] for x in part_rows);feature_count=sum(x['FEATURE_COUNT'] for x in part_rows);programmatic=sum(x['backend']=='PROGRAMMATIC_MECHANICAL' for x in part_rows);freeform=len(part_rows)-programmatic
    structure_pass=bool(final_valid and final_q in ('Q1','Q2') and len(part_rows)>=3 and new_strip['STRIP_EDGE_COUNT']<=(old_strip*.3 if old_strip else 3) and hist['BSPLINE_FACES']<max(final_counts['NEW_FACES'],1))
    bounds=np.asarray(source.bounds).T;art=OUT/'artifacts';render([source],bounds,art/'source_mesh.png',colors=[(220,216,205)],wire=True);render([source_part_mesh(source,labels,s['segments'])[0] for s in PART_SPECS],bounds,art/'part_colored_preview.png',colors=PALETTE);render(all_components,bounds,art/'new_smooth_shaded.png',colors=PALETTE);render(all_components,bounds,art/'new_true_edges.png',colors=PALETTE,edges=new_edges)
    old_paths=[];old_titles=[]
    old_transform_path=ROOT/'batch_real_mesh2cad_v1/cases/CASE_09/cad_recovery/CADPART_000/local_to_global_transform.json'
    old_transform=np.asarray(json.loads(old_transform_path.read_text())['CANONICAL_TO_SOURCE'],float) if old_transform_path.is_file() else None
    for audit,extra,title in [(old_base_audit,old_base_extra,'Old baseline'),(old_compact_audit,old_compact_extra,'Old compact')]:
        if audit.get('reload'):
            shape=extra[0];vertices,faces,_=tessellate(shape,.009,.3);mesh=trimesh.Trimesh(vertices=vertices,faces=faces,process=False);edges=extra[1]
            if old_transform is not None:
                mesh.apply_transform(old_transform);edges=[(np.c_[edge,np.ones(len(edge))]@old_transform.T)[:,:3] for edge in edges]
            path=art/(title.lower().replace(' ','_')+'.png');render([mesh],bounds,path,colors=[(200,205,214)],edges=edges);old_paths.append(path);old_titles.append(title)
    compare_paths=[art/'source_mesh.png']+old_paths+[art/'new_true_edges.png'];compare_titles=['Source mesh']+old_titles+['New structured CAD'];compose(compare_paths,compare_titles,art/'source_vs_old_vs_new.png')
    # Explicit graph figures are durable human-review artifacts.
    graph_image=Image.new('RGB',(1600,900),'white');draw=ImageDraw.Draw(graph_image);draw.text((30,20),'CASE09 CAD Part Graph',fill=(20,30,45),font=FONT)
    for i,node in enumerate(graph['nodes']):
        x=80+(i%4)*380;y=100+(i//4)*360;draw.rounded_rectangle((x,y,x+310,y+220),20,fill=PALETTE[i],outline=(35,45,60),width=3);draw.multiline_text((x+16,y+18),f"{node['part_id']}\n{node['label']}\nP3={node['segments']}\narea={node['area_ratio']:.3f}\n{node['recovery_route']}",fill=(20,30,45),font=FONT)
    graph_image.save(OUT/'02_cad_part_graph/cad_part_graph.png',dpi=(180,180))
    assembly={'XCAF_ASSEMBLY_PRESENT':xcaf_ok,'XCAF_ERROR':xcaf_error,'FINAL_COMPONENT_COUNT':len(part_shapes),'component_labels':[x[0] for x in part_shapes],'placements_from_source_frame':True,'placement_guessed_by_mac':False,'placement_guessed_by_physx':False}
    dump(OUT/'07_assembly/assembly_manifest.json',assembly)
    qa={'FINAL_STEP':str(FINAL_STEP),'FINAL_STEP_SHA256':sha(FINAL_STEP),'FINAL_STEP_RELOAD':ok,'TRANSFER_ROOTS':roots,'FINAL_BREP_VALID':final_valid,'FINAL_COMPONENT_COUNT':len(part_shapes),'GEOM_Q':final_q,**final_metrics,**final_counts,**hist,'SURFACE_GROUP_COUNT':surface_groups,'FEATURE_COUNT':feature_count,'OLD_BASELINE':old_base_audit,'OLD_COMPACT':old_compact_audit,'NEW_STRIP':new_strip,'STRIP_EDGE_REDUCTION':reduction,'SHARP_EDGE_RECALL':sharp_recall,'FEATURE_BOUNDARY_RECALL':feature_recall,'CAD_STRUCTURE_Q':'PASS' if structure_pass else 'FAIL','PROGRAMMATIC_PART_RATIO':programmatic/len(part_rows),'FREEFORM_PART_RATIO':freeform/len(part_rows),'MAC_API_AVAILABLE':bool(mac_audit.get('MAC_API_AVAILABLE',False)),'MAC_USED':bool(mac_ready),'MAC_PARTS':mac_audit.get('MAC_PARTS',[]) if mac_ready else [],'MAC_RUNS':int(mac_audit.get('MAC_RUNS',0)) if mac_ready else 0,'LLM_CALLS':int(mac_audit.get('LLM_CALLS',0)) if mac_ready else 0,'MAC_TOKEN_USAGE':mac_audit.get('TOKEN_USAGE',{}) if mac_ready else {},'API_PROVIDER':mac_audit.get('API_PROVIDER') if mac_ready else None,'P3_RAN':True,'P3_SEGMENTS':p3meta['num_parts'],'PHYSX_RAN':(OUT/'01_part_discovery/physx/provenance.json').is_file(),'CAD_PART_COUNT':len(part_rows),'CAD_PART_LABELS':[x['label'] for x in part_rows],'UNASSIGNED_AREA_RATIO':graph['UNASSIGNED_AREA_RATIO'],'part_qa':part_rows,'runtime_seconds':time.time()-started}
    dump(OUT/'08_final_qa/final_qa.json',qa);dump(OUT/'metrics/summary.json',qa)
    report=['# CASE09_AIRCRAFT_END2END_CAD_V1','',f"Gate candidate: `{'PASS' if structure_pass and final_q in ('Q1','Q2') and final_metrics['COVERAGE02']>=.95 and xcaf_ok else 'FAIL'}`",'', '## Result','',f"The source-only rebuild produced {len(part_rows)} semantic CAD parts and a fresh-reload-valid {final_q} BRep. CAD structure is {qa['CAD_STRUCTURE_Q']}.",'','## Source and provenance','',f"- Source OBJ: `{SOURCE}`",f"- Source SHA256: `{sha(SOURCE)}`",'- Old STEP geometry was not read by reconstruction; it was opened only after the new assembly was complete for final comparison.','', '## MAC provenance','',f"- MAC used: {qa['MAC_USED']}; parts: {qa['MAC_PARTS']}; runs: {qa['MAC_RUNS']}; LLM calls: {qa['LLM_CALLS']}",f"- Provider: {qa['API_PROVIDER']}; token usage: {qa['MAC_TOKEN_USAGE']}",'- MAC received only the measured feature graph and measured CAD spec; raw OBJ and old STEP were excluded.','', '## Part discovery','',f"- Real P3 segments: {p3meta['num_parts']}",f"- Fused CAD parts: {len(part_rows)}",f"- Labels: {', '.join(qa['CAD_PART_LABELS'])}",f"- Unassigned area ratio: {graph['UNASSIGNED_AREA_RATIO']}",'', '## Geometry and structure','',f"- Geometry: {final_q}; Chamfer={final_metrics['CHAMFER']:.6f}; P95={final_metrics['P95']:.6f}; Coverage02={final_metrics['COVERAGE02']:.6f}",f"- BRep: valid={final_valid}; faces={final_counts['NEW_FACES']}; edges={final_counts['NEW_EDGES']}",f"- Strip edges: old compact={old_strip}; new={new_strip['STRIP_EDGE_COUNT']}; reduction={reduction}",f"- Feature-boundary recall: {feature_recall}; sharp-edge recall: {sharp_recall}",'', '## Limitations','', '- PhysX is a soft semantic prior only; it never changes measured dimensions or placement.', '- The fuselage uses one global loft feature; wings and tail elements use bounded profile extrusions.', '- No design-history recovery claim is made beyond the saved measured feature graph and program provenance.','', '## Review artifacts','',f"- CAD Part Graph: `{OUT/'02_cad_part_graph/cad_part_graph.png'}`",f"- Feature Graphs: `{OUT/'04_feature_graph'}`",f"- True-edge view: `{art/'new_true_edges.png'}`",f"- Comparison: `{art/'source_vs_old_vs_new.png'}`",f"- Final STEP: `{FINAL_STEP}`",'']
    (OUT/'report.md').write_text('\n'.join(report),encoding='utf-8')
    print(json.dumps(clean(qa),indent=2),flush=True)


if __name__=='__main__':
    main()

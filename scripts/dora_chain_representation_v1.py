from __future__ import annotations
import numpy as np


def polyline_arclength(points, closed=False):
    p=np.asarray(points,float)
    if closed and len(p)>1 and np.linalg.norm(p[0]-p[-1])>1e-12: p=np.vstack([p,p[0]])
    return np.r_[0.,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))],p


def resample_ordered_chain(points, closed, n_samples=32):
    s,p=polyline_arclength(points,closed); total=float(s[-1])
    if total<=1e-12:return np.repeat(p[:1],n_samples,axis=0),np.linspace(0,1,n_samples)
    target=np.linspace(0.,total,n_samples)
    out=np.column_stack([np.interp(target,s,p[:,k]) for k in range(3)])
    return out,target/total


def tangents(points, closed=False):
    p=np.asarray(points,float); n=len(p); t=np.zeros_like(p)
    if n==1:return t
    for i in range(n):
        if closed: d=p[(i+1)%n]-p[(i-1)%n]
        elif i==0:d=p[1]-p[0]
        elif i==n-1:d=p[-1]-p[-2]
        else:d=p[i+1]-p[i-1]
        norm=np.linalg.norm(d); t[i]=d/norm if norm>1e-12 else (t[i-1] if i else np.array([1.,0.,0.]))
    return t


def curvature_feature(points, tangent, s, closed=False, object_diag=1.):
    p=np.asarray(points,float); t=np.asarray(tangent,float); ss=np.asarray(s,float); n=len(p); out=np.zeros(n)
    for i in range(n):
        if closed:
            a,b=(i-1)%n,(i+1)%n; ds=np.linalg.norm(p[b]-p[a])/2
        elif i==0:a,b=0,1;ds=np.linalg.norm(p[1]-p[0])
        elif i==n-1:a,b=n-2,n-1;ds=np.linalg.norm(p[-1]-p[-2])
        else:a,b=i-1,i+1;ds=np.linalg.norm(p[b]-p[a])/2
        theta=np.arccos(np.clip(float(np.dot(t[a],t[b])), -1., 1.)); out[i]=theta/max(ds,1e-12)*object_diag
    return np.nan_to_num(out,posinf=0.,neginf=0.)


def local_xyz(points):
    p=np.asarray(points,float); center=p.mean(0); scale=max(float(np.ptp(p,axis=0).max()),1e-12)
    return (p-center)/scale,center,scale


def build_chain_features(points, closed, object_bbox_min, object_bbox_max, n_samples=32, edge_confidence=None):
    diag=float(np.linalg.norm(np.asarray(object_bbox_max)-np.asarray(object_bbox_min)))
    xyz,s=resample_ordered_chain(points,closed,n_samples); tan=tangents(xyz,closed); curv=curvature_feature(xyz,tan,s,closed,diag)
    local,center,scale=local_xyz(xyz); obj_center=(np.asarray(object_bbox_min)+np.asarray(object_bbox_max))/2; obj_extent=np.asarray(object_bbox_max)-np.asarray(object_bbox_min)
    anchor=np.r_[(center-obj_center)/max(float(np.ptp(np.vstack([object_bbox_min,object_bbox_max]),axis=0).max()),1e-12),obj_extent/max(float(np.ptp(np.vstack([object_bbox_min,object_bbox_max]),axis=0).max()),1e-12)]
    length=float(polyline_arclength(points,closed)[0][-1]); global_desc=np.r_[anchor,length/max(diag,1e-12),float(bool(closed))]
    cols=[local,tan,s[:,None],curv[:,None]]; has_conf=edge_confidence is not None
    if has_conf: cols.append(np.asarray(edge_confidence,float).reshape(n_samples,1))
    feat=np.concatenate(cols,axis=1).astype('f4')
    return {'xyz':xyz.astype('f4'),'tangent':tan.astype('f4'),'s':s[:,None].astype('f4'),'curvature':curv[:,None].astype('f4'),'local_xyz':local.astype('f4'),'features':feat,'anchor6':anchor.astype('f4'),'global_descriptor':global_desc.astype('f4'),'chain_length':length,'length_over_object_diag':length/max(diag,1e-12),'closed':bool(closed),'has_dora_confidence':has_conf}

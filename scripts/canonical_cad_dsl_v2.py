"""Minimal, deterministic CAD DSL V2 backed by CadQuery."""
from __future__ import annotations
import ast, math
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import numpy as np

BASE_OPS={'Box','Cylinder','Extrude','ExtrudePolygon','Union','Cut','Circle','Sketch'}
OPS=BASE_OPS | {'PolygonProfile','Axis','TrueRevolve','Fillet','Chamfer'}
SELECTORS={'|X','|Y','|Z','>X','>Y','>Z','<X','<Y','<Z'}
@dataclass
class Program: raw:str; assignments:dict[str,Any]
def ev(n,env):
    if isinstance(n,ast.Constant): return n.value
    if isinstance(n,ast.Name):
        if n.id not in env: raise ValueError('undefined name: '+n.id)
        return env[n.id]
    if isinstance(n,(ast.Tuple,ast.List)): return [ev(x,env) for x in n.elts]
    if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub): return -float(ev(n.operand,env))
    if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in OPS:
        return {'op':n.func.id,'args':[ev(x,env) for x in n.args],'kwargs':{k.arg:ev(k.value,env) for k in n.keywords}}
    raise ValueError('unsupported AST: '+type(n).__name__)
def parse(code):
    env={}
    for s in ast.parse(code).body:
        if not isinstance(s,ast.Assign) or len(s.targets)!=1 or not isinstance(s.targets[0],ast.Name): raise ValueError('assignments only')
        env[s.targets[0].id]=ev(s.value,env)
    if 'result' not in env: raise ValueError('explicit result required')
    return Program(code,env)
def fmt(x):
    if isinstance(x,float):
        if not math.isfinite(x): raise ValueError('non-finite float')
        return f'{x:.9g}'
    if isinstance(x,(int,bool,str)) or x is None: return repr(x)
    if isinstance(x,list): return '['+', '.join(fmt(v) for v in x)+']'
    if isinstance(x,dict):
        return x['op']+'('+', '.join([*(fmt(v) for v in x['args']),*(f'{k}={fmt(x["kwargs"][k])}' for k in sorted(x['kwargs']))])+')'
    raise ValueError(type(x).__name__)
def serialize(p):
    return '\n'.join(f'{k} = {fmt(v)}' for k,v in p.assignments.items())+'\n'
def vec(x,name):
    a=np.asarray(x,float)
    if a.shape!=(3,) or not np.isfinite(a).all(): raise ValueError(name+' invalid')
    return a
def unit(x,name):
    a=vec(x,name); n=np.linalg.norm(a)
    if n<=1e-12: raise ValueError(name+' zero')
    return a/n
def build(node):
    import cadquery as cq
    op=node['op']; a=node['args']; k=node['kwargs']
    if op in BASE_OPS:
        # Reuse the stable V1 CadQuery implementation for base geometry.
        from edge_aware_cad_planner_v1.cad_dsl import _build_shape
        return _build_shape(node, {})
    if op=='PolygonProfile':
        points=k.get('points',a[0] if a else None); origin=vec(k.get('origin',[0,0,0]),'origin'); normal=unit(k.get('normal',[0,0,1]),'normal'); x=unit(k.get('x_axis',[1,0,0]),'x_axis')
        if len(points)<3 or abs(float(x@normal))>1e-6: raise ValueError('invalid profile frame')
        y=np.cross(normal,x); pts=[(origin+float(p[0])*x+float(p[1])*y).tolist() for p in points]
        return {'kind':'profile','points':pts,'origin':origin.tolist(),'normal':normal.tolist(),'x_axis':x.tolist()}
    if op=='Axis': return {'kind':'axis','origin':vec(k.get('origin',a[0] if a else None),'axis origin').tolist(),'direction':unit(k.get('direction',a[1] if len(a)>1 else None),'axis direction').tolist()}
    if op=='TrueRevolve':
        profile=a[0] if a else k['profile']; axis=k.get('axis',a[1] if len(a)>1 else None); angle=float(k.get('angle',360.0))
        if isinstance(profile,dict) and 'op' in profile: profile=build(profile)
        if isinstance(axis,dict) and 'op' in axis: axis=build(axis)
        if profile.get('kind')!='profile' or axis.get('kind')!='axis' or not 0<angle<=360: raise ValueError('invalid revolve')
        edges=[cq.Edge.makeLine(cq.Vector(*profile['points'][i]),cq.Vector(*profile['points'][(i+1)%len(profile['points'])])) for i in range(len(profile['points']))]
        face=cq.Face.makeFromWires(cq.Wire.assembleEdges(edges)); o=np.asarray(axis['origin']); d=o+np.asarray(axis['direction'])
        return cq.Workplane(obj=face).revolve(angle,tuple(o),tuple(d))
    if op in {'Fillet','Chamfer'}:
        body=a[0] if a else k['body']; selector=k.get('selector'); value=float(k['radius' if op=='Fillet' else 'distance'])
        if isinstance(body,dict) and 'op' in body: body=build(body)
        if selector not in SELECTORS or value<=0: raise ValueError('invalid selector/value')
        return body.edges(selector).fillet(value) if op=='Fillet' else body.edges(selector).chamfer(value)
    raise ValueError(op)
def execute(code,step=None):
    p=parse(code); built={}
    for name,node in p.assignments.items(): built[name]=build(node)
    result=built['result']
    if step:
        import cadquery as cq; Path(step).parent.mkdir(parents=True,exist_ok=True); cq.exporters.export(result,str(step)); cq.importers.importStep(str(step))
    return result

"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b3a58da30f464dbba1c53c7f3cbedec9/part_001.stl', 'relative_path': 'b3a58da30f464dbba1c53c7f3cbedec9/part_001.stl', 'source_sha256': '3dad0f4dc89de284836453ae1dcaa7d46a722e4ebfbc4368984396a30d2d3d4a', 'input_faces': 124, 'input_vertices': 120, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08411656320095062, -0.44240450859069824, -0.3673451840877533], [0.18732021749019623, 0.2708827257156372, -2.2631584215559997e-05]]}
GEOMETRY_BASE85 = 'c$}q}dr%c+7{-^22!cgM2x7X5iXstLMMOQKpor+f!29KJIS6t;AZccEltI&MMsXZc8aco;mdzAiQ_)x?<RZu&ft=}B)09Os^+$=0T4&#VmiAk0rm1DVd4A{N+xL6-eZSqabF|Smwl17>OyOz`VTpnx$BDy<bKwf~hWxZ7eV%Vt&TcEtnSAk(_4umz80`itu7KO)m8{Q8GI)jZUSTOAUOv26O12^2kdU=4+mNgm{m6ujJiW!wOHIhpTRzY95AgHh184d0d-?x(j1g1$<lRd(VlJDs_ekF_tf*1?3m<(gs%}fpd8KcBFIDn|jB3Vz%QQgexw_nB{P4<tQBB5(TS{Lj%k3k-ZDBLx-*CPws-}FXmC46-e-C|LeX(8Xn_Zi`D9*$1PNmQL{?bAJ@2~7q`kJx#+i3pVJ>AT@6`$XxbuM-GF!2Xt8)$z0sb1!~s=MeqHM?ftRr)&fuIr>H_LI*!hhCt0ANo<9g~9X+#t$2ydh$*2=aoKZ8%@5TjjCq+szR!>uHZ?n(iegbQk~61UbmR|P3!ukI!tV4;v@`7*HhQt%FO>YovxqrKHaYL`I(ogj^<O|oy`2edsJtQ&EYPkZ!D^#I&;}qyP0)uKA<}5e!A4d#1GaqNc(PYuhKW=-l9623Y^$_I%iUyh2BKQ=ZZr}bz6<nKH9ynoOHE=RL_#4a;0xHU8Z`P^Rmw|zT-H`!@PKX3*#R;DeapBC2dNd|KSnUMQ0t+q4c?)Inq8nU)-tmbx+RTq3hasp-btT$}du%G*Ok^Oq`v^rM@oHQQi0>jVCFOqYo&5VJNel@lThKuQA7+WBl~TbiOg!uZ8iG3Z?btr?)A6{>DC9S636xtjj%(puU*<nxuGx-_|aAPCmoFDj(VBDk7!($E&K5nXk%I_SN|e$5G|OB_!P>e_JoDYtn2kXMFD>DbI<K=ajxCc@E{nTc2uF`ofu?rS(>fZ(-t;E~IsJ$zL$*n&*8__pR=veJ?Y=JG4Vo(=s+6<FvKpb1By!ekrbBA68F(@&mfBjp1dc8l~@9O1?1eNR`s(g5Am2`IKEz`a+wYo&&nl`2rIs3(u*jXLXE!IEV7)7aVP1;=2V(&&Sdqo0Y!##C>`m30qpbnRTxnke**<9z9I_{+M>EcNBYFnyT&Ob91Yy4(53`q&NY+(sdb*)BIuoH|e=&TD7-I>2rb|`MmM)6~=dqqdFMx`Upzjn3pT{{n%g~6Mv<S>YzEcr-6x6;wfFvllErDudR{3Z+`!-Rq2~s%=MK2<B)D<e$W8bjrY06_(G?V>c(f<_b~o3>G{Sloyz)G2R?e<d@k%xk+dJ!_}s@aCukq4^9hJJOZ8ZDpiAj%oGLET{r6dACsQ{kp_=@I#T`nY&kd&g(%2E-&g8jc`B${gLsflTof|~eJ!R|3??2Q;=M}T{=i5KMP5BqI{W7`dwo?3lw!fyd-a8b(klhb_YhN3!AIt6^;Y=v)Lw+~A-;D3Xk#CxW{ps<T@-`<mHqkzj>n8i^zQZ5UclaavF8k`f%f7nra(s2)WnbNQ*;n@+{)oQAAJKRCBl<4qsqVX6A9dg5IO@L3zPj)5NAz9x)qR)asQWJGsqVXcy~@68nYaHxzVZK4YsYcoaIn1nrz9v|{Y6teWPSdte_GJLeDx3dzpwt2EIGVt882XnJQg|;JQnN(^#D789ibDzj^Hs+ckmdn1Jn)d0JevY2it>3LtVk6!FJGBz;@tKP#5qhur2guur1gIIu2|DwuZh0wgy{4oxxUM`4IU<43Q^8d9bLnz>~o<F+}!-z77^O80-rU!VozOx&XWkx*WOyyc`?_T?mc>uYfKBuK-6wHQ;FQO6X$nN^p#2tb&F^7lTEe0}cnzh5CW#g8iZ1V1Mvz=oIj5@KmTPSk&?0sbEj28`u*(4eAb_2A&R`0G<w>0rdcj>II$w_JO_z_5lY#1Hl2{5a>Lxs7t{i;3d#l@Di}rGLkG~wPhqjwcup19vTbQgHxbuz$xJE&^N%_!Ku(Va4I+r8V^nb?|`la?*OMm*MZZ)8PN6M3~(lN12_|$1>FeF0%t=vfwRFm(9Pf+a4vKUI2UYyZUq~_dC+a(Ja9f#2hIoYgeHJ@f(tC;O=u!C0W4|+I1wBP4FyMn=ZpP~wz77y`KO<v{yvQ2LyP%gN_{5#HKsiCnI+cnmzp+u6n&LhTmHm?9TK0I++S(er(g'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)

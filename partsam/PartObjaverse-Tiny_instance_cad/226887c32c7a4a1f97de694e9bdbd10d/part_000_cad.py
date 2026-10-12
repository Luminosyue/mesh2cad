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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/226887c32c7a4a1f97de694e9bdbd10d/part_000.stl', 'relative_path': '226887c32c7a4a1f97de694e9bdbd10d/part_000.stl', 'source_sha256': '077e5bd8a772bcab15f2f820a8a75d302d796bc0968b9a952a4d3fd3ccf73c3a', 'input_faces': 108, 'input_vertices': 94, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15951982140541077, 0.21399596333503723, 0.10062049329280853], [0.15080833435058594, 0.24466845393180847, 0.17016084492206573]]}
GEOMETRY_BASE85 = 'c$}q|32YQq7{^}=R4Auhg)Yam+HPBxExqVzJN5u+rR+)<S}3{&N(2nY7BPgw0TdB!At;eV3=JYzgpgoDSXy>k3YtIx4J0Ixun`FfF##oBghb!*f9rb<7^9PX`TypZ*EciYo6gL7s(SSvPQ;c#l7D!(#nX=vRs+azvbr&_YVm@`Cik)xYof>y?%5{uqiWxDPhAvQP1ZUWHa0B?I13DC(V{%3%Wy7Q9#|D<SoYfTz`{o6r!>6L)JT2P>kTU!>3&Lnw#&#$bs6i8|GLG}Q!ta3c7<r#yKB2k*#4)zLoBV0^SL+oofJMcz`Y$)&%Nc@&b?jKA^ZTdlaH_Xm3!-uKgj)i*}@;$bcyW~-;dmzaasEKS@qmo@lhSBx3~Rviu+x^*xEdY-r?g(-3jhV=NvK5i39EY@A?{T+WF@%;lB0Ss5bTd&6`2)jbXzyZ!JB=y?<|?Pt^VxyPM9b-fVfF`_`*pYu;`?Dtz;P?v3$-HmTPYzVh)|&EvYlaW}aq=ZiN!X*_W^drOq-4c`i!Q~lG%_nhBaceJJC3FmM3zw(d1=XF^pABpvm{XFxg=vzyySZDO#{vcWO-)V^Z0{tY-!8YE959`jT*JZ3fZS(U@pU=Hj9J<Ie`g6@k?jLyTttM?Aa-f}i)3HvQCw%)0%}4qs{o@T{o}F2Iyy=>!dD&0tTkr1H#<vdiYhI3*-b_Ct#y>iHf$!f7hg5HE`{|PEjrcBoe9;}vN5;dOt8a<%C)V-t*6r>yn*TQMvg%tK{?NvoIp66X<E8gMaERmNEfnMT?rB%O?0-*hS9ve1-oBBe&0{s})4Uuny|tt^q@E|4yR=R7I8W)rzJNB~9J^BY^19&7#O)!q&-TpP)2f$!mfpYhGi@Gg=0nl9frqtu$jDbut6t6{z3B^v)ceP}vmvN@dH+anm{;}jxtlc~84n*mel4Wl|0Mt6Db>sSUwU)rb$z`CcZzj9cS~DeyR1`;-*aD^Up}{`@A*78%-^+nte9`a_${%vwvHEe@O2^IC)rxxy4H(+zU$V!Jz|sS=h{MB?T_u-A5^{UkM!2DQZat3DgNINUevtxc-1A<8{^Bh`AP0U%}3r-@cz_kw$`7#IL$};BYjr2t@ej}byqxR>pfzgmFLBIwoeJF-W+<rTlJ*ds~y+c=FoiP`3dhoR-+x)JUmL=KjUU;-r9AKpO3xff<FGvXz{%GGQLCW^MuFZxN}lE)Z?0OuMq2UyHvcF<a?y!fw-T#Dl|_re-`)6@#);l_lx!CzEFur`x@JG{l>8!eF$OIkA96UYEVAKm}HyGCx419&i+@QVi}Y2{^z$?YzjSxJX$W~i(nTx133kp0nR}&o{D@4JQZAxd>PDgCb$~xL(T&Gz_XFBfM<hikX2xo)4?_18OUki8Q?PH3*a(v35szcG9O$Bo{Y=}PX=cqCxJ7;6Oj|Z6TzuSCpZ<HgnSO11WrJX2Pc5XAjg5nfE`E!>;R8NJ`WxXPDG}F6T!(y7dRQ5hRgt`fzy#W;B;^nig5vQD!2e#iL3^*^nokE9^`DW2kb@GfNQYcUKHaBWEr>uT#76KmxA5MLU1A0+l|ZwXJTF5$W(AD*3XSh04HFb+(-x5f%R}B6Tyk-yBnDXPD6j)$SklMoQo^~=YoromEcPBu^7d;9O(sn(XVn8V-r~lF2%7;6yqXfE;tv*C_<KlO(ff|qg6|54y}4x^JvYbHJVmDtx>cF(;7nSSz7FoJCxQiS|e%2(HcQ(5Me)q2^mPMKVc7HLfCK4C?d9KTD@rXro|q^&(P{iD~4TrRaErwUQhdJ{r6_^$<!a(J^xaF4XA(FLU$uC1y5C<7;#e3WF>0?yF&68C)!F#'

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

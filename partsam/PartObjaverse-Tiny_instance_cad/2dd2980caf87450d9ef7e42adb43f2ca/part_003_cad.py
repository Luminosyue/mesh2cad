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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2dd2980caf87450d9ef7e42adb43f2ca/part_003.stl', 'relative_path': '2dd2980caf87450d9ef7e42adb43f2ca/part_003.stl', 'source_sha256': '175633b23e86997cfdd8c336a251e04c51693cba4e48df5bbcc846049c61d3a5', 'input_faces': 126, 'input_vertices': 84, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.20833322405815125, -0.472224622964859, 0.06944441795349121], [0.34722211956977844, -0.22777773439884186, 0.2638913094997406]]}
GEOMETRY_BASE85 = 'c$}q|OKep|7{{mY_XFq)XyG90h1wP<r4(A)1Jcq`S}rABbj7_XEyWlfEukUCaO1+njT<(snkKlR3nL+rV2oarm&!|_Aii>wMt8cf8`PLMbMEgu%ste^=xM(E|MS0dXa4hjb7xM&y&0KhD*3EZ)k8D)Be_bMC{$(Y<jDAm!^0yJ4M&chN>intZXUri{eyksp)_?;y%9P%GBG?J+UkVbMq5I4PH6P#_=)l8kpoA^4~`hUEBgAxh}I{@qQ^#bdreDIowIRmo%5#iU!Qz!A%1@5iw<LHD(k@~8e`QrFLYRXEIja)r{7+6(bgUJ(|ex&^v}z-9;uzZ<LMv9KQiqEdc5SyLwg+2BVUJ-{h!{rYT9Zhsk@Vtj~CRxbUZ!&UHx@ichF^CzrS1i$o46EjP**}*IBPS@Ym<5<0RMXww2zpby=_YaRT#7f6)`<LB>yfaQt>k{%Z#>*}8M+yyr)ay>{8wW6R&V@996EzT)}0kksSzXC9^G4L$N+e^M{2`PkMIJKvdIXdLJF=tFy6(PiFP=iM7A<4m5qx8V5b?)#^&rTBUB>s{NYBl^_*58k|0zuipH@h{^z0srF13HXm?4&6!}KbdFu++2$8l4t4fqEG+Q@}t-PZR#5I**1K~))Vawp6))laL>!vfx%htbNa_Clj{;aPXAc!+;v-5^V#2f`qipyDdU`-`PQ3v^}C<hx)bex;*B5ZA1M!g<LQC%6PKco?L0rHvo6u6N2?#(dGK}in@b&ipVUjSAD+{xqn`(<<4?(b7}Q<r>*q)6dnma-{q@T4n)*J=KRUlJU#IRab@%fr`ynvCzyAY1MGyLv{U6MOuLtrVzYEFdwB(t6sL20xa9_11>opzNSBiZoy2HLwJyZ8>J;J_<oSjS2WnVdg{xSBI8yugyNIunE%Og+cJePI(I_I{Mb6a%IPbKFzy4)j*dqi}<zT97;M>x-e{T1iAlJgur(SaVA*WsLh&ZpdWavzD#y(a5*0_&CjqRV|Dew^TXxi3VQeeU1K=yHE~{lh75CxeZ<{us;FC%TS2{dO`MwO&n(Xdc0ZUri1-{i|1#4UNtJ^W7wWi7BP|*?=|hGI%**cm=ouUI8x!SHer-i$Djy2)-DsgfE6yflJ|4@MStON$)PO8*V<!qOZXWxbaiM{08&ktvdR3Yz6z^W{r8Q+h8vIRUP|uYyiXXM&@q<yW#6~bn$r?pEcqsgS8q=hp)t&0~Wxy=-7kbJ$P-!lkv6$%!Y5&F@WCzyc*u1qZ419cv{cg>D0tvnpK|y>R_-CzF9{vzIySrg}IG~YA^@BNymPC?Z=bh^*VOqYbTx>nA><L1r@v!4@<!!c(aZkeD&aIGjkgcHDEEkMaOP@?Z(q4<}gnMm<eB}V=sR9;<cW+jfZ7m7Tnan8(-acYG!WZVFg$MH+!xRUwwFLVQ%B09L$4<@v#A12Up~)8|<-oI_-4wBRqq426YskMcZJ%#fxYc;Z=Ac?LzzuFQ8pOo`vVrHaKAM650m$S-hBbG3yteLpz6D2+yXSO}&KY(l*#>@jTiFyDXkb+u$yEn~oQCYy)3{Z-cjkFT>m69bgFF0e8VQa2LKETnpb0-vQRbcfemE46jq>`cdiy9m~Ph@NjQhdRfLl{R{o<iFrRh`ycAyH&d@S`<qjGEdR0#_hxxlT)O@{ZWdxHs{RIN{utT'

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

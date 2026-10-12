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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/053b8a4984e340ad94f3b563594ff09d/part_003.stl', 'relative_path': '053b8a4984e340ad94f3b563594ff09d/part_003.stl', 'source_sha256': '78bad717b54b47296a66c96a39179e48f2565e9ee0724ceed0cee9c6201aa3d5', 'input_faces': 162, 'input_vertices': 105, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10884962975978851, -0.07501836121082306, -0.13208730518817902], [0.06978008896112442, 0.15426020324230194, 0.13446612656116486]]}
GEOMETRY_BASE85 = 'c$}qJ3rrP96dgd(`UC%3t6ddA1pFYNpx{asKMxQQ6cu5g@DNi)1!HThc2oOF)r$4g7MtiI_(2kjpGK`BizX&bEYa2`H5L2RYSn10O+^h=yL0C(-QC)xX*ZdiyJzm4d*<#eZ$p~PuT?iDuKp}}Z+v=IJI46vz`C&&p5o;T^E@R(i<YkRVS&W+%fv0InJH<reb@@NDkR@il2;rOCxwhH7#$KWg%m6)US8}j%3V^N@8Nusdr^tU;7bbKOFhQ@;1R>4!=;g-;nHg9KVIC0{&C}pIs>Imr}vCAP))lto}+%b_88~o1yP3y*KFKH^G-g+XIGttXU%@49JS!`iWl;;hE{SN+0?mklj>^E<=y<=+i>hls~>Hq@S_gde#lx^G5vry^>tI<!K?5iftOHMMO}Gk?0%7#Nc+*E+8^Wd%*m@s2Wj1zKE$){!ikqM%4t7;<4b=$NcTtYR8gJvi8ZA2&PB2RR;9!<->Jk)Jue+4{q*_!ME_Qkjyxnm=sS3&-&WF>Sqky&ev!yO*;V*=@ap$2@-HWi5IR?8QC(%}apBX+XDt(TJ-hbOd~^!&>h8g!4-TH~yh{GP>sRg|AKyGZP3OtipPrZG;N=T%meX_B7YY9UbK<=b*GOLhuk1g0hVn<ml8(2|&g;*sNk^-*>&V+ar+sM;b4C8SQ$i=Z`ytZ*-Oej#8Ytg;+JC#~;~#ea4!*_z8eih|djX`QReoDR`3_zxnMmi*`{+p->0Ehc+iwg1L1&>e!;g3ky!z`t;nVe$^c9mYJ7MonlRe-2XtAi<WY2HuTa(>SOW&I8e)Osn;`}aoKs;NwpLq3$F!8*K?7TkihB!yz_lQ?c)Y|$lh1q$t|N2k)8%d{8oO3qe(^}%!KKqFL<NacfD^3yr#y#R?yhqxT^QWjza2w)Th<JbH598{{*I8`?tuxO#+amM}<A_)Bo=O!vNM8=TxSkN_T-*M2E$L5cT1WYKzm(pQqHfUaef0hvJum+5ZOqVVzHzzWH*KK(X=85@&!m;atC{Wgklwmxo%(U)kjTGsRpbwgsi(Z;b0YulK+2bXo=!UY^&29;uvz?F+k8XlXFU~sStrU@0$vyTcVnuE_t_?VR#XzN>D32FztNwb3)?NuGpo1rda*dqYO5OJy(`)Z9_QBN^;tUwk8|sF@G8zHYi-xjaNd;3M~IgnXoAOi^E!E)H?=w73))|E$9k)O-NBpwWp@w3-|0|q^{+d4(~p`HL%e>i;j~TP!JGQ*W`dnJ`{UqEeLcIhhW6Dj%-%N#Z}v?q-Auf`2l-}y9K4GDXxH`<&(4;=M|IySJ52cwUcKFges4`)u52JwL(b9fEW2*!<%bEC)SvFvBJb^IpAowC<KzRp)_%?r!p9p#y&m>_sUh}worO2^mDGu%|9)SIeQgb>xAsSK@MeGHm|DTF?No2=kLuvf{wTLD(LAdTe4qBUs*3ufg4fl{!dK8;>VxLU*MAv6ebXHI@^3lRAE{5HsGpHtM(dYcrT!@3z3MXBuj+q5)N$lXm*-G_G)KO)ctK5Fn(eFf-Anh@_iD=+A1@hSr3G%wCn+cSW#WrJNf$=_yHC=X$p8CE+QIO^t@q@Q-Wbuw=nNczxV<r=jL{W18gVaUj50<ba3tc6#)vdV05Aq|0OB6NXvBe7+a4H&xI5;%06Qb@g18f~BVxXG4AyfTYw;_?Bgb)w`Tk<zkz*X<c+5p3j>UZxG)Dtv#G{}&5;z8NXRPZ8j6~cO>v~z%_k!MRXmHF#%<IpEKaL9!b8j;-KNEAY@aBP@2U_O7GvSY;8*v;o6M%V$V}Q}Xc*K!d69Y7J`PxFP=a`R}`^v_AHs%(<!z}pVI3F?hI|uV~FqetF6kxspbF;ArH}>sD-dOm`gYP`_C?0j@L4#wiMbCwL9H$`Wo|EC5qk=fg7*jDn6?56p%7tDow9I`>LH#MHJs-ZZ(5EbD%tcNL@;FXMoMDU{_~3Cm?sE`N1*RgN4j=On&%pgO)NmnA!9Cwc8uZgpL&5XRfyW$ZXQ3D7yn?xW)R_crj;~qjjE5JF6A<${li{7?M8xTcQ-O(yr(^95;3UM;P%8yE9&s+_U6wo-_K}Kxr((~^SR0J>90wv!GDbK&avX}7`wGH*5ayELD*}2E&@z1ugm;c1h$lmHA~4jl|3vspgmxN668e{f^%+<<1YS4}u=omtHpk(JhawII4zbh@Ma@uXBw`<f;GJWC%RUBUuN;RVjzAm?9E5lR)=UCMAm)BwhDVP55OZIBG2a(+12ESQ-Z@H$d7VD+$FVnJ?(G$L;rJ@zVTcC-`ydWNop4LNaO}B1yqmf_=9j-QS_9i5_Ay2qW3&RcMeN7;2Lofi{F%CZe7pJm)4#g@x>PP^`^T4arTufny7Ci4tL5V)&DENFG>ZGOWd`2nzq0I466O`L'

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

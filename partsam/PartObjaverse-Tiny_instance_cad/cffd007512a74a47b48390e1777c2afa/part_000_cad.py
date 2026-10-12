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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cffd007512a74a47b48390e1777c2afa/part_000.stl', 'relative_path': 'cffd007512a74a47b48390e1777c2afa/part_000.stl', 'source_sha256': '27dfcbe1f1fea4e32405ce1d339d5ebc54f18bc84356c2244fce7395af623f49', 'input_faces': 192, 'input_vertices': 133, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.38660216331481934, -0.4603525698184967, -0.4194178879261017], [0.3865852355957031, 0.13922730088233948, 0.4182518720626831]]}
GEOMETRY_BASE85 = 'c$}q}c}!GS6viK-pn`&evZ);wS!6(9M1-m{E`W&O2!f!<J_xc3NL{dwqD>Q1n~0S(^^Y;Njn!IPHP)D_18%L+x?n98)JdbUNs}&#+S)d@_rCkR=iJL{)3h%+`F``gJLjCc%rFmgrt45&iCw``abJJfubz@b!&CB=+APhjH5HbY*oLO{E|RzG(@W9L?7S><p^MZeZH%b2v{W=lr061MR?Ude>msTen_HX98cG_QD=pMdE30d<5Wl6mtjR)NN5&frdYvIkuiK>ikJm`rgWs9HvqbE%Pwhsc*1GyTMh(Bz^&RFLj>^92j~IS@?tbPQZg$J#dyg=`eHZ6j-#yR#ok7~;?-hSV{nC?5?^1QR#BjbXaEk2P{X;olxB2;i)_BL20om7`PiMYkCCjtA?JnngXK0Tfm#&>ZAXU2`-CXVdC!4hE9(Q5+@89C<UV3&*&fED!nAeZ8Z;jXSbss-u{*4U2uG>A9r=ymyoAib3J3PDjx`n4?U%Ggoulw5jY<!&?U-yG9Ha>qJpXXR7tLqcP_j79-%X1}@@27u@?3?^Q<Lf?Zmwnx}I@z~ZH){G0m%Yp%(ZK2+TgUeU-v-})pojTERm{J9cYvFhzJ&EN!^qbae6?<RF4p-CzW<zTwm#wMd_RJ(_Oomeo7WK!zAk(TzFN01ldWg_pM2e|$;^Mxi?1vAYTX@)tgbPT-<RF->|8DUykFDrF!6p@9P2af0KcB_t(V<T(ATyLY0Q6nDqDZoe7^rL{h8nC$NS%UvHnvp_iOoTKSTAruhbnD&HM+WS)Xp_`TS4Z+5Yxb^ZkcB?v=;i?&H@}@YVH<`$6{Y?ZJGW^arwUJN1CyU%`KIu9z<wul8%@QRXWJh46l_t2|%pgka{I9n3%2&d+yu56fQ_&HG*5vTu5Q2R~oISLb`^B-f9+{)&%&)b;=9Q|6~!<M;8*$E=^WPJVp^UtJ%^KDKVT2H|_2_tids>EioQ&Y|E-%J^q{_<1S$1z*ko`&+W_NW8(17kqWR$D1tA!X$pag0IduWIMmV%HLnXSN~p5-o~Gk+6GNu%^%*u*3EFUpX*2P)$#rhZ_4N4yQf#>{2$)1JNu4D%(ot&bDi_oG|9dxq@df`x5Brbetyl_moA2%lT{dRzrg%bVZ3dztw+9pi0{V)zf|bQ^i4pIR(=V-m|r?!IwI!}7WzNVe4Q}fIuL$XR-qrMpZO-CA8V}dA+7vU4D-eO(sILI`8<f@i<mDB8n3s}*Cw%_70lNu{X9IXy<hML?HBw(`vrf{e!(BK{z@Kk{S{waf2ALB{S{waPbH7Io{BH7r{W9iX>FUOdHxk&JpYO>uD|Mw>wkZ1FI9WiCHZq_JA3=iSq<MBeo*$U=XNr`Qa|84-a0X+Pp%iwes4?Lx3E0Zc4_+_`*}Za5A(nOg!#X*-~YNZUo-#uY1y~ypZ=q7iXeTOxu>SXKb?4P9YI<oF@iibRh2nCGEtLWifTVH)lB<$k4(u4|M!t8f*w&4QxKFVlXwX_5gG!X2%Z2922X;9L4(0z;3#M~n5rI}OkyU9R0QRD2+Ffa7@!HzncxI)JTw_hbvig690!dB$ALqkI&dgB2<it80*{A|1&;@hk?3PG(^1f|;8Ebw2+BTCKd=ut0ICBAfFq%?;7D*HbUHW@Y=kC*jbIZr6>I`$BPcI|&I2z3FGNtD51j>`51#F`XR{HMr;(Tnje#1#F<?D30jvi{LF2*k*uN+Q<uGWd^y2JMo&*g7PXhZx$AkUB<Dg@}<G|idd+d#%>><$)I@94$Pw;TCJ9HG-9qa}j4R!;ML{RpE`hdN_zR&=$FE|hy2@V8DLleQ#;3TLKoCKZ&HG$`V7eKSYOGu=XNW+*kr#zHXpy}Wg@XH9wGZ2*LLYIK&f-^{DlE@;FE3tE!BeAoY4P6S&0q0=sQUv8ZXcn02VsIXK88ic&fgYA2D4U^aU}gSh=mM}AoDa<gXQQWlXdXBZHS+P^e7qh)!bM`&P!g^rhLL!c#3mB$B({?1AhC_a77|txn@Kc~Xe3btT?wwkz2(p%a6Rs=fG!8Gz<cYVjo`H;T1l*eR)J~M;6Bw?z-{1aXbrd(_o|@P;58(gNR&ZK!89sxpK1%Z8C(vn05{=YDYP71g1N86TnjPRLflj4UV<@|m|GQkU+vUuHSSl#r(BF)OOcb-D1a7$3&6$D5^yoN3~F(jy9INzU@jG?Nqee=t^(JBEznA^1+1(^Ick<W^<Iy?u7fs!*JA%#p>1F~$Mxv91Z+VMR5wD`gK2EQ{SBByE!KqAUxz5h{bKaC0lFHz4mk^;g<yIn=s9SDHiONXE<=1>|L$MjFD|S6!E^oxxcE-~XP@&sr;{&u^+%vNa~S=OCm-e^a#KIkzckWc7>g0O'

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

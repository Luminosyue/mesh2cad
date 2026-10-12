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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f0742330720b49e59740835a12380219/part_003.stl', 'relative_path': 'f0742330720b49e59740835a12380219/part_003.stl', 'source_sha256': 'f32f0cb5d502de52a0bae7a20b2b8207a5dea547fb96f2bfbc8becab3b27fa97', 'input_faces': 408, 'input_vertices': 236, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1310713291168213, -0.09327638149261475, 0.18520870804786682], [0.19701388478279114, -0.023461800068616867, 0.44138699769973755]]}
GEOMETRY_BASE85 = 'c$}r033L=i8poSM1OZVA=W-091c4v|a;Y%Lp%{=LvVaIoghT=oAc4ruAfg<C$bAS5gb?ogl&ew6K_ViT$Pou4A|kHGuDk25Z?~)K*PX6n_Pu?(dGCAwU;b0`^;ch2*L3D3F1AF;C`10#F*2?Oi-js1hKO=Tl#!N@GCFBcLTcmWk>iRP_u0Pqadg4+y}HHqEoP({6QTzvqz+1nZsUu7GO<;3BVTmlh?LPO@yP>6qzq0Fe&_htQWGpcbx8ck1nc+uO`El7<ZJdwBi|(7|M+u{sNv@<^Oz{9=EeO&{oC7JY3K3%g`1_{WBg^WZ)}_*{a^N65`M7wK<WP)w*BD#vRAx*;N&seH$NJ8+3TCDR>|@Gzg6-Cqc`reU$1+glE-K|%l3^Xla)MyQb}@r?)P>cf9$;x$2-3HuQhvZf9h1}&&@ez|6aI4j?X%y`mt&IWL*suKeS`FoyTA0g5sN1=i0tGHpcdSEz*ug>W|~={dau5KaQ{W$MJpLL$dyy8_IRff>Cn(k|@R3`{veJ^MIUJwOeW)t#58UTV_iCW)<5H6x2Nush_T|_0#e7emcJ1&+z$A4@X*G$Jgr&yxRD1r2ad;zCRsb@4w^g{de<g^|<-<{W)X6p-AiQ`1*b4`1*Yp`mTPKeIJx*w!?n??8uW|KTvM<cH93kE!XS&@%<~3^1Qy$Z}?Wb&UI^Zyng5<=?A}gD&On-8rRrl=c!pq8E?i&KRi5786Q~Fe7&8gUtzY_4~Os{{aqO!jOw;FQhq<ao<Edntcp~>fgjN74-Z?o%+B*CwLc+zy+7uFQcJyk4u88s=3h{5TSPy5l-)OD#Ex9AZ)Qo~U!zH$*Z21^H{1U8^2&GvKb&z!86SSE#YTG{C5Ljne#r4_`16(g^xwQNUKwvV>#`?786Te5GCg8`$Jg_Jw;>d<etf-t^Vc6%+J3UypCG>8pHPbr-}m-8Snz?|hd(~JK9X<VIF(_~ckfFPec$=%YM#`z4COwGIug+j2an4-C!AFB>%NoUD4i|quTov9)7Lgv-WQFNl>EU>pU8gpjoBE{zx2xnyFXt<NA!(d2NXZ_c%1ErZ{N)I`ayjE%3qc7!5Mur?Rk|vu8a@h2j8llr(Bo)V`S`7#{2Mn-^3{6!!3@e>!SJYy5Jl2DrH2fC;YJV^?Jf%Yp#nlUlU)Sum9Y*^oae$*ZXPQd?MYuF6LurrGK`Zy1w^Zk$s!gTUp;gzb|Dy(>E)9(0!*5q3l9g&)k2h`=tM$<$C3JQupnGU*-7rtCakX@56WUo4J3JdAj_p<ni~cXrI&OkVQ%!-FNahzCX}joo{lK?fXXERD5GfbK4JGy{-DoAGiJRxn;_Ab>F$J?{v$E*EO2<%Z}7H|Fi+wk@~OuPX55T`0PmQ=<o5C^k0rv);)A_w!E(Sx!Qltck+kF&zINTKTSPnVh+mr?oLwj2TmW8pP!s3?*7qyH~*Y$+jq_-ci*P{DDyAOQu7b}P5Of;sQESDJ>NQ%ke|0X4b}aBy-ZG|z8Mp$+rEF^JL>vszPrBnH<W&bEG3U`(xdWosY7h0GOv-XrC-s=^yb%nci&FwDE-1cYW<aZ*}k#3**axi+Q!>{@b;K>-u$}no@3LJW&Jx3D|w81W8`(szbf?yng``|-`k?pulsI)>d%sXe7xF+x0lNPuU(^@SH23Xq~G?ZbZ>s$cl*;xe*XI}x0KK4NmCWyJU4QWoxkd2#Sbr8vP<~E+6{8Neh5E2Y+t_D4@NbYe*a)jB;OwsP{#Y~kFlSNOl`b@@6*Pcb+*~hr2(y;0KTc!6UzLD+z$svDDw&}AD*H3i_>MEM!W4kgnB%X>-GKkX6sXVUO!yUuzi1*&dPWb-)z5J8E<a*K|Z(N+LIm04_&H}qtt^R%=<WBsR!Q(HT=Zuhgx3Ej8sn$U$4hVkmo>9o3F|F5MsW8o$KU$J9kp{f1uGGndjKh4T`_?fV}R$${UpZulerh<IO|1@7wmFdLIqWlk+X!O1W<6^ry1UzZWX|U-#Yfv(8zW=cjj-`^e~XKH|DNzP|2`udln~>+A0N+Pdq$v+iy^+Pb^-XzT9y`no&5zV42%ue)21w(kCo7bBk=_;;Ke_;;Ke_;;Ke_;;Ken(v+)PCfd$fq%!j;nb<08~Ase8%~}2x#9TQxe=^%Rr==-s^|8ZujPI&D6i~)-FNqA=^M)Dj{AHv?|WJA`2NcM6&msvIo}6TGb8$Z-nsXM=DVLe^?sM@)%&(`-C#}$dtW%8BX0h}l5)RjpKH4B-q-m4Pk&aQuez6!&-MSDr#>%*%E>%0bXGsdf39Hr=FAhyyma6FydGCc`svryb-7+meoxS+y!u>$AH;W`t9#Uve(V(GIY;;1=cx2La=u5OQ=YqY-|hd=2W35nRx15B^JC=S)7PSv`ole&$$6DZQJ-VYma?7(-HZAbr+m9z`nSZTp^Da}tSDnd8Hw@UueK}7VU9-rYCEa<fA!UN^CqqS-><e$ST!uQ;t;wXJ|J3YMHadY&Vmo4nebsaA6*US!ylqs;p0|pvEmfE20jIw=w|q!73-|{7+nH?3?D$#VUzcsL|4Km;Unk<_z0YXu7Gpk56}z`Z=eUu;7oKSoC&W+H^Zypt>_wfE4&un0<VR)p{w9+a0uN9hu}@<`|u`sIl3NR4zEL(!t3BAXa>9lPDfY3E9ix@23ejSX3=Azhdn(%%$f+z_pDJqYbf+X*o04^pBhDbM(}a;BltL+hkgR*!AH?!@KHDy&4zQ~L+C;H5PSmt7(M}ifF6Jk&<nwRt>|q<f3z3eA0CMIga^X$Xb(6Zeg%C2egzJoFTw$M0QyIG0Q@o`xDO%tDMIiQ=!@_ZaBK7hxHa4g?E$xf+n_z+Ht>^ZFZfBgE!rDy3;WT&upfRJ?GHZ<cSHxm9pTPsJlq+627Lv72JVCg;7)J{bO77|ZjZhUw};!Iec(Ryx*Z|-Q9^JG`UD&UH$+>*4dF-7R`4TmeY6c+A8vp?2{(Wnp>5$taAVXDH-?*_Ps2^%rf5gFDcl_G3^#{cpwGZ9;Ff47xF!5J+5vtXZicppo57Ev?cjFwTJUx&7F+QyIv0Kyewz^dmKATJ@1S$xci@HSVt5g{mk_+)ihbx}bRoQl*S4dJ;j30$x8foihA+Zr(a+(t@E+oG&oza9fqo8u0e_2z;cwyZ(Ce_M=SwTT=J&4|`!&Av-Y>~5^n&MF7pP@F?DS?4y%ajf)7v@p{!Mr~>oT3SnvU<R-5mNhhg{o<Mf774*L3=`m!9pV9;b&F=<x;Sa1p%<JM;gB5PZvu8|ZcPJNP>9y+H^r;JpRpE5H|g+KMw)oJTLi=iw`8A$$ccAPPOT2)&6G!Z+b-=w<jCd=5PW@3LYCzwf|1L!9RIUGQ!zcA}r5r{M`!jJIM6IvJh<Peb2;r@^z)S@3Ll0XiRE0PiN|dukUt51kLsgJ+<#;2CfbeFF}{6Vb`=M0hMZ9`0wwAS)92UHGHXG<Y;T5>0_e!Xwb(@CbMqIusrTzltWpiPRwYc`Le8S9g5D&sp&-uRqIcf@68DD>YA`Mxn36X>baf3a7xs(PVfyJQN)Q4}}xa!Ehqn4~>KS!Ox>z;jYx|)ZfjDF3hV7bL)cNo#;j{guVn1f?q`w;8)>cXp*P@Nvx01*F5X>8tW-^lxKZMvHn8G7)AR*@K|&lJQkjaPBM!2p5P!l)hODlf@h#JjiS9RcpmzmQFJc|7Waxc2QC@%oDlkzQFLwyzC{Rj&M=`@(65Z5b4l=d^pa6@jtM?Z2>uMc1`9n0e+KVFcfdQS**R~7E<oQiip~VVv(cGG(HSCm8amY|I&%b1K_?kSXO!Rx=s0)+{5m=YejQFlN5QFZGWr^v3=ct*;34o}GyxtA$DuF5ad20(8!R*yE^kFyE5v`|RkPv`R#ZeQ!<88$_+Bf-|I1ZHtH4#^8ie3l<f%oDTKJWTDqOz`xym!X8e^-It0r0tuEiL~ug>*_MtSOqqF$lp;L=vyZHO;!WZcc%gqDKK!WGd6;EHfH^g*~9TobJe*MzI155d*pD6|qB1(!oh!=<U!;k&3;Xi4~PxD;9f7WLHT`a*qhUHBoi4*U>Y3B4b#1eZqdg72lSd(blQJ#cxnEL_}*V$@g?E`b_w3Ah4!A6x;hjXn(5hJ9!~*az1^qv1NRm`7Y}vEorB{?os%7X1Y60=@sps=rhHTG0E>0xOsMC1G6bU1D9VMijSi`h()HFXP`8ukmU'

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

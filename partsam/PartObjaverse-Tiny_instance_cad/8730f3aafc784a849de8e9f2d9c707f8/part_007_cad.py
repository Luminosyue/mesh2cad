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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8730f3aafc784a849de8e9f2d9c707f8/part_007.stl', 'relative_path': '8730f3aafc784a849de8e9f2d9c707f8/part_007.stl', 'source_sha256': '47a20b6468b8eadeaf7143587d5422e05b3312f7916e2405024066102d9e55ee', 'input_faces': 348, 'input_vertices': 220, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.13429440557956696, 0.12267464399337769, 0.12154123932123184], [0.1436222344636917, 0.254466712474823, 0.20813046395778656]]}
GEOMETRY_BASE85 = 'c$}r02~-qE8pj*)LNH=PL4w*|Ac{meB7(w%C?I&Cs3=Aq6jb63s6j>A+o<4uA~+tX!DBf@QLaYBs8MlaPzlL88aEqF;^x@Rnncag-}lGNl<a%^cIUl%zu){VYO1QctGnwN9%k9tPU25z>GnU4K9t)^l2&XaJ85BTd}7?x*aY`E^O7tiTgtUhJ+}=XGc0_(g|tvw;t~^^Fg4!AS9TdN&Bw(}c9}LeJ~2Le&g8lAF|k@66g?{;wk}VY5j`)q?t2dpk3Md)r>mQsEdP(67Ft&}^(il_qw-m!>j7GyDt{~2sF!+iKCsDE?Yq*e-35(?eXf*CedU|lcQrGM>dQ-;aDIQpN0g6sr26`@2P);K{VM5u^siLka4v^(rN`$L)V`d@zuRIh=k`IAOB)w+``02lca7tIgvW6GPfE%t|KX`h^^-<$?lYS6wLPexQisjl-t&Q!Oa6^%yvoHNDVOhgl$nip*)z)3(BDd_{+Tcum$K&x_ct(ya^;XKjmtRf66J>9yt%$-G1p7jP1Fyy;e0|@?ngu-Q8)cX3FV86cwQdqxIahzIlr@l#-(%lmd35N4=vVm-DP(kmy;#^zOv$%BI?h9CNwU?lQ_zyDb<uq7Y9-QrE{yza^*l%8n3}=E$3FJIghlU@AAa3N<N<RIS*ON^WysKBK_{sV9xJ<!N+^Dk#c!e3(ijuqj4$7)l=)wQy$>K<EmUpxo*hwLh5IhCyh(jcF-m2kN+Od<C@dBba|I3SAUPAT(R<_ap{d;QZ7H3#Pyprr*Y}6zoy(!(}weP`Sg1RzrB>}TRlBX`M&R|Kk|jq+<tNm=aG$QT*jG0Dc1#7aGvDO$FIzf^TyjLS3*<y{5;Ty+ZnKh>t{bKqk8vh`Fy!iSU|^dg%6EaZtBa&XG0|A$~7xKKl5);ZY=4-`3$S8d>p0Alv^85Q{JsN|9#pso{x9WaK5gR#-&V2q+GXkFXd7!&%0rDF69PkDd#mish?`KCFSzynVb(<O~=tVcQ)5A^W^rIRPb@H_2%p2pY~io_<O3a-W<dI4{65rOPr{_War8KX+J5C=HWL#ng?V1N1WenOS#g=n&+W7gT`xkT%1eoUu(hFY1L)Ql@9ADSBf^%c-3Zs=J_Hgo|hz*a@9MU+ex2J<CVQ@dEN2|;rz)Eo*&2AJkO<G+)l0+jY~J7FZXBnUvj8^$K||EHL|5#Kk+i<%Bpm(@5tlQ7acrFxwDSPo1R4Vb(Zd&Z?~cG8q0jIQ2VxrPMD5Y?>vTbDP}9@UF^8u7b3WRRTSmQ4~e`Uj()=PFwULp&mKtQ(w}cm^^M0naK3y2&4c02ChpJYRmZ8FJ5709Bda-&3gCQaAdf5V6puIFf%A7F__&9xr(9~4bwtb6{qN9t_0Rvx^*axxTzT4(uj`x>JTB{1S*GKaci*C1uA0qxr>#6Lrv;QNT_$Fk9$z`Xl5*YOf;e{=&g)CYa-JXGx40dLOEg}+r31I0)}8aGJ$bz<h~j+M7l$dYp3nJpPySuQHOdvgjXYl4*4+Q}dzn;!dJtdNsBhf7g!6Y>@%bG5oO1nY`%KgEsy{pPxU*w3sQroMye>Wal-t=DMY*(b3jeNJO1bLUpYsuC`M4PNn&rw*OZd1a-#5>9xbVE4vgh+_`Oo_(H#pMo>c3oc#Wa_0ea^p|vXI9+Ghz$nug&HA?(rAg&(<DWO#7oB^#!++-h^`HVlB0AD6-}2_|%EbRKMJxuivHxJkM@Ulq+*<sU7K1KL73*`%RQD4dMI6-Why+4}O|vI?u*hFKS=+{gyP-c~-8Z5{&~#q?yix@-T(}eS;0x|7ruRSMrUsd_L4%Nu@k8neTrK9J&3T*H@Ze?^4enc^=lyOQHG?-sAHpv>nfLwaqfBKlp2&=WX4&KZ<)Y)%PC7$35_49#{37Nt9pD=I4YbwcP&99n(zbUv4Gw{h=l$hR@sYRMX!zK5^!JLln>dj`Mt6MwJ~XHOcj>kD29)&)@mF%jD;ym-YK6@VNSYV_tuV72g-SspjqXkLPvuQE#($lpEdnzOr(cdHXnC#>R)u>zCQ`x?vw?maFbVcwL>J%;(A3ZZQE3j91=pn{#1)q>kTC3us_IRrd)=0S(N*^x632fCi42ns2=<pn>BnJxEUpXyANMZ$DTW(7^el54n;W(7^d7`*cYQXz2VrIh=Cwd^YYo%JqfwUqAFQ=fd@(zHr+_^@Qt7Z{f0;a^ZT^uRKe+c>NmY+is!y!u4*v+Lv;1eUQ3EY%!hxm+Oho&-<tyVO=srT4YdtVO`RF<C9@J5B2Mt(tJ>c>F?IBllA#4>tu8+=fXN%pNs3Tae#fM={(o3=W6VlOw)O;U;lOUA9F6;FLZ?u4)ghGe&5mk(ld*4;XY-|^5a~%uc;M5l)rKxOr65Hc;EC*;C6)jtnsUrS*GKvzc1^ahaI7Ig!{OXluh|7_x;L2$LZh2=ZD~G&V}a<$-e6eqVRlTsPN=mc%G4b^^}XxKXTPBt}i?<NlT8MFdbL@^Obt9_ep9;cpg)nk8v(MzsbYz=TJMsbD*5qFPG{I&yA`aLisDtnUAM(E<BgYx7Kqz!t?FRTzI~f4Q07z*E^n*^{Ebd^j&za*5A-mE<T5=*^Z~F9pQQ2U^Rzx;l03Eu#9uzJwgr6;9Pj`kX}DWx%i%<lt18Hc&||sx)%_|_n`M9ITzlW)Z#+Q#rG`TkK4}D-wW?$hI2b97vJNgr<Gh^c<+;D)o?DnC(4z-axT1AN}Jjh5{36r>E<NPh4)rn!7R$f_gwX-bgnPF7aLyu&bja&Eytvur*?$*Zl!<ABBJn~uA3Ojx$s`Ew@Kt&*auKc&u}j68yM~HQZDX4)aT;<gWl&Ea$z5%d1x{9OW5}?Zuc*t@4`Nb!O5bOa$#S^;A_LVun(g?^5$IFw=w=Jk8*LJN0wf2ePLh7u-%)^CvhK1$<t9T?mMa9jph2{KGiyvb75agbso>xiLei*i(SXLuy3Zf%i~<wXOkTta=XI5oP_mP+{aV4xpFS<`%Q2wHybbZ3Drk^IT!X74R1~1_kSE;d4-E=mM>~Y?HeLGlm&#F?XLdhrr6xHt-Dg{ij`z1O^Y_!TGc}BQ_qICR^z<>tF2W}FQ5N+Yjs^+A6C?r)hL=TLD75>m<(S8p93z1Yn%($I0ddT8a@X;9efu)9X=IB^YLILd^|h?Mf0KHF!)e-AovbE5bgu^hx@?Y!8hUV@UCEQcvpBA6wNz<J>i|;9Z)py0lo$A0rvs};9l^7;1KvgcnCNe9s(Z&PJxes>%qBjJ$xRD=F7mP@MZ81zzy&Z;5)$W@E!2|U<Q0Y{1})8KL*bQ{{+v47lY^F#qf(Lnpc2l;T7-;D4LgpXW-@VLhuB<5PlLo1V0Hs4DN*=hNpvD;OX$K;ClF0cq+IWo(f+BE`hIsF9sLE7sD5VbKnc%vr#mk0Zxa{fX9GS;W6-W;CT2r_$V*}J_;TN4uyxo-v$HWZ^Qe6KJb2UH_#pK2JZ}Zg?ENKfL-7YaC;QZ+ku_n?cjD`2e=))EsEwH!5;9Aa2L=E?gIA!2f{tz1HcgY0C*5M1|9?tN6~yTsE1F6&j;thH7<kCho^uaz*FF9D4OpAcffbS4d8yb0sbL)4E`ZJ56p$<!Hd9RcoDo3ya=y^-$2p)I#>a}4!;IofM0`ujH3BfupE9Beg#Ey6)c3S@N?iv_&InEco?1oKMJP9kHRy-t?*3vPB0a|6TT5#1K$W=1ullKf+v9s;YsiX;B5E;_$(C7<G>m4ICv}=1CNDAf#cv&@R8ss_(*s#7zPi9`-5-8{o$TqKe#8{6?B8U!ey{CT!yy?9pLTZwkVpn0`1|g;IE-*-V$sFZwa>n?cg?WYp^Zc8r}j$^EO~dcpJDA=mK|wJA)o@XLw(50K6~U4-A6)!3Trk@WJpAD4I_KC&MSf<H7lGjVbVWxB{lZ75F9;&3A*l;Je`mKm+^$JRAHFo(<0j^WgdL60itf0>1=S!Y{$Az#H%?cnyl?cfsrMyYSoKHTZ3KHTW^S8vZGY=C{DB@LTXtz$@@i;D1KZ{4%J*FT=~gbMP{F0hj|XfS&@7!cW1EfSK?k@O|J;_&)eHa3g#hd@Z;Nz81a`OoFe3zmKAMBDesa2%ibgf@_R}&xF4R#=_r&Peajs0vH9K03QpEgpY-Xg2C`mxDND(>)_s?C)^v}3v`9|f_DRDcsIBs*dFc(Zw=bQTf>{9Xx<EL1#bp#3cdz!3U7j<d1J68yfNGow1Hc~EkJ9y1zZAKNPm1ZZ-k<`71#!D1%Dky^EW^z_#5!<pfg-!UwC(TAJ7lp2kr|FhWo+?fg|99;KRX5@Zs=@U_5*xJOM@X<)8vz4&MxJf^UZJ0e8dqzz>24;0NKy!EE?(_-Qa7uCWAu8eR%sf|tTSLecytSOvcczXR65@4#zOH2<uwgojx)va|e8|JCe|kD{G8X8-X_{7ds~6w|+)RM*zaO_lJlCfa#jcak-tn^l~4W=Q`ALMl0t'

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

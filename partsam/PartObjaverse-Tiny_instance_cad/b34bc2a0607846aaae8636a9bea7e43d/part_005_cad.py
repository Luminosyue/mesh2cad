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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b34bc2a0607846aaae8636a9bea7e43d/part_005.stl', 'relative_path': 'b34bc2a0607846aaae8636a9bea7e43d/part_005.stl', 'source_sha256': 'bb32373121cb466037782b1e516350f49826fae690c1db1bc736d1772348c994', 'input_faces': 240, 'input_vertices': 235, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.020605290308594704, -0.22168731689453125, -0.10590346157550812], [0.11897660791873932, -0.21548670530319214, 0.144709974527359]]}
GEOMETRY_BASE85 = 'c$}r02~-y48pj7kuVtZ@H<#3gRB$0R6*Dy$TR^WH*IY6+J`=<ZM8GYzMsv$u5LduKL3RY$7je`wO<YRN60<Qg&F<+~-dky2@8x;tKQs?#?m73|`<?Tg|L^<re(yZ<KJWX^atIpM(7mN(emter@_-|2o{}Vr$E23h{LrYF8B;@}dqhMoa+8`1pFWnxjT}27Xo8zGUs~)P5*j@<%6ow9J!o2gZy(uv+MKAEs3{S_bD}~*$q$$^J36%1kDfjyGPL%4m)?DRedIn}edML`|M+>dHU(`%oA|?&%M<aZNL>flm5}NuTWqxZQd(rGlP?clQcP+ry0eV6Z#|~W$=AotEOGLciL;7G)#O28!dG0?qJ8+Ah0I5Lb<GRqPQGz#LaAf>wV@(Ut!?WW{<i+rcZQZZ`I0)cfcaLQOWRdA`SO5Zk-uwP*m8S6R{r&UEw=wb=GQx~`o48u#;@nsv*U(G<_kY<%|>=!?Z*@_zkXfn`Bq)jH*Uw0ueQK(?|UAi@5&*MIJ>WXR$N8jWzRm$cWw95Mf>>4%vT!zBz*baGVaf*I6~jG;aZ$Me<d(IPiRE8+1?+1&B~*qpZ6oS+S|*sR*Ug8ejgLh&KL8xzHiN2SGm^?@^$p@x;!z(-@(_G&(3u6)$aoe?7o$!`sArXC*QacT*>;e#-T?@nv<`79+Ttf$NS|u`L4r9^VxCX>o1KecJj5b^Cgb$w~Q}y^ebx0MSX)N^YcA(U(6Hj;s(~<D2_iYzR&uQwbw`OFz3Vib352P9Cqx07!SAKSwGT;q2@eU)qSVkm*@8u^T9}t-O2jtTPD_pmJ+(#?pym?eP1eBFV?ToeMTayue*`z@8rL6E8WT0q<gt`zixa+w<vM)^(FD8tRL&V@-FRl^7ZUHSx&y1Ddju*7gii($F=;2O$wcSt;>cYM}L2tawlIumsla@!}Tn7Uh*e?=DxA^7He<#T^0L=aiwvRef(9aPp;@s>7K;up5SlJli$Lbua0Xb=7V}5kNNWXuZ1stTFLr1mjBJ%PfiTfgpYm0b-h6B&x%)t#@Y`~7yE;Bc5Je}zS64K#rOKYwQpz}cPHEX*9-S%i@!HLnasxF+-b2cj0Ja+?c?UkD%0(L-S`aeAo7>KZME0lkJ4*{IS$1~_OkihyhiN*dc%SH?D?qIJ`wX=``6ul_WZ5+R_9y$Nomp^@%xf~DXgCvPh^SnShYOGeq5#RK2b;4-Ha4gM=8XtW8@{~E2mx*`MXjAQ`z|rYGCGXlrvxd=MQGR`p55Q`G;&v@OSX7ddZj0>}UCVt;`VlC$&nm`_j2ba)dvBS{hrYV?0Fus{1bHD_w4y=M{UJ^<zx$Dy~Ob)qr$%+(Zxaer9gJ4Es1so?Fd*t)6d<zx=Nm87$A5zo&`g=VoNEahn=0>Z06zCX>y#(R0oDroNuZ@@X?#?32ot39P+xEY7@+?=H_|^)2fu>Z0zwkYyidy?Wg?f4gs;7wTekXpqg;#io$`BCn79vRQo}o)>k|BfezqrGQ0wcE2vq2OpXDAztlrSY717B7be+fE>2oF9w-)shO9{<_X5X&bRts_`bOR&;k>4*|-hAlp_9q@mwy;KlX)m@%Kr=2Uz|$6meaXZ^s_6=dY)>HS-@=&f3fKqRsod{2JEYHNQsGQChn$&z`5=aq(s+UqfB=f?auRp11|>6ZuEwGhgbFB<dok{>*&EZ<AOTdYkt7cHgyStEh`n?457VQ$7`L?*Ds6FkkJ}Pvq~~dpV!wuiaSd<Xht}54n}k#<RFMSsdr#?<^nbh+C@A1mA<K{r0cKx=@=;X1?-vgs6)&&%91r^GAz0D(=&i?{g2@^Ve=~7WI<+yBDxLf4i{4$*-%+72g6jPiA^)LL0qS!1A0tUDQQw^$z#%bk7vW`89#}vop`EOYdt1_Wb1ztwjFn0gpm9{_<_}KCNbPAzP<=)+}}Mt-2ULEGuO5VN~x#F&<ks6|(XC?To04%i|F9rO`{px{$uR!u`wtFza&Xr6M-ZKb|G-E2R5#n6F)aRphTPs4imbcVyUH=GUu>OFdh}#;vr)F7fxBUlg%*y{@;Yi>r}T%+5FKlvo$~g?7x>Tl6>U(mSEpo~IG1oA*nH&oW<ao@CCe%}<xGad`HpZ9<bhOYG;REHXBWdUo!}+FRpq_;xK}bxhu~Qv5xjC+kPr_aI8>cwg>It;d@69mM;=d{7>|T*Ah|y{);vj!oh|>Z>jFDP?s`yeXa|l%K~jU(3@)eRZGNrEL7?-P<Y7YsA7*HV><B#fjhDU0KSGi}hmpb@>m;TPJ?EBaZt&wSQ0e`3bBa{e#1zzOM2;rEGix!Y7LUgLAl#`KFGjDr0p&>0y4qeWHxziTz5|u9Vr&SJ%z`O6zpB%)Wlr>T6>DxUMy=u(y|+H4^hv+0>5tinX7ocV@mdp7LF#!k)i1p8AfF6|7#r_?pinWp7qEji)p|l(ko8yNf(^HHNpxIIDph>-A%fr^_Rq<ztPfeDMhLRjglQcMWgf$=p|s?|xzZTh}`+r+FniF789rm~NG<AKV`*17Bsnbw4k?JE_uMN2C7-qK;C7w^)1Y`Q13NfE`!GdjoCk64sA&(#_mIH*MkV@w~6+C05$&XzdT`<!s&_?*Zfor7R!)eq(Xna;-VU+FSdHEBSb(y^ivg)8=*M*k_e&9uD3n_DA{Kt9(4M&&bma){n9OE%Q0|@gG?~t~H&-{MIWT@_w){8BfWFnE$Yq*q78F{ke~QNj@IT{JQIu=Q8G7_YcxNjrU{S?~OUieCvK&@%e`Nb<g9g8&<LTiT49?a7XUr{eaf*l`57ep5I-uA<Vbl8>qX&n6F&)6ZbdrzM0IIy1AL}owCBK?BlGxd(6Dv7erRs>!O}tDXv3`GLQL6mm#J8LF_H|wv#=Z=uK-6RU3~;Ev0EwY_G7%q>rV}udrwI{qJ63_wDunzQPWw&0$n+1VRJA&qI4c1Hh!Of_s8{Ac&uXz5*tF8T=f$6N1<WIv7kk0PF+qjv(#^eGyEmfV+XaB8WRe{lTPu;Ev#D5yV}fFM&z>gS&ve5yW25L15Asz+PZa1aW6*Kd=lP2<-<Z9RVH)9*!U$2OSG0eG5DeJQ+b83Y`WfjR1#&!x6;uq4U6`?}F!pmm-K)LRW!FH-cA!Hz0`Pq1(WuN#J;JB7!&*ngu2;0h1PkNejW5;0y$DI<x>xnh#C~??(`)Li50+Y2Z}w9t81rs0Jq80p1SYgdkoG-3%sO16~b&4?(;Ds)9)uf){}2Ac(`Dkzms4;4pA7f_OaC1txt1JRUp}LHru@uVB)l;Mc&t5X4VI`+!N?gP#UJfgo-MeG*LS0d59viXd(beH={s2)Hr05rVh@)Ez8A-JtGZ(k5Uxa6<&~pP-L|AA>fBJ_;sn0d5X%i6HI({WF;K8E^-1Uj*?ms4tlGFW_O|F$m&G(AUAF6Ty?fAqe8x(5Yb3nc&&r7zFWR=v*-ABJg7Has=^O=rS<r2jI2fSOoDd=oT>PPVg@9UIcLtG#N~q4bA}<A&ASN2f?Ie;BxRG1aURA5=>eJt_Gh)5Pu3i3?@AS{uF!xL3{~%3{3hV_!9Usg183y5t#HixCVR$LHrf;V=(Cn@K@lg2;#4yC&8qjfWHPC2;ytdQ()55;A`M-5X9G^XTYTAz}LawB8YE5KLeAV2j2jHhakQQy$B}#9DEae3qkxn^b7E9=$Fthz@$3(OYl(yaRsy#OqvU>03SdQr$G0CNq2)&zzGQAt<X3y={oRM@OlLC3h4V_(s#fsz)KLs(a<O`=?ri*cou^AZRiv*=>+iG;5QM(qoF}y(m?QN@DK!XZ|RTwRN{8fw$SInq&>lH!EF%4t)V@@q|bp{gIghppMrJ*2Mu#;(6Zrw`WKczJ}O-_*gv$?|0REHu>bOSZC`Z{5kbQm(RHl$;?zKFu1Dz3Rr)tPcZzQ'

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

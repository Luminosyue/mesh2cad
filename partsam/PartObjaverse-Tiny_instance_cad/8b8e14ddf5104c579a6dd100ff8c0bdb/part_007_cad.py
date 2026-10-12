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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8b8e14ddf5104c579a6dd100ff8c0bdb/part_007.stl', 'relative_path': '8b8e14ddf5104c579a6dd100ff8c0bdb/part_007.stl', 'source_sha256': 'fcee15e305d59dc92db6c7acaffacd6938290df0faec0229759869b16a33037b', 'input_faces': 432, 'input_vertices': 299, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.05004939064383507, 0.1579292118549347, 0.10949987918138504], [0.07228109985589981, 0.44317546486854553, 0.19566744565963745]]}
GEOMETRY_BASE85 = 'c$}r12~>^izsKJwnaWVf?3LLuXH18k;bbOc%3&uVB9%FgUB?iaBBX(hkXdG#wpqv!GP51WaE!-v2F{;<&+q$nZ{2n8T6f*sTEF%E?C<&Yd!Og`JkR^STkG`boZr@2!%t<c*W8$U(d9KwMN!RJn-CZ_E+`-{yxy3xlWnx(;;Wx;x}=+L*B<?Cv<X^7jiG_z0bw;f^ctSSn%AhK*BBNOHZIJ6%;1o)p@GW(!9O@WFvkxc;XgJo=X1?QEn3vk-D}m+r|JL4pTapqu$DA$Jes4%hlOsoR%7Z?_H651zBQnM_?A%DyuPKs_=dwJ^7zJ0vG98r$m=Hs-BO>8L+_u-?dy-K+*Y5>kGJOaldg(y3fXl!w{Nc2_Kti`J$N!t{f~piHw8aEk*Ch;2>1~Wd3@{fDDf>GE04=~-`v_Det9eUu&%3&-_&3U{A*G0i};Ig-f1Vk@zEghO{1rZZ*;SP-*c4A*R(8De9dOndhz?|a$R%Pk}_Y5S3mLfz%DXh&9e>i9je1m^+Z42qQuw#{%4)kd66Y`3~PJH_$?dL#5ecNhF{|%=GC>X_`1Vw^da3OebAooPmwykur8)bkEFg~Se*FQONUWsuKg*gZ?=WMsw(_2|1;>@A8Vyf%1{}<q4pSzzd>K|tt*^Se|3=z(UvpUNdDK0nAe6i=(9sx@%08pB;RoAwXD15`*O9^IhTR!8bf3}`lgHG8+)gr|NYxx|J>__{IR1@|8ti3+Tr%d?-+*t+<FGazow4(dVIKCSDX05X{_fbv(!m-#C0o7mwcls6#kn*Sg*!?Wc-#x!K<YI1umdYpL#M*<M(w}O1^o&_?G$yv5t32h;JUVQtE3DKS;iH-GgKq=iH7`-|}iN)@$+JWbB7M=<}?2toy`v;+u<?N1gR=j>-7jltjKM4Ey{{BK&<RNiv>cJK%4gCBD(iD86~x0Ib*Tn^>3VLgE{<ir<y%W<HaA?d`!tsdK*~=2dDX`e59bh;!{F`KIGPVjpG%iEsXAApDTa;+yArCP<x*y~H=a?<(^(&V0W@@*Ou~ed}+*`Znn<zV*5Z=ka+5_=_rwZ%lGT|8E?Zb=0j+@Z-)%zTWyftYgVvmdiNDx50Sktdi^M)%uHXj_iRx^l!pC4VH?(c0BGsTgr)V8L~D`#xr0C@`Jv}eMuYPA--{^9s2gE3;d5Y7t3|WRhM-%hW#YhH9Y(pD|IX<u>S*E;v9ME@FxvJ{XTy1g9?eS@1Ku-(zlQFQ%l>q2<Lq(`nGc-?lbzfMK~9g(4S=7$4oCG;E$S!bFmlqB~xang);s<uTlS53ieNk^8)F^)Kr|Wq`z@aD;Aw6`PIE}URHKRe!|lj$+s?npD{)Dxi)FaTp6eTON_JjM$}oD9W8#uPsnfXf&J#_K1=FUt}o*^hyIN^_jgCibtgQ=eqNT2eA~4qsdLf?_1l-jybgMcZw`pTeD4p<<LkF(V?Q@LiS_!rCqn!vH|&$WI{Lh$1bp}W=%<e()+PPUB&ollE7sBU9`~Qd`^48PN1$&lZ)3h+#!Qg$CtL7*TzVAwgR761I!k=8e|(1Fx;^5?Nq)dbTz9KC?hhA#50!iy<eQGABfsY0v2xv)--)m1tBrim$0McA=AO8p>@Sb}vXg?uulW|wi(j&kU-Zcc@yDm5Z{0Rw{4?71mHjh&6ZXkNKlI=9xsP18%L=T^<6G$G<$_IQ{ic7$x)gkkbu>O~Df8D{#Wy>9pbwT>t>p8?W;pL<XT$HeuC1KI%I|O=9$N(0?N(=~<oi~~{#o_AMf@$bM~I)e2jh>qfjZ~91&Qz49R8Z$Ft4uX#>#kHu#Ohb{TTnrs^N0oqa|=2r>;RAuhUZ`zspF>>-l2T`B$T9lJ7nR<Jma@=VJKxCh`02M*XVw(dUH=#n+<~;k$dIe(d{5@q4eiA%63g*tgc@QBr5|A@TLINyvZRZidV&Z41_M!wX#ZuWa$H&26P``lJG~?xv=;vm~GA+A{eu)@9#@Xqi`~^SJKIr<hmS6XNRwF5|hA+7A2Y=NfaQepY9!O9?Nm%aRH)lK-(0*3s@D#`)-&_-1_*>ZI&Hk=wT>{(}9JnvD9xpP)_&Ublf0^2@BBCv^@*;=X$M3f6s3p@ov~{0G*hg+<oU)Va|j$$$E{%*$G466STW5B$NqQ0Gu8>a@0vmAnu0u|KPXp#MkOE|$DaHPHV7$?z8q5Z^kqlK7@GZ86{CUE(C~l`qz}eRGUIV~zOMvV7lub6NUtigQ~keuP2l7+h~*oY8H>*FXOu<FuY_h4qbnvrPQe`J}$J@pI(6I4_savyyS&81IOFw%fiO{h25AweWO|v%P;j>fn7<3q6ebh2zCHj~an|8$Y}+rPf;^`RP}2E_!!IzTGbIt-B^;Ud97BM-NISNS&W%WXtE4i_o{m-Nd)Pm?^$tMicnmE#m8*|DgW%v$8IxE$tGePSy4}U)LI9Kfmgen0w!v?gV3Aqn9N~ooUN4{;Hd>&o8CHKaA(HVNMv<y;rvQ=JNfq4`;`r{*;=@;-{y`I8A?CLZAJvh;Q`jhw%*5WPMHb5>`t7u4~wb3!92>dG2DC`L4~pF2CPlEXHY9UwnPW74+f3VfbS_#5V?<72n+33-2Kd+M<s8HK}9ebKG!$0sQD|*gx@erT><wL*knYmc%~nP#OE-{1N1z4Z!^&=`ZPnA?=G9zu!!L-*B%E=5?gmYWZA%{!Q#>%ljbs{pVmGe_4S1*bU<Awr^yd7C!e4o~Mxi>J|Ff@d@6GPTvyWxV?ppQ@0M5eP!tJ8g-t$mOfafL}MMxyR4D%AF#oEZARk#$EBM1mJJd3J~L!J#@WLg`F2tGzWHeq_HC_h;u}^E#(Qm*Ht5@dp5hzNIb*%vc%uGoKh!B+PJB})pYKa{BELyL^f~aH^waX}6~=Ssq<k;3+>66~DY)cXS(of8I4`Rl(TB6&i*Ja;dA0_<$>SU66hj}jxne)u9ftfD4bMw{!ULSUij&2+Y#)w31X;14Q|IHlk%O*DUXmH-y2J|Pr|-WYpP%7-jb(MR_<F4gxSv$>!@LS_grC_@>X^c9aefoGqW*Pz8K?0?Dty}m7^jENMbQD%rM{usaq+G84bkV}W6;lte__6r>@Lgiw>*#hBKcCJ{uLeP`lnE=*Ek39b^ldYu|EURpW$`Ix7_KC?_C{kpbyba#kXEgkbG06Q`n!&Lc}*j48eQz6dn8hN-XO8_QrZ86u~)~x*c^UzQ#CbSH$=WoP>WZ7JUozLEpTy;h$`X`{D4x=<}85sNZ+A^iyxv0OQf>u9Nw?bwYn$+{HOd^AKPEdA*EZw||FoaiN#^hN<UdzZqKjp+8wk@aq|5pJ;dEF|T#IP^W4*=2fpJ&V}Pq<loG=kb7U5tk=aiIyS)lYN9XhKL_rLZ;1$y_0{^-K9$?ouNIa5Xd6TG_-6mxSH!OrjQO^G3;%5j`nGr<`W9bjy^JG%y7b3VC>DJSb%&qsf&0ve$=Gj;J;gVU|A2LgK8EX-@)zII!Ge8X?+CuP4hle>GdrZ8mOVbmpB{`l`F_Ov!}-t1Z?_hH^jzHMM;^gAKkg7;cO8cDoT`QO>UTkW^GHAGo9@*M>$1(bLA2#;%zu9L@!Y;OG6CNsd^+Gc_2&@r&A;K_8MIPO@ZQxr5c$Tt(oakKqS%M2W8vRFo`wCiAM?)M3EwRa{XAmDez<&Ge7)%5tLT3M);%Lje4|4M?i)_6a6kOPK2_?tM&Z42az2c|j<@*wtd&y7+SMNWWNi%cSK@oCHoYO9?=R*f-{6P)>JB&LPhAW@F&g{7PbG{etNKP6PuyvlmlizabZ%dFOpx&yi}L$v%SOm=G!OUBn8#Shm0iWR*q6fhx)^ty>yhJ7r^{8`A8y9t{cYz2)G_XmJ{W7=!u@&ZJ@|G<u^-G!uwIsen`FM-w_yK_-i!IpY%RVybQbCie1!FXHb8vClpS~vnDP8rZr|K480$Og(-G{8Vd5KoN?^Ut{Du6jvB-bD8UFGu*bkHUBi|++&&{H(FwTTy7-y%Ac+VO9o7AyXcp|>OJq_!Ud;onr?zCCz2acEV7}_Ksmj8aRiueZ4FX-on7TBN91I5>8PeuOXsfVO~_!RMty?wEcpY|Wk?dxt?=;wn1SjRtCif_I07W2C3h4BnX$9R6t!t-e4&-{1M+wjve(Es7Z(f=Qwqt1>)xDUT`$2kA`6Zv0i;yF_6CC+tM_boD>fCw4CUcVs5zqgh6=H&r6Uzq{2E~d3(#5ZhkJ|}sbPs_XvCnq95;~e&Lt%F#veap9CA6~$7r-}>4^D+b1opm1L^j(4RB;P<CEkv$sdFLbjH(V&QRr)!gFwXVBmZ;yP8vMB}(6@~GSofOk#kU5(kbFbTG+fuF3-UkQ!amtK9M`Sv3x9n!&e4{#s54{iR_wQ_a=$g(x=MdcuOh^^v>hkU5sSxX_!Ae2ZwUSs?*s8p@Z(pAuX~S|d70YIh2L=leBV3ho4tl{Hh7BhU+9SE;3jA3vsT4^n|z)(7VEWe2G*-nfAI~LhO#cEUN5oV7W*N8QaSX^!-ReEaf0|}uYYjgt8Br0@|#)WTOEJJb8y=ctgksvd}I7?GETF%5&fxp0QtrH;Q8`<5uD#RhwYLVHZ%)b4eMCZO?+e1m-xP!m5DmW#>ijt5zm+F`*7XnEyXwNE_ng_B1Y<1inl@j{W@6R{p-;m+acoX#v(Y^<x62+6(hvAt{Q}Ker+gq%n!94;xF_-oy7?<esjLU;#+EF%Q{-!BBjrU5C`#fKUb-5XjWOSYx-IObqeEs-Vjwwu4^9Ug8bk>SugXm;&NT%yN2Q$cYnb+3pJNI*2g~ZC-uQTnRXQ83?73zmq%kCX0DX+SoLwZZkiX?ar9Hkw_cosI+5LRpRbpRIu0qwUtIzFty8?rSF2wjP5kAbaG!iNN5*fpcM#v`hH;uxvN6uz+rhun81Hp<3(&W9oy0enZH4>Hswv{@qawxEom|kj+Fnw}+`HsXskckReV}%C?9XLY#n;DG!@N55M1KBA<YyK}orQ%gt$XD8E9Uy;iQbl+k17gj&e|~lTz|r}Fz=iG_kY3+YW%<Y6J}%gM*rVGVg8gehG97|k)e19wFh|!xf?^VC$%Nnll&dEDp{!u`8#qMhGGYX;-U=2MHq@58H$TD6qlyDkxP?Zsg=pD<Z9Gr<Z9#=)OKX0{mDxEkXw*@Q^%5flf$SB$YJDA>O68Nc{DYeJenLtjU)$=hcXmTV<=umHItQIB`+hNVJQBU`i`u$qz(92az2LQa?~nhr8UXr$W<ANYfx*GmDVEHAXj53u1u{?R$7r<nOuUQxG=RmxiHz5T8XT*4B3`kfa**xK(=Ej{-i;Rkd^+UfmJAeLw!nqLw?9me4cuRtaK0gJb4o}p1g^?oS}FHbrpF9Igz@7taKkak-VCEl)Rd}j-hxX)k5A#-a<W2R(g`Wg}j5IcqjD~c_;Y*^&DC0HSz)SX@=tK)cfS?<lEHeWTj8Yx5+mdiZiHp$x2U<GsxQ+iesrO$x7#tW636l;t=XYveF^s5b|J#;;z(g<gVn_R8O+f@5rsmb*W{@b;)I^4&<`r5*mJ#+E5+HHspNNqGY8-$oa_msgC6QWLs)+vMt$8Q?HOY=PD<PQSHcf%qd1KO;+kkE=Dd-twvVbf?S^5gxZ_jgxrf7Mphb1?nU;Yjwbt%yHJD3N{5n_b|5RQL+(PZ$58A<ElE~dn5?uA*@^5-El74Im!jH}?b)MJ)bix=oPQ~X;s(@S<X)U-1BT-I)Gp*MoI`!86WNJls!uINUY`?jIkAvBgFJ;gjyi)pjy#H?ID(;gE;WvvOx;C|Bkv+-QrD9+$+sAa_cIhPr7k3Y8|zYr;^_><BN>VVspH6jWPj=?vOjr1PV}V)P)CtRan1n@#p4-@qo{Mq-+B?nP`sF-IF+IJAaxh{Ao(&ilYE(MrQRZ2$uD!Fpbhj7hT;d*TjX2p?*oS7V+_Sf)TQL5>~9i7@y`s!W2hs^{iwdwkz`+TPii2!C%H4#pWK=3O&vh?Cb!SEX6+e@+b|S&XDBvO1IPhfKO;kNFhlWFY7{w&>o=95cs@gM0yUMKMm<bTB_AeVq8=n)BHyE4Cf_5!qFTwX$e*b%$=~+DXMR>}!%*yy6E4(J48_H$1<6X)9xBGqivPt>{FwTHtn?W9G5I1xaSAnwtn_Dc3VAj|aX57h`P<$KXDI%Wp|~wWu@}{s>_z^b+LQb}*@L0DIkhucsW-Vfxhb_hxhdJ5+J@{-Zp={Jh@sd(?M^n3J2DjeQH^A!!DK)3aE9W^)Tv~p^U0IRvlxn(P!q`C_U;mf;<Y)knR<wtMpk;5e29FOdWn3NoK3w)&L%&iz9K&&f1rLQD^>gW13xSNsv#5?<vw>Hf7|Ot87_RGQd;QS%N6-=4WamphEQCbp|~{Fh3vxfQ<|Z;EJLvqwHR5cIzLYQtT?|7Lh%a?`k1WrBKZY5i=lWcHHEBnHhC*KhM{-@HJq&UNAd*nAco=}sBOu$skNwW$+gHesb1uo<QmlP$u-E;sUBpd&B@itRTzqOYE!aKE=P4ID{V|JN3Ot7T#4F<T!~zfp|~MKaVx5Uth6J!6}b~b@j$8{S?O@{K=KHN;z`uW<Vob2)LCSuOUN_Hix`U6P}h>bo!d1G#oHK)_c9dkrXC{iCLduazCb-ozCgY~%_iR<|3ZC4{)POW`hl$UEBQV7H-_Rrsp<^>N!7?I6u+gaGyImJ_!&d-Yw8#BYx3_o@fX$J2Kt4pRGoi&hGJKSVx3x=T$<-!XDD`KD6T+tB0KT?S70c1WGMcqLDl(JtTc=Kk$i`tIGwtctTcw)qq9vu=luWE|HAQ~KPJ`RJpV(-fBnt8|7@E3H&5r(`j3A^?a|pzeW%R%f|^ghz#UU3O8YlC$qY{'

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

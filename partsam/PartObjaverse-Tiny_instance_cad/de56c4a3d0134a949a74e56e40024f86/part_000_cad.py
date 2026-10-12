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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/de56c4a3d0134a949a74e56e40024f86/part_000.stl', 'relative_path': 'de56c4a3d0134a949a74e56e40024f86/part_000.stl', 'source_sha256': '1b6c07f2c4ca1858955999b8e82e441bd490fdf4886eb2c663f027e568ba1d05', 'input_faces': 444, 'input_vertices': 243, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17040379345417023, 0.12261860817670822, 0.06689783185720444], [-0.06816580146551132, 0.37974610924720764, 0.15761877596378326]]}
GEOMETRY_BASE85 = 'c$}r033QEDyT`XFrl=`IVtR#&A?DOf-<oHMsnuv5LlQAhMG%g$^rID1o0wjzh9HPB5psx#S&%kb)KNnWrC7ARUw!TO?&tr{J$l!@Yu$BktY`gy`LCV5pZ)CNea~4!x)&(uqwrHrt$R{wLl<AAba*QtH6?uF<fviclj@HhADvH?5?}x1>55+cdxi|mr>3YGfy2Wm4VxI)(g<uF(L6B72#gpvaq`3=V+W6$I6PeYora8_6mI*IMhqDrZvS4Zad49$qe<-`BgXhY{uHxQu+Cn}NVC;3X#3@NZFN^qP1b7cbct`ZKPA5FRP!TR9pe+kH=e{@k#@yjAJ%I6trOop^BeKqr^ls;ZeAq5nRO#e|8A9eD!%EO4S!uR>ECf+WU5x@!f5yfS7O}xgQb7R+<_SP@nY%U@y^~u(%-rewD0_rv{%K)OFu@fV9YCKyR>(e*edxOfkE&erb|BV?Xxl8tSa!!q+FHXW7A|@<5GF?omR5=&SO<2e^tW=<Bl?sXTxPjWnRl3oRm7$Z6y60AN5Z~J?@L|=siMwH6TaYJO9cS->Ui#)IV~z%*!?YGTKM%mT|2fi^O+sO%q=|j7A-{-#sYfhNhsOxrx%=k*~AN*Zh4g^6C03>KyAW;~Kv%K|jT@Udrr+`bRE?f2acT?0jD4>nuHAeAfqi#CNTJdhAW#3OFUc88S!e=I%IDeCLGm7&pmV+PmIsC%#d4o#bi$aYphtyn>MD;~L+}xY;FST^v(uq5naZ#dr4YEBRP$0+7$JHCUIM53oPamP7u>>RpoG$0W*ptyX2w|B4ObyL)s^6MtDr@y&s;$g|T2QfJ5MLa6`1vDoLKmyoC5opc#@c1_f0#Wu;)9eP`QBdLnyX&H~Oj(=Q--|-ddcD;v;>sXv4zT?$v8P^(jFZE4doiB>{7K)U4Dc`GTKLh8^mD^m}TfZF<-<oj;`)zGgslT&FviR=9g=D^le_^z@62*5utAh3VwuwvnE4c>!oLwsU7#ZnOH}~+bkpGZRrOvKKhoufK$28O-Zh`p9Cr9$Ml0HKIxl!1k^QK50)TKelXNtGX%WT(NeDiS_{IG9iT<7_h@K^Rip81|-OCDSPDg8S?XfD1PjeEcqHX7@mzX|d$^%Cc?Pa&DFE3*djeE8^s{J!^|>_e+k0Q&J6fVv%RD(h%f^vAg0*N}e93pbA8oRx#$u(8zB8Gju6FvAD^|IqiM<k>Am>S_L~80IynEc&^(AL}x<Fvj&AE8{vBe2n&?3U%H;`Rbed(0Tmj2^lwcjLg@{+=ctF{0s421(spGHm760Hy)$?;Nuv#bP(p%=%M)5$CGfMoTz}hjm#C_oQnG-?|w5j-9-PLe#E`Hf1CJ@$V+HH`J&X*D(HuMEa<rSj-4-Ly$rLK<nMl-B)-w?JFMg8N4S>`ZH6E7i_}d$c`S8sUi}*W>L}a~yibfF8^l*3T`{k?Ycem_(|F`lgY6IA!o4wbHQHC6iu$zfk8!I<qdsa4>VIZ+GS+z#^54`L{re^3o}4^DeD}(&I7dG=MIBmn!MLrqOFxc4KdfW3<{0;<YcgN+_7Uv=arIHpKhnj|d!Cx^I>={+m(;;ppMrh<Pe1sxhM$-Ahn~v4;T}~U`4q)@w~8iWA8z(R`+EM^|M?r@KKb=Oj*CC$DEgV6D|uR_pNntbd)Ut<D;}5jU30~Egl1qJS6q_%yHf6mZ=5(PzE!3io`d<a#J5iLye5BNuRZR8L+3DV;QKPJ^2#sg$Y{4)d^M~(?!&fAu-{g1hCem!Z_gLYxm0}D&-J8#710>a+0N78pL+{_`GaVGdLr_F-c|Oev(<8$mwV}O_}dm-#QCf#dAhQD!tdA-`QKfLef3!n^zS<nbzYl*_lMP8QMbB{rM<gCtkl`8&;@nKzXQ*OnH`a5S{=-*eG%L<?_QSrt4-C>e}gZjK4zECr62WsHPkKCl>S{Y9kAb$E2ICkvdHs{5ALP+3Znm!O;Lx+Q*f^9{N|E8mq(qI{-XxVxW=+?#kWTINqaM_AMW|6O!(b`F|Vh$@EjkM0l(u;=|_!qV4pnLBfc@Bmh2z1-2yzPs_p*UxXv91@Z3*K5a0FSCs`LY_>A;pSewLmmaZz}8r@>>z7!BIzI#9e)L|RmOWhSeMf<}w@cvdjK<4G{yHI>bN)6PZ?JBJA!}%E3e42xL=9hEioIMZu533{Xt;Jh$j(mE<U*&`SbL)5M$NjyDerl%6e66$;<eAeDeoT4nlaW*LUQ{wre3ek`ocIeWoWT0jMEmtGB_H=DFKO@YSq63c(-(EvT2Jb)Zv2%d{gg<QdK!-#VPCb#gdh1j2kjr@{q6WJ@lC6=^y4%_v7cuo!0+Y2eVZ90^*0O765pLKJyU+Kv<drjON{u&^a7~oja1xAwLTHw(XKf5$%+NopY^@betaV8Rx=XkBIxxo88`YD>0b@ni}U!_EBMA0@r}9xSeF5xiSN$YCUr9t-j}*Ldq#_IY$%MnwRI!^kPp#M%Z)NG=ed)3jzl&RU-hpc{Wy=r<8#5|isCy;;yul|sM<+cpU#EQ{%#Z8&pTeF%Q$g=9hLo7s-^UAY)i#+;g1L6yQjtDp8O$5`Z3QQ72o`8IqH0Wt<1|Dx<`B~EKc%we%=rFd7oJHU$*;cX;<JAnXhZhLin?M#dmL9BI7z<O-4W6&!Y}e*?2FF^oQSK{CDC%TY>%7_Iax8w^OF%=ctl|`~T%H;yZS2mVQ*^A>0FX&cVN!F1~eVrtCv&*9q}em=Dg;>q=P1+ecEdj#cFzGs<|&xb9K&#W%X`MxLh>>hB+oeC{WsAJrP42P4Lb@1DB@>)yr}@9jCG;7<;d{Ebp|QMU_&#J2{Il71XMJNAj+=>z0{|9!0Mlk<|N6<Y%R49LRgi^-*AeO+ZX9ufciQK_?<m5jPwTQ0uYcMj_R({sE(uZa-fxupg6&&xj2kC8b{e8aaI>b4N?)kgcl;=AI9;ht~YP4aP7?<u}xMsGY%eFLQ*>s({>pKG9=!HaR9EO;C3GY(>ZP6$K(P5d!#y`iYXv@Z{c4)#U<!E<Ckn8}H#!;cSBr2SP3`*r>T?B}QpDcEm(-&o%f`IkKnKQ3O{yQAZ<zVj{dl~1npuWp!0(tgz#@y#|3Bp-887@kur!o+t!9VY8%RG5o>7~KZ_Umt*T@%uh`Uou?xl4ZV$tx?Ys^|60m=7?{6orr$!?vwsiJbXvhZW#CE&vNfMGqS~3HSfxLxlWdr{H-f{(2w^h?5EvZq&}*{F7cfk1JB6cR~e1=S(f;2@0YS4oY$t~JT{vyzEyIW)WK@GR_5i1>jU3=z;|e8?3M9j0+8p_8}Q$ryI;o7t|Y!$qd)dTkwVyqUPUqPtzMG9V}A$n&7m(2OaD>f(q6Umhu<L^e(;}I-)(nLxAm#;_npUk_@d5O$ADepo4&u{e9gO!`7R$QzR};3JY7St;5pu?1N`$9G0!hv<GFLat@uifk-E7DZp8h3teN<(ExpB8fq4F!7psf!@VdnP^QYWnjseAxr|}Bs>x<jiC-Dk-{*jJ#Z!<&kH2jYolJ@a?u+NLUi+t`M5Z_T{ri^R!U50+DCZK&tSKO1UH|=}VH|n~uj{D;AIpRbs@l|#N>fAm9&zEii;=4Kw!RLMd{5aQJiep^Asi^bT9MmcN!a><r6>i~q(djRIUP#Rp-;w2oI#=_<b8uuT+E+e;b+1xT@>Knj(LU+J4Cy~*63%btH}GF%N&n6kyX8DO7k!C-ru9SnX|dQRy_dkR(+d00J3{KO_6`@{3Tuh;QX)zEu_{*--+adp>lNG@&-WE?!A}{D`mX8=e|kaj)xA2X=hW`_o-P0515&r<(b(sa$MODi;G+1>k0;BxMn(gCPZHu1-|bZg{g=q#bL{}yH~9?x6u*Xh#<f#?BWXA4e0G!Ehpr7v#W$Dkz<PPT5Z`<~1^o{>j?Zh=)`{=zI|2PS#^>3*busV1gZ%p}5#O=k1m3sXG{m^)>R`PpCE^}7YNMa<by9!FRd1|syQ<<_ht{K?tGn_2z!&9^&v$WHucTwxSI^3#{j^W9F2if#^Igw>?U#A=T!;L3WF2|aw{FHsd-syUQh$|jUwlX89_*8?NqEmp*@yP|ywIM{YpeV^w6Exgby=5<&*Qb1iSM4jA9*(4h<#ovYoE+FeLtQb&2q6HqL+xTUQNgQW$bv|GuNsnN&fG<@jX=NGJH-v^!r}vXIvWky}uHlJ3=OjZ=Jb|{$2LI3;El(@LyL}u_5J@(ot0TsE8qNd<Cyf{gbEv{a5f&!T+nT;DdvM|G!_sud{R5X2&i&&f1Zzmx8*Byo+r#pR*&wj(rTxd#EYo6t>^P(7c+uoV=Pmi#mfmi#&lkiadcFL3NO|en5^O52X$w4<$!ZKO$?LOpYW^r+z`6PF_V#Bx~JEUPX?h?jy&M<EeYddpQ4ihUU4{S>(CoPpA{fpO8mTBghe)=Lm-8k<>_XB<C}dp*e=SioA+>$1pU{p~jQrncp0S=1J5~$dkz9sUyfEIQDpI3^|5<Y5u{Ei*}s1;|TRA^&(ko8d>XB@=@|PcKn07l)9C?l>8Y(^CoH<c^}vE9OGN%+2dNzQokjiC119~ZO2tR?ohuY-yz?kUM64W-`-+q{+@b{{5|<JbuU?KBKb7=IQ47taq?m6m*m6b?bJ`nT33*_llN0MkoS{Qshh}~Si@9?=1bIz<V)n6)E~%Ne<I%`KcL<tKOjG%{z(3jb$`Ur{4@0q`DgM&>Mimu*7qSpa}M=1`84a8!_b^XJxtCbpQ3IjZ)d$uF*IMGrjk=xmkSKdx2ZSDH#z^?49$<JkI0WW&&LeSxzvZ`hnzz$HH(}}zD_+wKE<4_Q*V=RbByc!+w1&YpM8Cf^?B}TN0=Q=solxl?0CnH7Ip;L(Mst@C$v7f8rh&WBpc*f)E49x?6Vd_a{xngGlu3K)NW+0ACh~J2UEw82a~5z=aHw77gN`e7n3(q50N*Lk1;e~vE!K?Pwlu%y+XcAK1n@9K1tp}T|?eNUP7HmUP7Kq9YdZ<9zy+)JcQhb+Kt?Y+?m>f+?m{#+K}9q+?raS+?w2p+KSwXJb<CO7d437i`?Fh22_7)5ZRwxhFXnWhFpqjkV}y(P-~I329S$U%Toi$<;k_F&B(RM?HHOvs6EJ92a`j{;nXSQaPmy*V)9IKEOjF}mYhI6Mou7~U}(NZy+YRdl-$J*d4HxhCY$8<s7=W4k-OUQxgCq_*g@S)-a$S?O(&lrKVfLTZ^tioJhvm8dY_z4K1fX`A0&T8-Aw+9Je#_RJexe6p?M<pbF$WH<cZ`k>M(K`xjVHlxjVTHwJW(RYo)m^^=)bs^4sJ<YGZOBxgPahay@bfhUVVXF67?i_Z7~U)=tze%5w%ax2BrPb7nQSrM{;;XIyh<YFFjC6Eyds_EnxcMDq~pFy*;(G*6{YQ=U6Y^AhUk%5$e_-a_4>Ja?exlhiZHb7yM4OMRj|cdX`T49zd7_sLqHlPlX%)(-tKu7(}@e^j-k)*-hf_osFw_a~2|eoP)mUPz55FC<&kWn_!&VrbrJ#{oMs?O0FUNnTH$PhCcyPaaK;CXXifqkc^8M{Z8-NN!H9O07e#N-jzDC6^=@VrVWwtwGl6M=n7wLiHgRAs3~VBbVbEX)ZwZrj{jplPfVa*Q8b^*CaPmI8$2dQ7bFYxzij-EvG!^RP)<ZALTjMn(I>il;;l6ns;w#Zc6nd`>`%f8Jc@iTPn{xm)5-dO7n1POS0Df%5(2&o=qL6Ja?n!uc!-^=PuQJkZLK<-K#m9>QbJ&TJtXq%{Qn!$yzhX#qB6<M}BHyaz3h}7A9-;Ql1~p1?>p6W1t;T)Uo6!vXi=i>?E(Gt|cF!?xwCK?<OZHJWsVIP}eHYGgosgb%F9cqczW@j#Zv#y5?}|K;?M{(46<4pt&72l&m#adEPfP*QQoco_7+><*9Ee&pV9fV$_1<f~;rWyN}jVR4?UuchX#jT3C7BwKV%vODoU2ndSxz&DE*J$<@gf70#wsZ)$PnIlr0<Q1g@X_DbHl*II;{PkHVQ&3Si==0a3OR-Av{9i_P>^)2PO$23=^R#BdNPjho>u=3oKn)^{hmFHg7JenG%Jom8X`BbO!+}oPhQ&*Dn_N!+7ywd0G1@#8`1^F2@Q+b|!nx9e+ke`yTQFoKCk@MasH7C8XW_jzVxh7d_-nwgUMAq6~dG6Wv49$7({F-}{wdQ?B(5&BILb~V6?^ED^`Y+L*AEzwxoBu)jzy9Ulzs7y@FBjT<{pXjuA>9kfy_4Vmr@xRZt)B$y-vYf86a'

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

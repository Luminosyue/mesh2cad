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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b5aa31a84cc746a982228827c5185ac3/part_003.stl', 'relative_path': 'b5aa31a84cc746a982228827c5185ac3/part_003.stl', 'source_sha256': 'e96c948fc6595919c98ace6eac9de6fa2b8805407008843c7559be751f6bb03c', 'input_faces': 540, 'input_vertices': 345, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4481496810913086, 0.23122936487197876, -0.13574475049972534], [-0.38995420932769775, 0.27222391963005066, -0.10206209123134613]]}
GEOMETRY_BASE85 = 'c$}r133QBi+s2=SAcWYr2oouihzN<;89PZ3LD5<!h`p9X?aOHUqG&1AQcI__)!LV$uUbZHsU?w6OGIm|MZK!3E!E|nd#>x5&h7Zl`Ofz_=Q`JKE`R^${%_AbGl`U>0tL$&_!DMC4K8n7uoxZ%8D)(L=^5jP4@%FB89jEgpHb42%OBI1bm`eSrH`L6!I)ZWaC+vTj9N`BwVDlSR4dw2Ysi?4@fm5O2aL%WoGy9$v{9Mq?mTl?+SqjW>xj7c2GN$d$Y{%S%m49DQK@0t=1T{}-|2s<rQ4hdcb)RuwsM^(x0jvb$&FthdvfE0kI_CSM74JvUXA>lIiB3QG4P<gww_vve)=8F_HFMxvjX|TNVLEBH~P7>9Qncd$mf*u^y9ko4*D<eQ2iJW-}dCzouA}*>g*7DKwdi@EkV9|lP9+q>9*f9u0I!}pR_nn|Mo?}sFS&U<r0jyPl(EmrCU7xIAfRYmDiT1^L>^*zPWYIc291Nzv9Uqh2BE@nrE_o$7?t9jq6qYmST%k|7QJW?wr3()#C_WsIF_)W9G(;&s073vTtI%?HXeqMpp2Q*BQD1?JsXobvl@v^XZ*uGv{^9I<3{`tLvI|I&02D`^h_1on~%~-L2}h#?D2Z_rA;aT`yPs9ORKLv0m}vp4>=&1^L#Us=b*Tm#$)511q7QB<7ty!hZWX)|1;(W~us(24Ps2o_6#<@^if|X5Q}$)L(VEXT0`4Gcn#C`!L?H8<_w8Gthrvg4)kk=4L<U{1}6#b3c5c>URvChJ5#(Y~Ois&X|aN@<El`UY&sc&!u3z*^Mwib6-ZjZntXhSTJ7Ar<uE!W+4B#tg7G4jnl34K7Vf<+MnEl_E9x(zIKg7`<H&t_N~XcX9U`}cdGd}b0hwcnt%I&;b{N+M_Bi;S{N^LYt5r-U98NF&|_*{EQf}npS4M9|Jc7CiahLVwJz4IA?Rm}MUB^+o9Eq}=hNxPdmK}_{oG*mKjg5=t@(q{er`9l?#{~t(Z2KB$SX$b{FMX94>!SeZ`;sMhXHCGy?KkYXXf_ck!roX`HmTCo?XB8LqDT>>3w46Uu{$M*q`)8Kh`LHP7UVEkK<gw+ZK6=KFF)BM*n-8VSkqHjog)+<+~5f+^7+&=FM*DiG12TRgWzu75R}VdcEShsdMU`A2a_U<C*R4p_B0bIIIimY?y-f569|tZ`T=lrQy1t#ANidJwMBLUs<{*dUD6T)B3)|+;ZuhzAu@1cAnb*&R(57x$98A+W#(F2lRjJBHC|w&Xe0lv_qX6!qvE}lUgIcxKho(H-GI$mO4kXtjKqD(DPvCybqZDTV}V!Jgm5{a_77jXutWc%54jqqy4zsxGvw<y!o-4s=e`cGvrmys@(o@BX$4uUUy3Z+9&^%rS`+W<B{K8hMdn!)-UTLKf6iSc_J3`Kkh$jy<Dg2A|G^Lt(W7Q7_8&eAJn?rnLA#1pw`ivR|oYMU!$(;_%>R#H`mwleH7}9SgFVRLnQjiU5)wNSy<;ym+AhQ+x`m3#XR)b@0(kGDV*y&F6;dWjMty-&HZfVKLqCbj?3}5ChC0bkNd{?goD1h(QC1uXXcKp#d3Ye>+-LG_B%hs`Qme?ley*XDyn{4;pdRguBPfYg2K`NvJh3js~B?Ev@lh_rCb>1XHs=lk2Sn1?|bX9fB5`qi>`v}eio3U#>L#cu6=ki=B-|cy3csmaZpL*|M?uxdrf*HA6FcC`@LA-KVmSS%w6^Csd=zY2tqy0>Z<XYxhpbG&5v_RG2|f$$b)a=eloMD&dq)JS|G;NHv;|lO7Zk>I0~T7aYI!7)=&M^`-qW|jQhs!zw$jfpAXIUHs>G6`MKli-21uU>AZIXl^chjpr5=-dOlA-Li?5lRc^oc0Quqv*}l2sxBH&lR-qx*v3d>6=N~_Ma!ZNEYW`gYbE6sdRk2l=XXdV7o2&V>1>Dm)=igQ0F6wvQQuSCW-a(ywPWH}2*e&F|pPTQ?W^TXX(&LJ{iS|YFRBr8;k9w>zYP`n4i|B{XpWb;JlIO`C4P*6rG;>P>%)_z>JSUI5pmKA(&N1h4-QtnB-wsGY|67k?{!bXVAJ%&T`PqZ{>KwIs9_xP5iGI>+s`?$@9Y8<bqg0)iYx|M6tE1|4e!ox6gITBj?p|EC^fo;IMD)dTRM0NW&+*q!sX9yTM0@`k&&=&V&QiIx{AXxiYl6yMm3QR(o-Z?ZMr=htS*g1Jw(F5wTB+RV^eOU&(fWPd_MtjQW_#Q4HE5q%SNAje1GJxBN7p%ZHS#qzbe)@*sB>rL4(8tTb*(q<V>=dO{&~ML*U`e<JYU}Zv->Ud6WB!Ww@TAd|NMQ~zSp%>pNjn29<`3nnp2P$*`ab<?a9bf*Xng|{xb59-qLxGu^8{;nJTx88i_o1yvmI!!;mMBR=H!wP~<&F>Hg=W<GL3nWc!{MGdHFT*6ml@FmH!Cs(H42(jW7j+YaZVWF*czbIYdAn9o1%;{APNKb+rf$@;wPc|q+r@4Q*sp&s+|qdEUEt&#72tjAlw74j=T>H3?tME_A&b^l$OqWzp~mD|%3(Ej3H-T$<DXdklWnYlS$bAF83b<uv$4n5ERLT*p^RM*MevMWi=r<1vBX{wq}`@9(R&+j+9<6>^Mx6Y2n`^B=_xbDOiy8a_!$j$Eq&HWZ$LY-^x{3Hk9yj*Xk>a=t#i2C!}=zYT6men5hJa*u@w`T#hue|%@sobpJGU1Pl*cUbMyi~P6>Y4ewCpSMwSf5YDJTSL4w5ayhH-7Wvmb3~gcfS8K+Al1w^Ii9l?<=5kSJv%|zWdPIKK~~2J3p%2xN#kM@GX_Q9$Z2F?Jud^S|%UY<@<{{&-N;LXwUnPcOICV?>k0rU%a0(x73K&^BHyl?fD#Nu8U#jynmYO;v91n*X8G5b3a)3??Rnj8lLi<e+zThz|MGIE@#6$oZNx-ueMjYD{m|6{G^3$|I-HK`Ee?@7FmaW0;6<ZZ4Jj2rt>=QdvZsY5S7~!Rv}L>uj}c!9QnKwDz|4W!gaSlIi=b!ejRl#zKQ1z^Lv}!v(TRR6YqXFI1~AW5qe)`Ps4Q|4SHto{anAj1?s;t3GGAs>T~fZ6YY~yRc`q+1NkGqzjW?_`#|s*)IX)8YHw5@iT>BN)OqYM)PJC{J}=GF)p|XhyOMuFzCQr#l9Go03)a@-o!lGkdsWioTAGUMww<RwH`&*A#dU43spmlJwq*1(b%uUE+>?lYvVYO{y#t-lo}bg5%ZsD_uR5arM=$62?sM10HmLv1NR=B8TA&}lfhxB?X@-7ye$CuouqpD|eRTb$8(~}>y6f?VB%r<X67uoo(B9HOojdRMISpe`=YqEQo`IjI9K9mZf8E1q-!&BN`$nMs<@%_9Y9in7!qES8e*bTNf4DFd?YDla_P=#m2<kk!7S|1~jrOZ5BOg%?{k+j0^Sr(S>bbQF^T5xou7jn~f2pPD=T3dB*NKv-$A$NO^ISN-4MIPiUPu3~cz$nC2>sZnt9~5*0jTFhN!$-(cjM<-#R{PP=1f(OQO*zTkH4hH75-PA=ejqCs(CP)Joe<S-~nph9E0wAa$El{YW{6A@1UQ`2I^UI0pGX3a|7+q#jAC<Y`={D`Ms01(=B{odMF=x6?`9V<oaR%oW78!_D`vY_#X27d9?p62l?G6_`d7jX;1EmI)eOY0jyVr<H)=2$94JhK}(~r(Ep;X>Kr)|51{{gZ>oA+-S;8SS)=-~_uh+sioC0?>lm{e^V4*Ju5<Zj<h&1f$F=|CJav9KKbC8&QGcPd9N&4i{=OXj@OwGui`Vh<(}+cA{{){Sj1qG(&(F_B`^0FhSI;eIpJB&!!~atK+o#SzKjzQ-*uOXD_dnKR2e1!cn}+$}{nI}2JLHQeBmXuC&t1n);<{%>A~)}2?BDWZdY<ojw~lsUypIN<&K1|y{Mh{lqCJ1k<*h$>0P1v|)%7Q(qW!=<IllGS$0i~-f6nNC5OpqXjehQ~%<-K!$5)L|f1d#u*NE}>x$yOR$k%qo{2zK3^%ty-`uSXHow5$?1EbJ?W_Yf;Zb(hk!{;Jr>mB$xS88QF|2L1I|I9LIpA(GsXO64f6*`KaYeryQCYDz7Z(i3ruLSxDDxmteF9||Es2}<%I1lZ&6hi)fiW;x;pg-!Ic_+uWe&d9J_IwU^E?A3ozxw2Y$9I31<2ygzoZm;;`)@)${=ax~^FH9YZi@P?h<$-2Yvfci3{jv_))<oJ^D7Y&${*98{VNf}<NsH`644+&_W%1U5o_Evtaa->`bzS9<VEzi$gj|6(cdDAFDB0-ze<0b{3`i1O88%t@DfUR6@4{%75PK@M`ZC`<PXWaDd8jZ!{j66v-C6Mv*d5-m&o6ef1rf_LkZud=aa=RlJAo5P{Ow;;XF$CH2oC$H2DzyE3)`!WbvKkaJOVjRi}h2Qo^Mu;nHrErH9Zfkt?yU5K8ztw;Isn>EYyXUN4>!u1^WqqlCjK;R^JM<ch4X0wrA1ts?Y5dMR=sIf!1GY>q965-vdr7pH{FP{NhzA><H_voa-IlM-&|GcOG(;pZvgp7eNfPjU}>eR2<ScX~atcq)0ATSMF$M;}8TN1jXxPjqVneKdUxc?|#kXi7Mp8p3OJC!4hmVeLa$M^BDXd<1<Mc^GRNK?#qiPbQBiPoad(`+%@{e-M6^KGFE+9wI!;XPm;*-J0#zB>F4lSNQjn=o843$YbfF$z#bw>FMO5<Wzchav?v%_}%Tr>3@-Xxjojc7wL`3FOvJZCGR7-ZtbUpvnk>0^c!UHU&+_WzqnP#eZA6d6{Hs+i_6~^r2k453IE3I2KhJgO?oc*Cixpm*hxP?c9OSI!dvP4$y>==+}cFnN8eB0N6w;Wle5Uz=-0{DIS1D$;fIv4KgTX};m<iKP4*|3q=dsL;c&O=(VwH2CX1IL*Pxf9mm!xU2ha<W#bvGo_*(c8CHy`8Ci#2vIr=x`bL21SPV$%J?euNr<@9CrZRBlSn`M;nJCyKJ`WEt1@<N}r6n>Mwk-mw%iR-$N65dM*pQLAzv$&QgDdDS>@Xz#z<cD16pZQwYpoD|zCCMeZ#=(@Zg%XaXgzHnnarAJqxj*74;bxR@JpDPcxmSc6&}-6bkZY35)60>|aj%r8gbUMU-xTI+;Ua#J@MB8&HvN0@ZSr~gIr4e(QTmtUFS&1yQo=hZ;T1mnYy~Ae!>t$Sne^r4<=k_bl<-URcgQc1N79#)N0NtA!h`7x$>zQsObMsCHNY*KTW`?Q$Z2fz1|__KzLC6<dv^mR{003a`3v$1`c?7?@)i2e<SXO{l<?nl*~fqLwQvdU?O<{+_ihPFxGFuCEMAvfl^o+%Q@0wq)q);Fj$xY?l(3Z&ZcUFR$MT%Cri9y4!ma3W<T##_R+MlXdOX=YCv7O<c5bz&C(s*^8}R%jP{Ot7<;k_k73qb^g?VO#tI&h!MabfEmV)?N_z5L^kA9ncn`h}BC47Mr{+fQ2{5AP=`VR8v<PYd8$SZi3KA?o>Qo<R=KW8t45+3MQBe%M_)sEhW+>YFd-k;o`|E?1yoJ@a#oJ>xkXOhKVBBzkMQo^0-Bgx{!$(_kblyD+_Fj+i}oJj6K3Ad%&$Zg3j=mW^&{m3oIO)23f^uA>A#^fgCNO~+;Jc1lauI5&NTfuG>rB@+W;oldfgv(LFq4WrH1g{ZF2}e=FUFf~YUC1*j;W_jd$#clBQ^E`AeaU?}7Yiui`IPWH`T(-{8{~Q9_4Ezo_2fPDFUWhy$LS}?$H^}G6|(pPvWxr^CHyD-Z}OkyV!Y4FJ+v4l97?ZBuFCskC?y<13D>4KBG)F@p*JPhAxG0&lEs^oqsdWjMbMkjo0B`y6Y0&#iR5H@OL9wIFPRcfqPHN6Tgge}&XjN$dTX+HTXGk2H+m~_H*yNS4LOC}gWis8-s^i%!q2<ao8E!mp4@@lke)zpNRFh}B8yifoA>=lO1K&&T#6n<7MJ^eDZUo=qu(Qogny)jFVioO#lI$BCg)JX2kD=a50W?2KOk==ze}G>ewS>gXOP7QlI`TFl<>>+{$%k!<d?~#=-tSp$b%^1-jr}hdLwd2avis7&|~P0$T8#udONasCvpP08716?o=g@`A&Yk<w;{Krgst?>WGlH9J&D|k+?t+9ZcT1Z??4uBOKwh%qqiW(k?Yc%lIxPA=}pMd<l6K|a&2-gdNpz_a#ea2vUo7LD!Du*T$mCrND2GX1IPy5j~+l4FKT!{mU*}UC0vMJjw~KZE<`Ry30vq<WDB`Hy$iWLc^Z8t`F*;BK9ejyhwLDKObM@}zfKlkKwd}wloI}gKA$W;k1W2PEWU^Q3HjfY@G<&vvbc+UjQkxXe4qXkS^Q7(eexfaa8W<FyyppvhmyrZ$bt0A^boRmZL)YBvUoJPGPx2xid>0Yff6q3_s@G?SxUG#C0v~nZcJ}NHs2Q;Q^Fl7;jWZ$Dm{^$O72ciCU+<Iq$iPkl6$$8lH})Kw!r`NUu6IJW0ymq{=@9k|5E=L$@gED4>SJxp;AgxfSeEaVe|KV$r>hi2jjmeywHR'

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

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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ca1867c11bb48a39eb2aca203beb70b/part_004.stl', 'relative_path': '8ca1867c11bb48a39eb2aca203beb70b/part_004.stl', 'source_sha256': 'c900aae614af82e29b51eb060d5808ae7b49b04679b827905d8d053722c0b83c', 'input_faces': 729, 'input_vertices': 458, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.18104571104049683, -0.2863118052482605, -0.3031321167945862], [0.14090465009212494, -0.09744122624397278, 0.2221304476261139]]}
GEOMETRY_BASE85 = 'c$~GI2b2`W+J>8`1O*g9F)#uO$fAhA0uq`eNrDm#qyd&BX<ecMG9*FLf`ABu49Q5&aT&t0JM8W(pkPD?MJ{?(R50Py`&UgrHFnn)|L?t?pL4$RKK1rDUsqLkRrk!<L&vrS3YNB<e|K6(FV4Q0T+Om%6t_xSqx+?d9Mreph<k@6Ka<ZY8S~{or3>13Y1i?IeAZ}dT;-&GBl@OPuJ5bdpnu)U3BJnxho_88={>C1@RX!}(toJ;kP-caKVo3-<bI-ErB>~_3BCuaCio`!{>y(wMHd2-5;6`54SoCQNvT$g&$17=e5-7snD6_&>T#1FN=**CegDF{PDl;Dx&DOFuQTYV+YennlWRJ!FL8OykJ|Sfar=R$vtz!!ZBxYLM^D|D<>_aKuEzSIM~cV%(5T4~lkY3t)LUn8FqRiQS@F2Z51kwDnFn8`dNJSb^nI?$kJfp|lOJkYFDKUiY|n9%?@Mo=>Gq?;e~gXC-yv|^=>PMuCqJ~PQ_S}j|Mie(-p)K18>d~g*a?&GAGIOF?b~SsV!m}K^SIG3{D9}YR^NkRQ-0jn@}te(3Y+?)e7!%xS*J3M<J#=h)#oSf>+|!;#SG*8<LmQp|9<hP>G~>PzrOw*Gme_>ALZ-!PcZkkqo(^)`TG6oKY23Ube{(Xy_#-ZFZlX;vA>#?Zd!Nt&WDZlgTI_PWLnq3OLrWM^;6q7l&|j_(PmRZ?)tuW20Qht*U2&Y(R)id>t)@8IY$4?3{Sq5THIL2{^C-$b3fjZWAg3FuX+2EvD3+a+n;0d?ZtJCeqh2JbDdB7diz=aSz~{culL6u)jQibZ>PFvo8~9(Yx5I2ooK8R-05@9d*-8v$&aqPaLn!d-oL@A-*$Y&<OdtI%JQ6d^)Jr8apQ@I$&Ze{<f(5ZU3Bi(F7qNLKUk}lxBilIv3BTUm0XkWTl$Kpel+#ClRvIduF1ErKj6u?J7zfkt|k$aA38DF(;w^keNO+I42&54R^2`M_Q_Po-+O(o(T{BR&d;^eobxuXoon&~EmFPx&m8B>|D>lQM!!fW?|eSc-|??&A2Iq9MtkxDgSt8Aef@mI<Oe@H<LQron{z(vtF;l6AG*iqsqg<W(W$@rO2p&`-w%802ZGg{{PM3vjQ&$qJ@uo3-@~T-xUc0~3EziJ{ZW3N{``D8Y#Oif_3>J}a>AzhRK7l+!EX+QP1h^#Yu79E`G&CReu(?p{SdfiP1tn5DPO<ed>xjAP4{!$*YD@MhlP#nMfuu#33clmHmyhH>+3Nv|M9SCy(?c|?}6#foqTOSQNF&P*!$}_{nYj=<?H)Za6%1dp0)i@`TBlnw=Uz<*Y;cG>-(+$auH`-+J3HlwVzv)ZgQ^6v|l{W1?7hdop+uKQ%dHT{7~U-p8WXpaZaTilOOum3UB@&(~b3&uh+LHjxzQ$Q0ct0Kaa?cnEX(gUp(XW5C6ooKjiUQ@A31p&s)<kM~r@f<DU9~ZacEv*Gu=+^-{i-ve2`?>Au=e;=bDdd2iHx_1+loXU`#7?)yRa_4`5X^Pv~sikN)cD(9)M_8C22`Fg&6cwgAqAAG$(@%={|uk!Wr`Zq50?9aNd&u26}#k0P2U%y^zpV9A!xUbz0)|NJ&=Sv=6yWiA4ljnX``;vA)+pD%_n$|_M!pcn3`ci(L^?NQQ)3|=|_4OOPwVAQL^7E|UWi>qg^sl_enYUkSMvVTr-(qz`k@69fZ|_}`<@W7_ZjPT@C)ebw=aljTGn1V6)eZTNoBU|Pfw1SiPt|em{{i)moBY7uM?Cp<lgnXKzVh|_=u1a3P5n{6-XHtNoDAc5@%8bB)>h9j&L_S;pP|Y>9d%!qV2L-J@0n-&<d}S4ff~;I7wev5@&iSl^5n;#3q9xLn0&ihq9;ETZR_|oFGNhf_4vofJpIhqDBIK@<?H>izOL`&C-jS${7{cxS)OrKEarJ0#q)Rn=B(#uI^-JtQlmWm43s<R+*he(A|^j{WxeOTp@z>o{!o9e$+vGy^3KDGj!yoR$`O-q7hdii*N{?9{_#?|Cf{nl&D;MmmXm*MZp7r<2WorjTW?i4X3AH-o^Nk2d(6}y<?H>iC%+#yju&4auRUy2*fgKY*XJ`@__46*dMRJOUjBjA!>0Qo?rZmhc=60M-iP@5eQ0NWl4)8O%2(^c8eYNqT}JyISo!+zz`Cz~&r!bqJ8&MK-;0#5e(w!d$~kHB)$dX9e)4;!J+=QkCSUy?sC@N1p`Ne*eyDu)JDA=d{r9nW9rZhyHeUVrvAD1OKBoKneCofC`Nx)zwfzNmoiO=<`$szdt6%0C{jWa^d+L0?A=VGOVVe^sKTx7ZhTHeuP{65Mq~%GI?;BGm-R)b|%RA4_FLO?se0xWgBOZTZv9K{8U(ffKxcjK7Kg!qp6L>P~uxY%?*T)-e)%1{QKI6VNpTV1VAM{+8^^c^*t}E{|!SYQq8k_uIYaes_cHe5w^QrT-=_cP!AC~R*t?oJ5rhMhAeCzg{{jvV9EbKhjGxlV<{m{IH&c4v3jnR+3pAdHYzM_?mx$D>y2keXG<@R#s>6`R)lW!$#&XRuc+t2p8ef#51=_cR*LcOCVKbqRmSjTEuF*aViXV1N+`Oo7s|H{|rU-#8~Dqo*}-B<acoDcSx#;f~kyt=Q(tNUuazJ^`A`OLrWtND*sI5a<YzVF65-<vA0$T0dpycfIf!K$<7#OBRkA<Lbg$0y$|bLP87@_bi5_2lRA_52S`d+#g!P)3sH{?vVSe=1+SSL=23@#gXAPpI&+IgJhD&Eu0FXplC)v7vq*pL~Bx&$na8`Q0yCt9gdW50yM<^nFEk80!Si)r{TGfz;FM8oTB>xaWfmlW+H09(Ma`TzbCpRldD-(fU}O!zHra{nvfff8AI8*L~Ih(7z{ci0KcLobw*^WtjZn<6UF<!Asd2WBz@oJo&n>=liNvH|8r}<%cfK-el~L=Bs?WT>j0*`O*CN{AhlBel$NmKWQ5_o35|!tLvqF{rc*DJb%yaTTJ(-?yLUmzUsg3$NPWBp4~CECLV~bYxX7O+sRj)=hzcN&Hl(s9zSp_CCy#OSMxK+e_*%syTOIz43i(MQTUkK_b>e|+mx?-l^<%>d5=_mzt#PCf8KpR=G$p@?EOLQOUl=u3%akK3%akK3%VbFE~xY7R7o?{SH50H`Ffo|$L#&?>!SOCKQ4Ry3*YZ@k2iYq_n7bh=u_wW#+w5&Oun65;+Wf4?;*jNrH>l@xqY(SzV%S+OjCX3tNMYY9(!YTwD*KOKJN+2*WVL#Up@DgufHege*8UQ&Wye8`y_h(`3#fqFFHT$_SHP=`SJNz`9JO3Yg!k&AHUD>^>v~9D&J}wcKUhnSf=~BE8q9zHqZSZ7?tbH!-oZP-0Mj9<L@n(&+av?7u{FuMfcTxuKVgfSH8YpbYHKpuOr>p>+9=C_v7oRX6=3M`3#+|pK0;~O&f&WzM5w}U->HEzpQ!8*Y{!N>-%sXpM6;Q`aT>e+<Bk-I;#29eKnuDujW(t<MTPK|31(4<^Iuq)gSxD+WXz}79CnR)8zZ#P7b?$HE();{C?K*)jAEmK0CwY2cG`QldsmPp0E6Pe&rtfP4lVyYCd&e&8P0izc<y*jrscbMCI$>6LmlS9*(bnPYmun>+KKMOZVf?&7yVFjQ79h$M1jqJomrmt9(1$Ddy+-o~Zlkdm?_G?}?fp|DK4S=X;{&$DbD;1wG@6@00lY{^?(GHqCussr_H~)&8%1{duALD&HQs@PMa|x*zcKJm0GpITWj>Ki@S!{(Q&J^L*ER^?b+A^L*F*SpANkzt(*!=}?Jv6)a0e5v#P-zqjj8b)_l)DK-D8?x0$K=}&bNYu5X_f2untpJlxuVm3Mho((^R_J`jPu@rA9zT{0Ddlj7l%be%QliJtCuh5n{z{PLUev>{a-b8y7wIz2G@sfxh=*w_-5sNv#m}A{ICUbhCOW>YxcXToQGM`<7E{5lcm@8r^Iv5@%Vu*<OXsU|`(Uv+39?EBj5rfH<IuIVnXH?x(&OZ;Hi_U_j&V=W}gVBNTTOyX>EyI_*nPV%^nXt^6PM*{x7cZy1oPH{PoA%rEN%3ado2e~XEDmdoh~4N;c!P+IA|4P?7QLB}TnpU@uNSdSL`@N8(3=R!_oM6JjeMpSHEZ#?GH^{-UG=#QeD)@^EO9@5xt|=#oka8!(HZr_T|_hy(G_h9*AtN_qPB=?XmvvJeP|+luZS8V5(vq42+8%)x^R8C9-0W(pk7@x5q?-iTM@0$mT-F!?Ks|!W0Kp5XwC7~9Ba>KT5`N4$J%gAeePlMR8Cv++EPdI<03kWcns~};^wraHiI7(@rZ~g(I?=h%)5;?hGqQ*)N4R3$t^@Qq((#PsJe|fkJN|Y#$0<F?F`F)JxJdkr0=TF4LII_W6h}7f|@Njr#e?djyL3(WO<JT@;UdJ)Jbsfe9k@B2ki<sq1~A1LVvsPnNCD+YD=9APv#to<*_MfA9xb#NBh8jxHH-n?hM;#Q+St%9U{h}qv6rC$Dljm5h5}~j6%b3vWO!ho<`H*QRIw7GvTMn8G&ZNBgsiYkHRT%GI|7FDPpyV1?VDpi->I^_M!XX1>{Ucr@{Nk*@|w5r;_s`x)9z<&PsGO92BvN^RMFETlmaEjxXd`kedDQq>hId!mH3V@G5v4ng(x!_oIj4{qT0`%kxb@7r_(YwdiViEqnmo4sWOC0s1EEK8Fs6*Kq7L^f|a6=Npbrbn#l+QeSuR0oqazy7&-nsfS&hMq6sg#cOD<p)Zo}6j4z`d9)H-9`>OX;2T7g7Euzt5iSXrKuf_@McgIgZV|VMxK+e0BJL4USws~PcZj%MM7ex_uDxdo$>Y#5@HkjL+vT%duFbuK<UQyPcn>Vsx_lRu?|t%JQNHKN_dWSeDc>#RdxU)Vknauh{XxE?Ocn3alSND;Bu^nEPZF_M#3K35jn0P`z^UjQI2E2nNPa=YY7r|$tRy5aM_+;85b>IbHRvjM4ID&Yg@f=iLh@1(FN;_x;w3`zi|9P~MR+bc8=ec#6fr}@^CG6BQ{m~bnzyOUnVQf4uQ`03d0b1ZW-kBA+%AWgh}a}zgNTjjI(Q?z9(@a555G-FepAF#BKn9Jg7$~UiU^1pjgE(9ew19PAH(Ch#-rgkXeUuq=3EdlQp9ucIoe<01>g&`$5JmD4Z3&@?elzYEc_Mik2!ZA_!HXQE$4oE5`LNX<09IN=!$lPn~TU1(G(5CQro!rIBgl7MLdi?3d{PZsV(&+?B`f_v@0w>H<!;!evx)_`ldeHow0OfEZyOSwA)bQA#|pT=h8k&-S%(}?FTJq{WOH1r)`U9gx`o`l52`MBI17ZFkD|m9T5-EmRbv~1KZSSfHw(W@)X+g_;hj_(wFJfN#{ILGvJz>uQpoC#fSOaVLl_d9_Ok9Pov$<a@Khlcrop^B3f9^+LrnPEc4|0?*K2LE%W6b@d!MJ_HfHt|D)g)v<JY$;a6zO^(6PnA@EY#DVDS6J`1m+eYG_%*OJ_G2f{(xa-GQaG7S9;9tMv^&s%@)6LP(dN1uiN(>-J)$5PNCu-a4BSl+!w=AR??9JSO~)xML&`1%tAnXiG2b*c5|el*hZ?n}?1&!Q==xgEm%4q@(BS%2<d&spAmY#4KqZ2i4GEs0tK(PVf${dxm^4OV+!lI7h4<^CY|kcH?x_&?nn<vt>xv#sEnw6C^jy7x`@o+<aqo|d!E_2m4IT36po)jq2B)c<xbmH8i%`ysW|Sk*q;obh!;=ec+`?f0qG6aLWE_A?&8^?&cxa*Xftxp%46lX+{y9RHR5{5ZAR!0*y-POVnxL-3Q#$)oT~wAJ&Vx%Jnc3vyqUduBa&I&IrBKQH87EZ?{4!jowyia2UH`?u61@YS9#a_?5pnEIT*j`hDkYa;YT>M^)6#~N6F?Rg~gv&hY&mKtj!<4k0H52DYzcq(n#=M3s)P^&S1W5&~%zNooX&%(d+9IVBhE1pFAYR|_+YSl$+!&iH5HezlQ(W9_>jxMmg&(oHc^UR!uroxYj=*8!H@fpeTIV#`9pMdAn?jhnm5uMO?;7)LBG#73nqM7A9!<*5M7OrD$(H8J2`tcb20qu5p9ndbYdPh+23+g@L1bOY?Q?9Z0V4OV|UpI8Iix<(Bea@y%HnrN}w_`l*=u1oM>hC9VjG25clUmJ~x7N&YYsR78VNCBct(n^<XeQi)T2G*lz%7}R7Vs?Ey_nk`=zH+fmh)X`Fuam>Kg)SX8UQb$JxIg|@<;F)$<K%wXF1=)q`nSM5b+NY6VWeWsbgIH1?{0C`dZF=T3^mT+;waeIvoC#ehh*?r`;Q`A37Mm+WX;0<n@L>b&Yib<D9@apGH@@cr9(&=QGqfL#^KUy%|q$`l9A`F!MW@xnIH<&+@sm)auK8jbV<*FphD=DCT_>V|tyOFR1qgwT3d5iS&IUpMS=>`g`){d}ajv585}2xKTtYLh^NJ3HUnrTC^B^EnEmK0vCd>L5srIz{Sz);o@*f^ai*jd=pw0z6rh+y#>A%_MvycKDZKE0j>mBMel~I!U<><I03!~tqe=82;T$WMM%CAEf3!b--echZ-dLAH^Vn`Z6qJ$e235~@F6&a-VKM~G_(So2Jb`ffcL?B&|Ba=@Gi70ybIoe-T?1_x1ra=+u$u|QFsfy87%^DhPR@{;H~g>v;@2z-ih7_?}T@wH^aN(y=XajFT5Wu5ATN$pcUbYT#p0jLHM5{ei!i#`fvCf_#&DwpTig7@6iIV49S<!La+?UKcd&bG9>?u7J+3*{uM0-%aHsVdL1l7^1smQVHuLIFfKXHKhUq?KVU1Lqu;_ZB<DxJgJnoAi2eY}kX#tO49k#wE&3BILvm5{7g&bm;^-Cl3S*IMF^2r;H*kKqAbJrl2p2}bhYQ1{(Mxb?_;&P1_;$D&`ZHV&u8#f+SBLLIe}nIXYoPyvYryw1E=ye-F3HzKKCYA00`Rx6ye1vn=F4BYz}5a+x<CH~Vsq*KPwMnfdjCYm{mBiYR{RfUI<_q&=TcmN{IQ4iBKb|s`X8KX8*u'

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

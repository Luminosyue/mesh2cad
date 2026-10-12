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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6568e5d622254ccdba3503288faed773/part_000.stl', 'relative_path': '6568e5d622254ccdba3503288faed773/part_000.stl', 'source_sha256': '5bbaf4f06916179d832ebffcada6f9b7733abd6d3a65d3ac626d9e6abfa374ad', 'input_faces': 456, 'input_vertices': 257, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18427865207195282, -0.32170307636260986, -0.4999998211860657], [0.18428495526313782, 0.3217029273509979, 0.49999988079071045]]}
GEOMETRY_BASE85 = 'c$}r02UHc;x5h_oDQN6i5}jCLVvR<Eoe65N*Tfd17b9rYzYq~i)OhW^Vz3e~7Hm;KF^EPPJ7SEWSTKoRB+*FFSYwO&X7BwS8Cd?;dh0#b+UxuA-81K&IkV56GXq^a6f9Imlb^S>osZ|$SYBS!C_J??+UUTMqrUtiFtpx?kZ}dH6718D((ulocIw)vfHqniUvp4k=ocevHq~o34{BVqj$Sh;c;u*&0V4(kj~o<8{>K5sLjx^8bVxu*p!NH^4ZVHp=pVdSN1v$wAAer6hT!-r;#iWU&QV3vNwwD=uJonftIcQM71=A5{RX;=d@X%A`&!@6Quw$&9XFG2_UR&i$EAl!9qrG?lJ9QOh<!7t?S5&$J)V4HXg%@&^f}7McbK?~)HSfC^t0;O8UFt1lYb!J@trQ?y#7SSGk8n_`_C$}@4kIzCx35BtKIBh@R0VUV%Bj#AII(G{_EX2%Ew=I?BMS`P<%i8zup#qaB>_Uzosnv`nVkN^#y^fjW4n9KAkOot-dlZH7h1@KM!|`Kj1!(U)%iEA)e2LaqJuGd#AA<7RkQr@2%{cReH*Jq6;48{-z8TKdU4Ajw_dvS=%&|{;TD1|N1JApSb<NrqVufDEIH)SBiaoLv``r^5cHoF_9<vd;iQl!hU9B_FZ0e(^%g-#J+Rd74F{*Y<-%?RpX$vul<pX|GQ4?J2KX=uYD6Rfj@6B{S1H4^hoKaQa$cp>#>r3=iCTsKj#2n7b78qeWUqI@vFCt=YCQKrL*5>toThTnS33K<gl+594h|5MP)u(k2uTy-|i=V)7aHKj>o^VZxn|g`%!QHUe6osyAnPVztQy*tW|EY@BY4*jK9$t&IfZ{>2utFKk>~^tMPdmabD~ji@Qlb>DM_wojp3TZ`K#z*)~JwGr0@<u18(PpVcseHNKnlv#5pibJZEc*VohIJdelc9rj&MM*hg{E1wg;Y$+K}^-Nwz&eXXV_<M_&kbWlj;`OKnuVLR+>9PEtG>X@+c_t`>ujBYE_MK^|JWiv3ql?^sU-1oB2%nc@x;OjIR|iV_<Or@Cj;Av(C%wcspDw;^Z*L@j!@lwSd7k#lcRZc<U;UT$<Fxv*``VE$XI?fQ<>w!d9uj)Y_a);|e*W>;{g?Hl#^Z|jJHW@Ox_Y+Wa-Pp~O%KTUM@t>68_juYjHx7k<QA!`RYEuNbxeE8d2bxQAm<(ZTMXxa*cI`w@8`PesF=2s*ZYOj?5p}|49nrVss$yBU#bhQFYWnYsh^Hm@$c?i&+RX#?&0(JaE<t=lg6BW`*{3ISBU>lXb6w9UNNqRM#p9N-b}8C&RPzst6l@dM?G|WRF~_X<Mlr5tGcIGUB$jWtBm-ld)l=zT=(>bX-V7<>Yk(W`V;K$jbdNbH?4CUsc%Iqh~LXc>gS?YxW4JlugHA}_01Ud3fD3B?giqbUOA42NgXTvD*M`wgM6LL*Auxu=<7V#S9QQF_LtO+_yW@Y!m>g9`Nv13eTAp{*xxF3z-U~7*SnsT$^MHvkWyXh!@#5LoA1uu#`(4Tu(Yog$-dq$daqo!Ra^&L*(2F^XSS95@5K;a??&zZ>>IOw;O}(?8(WfWzLkg*d~Lp~bUX29%;r2at~QtYFtLh^6ZJtmQIzX|UZt{(v(^~SXSXK4IosemrET&b&;1u0z~fTB`&dM}-PfLX+G`)D+0Qf8?yGSs-zfcjkIb92*Anlg*?q0Cv{%0K^Y{1U8PD0f=j{HA@xa%v-P~>O-z=JV$?mKEm2Zr@yerRoe-QXB&woTJ`$mr`az5wQtl;^K3KzfI(G=<T>IR<A+P&F#)Vm|=J-pX;ZhyLpv@eh?c{lA1UhmrJXYuy+u2<^7>)mW|gMDZGcvgK<H1DHa4fo0YwSC16+~0sVc)go<BjWArU2C!BM;?Fuh2l4=KT_ta2iF1Z^Eu-0^o-);?{8t>S-3*HeZ89%e>uqhCeQdh>wRbo*%!^5y3@Yi&ASzOy&KzW@3gOXt+v0c_i~SS*w?!mdqeg)Cqj1E*Sj(Daw?y1ecv7S^{yX1%XL6oay8Dr-ra3F@_N@h_h(=8I3;zt;e1)Yu0C=0^{$2OXJ6~xJI=nYo$ap4zT%56;+H?pbwIndT=pkji^=!CUyj$c;ki`y312^pm3)&rpbvT=`<6Yo*w;SoBkSY(mvY}PmBPL|(NEUT#8$lC-4E7E`^JkUuih%j>sOyYE;i5lZSf2H+O{$5n=QYV{5<e0`)2jgYxCrDaO4smzt)p|BR*8x_piH*+i$xN#p8ayLGEAccdqCDTMcC2*mYLcfB8z=*ne`*#qE6(IG>I7BV=A339dZ(oHJRT7sBVUZ#euVuXh*Wd^RT55r5%!zJIxv2Pg7+`5<MDJ)iYT4`u%!xmNr^W-!m+wXK}zj(&^TcRstt_b=1`vG_yMBJKI?7(1HtS+BD^(w@)m&}{JoLs!}J*>NzL_XY0GUMubS>}r1_g~v1S(-ro7cI{Zk`Rr=haG5=ywHiAlpIZk+*z?&KxsCJLUF5ZI?fI-Vs?7Q9^1Zi&zt>NT<neTOa9%n7NMB;lXJ^i0@pqkAV$Wye^CY>i^-fu0&u91V!)0BBS6pJxTi4hV(oawk>A!a-=eagy1n0S9@aK#9y1o%7`P`)y=d=FSrbXQEu=bKCwad#sHtYUEZeL<9=au_ZmfY8_tzKZyXCr32<ZTo2&G@mh4=))b_ph5h=la_7x$5SH{JkIEW?w(tS@OADXQ|s?-<{9%nAKhK`Ol;4`1g<$K2EE?K-OK!s^9bRUi%mEJk4t=`!TO<er|BD%Vu9a=jva@%XOZsFZQ+NxzTPj*K?;=Kk*wslKb3&1kQi=m$TS6=O31OS#q-M>yAH>_EZ0o=a-7}d0*#j)sEMz(SDIU{}#Hz&&AG*@$Bo(>hp7xEB-9ke`Eeh_SJfEX0_q<qLn<wzL{28>h0l<>^rVKk@jyE;(TxpFE8t*>?`4X{G~8nM|x5h_RSIj;gWY-<vH$p7T+)QgW6L5JZ!}ee7;frO#c1OQudwib=}10TX)+5{{8$O_SJfHH805P&d5lUeiC}h{eFTE`|jBqU(XlM*VCiecli}!U;8n761RV}S^5dDAil>ZQU?MqO8dlW;t&1sB+qm3ZT1~ABH7p9Su5`wJd5!2ySs0N2p(@`uY-JEA6GfT$FG~gzL8KNk<Tm4i}OO;cP&Elefam>|G#(HH#XLg`igquUhd?2;u>6=eeLMp*}N_`&6np7A8+vw$F1SxZ?6+S*~!lzs{T0dE|vPTXcqg9H;3`OnQNliH~iPKZ<IU6=W7(s6u;R|%OwwnC38O=4Zbg%)$YpkO`8jRzRu0d<$m3^H1Bte^aiqD+my+^@!I?BI}eoK&iy~ED(^8aHep};x|6J9qY3-Yh?eZDI_dOi&Az*pue5I%^BwEFHtai2wOGZ!FLll0@0}XN_0#b76TewgX+LEc`&!y3?5p=7j&)A)Ckzw6;$hw&yB#Z~4*N&3?_SWE_k-@y=h@c>o@L*dkS))1QKh6l&n>pvo+qxs-Q{_tTtj(J(X$25v-!t(_Khum?5jGjB`#p!^lB&1A-=8odbtWmu<s1*!}VSJ>=vuu;e@=mnbBYT)!oNadq?p!dERLd#{P@@#ZTGnyIOA)|Jhcq8~Ubd@_wdlRh}<>RD0RqRgRJOIp>y(KkF@C*UkstypMKydvgBiC0>_0^Jus1uT#geulXI}?=d?zlKV)@N#b9<#dXYB(JZeYyQr_-ceQu1?;M=Yb=Ii|$bPKKdiGyDmyHXQebnJo(tdi5)YVs)v2Qxl#mD;@educ0r+J?jANMu)gf-$DO{6ZoJ%``VIMd~Qj(##i{A%O)`Nn8h{k-JSRq^qD#$1uXzWLSP^4>7DkKFH8+z`K%Kkuit;$!6bYjwQb2g9S-SNA*fohfp^E4x<q-!0_*jM-_b?DzI>+`{Lrp8Hyzj83xoFP{69Um%O`W9s?H;Wy=w-B-^?%6FAZ-fr*Tb+g$iyRZ6JzWYXCjLav-(_==O-B-_3$~V8C9BUts7Bc;u-B;sLzESN^oV|ZzZTm}hU-kdOkB&fH%=`W-zpvgGDL?=FtNgxtU-UBnW&No4Mas|r{wlwpe?0l$U*-4nk0<~8tNcEXr)!?SYGfppe%D==UNvgkt6CW?D8Tk74KnFR>C6A5@nxg`)t@vPd4Kr-{gXyzYYg<)l`0708qkVh(n{bO;CB$jHKA{UN#6q31iyzMt_9V>q}9N+z;zJBwGqVCp<dwX;BpA!Qqa<1(l@}Rz{R0O!NtKvpc;6b72~Z~h9F*!AYK9e8caF?yaK!uIuX1Qyb3|Q8u|_RJE#--4cH0pjUes`oe1s;?tvig4xIp=fU$N*5O;%)2X_N^MG$v}jstguj)sl{kHdV8Mi4Kx;u7>Cg7{bHGVn6Y@2?2rOy~-5Cin`1I19QGyb|-9g&_U|L3|au8m#91DuVb=1o1TlaU|3Ujs#DF_6AP^_d*b>d?r?TPFxGx6WkNmPpu2$_n_Ui+%-k4)*A6U&~D&vxPEHQ605aLTm{-0tgfr73B;8V#8nZ*oe;!hprgT~ab3qCh`-fx^ME+Sijh_<KoBoN5HE&?g2SO<&`@v(Xgg>qI26aXLlCz`5Pu8}0k?q$LqotJ7+)}gc)k@|q4CfK;CS$l2;yVVMc`xL6VSzAb)F{>#AgxVn7d2hZ=qq}Z^3HL!*G4n9I5No!FC;qD<Fu=Lfe7Mg3CbLg4<$_${>hKB8W@a=ClNY_%#IaN6=vKN8n)y;@QyoU^VZ=fmQ@rF%>~P4LTS+4Llt|JQMmQm~<$3CU_Qtcn)+pcrNrm(Ba@#P(SE!upiif4h0XzcN+*|U+7@4FSrGQxH&Wk9E7=Ojv#JkMN{Y?XdpNc^EC)TJjIGNP#1J6*aeP45U+(!15d;Ju0;^9LlAF-&IHfI{BA@LZ$=PrgU$h~dEbU0-i{#NiXfhiARY$&4_I9%m1D#z_lQ+~5*LH|fs27Xp$6C!{3?R@6{s)R7uW9<1aTo~b8sPWK?Jb}v>8}kR}Tbn0R*x7A#Q>o{sKA(OgaVp1$eTSn+L=PtT<>zDuVbFg7|0XAu#D-@Xz3r&?DfJ;GYo0#}ULwt=I?M3q1lpg1+`5i1#3f6QPH|hcLcG1o3VJaRT%JI03v9L2M$3PeW6|m!ZEvQ^Bd2qhAoj8PK1>8Q=>D;`7jx;FFl6^9bT|2;y|;aqt;v3iLSmIOZ`0L7a>r-fx?C;vb;9p!>kPz;V#M;Jvs8aR}mA1aS;B5uAu?5Q8Azf*{@mO#mn0dTc@vM{AO&q#K|+!5hFk5X4DP6Kvv|B_W8@Y}YjnLF`5lt9>BxpU_{l+`S^P+Cvim0nGqs;CidQD6!h35?_Iy2cO6FR(oAywFf5t6`BrKd7$>s#A?4yto9GYXQ3%t?jD0!?LCN(L6f!IeGBoA(EVVQH)_vAtoB00sy-8MhwjpHYdEp0?Zlg*abVI|E%zQltnMAe>!2}U(k)u<J&0J{n~0;Jo4};eTJAlL*rny>8F5Q1hFH-WIs#1k6}UCnA36%`4{nbj?t&m5YefWf33L>A6#80%AYKR^0bU562OR>Q2cCiRAe{^y0-g+3_X6T3(3V>6eS}#35Ep^A1{VRVXKLb7P=ByL&R;!`6RYQU;_A>YTJAGGv3hPI?gbsI<vv>xt7k6aNZXvMXEb89eu>@CC0gzpCsu2pI0?ECybyD$>IU%+=nO5l<`8eN%{y^jEACrS5Bd+dkrn@1@d5M+xGp~bz}D^q99tLd>cV@1{_dlX`|$q7vH#%sf8Y@}u;P&w4WW<0jp+hg8wwxjb4|DbKKHS;^TDz7*>k85_%S}CJ|4j%ZivqsL&+nqZ^Z*E-iJN}e`v)sE4-mk!S(UEx2>Hwj;)V&_2E55e-F^d19;DH>_Z&?5FYW{R=jS-yU@bm@2yx5Z#{hC-|*Sn(AUAg;ke(yZ{zp%@CrlU1+T~Pze9fm=U8#aioQ?>xQ`VBtoRFh8=QmB|FX6F3&-Z5T@Jk4=<g2txC3thj&<O82R!0zD{flxDYPH>6DvNm;yUyOI2)f|x3#;DW3$mN8{Q4{cN2Zwg!dVa?T6$0!6Uw9#XT$fLkEICw<5rbzoB=*xA6JjwswEx*js3K3*KGycMpBsgBO5f2jcjF@QAy1DBw}1;D7s<_uL;RZQk?z1AP7?^S)NLA9>E|>%~jvt{n<f4YnQ(Jox5tn^wN|KQun|V*'

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

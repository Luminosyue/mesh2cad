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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ea7259d5a16544c08369264acb581f89/part_003.stl', 'relative_path': 'ea7259d5a16544c08369264acb581f89/part_003.stl', 'source_sha256': '04fb271bb9e3e2da1eec1a42f7963af39f14d0001341039bf7833745d857e18c', 'input_faces': 380, 'input_vertices': 319, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.25997161865234375, -0.3812306225299835, -0.22568170726299286], [0.2148342877626419, 0.12106063961982727, 0.25150543451309204]]}
GEOMETRY_BASE85 = 'c$}r12XGX}o5foMN#q=CgIFw*Kp>I91Pvf^63HY1D}qc8B7-qQPBJ+o@Q{-vL`EVF!C06aY``Y0$-x-&w~5AZ)9-yc@Biwq>grBaUGIIr?fs^wr>Cc<7b2Rb&yZK~uc)#UZrA7?pp-6IRbDlsSIn?JJ$el-H*oN1AC(ha|E1}I7VVlxbo5ap)Yy_edkyUoQ}Q!c$(qsCN(Q@1Mh}V^785nF+n|`9y)<tS)qiL&hY#%?HMo}(m#SF4da$cvP_S#9>;L$dS+~Kx_WWT-Tz9)%(W*MR7KS-uyv+`-rd}qGtu|D1SLBRyIyQzr12@y1Sf#n=MNe=$+r~XQR{e_2(rV3hpGE$B(N~dY{)5@bv!uaEd_VrLL#W?)%QUTK@9<RQNt}ED^*5~tcP$P8S0g6v$M>d3&Bt+rg=Y#q3O&~q+*M=l3AFS5JLbQ1c#@8-^K-ym1>b<%?T=Z=GjagyugZNG`QN8Z$M>qX2Uh``cwWoHW}<&0tFiv<sch#(SBzHAg{t88>Pg^s>&kJcpW)%RI(Emfoo0v3YtYWC55SE@lX+gd{lTr1w^;xAW*pZVH~{LIbrjrO&we&{AKr%V$A^R4^GDcd&-wLV;5`3IJdXN*Zw5E3yjzU#O$r9L!>6E~<}3EUJ?z>se82Bo_FKKR<RMeRjXFz?;PbyWeueW|F^W9+D6YR*`TS0_xAy1E^J@cKe|O@W9jIToCAfWV9>$kvap~RQFCU{{jIpOqgTLH``u6o3<nx0rAYa(;Jntj5!0r5fPoaKaKO9&2l>xV2u0(yqKYcQI-p**ZaqqM5(Jx0Hv;OOP;O-I+P~W^&dq4U)ycW;%gY<JndpopCNpR0~;o0Ig;Cr*DvEOHeuw6N4rXasTZZw~W>+4BgumkP;aVoeyjP=dl3(41!E5&hc3}qhIrdGUu8Cv7MQMn@6Z_leTe?xVV{rTlV^nczj4xwI`!?-_OfdPAwC$R#!yFJg>wR7QN@YVA<j;EF5edOy4ZupbCa<QH2W{$mxFVExnE;W_yT*vw<iCkTpK)x*}>MKtWxH0Z)w8sdmg6m?&yhJ@a{VMi<_w6>W`^8)-;D^|L>*Y{f7k9I}$;cPW@n9b9aRkRbxOX4;eO?#O)|BJuhh6o+jR5Jlv)j-=YET{4pUL~$9W@Wv)d~v$H{Wu6TDyNheoxBHJ!sEW89#nUalYoX<Kz=K{;iGgQQxTj*KQoQKgXw4<T%dDs{a(+EYcA7g<5!>?XSHVTwUP!cl!?kca6`y3)j`fc6w$PL>@CXX(#H{<N4a{enY>QXV!8&X6F26ZO*~*7+;6H_ut^I7a`x`xbEonXkY69j<07oj)Di;>(Ksl2IhHpsh`i{ygCjAS39O~JU?&FJnx3EeqW9st7Z#u&&bznar}N0as91BdwCxwF9kPm3s1a?>*Z>GeKqQPqB#$T=D~P1kFB@xy}Y}AMEyF~(64Iy_*G~}SOo9Op6%G5v&yZ+b-H#9?f2Yhbq4)5^F$o-<zim<@X9!@YBzQT>JQw5{Kl4o=h3g(t}VlHx)wuz`~6moOS9hMC5T&a{x^SU&-NZz2yR4j{&Y7zfq7QFnFnq?<MYmr-_HB<Jh|P8&pY?%<Cq`KheKF@Y=5-hs#^l%PPHk|`t5mtx#v#)4(-oe4&3vG{qL$yZf?D}80}d)f&JX`?g`XyBm4r7YyWYI*ZtxJaNEUpy6@jd9%I8<a90G!l_&EU)HiFTfV=Z=<#XzK7{-aYwh6cj-N12sy8_08SuA=Xj{7smvo)>+=f8pfT7dQ!<@3&1R1w$L9D55~6_|PupC{+${CIG{Jj8$2!1Zzm-obsN&JCN3{Bbo<&r>>{=T)iAY{Vm5qCf3So7m3Z@=QiNxC+OA^~0RMJnpX$Z+wCLF5gg&x52x<1aBeF_n>`zPJFp%H1u0?s~*R*+FldfZpr!6bJHKsX*Hq<>wnGXf}J2d>3J9AuOs*ADBi!S)U#H|8^iUCJ3N&AdH&*5Xg66GJ-@*I>~#&?^<IwK=%PF?Ph!1h?rgRI{XDxj=aWijz>Nzn!Cf85)r9fiKx2(B!TVPx4=~B?aPm{+#*DI9PZ>+6;B&h|YtH9ILc#3}Q^^|(4~_;`?Hgj9q3$=~yuU_xxt3gieAATo-M&NQgB#XEzofs1dCzzevKr^H?bjvHr-e~pRSgBV*WLj)>Iaags{*cEF+<R=>&9R{x8Df&M1mVx$;~WTur4#ka=tarr(-`9$^~wA8nqr8_>lEod079_Sa4Nec+0Bbs%^&U$e;Kpo;UXIhrsQXykE>qAMt#f=3I+7el5>$T6aGGuH+&=yPoHFJc>Mc2e>NGG8TE4<ls8)&z<CxYk^yz32#?#9dt_jxoB@vHaus|IYY?fDo@6ETXzlX5MxWiI<{{i){(Brm*8f>o#d^~EW&u}Gy~6ld-?-#yKuKH`2M>shj>2Zo~)g>@cUaiFTMz2e<`0K&|kZ99d%_jxDnC^>uGb;61FGk5xDzG>;`=Q$3XVyDRQIqY;dDvF|GrKj6ke@@81aV=Ji}3R{w+iZtNVbR?*8`|E%`eh`ddjF9J`#Mt;~2Ts@BG`L3^X0QDY{n{&xs3+sZbL;1)T?ZWtVFZ`3oUGa)}GCZBl`>izZqvIJjah&ADam{OGdB4o`CqLZ`&o}F*{aiN`E=_(Q3hyE6LdrgTZ{tL8b9j+Ne82k#w8zXb3EWQk6x>`Xe8gjL*YRb154raV+j)25X0$uC1+JGJH=667PbPuei<*$XA~!ac<@Nri3*Xajx8Zp;EeEcu+#QR0v$kSgY8UBC{-hVin`u_y{q@rx@_tK~<M=7zoUi)6<+yp(dpXW`O$CmV{_n`=_W<_{5`Hh^Rvf3*S=<LkVnOtenjTD^AkVK&D>-iuDhIAYrcXir1x0y37V1TQzDrMV=XD0h`*SDrq~62%s?ZFaXC}P_x8@h%yfW99*Rkt6=4p}<>mB!+c&z7)RC3euBfq>ATn*13kNWvJ|5(;Gu15l+$P=57$9QWnm+Qg(tHE6lYbBwboqTa$+xN)L?X|&GCE*)hf*ZFMp`Y!jshn4%vn8OOd1?^G+s$*hPmN<?<k<||$5!JHoVO;f0XH6QX1+Wo*00KcEx1`S5!^aI9^Ab5GwW}R<a}_qD*Mw|fpMu)vfz2^Nga;&9kbsJaO>e*i`RKO@AoT>wjuUYT;C<9$Mv<#HU?Lx{3oIvZQ`*0H{Ot&v2U^N^VH42`Z;32tz#ECUncy*;|>Z$f4N`$f_cI->0_?1I}`)AS6#;SauxY%JKA%bTn+pITy+}<Znf=1UZMx?Q`gO*yO3|ncwVQt4b;6i_pzPis@^)NIgi|&K8y9nalL1U^8L#y8q0cq@?N=<?`vi|aw8w#*UYo5Z;uv!nCnS<GT+zSJJvE!`rPOT`@sU{nUKQvERp%)UzgE-!|xS&SVKJ5RA3FvC+?vin5Xq9j+cEM@Sdw)lB)&eRv5WE@MFAZtH@%r(4K&~xPPrB4anyvH3Uyw#(jo64Z)3UvoQ~u7Y?Gnd-WvNKR1T+*`rj>!<`oKJ$`l~$IqFE$Yal2%=+c};rVE;D#v|*R>#5Z4mFYA6A{V#CFzpncVnKhPhZD4aTmPI{6(X{jWOibv=6NBn;p+JSAo~q-!QXgfVz8b;PW%Q9_CLgq$)qJHvrE&wJZefbPs96eUXd4d{0`LkO&>tmisIBeaO4TgIg7&!Bva#GcnF5e2f0^MD-<qQ33tz9?$~wys>%=`I@qrhg}br@OWFP$}<noedEb)#Gax{p{_4xvVV$vi9FWf4Q&5p&NFt;B+d_iklQWEJ!8l{sfnx~)DG(q^VS5O&-wd2?subcUDVTGxo^<+0eQ<uc%SeXVVqA^vR~b~({nsrY0v8wp9lSCriAc0cIjj8t86d9>;HHQ=h4?eN$8LF<f>W%xTkYza8JT$^6$7#u?t_saqUsp$)9xN_#fL2?R2fVL*9QA)&tfM#^y%h*||<oNw+zk<2&PiQoDcPdr$Fm+!qSz0dAIPj_1DJIe81l*EHdaTYwvz_kw$J_hFuO!!Z7hI(OKfZ5Hd-4a7X^>Cf1me>K$JRh08?2xCw4N923favfK(3!X<-D?g6+A7$Tl<P5II7L(g6WS?^)_q)vB$c=~G=TvQFzw0fzYQg;k)o~W`*x8D5-i?y=#^H+bIKSXec|R3zMIKrS+}u)=c_zP`pktSZ^S`>4L>}9S>)s62IBtt<C$Ag^?mEExO-<U*^YXigdES+4BJx<x4zN83;_-gzF8w9ubJGmvxc=x8uj7**8_~`;!hbytZU*%Pw~N)}cpt!d)hzXndA@GS_lhHKuABN?LVK)R<kr$2Jl|gA?vgRwj}Bdl=dv;WKKHTapCaEkgX`V~OE=-TtxvN(kz5bkC6<G$fU8_DyzIv7JEl3-W9lyVS=IEAY54xZZW#Y6`V)R`O~(6?Ip;0s_k4xOUw0zEAv~ZXxLNRPz87{mfjs8bo~-ZMg>{q)&xPZ;M$Z6u|2zWsmzCO^^XVFLGmP(3W+b^0zmR!m$6?*BS|#H?a@|-?UgmSIpDWwo#)cK-o)0)L_02=<TiIX4kvDq<ZajIw{j3>l$V23JjSJD7$72(~jaP-ZuFKb%{W$R)xy|=Db+Hw$yQ{%n=4li%4Cj9{ANK840@odCTqn%8#<PVSXH_$UyE1KNe)Aai>CBF4d;_>KhTOQ9g?aKe#rwFOB=c^;tmNr}z|9%t#!vak?e}=^Futn6d7)GRa%(vEHM%b0?=sm7bKUWoFZ$ESUx&~A%w<@A=X|akyC?HL_bJQz>*jzP(>C#Z<HEVFIWZmk09N0TY-hguTz_@u{(yQ%ZZ>GlJehj)cb!!uc;9XwLY~k7`xR!f+|1J@hI#5W=RU^WT;zwQu$_@JG2YCWLU=wJyJMvv`qoAN)`-Erq>=k;a?dDmBW4Ks^et@v!N*+Z*NA4G?~jwe@L-=owZF~%%~IczKe@St=XZyBx~DS#lUaDbP-AZ;U>uHnPCmaD_e1<YV*NPb@56aLUKe2g+Iu)(cIeIht22J=?<s}2U;d#e_siUE%On3!zI@NS%>5<v^mj9mx9L`J;|%v>)n7-!jTQU3ULG98{mQtf_+8Icvpe7Cj&NU5y{oqpaYNy6<oCOXcm1@w{Re=%K9c>D;;%T)PtN4N_#5u~dAfbh=WP9CzURH+exn*_VP3Z@rZB(3{YfLa3GM@Hrw{kbSId2uJO=w;?w_h+|Ia-@o>R}OasKwL#(lwA@;s_i6Wrw*NS?%fJk|67`oWqr_!zH?{GRxo4ekmV$oIvr^8B)ww@16ClADJ7o>I^Tx0B;j!J{_ucU61ic;rd<_er$#Oi}WirMbUSB>VT^HRSil=1VbNJjFxFt@qfURBFaxtya?bQ~3PdNOHU4<gkc;`;~gg{n)M%xt%NHluRnGijMO7iCRNkHqrn7C+a?x{&zo7R}20B{zQGlX~RCJY;cP9_a)YP$;-czSnESC@8iQ*>udFo&mpna%;JlP*Gzkt#M&2^SZfI{|Ea`Ui+TBvB-WbS%V&^S>wEQ&f2$a4{g;>jRbs6kFMnHNt;fCmd5N`d^YTX|*1FWo?~qvQbn#oo?-2i`#M-ZwSnE*ntHrMsKSbhNPPy)stD--MPj$)(r<@i&B|cU3s^~2*e@fz0k}J)hkobh;PxGk~r%Dd(=Q*W-)7P=0nZ)}$I@i%z;`4dMT4P1$d3jxDo@fCt?=P{x<WKWDS0>R|@jpA7)6qiWf0S4k?K6s=6R(T*e+&Cg{NLjL5KR&Phxj|9+r{4ze_3>s_{-vti7pp^O#Cj<1>$#!j~AUOK3@D9(W&Csh+iQ(LA=&wUfz^=nfN%-iQ=`c^YYUqUMD_DbdGqfd%gT(iT8>>Df*50lj3iRCWyZ&{*mY&@sGs66g?{brFi8-{a(B-+Gi8JAYK>k3yNM5uZ#ADM1K}vNXANG(L7#0qr_U%d3iln(uuzC@_$II^{$t{BeB-AUjDMgT6cT-V-jm!<>hxtto3UzA1|@i@m_w7#9Bvq`4tjt?eFE6NvyS>myeTJ>p(BRPGYU2y?m0yTBmsVy%K9(=;cpJtaY=OzbUcS177}-#9FU;`Ii!Fed6WySa~A)PW|JvNvze^%NLYb>nC2mki>;#jA;Lv^POr=sUccLd=2r{MJtG}F21U0sQ9YlD~XmCUrBs<(Nf~eiw_ZXi4PGUBpM(-NPJ1rLgGt`FCzM}_#)y9ixw1LSo|kawEsxwarz?ADMh7dpG7p6_$=bzDC!4AuZ#8%M4yX)ApWB0FXAtXPZs@Fe6slUqKV?yi=QvLMErd5lSF5TpCo>a=s59X#K(vZ6CWdfuv30=%44VOm!ka^(Z9rR5x+>(&xd}I_{pLli`PZ_QKA9jb<uv1XkPKUXx~>fy?9-;A0YatqSr<H;iC7%4;TNH=o#@}iJvXHQ~Yf4E1lBPDbY@;E!skSxKkpW(p<E=_;AtMqAk6AcZs`8t~4JZafIYg^WhSQOAhTTIOki{DWyfri!bApa!x5LT19*r(bA$7ynGdjt4OXiUryq3l0VItk+_WH(Ef9$O<y=AOtiiD`c7%*l(wQh#Mc)M6aC!F_mH@U<Vy4HByK19(|mo2>q`#p^}l1y@05(9nZ)}#C7V;Si{=yWE1FR>vzN~&aX!hF=CethP4cICUx|GshxVaPA7yvSMnxT~=qvj0vzk8i*(I**d{)aTxkWz}-%0Va&f;rHoJ;A~I46f_P4QXfv-IMNN^Ci0q*FqCs9AmJJIZGr6#YnvpE<>LN?Fko;>$QC&?&!(9ui+hw5;eeFMmklLy{}a2TB|$`O|zEiOWb1?e%-??@lQuT26d%rvy9Ypy*Ta#YKyW9`^E2C4MTo(tNPQ!ID4C7niuW<j}sAQ=**GOw=vDfm0%#(onRE_y(fQL|b|JE)sW<TxmX1;z-G#<{L=dKyqkb!?~8Vol;6PSbTn`1nK9zXf5&iMN5g+@ba}Jt|htBe2~OJl0VJompH%V&_12hrVLKWD_TH&7N_J<{L|_qK8tAD7DYNQ?<28~<Vy2-B+euG(|i_*vq%o@n>wYNQ<{i&6>m7DkyGl3HWqJ)HW6*=<r_=fSaPNLMiMuY{Au2h*pM9B*L6y3r&RW#R`a2+<do`8si&xI6n!OOl|}1%`8E=_k(_D1y5!bc&C6GkxRM-Gdq3y1oKEQ_+FN{2r}S}(zi1BeJw<zo`g!>r66cUyX}*ud5lwy4<xT%T{g;V<{!9!G@BcvYU%&b9+gRS;+~DN;&rPj}rWy6z><pZA*qA7<SD)%X00Q`l<p'

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

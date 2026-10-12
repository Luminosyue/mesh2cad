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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b8c12a34914f41c18bc4d2c3a9710562/part_000.stl', 'relative_path': 'b8c12a34914f41c18bc4d2c3a9710562/part_000.stl', 'source_sha256': '067486a1b64a2d07251a605254746277fc517afbd1b809b34e6d88b42447c877', 'input_faces': 625, 'input_vertices': 475, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.03617921844124794, 0.013208769261837006, 0.032900333404541016], [0.03671157360076904, 0.08818996697664261, 0.08257162570953369]]}
GEOMETRY_BASE85 = 'c$}r233L=iyM}u}AnXCcYQSL)YrrI|A~YcTVnFuI0ohFe69{XdiP5kV0*bPPNk||DP}$dnAs~d+{0NAMI3oH3KUYyUMTOg6eQ%B3HQsaXxi_9V?^{oOQ&U}CU0u^%64|rxb3q#a)zpq}`So@{6HTL3N(<8B#>PyW_{P}S(8*J0IkZ5*=}+paJ_CA34smF4+MJLvV`JZl32EaDX*;e}NMmQnxG6EyVn$7VeM-!jvBbNKii#a;^4JNZrj9l9^&?s~Z|n?j(AXL8{6GGcFq`14_-^_UYRk`gAGIf~v>}buJGzPBo{e=j3*N9wrr;+V2(I^jfq99HG%MHEjN2}F>IZ^*qDQ6?H<C|t{c8`1dYpSk2=4THn8%eC@kUa0!QBBF>4N9g5b;`OHNicR8=0qPr&+o2XUwM}ACSU4HGug~E^g;<M>4HkI~T$2Y_m&n*AK-we$zmXzg!{B%AE-fIlfvkZfA+nZc&dL?ce#pE#j943hw!@B(5jriH+<1e%~he#h;iDE-tuXRM{kW;;~FC*Vne=<BHfWxMyPk^MW!QKe}?7l^Y?gIX=k2y!+#g#9a*wr3&8hO1hPM_7-9O=&7jBh{{hD$JOy7^Nc#;dyOr5g1d{IWuEY9nw9JK%I*}r&Qihkh-9v33i_wbiF6x3iSaP+k@#M{33IQ3_<o27*DfReGRJ!+w&(WfQ@9_3wKN-l7Qp?`?Y8J={kPvX2>#bm?*H7Q=~k}yJ<ELPJ?@8G=Gv)TK9A{V(yd&taf*5UKW*`zR(V{HcGMQ{U55G>{=)6Oc6q%xFZaud_GvfrGp*cMb##ZwU){pzebObtot*+WJ~uec%C*UdIezaSqTFcNN^sBCtNeW#1?g6<IeuW?*pXr512=yn_|rqSczx@q%oFeO`Kr;9>o1S^TO9A>lMo-u@miDcb>eu#S9ALVilo{2yK&t9;WxSbXdS_g{WU)j`8!wBtz4U3k9jJ$Un@~(t?1{s8ht48MuSW%H}=Hu68Uj|@bPx8A-EP@hvSFuNwace(JYSdlf?ZzZRCfd|Ccx8c9*}DZsq#-ZJ4hul40eZ*7f<glK0u-jWJD_SGmRGXJ-5dqW-;?*7CSLmucnh7b<dlVm1k`7n>`%w&WPc*Q%Lj<=$;&Illj69{=Ymui^NR_1rJT)2v+2*~{1Oa4*Mu7QH9F_tNeSf^X(|!^h{JV&1rThL!72`*A%_ciG}S^#?OgyvfJ=xHHEWk6gvq(Rb-quAS-6{8}+SUmIqx7X9W<TFv99Nv4(Sk2mk;>*X<zheI=%uQNFQ=KeG**XE^j{E4@j-wItN;^$0!U*wP1vvFhd9Oic}WLmivQIG3s$n(GCp3RMzcXRXgyRBl1=(kR#c--D7nP%nA6*+vq62IYk_FYRB^?dRzkI(hrq+7Y(`vLRpk{P!69^JT}gdMhcXH0MAOTXp*pHX|6h;KY|h2W9jr`vev`OJ%!$gpzv&P#g)&)aN^cYc4FdE7akpI4MwD&l(wt>k)|W?H#+_HB;8{!rBKJQE<e5nqPmy$92*+*M>g$Ddxn{9dQUJZ_utIGJ1D#*JI;nWtXNwDH;x`MkvZ>bBMM{uAb_Q+b^eb#$TNna_Cq4CVES<Q{DS$1nei>&dK;BzVzcYXrY=J>AN+9nUi#S~kPV^&?ODycBG=#d~fS=K2R;=l%?C9xv(%FTF(Y&>z#S+_R?=b8o2(TYUL9_6q*vCR@Dr5Pa=vp3kRNn=AUqd3zaO7cXX7xqhf5$Je;e<851z;9lb!j(6vzS-IyyQH~Fo&+}@7uCvAWUTVtcH?Wb7>sm+V5npCnxv^my#>vlaTYTVb=GuB*F9jc%DZV$UI-mEmWz(!&Yxg_%=UP5ro`@ndL_McEzbAM-Z@P`o8p=E>P#mv!dm+KS3lU$1=PSuw^$=gLtS#QSIGMk<=*PBr?;o+u%U|R3+yC4&@x4>ZbHAOR$K$QiNx{99b9nu8B{a**jXmH~581f$>wM<HFJ+5y6){Y3_pS)6$C_nXxxTwO^M;4){JPG3Zd+SD&Z?cWc|0_=#e1rDVP58-op<WXd^ESm8x|YO*E_E33_ib->-Q3w=da`WcI@+lyC3cl^=eCB%(8O*(N50KJ8a`lXD;W@znpF5M!S5@pKfA{_kIa}c)yK%92c1fw&8wg)ip+ps}_a1o#S|1xhqtDOVrc7HGjSux6{Y_v|+wC$Ht9moteA1osw%m>RSa*X>5ykzukd(;{!IXf7FZl<yN8|eeBbzq95kZ<neZq=NZY3&GF2=U-LTcuLYC;X}oEh+D`tbapkV>jTY@0KZv=P$Ajd~{94>^1>DbiLORF){szZ8d0a{EsvpYnxm>@i*s&-PpZxh2KHjh_8-K5Wd48^qI}d%$Jf@wk9(`jr_m9!Y7VmAlm3g)OHg1gG%lvptt|zDj*FWST_sey@jwJWQCUW~{qu(Z<eN)u$ER24`I0Sb(R&YKK<7!&5iQ>41uj9|3;PE55@#S@nPv-vgoI5o^eD9KvIQ}_4Udi?MZ*lz9*4)n{8jTb6oS(`4Qzksi%AHZOm}eicaqr4R=Kb2+>d{9z_;*ceLtDH)t`PH9`|R~6mu9}0$EU0M<1vDF=*8{7gZ>0}B{f0+^Z3`j`GRYmhT*#A<Mr`xTX1|JAFr!NF_);Pdr6K@;r^7|Ie#+82Xp<}J4as^{aNvO&Y#8k0@ng&aQq~0zZTwRgs7)oEAF4&+@F$r+O=k$m22k{USa;Ey{#Va!w%@rMz(m@ijK@v_S(39pf~dyJU+G1N<&3E_r1&akpjN&ORn!qVxGtMedFen!J_`kq0Hz0%J(n#eZk$)4Vcg4`;l`^$RJVw__aLmE#&!GZ&X)s<Nj*q%`l(eT|Yp4@0!ZY6R+@kDfVoC@x8C$IxWN3wd8vDYZ!;QHg5bUb*r_1^fSu^cL)B5<9lE{fNQ0<aQt2FA7lHEuZjL2w1nrqcekZmxp#Up^9MX18qaoh7w5NUAlDxpk!9tcp5>Sa9<lT3!OUHHww1dVOvH83$QG|BOk&<}uZ=smO=mur+wYtj(m@>8gdDDaIQmWU=v?NHa&6pj9p--Mhk5VJZC%6{KF{&1F;9Yfs~zX~bpBrNAB&rbe3Qvbg)YxcvvU31EatnzGOgV6G$C2=xCXX(E$V&d<*(S{wbVH&tbw+8@4SzB9exe#E^t@yG3Ix$uGTWRo(rq_Joe}FE4l05hggsCx=V8Jp_)8CBQZX~ojW%&|LrFm_tec~-jBz>?|c6p!PiSiTraYom93d4{Az2bo}R+|;wD==ovEvsC-Qabx}D4IFN=P-!|PQaKa$71S-A`=*Pj&P^V^Qct>m63g_(yPvGY1*nJ4nNmE7pNi+Nm_E#4Ton|XPAJ^I~a%s*~ttH(Lx#8&J0_qG4U^UN2vw14k~I3E8&_IUk^8O#Ir+PL$t1m=Ue9?#FmBSl^r=aQ@AT+92O<CW{n$Cc|#a`pQ1mTEXav`3jYBv<DRA6MoL$<=v7a&_MDeXlZacssNhF6vk2J;~L1Prq_qaKCvKT%A{)@xdd+c~IwbaKHH+T%FG)cP`q9al-2{uW^^_QST#-X1p%yQSLjEtM@6RAl)U7OS!M<Z8HT|?}OTRVWWhq_fv4c`)Q5OMvL!P)&r8O>j58E)&r8O>jBBt^?>B+dcZgtFh<m`tY;)w*E8P8rh=>MCCT+ZrI?52+PJ!o^6|te%y;v7)PJ})LFCo-o8;>Ht=0<@MLp{J5M1lhn|Wf6jjQWMA72{Ed^rDZ(nr5GN%V)h9tQVY4}<%yhr#{U!;-7(VOhVj9@a1Z5+%-;vYwY*UC+B`H;opm{9cgUHDW#U{fBK_{T(5>XX>}i6Y%>t_Q4c!yz1{4aP{|#r&QIcf-Ap|B=-(^g!6vL#?{|VlIzpnVLpk^mzFeLaP{|~k1M|iC0BnBO0NDMlwAEiD7oM7!B>9Z?^S-!O0NE%H6AkemKnqGC)(P$zHdJBNwvkiWmJCdEm6Pn`&x3n$YAC(58Jr<yIXSYTy5qP`1y?IK{LTU_wl<vkJ~A^zWyfjTeWx|?H|VVE6)MEjsb%EJ*NU!pHn$2HHsDG%5xGQSDuqdu0AJ`TzyU=x%!+$a`ichF}~?^5wAR7l3abhB)R&0Npki1lH}_1CCSz2OYRm^;)E*C>m*m7*ZH{eyiRiUd7b3y^Ew|_p4U06eI55t=T~yS^9!zy6K&6RZm0U3bJk6+zj<ZmH~9Xm-#sux<gZR<p2hcHAJ3V>d?cP@x2!r#sPbIb$Cc;0`UU3db6v^R=em-s&vkwED9?4>9SUZP{#2ezOYZkvdePvyBCk9rmt1{LF1h-g+!wDrCpSvgn<v_-JhzwJ@40<JBf-`80+Rc^7l`jNU#Rk)LUQ#zg)d%tPvPUrdkXh};Dw?d<vok!>U$Q+)%PsEdX)DpTJ_V5M7;9eM{@POkM8azjz@hDCAs>($(8UbbLIV%<bLm=W|tHFuD%zOTzxO*ZC_b%^}U<q>U%f6MAPNsxRm#RKCZk6lw5reD7pF`(7a)acKE%=1owN7DdW}mnBeMrOwaUn;(3AJdsT4ty{f1EF46DmdtS-a_qqCx-GZy{e<fGn^Xe7;6yrvH?<~3c-q|xw6Z4DuUfc8PX~EU^<C3fI$Mq^@MEm^S*GsOxuLt*gUk~p0zP|2yzOI!01Cp!z2aMM>KCjCD1j*I?2}XfKaKHTz;OhPd&)FLsukObH_uG#F?zbNUT-}f1DU-qNQ1*vNuI>-fM`sDH?mv-S-G8Dl&R!?DvcE-gb$^Q|ai8Go{uv)v_s_g=Sez$ye~ynU`*ZXa;L3g>$<_TrKCbK+lH6~<P{c4X{?z?TlB@fd^vvOctNWuQ_uC&;DW3PGDf_h~SNCg4uI|^8+;6|u@66TxW0I@;$Mo>eI9}PG=Hu%Aw0D9witknTzk#d!-?ZixnJfG2d|cUIXFTg7xZnOgaCQHlal9ATqwWI)_nfc5@w&$SU+^;D-_(7E;Oag@S7J{-Ze<^%<mx^~Z`)qXm3@+utNSEf2mA5&s{1g()qR-m78yLwl>MA~xgOjf%Dzy^)qSDfQ;1jgol36mJM|U}=j&M6*DAT+zSbxg$1jUxUaKg-AOCJ6w@2AetM^OedX)XQu5D2~zLb5ulB@f8jjmJqd@B2aCHK~d=J@@kxIG>6xgKR-v38BGOXoHGE{G_X**?;?i@L@3`|)S1n=2JF71x5aaic6-s0q@a)PLSWJu%{cwS~Gx*#CPA^-_m9Rhwy^nU0w0n3>X`nHGN>dD6}BN8yjdZ$h5@4&+JK!4Ef&caWJTLnm7NVB|?BS^QAsNu%JS%{1Oj!=M8!egg8O11<hd<VlCXcQsQlGlfH6f=|QoEr+gz-wdA#pMv~m9A64F8UBh{*HwHc=~Vb(XjgY=XNw<*JZTq;AA<Z4w43~LeE(diVeu)*lP<9MWaN`^&dCp@b7Q7Ap;Ik>1oEVBS^O~MNu%MrqrJ_cFT!_$?+hP?d>0%`7&IJyF4{W@I@#hEAWu5Q;^!ex8U_C*+8Yl|u=ux-Cw<%Eqmd__5AVX*qcKQ62KnYVj>^y=iw{Gdv?6>sd>DKs<ij!cDnaYQmo!r`GZlg_k9>VIRWMT(Xn@5RMxJ~r<mtMj>+E&tTkw>6qnxw{d=KPXK-<B8X7<HdGZjED!Bd@cP%r5_@CBGtK7)P&Pv>_gt|`*R@abk+Yo-;@CGd3a$KiA1@EP)-;xiujwa5>{^)v$76aFi+><cqphMt3e8F6$zUq(FTFX1@9f_?!{bxpx_Od1XUwVAG&X^ex_<zP>Vd>k|eJ`R2%G!dS3jm57*ehvH<=mz*L@CTq<;Sa!{g6@Jp1%C#52>uNGY3LsK)9?qO+u;wwXF)f@XTg5}eGmQv_(jln;TOTrfKG#-0Y4Tx8h)ACx2w%G4LS>c8vJPJSoqQKk<i!RBjI&uCwLvc8MHNgGx!?NM({P@%R+0zmxV74eIC9vd>Lp>_%iU-p$*`x!#9Ptgl`Jp9@+uEJ^ZWCzVNTYkAl7dKMFn;Is-ly{%hzpc$!1a#f+F=NhiS5wMy4)JaiWP30$B5f_mUDqfGj9$kSXw_ux;UAHvfdu^4PIIQcK>+SYiUAf-8id^E1lFQH$-(;OXw>pcY5Jb9X1%cHzJ%E%Ydc>dL(h2Uv!Ed^f+ar8%XCC$-Q;M*ZT%52j&rjCbRg^zV`*=*=|c;d7^dk20t@~gqtL6^d(qHG6r9sD+worLay-;J{K(39|oQFak}9)2&%K8Id}{}^TY(9hxBDBB6mhkqYs>!Ca0lTfw{x*mQy%H}|q!M}mBiO@Olv(0{ePviSE>AUdbG%j;NW8nLvtPj)${|d_5Li@nCL0LU$TlmH(D+jFyUk7C+pyl9$QT80P1bi)&6^A|t-w<Vi(Bkl|P*xWj2;UK9FG1_V_d{7P=u7a#N1AC2d@tl@f=z{vg#QL*SD{nk=V7cyLC3>i#hCdLdLI4?#>`ddMfePifjsC=_&oRv(0q70KeR^chI8dYJ_6^c8?+BRjTKtsMPuB|LB1&Z&;czDUkQC!6dDNsCXRgwbR_%`_^!}i@KNX!`h7r3eMbHz)3-5G2dEA|*h~Y=lmmSgJ_mlEnarP%TCSM}B9V_oBER2EOU&<h!AvPg<lRW*>Hq3oYNk~h?c-uigLlG*nkn8)Rn7D^68R-aRZ-VGGbNg-8gwaqHF&Cz+TI=QCv5@05B?*xpW5C7iF`{W^4Vtkw^`R6>SG7%6L?DG%OYkv;_kqoLn42`Ot;MRx*7W)jT8AlG*09L9UMbtanSSdaqtJtRM?Dr&P<h{mEjkok5)oc;Hf+qG32WwpMd^d3|#{MnVC+Q=>qf%c=}v@e3pCz<mcj?B|zVXzktu)h5i?OeS9_)+7y1iS!QTlpMko_ha#pe^kw)YvuvTppIeB}kf-uah#~(9^2^P#6&inT1wKQ*6Jpvy+rw|r_%rJ@_A8KYhnQy27vZ-eHd|xA0ePocR?|#npk?8k;j;~)jo|lVyktYS!iSk<;SR1Z9CbPIxf=K^`4^Dy;^5D8h7U)c%BvuTd{yLoA+{%c7v!rTrU<ks{B4}i-=UA-N$L2cFO1`*R2Xe8jPdA1s)V*x!uSe93Pu}(G1fXG)kiz)W9;;V_O<x7$oGXG1nmSr2);kG9Xx3ti*JT}ANX$2hVb3sn?q~BH;1nctpZ;gz8tg&d^z|(HP+uW_LRu~0{t2O7x>Si7vVpLKLkAqe+Yg%bPxP?_>IsV@H;SnNWTU7mGFz9o8UL$x|jY#<P+fMLf?m<3qK$F0sMUUBxpK(68v)LX87gs>!F{*uZPcu?uO5X-w*u^en0$K=mq$*@VB9N;prYy$HDgs(z@{F;p@OxK%V?x8s|x$TKuoblis)Z0^~{mW$}lRC(VKX82&K)C&-g`BTt$JPxGsx@x7FEfyFOGo^+ALuRxwO+2S`KPnrt96@CN!Hsr}4K%Vp<Jk4ix52X2#d@ba|;cLQ2ARmr7DgxRSz88EK_}<8q?}t3;YZgBkdD0>9x$rsA!SM0ur>f9u@U)(wF_8^z37>|34}~^?r+fNz9RGAnU(oT7#IcjgwE?XY9%#HSApHrR${Z*sr84r=M?v^(5MszzL;pp<2O(b%tSfvq<f)GugEvN5SM*UUl(#||`Hm<X0^bVx)?fqSJ0eeOuqNP5P)45CV<9LHK^ghyQPvVZ1o?_!b>W{!z7SXi_=?EWHTDqKAZa1Q&^2}s*Wf+GJjFG38Q0)tl-<WQb_(UEQ1&leWBX9P4`n&H{&t~!7s|+ggtAreyO5{#Y$kXn%E;5YcOA;tp^W?*l+A-*hx}Tw1@LQ-r)xL^JOgD5a1CdnJPT#yccLs6J_~uehWCQ+MOiAwbUw=SQAVEDvzJhQ31tT{rhh{DPbec#>sh)Nt%P?Y|5)So#3OiG6H|U8Vzxs+hNt<P)}oJ~kKwl?<`DF-_V<00{O8aD?eF_6`Cp*FYJcCC$^QxcOZ)piPM+@bq;x-!_kHrUp>^O%n_GMf<Vm|(e0SsrVUFqx?dSM={X@Pdv={u3W*csrskDQ&q=Wqr8kdzq3^DTGYg|?WF~rE<z-Orr^2HsT|JL-+%%s6zNB)e)`8?<icrRj(Lr=pW)%d%QLBE6l4xc#&Jr4gZzT-OdG<-1!e<r}e-itb@{#?|Zi({1j2=YhJC*(cwN8oQFp9k-Ozk&Ss=(F#j0r1p@XK4E~w9$+9Yv@<f;_#6@9fg7l|4;v%*57~h9!s<R<67z`?XQrnpX_4R<$IwV*|P{ef6xk<|IrJV-t^`|`)`cSox%'

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
